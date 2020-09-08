#! /usr/bin/python
import os
import csv
import json
import polib
from pathlib import Path
from hashlib import md5
from collections import OrderedDict
from datetime import datetime

from common import log_normal, log_debug, log_warn, log_info, log_error, AVAILABLE_LANGS

lang = os.getenv('MAJSOUL_LANG', 'en')
verbose = int(os.getenv('MAJSOUL_VERBOSE', 0)) == 1

class LanguageText():
    def __init__(self, source_filepath, source_lineno, language, text):
        self.source_filepath = source_filepath
        self.source_lineno = source_lineno
        self.language = language
        self.text = text

    def __repr__(self):
        return f"{self.language}: {self.text}"

class TString:
    def __init__(self, main_language, source_type, context):
        self.main_language = main_language
        self.source_type = source_type
        self.context = context
        self.texts = OrderedDict()
    
    def set_text(self, source_filepath, source_lineno, language, text):
        self.texts[language] = LanguageText(source_filepath, source_lineno, language, text)

    def get_text(self, language):
        if language in self.texts:
            return self.texts[language]
        return None

    def hash_text(self, language):
        return md5(self.get_text(language).text.encode()).hexdigest()

    def msgid(self):
        main_lang = self.main_language
        if not self.get_text(main_lang) and len(self.texts) > 0:
            main_lang = next(iter(self.texts))
        if self.source_type == "json-ui":
            return f"json|{self.context}|{self.hash_text(main_lang)}"
        return f"{self.source_type}|{self.get_text(main_lang).source_filepath}|{self.context}|{self.hash_text(main_lang)}"

    def msgctxt(self):
        main_lang = self.main_language
        if not self.get_text(main_lang) and len(self.texts) > 0:
            main_lang = next(iter(self.texts))
        return self.get_text(main_lang).text

    @classmethod
    def key(cls, source_type, context, source_filepath, source_lineno):
        if source_type == "sheet":
            return f"{source_type}|{context}|{source_filepath}|{source_lineno}"
        return f"{source_type}|{context}"

    def __repr__(self):
        return f"{self.context}({', '.join(repr(self.texts[t]) for t in self.texts)})"


class TStringData:
    def __init__(self, main_language):
        self.main_language = main_language
        self._t_strings = OrderedDict()

    def get(self, source_type, context, source_filepath, source_lineno, with_creation=False):
        key = TString.key(source_type, context, source_filepath, source_lineno)
        if key not in self._t_strings:
            if with_creation:
                self._t_strings[key] = TString(self.main_language, source_type, context)
            else:
                return None 
        return self._t_strings[key]

    def set(self, source_type, context, source_filepath, source_lineno, language, text):
        t_string = self.get(source_type, context, source_filepath, source_lineno, with_creation=True)
        t_string.set_text(source_filepath, source_lineno, language, text)

    @classmethod
    def merge(cls, t_string_datas):
        merged = TStringData(t_string_datas[0].main_language)
        for t_string_data in t_string_datas:
            for key, t_string in t_string_data._t_strings.items():
                merged._t_strings[key] = t_string
        return merged

    def write_pofiles(self, translation_path):
        rev_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S%z")
        for language in AVAILABLE_LANGS:
            log_info(f'Generate pofile for {language}...', verbose)
            po = polib.POFile(encoding='utf-8')
            po.metadata = {
                'PO-Revision-Date': f'{rev_date}',
                'MIME-Version': '1.0',
                'Language': AVAILABLE_LANGS[language],
                'Content-Type': 'text/plain; charset=utf-8',
                'Content-Transfer-Encoding': '8bit',
            }

            for key, t_string in self._t_strings.items():
                translated = t_string.get_text(language)

                if not translated:
                    continue

                entry = polib.POEntry(
                    msgctxt=t_string.msgctxt(),
                    msgid=t_string.msgid(),
                    msgstr=translated.text,
                    occurrences=[(translated.source_filepath, translated.source_lineno)] ,
                    encoding='utf-8'
                )
                po.append(entry)
                
            
            po.save(translation_path / f'translate_{language}.po')


def parse_ui_json_node(json_rows, node, path):
    if 'text' in node['props']:
        text = node['props']['text']
        if text:
            json_rows.append((path, text))
    if 'child' in node:
        for i, child in enumerate(node['child']):
            parse_ui_json_node(json_rows, child, f'{path}|{i}')

