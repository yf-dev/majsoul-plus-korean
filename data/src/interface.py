#! /usr/bin/python
from pathlib import Path
import argparse
import os
import shutil
import sys

from mpk.apply_translation_json import main as apply_translation_json
from mpk.apply_translation_po import main as apply_translation_po
from mpk.apply_translation_sheet import main as apply_translation_sheet
from mpk.build_sheets import main as build_sheets
from mpk.common import run_cmd, log_normal, log_debug
from mpk.copy_cached_asset import main as copy_cached_asset
from mpk.copy_translated_asset import main as copy_translated_asset
from mpk.download_assets import main as download_assets
from mpk.export_sheets import main as export_sheets
from mpk.extract_chars import main as extract_chars
from mpk.generate_fonts import main as generate_fonts
from mpk.generate_resourcepack import main as generate_resourcepack
from mpk.generate_scene import main as generate_scene
from mpk.generate_sheet_proto import main as generate_sheet_proto
from mpk.generate_translation_po import main as generate_translation_po
from mpk.merge_all_atlas import main as merge_all_atlas
from mpk.pack_all_atlas import main as pack_all_atlas
from mpk.pack_atlas import main as pack_atlas
from mpk.unpack_all_atlas import main as unpack_all_atlas
from mpk.unpack_atlas import main as unpack_atlas


DEFAULT_PATHS = {}

if getattr(sys, "frozen", False):
    # bundle env
    DEFAULT_PATHS["dist"] = str(Path("."))
    DEFAULT_PATHS["cached_static"] = str(Path("../../static"))
    DEFAULT_PATHS["original_assets"] = str(Path("./data/assets-original"))
    DEFAULT_PATHS["translation"] = str(Path("./data/translation"))
    DEFAULT_PATHS["temp"] = str(Path("./data/temp"))
    DEFAULT_PATHS["protoc"] = str(Path("./data/utils/protoc/bin/protoc.exe"))
    DEFAULT_PATHS["fontbm"] = str(Path("./data/utils/fontbm/fontbm.exe"))
    DEFAULT_PATHS["fonts"] = str(Path("./data/fonts"))
else:
    # script env
    DEFAULT_PATHS["dist"] = str(Path(".."))
    DEFAULT_PATHS["cached_static"] = str(Path("../../../static"))
    DEFAULT_PATHS["original_assets"] = str(Path("./assets-original"))
    DEFAULT_PATHS["translation"] = str(Path("./translation"))
    DEFAULT_PATHS["temp"] = str(Path("./temp"))
    DEFAULT_PATHS["protoc"] = str(Path("./utils/protoc/bin/protoc.exe"))
    DEFAULT_PATHS["fontbm"] = str(Path("./utils/fontbm/fontbm.exe"))
    DEFAULT_PATHS["fonts"] = str(Path("./fonts"))


def action_download(args):
    if hasattr(args, "clear") and args.clear:
        log_normal("Remove downloaded files...", args.verbose)
        shutil.rmtree(args.original_assets_path, ignore_errors=True)
        log_debug("Remove complete", args.verbose)
    if hasattr(args, "copy") and args.copy:
        log_normal("Copy cached static files...", args.verbose)
        copy_cached_asset(args.original_assets_path, args.cached_static_path)
        log_debug("Copy complete", args.verbose)

    log_normal("Download assets...", args.verbose)

    if not hasattr(args, "skip_exist"):
        setattr(args, "skip_exist", False)
    if not hasattr(args, "force_update"):
        setattr(args, "force_update", False)
    if not hasattr(args, "max_tries"):
        setattr(args, "max_tries", 10)

    download_assets(
        not args.skip_exist,
        args.force_update,
        args.original_assets_path,
        args.max_tries,
    )

    log_debug("Download complete", args.verbose)


