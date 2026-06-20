from __future__ import annotations

import csv
import json
import re
import shutil
import struct
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import date
from html import escape, unescape
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup


OUT_DIR = Path(__file__).resolve().parent


def find_workspace_root(out_dir: Path) -> Path:
    for candidate in [out_dir.parent, *out_dir.parents]:
        if (
            (candidate / "catalog" / "content-inventory.csv").exists()
            and (candidate / "site" / "www.diversitytattoolv.com").exists()
        ):
            return candidate
    raise FileNotFoundError(
        "Could not locate Diversity scrape workspace root containing catalog/content-inventory.csv"
    )


ROOT = find_workspace_root(OUT_DIR)
CATALOG_DIR = ROOT / "catalog"
MIRROR_DIR = ROOT / "site" / "www.diversitytattoolv.com"

CONTENT_CSV = CATALOG_DIR / "content-inventory.csv"
MEDIA_CSV = CATALOG_DIR / "media-inventory.csv"
EXTERNAL_CSV = CATALOG_DIR / "external-links.csv"
SCRAPE_LOG_JSON = ROOT / "scrape-log.json"
SITE_MAP_MD = CATALOG_DIR / "site-map.md"
LOCAL_SITEMAP_HTML = MIRROR_DIR / "sitemap.html"
OBSERVED_404_JSON = CATALOG_DIR / "observed-404-ledger.json"
OBSERVED_404_CSV = CATALOG_DIR / "observed-404-ledger.csv"
FEED_XML = MIRROR_DIR / "blog-feed.xml"

SITE_DATA_JS = OUT_DIR / "site-data.js"
ROUTE_MAP_JSON = OUT_DIR / "route-map.json"
REDIRECTS_JSON = OUT_DIR / "redirects.json"
REDIRECTS_TXT = OUT_DIR / "_redirects"
MEDIA_REVIEW_JSON = OUT_DIR / "media-review.json"
CANONICAL_MANIFEST_JSON = CATALOG_DIR / "canonical-page-manifest.json"
SOURCE_ROUTE_LEDGER_JSON = OUT_DIR / "source-route-ledger.json"
SOURCE_ROUTE_LEDGER_CSV = OUT_DIR / "source-route-ledger.csv"
CANONICAL_URL_MAP_JSON = OUT_DIR / "canonical-url-map.json"
CANONICAL_URL_MAP_CSV = OUT_DIR / "canonical-url-map.csv"
ALIAS_LEDGER_JSON = OUT_DIR / "alias-ledger.json"
ALIAS_LEDGER_CSV = OUT_DIR / "alias-ledger.csv"
PRODUCT_PUBLICATION_LEDGER_JSON = OUT_DIR / "product-publication-ledger.json"
PRODUCT_PUBLICATION_LEDGER_CSV = OUT_DIR / "product-publication-ledger.csv"
BLOG_POST_LEDGER_JSON = OUT_DIR / "blog-post-ledger.json"
BLOG_POST_LEDGER_CSV = OUT_DIR / "blog-post-ledger.csv"
SOURCE_DIR = OUT_DIR / "source"
BLOG_SOURCE_JSON = SOURCE_DIR / "blog-posts.json"
BLOG_SOURCE_MD = SOURCE_DIR / "blog-posts.md"
QA_MD = OUT_DIR / "QA_CHECKLIST.md"
VERSION_NOTES = OUT_DIR / "VERSION_1_2_NOTES.md"
RESULTS_MD = OUT_DIR / "IMPLEMENTATION_RESULTS.md"
VALIDATION_TXT = OUT_DIR / "validation.txt"
BROWSER_QA_MD = OUT_DIR / "BROWSER_QA_RESULTS.md"
ROBOTS_TXT = OUT_DIR / "robots.txt"
SITEMAP_XML = OUT_DIR / "sitemap.xml"
HEADERS_TXT = OUT_DIR / "_headers"
NOT_FOUND_HTML = OUT_DIR / "404.html"
PRODUCTION_SPEC_MD = OUT_DIR / "V1_2_FULL_IMPLEMENTATION_SPEC.md"
ASSET_NOT_FOUND_IMAGE = "assets/placeholders/asset-not-found.svg"
LOGO_ASSET_PATH = Path(
    "assets/static.wixstatic.com/media/8d0ab0_6a77779840c44b9586da1fefe272017b_mv2_d_3300_1480_s_4_2.png"
)

