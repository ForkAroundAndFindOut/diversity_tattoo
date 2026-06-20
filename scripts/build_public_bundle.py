from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
MANIFEST_PATH = ROOT / "PUBLIC_BUNDLE_MANIFEST.json"

TOP_LEVEL_FILES = [
    "index.html",
    "styles.css",
    "content-render.js",
    "motion.js",
    "site-data.js",
    "404.html",
    "robots.txt",
    "sitemap.xml",
    "_headers",
    "_redirects",
]

CANONICAL_DIRS = [
    "assets",
    "artists",
    "blog",
    "products",
    "services",
    "shop",
    "tattoo",
    "piercing",
    "tooth-gems",
    "smoke-shop",
    "reviews",
    "faq",
    "utility",
]

ALIAS_DIRS = [
    "artist",
    "blog",
    "bodypiercing",
    "charlie",
    "contact",
    "gallery",
    "home",
    "locations",
    "post",
    "price-list-1",
    "product-page",
    "profile",
    "tank",
    "toothgems",
]


def filesystem_path(path: Path) -> str:
    resolved = str(path.resolve())
    if os.name != "nt" or resolved.startswith("\\\\?\\"):
        return resolved
    if resolved.startswith("\\\\"):
        return "\\\\?\\UNC\\" + resolved[2:]
    return "\\\\?\\" + resolved


def assert_public_target() -> None:
    resolved = PUBLIC_DIR.resolve()
    root = ROOT.resolve()
    if resolved == root or root not in resolved.parents or PUBLIC_DIR.name != "public":
        raise RuntimeError(f"Refusing to clean unsafe public path: {PUBLIC_DIR}")


def clean_public_dir() -> None:
    assert_public_target()
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    for child in PUBLIC_DIR.iterdir():
        if child.is_dir():
            shutil.rmtree(filesystem_path(child))
        else:
            child.unlink()


def copy_file(relative_path: str, copied: list[str]) -> None:
    source = ROOT / relative_path
    if not source.exists():
        raise FileNotFoundError(f"Required public file is missing: {source}")
    destination = PUBLIC_DIR / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(filesystem_path(source), filesystem_path(destination))
    copied.append(relative_path)


def copy_dir(relative_path: str, copied: list[str]) -> None:
    source = ROOT / relative_path
    if not source.exists():
        return
    destination = PUBLIC_DIR / relative_path
    shutil.copytree(filesystem_path(source), filesystem_path(destination), dirs_exist_ok=True)
    copied.append(relative_path + "/")


def main() -> None:
    clean_public_dir()

    copied: list[str] = []
    for file_name in TOP_LEVEL_FILES:
        copy_file(file_name, copied)
    for dir_name in CANONICAL_DIRS + ALIAS_DIRS:
        copy_dir(dir_name, copied)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "output_dir": str(PUBLIC_DIR),
        "copied_entries": copied,
        "note": "Deployment-shaped bundle only. Production readiness is determined by scripts/validate_production.py.",
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"built public bundle: {PUBLIC_DIR}")
    print(f"copied entries: {len(copied)}")
    print(f"manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
