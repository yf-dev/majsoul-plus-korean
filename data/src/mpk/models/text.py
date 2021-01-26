#! /usr/bin/python
from collections import OrderedDict
from datetime import datetime
from hashlib import md5
from pathlib import Path
import csv
import json
import polib

from ..common import AVAILABLE_LANGS, log_info, log_debug, log_warn, mpk_lang


class LanguageString:
    """Single string of specific language"""

    def __init__(self, source_filepath, source_lineno, language, text):
        self.source_filepath = source_filepath
        self.source_lineno = source_lineno
        self.language = language
        self.text = text

    def __repr__(self):
        return f"{self.language}: {self.text}"


class TranslationString:
    """
    Translated string with multiple LanguageString
    """

    def __init__(self, main_language, source_type, context):
        self.main_language = main_language
        self.source_type = source_type
        self.context = context
        self.language_string_map = OrderedDict()

    def set_string(self, source_filepath, source_lineno, language, text):
        """Set string for specific language"""
        self.language_string_map[language] = LanguageString(
            source_filepath, source_lineno, language, text
        )

    def get_string(self, language):
        """
        Get string for specific language

        If the string is not exist, return None
        """
        if language in self.language_string_map:
            return self.language_string_map[language]
        return None

    def hash_text(self, language):
        """Generate hash from specific language"""
        return self.generate_hash(self.get_string(language).text)

    def get_main_lang(self):
        """Get main language"""
        main_lang = self.main_language
        if not self.get_string(main_lang) and len(self.language_string_map) > 0:
            # There is no string for main language.
            # Use alternative language
            main_lang = sorted(list(self.language_string_map.keys()))[0]
        return main_lang

    def msgid(self):
        """Generate message ID"""
        main_lang = self.get_main_lang()
        if self.source_type == "json-ui":
            # For legacy translation format
            return f"json|{self.context}|{self.hash_text(main_lang)}"
        return f"{self.source_type}|{self.get_string(main_lang).source_filepath}|{self.context}|{self.hash_text(main_lang)}"

    def msgctxt(self):
        """Generate original string"""
        main_lang = self.get_main_lang()
        return self.get_string(main_lang).text

    @classmethod
    def key(cls, source_type, context, source_filepath, original_string=None):
        """
        Generate unique key

        original_string parameter is only for sheet source
        """
        if source_type == "sheet":
            return f"{source_type}|{context}|{source_filepath}|{cls.generate_hash(original_string)}"
        return f"{source_type}|{context}"

    @classmethod
    def generate_hash(cls, text):
        """Generate hash from text"""
        return md5(text.encode()).hexdigest()

    def __repr__(self):
        return f"{self.context}({', '.join(repr(self.language_string_map[t]) for t in self.language_string_map)})"


