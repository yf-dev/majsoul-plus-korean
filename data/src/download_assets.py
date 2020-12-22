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
from tqdm.asyncio import tqdm_asyncio
from common import log_normal, log_debug, log_warn, log_info, log_error

lang = os.getenv('MAJSOUL_LANG', 'en')
verbose = int(os.getenv('MAJSOUL_VERBOSE', 0)) == 1

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

async def download_file(session, url):
    filepath = url['target'] / url['path']
    full_url = f'{url["server"]}/{url["prefix"]}/{url["path"]}'.replace(' ', '%20')
    try:
        timeout = aiohttp.ClientTimeout(total=60 * 5)
        async with session.get(full_url, timeout=timeout) as response:
            if response.status == 200:
                Path(filepath.parent).mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(filepath, "wb") as out_file:
                    if url['path'].startswith(f'{lang}/extendRes/'):
                        ba = await response.content.read()
                        await out_file.write(bytes(b ^ 0x49 for b in ba))
                    else:
                        await out_file.write(await response.content.read())
                    await out_file.flush()
                log_debug(f'Download OK - {filepath}', verbose)
            else:
                log_warn(f'Download Failed({response.status}) - {filepath} = {full_url}', verbose, is_verbose=True)
            return None
    except asyncio.TimeoutError as e:
        # log_warn(f'Download Failed(TimeoutError) - {filepath} = {full_url}', verbose, is_verbose=True)
        return url
    except aiohttp.client_exceptions.ClientConnectorError as e:
        # log_warn(f'Download Failed(ClientConnectorError) - {filepath} = {full_url}', verbose, is_verbose=True)
        return url
    except Exception as e:
        log_warn(f'Download Failed({type(e).__name__}) - {filepath} = {full_url}', verbose, is_verbose=True)
        return url

@asyncio.coroutine
async def download_files(urls, max_tries):
    try_counter = 1
    while urls and try_counter <= max_tries:
        log_info(f'Download... (Try {try_counter})', verbose)
        retry_urls = []
        connector = aiohttp.TCPConnector(limit=64)
        async with aiohttp.ClientSession(connector=connector) as session:
            download_futures = [download_file(session, url) for url in urls]
            first_error = None
            for download_future in tqdm_asyncio.as_completed(download_futures, total=len(download_futures)):
                try:
                    retry_url = await download_future
                    if retry_url:
                        retry_urls.append(retry_url)
                except Exception as e:
                    if first_error is None:
                        first_error = e
            if first_error:
                raise first_error
        try_counter += 1
        urls = retry_urls
    if urls:
        log_error(f'Cannot access urls: {urls}', verbose)
    else:
        log_info(f'Download completed with {try_counter - 1} tries', verbose)

def main(overwrite_exist, force_update, original_assets_path, max_tries):
    log_normal('Download assets from server...', verbose)
    server = None
    if lang == 'en':
        server = 'https://mahjongsoul.game.yo-star.com'
    elif lang == 'jp':
        server = 'https://game.mahjongsoul.com'

    log_info('Try to get downloaded asset version...', verbose)
    prev_version = None
    prev_version_path = Path(original_assets_path) / 'version.txt'
    if prev_version_path.is_file():
        with open(Path(original_assets_path) / 'version.txt', 'r', encoding='utf-8') as version_file:
            prev_version = version_file.read()
    
    log_info(f'Downloaded version: {prev_version}', verbose)

    log_info('Try to get server asset version...', verbose)
    version = None
    with urllib.request.urlopen(f'{server}/version.json') as response:
        data = response.read()
        text = data.decode('utf-8')
        version = json.loads(text)['version']

    log_info(f'Server version: {version}', verbose)

    log_info('Collect assets url...', verbose)
    urls = []
    with urllib.request.urlopen(f'{server}/resversion{version}.json') as response:
        data = response.read()
        text = data.decode('utf-8')
        res_dict = json.loads(text)['res']
        log_info(f'Total urls count: {len(res_dict)}', verbose)
        for res in res_dict:
            prefix = res_dict[res]['prefix']
            filepath = Path(original_assets_path) / res
            if not force_update and prev_version and order_version(prev_version) > order_version(prefix):
                log_debug(f'Skip(Old) - {filepath}', verbose)
                continue
            if not overwrite_exist and filepath.exists():
                log_debug(f'Skip(Exist) - {filepath}', verbose)
                continue
            urls.append({
                'server': server,
                'prefix': prefix,
                'path': res,
                'target': Path(original_assets_path)
            })
    log_info(f'urls to download count: {len(urls)}', verbose)

    log_info('Download assets...', verbose)
    try:
        if asyncio.get_event_loop().is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
        with closing(asyncio.get_event_loop()) as loop:
            loop.run_until_complete(download_files(urls, max_tries))
    except asyncio.CancelledError:
        log_error('Tasks has been canceled', verbose)
        sys.exit(-1)

    log_info('Save downloaded asset version...', verbose)
    with open(Path(original_assets_path) / 'version.txt', 'w', encoding='utf-8') as version_file:
        version_file.write('v')
        version_file.write(version)

    log_info('Download complete', verbose)

if __name__ == '__main__':
    main(True, False, str(Path('./assets-original')), 10)
