from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"

EXPECTED_STATS = {
    "products": 124,
    "blogPosts": 15,
}

EXPECTED_PRODUCT_CATEGORIES = {
    "Shop - Body Jewelry": 25,
    "Shop - Detox / Cleanses": 22,
    "Shop - Other Products": 31,
    "Shop - Smoke Accessories": 31,
    "Shop - Vaporizers": 15,
}

REQUIRED_PUBLIC_FILES = [
    "index.html",
    "404.html",
    "robots.txt",
    "sitemap.xml",
    "_headers",
    "_redirects",
    "styles.css",
    "content-render.js",
    "motion.js",
    "site-data.js",
]

CORE_ROUTES = [
    "/",
    "/tattoo/",
    "/artists/",
    "/piercing/",
    "/tooth-gems/",
    "/smoke-shop/",
    "/shop/",
    "/blog/",
    "/reviews/",
    "/faq/",
]

FORBIDDEN_TEXT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bfile://",
        r"\bmhtml:",
        r"\bcid:",
        r"\b[A-Z]:\\",
    ]
]

FORBIDDEN_REMOTE_ASSET_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"https?:\/\/(?:static|static\.parastorage)\.wixstatic\.com",
        r"https?:\/\/[^\"'\s>]*\.wixstatic\.com\/",
        r"https?:\/\/[^\"'\s>]*parastorage\.com\/",
    ]
]

REFERENCE_ATTRS = {"href", "src", "poster", "data-src"}
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "sms", "data", "javascript"}


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if value and name.lower() in REFERENCE_ATTRS:
                self.references.append((name.lower(), value))
            if value and name.lower() == "srcset":
                for candidate in value.split(","):
                    url = candidate.strip().split(" ", 1)[0]
                    if url:
                        self.references.append(("srcset", url))


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def public_path_for_route(route: str) -> Path:
    clean = route.split("?", 1)[0].split("#", 1)[0]
    if clean in {"", "/"}:
        return PUBLIC_DIR / "index.html"
    clean = clean.lstrip("/")
    if clean.endswith("/"):
        return PUBLIC_DIR / clean / "index.html"
    path = PUBLIC_DIR / clean
    if path.suffix:
        return path
    return path / "index.html"


def resolve_reference(source_file: Path, reference: str) -> Path | None:
    reference = reference.strip()
    if not reference or reference.startswith("#"):
        return None
    parsed = urlparse(reference)
    if parsed.scheme.lower() in SKIP_SCHEMES or reference.startswith("//"):
        return None

    clean = unquote(parsed.path)
    if not clean:
        return None
    if clean.startswith("/"):
        return public_path_for_route(clean)
    return (source_file.parent / clean).resolve()


def load_site_data(errors: list[str]) -> dict:
    site_data_path = PUBLIC_DIR / "site-data.js"
    if not site_data_path.exists():
        fail(errors, "Missing public/site-data.js")
        return {}

    text = site_data_path.read_text(encoding="utf-8")
    match = re.match(r"\s*window\.DIVERSITY_SITE_DATA\s*=\s*(\{.*\})\s*;?\s*$", text, re.DOTALL)
    if not match:
        fail(errors, "public/site-data.js does not match expected assignment shape")
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        fail(errors, f"public/site-data.js is not parseable JSON: {exc}")
        return {}


def validate_required_files(errors: list[str]) -> None:
    for relative in REQUIRED_PUBLIC_FILES:
        path = PUBLIC_DIR / relative
        if not path.is_file():
            fail(errors, f"Missing required deploy file: public/{relative}")


def validate_core_routes(errors: list[str]) -> None:
    for route in CORE_ROUTES:
        path = public_path_for_route(route)
        if not path.is_file():
            fail(errors, f"Missing core route {route} -> {path.relative_to(ROOT)}")


