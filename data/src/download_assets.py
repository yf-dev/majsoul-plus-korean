#! /usr/bin/python
import os
import urllib.request
import shutil
import json
from pathlib import Path
from multiprocessing.pool import ThreadPool
from common import order_version

lang = os.getenv('MAJSOUL_LANG', 'en')

def download(url):
    filepath = url['target'] / url['path']

    try:
        full_url = f'{url["server"]}/{url["prefix"]}/{url["path"]}'.replace(' ', '%20')
        with urllib.request.urlopen(full_url) as response:
            Path(filepath.parent).mkdir(parents=True, exist_ok=True)
            with open(filepath, 'wb') as out_file:
                if url['path'].startswith('en/extendRes/'):
                    byte = response.read(1)
                    while byte != b"":
                        out_file.write(bytes([byte[0] ^ 0x49]))
                        byte = response.read(1)
                else:
                    shutil.copyfileobj(response, out_file)
    except urllib.error.HTTPError as e:
        return f'[!] Download Failed({e.code}) - {filepath}'
    return f'[+] Download OK - {filepath}'

def main(overwrite_exist, force_update, original_assets_path):
    server = None
    if lang == 'en':
        server = 'https://mahjongsoul.game.yo-star.com'
    elif lang == 'jp':
        server = 'https://game.mahjongsoul.com'

    THREAD = 16

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

    results = ThreadPool(THREAD).imap_unordered(download, urls)
    for result in results:
        print(result)

    with open(Path(original_assets_path) / 'version.txt', 'w', encoding='utf-8') as version_file:
        version_file.write('v')
        version_file.write(version)

if __name__ == '__main__':
    main(False, False, str(Path('./dev-resources/assets-latest')))

