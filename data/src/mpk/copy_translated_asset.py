#! /usr/bin/python
from pathlib import Path
from shutil import copyfile

from .common import log_normal, log_info


def main(translation_path, dist_path):
    log_normal("Copy translated assets to dist path...")
    for file_path in sorted((Path(translation_path) / "assets").glob("**/*")):
        if file_path.is_dir():
            continue
        if ".atlas_unpack" in str(file_path):
            continue
        if file_path.name.endswith(".psd"):
            continue

        dest_path = Path(dist_path) / file_path.relative_to(Path(translation_path))
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        log_info(f"Copy file: {file_path}")
        copyfile(str(file_path), str(dest_path))
    log_info("Copy complete")


if __name__ == "__main__":
    main(str(Path("./translation")), str(Path("..")))
