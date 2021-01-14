#! /usr/bin/python
from pathlib import Path

from .common import log_normal, log_info
from .unpack_atlas import main as unpack_atlas


def main(original_assets_path):
    log_normal("Unpack all atlas files...")
    for atlas_unpack_path in sorted(Path(original_assets_path).glob("**/*.atlas")):
        unpack_atlas(str(atlas_unpack_path))
    log_info("Unpack complete")


if __name__ == "__main__":
    main(str(Path("./assets-original")))
