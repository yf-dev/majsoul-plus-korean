#! /usr/bin/python
import os
import sys
import urllib.request
import shutil
import json
from pathlib import Path
from common import order_version
import asyncio
from contextlib import closing
import aiohttp
import aiofiles

lang = os.getenv('MAJSOUL_LANG', 'en')

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

async def download_file(session, url):
    filepath = url['target'] / url['path']
    full_url = f'{url["server"]}/{url["prefix"]}/{url["path"]}'.replace(' ', '%20')
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with session.get(full_url, timeout=timeout) as response:
            if response.status == 200:
                Path(filepath.parent).mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(filepath, "wb") as out_file:
                    if url['path'].startswith('en/extendRes/'):
                        ba = await response.content.read()
                        await out_file.write(bytes(b ^ 0x49 for b in ba))
                    else:
                        await out_file.write(await response.content.read())
                    await out_file.flush()
                print(f'[+] Download OK - {filepath}')
            else:
                print(f'[!] Download Failed({response.status}) - {filepath} = {full_url}')
            return None
    except asyncio.TimeoutError as e:
        return url
    except aiohttp.client_exceptions.ClientConnectorError as e:
        return url

@asyncio.coroutine
async def download_files(urls, max_tries):
    try_counter = 1
    while urls and try_counter <= max_tries:
        print(f'[.] Try {try_counter}')
        retry_urls = []
        connector = aiohttp.TCPConnector(limit=64)
        async with aiohttp.ClientSession(connector=connector) as session:
            download_futures = [download_file(session, url) for url in urls]
            for download_future in asyncio.as_completed(download_futures):
                retry_url = await download_future
                if retry_url:
                    retry_urls.append(retry_url)
        try_counter += 1
        urls = retry_urls
    if urls:
        print(f'[!] Cannot access urls: {urls}')
    else:
        print(f'[=] Download completed with {try_counter - 1} tries')

def main(overwrite_exist, force_update, original_assets_path, max_tries):
    server = None
    if lang == 'en':
        server = 'https://mahjongsoul.game.yo-star.com'
    elif lang == 'jp':
        server = 'https://game.mahjongsoul.com'

    prev_version = None
    prev_version_path = Path(original_assets_path) / 'version.txt'
    if prev_version_path.is_file():
        with open(Path(original_assets_path) / 'version.txt', 'r', encoding='utf-8') as version_file:
            prev_version = version_file.read()

    version = None
    with urllib.request.urlopen(f'{server}/version.json') as response:
        data = response.read()
        text = data.decode('utf-8')
        version = json.loads(text)['version']

    urls = []
    with urllib.request.urlopen(f'{server}/resversion{version}.json') as response:
        data = response.read()
        text = data.decode('utf-8')
        res_dict = json.loads(text)['res']
        for res in res_dict:
            prefix = res_dict[res]['prefix']
            filepath = Path(original_assets_path) / res
            if not force_update and prev_version and order_version(prev_version) > order_version(prefix):
                print(f'[.] Skip(Old) - {filepath}')
                continue
            if not overwrite_exist and filepath.exists():
                print(f'[.] Skip(Exist) - {filepath}')
                continue
            urls.append({
                'server': server,
                'prefix': prefix,
                'path': res,
                'target': Path(original_assets_path)
            })

    try:
        if asyncio.get_event_loop().is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
        with closing(asyncio.get_event_loop()) as loop:
            loop.run_until_complete(download_files(urls, max_tries))
    except asyncio.CancelledError:
        print('[!] Tasks has been canceled')
        sys.exit(-1)

    with open(Path(original_assets_path) / 'version.txt', 'w', encoding='utf-8') as version_file:
        version_file.write('v')
        version_file.write(version)

if __name__ == '__main__':
    main(True, False, str(Path('./dev-resources/assets-latest')), 10)