def action_template(args):
    log_normal("Generate templates...", args.verbose)

    log_normal("Generate config_pb2.py file from config.proto...", args.verbose)
    proto_temp = Path(args.temp_path) / "proto"
    proto_temp.mkdir(parents=True, exist_ok=True)

    config_cmd = [
        args.protoc_path,
        f'--proto_path={Path(args.original_assets_path) / "res" / "proto"}',
        f"--python_out={proto_temp}",
        "config.proto",
    ]
    log_debug(" ".join(config_cmd), args.verbose)
    if not run_cmd(config_cmd):
        sys.exit(-1)

    generate_sheet_proto(args.original_assets_path, args.temp_path)

    log_normal("Generate sheets_pb2.py file from sheets.proto...", args.verbose)
    sheets_cmd = [
        args.protoc_path,
        f"--proto_path={proto_temp}",
        f"--python_out={proto_temp}",
        "sheets.proto",
    ]
    log_debug(" ".join(sheets_cmd), args.verbose)
    if not run_cmd(sheets_cmd):
        sys.exit(-1)

    export_sheets(args.original_assets_path, args.temp_path)
    generate_translation_po(
        args.translation_path, args.original_assets_path, args.temp_path
    )

    log_debug("Generate complete", args.verbose)


def action_atlas(args):
    if args.atlas_action == "pack":
        pack_atlas(args.atlas_size, args.path, args.target_path)
    elif args.atlas_action == "pack-all":
        pack_all_atlas(args.atlas_size, args.translation_path, args.target_path)
    elif args.atlas_action == "unpack":
        unpack_atlas(args.path)
    elif args.atlas_action == "unpack-all":
        unpack_all_atlas(args.original_assets_path)


def action_build(args):
    log_normal("Build...", args.verbose)

    export_sheets(args.original_assets_path, args.temp_path)
    if not hasattr(args, "skip_po") or not args.skip_po:
        apply_translation_po(args.translation_path)
    apply_translation_sheet(args.translation_path, args.temp_path)
    apply_translation_json(
        args.original_assets_path, args.translation_path, args.dist_path
    )
    build_sheets(
        args.original_assets_path, args.translation_path, args.dist_path, args.temp_path
    )
    merge_all_atlas(args.original_assets_path, args.translation_path, args.temp_path)
    pack_all_atlas(
        args.atlas_size, args.temp_path, str(Path(args.dist_path) / "assets")
    )
    extract_chars(args.dist_path, args.temp_path)
    generate_fonts(args.dist_path, args.fonts_path, args.temp_path, args.fontbm_path)
    generate_scene(args.original_assets_path, args.dist_path)
    copy_translated_asset(args.translation_path, args.dist_path)
    generate_resourcepack(args.dist_path)

    log_debug("Build complete", args.verbose)


