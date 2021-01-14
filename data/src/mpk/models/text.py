#! /usr/bin/python
from collections import OrderedDict
from datetime import datetime
from hashlib import md5
import polib

from ..common import AVAILABLE_LANGS, log_info


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
        return md5(self.get_string(language).text.encode()).hexdigest()

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
    def key(cls, source_type, context, source_filepath, source_lineno):
        """Generate unique key"""
        if source_type == "sheet":
            return f"{source_type}|{context}|{source_filepath}|{source_lineno}"
        return f"{source_type}|{context}"

    def __repr__(self):
        return f"{self.context}({', '.join(repr(self.language_string_map[t]) for t in self.language_string_map)})"


class TranslationDataset:
    """
    Translated dataset with multiple TranslationString
    """

    def __init__(self, main_language):
        self.main_language = main_language
        self._translation_string_map = OrderedDict()

    def get(
        self, source_type, context, source_filepath, source_lineno, with_creation=False
    ):
        """
        Get single TranslationString
        """
        key = TranslationString.key(
            source_type, context, source_filepath, source_lineno
        )
        if key not in self._translation_string_map:
            if with_creation:
                self._translation_string_map[key] = TranslationString(
                    self.main_language, source_type, context
                )
            else:
                return None
        return self._translation_string_map[key]

    def set(self, source_type, context, source_filepath, source_lineno, language, text):
        """Set single TranslationString"""
        translation_string = self.get(
            source_type, context, source_filepath, source_lineno, with_creation=True
        )
        translation_string.set_string(source_filepath, source_lineno, language, text)

    @classmethod
    def merge(cls, translation_datasets):
        # pylint: disable=protected-access
        """Merge multiple TranslationDataset into single TranslationDataset"""
        merged = TranslationDataset(translation_datasets[0].main_language)
        for translation_dataset in translation_datasets:
            for (
                key,
                translation_string,
            ) in translation_dataset._translation_string_map.items():
                merged._translation_string_map[key] = translation_string
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

            for _, translation_string in self._translation_string_map.items():
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