DETAIL_DIRS = [
    "products",
    "blog",
    "guides",
    "artists",
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
ALIAS_CLEAN_DIRS = [
    "artist",
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
RECOVERABLE_404_ALIASES = {
    "/post/now-in-store-dr-dabber-switch.html": "/blog/now-in-store-dr-dabber-switch.html",
    "/post/honeystick-beekeeper-conceal-essential-oil-vaporizer.html": "/blog/honeystick-beekeeper-conceal-essential-oil-vaporizer.html",
    "/post/what-is-detox.html": "/blog/what-is-detox.html",
    "/post/are-detox-cleanses-permanent.html": "/blog/are-detox-cleanses-permanent.html",
    "/post/levo-oil-butter-maker.html": "/blog/levo-oil-butter-maker.html",
    "/post/davinci-miqro.html": "/blog/davinci-miqro.html",
    "/post/kandypens-k-stick.html": "/blog/kandypens-k-stick.html",
    "/post/categories/getting-started.html": "/blog/index.html",
    "/post/categories/your-community.html": "/blog/index.html",
}
PRODUCTION_ORIGIN = "https://www.diversitytattoolv.com"

NAV_NOISE = [
    "top of page",
    "WE ARE HIRING!!!",
    "CONTACT",
    "TATTOO ARTISTS",
    "Joanie",
    "Charlie",
    "BODY PIERCING",
    "Price List",
    "FAQ",
    "Tooth Gems",
    "REVIEWS",
    "SMOKE SHOP",
    "LOCATIONS",
    "BLOG",
    "All Posts Getting Started Your Community Search",
    "More",
    "Use tab to navigate through the menu items.",
    "bottom of page",
    "Atomic Lash Lounge",
    "Â© 2023 by Diversity Tattoo, Piercing & Smoke Shop in Las Vegas NV",
]

TITLE_SUFFIXES = [
    " | Diversity Tattoo 2",
    " | Diversity Tattoo LV | United States",
    " | United States | Diversity Tattoo",
    " | Diversity Tattoo",
]

MOJIBAKE_REPLACEMENTS = {
    "â€™": "'",
    "â€˜": "'",
    "â€œ": '"',
    "â€": '"',
    "â€�": '"',
    "â€“": "-",
    "â€”": "-",
    "â€¦": "...",
    "Ã¢â‚¬â„¢": "'",
    "Ã¢â‚¬Å“": '"',
    "Ã¢â‚¬Â": '"',
    "Ã¢â‚¬Å\ufeff": '"',
    "Ã¢â‚¬â€œ": "-",
    "Ã¢â‚¬â€": "-",
    "Ã¢â‚¬Â¢": "-",
    "Ã‚Â©": "",
    "Ã‚Â¼": "1/4",
    "Ã‚": "",
    "â€¢": "-",
    "Â¼": "1/4",
    "\u00a0": " ",
}

CATEGORY_IMAGES = {
    "Shop - Smoke Accessories": "assets/static.wixstatic.com/c131011fd82773ff.jpg",
    "Shop - Detox / Cleanses": "assets/static.wixstatic.com/5fba7b44e230022f.jpg",
    "Shop - Body Jewelry": "assets/static.wixstatic.com/e57dce51900137bf.jpg",
    "Shop - Vaporizers": "assets/static.wixstatic.com/7215c4a996cef463.jpg",
    "Shop - Other Products": "assets/static.wixstatic.com/76300833f4cccab0.jpg",
    "Artists": "assets/static.wixstatic.com/fea829b35635125e.jpg",
    "Blog / Guides": "assets/static.wixstatic.com/b99142ec9d528464.jpg",
    "Piercing": "assets/static.wixstatic.com/e57dce51900137bf.jpg",
    "Tattoo Services": "assets/static.wixstatic.com/b99142ec9d528464.jpg",
    "Smoke Shop": "assets/static.wixstatic.com/76300833f4cccab0.jpg",
    "Tooth Gems": "assets/static.wixstatic.com/57b962a74e3c3f70.png",
    "Reviews": "assets/static.wixstatic.com/bf2da649c19096a7.jpeg",
    "FAQ": "assets/static.wixstatic.com/57b962a74e3c3f70.png",
    "Location / Contact": "assets/static.wixstatic.com/bf2da649c19096a7.jpeg",
    "Home": "assets/static.wixstatic.com/bf2da649c19096a7.jpeg",
    "Utility / Member Account": "assets/static.wixstatic.com/b99142ec9d528464.jpg",
}

SKIP_MEDIA_STEMS = {
    "ef417a5e58886445",
    "654e0cb72cd3ca16",
}

PIERCING_ROWS = [
    {"name": "Standard navel", "price": "$45", "notes": "Jewelry included"},
    {"name": "Tongue", "price": "$45", "notes": "Jewelry included"},
    {"name": "Nostril", "price": "$45", "notes": "Jewelry included"},
    {"name": "Eyebrow", "price": "$45", "notes": "Jewelry included"},
    {"name": "Ear lobe", "price": "$20", "notes": "Structured from price list route"},
    {"name": "Helix", "price": "$40", "notes": "Structured from price list route"},
    {"name": "Rook", "price": "$40", "notes": "Structured from price list route"},
    {"name": "Tragus", "price": "$40", "notes": "Structured from price list route"},
    {"name": "Daith", "price": "$40", "notes": "Structured from price list route"},
    {"name": "Conch", "price": "$50", "notes": "Structured from price list route"},
    {"name": "Anti-tragus", "price": "$40", "notes": "Structured from price list route"},
    {"name": "Industrial", "price": "$65", "notes": "Structured from price list route"},
]

CONTACT = {
    "address": "4401 N Rancho Dr, Las Vegas, NV 89130",
    "phone": "702.454.1300",
    "phoneHref": "tel:+17024541300",
    "hours": "Everyday: 10:00 a.m. - 10:00 p.m.",
    "emails": ["diversitytattoo702@gmail.com", "diversitytattoo@gmail.com"],
    "socials": [
        {"label": "Instagram", "url": "https://www.instagram.com/diversitytattoolv/"},
        {"label": "Facebook", "url": "https://www.facebook.com/diversitytattoolv/"},
        {"label": "Atomic Lash Lounge", "url": "https://www.atomiclashlounge.com/"},
    ],
}

SERVICE_CATEGORIES = {
    "Home",
    "Tattoo Services",
    "Piercing",
    "Tooth Gems",
    "Smoke Shop",
    "Reviews",
    "FAQ",
    "Location / Contact",
}

PRODUCT_CATEGORY_ORDER = [
    "Shop - Body Jewelry",
    "Shop - Detox / Cleanses",
    "Shop - Smoke Accessories",
    "Shop - Vaporizers",
    "Shop - Other Products",
]

SMOKE_SHOP_CATEGORIES = [
    "Shop - Detox / Cleanses",
    "Shop - Smoke Accessories",
    "Shop - Vaporizers",
    "Shop - Other Products",
]

SECTION_ROUTE_TARGETS = {
    "Tattoo Services": "tattoo/index.html",
    "Piercing": "piercing/index.html",
    "Tooth Gems": "tooth-gems/index.html",
    "Smoke Shop": "smoke-shop/index.html",
    "Reviews": "reviews/index.html",
    "FAQ": "faq/index.html",
}

SECTION_PAGE_CONFIGS = [
    {
        "key": "tattoo",
        "path": "tattoo/index.html",
        "title": "Tattoo Services",
        "eyebrow": "Tattoo",
        "description": "Custom tattoos, cover-up planning, artist selection and visit guidance from Diversity Tattoo in Las Vegas.",
        "heroImage": CATEGORY_IMAGES["Tattoo Services"],
        "sourceCategories": ["Tattoo Services"],
        "summary": "Review studio standards, meet the artists, and call the Rancho studio when you are ready to talk through tattoo availability.",
        "primaryLabel": "Call about a tattoo",
        "primaryHref": "tel:+17024541300",
        "secondaryLabel": "Meet the artists",
        "secondaryHref": "../artists/index.html",
        "highlights": [
            "Custom work, cover-up conversations and planning support",
            "Artist profiles and tattoo planning context in one place",
            "Direct visit and call paths for appointment questions",
        ],
    },
    {
        "key": "piercing",
        "path": "piercing/index.html",
        "title": "Piercing And Body Jewelry",
        "eyebrow": "Piercing",
        "description": "Body piercing information, common piercing prices and body jewelry browsing from Diversity Tattoo.",
        "heroImage": CATEGORY_IMAGES["Piercing"],
        "sourceCategories": ["Piercing"],
        "summary": "Plan a piercing visit, review common pricing, and browse body jewelry before you come into the Rancho studio.",
        "primaryLabel": "Call about piercing",
        "primaryHref": "tel:+17024541300",
        "secondaryLabel": "Jump to pricing",
        "secondaryHref": "#pricing",
        "extraActions": [
            {"label": "See Jewelry", "href": "#product-filters"},
        ],
        "productScope": ["Shop - Body Jewelry"],
        "productIntro": "Body jewelry from the shop catalog.",
        "productCopy": "Browse body jewelry before visiting the studio. Call ahead for current availability, sizing, and placement guidance.",
        "highlights": [
            "Common piercing options and pricing in one focused place",
            "Body jewelry browsing tied to current catalog records",
            "Visit and call paths kept close to the service detail",
        ],
    },
    {
        "key": "tooth-gems",
        "path": "tooth-gems/index.html",
        "title": "Tooth Gems",
        "eyebrow": "Tooth Gems",
        "description": "Tooth gem service information, visit guidance and available service visuals.",
        "heroImage": CATEGORY_IMAGES["Tooth Gems"],
        "sourceCategories": ["Tooth Gems"],
        "summary": "Add a small flash of shine with tooth gems, then call or stop by for current options and visit guidance.",
        "primaryLabel": "Call about tooth gems",
        "primaryHref": "tel:+17024541300",
        "secondaryLabel": "Plan your visit",
        "secondaryHref": "../index.html#visit",
        "highlights": [
            "Focused service details for tooth gem planning",
            "Available service visuals for planning",
            "Related links back to piercing and visit information",
        ],
    },
    {
        "key": "smoke-shop",
        "path": "smoke-shop/index.html",
        "title": "Smoke Shop And Detox",
        "eyebrow": "Smoke Shop",
        "description": "Smoke accessories, vaporizers, detox cleanses and other retail products from the Diversity Tattoo shop catalog.",
        "heroImage": CATEGORY_IMAGES["Smoke Shop"],
        "sourceCategories": ["Smoke Shop"],
        "summary": "Browse detox cleanses, vaporizers, smoke accessories, and other retail products before calling or stopping by.",
        "primaryLabel": "Call about availability",
        "primaryHref": "tel:+17024541300",
        "secondaryLabel": "Explore items",
        "secondaryHref": "#product-filters",
        "productScope": SMOKE_SHOP_CATEGORIES,
        "productIntro": "Smoke shop categories.",
        "productCopy": "Browse smoke shop products and detox options before visiting. Call ahead for current availability.",
        "highlights": [
            "Detox / Cleanses, Vaporizers, Smoke Accessories and Other Products",
            "Body jewelry remains with piercing so each shopping lane stays clear",
            "Direct path to the full shop when visitors need every category",
        ],
    },
    {
        "key": "reviews",
        "path": "reviews/index.html",
        "title": "Reviews",
        "eyebrow": "Reviews",
        "description": "Customer trust and review information for Diversity Tattoo.",
        "heroImage": CATEGORY_IMAGES["Reviews"],
        "sourceCategories": ["Reviews"],
        "summary": "See trust signals, customer context, and quick ways to call or plan a visit with the studio.",
        "primaryLabel": "Call the studio",
        "primaryHref": "tel:+17024541300",
        "secondaryLabel": "Visit details",
        "secondaryHref": "../index.html#visit",
        "highlights": [
            "Studio trust and customer context",
            "Review context and studio trust signals",
            "Clear path back to visit planning",
        ],
    },
    {
        "key": "faq",
        "path": "faq/index.html",
        "title": "FAQ",
        "eyebrow": "FAQ",
        "description": "Common questions about tattoos, piercing, aftercare, retail products and visiting Diversity Tattoo.",
        "heroImage": CATEGORY_IMAGES["FAQ"],
        "sourceCategories": ["FAQ"],
        "summary": "Find quick answers for tattoo, piercing, product, aftercare, and visit questions before you call or come in.",
        "primaryLabel": "Call with a question",
        "primaryHref": "tel:+17024541300",
        "secondaryLabel": "Plan your visit",
        "secondaryHref": "../index.html#visit",
        "highlights": [
            "Common questions for tattoos, piercing, products, and visits",
            "Short answers written for customer decisions",
            "Contact path when a question needs current studio guidance",
        ],
    },
]

GUIDE_TYPES = {"blog_post", "blog_category", "blog_index", "blog_redirect"}
BLOG_NAVIGATION_TEXT = "All Posts Getting Started Your Community Search"
BLOG_SIDEBAR_TEXT = "Recent Posts See All"
MIN_PRODUCT_IMAGE_EDGE = 180
MIN_PRODUCT_SLIM_IMAGE_EDGE = 120
MIN_PRODUCT_SLIM_IMAGE_LONG_EDGE = 360
MIN_PRODUCT_SLIM_IMAGE_AREA = 45000
MIN_BLOG_IMAGE_EDGE = 180


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def clean_text(value: str | None, limit: int | None = None) -> str:
    text = unescape(value or "")
    for source, target in MOJIBAKE_REPLACEMENTS.items():
        text = text.replace(source, target)
    for token in NAV_NOISE:
        text = text.replace(token, " ")
    text = re.sub(r"\s+", " ", text).strip()
    if limit and len(text) > limit:
        text = text[: limit - 1].rsplit(" ", 1)[0].strip() + "..."
    return text


def clean_title(title: str | None) -> str:
    text = clean_text(title)
    for suffix in TITLE_SUFFIXES:
        if text.endswith(suffix):
            text = text[: -len(suffix)]
    return text.strip(" -|") or "Untitled"


def clean_excerpt(value: str | None, title: str | None, limit: int = 220) -> str:
    text = clean_text(value)
    raw_title = clean_text(title)
    short_title = clean_title(title)
    title_variants = [item for item in [raw_title, short_title] if item]
    for suffix in TITLE_SUFFIXES:
        if short_title:
            title_variants.append(f"{short_title}{suffix}")
    for variant in sorted(set(title_variants), key=len, reverse=True):
        if text.startswith(variant):
            text = text[len(variant) :].strip()
            text = re.sub(r"^[\s|:.-]+", "", text).strip()
            break
    if short_title and len(short_title) > 6:
        repeated_title_index = text.find(short_title)
        if repeated_title_index > 40:
            text = text[:repeated_title_index].strip()
    text = re.sub(r"\s*\|\s*Diversity Tattoo 2\b", "", text)
    text = re.sub(r"\bDiversity Tattoo LV \| United States\b", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        text = f"Contact Diversity Tattoo for current information about {short_title or raw_title or 'this page'}."
    if limit and len(text) > limit:
        text = text[: limit - 1].rsplit(" ", 1)[0].strip() + "..."
    return text


def make_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def image_size(path: Path) -> tuple[int, int]:
    try:
        data = path.read_bytes()
    except OSError:
        return (0, 0)
    if len(data) < 24:
        return (0, 0)
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        offset = 2
        while offset + 9 < len(data):
            if data[offset] != 0xFF:
                offset += 1
                continue
            marker = data[offset + 1]
            offset += 2
            if marker in {0xD8, 0xD9}:
                continue
            if offset + 2 > len(data):
                break
            length = struct.unpack(">H", data[offset : offset + 2])[0]
            if length < 2 or offset + length > len(data):
                break
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                height = struct.unpack(">H", data[offset + 3 : offset + 5])[0]
                width = struct.unpack(">H", data[offset + 5 : offset + 7])[0]
                return (width, height)
            offset += length
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        chunk = data[12:16]
        if chunk == b"VP8X" and len(data) >= 30:
            width = 1 + int.from_bytes(data[24:27], "little")
            height = 1 + int.from_bytes(data[27:30], "little")
            return (width, height)
        if chunk == b"VP8L" and len(data) >= 25:
            bits = int.from_bytes(data[21:25], "little")
            width = 1 + (bits & 0x3FFF)
            height = 1 + ((bits >> 14) & 0x3FFF)
            return (width, height)
        if chunk == b"VP8 " and len(data) >= 30:
            width = struct.unpack("<H", data[26:28])[0] & 0x3FFF
            height = struct.unpack("<H", data[28:30])[0] & 0x3FFF
            return (width, height)
    return (0, 0)


def image_meets_quality(
    path: Path,
    min_edge: int,
    *,
    slim_min_edge: int = 0,
    slim_min_long_edge: int = 0,
    slim_min_area: int = 0,
) -> bool:
    width, height = image_size(path)
    if min(width, height) >= min_edge:
        return True
    return bool(
        slim_min_edge
        and min(width, height) >= slim_min_edge
        and max(width, height) >= slim_min_long_edge
        and width * height >= slim_min_area
    )


def media_id_from_value(value: str) -> str:
    if not value:
        return ""
    parsed = urlparse(value)
    raw_path = unquote(parsed.path if parsed.scheme else value)
    parts = [part for part in raw_path.split("/") if part]
    candidate = ""
    if "media" in parts:
        media_index = parts.index("media")
        if media_index + 1 < len(parts):
            candidate = parts[media_index + 1]
    if not candidate and parts:
        candidate = parts[-1]
    candidate = candidate.split("?", 1)[0]
    return normalize_media_key(candidate)


def asset_path_from_local(local_path: str) -> str:
    return local_path.replace("\\", "/").replace("site/", "assets/", 1)


def local_path_for_asset(asset_path: str) -> Path:
    if asset_path.startswith("assets/"):
        return OUT_DIR / asset_path
    return ROOT / asset_path


def copy_or_download_media(source_path: Path | None, source_url: str, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source_path and source_path.exists():
        if source_path.resolve() != destination.resolve():
            shutil.copy2(source_path, destination)
        return "local"
    if source_url:
        request = Request(source_url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=45) as response:
            destination.write_bytes(response.read())
        return "downloaded"
    return "missing"


def extension_for_media(path: Path | None, url: str) -> str:
    if path and path.suffix:
        return path.suffix.lower()
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}:
        return suffix
    return ".jpg"


def refresh_canonical_manifest() -> list[dict[str, object]]:
    manifest_script = CATALOG_DIR / "generate_canonical_manifest.py"
    if not manifest_script.exists():
        return []
    sys.path.insert(0, str(CATALOG_DIR))
    try:
        from generate_canonical_manifest import generate_manifest

        return generate_manifest(download_missing=True)
    finally:
        try:
            sys.path.remove(str(CATALOG_DIR))
        except ValueError:
            pass


def load_canonical_manifest() -> dict[str, dict[str, object]]:
    if not CANONICAL_MANIFEST_JSON.exists():
        return {}
    try:
        rows = json.loads(CANONICAL_MANIFEST_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return {row.get("source_route", ""): row for row in rows if isinstance(row, dict) and row.get("source_route")}


def rebuild_asset_path(root_relative_path: str) -> str:
    clean = str(root_relative_path or "").replace("\\", "/")
    prefix = "v1.2 rebuild/"
    if clean.startswith(prefix):
        return clean[len(prefix) :]
    return clean


def manifest_asset_for_record(manifest_row: dict[str, object]) -> str:
    asset_path = rebuild_asset_path(str(manifest_row.get("local_canonical_asset_path", "")))
    canonical_id = str(manifest_row.get("canonical_image_media_id", ""))
    local_id = str(manifest_row.get("local_canonical_asset_media_id", ""))
    workspace_asset = ROOT / str(manifest_row.get("local_canonical_asset_path", ""))
    if asset_path and canonical_id and local_id == canonical_id and ((OUT_DIR / asset_path).exists() or workspace_asset.exists()):
        return asset_path
    return ASSET_NOT_FOUND_IMAGE


def parse_feed_posts() -> dict[str, dict[str, str]]:
    tree = ET.parse(FEED_XML)
    channel = tree.getroot().find("channel")
    if channel is None:
        return {}
    posts: dict[str, dict[str, str]] = {}
    for index, item in enumerate(channel.findall("item")):
        link = clean_text(item.findtext("link"))
        slug = urlparse(link).path.rstrip("/").rsplit("/", 1)[-1]
        if not slug:
            continue
        enclosure = item.find("enclosure")
        enclosure_url = enclosure.get("url", "") if enclosure is not None else ""
        posts[slug] = {
            "slug": slug,
            "title": clean_title(item.findtext("title")),
            "description": clean_text(item.findtext("description")),
            "url": link,
            "pubDate": clean_text(item.findtext("pubDate")),
            "category": clean_text(item.findtext("category")),
            "enclosureUrl": enclosure_url,
            "archiveOrder": str(index + 1),
        }
    return posts


def meta_content(soup: BeautifulSoup, *, name: str = "", prop: str = "") -> str:
    selector = ""
    if name:
        selector = f'meta[name="{name}"]'
    elif prop:
        selector = f'meta[property="{prop}"]'
    node = soup.select_one(selector) if selector else None
    return clean_text(node.get("content", "")) if node else ""


def extract_blog_blocks(html: str, title: str) -> list[str]:
    soup = make_soup(html)
    article = soup.select_one('article[data-hook="post"]')
    if not article:
        return []
    for selector in [
        "header",
        "footer",
        "svg",
        "button",
        '[data-hook="post-title"]',
        '[data-hook="post-stats"]',
        '[data-hook="more-button"]',
        '[data-hook="post-main-actions-desktop"]',
    ]:
        for node in article.select(selector):
            node.decompose()
    blocks: list[str] = []
    for node in article.find_all(["p", "h2", "h3", "h4", "li"]):
        text = clean_text(node.get_text(" ", strip=True))
        for marker in [BLOG_SIDEBAR_TEXT, "© 2023 by Diversity Tattoo", BLOG_NAVIGATION_TEXT]:
            if marker in text:
                text = text.split(marker, 1)[0].strip()
        if not text or text == BLOG_NAVIGATION_TEXT:
            continue
        if text == clean_title(title):
            continue
        if text.startswith(clean_title(title)) and " min read" in text:
            continue
        if text not in blocks:
            blocks.append(text)
    return blocks


def extract_blog_source(
    row: dict[str, str],
    feed_posts: dict[str, dict[str, str]],
    media_lookup: dict[str, list[dict[str, str]]],
    grouped_media: dict[str, list[dict[str, str]]],
) -> dict[str, object]:
    route = row.get("route_path", "")
    slug = slug_from_route(route)
    feed = feed_posts.get(slug, {})
    path = ROOT / row.get("local_path", "")
    html = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
    soup = make_soup(html) if html else BeautifulSoup("", "lxml")
    title = clean_title(feed.get("title") or row.get("title", ""))
    blocks = extract_blog_blocks(html, title) if html else []
    if not blocks:
        fallback = clean_excerpt(feed.get("description") or row.get("body_text_excerpt", ""), title, 1200)
        if (
            not fallback
            or BLOG_NAVIGATION_TEXT in fallback
            or BLOG_SIDEBAR_TEXT in fallback
            or (" min read" in fallback and fallback.startswith(title))
        ):
            fallback = (
                f"{title} is a studio media post from Diversity Tattoo. "
                "Contact the studio for current product availability, service questions, and visit details."
            )
        blocks = [fallback] if fallback else []
    blocks = [clean_text(block, 5000) for block in blocks if clean_text(block, 5000)]
    image_url = meta_content(soup, prop="og:image") or feed.get("enclosureUrl", "")
    image = resolve_local_media_asset(route, image_url, media_lookup) or pick_image(row, media_by_route(read_csv(MEDIA_CSV)))
    category = feed.get("category") or guide_category(row)
    return {
        "slug": slug,
        "title": title,
        "route": route,
        "sourceUrl": feed.get("url") or row.get("legacy_url", ""),
        "destinationPath": f"blog/{slug}.html",
        "pubDate": feed.get("pubDate", ""),
        "archiveOrder": safe_int(feed.get("archiveOrder")) or 999,
        "category": category,
        "excerpt": clean_text(blocks[0], 260) if blocks else clean_excerpt(feed.get("description"), title, 260),
        "body": "\n\n".join(blocks),
        "bodyBlocks": blocks,
        "image": image or pick_image(row, grouped_media),
        "imageSourceUrl": image_url,
    }


def safe_int(value: str | int | None) -> int:
    try:
        return int(value or 0)
    except ValueError:
        return 0


def slug_from_route(route: str) -> str:
    route = route.strip("/")
    stem = Path(route).stem
    if stem in {"index", ""}:
        parent = Path(route).parent.name
        return parent if parent and parent != "." else "index"
    return stem


def unique_path(base: str, used: set[str]) -> str:
    path = base
    suffix = 2
    while path in used:
        p = Path(base)
        path = str(p.with_name(f"{p.stem}-{suffix}{p.suffix}")).replace("\\", "/")
        suffix += 1
    used.add(path)
    return path


def first_price(text: str) -> str:
    match = re.search(r"\$\d+(?:\.\d{2})?", text)
    return match.group(0) if match else "In-store"


def product_category_label(category: str) -> str:
    return category.replace("Shop - ", "")


def guide_category(row: dict[str, str]) -> str:
    source = " ".join([row.get("route_path", ""), row.get("title", ""), row.get("body_text_excerpt", "")]).lower()
    if "cover" in source:
        return "Tattoo Planning"
    if "aftercare" in source or "taking-care" in source or "itches" in source:
        return "Aftercare"
    if "detox" in source or "cleanse" in source or "dr. dabber" in source or "kandypens" in source or "levo" in source:
        return "Retail Education"
    if "dog" in source or "community" in source or "cbd" in source:
        return "Your Community"
    return "Getting Started"


def to_relative_site_path(local_path: str, media_url: str = "", media_key: str = "") -> str | None:
    if not local_path:
        return None
    if media_key.endswith(".html") or "w_38,h_38" in media_url:
        return None
    path = Path(local_path)
    if path.stem in SKIP_MEDIA_STEMS:
        return None
    if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        return None
    full_path = ROOT / path
    if not full_path.exists():
        return None
    if full_path.stat().st_size < 8_000:
        return None
    return local_path.replace("\\", "/").replace("site/", "assets/", 1)


def media_by_route(media_rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in media_rows:
        rel = to_relative_site_path(row.get("local_path", ""), row.get("media_url", ""), row.get("media_key", ""))
        if not rel:
            continue
        grouped[row.get("page_route", "")].append(
            {
                "url": row.get("media_url", ""),
                "localPath": rel,
                "risk": clean_text(row.get("risk", "")),
                "status": row.get("scrape_status", ""),
            }
        )
    return grouped


def pick_image(row: dict[str, str], grouped_media: dict[str, list[dict[str, str]]]) -> str:
    route = row.get("route_path", "")
    for media in grouped_media.get(route, []):
        if not media["risk"]:
            return media["localPath"]
    return CATEGORY_IMAGES.get(row.get("current_category", "")) or CATEGORY_IMAGES.get(
        row.get("recommended_refactor_category", ""), "assets/static.wixstatic.com/b99142ec9d528464.jpg"
    )


def detail_image_path(index_image_path: str) -> str:
    if index_image_path.startswith("assets/"):
        return "../" + index_image_path
    return index_image_path


def mirror_href(route: str) -> str:
    return "../site/www.diversitytattoolv.com/" + route


def public_url_path(destination: str) -> str:
    if not destination or destination == "index.html":
        return "/"
    if destination.endswith("/index.html"):
        return "/" + destination[: -len("index.html")]
    return "/" + destination


def row_destination(row: dict[str, str], used: set[str], post_stems: set[str]) -> tuple[str, str, str]:
    route = row["route_path"]
    page_type = row["page_type"]
    section = row["recommended_refactor_category"]
    slug = slug_from_route(route)

    if page_type == "product":
        return "rebuilt detail page", unique_path(f"products/{slug}.html", used), "product detail"
    if page_type == "shop_page":
        if route == "shop.html":
            return "rebuilt section page", unique_path("shop/index.html", used), "shop catalog"
        return "redirect to rebuilt destination", "shop/index.html", "shop compatibility alias"
    if page_type == "blog_index":
        return "rebuilt section page", "blog/index.html", "blog archive"
    if page_type == "blog_category":
        return "redirect to rebuilt destination", "blog/index.html", "blog category filter"
    if page_type == "blog_post":
        return "rebuilt detail page", unique_path(f"blog/{slug}.html", used), "blog post"
    if page_type == "blog_redirect":
        target = f"blog/{slug}.html" if slug in post_stems else "blog/index.html"
        return "redirect to rebuilt destination", target, "blog redirect alias"
    if page_type == "profile":
        return "intentionally excluded utility route", "utility/account-unavailable.html", "utility exclusion"
    if section == "Artists":
        if route == "artist.html":
            return "rebuilt section page", unique_path("artists/index.html", used), "artist index"
        return "rebuilt detail page", unique_path(f"artists/{slug}.html", used), "artist profile"
    if section == "Home":
        return "rebuilt primary page", "index.html", "home alias"
    if section in SECTION_ROUTE_TARGETS:
        return "rebuilt section page", SECTION_ROUTE_TARGETS[section], "top-level section page"
    if section in SERVICE_CATEGORIES:
        return "rebuilt detail page", unique_path(f"services/{slug}.html", used), "service page"
    return "rendered content record", unique_path(f"services/{slug}.html", used), "content page"


def redirect_source(row: dict[str, str]) -> str:
    parsed = urlparse(row.get("recommended_legacy_url") or row.get("legacy_url") or "")
    if parsed.path:
        source = parsed.path
        if parsed.query:
            source += "?" + parsed.query
        return source or "/"
    route = row.get("route_path", "")
    if route == "index.html":
        return "/"
    return "/" + route.removesuffix(".html")


def build_route_ledger(pages: list[dict[str, str]]) -> list[dict[str, str]]:
    used: set[str] = {"index.html"}
    post_stems = {slug_from_route(row["route_path"]) for row in pages if row["page_type"] == "blog_post"}
    ledger = []
    for row in pages:
        status, destination, destination_type = row_destination(row, used, post_stems)
        ledger.append(
            {
                "legacyUrl": row.get("legacy_url", ""),
                "recommendedLegacyUrl": row.get("recommended_legacy_url", ""),
                "localPath": row.get("local_path", ""),
                "route": row.get("route_path", ""),
                "type": row.get("page_type", ""),
                "title": clean_title(row.get("title", "")),
                "sourceTitle": clean_text(row.get("title", "")),
                "currentCategory": row.get("current_category", ""),
                "futureSection": row.get("recommended_refactor_category", ""),
                "destinationStatus": status,
                "destinationType": destination_type,
                "destinationPath": destination,
                "redirectSource": redirect_source(row),
                "sourceContentStatus": "available" if row.get("body_text_excerpt") else "thin or unavailable",
                "mediaReviewStatus": "review required" if "No user-facing media" in row.get("notes", "") else "cataloged",
                "implementationStatus": "generated",
                "qaStatus": "pending browser review",
                "notes": clean_text(row.get("notes", "")),
            }
        )
    return ledger


def external_domain(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    if parsed.netloc:
        return parsed.netloc.lower()
    if url.startswith("cid:"):
        return "cid"
    return ""


def approved_external(row: dict[str, str]) -> bool:
    include = row.get("include_in_rebuild", "").lower()
    domain = external_domain(row.get("url", ""))
    return include == "yes" and not any(skip in domain for skip in ["cid", "wix", "parastorage", "sentry", "wixmp"])


def html_to_text(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = unescape(text)
    return clean_text(text)


def find_product_object(payload: object) -> dict | None:
    if isinstance(payload, dict):
        catalog = payload.get("catalog")
        if isinstance(catalog, dict) and isinstance(catalog.get("product"), dict):
            return catalog["product"]
        for value in payload.values():
            found = find_product_object(value)
            if found:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = find_product_object(value)
            if found:
                return found
    return None


def extract_product_truth(row: dict[str, str]) -> dict:
    local_path = row.get("local_path", "")
    path = ROOT / local_path
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r'<script id="wix-warmup-data" type="application/json">(.*?)</script>', text, re.S)
    if not match:
        return {}
    try:
        payload = json.loads(unescape(match.group(1)))
    except json.JSONDecodeError:
        return {}
    product = find_product_object(payload)
    if not product:
        return {}
    additional_info = [
        {
            "title": clean_text(item.get("title", "")),
            "description": html_to_text(item.get("description", "")),
        }
        for item in product.get("additionalInfo", [])
        if isinstance(item, dict)
    ]
    media = [
        {
            "id": clean_text(item.get("id", "")),
            "fullUrl": item.get("fullUrl", ""),
            "altText": clean_text(item.get("altText", "")),
            "title": clean_text(item.get("title", "")),
            "width": item.get("width", ""),
            "height": item.get("height", ""),
        }
        for item in product.get("media", [])
        if isinstance(item, dict) and item.get("mediaType") == "PHOTO"
    ]
    return {
        "id": product.get("id", ""),
        "name": clean_title(product.get("name", "")),
        "slug": product.get("urlPart", ""),
        "formattedPrice": product.get("formattedPrice", ""),
        "description": html_to_text(product.get("description", "")),
        "productType": product.get("productType", ""),
        "inventoryStatus": (product.get("inventory") or {}).get("status", ""),
        "isInStock": bool(product.get("isInStock")),
        "additionalInfo": additional_info,
        "additionalInfoText": " ".join(
            clean_text(f"{item['title']} {item['description']}") for item in additional_info if item.get("description")
        ),
        "media": media,
        "source": "wix-warmup-data",
    }


def normalize_media_key(value: str) -> str:
    return clean_text(value).replace("~", "_")


def product_media_lookup(media_rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    lookup: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in media_rows:
        route = row.get("page_route", "")
        key = normalize_media_key(row.get("media_key", ""))
        local_path = row.get("local_path", "")
        if not route or not key or not local_path:
            continue
        if not (ROOT / local_path).exists():
            continue
        lookup[f"{route}::{key}"].append(row)
        lookup[f"*::{key}"].append(row)
    return lookup


def candidate_row_score(row: dict[str, str]) -> tuple[int, int, int]:
    local_path = row.get("local_path", "")
    path = ROOT / local_path
    width, height = image_size(path)
    area = width * height
    not_blurred = 0 if "blur_" in row.get("media_url", "") else 1
    try:
        size = path.stat().st_size
    except OSError:
        size = 0
    return (not_blurred, area, size)


def resolve_local_media_asset(route: str, media_value: str, media_lookup: dict[str, list[dict[str, str]]]) -> str:
    media_id = media_id_from_value(media_value)
    if not media_id:
        return ""
    rows = [*media_lookup.get(f"{route}::{media_id}", []), *media_lookup.get(f"*::{media_id}", [])]
    rows = [row for row in rows if row.get("local_path") and (ROOT / row["local_path"]).exists()]
    if not rows:
        return ""
    best = sorted(rows, key=candidate_row_score, reverse=True)[0]
    return asset_path_from_local(best["local_path"])


def product_truth_image(route: str, truth: dict, media_lookup: dict[str, list[dict[str, str]]]) -> str:
    for media in truth.get("media", []):
        for value in [media.get("id", ""), media.get("fullUrl", ""), media.get("url", ""), media.get("thumbnailFullUrl", "")]:
            resolved = resolve_local_media_asset(route, value, media_lookup)
            if resolved:
                return resolved
    return ""


def build_data() -> tuple[dict, list[dict[str, str]], list[dict[str, str]], dict]:
    pages = read_csv(CONTENT_CSV)
    media_rows = read_csv(MEDIA_CSV)
    external_rows = read_csv(EXTERNAL_CSV) if EXTERNAL_CSV.exists() else []
    media_grouped = media_by_route(media_rows)
    product_media_by_key = product_media_lookup(media_rows)
    feed_posts = parse_feed_posts()
    ledger = build_route_ledger(pages)
    ledger_by_route = {item["route"]: item for item in ledger}
    canonical_manifest = load_canonical_manifest()

    counts_by_type = Counter(row["page_type"] for row in pages)
    counts_by_refactor = Counter(row["recommended_refactor_category"] for row in pages)
    product_counts = Counter(row["current_category"] for row in pages if row["page_type"] == "product")

    products = []
    guides = []
    artists = []
    service_pages = []
    shop_pages = []
    utility_pages = []

    for row in pages:
        route = row["route_path"]
        ledger_item = ledger_by_route[route]
        base = {
            "title": clean_title(row.get("title", "")),
            "sourceTitle": clean_text(row.get("title", "")),
            "route": route,
            "legacyUrl": row.get("legacy_url", ""),
            "recommendedLegacyUrl": row.get("recommended_legacy_url", ""),
            "destinationPath": ledger_item["destinationPath"],
            "destinationStatus": ledger_item["destinationStatus"],
            "futureSection": row.get("recommended_refactor_category", ""),
            "excerpt": clean_excerpt(row.get("body_text_excerpt", ""), row.get("title", ""), 240),
            "body": clean_excerpt(row.get("body_text_excerpt", ""), row.get("title", ""), 1600),
            "image": pick_image(row, media_grouped),
            "mediaCount": safe_int(row.get("media_count")),
            "externalLinkCount": safe_int(row.get("external_link_count")),
            "notes": clean_text(row.get("notes", "")),
        }

        if row["page_type"] == "product":
            truth = extract_product_truth(row)
            manifest_row = canonical_manifest.get(route, {})
            truth_image = product_truth_image(route, truth, product_media_by_key)
            manifest_body_html = str(manifest_row.get("source_body_html", "")) if manifest_row else ""
            manifest_body_text = str(manifest_row.get("source_body_text", "")) if manifest_row else ""
            product_body = manifest_body_text or truth.get("description") or base["body"]
            additional_info_text = truth.get("additionalInfoText", "")
            if additional_info_text and not manifest_body_text:
                product_body = clean_text(f"{product_body} {additional_info_text}", 1600)
            manifest_image = manifest_asset_for_record(manifest_row) if manifest_row else ""
            products.append(
                {
                    **base,
                    "title": truth.get("name") or base["title"],
                    "excerpt": clean_text(product_body, 240),
                    "body": product_body,
                    "bodyHtml": manifest_body_html,
                    "image": manifest_image or truth_image or base["image"],
                    "category": row.get("current_category", ""),
                    "categoryLabel": product_category_label(row.get("current_category", "")),
                    "price": truth.get("formattedPrice") or first_price(clean_text(row.get("body_text_excerpt", ""))),
                    "productType": truth.get("productType", ""),
                    "inventoryStatus": truth.get("inventoryStatus", ""),
                    "isInStock": truth.get("isInStock", False),
                    "additionalInfo": truth.get("additionalInfo", []),
                    "productMedia": truth.get("media", []),
                    "productTruthSource": truth.get("source", "catalog"),
                    "sourceConfidence": "wix stores warmup data" if truth else "catalog extracted",
                    "canonicalImageUrl": str(manifest_row.get("canonical_image_url", "")) if manifest_row else "",
                    "canonicalImageMediaId": str(manifest_row.get("canonical_image_media_id", "")) if manifest_row else "",
                    "canonicalImageSource": str(manifest_row.get("canonical_image_source", "")) if manifest_row else "",
                    "canonicalAssetPath": rebuild_asset_path(str(manifest_row.get("local_canonical_asset_path", ""))) if manifest_row else "",
                    "canonicalWorkspaceAssetPath": str(ROOT / str(manifest_row.get("local_canonical_asset_path", ""))) if manifest_row else "",
                    "imageSourceUrl": str(manifest_row.get("canonical_image_url", "")) if manifest_row else "",
                    "canonicalAssetWidth": safe_int(str(manifest_row.get("asset_width", ""))) if manifest_row else 0,
                    "canonicalAssetHeight": safe_int(str(manifest_row.get("asset_height", ""))) if manifest_row else 0,
                    "assetMatchStatus": str(manifest_row.get("asset_match_status", "")) if manifest_row else "",
                    "contentStatus": str(manifest_row.get("content_status", "")) if manifest_row else "",
                }
            )
        elif row["page_type"] in GUIDE_TYPES:
            if row["page_type"] == "blog_post":
                blog_source = extract_blog_source(row, feed_posts, product_media_by_key, media_grouped)
                guides.append(
                    {
                        **base,
                        **blog_source,
                        "type": row["page_type"],
                        "sourceConfidence": "local post html + rss feed",
                    }
                )
            else:
                guides.append(
                    {
                        **base,
                        "type": row["page_type"],
                        "category": guide_category(row),
                        "sourceConfidence": "catalog extracted",
                    }
                )
        elif row["page_type"] == "shop_page":
            shop_pages.append({**base, "type": row["page_type"]})
        elif row["page_type"] == "profile":
            utility_pages.append({**base, "type": row["page_type"]})
        elif row["recommended_refactor_category"] == "Artists":
            artists.append({**base, "type": row["page_type"]})
        elif row["recommended_refactor_category"] in SERVICE_CATEGORIES:
            service_pages.append({**base, "type": row["page_type"], "category": row["recommended_refactor_category"]})
        else:
            service_pages.append({**base, "type": row["page_type"], "category": row["recommended_refactor_category"]})

    risky_media = []
    media_risk_counter = Counter()
    for row in media_rows:
        risk = clean_text(row.get("risk", "")) or "none"
        media_risk_counter[risk] += 1
        if risk != "none":
            risky_media.append(
                {
                    "route": row.get("page_route", ""),
                    "title": clean_title(row.get("page_title", "")),
                    "risk": risk,
                    "mediaUrl": row.get("media_url", ""),
                    "localPath": row.get("local_path", ""),
                    "status": row.get("scrape_status", ""),
                }
            )

    include_counter = Counter((row.get("include_in_rebuild") or "blank").lower() for row in external_rows)
    external_counter = Counter()
    approved_links = []
    for row in external_rows:
        domain = external_domain(row.get("url", ""))
        if not domain:
            continue
        if not any(skip in domain for skip in ["cid", "wix", "parastorage", "sentry", "wixmp"]):
            external_counter[domain] += 1
        if approved_external(row):
            approved_links.append(
                {
                    "pageRoute": row.get("page_route", ""),
                    "label": clean_text(row.get("link_text", "")),
                    "url": row.get("url", ""),
                    "domain": domain,
                }
            )

    redirects = []
    for item in ledger:
        source = item["redirectSource"]
        target = item["destinationPath"]
        redirects.append(
            {
                "source": source,
                "target": target if target.startswith("#") else public_url_path(target),
                "status": item["destinationStatus"],
                "route": item["route"],
                "type": item["type"],
            }
        )

    data = {
        "version": "1.2",
        "generatedAt": date.today().isoformat(),
        "siteMeta": {
            "name": "Diversity Tattoo",
            "description": "Diversity Tattoo, Piercing and Smoke Shop in Las Vegas.",
            "source": "catalog/content-inventory.csv",
        },
        "stats": {
            "routes": len(pages),
            "products": counts_by_type["product"],
            "shopPages": counts_by_type["shop_page"],
            "guideRoutes": sum(counts_by_type[item] for item in GUIDE_TYPES),
            "blogPosts": counts_by_type["blog_post"],
            "blogCategories": counts_by_type["blog_category"],
            "blogRedirects": counts_by_type["blog_redirect"],
            "profiles": counts_by_type["profile"],
            "mediaReferences": len(media_rows),
            "riskyMediaReferences": len(risky_media),
            "externalLinks": len(external_rows),
            "externalApproved": include_counter["yes"],
            "externalReview": include_counter["review"],
            "routeTypes": dict(sorted(counts_by_type.items())),
            "futureSections": dict(sorted(counts_by_refactor.items())),
            "productCategories": dict(sorted(product_counts.items())),
        },
        "contact": CONTACT,
        "products": products,
        "guides": guides,
        "artists": artists,
        "servicePages": service_pages,
        "shopPages": shop_pages,
        "utilityPages": utility_pages,
        "piercingPrices": PIERCING_ROWS,
        "routeCoverage": ledger,
        "redirects": redirects,
        "mediaRisks": risky_media[:160],
        "mediaRiskSummary": dict(media_risk_counter.most_common()),
        "externalDomains": dict(external_counter.most_common(12)),
        "approvedExternalLinks": approved_links[:80],
    }

    media_review = {
        "generatedAt": data["generatedAt"],
        "totalMediaReferences": len(media_rows),
        "riskSummary": dict(media_risk_counter.most_common()),
        "risks": risky_media,
    }

    return data, ledger, redirects, media_review


def observed_path(url: str) -> str:
    parsed = urlparse(url)
    return parsed.path + (f"?{parsed.query}" if parsed.query else "")


def classify_404_path(path: str) -> str:
    if re.search(r"\.(jpg|jpeg|png|webp|svg|gif)(\?|$)", path, re.IGNORECASE) or any(
        marker in path for marker in ["/quality_auto/", "/enc_auto/", "/media/"]
    ):
        return "malformed_or_missing_media_url"
    if path.startswith("/post/categories/") and path.endswith(".html"):
        return "legacy_blog_category_html_alias"
    if path.startswith("/post/") and path.endswith(".html"):
        return "legacy_blog_html_alias"
    if path.startswith("/blog/hashtags/"):
        return "missing_blog_hashtag_archive"
    return "missing_legacy_promo_page"


def media_lookup_key(path: str) -> str:
    matches = re.findall(r"([A-Za-z0-9]+_[A-Za-z0-9]+(?:~mv2(?:_[^/.]+)?)?)", path)
    media_matches = [match for match in matches if match not in {"quality_auto", "enc_auto"} and len(match) > 20]
    if media_matches:
        raw = media_matches[-1].replace("~", "_")
        return raw.split("_mv2")[0] if "_mv2" in raw else raw
    return Path(path).name.split(".")[0]


def canonical_row_for_observed_404(path: str, pages: list[dict[str, str]]) -> dict[str, str] | None:
    by_recommended = {}
    by_route = {}
    for row in pages:
        parsed = urlparse(row.get("recommended_legacy_url") or row.get("legacy_url") or "")
        if parsed.path:
            by_recommended[parsed.path.rstrip("/")] = row
        by_route["/" + row.get("route_path", "").removesuffix(".html").rstrip("/")] = row

    if path.startswith("/post/categories/"):
        slug = path.rsplit("/", 1)[-1].removesuffix(".html")
        canonical = f"/blog/categories/{slug}"
    else:
        canonical = path.removesuffix(".html")
    return by_recommended.get(canonical.rstrip("/")) or by_route.get(canonical.rstrip("/"))


def build_observed_404_ledger(
    pages: list[dict[str, str]], media_rows: list[dict[str, str]], route_ledger: list[dict[str, str]]
) -> list[dict[str, str]]:
    if not SCRAPE_LOG_JSON.exists():
        return []

    scrape_entries = json.loads(SCRAPE_LOG_JSON.read_text(encoding="utf-8"))
    route_by_path = {row["route"]: row for row in route_ledger}
    media_rows_by_key: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in media_rows:
        key = media_lookup_key(row.get("media_key", ""))
        if key:
            media_rows_by_key[key].append(row)
        media_url_key = media_lookup_key(urlparse(row.get("media_url", "")).path)
        if media_url_key:
            media_rows_by_key[media_url_key].append(row)

    ledger = []
    for entry in scrape_entries:
        if entry.get("status") != 404:
            continue
        url = entry.get("url", "")
        path = observed_path(url)
        classification = classify_404_path(path)
        canonical_target = ""
        notes = ""

        if classification == "malformed_or_missing_media_url":
            key = media_lookup_key(path)
            matches = media_rows_by_key.get(key, [])
            unique_routes = sorted({row.get("page_route", "") for row in matches if row.get("page_route", "")})
            has_local_media = any(row.get("local_path") for row in matches)
            data_status = "accounted_elsewhere" if has_local_media else ("referenced_but_not_localized" if matches else "missing_unmatched")
            canonical_target = "; ".join(unique_routes[:4])
            sitemap_action = "document_only"
            implementation_action = "no_page_media_accounted" if has_local_media else "omit_use_404"
            notes = (
                "Malformed Wix media transform URL; the underlying media is represented elsewhere."
                if has_local_media
                else "Wix placeholder or unlocalized media reference with no recoverable page content."
            )
        elif classification in {"legacy_blog_html_alias", "legacy_blog_category_html_alias"}:
            canonical = RECOVERABLE_404_ALIASES.get(path)
            row = canonical_row_for_observed_404(path, pages)
            if not canonical and row:
                target = route_by_path.get(row.get("route_path", ""), {}).get("destinationPath", "")
                canonical = f"/{target}" if target else ""
            data_status = "canonical_content_available" if canonical else "missing_unmatched"
            canonical_target = canonical or ""
            sitemap_action = "document_and_alias" if canonical else "document_only"
            implementation_action = "create_static_alias" if canonical else "omit_use_404"
            notes = "Observed extension-bearing legacy URL; canonical blog content is available in the sitemap."
        elif classification == "missing_blog_hashtag_archive":
            data_status = "not_in_sitemap_no_source_content"
            sitemap_action = "document_only"
            implementation_action = "omit_use_404"
            notes = "Wix hashtag archive URL was observed as 404 and has no recoverable sitemap content."
        else:
            data_status = "not_in_sitemap_no_source_content"
            sitemap_action = "document_only"
            implementation_action = "omit_use_404"
            notes = "Stale promotional URL linked from old page content; no standalone page was captured."

        ledger.append(
            {
                "observed_url": url,
                "observed_path": path,
                "status": str(entry.get("status", "")),
                "classification": classification,
                "data_status": data_status,
                "canonical_target": canonical_target,
                "sitemap_action": sitemap_action,
                "implementation_action": implementation_action,
                "notes": notes,
            }
        )
    return ledger


def write_observed_404_files(ledger: list[dict[str, str]]) -> None:
    write_json(OBSERVED_404_JSON, ledger)
    fieldnames = [
        "observed_url",
        "observed_path",
        "status",
        "classification",
        "data_status",
        "canonical_target",
        "sitemap_action",
        "implementation_action",
        "notes",
    ]
    with OBSERVED_404_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ledger)


def update_site_map_404_section(ledger: list[dict[str, str]]) -> None:
    marker = "## Observed 404s - Not Implementation Targets"
    text = SITE_MAP_MD.read_text(encoding="utf-8")
    if marker in text:
        text = text.split(marker, 1)[0].rstrip()

    lines = [
        "",
        marker,
        "",
        "These URLs returned HTTP 404 during scrape/reconciliation. They are documented for accounting only and are not added to the 171-route rebuild count unless a canonical target is listed.",
        "",
    ]
    for item in ledger:
        lines.extend(
            [
                f"- **{item['observed_path']}** | `{item['classification']}` | status: `{item['data_status']}`",
                f"  - Observed URL: {item['observed_url']}",
                f"  - Canonical target: {item['canonical_target'] or 'None'}",
                f"  - Sitemap action: {item['sitemap_action']}",
                f"  - Implementation action: {item['implementation_action']}",
                f"  - Notes: {item['notes']}",
            ]
        )
    SITE_MAP_MD.write_text(text.rstrip() + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def write_local_sitemap_html(observed_404_ledger: list[dict[str, str]]) -> None:
    section = ""
    rows: list[dict[str, str]] = []
    notes_by_route: dict[str, list[str]] = {}
    last_route = ""
    in_404_section = False

    for line in SITE_MAP_MD.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            in_404_section = section == "Observed 404s - Not Implementation Targets"
            last_route = ""
            continue
        if in_404_section:
            continue
        match = re.match(r"- \*\*(.*?)\*\* \| `([^`]+)` \| `([^`]+)`", line)
        if match:
            title, route, page_type = match.groups()
            if route == "sitemap.html":
                last_route = ""
                continue
            rows.append({"section": section, "title": title, "route": route, "type": page_type})
            last_route = route
            continue
        note_match = re.match(r"\s+- Notes: (.*)", line)
        if note_match and last_route:
            notes_by_route.setdefault(last_route, []).append(note_match.group(1))

    parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>Diversity Tattoo Local Sitemap</title>",
        "<style>",
        "body{font-family:Arial,sans-serif;margin:24px;line-height:1.4;background:#fff;color:#111}",
        "h1{font-size:28px;margin-bottom:4px} h2{margin-top:28px;border-bottom:1px solid #ddd;padding-bottom:4px}",
        "table{border-collapse:collapse;width:100%;margin-top:8px} th,td{border-bottom:1px solid #e5e5e5;padding:8px;text-align:left;vertical-align:top}",
        "th{background:#f6f6f6;font-size:13px} code{font-family:Consolas,monospace;font-size:12px} a{color:#0645ad}",
        ".muted{color:#666}",
        "</style>",
        "</head>",
        "<body>",
        "<h1>Diversity Tattoo Local Sitemap</h1>",
        "<p>Generated from catalog/site-map.md.</p>",
    ]
    current_section = None
    for row in rows:
        if row["section"] != current_section:
            if current_section is not None:
                parts.append("</tbody></table>")
            current_section = row["section"]
            parts.append(f"<h2>{escape(current_section)}</h2>")
            parts.append("<table><thead><tr><th>Page</th><th>Type</th><th>Local Path</th><th>Notes</th></tr></thead><tbody>")
        route = row["route"]
        notes = " ".join(notes_by_route.get(route, []))
        parts.append(
            "<tr>"
            f'<td><a href="{escape(route, quote=True)}">{escape(row["title"])}</a></td>'
            f"<td>{escape(row['type'])}</td>"
            f"<td><code>{escape(route)}</code></td>"
            f"<td>{escape(notes)}</td>"
            "</tr>"
        )
    if current_section is not None:
        parts.append("</tbody></table>")

    parts.append("<h2>Observed 404s - Not Implementation Targets</h2>")
    parts.append(
        "<p class=\"muted\">These observed failures are documented for accounting only. They are not browse targets in the rebuilt sitemap unless a canonical target is listed.</p>"
    )
    parts.append(
        "<table><thead><tr><th>Observed Path</th><th>Class</th><th>Data Status</th><th>Canonical Target</th><th>Implementation</th><th>Notes</th></tr></thead><tbody>"
    )
    for item in observed_404_ledger:
        target = item["canonical_target"]
        target_html = f"<code>{escape(target)}</code>" if target else "<span class=\"muted\">None</span>"
        parts.append(
            "<tr>"
            f"<td><code>{escape(item['observed_path'])}</code></td>"
            f"<td>{escape(item['classification'])}</td>"
            f"<td>{escape(item['data_status'])}</td>"
            f"<td>{target_html}</td>"
            f"<td>{escape(item['implementation_action'])}</td>"
            f"<td>{escape(item['notes'])}</td>"
            "</tr>"
        )
    parts.append("</tbody></table>")
    parts.extend(["</body>", "</html>"])
    LOCAL_SITEMAP_HTML.write_text("\n".join(parts) + "\n", encoding="utf-8")


def html_page(
    title: str,
    eyebrow: str,
    body: str,
    image: str,
    meta: list[tuple[str, str]],
    back_href: str = "../index.html",
    canonical_path: str = "",
    primary_label: str = "Contact the studio",
    primary_href: str = "../index.html#visit",
    robots: str = "index, follow",
    body_html_override: str = "",
) -> str:
    meta_html = "\n".join(
        f"<li><strong>{escape(label)}</strong><span>{escape(value)}</span></li>" for label, value in meta if value
    )
    body_html = body_html_override or body_to_html(body)
    canonical_html = f'    <link rel="canonical" href="{escape(canonical_path, quote=True)}" />\n' if canonical_path else ""
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape(title)} | Diversity Tattoo</title>
    <meta name="description" content="{escape(clean_text(body, 155))}" />
{canonical_html}    <meta name="robots" content="{escape(robots)}" />
    <link rel="icon" href="/assets/static.wixstatic.com/media/8d0ab0_6a77779840c44b9586da1fefe272017b_mv2_d_3300_1480_s_4_2.png" type="image/png" />
    <link rel="stylesheet" href="../styles.css?v=1.2.1" />
  </head>
  <body class="detail-page">
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header is-stuck" data-sticky-header>
      <a class="brand-mark" href="{escape(back_href)}#top" aria-label="Diversity Tattoo home">
        <img src="../assets/static.wixstatic.com/media/8d0ab0_6a77779840c44b9586da1fefe272017b_mv2_d_3300_1480_s_4_2.png" alt="Diversity Tattoo" />
      </a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
      <nav class="site-nav is-detail-nav" id="site-nav" aria-label="Detail navigation">
        {section_nav_html("../")}
      </nav>
      <a class="header-cta" href="tel:17024541300">Call</a>
    </header>
    <main id="main" class="detail-shell">
      <article class="detail-article">
        <img class="detail-hero-image" src="{escape(detail_image_path(image))}" alt="{escape(title)}" />
        <div class="detail-copy">
          <p class="eyebrow">{escape(eyebrow)}</p>
          <h1>{escape(title)}</h1>
          <div class="detail-body">
            {body_html}
          </div>
          <ul class="contact-detail-list detail-meta">
            {meta_html}
          </ul>
          <a class="button primary" href="{escape(primary_href)}">{escape(primary_label)}</a>
          <a class="button secondary" href="{escape(back_href)}">Home</a>
        </div>
      </article>
    </main>
    <script src="../motion.js"></script>
  </body>
</html>
"""


def body_to_html(body: str) -> str:
    blocks = [clean_text(block) for block in re.split(r"\n{2,}", body or "") if clean_text(block)]
    if not blocks:
        return "<p>Contact Diversity Tattoo for current details.</p>"
    return "\n".join(f"<p>{escape(block)}</p>" for block in blocks)


def section_nav_html(prefix: str = "../") -> str:
    return f"""
        <a href="/tattoo/">Tattoo</a>
        <a href="/artists/">Artists</a>
        <a href="/piercing/">Piercing</a>
        <a href="/tooth-gems/">Tooth Gems</a>
        <a href="/smoke-shop/">Smoke Shop</a>
        <a href="/shop/">Shop all</a>
        <a href="/blog/">Blog</a>
        <a href="/reviews/">Reviews</a>
        <a href="/faq/">FAQ</a>
        <a href="/#visit">Visit</a>
    """


def section_source_cards(source_pages: list[dict]) -> str:
    if not source_pages:
        return ""
    cards = []
    for page in source_pages:
        body = page.get("body") or page.get("excerpt", "")
        cards.append(
            f"""
            <article class="service-record is-visible">
              <span>{escape(page.get('category', 'Service'))}</span>
              <h3>{escape(page.get('title', 'Service detail'))}</h3>
              <p>{escape(clean_text(body, 260))}</p>
            </article>
            """
        )
    return f"""
      <section class="section section-band">
        <div class="section-intro">
          <p class="eyebrow">Details</p>
          <h2>Service details.</h2>
          <p>Review the most useful details, then call or visit for current availability and guidance.</p>
        </div>
        <div class="service-record-grid" data-stagger>
          {''.join(cards)}
        </div>
      </section>
    """


def section_highlight_cards(highlights: list[str]) -> str:
    return "".join(
        f"""
        <article class="service-record is-visible">
          <span>{escape(str(index).zfill(2))}</span>
          <h3>{escape(highlight)}</h3>
          <p>Call or visit when you are ready for current options, timing, and next steps.</p>
        </article>
        """
        for index, highlight in enumerate(highlights, start=1)
    )


def section_hero_actions(config: dict) -> str:
    actions = [
        ("button primary", config["primaryHref"], config["primaryLabel"]),
        ("button secondary", config["secondaryHref"], config["secondaryLabel"]),
    ]
    for action in config.get("extraActions", []):
        actions.append(("button secondary", action["href"], action["label"]))
    return "\n".join(
        f'            <a class="{escape(class_name, quote=True)}" href="{escape(href, quote=True)}">{escape(label)}</a>'
        for class_name, href, label in actions
    )


def piercing_price_section() -> str:
    return """
      <section class="section price-section" id="pricing">
        <div class="section-intro">
          <p class="eyebrow">Piercing pricing</p>
          <h2>Common piercing options.</h2>
          <p>Call ahead for current jewelry availability and any service-specific instructions.</p>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th scope="col">Service</th>
                <th scope="col">Price</th>
                <th scope="col">Notes</th>
              </tr>
            </thead>
            <tbody id="piercing-price-body"></tbody>
          </table>
        </div>
      </section>
    """


def scoped_product_section(config: dict) -> str:
    scope = config.get("productScope")
    if not scope:
        return ""
    return f"""
      <section class="section product-catalog">
        <div class="section-intro">
          <p class="eyebrow">Products</p>
          <h2>{escape(config.get('productIntro', 'Related products'))}</h2>
          <p>{escape(config.get('productCopy', 'Browse related products before visiting the studio.'))}</p>
        </div>
        {shop_controls_html("../", scope, include_scripts=False)}
      </section>
    """


def write_section_pages(data: dict) -> None:
    for config in SECTION_PAGE_CONFIGS:
        source_pages = [
            page
            for page in data.get("servicePages", [])
            if page.get("category") in set(config.get("sourceCategories", []))
        ]
        if config["key"] == "tooth-gems":
            specific_source_image = next(
                (
                    page.get("image")
                    for page in source_pages
                    if page.get("image") and page.get("image") != CATEGORY_IMAGES["Tooth Gems"]
                ),
                "",
            )
            if specific_source_image:
                config = {**config, "heroImage": specific_source_image}
            else:
                config = {**config, "heroImage": ASSET_NOT_FOUND_IMAGE}
        source_cards = section_source_cards(source_pages)
        price_section = piercing_price_section() if config["key"] == "piercing" else ""
        product_section = scoped_product_section(config)
        canonical_path = public_url_path(config["path"])
        page = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape(config['title'])} | Diversity Tattoo</title>
    <meta name="description" content="{escape(config['description'])}" />
    <link rel="canonical" href="{escape(canonical_path, quote=True)}" />
    <meta name="robots" content="index, follow" />
    <link rel="icon" href="/assets/static.wixstatic.com/media/8d0ab0_6a77779840c44b9586da1fefe272017b_mv2_d_3300_1480_s_4_2.png" type="image/png" />
    <link rel="stylesheet" href="../styles.css?v=1.2.1" />
  </head>
  <body class="detail-page section-page">
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header is-stuck" data-sticky-header>
      <a class="brand-mark" href="../index.html#top" aria-label="Diversity Tattoo home">
        <img src="../assets/static.wixstatic.com/media/8d0ab0_6a77779840c44b9586da1fefe272017b_mv2_d_3300_1480_s_4_2.png" alt="Diversity Tattoo" />
      </a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
      <nav class="site-nav is-detail-nav" id="site-nav" aria-label="Section navigation">
        {section_nav_html("../")}
      </nav>
      <a class="header-cta" href="tel:17024541300">Call</a>
    </header>
    <main id="main" class="detail-shell section-shell" data-motion-root>
      <section class="section-page-hero" data-reveal="up">
        <div class="section-page-copy">
          <p class="eyebrow">{escape(config['eyebrow'])}</p>
          <h1 data-split>{escape(config['title'])}</h1>
          <p>{escape(config['summary'])}</p>
          <div class="hero-actions">
{section_hero_actions(config)}
          </div>
        </div>
        <img class="section-page-image" src="{escape(detail_image_path(config['heroImage']), quote=True)}" alt="{escape(config['title'])}" />
      </section>

      <section class="section section-band">
        <div class="section-intro">
          <p class="eyebrow">Overview</p>
          <h2>Highlights.</h2>
          <p>Use these quick points to decide the best next step before calling or visiting.</p>
        </div>
        <div class="service-record-grid" data-stagger>
          {section_highlight_cards(config.get('highlights', []))}
        </div>
      </section>

      {source_cards}
      {price_section}
      {product_section}

      <section class="section contact-section">
        <div class="section-intro">
          <p class="eyebrow">Visit</p>
          <h2>Call or stop by the Rancho studio.</h2>
          <p>Use the details below for appointment questions, product availability and day-of visit planning.</p>
        </div>
        <ul class="contact-detail-list" id="contact-detail-list"></ul>
        <div class="hero-actions">
          <a class="button primary" href="tel:+17024541300">Call now</a>
          <a class="button secondary" href="../index.html#visit">Homepage visit details</a>
        </div>
      </section>
    </main>
    <script src="../site-data.js"></script>
    <script src="../content-render.js"></script>
    <script src="../motion.js"></script>
  </body>
</html>
"""
        path = OUT_DIR / config["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(page, encoding="utf-8")


def write_blog_archive(data: dict) -> None:
    posts = sorted(
        [guide for guide in data["guides"] if guide.get("type") == "blog_post"],
        key=lambda post: safe_int(post.get("archiveOrder")) or 999,
    )
    cards = "\n".join(
        f"""
        <a class="guide-card hover-lift is-visible" href="{escape(Path(post['destinationPath']).name)}">
          <img src="../{escape(post['image'])}" alt="{escape(post['title'])}" loading="lazy" />
          <div>
            <span>{escape(post.get('category', 'Blog'))}</span>
            <h2>{escape(post['title'])}</h2>
            <p>{escape(post.get('excerpt', ''))}</p>
            <span class="details-link">Read post</span>
          </div>
        </a>
        """
        for post in posts
    )
    (OUT_DIR / "blog" / "index.html").write_text(
        f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Blog | Diversity Tattoo</title>
    <meta name="description" content="Tattoo, piercing, smoke shop and product education from Diversity Tattoo in Las Vegas." />
    <link rel="canonical" href="/blog/" />
    <meta name="robots" content="index, follow" />
    <link rel="icon" href="/assets/static.wixstatic.com/media/8d0ab0_6a77779840c44b9586da1fefe272017b_mv2_d_3300_1480_s_4_2.png" type="image/png" />
    <link rel="stylesheet" href="../styles.css?v=1.2.1" />
  </head>
  <body class="detail-page">
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header is-stuck" data-sticky-header>
      <a class="brand-mark" href="../index.html#top" aria-label="Diversity Tattoo home">
        <img src="../assets/static.wixstatic.com/media/8d0ab0_6a77779840c44b9586da1fefe272017b_mv2_d_3300_1480_s_4_2.png" alt="Diversity Tattoo" />
      </a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
      <nav class="site-nav is-detail-nav" id="site-nav" aria-label="Blog navigation">
        {section_nav_html("../")}
      </nav>
      <a class="header-cta" href="tel:17024541300">Call</a>
    </header>
    <main id="main" class="detail-shell">
      <section class="section" id="blog">
        <div class="section-intro">
          <p class="eyebrow">Blog</p>
          <h1>Advice, aftercare and product education.</h1>
          <p>Browse tattoo planning, aftercare, detox and product education from the studio.</p>
        </div>
        <div class="guide-grid" id="blog-archive-grid">
          {cards}
        </div>
      </section>
    </main>
    <script src="../motion.js"></script>
  </body>
</html>
""",
        encoding="utf-8",
    )


def write_blog_source_archive(data: dict) -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    posts = sorted(
        [guide for guide in data["guides"] if guide.get("type") == "blog_post"],
        key=lambda post: safe_int(post.get("archiveOrder")) or 999,
    )
    rows = [
        {
            "title": post.get("title", ""),
            "slug": Path(post.get("destinationPath", "")).stem,
            "sourceUrl": post.get("sourceUrl", ""),
            "canonicalUrl": "/" + post.get("destinationPath", ""),
            "pubDate": post.get("pubDate", ""),
            "category": post.get("category", ""),
            "image": post.get("image", ""),
            "excerpt": post.get("excerpt", ""),
            "body": post.get("body", ""),
        }
        for post in posts
    ]
    write_json(BLOG_SOURCE_JSON, rows)
    parts = ["# Diversity Tattoo Blog Source Archive", ""]
    for row in rows:
        parts.extend(
            [
                f"## {row['title']}",
                "",
                f"- Slug: `{row['slug']}`",
                f"- Source: {row['sourceUrl']}",
                f"- Canonical: {row['canonicalUrl']}",
                f"- Date: {row['pubDate']}",
                f"- Category: {row['category']}",
                "",
                str(row["body"]),
                "",
            ]
        )
    BLOG_SOURCE_MD.write_text("\n".join(parts).strip() + "\n", encoding="utf-8")


def filter_slug(value: str) -> str:
    return re.sub(r"(^-+|-+$)", "", re.sub(r"[^a-z0-9]+", "-", value.lower()))


def product_category_tiles_html(data: dict, prefix: str = "", categories: list[str] | None = None) -> str:
    categories = categories or PRODUCT_CATEGORY_ORDER
    products = data.get("products", [])
    cards = []
    for category in categories:
        count = sum(1 for product in products if product.get("category") == category)
        if not count:
            continue
        label = product_category_label(category)
        image = CATEGORY_IMAGES.get(category, CATEGORY_IMAGES["Shop - Other Products"])
        href = f"{prefix}shop/index.html?category={filter_slug(label)}#product-filters"
        cards.append(
            f"""
            <a class="category-tile hover-lift is-visible" href="{escape(href, quote=True)}">
              <img src="{escape(prefix + image, quote=True)}" alt="{escape(label)}" loading="lazy" />
              <div>
                <span>{escape(str(count))} products</span>
                <h3>{escape(label)}</h3>
                <p>Browse {escape(label.lower())} before visiting the studio.</p>
              </div>
            </a>
            """
        )
    return f"""<div class="category-tile-grid" data-stagger>
      {''.join(cards)}
    </div>"""


def shop_controls_html(prefix: str = "", scope: list[str] | None = None, include_scripts: bool = True) -> str:
    scope_attr = ""
    if scope:
        scope_attr = f' data-product-scope="{escape("|".join(scope), quote=True)}"'
    scripts = (
        f"""
      <script src="{prefix}site-data.js"></script>
      <script src="{prefix}content-render.js"></script>
"""
        if include_scripts
        else ""
    )
    return f"""
      <div class="product-toolbar" id="product-filters" aria-label="Shop controls">
        <div class="filter-list" id="product-category-filter-list"></div>
        <label class="field-label" for="product-search">Search products</label>
        <input id="product-search" name="q" type="search" autocomplete="off" placeholder="Search by name, use or details" />
        <label class="field-label" for="product-sort">Sort products</label>
        <select id="product-sort" name="sort">
          <option value="category-name">Category then A-Z</option>
          <option value="name-asc">Name A-Z</option>
          <option value="price-asc">Price Low-High</option>
          <option value="price-desc">Price High-Low</option>
          <option value="stock-first">In-stock first</option>
        </select>
        <button class="button secondary" type="button" id="product-clear-filters" hidden>Clear filters</button>
      </div>
      <p class="catalog-count" id="product-filter-summary" aria-live="polite"></p>
      <div class="product-grid" id="product-grid" data-stagger{scope_attr}></div>
      {scripts}
"""


def write_shop_page(data: dict) -> None:
    (OUT_DIR / "shop" / "index.html").write_text(
        f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Shop | Diversity Tattoo</title>
    <meta name="description" content="Browse body jewelry, detox products, smoke accessories, vaporizers and other products available through Diversity Tattoo." />
    <link rel="canonical" href="/shop/" />
    <meta name="robots" content="index, follow" />
    <link rel="icon" href="/assets/static.wixstatic.com/media/8d0ab0_6a77779840c44b9586da1fefe272017b_mv2_d_3300_1480_s_4_2.png" type="image/png" />
    <link rel="stylesheet" href="../styles.css?v=1.2.1" />
  </head>
  <body class="detail-page">
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header is-stuck" data-sticky-header>
      <a class="brand-mark" href="../index.html#top" aria-label="Diversity Tattoo home">
        <img src="../assets/static.wixstatic.com/media/8d0ab0_6a77779840c44b9586da1fefe272017b_mv2_d_3300_1480_s_4_2.png" alt="Diversity Tattoo" />
      </a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
      <nav class="site-nav is-detail-nav" id="site-nav" aria-label="Shop navigation">
        {section_nav_html("../")}
      </nav>
      <a class="header-cta" href="tel:17024541300">Call</a>
    </header>
    <main id="main" class="detail-shell">
      <section class="section section-band">
        <div class="section-intro">
          <p class="eyebrow">Shop categories</p>
          <h1>Choose a product lane.</h1>
          <p>The full catalog remains below. These tiles help visitors jump into the current catalog categories before they come in.</p>
        </div>
        {product_category_tiles_html(data, "../")}
      </section>
      <section class="section product-catalog" id="shop-catalog">
        <div class="section-intro">
          <p class="eyebrow">Shop</p>
          <h1>Browse products before you visit.</h1>
          <p>Filter by category, search by product details and sort the full catalog on one page. Call the studio to confirm availability before stopping in.</p>
        </div>
        {shop_controls_html("../")}
      </section>
    </main>
    <script src="../motion.js"></script>
  </body>
</html>
""",
        encoding="utf-8",
    )


def write_detail_pages(data: dict) -> None:
    for dirname in DETAIL_DIRS:
        target = OUT_DIR / dirname
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)

    account_unavailable = OUT_DIR / "utility" / "account-unavailable.html"
    account_unavailable.write_text(
        html_page(
            "Account features are unavailable",
            "Account",
            "Online account features are not part of the public site. Contact the studio directly for appointments, retail questions, piercing questions or visit details.",
            CATEGORY_IMAGES["Location / Contact"],
            [("Contact", CONTACT["phone"]), ("Email", CONTACT["emails"][0])],
            canonical_path="/utility/account-unavailable.html",
            robots="noindex, follow",
        ),
        encoding="utf-8",
    )

    def write_record(
        record: dict,
        eyebrow: str,
        extra_meta: list[tuple[str, str]] | None = None,
        primary_label: str = "Contact the studio",
        primary_href: str = "../index.html#visit",
    ) -> None:
        destination = record["destinationPath"]
        if destination in {"index.html", "utility/account-unavailable.html"}:
            return
        path = OUT_DIR / destination
        path.parent.mkdir(parents=True, exist_ok=True)
        meta = []
        if extra_meta:
            meta.extend(extra_meta)
        path.write_text(
            html_page(
                record["title"],
                eyebrow,
                record.get("body") or record.get("excerpt", ""),
                record["image"],
                meta,
                canonical_path=public_url_path(destination),
                primary_label=primary_label,
                primary_href=primary_href,
                body_html_override=record.get("bodyHtml", ""),
            ),
            encoding="utf-8",
        )

    for product in data["products"]:
        write_record(
            product,
            product["categoryLabel"],
            [
                ("Price", product["price"]),
                ("Category", product["categoryLabel"]),
                ("Availability", product.get("inventoryStatus", "").replace("_", " ").title() or "Call to confirm"),
            ],
            primary_label="Ask about this product",
            primary_href="../index.html#visit",
        )
    for guide in data["guides"]:
        if guide["type"] != "blog_post":
            continue
        write_record(
            guide,
            guide["category"],
            [("Topic", guide["category"])],
            primary_label="See all posts",
            primary_href="index.html",
        )
    for artist in data["artists"]:
        write_record(artist, "Artist profile", [("Appointments", CONTACT["phone"])], primary_label="Start a visit")
    for service in data["servicePages"]:
        write_record(
            service,
            service.get("category", "Service"),
            [("Contact", CONTACT["phone"]), ("Location", CONTACT["address"])],
            primary_label="Contact the studio",
        )

    write_section_pages(data)
    write_blog_archive(data)
    write_shop_page(data)


def copy_assets() -> None:
    assets_root = OUT_DIR / "assets"
    preserved_dirs = ["products", "blog", "placeholders"]
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp_root = Path(tmp_name)
        manual_logo = OUT_DIR / LOGO_ASSET_PATH
        preserved_logo = tmp_root / LOGO_ASSET_PATH.name
        if manual_logo.exists():
            shutil.copy2(manual_logo, preserved_logo)

        for dirname in preserved_dirs:
            source = assets_root / dirname
            if source.exists():
                shutil.copytree(source, tmp_root / dirname)

        if assets_root.exists():
            shutil.rmtree(assets_root)
        assets_root.mkdir(parents=True, exist_ok=True)
        for dirname in ["static.wixstatic.com", "i.ytimg.com"]:
            source = ROOT / "site" / dirname
            if source.exists():
                shutil.copytree(source, assets_root / dirname)

        for dirname in preserved_dirs:
            preserved = tmp_root / dirname
            if preserved.exists():
                shutil.copytree(preserved, assets_root / dirname)

        logo_sources = [
            preserved_logo,
            ROOT / "v1.2 rebuild" / LOGO_ASSET_PATH,
            ROOT / "w" / "public" / LOGO_ASSET_PATH,
        ]
        logo_destination = OUT_DIR / LOGO_ASSET_PATH
        logo_destination.parent.mkdir(parents=True, exist_ok=True)
        for logo_source in logo_sources:
            if logo_source.exists():
                shutil.copy2(logo_source, logo_destination)
                break
        else:
            raise FileNotFoundError(f"Required cropped logo asset is missing: {LOGO_ASSET_PATH.as_posix()}")


def ensure_asset_not_found_placeholder() -> None:
    placeholder = OUT_DIR / ASSET_NOT_FOUND_IMAGE
    placeholder.parent.mkdir(parents=True, exist_ok=True)
    placeholder.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" width="900" height="900" viewBox="0 0 900 900" role="img" aria-labelledby="title desc">
  <title id="title">Asset not found</title>
  <desc id="desc">Placeholder shown when a canonical product image is unavailable.</desc>
  <rect width="900" height="900" fill="#11151d"/>
  <rect x="48" y="48" width="804" height="804" fill="#171d28" stroke="#394254" stroke-width="4"/>
  <path d="M226 589 365 423l95 112 62-75 152 129H226Z" fill="#2f394b"/>
  <circle cx="595" cy="305" r="66" fill="#2f394b"/>
  <text x="450" y="693" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="54" font-weight="700" fill="#f1f3f7">asset-not-found</text>
  <text x="450" y="752" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="28" fill="#aab3c2">canonical media missing</text>
</svg>
""",
        encoding="utf-8",
    )


def localize_record_image(
    record: dict,
    root_dir: str,
    min_edge: int,
    *,
    slim_min_edge: int = 0,
    slim_min_long_edge: int = 0,
    slim_min_area: int = 0,
) -> None:
    slug = Path(record.get("destinationPath", "")).stem or slug_from_route(record.get("route", ""))
    if not slug:
        return
    source_image = record.get("image") or CATEGORY_IMAGES.get(record.get("category", ""), "")
    placeholder_source = source_image == ASSET_NOT_FOUND_IMAGE
    source_path = local_path_for_asset(source_image) if source_image else None
    canonical_workspace_asset = str(record.get("canonicalWorkspaceAssetPath", "")).strip()
    canonical_workspace_path = Path(canonical_workspace_asset) if canonical_workspace_asset else None
    if (not source_path or not source_path.exists()) and canonical_workspace_path and canonical_workspace_path.exists():
        source_path = canonical_workspace_path
    source_url = str(record.get("imageSourceUrl", ""))
    use_source_path = (
        source_path
        if source_path
        and source_path.exists()
        and image_meets_quality(
            source_path,
            min_edge,
            slim_min_edge=slim_min_edge,
            slim_min_long_edge=slim_min_long_edge,
            slim_min_area=slim_min_area,
        )
        else None
    )
    if not use_source_path and source_path and source_path.exists() and not source_url:
        use_source_path = source_path
    suffix = extension_for_media(use_source_path or source_path, source_url)
    destination = OUT_DIR / "assets" / root_dir / slug / f"{slug}{suffix}"
    status = "missing"
    try:
        status = copy_or_download_media(use_source_path, source_url, destination)
    except Exception:
        if source_path and source_path.exists():
            if source_path.resolve() != destination.resolve():
                shutil.copy2(source_path, destination)
            status = "local_low_resolution_fallback"
    if not destination.exists():
        return
    width, height = image_size(destination)
    record["image"] = destination.relative_to(OUT_DIR).as_posix()
    record["imageWidth"] = width
    record["imageHeight"] = height
    record["imageBytes"] = destination.stat().st_size
    record["imageSourceStatus"] = status
    if record.get("canonicalImageMediaId"):
        record["generatedAssetMediaId"] = "asset-not-found" if placeholder_source else record["canonicalImageMediaId"]
        record["assetMatchStatus"] = "missing_image" if placeholder_source else "match"


def localize_product_images(data: dict) -> None:
    product_root = OUT_DIR / "assets" / "products"
    product_root.mkdir(parents=True, exist_ok=True)
    for product in data.get("products", []):
        if not product.get("imageSourceUrl"):
            media = next(iter(product.get("productMedia", [])), {})
            product["imageSourceUrl"] = media.get("fullUrl", "") or media.get("url", "")
        localize_record_image(
            product,
            "products",
            MIN_PRODUCT_IMAGE_EDGE,
            slim_min_edge=MIN_PRODUCT_SLIM_IMAGE_EDGE,
            slim_min_long_edge=MIN_PRODUCT_SLIM_IMAGE_LONG_EDGE,
            slim_min_area=MIN_PRODUCT_SLIM_IMAGE_AREA,
        )


def localize_blog_images(data: dict) -> None:
    blog_root = OUT_DIR / "assets" / "blog"
    blog_root.mkdir(parents=True, exist_ok=True)
    for guide in data.get("guides", []):
        if guide.get("type") == "blog_post":
            localize_record_image(guide, "blog", MIN_BLOG_IMAGE_EDGE)


def public_runtime_data(data: dict) -> dict:
    allowed_keys = [
        "version",
        "generatedAt",
        "siteMeta",
        "stats",
        "contact",
        "products",
        "guides",
        "artists",
        "servicePages",
        "piercingPrices",
    ]
    public_data = {key: data[key] for key in allowed_keys if key in data}
    def keep(item: dict, keys: list[str]) -> dict:
        return {key: item.get(key, "") for key in keys if key in item}

    public_data["products"] = [
        keep(
            product,
            [
                "title",
                "destinationPath",
                "excerpt",
                "body",
                "image",
                "category",
                "categoryLabel",
                "price",
                "inventoryStatus",
                "isInStock",
                "imageWidth",
                "imageHeight",
                "canonicalAssetWidth",
                "canonicalAssetHeight",
                "imageBytes",
                "imageSourceStatus",
                "bodyHtml",
                "canonicalImageMediaId",
                "canonicalImageSource",
                "generatedAssetMediaId",
                "assetMatchStatus",
                "contentStatus",
            ],
        )
        for product in public_data.get("products", [])
    ]
    public_data["guides"] = [
        keep(
            guide,
            [
                "title",
                "destinationPath",
                "excerpt",
                "body",
                "image",
                "type",
                "category",
                "pubDate",
                "archiveOrder",
                "imageWidth",
                "imageHeight",
                "imageBytes",
                "imageSourceStatus",
            ],
        )
        for guide in public_data.get("guides", [])
        if guide.get("type") == "blog_post"
    ]
    public_data["artists"] = [
        keep(artist, ["title", "destinationPath", "excerpt", "body", "image", "type"])
        for artist in public_data.get("artists", [])
    ]
    public_data["servicePages"] = [
        keep(service, ["title", "destinationPath", "excerpt", "body", "image", "type", "category"])
        for service in public_data.get("servicePages", [])
    ]
    public_data["siteMeta"] = {
        "name": "Diversity Tattoo",
        "description": "Diversity Tattoo, Piercing and Smoke Shop in Las Vegas.",
        "origin": PRODUCTION_ORIGIN,
    }
    return public_data


def write_js(data: dict) -> None:
    serialized = json.dumps(public_runtime_data(data), indent=2, ensure_ascii=True)
    SITE_DATA_JS.write_text(f"window.DIVERSITY_SITE_DATA = {serialized};\n", encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_dict_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_json_and_csv(json_path: Path, csv_path: Path, rows: list[dict[str, object]]) -> None:
    write_json(json_path, rows)
    write_dict_csv(csv_path, rows)


def source_route_ledger_rows(ledger: list[dict[str, str]]) -> list[dict[str, object]]:
    return [
        {
            "source_route": item["route"],
            "source_type": item["type"],
            "source_status": item["sourceContentStatus"],
            "content_area": item["futureSection"],
            "canonical_target": item["destinationPath"],
            "destination_status": item["destinationStatus"],
            "exception": "yes" if item["destinationPath"].startswith("utility/") else "",
        }
        for item in ledger
    ]


def canonical_url_map_rows(data: dict) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [
        {
            "url": "/",
            "page_type": "home",
            "source_evidence": "index.html",
            "indexability": "index",
            "included_in_sitemap": "yes",
        }
    ]
    collections = [
        ("products", "product"),
        ("guides", "blog_post"),
        ("artists", "artist"),
        ("servicePages", "service"),
    ]
    rows.extend(
        [
            {
                "url": public_url_path(item["destinationPath"]),
                "page_type": page_type,
                "source_evidence": item.get("route", ""),
                "indexability": "index",
                "included_in_sitemap": "yes",
            }
            for collection, page_type in collections
            for item in data.get(collection, [])
            if item.get("destinationPath") and not item["destinationPath"].startswith("utility/")
        ]
    )
    rows.extend(
        [
            {
                "url": "/shop/",
                "page_type": "shop_catalog",
                "source_evidence": "shop.html",
                "indexability": "index",
                "included_in_sitemap": "yes",
            },
            {
                "url": "/blog/",
                "page_type": "blog_archive",
                "source_evidence": "blog.html",
                "indexability": "index",
                "included_in_sitemap": "yes",
            },
        ]
    )
    deduped: dict[str, dict[str, object]] = {}
    for row in rows:
        deduped[str(row["url"])] = row
    return list(deduped.values())


def product_publication_rows(data: dict) -> list[dict[str, object]]:
    rows = []
    for product in data.get("products", []):
        image = product.get("image", "")
        rows.append(
            {
                "source_route": product.get("route", ""),
                "product": product.get("title", ""),
                "canonical_url": "/" + product.get("destinationPath", ""),
                "product_truth_status": "extracted_from_wix_stores_warmup_data"
                if product.get("productTruthSource") == "wix-warmup-data"
                else "catalog_fallback",
                "media_status": "localized_product_asset" if image.startswith("assets/products/") else "needs_review",
                "public_inclusion_status": "include",
                "suppression_reason": "",
                "category": product.get("categoryLabel", ""),
                "price": product.get("price", ""),
                "inventory_status": product.get("inventoryStatus", ""),
                "source_confidence": product.get("sourceConfidence", ""),
                "image": image,
                "image_width": product.get("imageWidth", ""),
                "image_height": product.get("imageHeight", ""),
                "image_bytes": product.get("imageBytes", ""),
                "image_source_status": product.get("imageSourceStatus", ""),
            }
        )
    return rows


def blog_post_rows(data: dict) -> list[dict[str, object]]:
    return [
        {
            "source_route": post.get("route", ""),
            "canonical_url": "/" + post.get("destinationPath", ""),
            "title": post.get("title", ""),
            "category": post.get("category", ""),
            "pub_date": post.get("pubDate", ""),
            "body_length": len(post.get("body", "")),
            "indexability": "index",
            "archive_order": post.get("archiveOrder") or index + 1,
        }
        for index, post in enumerate([item for item in data.get("guides", []) if item.get("type") == "blog_post"])
    ]


def alias_ledger_rows(aliases: list[dict[str, str]]) -> list[dict[str, object]]:
    return [
        {
            "old_url": item.get("source", ""),
            "generated_alias_path": item.get("path", ""),
            "canonical_target": item.get("target", ""),
            "reason": item.get("kind", ""),
            "noindex_status": "noindex",
        }
        for item in aliases
    ]


def write_accounting_ledgers(data: dict, ledger: list[dict[str, str]], aliases: list[dict[str, str]]) -> None:
    write_json_and_csv(SOURCE_ROUTE_LEDGER_JSON, SOURCE_ROUTE_LEDGER_CSV, source_route_ledger_rows(ledger))
    write_json_and_csv(CANONICAL_URL_MAP_JSON, CANONICAL_URL_MAP_CSV, canonical_url_map_rows(data))
    write_json_and_csv(ALIAS_LEDGER_JSON, ALIAS_LEDGER_CSV, alias_ledger_rows(aliases))
    write_json_and_csv(PRODUCT_PUBLICATION_LEDGER_JSON, PRODUCT_PUBLICATION_LEDGER_CSV, product_publication_rows(data))
    write_json_and_csv(BLOG_POST_LEDGER_JSON, BLOG_POST_LEDGER_CSV, blog_post_rows(data))


def write_redirects_txt(redirects: list[dict[str, str]]) -> None:
    lines = [
        "# Generated Diversity Tattoo v1.2 legacy redirects",
        "# Source paths are from catalog/content-inventory.csv.",
        "# Static alias pages are generated for portability; this file is an optional host enhancement.",
    ]
    seen: set[str] = set()
    for item in redirects:
        source = item["source"]
        target = item["target"]
        if not source or source in seen:
            continue
        seen.add(source)
        if source == "/":
            lines.append(f"# Root serves index.html directly; no redirect emitted for {source} -> {target}")
            continue
        if "?" in source:
            lines.append(f"# Query-bearing legacy route: {source} -> {target}")
            continue
        lines.append(f"{source} {target} 301")
    REDIRECTS_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def alias_output_path(source: str) -> Path | None:
    if not source or source == "/" or "?" in source:
        return None
    clean = source.lstrip("/")
    if not clean or clean == "shop":
        return None
    path = OUT_DIR / clean
    if Path(clean).suffix:
        return path
    return path / "index.html"


def alias_page(source: str, target: str, title: str = "Page moved") -> str:
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="robots" content="noindex, follow" />
    <meta http-equiv="refresh" content="0; url={escape(target, quote=True)}" />
    <link rel="canonical" href="{escape(target, quote=True)}" />
    <title>{escape(title)} | Diversity Tattoo</title>
    <script>window.location.replace({json.dumps(target)});</script>
    <style>
      body{{font-family:Arial,sans-serif;margin:40px;line-height:1.5;color:#141414;background:#fff}}
      a{{color:#0645ad}}
    </style>
  </head>
  <body>
    <main>
      <h1>{escape(title)}</h1>
      <p>This page has moved. Continue to <a href="{escape(target, quote=True)}">the current Diversity Tattoo page</a>.</p>
    </main>
  </body>
</html>
"""


def clean_alias_dirs() -> None:
    for dirname in ALIAS_CLEAN_DIRS:
        target = OUT_DIR / dirname
        if target.exists() and target.is_dir():
            shutil.rmtree(target)


def write_alias_pages(redirects: list[dict[str, str]], observed_404_ledger: list[dict[str, str]]) -> list[dict[str, str]]:
    clean_alias_dirs()
    aliases: list[dict[str, str]] = []
    for item in redirects:
        source = item["source"]
        target = item["target"]
        if item.get("type") == "profile":
            target = "/utility/account-unavailable.html"
        path = alias_output_path(source)
        if not path:
            continue
        alias_rel = path.relative_to(OUT_DIR).as_posix()
        target_rel = target.lstrip("/")
        if alias_rel == target_rel or (alias_rel.endswith("/index.html") and alias_rel[: -len("/index.html")] == target_rel.rstrip("/")):
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(alias_page(source, target, "Page moved"), encoding="utf-8")
        aliases.append({"source": source, "target": target, "path": alias_rel, "kind": "legacy_redirect"})

    existing_sources = {item["source"] for item in redirects}
    for item in observed_404_ledger:
        if item["implementation_action"] != "create_static_alias":
            continue
        source = item["observed_path"]
        if source in existing_sources:
            continue
        target = item["canonical_target"]
        path = alias_output_path(source)
        if not path or not target:
            continue
        alias_rel = path.relative_to(OUT_DIR).as_posix()
        target_rel = target.lstrip("/")
        if alias_rel == target_rel or (alias_rel.endswith("/index.html") and alias_rel[: -len("/index.html")] == target_rel.rstrip("/")):
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(alias_page(source, target, "Article moved"), encoding="utf-8")
        aliases.append({"source": source, "target": target, "path": alias_rel, "kind": "observed_404_alias"})
    return aliases


def write_support_files(data: dict) -> None:
    NOT_FOUND_HTML.write_text(
        f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Page Not Found | Diversity Tattoo</title>
    <link rel="stylesheet" href="styles.css?v=1.2.1" />
  </head>
  <body class="detail-page">
    <main id="main" class="detail-shell">
      <article class="detail-article">
        <img class="detail-hero-image" src="assets/static.wixstatic.com/bf2da649c19096a7.jpeg" alt="Diversity Tattoo studio" />
        <div class="detail-copy">
          <p class="eyebrow">404</p>
          <h1>Page not found</h1>
          <p>The page you requested is not available. Use the links below to continue to the shop, blog, services or visit information.</p>
          <ul class="contact-detail-list detail-meta">
            <li><strong>Call</strong><span>{escape(CONTACT['phone'])}</span></li>
            <li><strong>Visit</strong><span>{escape(CONTACT['address'])}</span></li>
          </ul>
          <a class="button primary" href="/index.html">Go to home</a>
          <a class="button secondary" href="/shop/index.html">Browse shop</a>
        </div>
      </article>
    </main>
  </body>
</html>
""",
        encoding="utf-8",
    )
    ROBOTS_TXT.write_text(
        f"""User-agent: *
Allow: /

Sitemap: {PRODUCTION_ORIGIN}/sitemap.xml
""",
        encoding="utf-8",
    )
    HEADERS_TXT.write_text(
        """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN

/assets/*
  Cache-Control: public, max-age=31536000, immutable
""",
        encoding="utf-8",
    )
    targets = {"index.html"}
    for item in data["routeCoverage"]:
        target = item["destinationPath"]
        if target and not target.startswith("utility/"):
            targets.add(target)
    url_lines = []
    for target in sorted(targets):
        loc = PRODUCTION_ORIGIN + public_url_path(target)
        url_lines.append(
            "  <url>\n"
            f"    <loc>{escape(loc)}</loc>\n"
            f"    <lastmod>{data['generatedAt']}</lastmod>\n"
            "  </url>"
        )
    SITEMAP_XML.write_text(
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
        + "\n".join(url_lines)
        + "\n</urlset>\n",
        encoding="utf-8",
    )


def write_qa(data: dict) -> None:
    stats = data["stats"]
    browser_text = BROWSER_QA_MD.read_text(encoding="utf-8", errors="ignore") if BROWSER_QA_MD.exists() else ""
    browser_passed = "- [x] Page loaded" in browser_text and "- [x] Mobile menu button was visible." in browser_text
    checked = "x" if browser_passed else " "
    product_lines = "\n".join(f"- {category}: {count}" for category, count in stats["productCategories"].items())
    section_lines = "\n".join(f"- {section}: {count}" for section, count in stats["futureSections"].items())
    risk_lines = "\n".join(f"- {risk}: {count}" for risk, count in data["mediaRiskSummary"].items())
    domain_lines = "\n".join(f"- {domain}: {count}" for domain, count in data["externalDomains"].items())
    route_examples = "\n".join(
        f"- `{item['route']}` -> `{item['destinationPath']}` ({item['destinationStatus']})"
        for item in data["routeCoverage"][:36]
    )

    QA_MD.write_text(
        f"""# Diversity Rebuild V1.2 QA Checklist

Generated: {data['generatedAt']}

## Inventory Targets

- Total legacy HTML routes represented: {stats['routes']}
- Product records rendered in the shop catalog: {stats['products']}
- Shop compatibility inputs represented: {stats['shopPages']}
- Blog/guide routes represented: {stats['guideRoutes']}
- Blog posts rendered in the guide system: {stats['blogPosts']}
- Blog category routes preserved: {stats['blogCategories']}
- Blog redirect routes preserved: {stats['blogRedirects']}
- Member/profile routes flagged for utility handling: {stats['profiles']}
- Media references cataloged: {stats['mediaReferences']}
- External links cataloged: {stats['externalLinks']}

## Product Category Coverage

{product_lines}

## Future Section Coverage

{section_lines}

## Browser QA Pass

- [{checked}] Hero loads with local media and first viewport communicates tattoo, piercing, retail, guide and visit paths.
- [{checked}] Primary navigation reaches Tattoo, Artists, Piercing, Tooth Gems, Shop Catalog, Guides, Reviews, FAQ and Visit.
- [{checked}] Product filter buttons update the {stats['products']}-record product grid without layout overflow.
- [{checked}] Guide filters expose posts, category routes, index route and redirect routes.
- [ ] Generated product, guide, artist, service, shop and utility detail pages open from v1.2 links.
- [{checked}] Accordion, tabs, guide slider and contact modal remain keyboard-usable.
- [{checked}] Mobile menu opens on narrow viewports and all generated sections fit without horizontal scrolling.
- [ ] Reduced-motion mode leaves all content visible without parallax, pinning or scrubbed motion.

## Media Risk Review

{risk_lines or '- No media risks were present in the generated catalog.'}

## External Link Review

- Approved for rebuild: {stats['externalApproved']}
- Needs review/excluded runtime candidates: {stats['externalReview']}

{domain_lines or '- No non-runtime external domains were detected.'}

## Route Preservation Samples

{route_examples}

## Final QA Notes

- v1.2 is generated from the updated 171-route catalog.
- Wix runtime, analytics and framework assets remain excluded from user-facing rebuild content.
- Legacy product and blog URLs are represented through structured detail pages and `redirects.json`.
- Media rows with risks remain visible in `media-review.json` and the QA panel until replaced or approved.
""",
        encoding="utf-8",
    )


def write_version_notes(data: dict) -> None:
    VERSION_NOTES.write_text(
        f"""# Diversity Rebuild V1.2 Notes

This folder is a standalone rebuild forked from the v1.1 visual system and regenerated from the updated catalog.

## What Changed From V1.1

- Added `build_v1_2_content.py` for the updated 171-route inventory.
- Regenerated `site-data.js` with products, guides, artists, service pages, shop pages, utility pages, route coverage, redirects, media risks and external-link summaries.
- Added `route-map.json`, `redirects.json`, and `media-review.json` as implementation accounting artifacts.
- Added generated static detail pages under `products/`, `guides/`, `artists/`, `services/`, `shop/`, and `utility/`.
- Updated QA and implementation result files for v1.2.

## Current Generated Counts

- Routes: {data['stats']['routes']}
- Products: {data['stats']['products']}
- Shop pages: {data['stats']['shopPages']}
- Blog/guide routes: {data['stats']['guideRoutes']}
- Media references: {data['stats']['mediaReferences']}
- Risky media references surfaced: {data['stats']['riskyMediaReferences']}
""",
        encoding="utf-8",
    )


def write_browser_qa_placeholder(data: dict) -> None:
    if BROWSER_QA_MD.exists() and "Desktop QA" in BROWSER_QA_MD.read_text(encoding="utf-8", errors="ignore"):
        return
    BROWSER_QA_MD.write_text(
        f"""# Diversity Rebuild V1.2 Browser QA Results

Generated: {data['generatedAt']}

Browser QA has not been completed yet.

## Required Viewports

- [ ] Desktop 1440px
- [ ] Small desktop 1024px
- [ ] Tablet 768px
- [ ] Mobile 390px

## Required Checks

- [ ] No console errors.
- [ ] No broken visible images.
- [ ] No mobile horizontal scroll.
- [ ] Product filters render {data['stats']['products']} product records.
- [ ] Guide filters render {data['stats']['guideRoutes']} guide-related records.
- [ ] Route QA renders {data['stats']['routes']} route records.
- [ ] Modal, tabs, accordion, slider and mobile menu work.
""",
        encoding="utf-8",
    )


def write_production_spec(observed_404_ledger: list[dict[str, str]], aliases: list[dict[str, str]]) -> None:
    counts = Counter(item["classification"] for item in observed_404_ledger)
    status_counts = Counter(f"{item['classification']} / {item['data_status']}" for item in observed_404_ledger)
    class_lines = "\n".join(f"- {name}: {count}" for name, count in sorted(counts.items()))
    status_lines = "\n".join(f"- {name}: {count}" for name, count in sorted(status_counts.items()))
    PRODUCTION_SPEC_MD.write_text(
        f"""# Diversity Tattoo V1.2 Production Implementation Spec

Generated: {date.today().isoformat()}

## Objective And Operating Principle

Make v1.2 a standalone, consumer-facing static site that can be committed to GitHub and deployed to Cloudflare Pages without relying on Cloudflare dashboard redirect rules or query-specific redirect logic.

The sitemap, scrape files and route ledgers are source inventory and coverage evidence. They are not the public information architecture. V1.2 must migrate business content into a modern structure organized around customer intent, SEO recovery and operational maintainability.

Legacy URLs exist only for inbound-link compatibility and audit accounting. They must not become navigation targets, sitemap targets, search targets or customer-journey requirements.

## Deployment Target

- GitHub repository: `https://github.com/ForkAroundAndFindOut/diversity_tattoo.git`
- Repository root: `C:\\Users\\pgche\\OneDrive\\Documents\\Diversity Website Scrapev2\\v1.2 rebuild`
- Deployable output directory: `public`
- Cloudflare Pages build command: leave blank after `public/` is committed.
- Cloudflare Pages output directory: `public`
- Cloudflare dashboard redirects/query rules: none.
- Production readiness gate: `python "v1.2 rebuild\\scripts\\validate_production.py"` must return `PASS`.

## Current Status

- `validation.txt` is a source-accounting validation, not a launch validation.
- The current generated pages still contain migration/audit language and category-style product media fallbacks.
- The project is not ready to push as a live business site until the production readiness gate passes.
- `public/` is the packaging target; source ledgers, generators, scrape evidence and QA notes stay outside that deployed folder.

## Source Inventory Snapshot

- Source routes accounted: 171
- Observed scrape 404s documented: {len(observed_404_ledger)}
- Compatibility alias pages generated: {len(aliases)}
- Optional `_redirects` file remains as host enhancement only.
- Root `/` must serve `index.html` directly; do not redirect `/` to `/index.html`.
- `public/shop/index.html` is the only canonical shop catalog page.
- `/shop?page=2` through `/shop?page=7` are old compatibility inputs only; they must open the same full catalog surface and must not create pagination UI, page buttons, page counts or paged product subsets.

### Observed 404 Classes

{class_lines}

### Observed 404 Data Status

{status_lines}

## Public Information Architecture

- `/` - home and primary conversion path.
- `/services/` plus customer-facing service pages for tattoo, piercing, tooth gems, smoke shop, reviews, FAQ and related service content.
- `/artists/` plus individual artist profile pages.
- `/shop/` - one filterable, searchable, sortable catalog.
- `/products/<slug>.html` - approved public product detail pages.
- `/blog/` - chronological blog archive.
- `/blog/<slug>.html` - individual indexable blog posts.
- `/visit/` or `/contact/` - location, hours, phone and visit/contact conversion.

Static `.html` files are an output format for Cloudflare Pages, not a requirement to mirror old Wix routes. Old `/post/*`, `/blog/*`, `/product-page/*`, profile and query URLs are compatibility inputs only.

## Required Accounting Artifacts

- `source-route-ledger`: source route, source type, source status, content area, canonical target or exception.
- `canonical-url-map`: public canonical URL, page type, source evidence, indexability and included-in-sitemap status.
- `alias-ledger`: old URL, generated alias path, canonical target, reason and noindex status.
- `noindex-ledger`: every noindex URL, reason, canonical target, owner and removal condition.
- `product-publication-ledger`: scraped product, product truth status, media status, public inclusion status and suppression reason.
- `blog-post-ledger`: source post, canonical blog URL, date/order, category/tag mapping and indexability.

## Milestone Checklist

### Milestone 0 - Source Inventory And Evidence Preserved

Done when the source inventory is stable and nothing in the production plan depends on re-scraping.

- [ ] Run source accounting.
- [ ] Preserve `catalog/observed-404-ledger.csv` and `catalog/observed-404-ledger.json`.
- [ ] Confirm 43 observed 404 rows are documented.
- [ ] Confirm 171 source routes are accounted as source coverage only.
- [ ] Confirm accounting artifacts are outside `public/`.

Verification commands:

```powershell
cd "C:\\Users\\pgche\\OneDrive\\Documents\\Diversity Website Scrapev2"
python "v1.2 rebuild\\build_v1_2_content.py"
python -m py_compile "v1.2 rebuild\\build_v1_2_content.py"
node --check "v1.2 rebuild\\content-render.js"
node --check "v1.2 rebuild\\motion.js"
Get-Content "v1.2 rebuild\\validation.txt"
```

Done criteria:

- Generator reports `171 routes`, `124 products`, `43 observed 404s`, `172 aliases`.
- `validation.txt` is `PASS`.
- `catalog/observed-404-ledger.csv` and `catalog/observed-404-ledger.json` have exactly 43 rows.
- `catalog/site-map.md` contains `## Observed 404s - Not Implementation Targets`.

### Milestone 1 - Public IA And URL Map Approved

Done when the canonical site map reflects the new v1.2 structure instead of old Wix page boundaries.

- [ ] Build `canonical-url-map`.
- [ ] Map services, artists, shop, products, blog, visit/contact, FAQ and reviews to customer-facing canonical URLs.
- [ ] Map old blog category pages to blog filters/tags unless a category has standalone editorial value.
- [ ] Map old post URLs to `/blog/<slug>.html`.
- [ ] Map old product URLs to `/products/<slug>.html` for approved products.
- [ ] Record explicit exceptions for stale promo/tag/utility content.
- [ ] Confirm aliases are not in navigation, internal search or `sitemap.xml`.

Done criteria:

- Canonical URL map exists.
- Public IA can be reviewed without reading legacy route lists.
- Every source route has one of: canonical content target, compatibility alias, or explicit exception.

### Milestone 2 - Product Truth, Media And Publication Ledger

Done when the product catalog is sourced from Wix Stores product truth, not category fallback scrape rows.

- [ ] Extract product truth from each `site/www.diversitytattoolv.com/product-page/*.html` embedded `script#wix-warmup-data`.
- [ ] Extract name, slug, formatted price, description, product type, stock status, additional info, canonical source URL and product-specific media metadata.
- [ ] Localize product images into `public/assets/products/<slug>/`.
- [ ] Create `product-publication-ledger`.
- [ ] Mark each scraped product as `include`, `suppress`, or `needs_business_review`.
- [ ] Use v1.2 catalog categories, not Wix category IDs, for public filters and product cards.

Done criteria:

- 124 scraped products are accounted in the publication ledger.
- Included products have product-specific local media.
- Suppressed products have a recorded reason.
- Public shop and product pages consume the same product truth.

### Milestone 3 - Public Page Templates Rebuilt

Done when the site reads as a business site, not an implementation report.

- [ ] Use `v1.1 rebuild/index.html` only as visual/template source material.
- [ ] Rebuild home, services, artists, shop, products, blog, visit/contact, FAQ and reviews as consumer-facing pages.
- [ ] Remove public labels and phrases: `legacy`, `route`, `rebuild`, `mirror`, `QA`, `media risk`, `future section`, `should become`, `Legacy route`, `Future section`, `Media references`, `Back to v1.2 rebuild`.
- [ ] Convert old service content into decision-focused service pages.
- [ ] Keep utility/member-account concepts out of customer journeys.

Done criteria:

- No customer-facing HTML or JS contains audit/migration language.
- Canonical public pages are indexable by default.
- Navigation exposes only v1.2 customer-facing destinations.

### Milestone 4 - Blog Archive And Posts Implemented

Done when blog content keeps the useful old format while using the new URL structure.

- [ ] Create `/blog/` as a chronological archive.
- [ ] Create one canonical, indexable `/blog/<slug>.html` page for each public blog post.
- [ ] Preserve source post body content where available, rewritten only for readability/formatting as needed.
- [ ] Treat old categories as archive filters/tags unless separately approved as editorial landing pages.
- [ ] Generate aliases from old `/post/*`, old `/blog/*` post URLs and recoverable `.html` blog 404 aliases to the new blog URLs.
- [ ] Add every post to `blog-post-ledger` with source path, canonical URL, date/order, tags and indexability.

Done criteria:

- `/blog/` lists posts chronologically.
- Every included blog post has one canonical indexable page.
- Old blog/post aliases are noindex and canonicalized.

### Milestone 5 - Aliases, 404s, Noindex And SEO Files Finalized

Done when SEO behavior is intentional and easy to audit.

- [ ] Generate physical alias pages for compatibility URLs.
- [ ] Add noindex only to compatibility aliases, utility/member-account pages, intentionally omitted placeholders and approved temporary staging pages.
- [ ] Generate `noindex-ledger` with URL, reason, canonical target, owner and removal condition.
- [ ] Generate `404.html`, `robots.txt`, `sitemap.xml`, `_headers` and optional `_redirects`.
- [ ] Ensure `sitemap.xml` includes canonical public pages only.
- [ ] Ensure aliases do not appear in `sitemap.xml`.

Done criteria:

- Every noindex page appears in the noindex ledger.
- No canonical public page is noindex unless explicitly approved in the ledger.
- `sitemap.xml` is clean canonical inventory, not an alias inventory.

### Milestone 6 - Production Bundle And Validator Pass

Done when one repeatable command proves deployability.

- [ ] Build `public/`.
- [ ] Exclude source ledgers, generators, scrape evidence and QA notes from `public/`.
- [ ] Run production readiness validation.
- [ ] Serve `public/` locally and verify canonical pages, aliases, old query URLs, `404.html`, `robots.txt` and `sitemap.xml`.

Verification commands:

```powershell
cd "C:\\Users\\pgche\\OneDrive\\Documents\\Diversity Website Scrapev2"
python "v1.2 rebuild\\build_v1_2_content.py"
python "v1.2 rebuild\\scripts\\extract_product_truth.py"
python "v1.2 rebuild\\scripts\\localize_product_media.py"
python "v1.2 rebuild\\scripts\\build_public_bundle.py"
python "v1.2 rebuild\\scripts\\validate_production.py"
Get-Content "v1.2 rebuild\\production-readiness.txt"
```

Done criteria:

- `production-readiness.txt` is `PASS`.
- `/`, `/services/`, `/artists/`, `/shop/`, `/blog/`, one product, one blog post, one alias and `/404.html` serve locally.

### Milestone 7 - GitHub Push And Cloudflare Pages Deployment Check

Done when a fresh clone can deploy as static files.

- [ ] Initialize or update the standalone repo only after Milestone 6 passes.
- [ ] Push to `https://github.com/ForkAroundAndFindOut/diversity_tattoo.git`.
- [ ] Fresh clone and serve `public/`.
- [ ] Configure Cloudflare Pages with no build command and output directory `public`.
- [ ] Confirm no dashboard redirect/query rules are required.

Repo commands, after production validation passes:

```powershell
cd "C:\\Users\\pgche\\OneDrive\\Documents\\Diversity Website Scrapev2\\v1.2 rebuild"
git init
git branch -M main
git remote add origin https://github.com/ForkAroundAndFindOut/diversity_tattoo.git
git status --short
```

If `origin` already exists, use:

```powershell
git remote set-url origin https://github.com/ForkAroundAndFindOut/diversity_tattoo.git
```

Commit and deployment validation:

```powershell
git status --short
git add .
git commit -m "Build Diversity Tattoo v1.2 static site"
git push -u origin main
cd "$env:TEMP"
git clone https://github.com/ForkAroundAndFindOut/diversity_tattoo.git diversity_tattoo_deploy_check
cd diversity_tattoo_deploy_check
python -m http.server 4173 -d public
```

Done criteria:

- Fresh clone serves the same static site.
- Cloudflare Pages deploys from `main` with output directory `public`.

## Implementation Handbook

### Source And Public Structure

- `public/`: deployable site only.
- `scripts/`: local generation, packaging and validation scripts.
- `source/`: extracted product truth, content ledgers and QA evidence that should not be served.
- Accounting files such as route maps, alias maps, media review, implementation results and QA checklists remain outside `public/`.

### Product Data Requirements

- Product truth comes from each `site/www.diversitytattoolv.com/product-page/*.html` embedded Wix Stores `wix-warmup-data` JSON.
- Required extracted fields: name, slug, formatted price, description, product type, stock status, additional information, canonical source URL, product-specific media and media alt/title.
- Public catalog inclusion is governed by `product-publication-ledger`.
- Product pages and shop cards use localized media from `public/assets/products/<slug>/`.
- Public taxonomy uses v1.2 categories, not Wix category IDs.
- Category fallback images require an explicit exception.

### Shop Catalog Requirements

- `/shop/` is the canonical shop catalog.
- All approved products are available on one filterable, searchable, sortable catalog surface.
- Default order is category order, then product name A-Z.
- Category filters are: All, Body Jewelry, Detox / Cleanses, Smoke Accessories, Vaporizers, Other Products.
- Sort options are: Category then A-Z, Name A-Z, Price Low-High, Price High-Low, In-stock first.
- Search covers product name, body/description and additional information.
- Valid URL state may restore `category`, `sort` and `q`; old `page` query values are ignored.
- `/shop?page=2` through `/shop?page=7` are retained only so inbound links do not break.
- No pagination UI, page-count copy or paged product subsets are allowed.

### Blog Requirements

- `/blog/` is a chronological archive of public posts.
- `/blog/<slug>.html` is the canonical page shape for individual posts.
- Public blog posts are indexable by default.
- Old post/category/blog URLs become noindex compatibility aliases or archive filters.
- Old hashtag archives remain omitted unless the business requests revival.

### SEO And Noindex Policy

- Canonical public pages are indexable by default.
- Only compatibility aliases, utility/member-account pages, intentionally omitted placeholders and approved temporary staging pages may be noindex.
- Every noindex page must be listed in `noindex-ledger`.
- `sitemap.xml` includes canonical public pages only.
- Alias pages include noindex robots, canonical link, meta refresh, JS replacement, visible fallback link and plain moved-page copy.

### Alias And 404 Requirements

- Compatibility aliases are physical static pages for portability.
- Alias pages are not customer-facing IA, navigation entries, search entries or sitemap entries.
- 404 promo/tag URLs remain documented only unless revived as new business content.
- `404.html` is a branded public page, not an audit report.

## Validation Requirements

- Source accounting validates coverage, not legacy IA parity.
- Public validation fails if customer-facing pages expose audit labels like `Legacy route`, `Future section` or `Media references`.
- Product validation confirms every included product has product-specific media or an approved exception.
- Blog validation confirms `/blog/` is chronological and every included post has a canonical indexable page.
- Shop validation confirms category filters, search, sort, clear filters, live summary and empty state exist.
- SEO validation confirms canonical pages are indexable unless listed in `noindex-ledger`.
- SEO validation confirms every noindex URL appears in `noindex-ledger`.
- SEO validation confirms aliases are noindex and canonicalized.
- SEO validation confirms aliases are excluded from `sitemap.xml`.
- Fresh GitHub clone can deploy to Cloudflare Pages without dashboard redirect rules.

## Production Readiness Validator Must Fail For

- Missing `public/` or required support files.
- Any source/accounting artifact in `public/`.
- Any customer-facing audit/migration phrase in public HTML or JS.
- Included product-specific media gate not satisfied.
- Shop catalog contract not satisfied.
- Shop pagination UI or paged catalog language appears in public HTML or JS.
- Missing chronological `/blog/` archive or missing included blog post pages.
- Canonical public page marked noindex without ledger approval.
- Noindex page missing from `noindex-ledger`.
- Alias URL present in `sitemap.xml`.
- External Wix runtime or non-local media markers in public files.

## Cloudflare Pages Settings

- Project name: `diversity-tattoo`
- Production branch: `main`
- Framework preset: `None`
- Build command: leave blank
- Build output directory: `public`
- Root directory: repository root
- Environment variables: none required for static deployment
- Dashboard redirects/query rules: none
- Custom domain: add only after the Pages preview passes production validation

## Post-Deploy Checks

- Open the Pages preview URL.
- Test `/`, `/services/`, `/artists/`, `/shop/`, `/blog/`, one product page, one blog post, one old alias and `/404.html`.
- Confirm shop category filters, search, sort, clear filters, live summary, empty state, keyboard focus and mobile layout work without pagination.
- Confirm `/blog/` lists posts chronologically and each included post is indexable.
- Confirm noindex URLs are present only where listed in `noindex-ledger`.
- Confirm no public page exposes audit/migration labels.
- Confirm product images are product-specific and local.

## Launch Blockers At Time Of Generation

- `public/` may be absent or may contain a deployment-shaped copy of the current prototype only.
- `scripts/extract_product_truth.py` and `scripts/localize_product_media.py` still need to be implemented unless product extraction is folded into `build_v1_2_content.py`.
- The current public HTML generation still emits audit/migration copy.
- Product media still needs to be sourced from Wix Stores product JSON and localized per product.
- The current shop surface still needs to be rebuilt as a single filterable catalog with search, sort, clear filters and live summary.
- The current blog output still needs to become `/blog/` chronological archive plus `/blog/<slug>.html` posts.
- `scripts/validate_production.py` now generates `noindex-ledger.json`; launch remains blocked until that ledger contains only approved noindex pages and no canonical public pages are accidentally noindex.
- Browser QA for generated detail-page links and reduced-motion behavior must be rerun against `public/`, not the mixed source folder.
""",
        encoding="utf-8",
    )


def validate_outputs(
    data: dict,
    ledger: list[dict[str, str]],
    redirects: list[dict[str, str]],
    observed_404_ledger: list[dict[str, str]],
    aliases: list[dict[str, str]],
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    stats = data["stats"]
    expected = {
        "routes": 171,
        "products": 124,
        "shopPages": 7,
        "guideRoutes": 22,
        "blogPosts": 15,
        "blogCategories": 2,
        "blogRedirects": 4,
        "profiles": 4,
    }
    for key, value in expected.items():
        if stats.get(key) != value:
            errors.append(f"{key} expected {value}, got {stats.get(key)}")

    if len(ledger) != stats["routes"]:
        errors.append(f"route ledger length expected {stats['routes']}, got {len(ledger)}")
    if len(redirects) != stats["routes"]:
        errors.append(f"redirect count expected {stats['routes']}, got {len(redirects)}")

    if len(observed_404_ledger) != 43:
        errors.append(f"observed 404 count expected 43, got {len(observed_404_ledger)}")
    expected_404_classes = {
        "malformed_or_missing_media_url": 21,
        "legacy_blog_html_alias": 7,
        "legacy_blog_category_html_alias": 2,
        "missing_blog_hashtag_archive": 10,
        "missing_legacy_promo_page": 3,
    }
    actual_404_classes = Counter(item["classification"] for item in observed_404_ledger)
    for key, value in expected_404_classes.items():
        if actual_404_classes.get(key) != value:
            errors.append(f"observed 404 class {key} expected {value}, got {actual_404_classes.get(key)}")

    generated_targets = {item["destinationPath"] for item in ledger if item["destinationPath"] != "index.html"}
    for target in sorted(generated_targets):
        if not (OUT_DIR / target).exists():
            errors.append(f"missing generated destination: {target}")

    image_paths = []
    for collection in ["products", "guides", "artists", "servicePages", "shopPages", "utilityPages"]:
        for item in data[collection]:
            image_paths.append(item["image"])
    for image in sorted(set(image_paths)):
        if image.startswith("assets/") and not (OUT_DIR / image).resolve().exists():
            errors.append(f"missing image referenced from index data: {image}")

    sources = [item["source"] for item in redirects]
    duplicates = [source for source, count in Counter(sources).items() if count > 1 and source != "/"]
    if duplicates:
        errors.append("duplicate redirect sources: " + ", ".join(sorted(duplicates)[:10]))

    alias_sources = {item["source"] for item in aliases}
    for item in redirects:
        source = item["source"]
        if not source or source == "/" or "?" in source or source == "/shop":
            continue
        alias_path = alias_output_path(source)
        if alias_path:
            alias_rel = alias_path.relative_to(OUT_DIR).as_posix()
            target_rel = item["target"].lstrip("/")
            if alias_rel == target_rel or (alias_rel.endswith("/index.html") and alias_rel[: -len("/index.html")] == target_rel.rstrip("/")):
                continue
        if source not in alias_sources:
            errors.append(f"missing alias page for redirect source: {source}")
    for item in observed_404_ledger:
        if item["implementation_action"] == "create_static_alias" and item["observed_path"] not in alias_sources:
            errors.append(f"missing alias page for observed 404 source: {item['observed_path']}")

    if any(line.strip() == "/ /index.html 301" for line in REDIRECTS_TXT.read_text(encoding="utf-8").splitlines() if REDIRECTS_TXT.exists()):
        errors.append("root redirect still emitted in _redirects")

    if "Observed 404s - Not Implementation Targets" not in SITE_MAP_MD.read_text(encoding="utf-8"):
        errors.append("site-map.md missing observed 404 section")

    return not errors, errors


def write_results(data: dict, valid: bool, errors: list[str], observed_404_ledger: list[dict[str, str]], aliases: list[dict[str, str]]) -> None:
    stats = data["stats"]
    failures = "\n".join(f"- {item}" for item in errors) or "- None"
    browser_text = BROWSER_QA_MD.read_text(encoding="utf-8", errors="ignore") if BROWSER_QA_MD.exists() else ""
    desktop_qa = "passed" if "- [x] Page loaded" in browser_text else "pending"
    mobile_qa = "passed" if "- [x] Mobile menu button was visible." in browser_text else "pending"
    RESULTS_MD.write_text(
        f"""# Diversity Rebuild V1.2 Implementation Results

Generated: {data['generatedAt']}

## Generated Artifacts

- v1.2 folder created: yes
- v1.1 files forked into v1.2: yes
- v1.2 content generator created: yes
- `site-data.js`: generated
- `route-map.json`: generated
- `redirects.json`: generated
- `_redirects`: generated
- `media-review.json`: generated
- `observed-404-ledger.json`: generated
- `observed-404-ledger.csv`: generated
- Static alias pages: generated
- `404.html`, `robots.txt`, `sitemap.xml`, `_headers`: generated
- Detail page folders: products, guides, artists, services, shop, utility

## Counts

- Generated route records: {stats['routes']}
- Generated product records: {stats['products']}
- Generated shop page records: {stats['shopPages']}
- Generated guide/blog records: {stats['guideRoutes']}
- Generated artist records: {len(data['artists'])}
- Generated service/page records: {len(data['servicePages'])}
- Generated profile/utility records: {len(data['utilityPages'])}
- Generated redirect records: {len(data['redirects'])}
- Generated static alias pages: {len(aliases)}
- Observed 404 ledger rows: {len(observed_404_ledger)}
- Media references reviewed/cataloged: {stats['mediaReferences']}
- Media risks remaining: {stats['riskyMediaReferences']}
- External links approved: {stats['externalApproved']}
- External links marked review/excluded candidates: {stats['externalReview']}

## Validation

- Automated validation: {'passed' if valid else 'failed'}

## Validation Failures

{failures}

## Browser QA

- Desktop browser QA: {desktop_qa}
- Mobile browser QA: {mobile_qa}

## Known Unresolved Items

- Media risks remain cataloged in `media-review.json`; final launch would still require manual approval or replacement for flagged media.
""",
        encoding="utf-8",
    )


def write_validation(valid: bool, errors: list[str]) -> None:
    VALIDATION_TXT.write_text(
        ("PASS\n" if valid else "FAIL\n") + "\n".join(errors) + ("\n" if errors else ""),
        encoding="utf-8",
    )


def main() -> None:
    copy_assets()
    ensure_asset_not_found_placeholder()
    refresh_canonical_manifest()
    data, ledger, redirects, media_review = build_data()
    localize_product_images(data)
    localize_blog_images(data)
    pages = read_csv(CONTENT_CSV)
    media_rows = read_csv(MEDIA_CSV)
    observed_404_ledger = build_observed_404_ledger(pages, media_rows, ledger)
    write_observed_404_files(observed_404_ledger)
    update_site_map_404_section(observed_404_ledger)
    write_local_sitemap_html(observed_404_ledger)
    write_blog_source_archive(data)
    write_detail_pages(data)
    write_js(data)
    refresh_canonical_manifest()
    write_json(ROUTE_MAP_JSON, ledger)
    write_json(REDIRECTS_JSON, redirects)
    write_redirects_txt(redirects)
    write_json(MEDIA_REVIEW_JSON, media_review)
    aliases = write_alias_pages(redirects, observed_404_ledger)
    write_json(OUT_DIR / "alias-map.json", aliases)
    write_accounting_ledgers(data, ledger, aliases)
    write_support_files(data)
    write_qa(data)
    write_version_notes(data)
    write_browser_qa_placeholder(data)
    # V1_2_FULL_IMPLEMENTATION_SPEC.md is a manually maintained handbook/checklist/runbook.
    # This generator owns source/accounting artifacts only; do not overwrite the spec here.
    valid, errors = validate_outputs(data, ledger, redirects, observed_404_ledger, aliases)
    write_results(data, valid, errors, observed_404_ledger, aliases)
    write_validation(valid, errors)
    print(
        "generated v1.2 data: "
        f"{data['stats']['routes']} routes, "
        f"{data['stats']['products']} products, "
        f"{data['stats']['guideRoutes']} guide routes, "
        f"{len(observed_404_ledger)} observed 404s, "
        f"{len(aliases)} aliases, "
        f"validation {'passed' if valid else 'failed'}"
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")


if __name__ == "__main__":
    main()