class TranslationDataset:
    """
    Translated dataset with multiple TranslationString
    """

    def __init__(self, main_language):
        self.main_language = main_language
        self.translation_string_map = OrderedDict()

    def get(
        self,
        source_type,
        context,
        source_filepath,
        original_string=None,
        with_creation=False,
    ):
        """
        Get single TranslationString

        original_string parameter is only for sheet source
        """
        key = TranslationString.key(
            source_type, context, source_filepath, original_string=original_string
        )
        if key not in self.translation_string_map:
            if with_creation:
                self.translation_string_map[key] = TranslationString(
                    self.main_language, source_type, context
                )
            else:
                return None
        return self.translation_string_map[key]

    def set(
        self,
        source_type,
        context,
        source_filepath,
        source_lineno,
        language,
        text,
        original_string=None,
    ):
        """
        Set single TranslationString

        original_string parameter is only for sheet source
        """
        translation_string = self.get(
            source_type,
            context,
            source_filepath,
            original_string=original_string,
            with_creation=True,
        )
        translation_string.set_string(source_filepath, source_lineno, language, text)

    @classmethod
    def merge(cls, translation_datasets):
        """Merge multiple TranslationDataset into single TranslationDataset"""
        merged = TranslationDataset(translation_datasets[0].main_language)
        for translation_dataset in translation_datasets:
            for (
                key,
                translation_string,
            ) in translation_dataset.translation_string_map.items():
                merged.translation_string_map[key] = translation_string
        return merged

    def write_pofiles(self, translation_path):
        """Write po files"""
        rev_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S%z")
        for language in AVAILABLE_LANGS:
            log_info(f"Generate pofile for {language}...")
            pofile = polib.POFile(encoding="utf-8")
            pofile.metadata = {
                "PO-Revision-Date": f"{rev_date}",
                "MIME-Version": "1.0",
                "Language": AVAILABLE_LANGS[language],
                "Content-Type": "text/plain; charset=utf-8",
                "Content-Transfer-Encoding": "8bit",
            }

            for _, translation_string in self.translation_string_map.items():
                translated = translation_string.get_string(language)

                if not translated:
                    continue

                entry = polib.POEntry(
                    msgctxt=translation_string.msgctxt(),
                    msgid=translation_string.msgid(),
                    msgstr=translated.text,
                    occurrences=[
                        (translated.source_filepath, translated.source_lineno)
                    ],
                    encoding="utf-8",
                )
                pofile.append(entry)

            pofile.save(translation_path / f"translate_{language}.po")

    def read_pofile(self, pofile_path, language):
        """read po file"""
        log_info(f"Read {pofile_path.name}...")
        pofile = polib.pofile(pofile_path, encoding="utf-8")
        for entry in pofile:
            splited_msgid = entry.msgid.split("|")
            source_type = splited_msgid[0]
            if source_type == "json":
                source_type = "json-ui"  # For legacy translation format
                context = "|".join(splited_msgid[1:-1])
                source_filepath = entry.occurrences[0]
            elif source_type == "json-xinshouyindao":
                context = "|".join(splited_msgid[2:4])
                source_filepath = entry.occurrences[0]
            elif source_type == "bytes":
                context = "|".join(splited_msgid[2:4])
                source_filepath = entry.occurrences[0]
            elif source_type == "sheet":
                context = splited_msgid[2]
                source_filepath = splited_msgid[1]
            else:
                log_warn(f"Unknown source type: {source_type}")
                continue
            source_lineno = entry.occurrences[1] if len(entry.occurrences) > 1 else 0
            self.set(
                source_type,
                context,
                source_filepath,
                source_lineno,
                language,
                entry.msgstr,
                original_string=entry.msgctxt,
            )


class Translator:
    def __init__(self):
        self._translation_dataset = TranslationDataset(mpk_lang)
        self.source_type = "unknown"

    def load_from_game_objects(self, game_objects_root_path):
        raise NotImplementedError()

    def save_to_game_objects(self, game_objects_root_path, dist_path):
        raise NotImplementedError()

    def filtered_translation_dataset(self, translation_dataset):
        new_dataset = TranslationDataset(translation_dataset.main_language)
        for (
            key,
            translation_string,
        ) in translation_dataset.translation_string_map.items():
            if translation_string.source_type == self.source_type:
                new_dataset.translation_string_map[key] = translation_string
        return new_dataset

    @property
    def translation_dataset(self):
        return self._translation_dataset

    @translation_dataset.setter
    def translation_dataset(self, value):
        self._translation_dataset = self.filtered_translation_dataset(value)


