#! /usr/bin/python
from pathlib import Path
import csv
import polib

from .common import log_normal, log_debug, log_info

HASH_LEN = 32


def main(translation_path):
    log_normal("Apply translate_ko.po to translate_json.csv and translate_sheet.csv...")
    translation_path = Path(translation_path)

    json_entries = []
    sheet_entries = []

    log_info("Read translate_ko.po...")
    pofile = polib.pofile(translation_path / "translate_ko.po", encoding="utf-8")

    log_info("Split entries...")
    for entry in pofile.translated_entries():
        if entry.msgid.startswith("json|"):
            log_debug(f"Add {entry.msgid} to json data")
            json_entries.append(entry)
        elif entry.msgid.startswith("sheet|"):
            log_debug(f"Add {entry.msgid} to sheet data")
            sheet_entries.append(entry)
        else:
            pass
            # error_msg = f'Unexpected msgid: {entry.msgid}'
            # log_error(error_msg)
            # raise Exception(error_msg)

    log_info("Write translate_json.csv...")
    with open(
        translation_path / "translate_json.csv", "w", encoding="utf-8-sig", newline=""
    ) as csvfile:
        csv_writer = csv.writer(csvfile)
        log_info("Write translate_json.csv rows...")
        csv_writer.writerow(["location", "source", "target"])
        for entry in json_entries:
            path = entry.msgid[len("json|") : -(HASH_LEN + 1)]
            target = entry.msgctxt.replace("\\", "\\\\").replace("\n", "\\n")
            translated = entry.msgstr.replace("\\", "\\\\").replace("\n", "\\n")
            log_debug(f"Write {entry.msgid} to {path}")
            csv_writer.writerow([path, target, translated])

    log_info("Write translate_sheet.csv...")
    with open(
        translation_path / "translate_sheet.csv", "w", encoding="utf-8-sig", newline=""
    ) as csvfile:
        csv_writer = csv.writer(csvfile)
        log_info("Write translate_sheet.csv rows...")
        csv_writer.writerow(["location", "context", "source", "target"])
        for entry in sheet_entries:
            full_path = entry.msgid[len("sheet|") : -(HASH_LEN + 1)]
            sheet_path = "|".join(full_path.split("|")[:-1])
            header = full_path.split("|")[-1]
            target = entry.msgctxt.replace("\\", "\\\\").replace("\n", "\\n")
            translated = entry.msgstr.replace("\\", "\\\\").replace("\n", "\\n")
            log_debug(f"Write {entry.msgid} to {sheet_path}")
            csv_writer.writerow([sheet_path, header, target, translated])

    log_info("Apply complete")


if __name__ == "__main__":
    main(str(Path("./translation")))