if __name__ == "__main__":
    orig_env = dict(os.environ)
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--lang", help="language to translate", type=str, choices=("en", "jp")
        )
        parser.add_argument(
            "--verbose", help="verbose result", action="store_true", default=False
        )
        parser.add_argument(
            "--dist-path",
            help=f'path to save built data (default={DEFAULT_PATHS["dist"]})',
            type=str,
            default=DEFAULT_PATHS["dist"],
        )
        parser.add_argument(
            "--cached-static-path",
            help=f'path of cached static files (default={DEFAULT_PATHS["cached_static"]})',
            type=str,
            default=DEFAULT_PATHS["cached_static"],
        )
        parser.add_argument(
            "--original-assets-path",
            help=f'path to save downloaded original assets (default={DEFAULT_PATHS["original_assets"]})',
            type=str,
            default=DEFAULT_PATHS["original_assets"],
        )
        parser.add_argument(
            "--translation-path",
            help=f'path of translation data (default={DEFAULT_PATHS["translation"]})',
            type=str,
            default=DEFAULT_PATHS["translation"],
        )
        parser.add_argument(
            "--protoc-path",
            help=f'path of protoc (default={DEFAULT_PATHS["protoc"]})',
            type=str,
            default=DEFAULT_PATHS["protoc"],
        )
        parser.add_argument(
            "--fontbm-path",
            help=f'path of fontbm (default={DEFAULT_PATHS["fontbm"]})',
            type=str,
            default=DEFAULT_PATHS["fontbm"],
        )
        parser.add_argument(
            "--temp-path",
            help=f'path to use temporary (default={DEFAULT_PATHS["temp"]})',
            type=str,
            default=DEFAULT_PATHS["temp"],
        )
        parser.add_argument(
            "--fonts-path",
            help=f'path of fonts (default={DEFAULT_PATHS["fonts"]})',
            type=str,
            default=DEFAULT_PATHS["fonts"],
        )
        parser.add_argument(
            "--atlas-size",
            help="size factor of atlas image (default=8)",
            type=int,
            default=8,
        )

        action_subparsers = parser.add_subparsers(
            title="action", description="action to do", dest="action", required=True
        )
        parser_download = action_subparsers.add_parser(
            "download", help="download assets from server"
        )
        parser_download.add_argument(
            "--clear",
            help="remove all files before download",
            action="store_true",
            default=False,
        )
        parser_download.add_argument(
            "--copy",
            help="copy cached static files before download",
            action="store_true",
            default=False,
        )
        parser_download.add_argument(
            "--skip-exist",
            help="skip file to download that already exist",
            action="store_true",
            default=False,
        )
        parser_download.add_argument(
            "--force-update",
            help="do not skip file to download that older than downloaded version",
            action="store_true",
            default=False,
        )
        parser_download.add_argument(
            "--max-tries",
            help="max number of tries to download files (default=10)",
            type=int,
            default=10,
        )

        parser_template = action_subparsers.add_parser(
            "template", help="generate template files to translate"
        )

        parser_atlas = action_subparsers.add_parser(
            "atlas", help="pack/unpack atlas file"
        )
        atlas_subparsers = parser_atlas.add_subparsers(
            title="action",
            description="action to do",
            dest="atlas_action",
            required=True,
        )

        parser_atlas_pack = atlas_subparsers.add_parser(
            "pack", help="pack .atlas_unpack directory to .atlas file"
        )
        parser_atlas_pack.add_argument(
            "path", help="path of .atlas_unpack directory", type=str
        )
        parser_atlas_pack.add_argument(
            "--target-path",
            help="path to save .atlas file and images",
            type=str,
            default="",
        )

        parser_atlas_pack_all = atlas_subparsers.add_parser(
            "pack-all", help="pack all .atlas_unpack directories in default path"
        )
        parser_atlas_pack_all.add_argument(
            "--target-path",
            help=f'path to save .atlas file and images (default={Path(DEFAULT_PATHS["dist"]) / "assets"})',
            type=str,
            default=(Path(DEFAULT_PATHS["dist"]) / "assets"),
        )

        parser_atlas_unpack = atlas_subparsers.add_parser(
            "unpack", help="unpack .atlas file to .atlas_unpack directory"
        )
        parser_atlas_unpack.add_argument("path", help="path of .atlas file", type=str)

        parser_atlas_unpack_all = atlas_subparsers.add_parser(
            "unpack-all", help="unpack all .atlas files in default path"
        )

        parser_build = action_subparsers.add_parser("build", help="build asset data")
        parser_build.add_argument(
            "--skip-po",
            help="skip build po file to csv",
            action="store_true",
            default=False,
        )

        parser_all = action_subparsers.add_parser(
            "all",
            help="update original assets, apply translation and build all things automatically",
        )
        parser_all.add_argument(
            "--skip-download", help="skip download", action="store_true"
        )

        parser_args = parser.parse_args()

        if parser_args.lang:
            os.environ["MAJSOUL_LANG"] = parser_args.lang

        if parser_args.verbose:
            os.environ["MAJSOUL_VERBOSE"] = "1"

        if parser_args.action == "download":
            action_download(parser_args)

        elif parser_args.action == "template":
            action_template(parser_args)

        elif parser_args.action == "atlas":
            action_atlas(parser_args)

        elif parser_args.action == "build":
            action_build(parser_args)

        elif parser_args.action == "all":
            if not parser_args.skip_download:
                action_download(parser_args)

            unpack_all_atlas(parser_args.original_assets_path)
            action_template(parser_args)
            action_build(parser_args)

    finally:
        os.environ.clear()
        os.environ.update(orig_env)
