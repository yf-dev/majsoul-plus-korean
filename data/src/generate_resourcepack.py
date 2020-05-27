#! /usr/bin/python
import os
from pathlib import Path
import json
from datetime import datetime
lang = os.getenv('MAJSOUL_LANG', 'en')

def main(dist_path):
    resourcepack_data = {
        'id': 'korean',
        'version': f'2.{datetime.now().strftime("%Y%d%m.1%H%M%S")}',
        'name': '한국어',
        'author': 'Nesswit',
        'description': '인터페이스를 한국어로 표시합니다.',
        'preview': 'preview.png',
        'dependencies': {
            'majsoul_plus': '^2.0.0'
        },
        'replace': []
    }

    assets_path = Path(dist_path) / 'assets'
    for file_path in assets_path.glob('**/*'):
        if file_path.is_dir():
            continue
        resourcepack_data['replace'].append(file_path.relative_to(assets_path).as_posix())

    with open(Path(dist_path) / 'resourcepack.json', 'w', encoding='utf-8') as resourcepack_file:
        json.dump(resourcepack_data, resourcepack_file, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main(
        str(Path('..'))
    )