class UiJsonTranslator(Translator):
    def __init__(self):
        super().__init__()
        self.source_type = "json-ui"

    def load_from_game_objects(self, game_objects_root_path):
        json_paths = sorted(
            (Path(game_objects_root_path) / "uiconfig").glob("ui_*.json")
        )
        self.translation_dataset = TranslationDataset(mpk_lang)
        for json_path in json_paths:
            log_info(f"Read {json_path}...")
            source_filepath = json_path.name
            language = json_path.name[len("ui_") : -len(".json")]

            with open(json_path, "r", encoding="utf-8") as jsonfile:
                json_data = json.load(jsonfile)

            json_rows = []
            for node_key in json_data:
                self.parse_node(json_rows, json_data[node_key], node_key)

            for context, text in json_rows:
                self.translation_dataset.set(
                    self.source_type, context, source_filepath, 0, language, text
                )

    def save_to_game_objects(self, game_objects_root_path, dist_path):
        ui_json = None

        log_info(f"Read ui_{mpk_lang}.json...")
        with open(
            Path(game_objects_root_path) / "uiconfig" / f"ui_{mpk_lang}.json",
            "r",
            encoding="utf-8",
        ) as jsonfile:
            ui_json = json.load(jsonfile)

        for (
            translation_string
        ) in self.translation_dataset.translation_string_map.values():
            target = translation_string.get_string(mpk_lang)
            if target is None:
                continue
            translated = translation_string.get_string("ko")
            if translated is None:
                continue
            path = translation_string.context
            node = None
            try:
                log_debug(f"Convert {path}")
                node = self.get_node(ui_json, path.split("|"))
            except Exception:  # pylint: disable=broad-except
                log_warn(f"Cannot access {path}")
                continue

            if "text" not in node["props"]:
                log_warn(f"Node has not text on {path}: '{target.text}'")
                continue
            elif node["props"]["text"] != target.text:
                log_warn(
                    f"Target is not matched on {path}: '{node['props']['text']}' != '{target.text}'"
                )
                continue

            self.update_value(ui_json, path.split("|"), translated.text)

        log_info(f"Write ui_{mpk_lang}.json...")
        target_path = Path(dist_path) / "assets" / "uiconfig" / f"ui_{mpk_lang}.json"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as jsonfile:
            json.dump(ui_json, jsonfile, separators=(",", ":"), ensure_ascii=False)

    @classmethod
    def parse_node(cls, json_rows, node, path):
        if "text" in node["props"]:
            text = node["props"]["text"]
            if text:
                json_rows.append((path, text))
        if "child" in node:
            for i, child in enumerate(node["child"]):
                cls.parse_node(json_rows, child, f"{path}|{i}")

    @classmethod
    def get_node(cls, root, path_list):
        copied_path_list = list(path_list)
        node = root[copied_path_list.pop(0)]
        while copied_path_list:
            node = node["child"][int(copied_path_list.pop(0))]
        return node

    @classmethod
    def update_value(cls, root, path_list, value):
        node = cls.get_node(root, path_list)
        node["props"]["text"] = value

        copied_path_list = list(path_list)
        while len(copied_path_list) > 1:
            i = int(copied_path_list.pop())
            parent = cls.get_node(root, copied_path_list)
            parent["child"][i] = node
            node = parent
        root[copied_path_list[0]] = node


