#! /usr/bin/python
import json
import csv
from pathlib import Path
import os
from common import log_normal, log_debug, log_warn, log_info, log_error
lang = os.getenv('MAJSOUL_LANG', 'en')
verbose = int(os.getenv('MAJSOUL_VERBOSE', 0)) == 1

def get_node(root, path_indexes=None):
    current_node = root
    if path_indexes is None:
        path_indexes = []
    for i in path_indexes:
        current_node = current_node['child'][i]
    return current_node

def apply_node(root, path_indexes, node):
    log_debug(f'Apply data to {path_indexes}', verbose)
    if path_indexes is None:
        path_indexes = []
    copied_indexes = list(path_indexes)
    while copied_indexes:
        i = copied_indexes.pop()
        target_node = get_node(root, copied_indexes)
        target_node['child'][i] = node
        node = target_node

def update_node(root, check_target, update_data, path_indexes=None):
    current_node = root
    if path_indexes is None:
        path_indexes = []
    else:
        current_node = get_node(root, path_indexes)
    for i, child_node in enumerate(current_node['child']):
        if check_target(child_node):
            child_node = update_data(child_node)
            apply_node(root, path_indexes + [i], child_node)
        if 'child' in child_node:
            update_node(root, check_target, update_data, path_indexes + [i])

def main(original_assets_path, dist_path):
    if lang != 'en':
        return
    
    log_normal('Generate scene data...', verbose)

    def mjdesktop_en_check_target_chang(node):
        if 'customProps' not in node:
            return False
        customProps = node['customProps']
        if 'materials' not in customProps:
            return False
        materials = customProps['materials']
        if (len(materials) != 1) or ('path' not in materials[0]):
            return False
        path = materials[0]['path']
        if path != 'Assets/Resource/table/tablemid_en/chang.lmat':
            return False
        return True

    def mjdesktop_en_update_data_chang(node):
        node['customProps']['translate'][0] = 0.0028
        node['customProps']['scale'][0] *= 1.2
        node['customProps']['scale'][1] *= 1.2
        node['customProps']['scale'][2] *= 1.2
        return node

    def mjdesktop_en_check_target_ju(node):
        if 'customProps' not in node:
            return False
        customProps = node['customProps']
        if 'materials' not in customProps:
            return False
        materials = customProps['materials']
        if (len(materials) != 1) or ('path' not in materials[0]):
            return False
        path = materials[0]['path']
        if path != 'Assets/Resource/table/tablemid_en/ju.lmat':
            return False
        return True

    def mjdesktop_en_update_data_ju(node):
        node['customProps']['translate'][0] = 0.0028
        node['customProps']['scale'][0] *= 1.1
        node['customProps']['scale'][1] *= 1.1
        node['customProps']['scale'][2] *= 1.1
        return node

    log_info('Read mjdesktop_en.lh...', verbose)
    mjdesktop_en_lh = None
    with open(Path(original_assets_path) / 'scene' / 'mjdesktop_en.lh', 'r', encoding='utf-8') as jsonfile:
        mjdesktop_en_lh = json.load(jsonfile)

    log_info('Update chang data on mjdesktop_en.lh...', verbose)
    update_node(mjdesktop_en_lh, mjdesktop_en_check_target_chang, mjdesktop_en_update_data_chang)
    log_info('Update ju data on mjdesktop_en.lh...', verbose)
    update_node(mjdesktop_en_lh, mjdesktop_en_check_target_ju, mjdesktop_en_update_data_ju)

    log_info('Write mjdesktop_en.lh...', verbose)
    mjdesktop_en_lh_dist_path = Path(dist_path) / 'assets' / 'scene' / 'mjdesktop_en.lh'
    mjdesktop_en_lh_dist_path.parent.mkdir(parents=True, exist_ok=True)
    with open(mjdesktop_en_lh_dist_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(mjdesktop_en_lh, jsonfile, separators=(',', ':'), ensure_ascii=False)

    log_info('Read mjdesktop_en.ls...', verbose)
    mjdesktop_en_ls = None
    with open(Path(original_assets_path) / 'scene' / 'mjdesktop_en.ls', 'r', encoding='utf-8') as jsonfile:
        mjdesktop_en_ls = json.load(jsonfile)

    log_info('Update chang data on mjdesktop_en.ls...', verbose)
    update_node(mjdesktop_en_ls, mjdesktop_en_check_target_chang, mjdesktop_en_update_data_chang)
    log_info('Update ju data on mjdesktop_en.ls...', verbose)
    update_node(mjdesktop_en_ls, mjdesktop_en_check_target_ju, mjdesktop_en_update_data_ju)

    log_info('Write mjdesktop_en.ls...', verbose)
    mjdesktop_en_ls_dist_path = Path(dist_path) / 'assets' / 'scene' / 'mjdesktop_en.ls'
    mjdesktop_en_ls_dist_path.parent.mkdir(parents=True, exist_ok=True)
    with open(mjdesktop_en_ls_dist_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(mjdesktop_en_ls, jsonfile, separators=(',', ':'), ensure_ascii=False)

    log_info('Generate complete', verbose)

if __name__ == '__main__':
    main(
        str(Path('./assets-original')),
        str(Path('..'))
    )