def parse_ui_json(json_paths):
    t_string_data = TStringData(lang)
    source_type = "json-ui"
    for json_path in json_paths:
        log_info(f'Read {json_path}...', verbose)
        source_filepath = json_path.name
        language = json_path.name[len('ui_'):-len('.json')]
        with open(json_path, 'r', encoding='utf-8') as jsonfile:
            json_data = json.load(jsonfile)
        json_rows = []
        for node_key in json_data:
            parse_ui_json_node(json_rows, json_data[node_key], node_key)
        for context, text in json_rows:
            t_string_data.set(source_type, context, source_filepath, 0, language, text)
    return t_string_data

def parse_xinshouyindao_json(json_paths):
    t_string_data = TStringData(lang)
    source_type = "json-xinshouyindao"
    for json_path in json_paths:
        log_info(f'Read {json_path}...', verbose)
        source_filepath = json_path.name
        language = json_path.name[len('xinshouyindao_'):-len('.json')]
        with open(json_path, 'r', encoding='utf-8') as jsonfile:
            json_data = json.load(jsonfile)
        json_rows = []
        for page in json_data["datas"]:
            page_id = '_'.join(page['page_id'].split('_')[1:])
            t_string_data.set(source_type, f"{page_id}|name", source_filepath, 0, language, page["name"])
            t_string_data.set(source_type, f"{page_id}|text", source_filepath, 0, language, page["text"])
    return t_string_data

def parse_bytes(bytes_paths):
    t_string_data = TStringData(lang)
    source_type = "bytes"
    for bytes_path in bytes_paths:
        log_info(f'Read {bytes_path}...', verbose)
        source_filepath = f"{bytes_path.parent.name}/{bytes_path.name}"
        language = bytes_path.name[len('100004_'):-len('.bytes')]
        with open(bytes_path, 'r', encoding='utf-8-sig') as bytesfile:
            source_lineno = 1
            for line in bytesfile:
                splited = line.split(":")
                line_id = splited[0]
                text = ":".join(splited[1:])
                context = f"{source_filepath[:-(1 + len(language) + len('.bytes'))]}|{line_id}"
                t_string_data.set(source_type, context, source_filepath, source_lineno, language, text)
                source_lineno += 1
    return t_string_data

def parse_csv(csv_path):
    t_string_data = TStringData(lang)
    source_type = "sheet"
    source_filepath = csv_path.name
    log_info(f'Read {csv_path}...', verbose)
    with open(csv_path, 'r', encoding='utf-8-sig') as csvfile:
        csv_reader = csv.DictReader(csvfile)

        has_voice_path = False
        header_prefixs = []
        for fieldname in csv_reader.fieldnames:
            if fieldname == lang or fieldname.endswith(f'_{lang}'):
                header_prefixs.append(fieldname[:-len(lang)])
            if fieldname == 'path' and csv_path.name == 'VoiceSound.csv':
                has_voice_path = True

        source_lineno = 2
        for row in csv_reader:
            for header_prefix in header_prefixs:
                context = f"{header_prefix}{lang}"
                if has_voice_path:
                    context = f"{context}({row['path']})"
                
                for language in AVAILABLE_LANGS:
                    header = f"{header_prefix}{language}"
                    if header in row:
                        t_string_data.set(source_type, context, source_filepath, source_lineno, language, row[header])
            source_lineno += 1
    return t_string_data


def main(translation_path, original_assets_path, temp_path):
    t_string_datas = []

    log_info('Read ui json files...', verbose)
    ui_json_dir_path = Path(original_assets_path) / 'uiconfig'
    t_string_datas.append(parse_ui_json(sorted(ui_json_dir_path.glob('ui_*.json'))))

    log_info('Read xinshouyindao json files...', verbose)
    xinshouyindao_json_dir_path = Path(original_assets_path) / 'docs'
    t_string_datas.append(parse_xinshouyindao_json(sorted(xinshouyindao_json_dir_path.glob('xinshouyindao_*.json'))))

    log_info('Read bytes files...', verbose)
    bytes_dir_path = Path(original_assets_path) / 'docs' / 'spot'
    t_string_datas.append(parse_bytes(sorted(bytes_dir_path.glob('**/*.bytes'))))

    log_info('Read csv files...', verbose)
    csv_dir_path = Path(temp_path) / 'csv'
    for csv_path in sorted(csv_dir_path.glob('*.csv')):
        t_string_datas.append(parse_csv(csv_path))

    merged = TStringData.merge(t_string_datas)
    merged.write_pofiles(Path(translation_path))
       

if __name__ == '__main__':
    main(
        str(Path('./translation')),
        str(Path('./assets-original')),
        str(Path('./temp')),
    )