class XinshouyindaoJsonTranslator(Translator):
    def __init__(self):
        super().__init__()
        self.source_type = "json-xinshouyindao"

    def load_from_game_objects(self, game_objects_root_path):
        json_paths = sorted(
            (Path(game_objects_root_path) / "docs").glob("xinshouyindao_*.json")
        )
        self.translation_dataset = TranslationDataset(mpk_lang)
        for json_path in json_paths:
            log_info(f"Read {json_path}...")
            source_filepath = json_path.name
            language = json_path.name[len("xinshouyindao_") : -len(".json")]
            with open(json_path, "r", encoding="utf-8") as jsonfile:
                json_data = json.load(jsonfile)
            for page in json_data["datas"]:
                page_id = "_".join(page["page_id"].split("_")[1:])
                self.translation_dataset.set(
                    self.source_type,
                    f"{page_id}|name",
                    source_filepath,
                    0,
                    language,
                    page["name"],
                )
                self.translation_dataset.set(
                    self.source_type,
                    f"{page_id}|text",
                    source_filepath,
                    0,
                    language,
                    page["text"],
                )

    def save_to_game_objects(self, game_objects_root_path, dist_path):
        xinshouyindao_json = None
        xinshouyindao_json_path = (
            Path(game_objects_root_path) / "docs" / f"xinshouyindao_{mpk_lang}.json"
        )

        log_info(f"Read xinshouyindao_{mpk_lang}.json...")
        with open(
            xinshouyindao_json_path,
            "r",
            encoding="utf-8",
        ) as jsonfile:
            xinshouyindao_json = json.load(jsonfile)

        for index, page in enumerate(xinshouyindao_json["datas"]):
            page_id = "_".join(page["page_id"].split("_")[1:])
            source_filepath = xinshouyindao_json_path.name

            # Apply name
            translation_string_name = self.translation_dataset.get(
                self.source_type, f"{page_id}|name", source_filepath
            )
            if translation_string_name is not None:
                target_name = translation_string_name.get_string(mpk_lang)
                translated_name = translation_string_name.get_string("ko")
                if target_name is not None and translated_name is not None:
                    xinshouyindao_json["datas"][index]["name"] = translated_name.text

            # Apply text
            translation_string_text = self.translation_dataset.get(
                self.source_type, f"{page_id}|text", source_filepath
            )
            if translation_string_text is not None:
                target_text = translation_string_text.get_string(mpk_lang)
                translated_text = translation_string_text.get_string("ko")
                if target_text is not None and translated_text is not None:
                    xinshouyindao_json["datas"][index]["text"] = translated_text.text

        log_info(f"Write xinshouyindao_{mpk_lang}.json...")
        target_path = (
            Path(dist_path) / "assets" / "docs" / f"xinshouyindao_{mpk_lang}.json"
        )
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as jsonfile:
            json.dump(
                xinshouyindao_json, jsonfile, separators=(",", ":"), ensure_ascii=False
            )


class BytesTranslator(Translator):
    def __init__(self):
        super().__init__()
        self.source_type = "bytes"

    def load_from_game_objects(self, game_objects_root_path):
        bytes_paths = sorted(
            (Path(game_objects_root_path) / "docs" / "spot").glob("**/*.bytes")
        )
        self.translation_dataset = TranslationDataset(mpk_lang)
        for bytes_path in bytes_paths:
            log_info(f"Read {bytes_path}...")
            source_filepath = f"{bytes_path.parent.name}/{bytes_path.name}"
            language = bytes_path.name[len("100004_") : -len(".bytes")]
            with open(bytes_path, "r", encoding="utf-8-sig") as bytesfile:
                source_lineno = 1
                for line in bytesfile:
                    splited = line.split(":")
                    line_id = splited[0]
                    text = ":".join(splited[1:])
                    context = f"{source_filepath[:-(1 + len(language) + len('.bytes'))]}|{line_id}"

                    self.translation_dataset.set(
                        self.source_type,
                        context,
                        source_filepath,
                        source_lineno,
                        language,
                        text,
                    )
                    source_lineno += 1

    def save_to_game_objects(self, game_objects_root_path, dist_path):
        bytes_paths = sorted(
            (Path(game_objects_root_path) / "docs" / "spot").glob(
                f"**/*_{mpk_lang}.bytes"
            )
        )
        for bytes_path in bytes_paths:
            log_info(f"Read {bytes_path}...")
            source_filepath = f"{bytes_path.parent.name}/{bytes_path.name}"
            new_bytes = ""
            is_translated = False
            with open(bytes_path, "r", encoding="utf-8-sig") as bytesfile:
                source_lineno = 1
                for line in bytesfile:
                    splited = line.split(":")
                    line_id = splited[0]
                    context = f"{source_filepath[:-(1 + len(mpk_lang) + len('.bytes'))]}|{line_id}"

                    translation_string = self.translation_dataset.get(
                        self.source_type, context, source_filepath
                    )

                    if translation_string is not None:
                        target = translation_string.get_string(mpk_lang)
                        translated = translation_string.get_string("ko")
                        if target is not None and translated is not None:
                            line = f"{line_id}:{translated.text}"
                            is_translated = True

                    new_bytes += line
                    source_lineno += 1

            if not is_translated:
                continue

            log_info(f"Write {bytes_path}...")
            target_path = (
                Path(dist_path)
                / "assets"
                / "docs"
                / "spot"
                / bytes_path.parent.name
                / bytes_path.name
            )
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "w", encoding="utf-8-sig") as bytesfile:
                bytesfile.write(new_bytes)


