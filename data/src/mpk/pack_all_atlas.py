#! /usr/bin/python
from pathlib import Path

from .common import log_normal, log_info
from .pack_atlas import main as pack_atlas


def main(size_factor, translation_path, target_path):
    log_normal("Pack all atlas files...")
    assets_path = Path(translation_path) / "assets"
    if not target_path:
        target_path = str(assets_path)
    for atlas_unpack_path in sorted(assets_path.glob("**/*.atlas_unpack")):
        new_target_path = Path(target_path) / atlas_unpack_path.relative_to(assets_path)
        pack_atlas(size_factor, str(atlas_unpack_path), str(new_target_path.parent))
    log_info("Pack complete")


if __name__ == "__main__":
    main(8, str(Path("./translation")), str(Path("./dist/korean/assets")))