def validate_site_data(site_data: dict, errors: list[str]) -> None:
    stats = site_data.get("stats", {})
    for key, expected in EXPECTED_STATS.items():
        actual = stats.get(key)
        if actual != expected:
            fail(errors, f"Expected stats.{key}={expected}, found {actual}")

    categories = stats.get("productCategories", {})
    for key, expected in EXPECTED_PRODUCT_CATEGORIES.items():
        actual = categories.get(key)
        if actual != expected:
            fail(errors, f"Expected product category {key!r} count {expected}, found {actual}")

    products = site_data.get("products", [])
    if len(products) != EXPECTED_STATS["products"]:
        fail(errors, f"Expected {EXPECTED_STATS['products']} products, found {len(products)}")
    for product in products:
        for key in ["destinationPath", "image"]:
            value = product.get(key)
            if not value:
                fail(errors, f"Product {product.get('title', '<untitled>')!r} missing {key}")
                continue
            path = public_path_for_route(value) if key == "destinationPath" else PUBLIC_DIR / value
            if not path.is_file():
                fail(errors, f"Product {product.get('title', '<untitled>')!r} references missing {key}: {value}")

    blog_posts = site_data.get("blogPosts")
    if isinstance(blog_posts, list) and len(blog_posts) != EXPECTED_STATS["blogPosts"]:
        fail(errors, f"Expected {EXPECTED_STATS['blogPosts']} blog posts, found {len(blog_posts)}")


def validate_forbidden_text(errors: list[str]) -> None:
    for path in PUBLIC_DIR.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".html", ".css", ".js", ".xml", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        relative = path.relative_to(ROOT)
        for pattern in FORBIDDEN_TEXT_PATTERNS:
            if pattern.search(text):
                fail(errors, f"Forbidden local/offline reference in {relative}: {pattern.pattern}")
        for pattern in FORBIDDEN_REMOTE_ASSET_PATTERNS:
            if pattern.search(text):
                fail(errors, f"Forbidden remote Wix/Parastorage asset URL in {relative}: {pattern.pattern}")


def validate_html_references(errors: list[str]) -> None:
    for path in PUBLIC_DIR.rglob("*.html"):
        if path.is_relative_to(PUBLIC_DIR / "assets"):
            continue
        parser = ReferenceParser()
        parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
        for attr, reference in parser.references:
            target = resolve_reference(path, reference)
            if target is None:
                continue
            try:
                target.relative_to(PUBLIC_DIR)
            except ValueError:
                fail(errors, f"{path.relative_to(ROOT)} {attr} escapes public/: {reference}")
                continue
            if not target.exists():
                fail(errors, f"{path.relative_to(ROOT)} {attr} references missing file: {reference}")


def validate_css_urls(errors: list[str]) -> None:
    url_pattern = re.compile(r"url\(\s*['\"]?([^'\"\)]+)['\"]?\s*\)")
    for path in PUBLIC_DIR.rglob("*.css"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for reference in url_pattern.findall(text):
            target = resolve_reference(path, reference)
            if target is None:
                continue
            try:
                target.relative_to(PUBLIC_DIR)
            except ValueError:
                fail(errors, f"{path.relative_to(ROOT)} CSS url escapes public/: {reference}")
                continue
            if not target.exists():
                fail(errors, f"{path.relative_to(ROOT)} CSS url references missing file: {reference}")


def validate_sitemap(errors: list[str]) -> None:
    sitemap = PUBLIC_DIR / "sitemap.xml"
    if not sitemap.is_file():
        return
    try:
        tree = ET.parse(sitemap)
    except ET.ParseError as exc:
        fail(errors, f"public/sitemap.xml is invalid XML: {exc}")
        return

    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [element.text or "" for element in tree.findall(".//sm:loc", namespace)]
    if not locs:
        fail(errors, "public/sitemap.xml contains no <loc> entries")
        return
    for loc in locs:
        parsed = urlparse(loc)
        path = public_path_for_route(parsed.path)
        if not path.is_file():
            fail(errors, f"Sitemap loc references missing route: {loc}")


def main() -> int:
    errors: list[str] = []
    if not PUBLIC_DIR.is_dir():
        print("FAIL: Missing public/ directory", file=sys.stderr)
        return 1

    validate_required_files(errors)
    validate_core_routes(errors)
    site_data = load_site_data(errors)
    if site_data:
        validate_site_data(site_data, errors)
    validate_forbidden_text(errors)
    validate_html_references(errors)
    validate_css_urls(errors)
    validate_sitemap(errors)

    if errors:
        print("Cloudflare public bundle validation: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Cloudflare public bundle validation: PASS")
    print(f"Validated deploy bundle: {PUBLIC_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
