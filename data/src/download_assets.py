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
    retry_counter = 5
    while retry_counter > 0:
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
                    return f'[+] Download OK - {filepath}'
                else:
                    return f'[!] Download Failed({response.status}) - {filepath} = {full_url}'
        except asyncio.TimeoutError as e:
            retry_counter -= 1
        except aiohttp.client_exceptions.ClientConnectorError as e:
            retry_counter -= 1
    return f'[!] Download Failed(max retry) - {filepath} = {full_url}'

@asyncio.coroutine
async def download_files(urls):
    async with aiohttp.ClientSession() as session:
        download_futures = [download_file(session, url) for url in urls]
        for download_future in asyncio.as_completed(download_futures):
            print(await download_future)

def main(overwrite_exist, force_update, original_assets_path):
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

    connection_num = 256

    try:
        for chunk in chunks(urls, connection_num):
            if asyncio.get_event_loop().is_closed():
                asyncio.set_event_loop(asyncio.new_event_loop())
            with closing(asyncio.get_event_loop()) as loop:
                loop.run_until_complete(download_files(chunk))
    except asyncio.CancelledError:
        print('[!] Tasks has been canceled')
        sys.exit(-1)

    with open(Path(original_assets_path) / 'version.txt', 'w', encoding='utf-8') as version_file:
        version_file.write('v')
        version_file.write(version)

if __name__ == '__main__':
    main(True, False, str(Path('./dev-resources/assets-latest')))
