#! /usr/bin/python
from datetime import datetime
from pathlib import Path
import json

from .common import log_normal, log_info, mpk_resourcepack_id, mpk_resourcepack_name


def main(dist_path):
    log_normal("Generate resourcepack.json...")
    resourcepack_data = {
        "id": mpk_resourcepack_id,
        "version": f'3.0.{datetime.now().strftime("%Y%m%d%H%M%S")}',
        "name": mpk_resourcepack_name,
        "author": "Nesswit",
        "description": "인터페이스를 한국어로 표시합니다.",
        "preview": "preview.png",
        "dependencies": {"majsoul_plus": "^2.0.0"},
        "replace": [],
    }

    log_info("Collect asset paths...")
    assets_path = Path(dist_path) / "assets"
    for file_path in sorted(assets_path.glob("**/*")):
        if file_path.is_dir():
            continue
        if file_path.name == ".gitkeep":
            continue
        resourcepack_data["replace"].append(
            file_path.relative_to(assets_path).as_posix()
        )

    log_info("Write resourcepack.json...")
    with open(
        Path(dist_path) / "resourcepack.json", "w", encoding="utf-8"
    ) as resourcepack_file:
        json.dump(resourcepack_data, resourcepack_file, indent=2, ensure_ascii=False)

    log_info("Generate complete")


if __name__ == "__main__":
    main(str(Path("..")))