class CsvTranslator(Translator):
    def __init__(self):
        super().__init__()
        self.source_type = "sheet"

    def load_from_game_objects(self, temp_path):  # pylint: disable=arguments-differ
        csv_paths = sorted((Path(temp_path) / "csv").glob("*.csv"))
        temp_translation_datasets = []
        for csv_path in csv_paths:
            temp_translation_dataset = TranslationDataset(mpk_lang)
            source_filepath = csv_path.name
            log_info(f"Read {csv_path}...")
            with open(csv_path, "r", encoding="utf-8-sig") as csvfile:
                csv_reader = csv.DictReader(csvfile)

                has_voice_path = False
                header_prefixs = []
                for fieldname in csv_reader.fieldnames:
                    if fieldname == mpk_lang or fieldname.endswith(f"_{mpk_lang}"):
                        header_prefixs.append(fieldname[: -len(mpk_lang)])
                    if fieldname == "path" and csv_path.name == "VoiceSound.csv":
                        has_voice_path = True

                source_lineno = 2
                for row in csv_reader:
                    for header_prefix in header_prefixs:
                        context = f"{header_prefix}{mpk_lang}"
                        if has_voice_path:
                            context = f"{context}({row['path']})"

                        for language in AVAILABLE_LANGS:
                            header = f"{header_prefix}{language}"
                            original_header = f"{header_prefix}{mpk_lang}"
                            if header in row:
                                temp_translation_dataset.set(
                                    self.source_type,
                                    context,
                                    source_filepath,
                                    source_lineno,
                                    language,
                                    row[header],
                                    original_string=row[original_header],
                                )
                    source_lineno += 1
            temp_translation_datasets.append(temp_translation_dataset)
        self.translation_dataset = TranslationDataset.merge(temp_translation_datasets)

    def save_to_game_objects(self, temp_path, _):  # pylint: disable=arguments-differ
        csv_paths = sorted((Path(temp_path) / "csv").glob("*.csv"))
        for csv_path in csv_paths:
            source_filepath = csv_path.name
            log_info(f"Read {csv_path}...")
            rows = []
            fieldnames = None
            is_translated = False
            with open(csv_path, "r", encoding="utf-8-sig") as csvfile:
                csv_reader = csv.DictReader(csvfile)

                has_voice_path = False
                header_prefixs = []
                fieldnames = csv_reader.fieldnames
                for fieldname in csv_reader.fieldnames:
                    if fieldname == mpk_lang or fieldname.endswith(f"_{mpk_lang}"):
                        header_prefixs.append(fieldname[: -len(mpk_lang)])
                    if fieldname == "path" and csv_path.name == "VoiceSound.csv":
                        has_voice_path = True

                source_lineno = 2
                for row in csv_reader:
                    for header_prefix in header_prefixs:
                        context = f"{header_prefix}{mpk_lang}"
                        if has_voice_path:
                            context = f"{context}({row['path']})"

                        header = f"{header_prefix}{mpk_lang}"
                        if header in row:
                            translation_string = self.translation_dataset.get(
                                self.source_type,
                                context,
                                source_filepath,
                                original_string=row[header],
                            )

                            if translation_string is not None:
                                target = translation_string.get_string(mpk_lang)
                                translated = translation_string.get_string("ko")
                                if target is not None and translated is not None:
                                    row[header] = translated.text
                                    is_translated = True

                    rows.append(row)
                    source_lineno += 1

            if not is_translated:
                continue

            log_info(f"Write {csv_path}...")
            with open(csv_path, "w", encoding="utf-8-sig") as csvfile:
                sheet_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                sheet_writer.writeheader()
                sheet_writer.writerows(rows)