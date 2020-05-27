#! /usr/bin/python
import os
import urllib.request
import shutil
import json
from pathlib import Path
from multiprocessing.pool import ThreadPool

lang = os.getenv('MAJSOUL_LANG', 'en')

def download(url):
    filepath = url['target'] / url['path']
    skip_exist = True
    if skip_exist and filepath.exists():
        return f'[.] Skip - {filepath}'

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

def main(original_assets_path):
    server = None
    if lang == 'en':
        server = 'https://mahjongsoul.game.yo-star.com'
    elif lang == 'jp':
        server = 'https://game.mahjongsoul.com'

    THREAD = 16

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
            urls.append({
                'server': server,
                'prefix': res_dict[res]['prefix'],
                'path': res,
                'target': Path(original_assets_path)
            })

    results = ThreadPool(THREAD).imap_unordered(download, urls)
    for result in results:
        print(result)

if __name__ == '__main__':
    main(str(Path('./dev-resources/assets-latest')))

