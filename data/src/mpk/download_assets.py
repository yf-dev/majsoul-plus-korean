#! /usr/bin/python
from contextlib import closing
from pathlib import Path
import asyncio
import json
import sys
import urllib.request
from tqdm.asyncio import tqdm_asyncio
import aiofiles
import aiohttp
import random

from .common import (
    log_normal,
    log_debug,
    log_warn,
    log_info,
    log_error,
    order_version,
    mpk_lang,
)

HEADERS = {
    "Referer": "https://mahjongsoul.game.yo-star.com/",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}


def chunks(list_data, chunk_size):
    """Yield successive specific sized chunks from list_data."""
    for i in range(0, len(list_data), chunk_size):
        yield list_data[i : i + chunk_size]


async def download_file(session, url):
    filepath = url["target"] / url["path"]
    full_url = f'{url["server"]}/{url["prefix"]}/{url["path"]}'.replace(" ", "%20")
    try:
        timeout = aiohttp.ClientTimeout(total=60 * 5)
        async with session.get(full_url, timeout=timeout) as response:
            if response.status == 200:
                Path(filepath.parent).mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(filepath, "wb") as out_file:
                    if url["path"].startswith(f"{mpk_lang}/extendRes/"):
                        bytearray_ = await response.content.read()
                        await out_file.write(bytes(b ^ 0x49 for b in bytearray_))
                    else:
                        await out_file.write(await response.content.read())
                    await out_file.flush()
                log_debug(f"Download OK - {filepath}")
            else:
                log_warn(
                    f"Download Failed({response.status}) - {filepath} = {full_url}",
                    is_verbose=True,
                )
            return None
    except asyncio.TimeoutError as exception:
        # log_warn(f'Download Failed(TimeoutError) - {filepath} = {full_url}', is_verbose=True)
        return url
    except aiohttp.client_exceptions.ClientConnectorError as exception:
        # log_warn(f'Download Failed(ClientConnectorError) - {filepath} = {full_url}', is_verbose=True)
        return url
    except Exception as exception:  # pylint: disable=broad-except
        log_warn(
            f"Download Failed({type(exception).__name__}) - {filepath} = {full_url}",
            is_verbose=True,
        )
        return url


@asyncio.coroutine
async def download_files(urls, max_tries):
    try_counter = 1
    while urls and try_counter <= max_tries:
        log_info(f"Download... (Try {try_counter})")
        retry_urls = []
        connector = aiohttp.TCPConnector(limit=64)
        async with aiohttp.ClientSession(connector=connector, headers=HEADERS) as session:
            download_futures = [download_file(session, url) for url in urls]
            first_error = None
            for download_future in tqdm_asyncio.as_completed(
                download_futures, total=len(download_futures)
            ):
                try:
                    retry_url = await download_future
                    if retry_url:
                        retry_urls.append(retry_url)
                except Exception as exception:  # pylint: disable=broad-except
                    if first_error is None:
                        first_error = exception
            if first_error:
                raise first_error
        try_counter += 1
        urls = retry_urls
    if urls:
        log_error(f"Cannot access urls: {urls}")
    else:
        log_info(f"Download completed with {try_counter - 1} tries")


def main(overwrite_exist, force_update, original_assets_path, max_tries):
    log_normal("Download assets from server...")
    server = None
    if mpk_lang == "en":
        server = "https://mahjongsoul.game.yo-star.com"
    elif mpk_lang == "jp":
        server = "https://game.mahjongsoul.com"

    log_info("Try to get downloaded asset version...")
    prev_version = None
    prev_version_path = Path(original_assets_path) / "version.txt"
    if prev_version_path.is_file():
        with open(
            Path(original_assets_path) / "version.txt", "r", encoding="utf-8"
        ) as version_file:
            prev_version = version_file.read()

    log_info(f"Downloaded version: {prev_version}")

    log_info("Try to get server asset version...")
    version = None
    version_req = urllib.request.Request(
        f"{server}/version.json?randv={random.randrange(1000000000)}{random.randrange(1000000000)}",
        headers=HEADERS
    )
    with urllib.request.urlopen(version_req) as response:
        data = response.read()
        text = data.decode("utf-8")
        version = json.loads(text)["version"]

    log_info(f"Server version: {version}")

    log_info("Collect assets url...")
    urls = []
    resversion_req = urllib.request.Request(
        f"{server}/resversion{version}.json",
        headers=HEADERS
    )
    with urllib.request.urlopen(resversion_req) as response:
        data = response.read()
        text = data.decode("utf-8")
        res_dict = json.loads(text)["res"]
        log_info(f"Total urls count: {len(res_dict)}")
        for res in res_dict:
            prefix = res_dict[res]["prefix"]
            filepath = Path(original_assets_path) / res
            if (
                not force_update
                and prev_version
                and order_version(prev_version) > order_version(prefix)
            ):
                log_debug(f"Skip(Old) - {filepath}")
                continue
            if not overwrite_exist and filepath.exists():
                log_debug(f"Skip(Exist) - {filepath}")
                continue
            urls.append(
                {
                    "server": server,
                    "prefix": prefix,
                    "path": res,
                    "target": Path(original_assets_path),
                }
            )
    log_info(f"urls to download count: {len(urls)}")

    log_info("Download assets...")
    try:
        if asyncio.get_event_loop().is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
        with closing(asyncio.get_event_loop()) as loop:
            loop.run_until_complete(download_files(urls, max_tries))
    except asyncio.CancelledError:
        log_error("Tasks has been canceled")
        sys.exit(-1)

    log_info("Save downloaded asset version...")
    with open(
        Path(original_assets_path) / "version.txt", "w", encoding="utf-8"
    ) as version_file:
        version_file.write("v")
        version_file.write(version)

    log_info("Download complete")


if __name__ == "__main__":
    main(True, False, str(Path("./assets-original")), 10)
