from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
REPORT_PATH = ROOT / "production-readiness.txt"
NOINDEX_LEDGER_PATH = ROOT / "noindex-ledger.json"

REQUIRED_FILES = [
    "index.html",
    "404.html",
    "robots.txt",
    "sitemap.xml",
    "_headers",
    "_redirects",
    "styles.css",
]

FORBIDDEN_PUBLIC_ARTIFACTS = {
    "build_v1_2_content.py",
    "QA_CHECKLIST.md",
    "IMPLEMENTATION_RESULTS.md",
    "V1_2_FULL_IMPLEMENTATION_SPEC.md",
    "BROWSER_QA_RESULTS.md",
    "VERSION_1_2_NOTES.md",
    "WEBSITE_STRUCTURE_TEMPLATE.md",
    "route-map.json",
    "redirects.json",
    "alias-map.json",
    "media-review.json",
    "validation.txt",
    "PUBLIC_BUNDLE_MANIFEST.json",
    "source-route-ledger.json",
    "canonical-url-map.json",
    "alias-ledger.json",
    "noindex-ledger.json",
    "product-publication-ledger.json",
    "blog-post-ledger.json",
    "source-route-ledger.csv",
    "canonical-url-map.csv",
    "alias-ledger.csv",
    "noindex-ledger.csv",
    "product-publication-ledger.csv",
    "blog-post-ledger.csv",
}

FORBIDDEN_PUBLIC_DIRS = {"scripts", "__pycache__", "source", "catalog"}

FORBIDDEN_COPY_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bLegacy route\b",
        r"\bFuture section\b",
        r"\bMedia references\b",
        r"\bBack to v1\.2 rebuild\b",
        r"\brebuild\b",
        r"\boffline mirror\b",
        r"\bmirrored\s+(?:site|copy|scrape|version)\b",
        r"\bQA\b",
        r"\bmedia risk",
        r"\broute ledger\b",
        r"\bshould become\b",
    ]
]

NOINDEX_RE = re.compile(
    r"<meta\s+[^>]*name=[\"']robots[\"'][^>]*content=[\"'][^\"']*noindex",
    re.IGNORECASE,
)

CANONICAL_RE = re.compile(
    r"<link\s+[^>]*rel=[\"']canonical[\"'][^>]*href=[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)

ALIAS_HINT_RE = re.compile(
    r"(http-equiv=[\"']refresh[\"']|window\.location\.replace|Continue to)",
    re.IGNORECASE,
)

ALIAS_TOP_LEVEL_DIRS = {
    "artist",
    "blog",
    "bodypiercing",
    "charlie",
    "contact",
    "faq",
    "gallery",
    "home",
    "locations",
    "post",
    "price-list-1",
    "product-page",
    "profile",
    "reviews",
    "smoke-shop",
    "tank",
    "toothgems",
}

PUBLIC_TOP_LEVEL_DIRS = {
    "artists",
    "blog",
    "contact",
    "products",
    "services",
    "shop",
    "visit",
}

FORBIDDEN_RUNTIME_PATTERNS = [
    "https://static.wixstatic.com",
    "static.parastorage.com",
    "viewer-apps.parastorage.com",
    "wix-warmup-data",
    "mhtml:",
    "cid:",
]

SHOP_REQUIRED_MARKERS = {
    "category filter bar": ['id="product-category-filter-list"', "id='product-category-filter-list'", "#product-category-filter-list"],
    "category filter buttons": ["data-product-filter"],
    "filter button pressed state": ["aria-pressed"],
    "search input": ['id="product-search"', "id='product-search'", "#product-search"],
    "sort select": ['id="product-sort"', "id='product-sort'", "#product-sort"],
    "live result summary": ['id="product-filter-summary"', "id='product-filter-summary'", "#product-filter-summary"],
    "live region": ['aria-live="polite"', "aria-live='polite'"],
    "clear filters button": ['id="product-clear-filters"', "id='product-clear-filters'", "#product-clear-filters"],
    "product grid": ['id="product-grid"', "id='product-grid'", "#product-grid"],
}

SHOP_FORBIDDEN_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bshop pagination\b",
        r"\bcatalog pagination\b",
        r"\bpagination controls?\b",
        r"\bpaged catalog\b",
        r"\bpaged product subset",
        r"\bpage\s+\d+\s+of\s+\d+\b",
        r"\bnext page\b",
        r"\bprevious page\b",
        r"\bload more page\b",
        r"\bpage buttons?\b",
        r"\bpage-count\b",
        r"\bproduct-page-count\b",
        r"\bdata-shop-page\b",
        r"class=[\"'][^\"']*pagination",
    ]
]


def rel(path: Path) -> str:
    return path.relative_to(PUBLIC_DIR).as_posix()


def load_site_data() -> dict:
    site_data = PUBLIC_DIR / "site-data.js"
    if not site_data.exists():
        return {}
    text = site_data.read_text(encoding="utf-8", errors="ignore")
    prefix = "window.DIVERSITY_SITE_DATA = "
    if not text.startswith(prefix):
        return {}
    return json.loads(text[len(prefix) :].rstrip().rstrip(";"))


def product_image_exceptions() -> set[str]:
    path = ROOT / "product-media-exceptions.json"
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {str(item.get("slug", "")).strip() for item in data if isinstance(item, dict)}
    return set()


def product_slug(product: dict) -> str:
    direct = str(product.get("slug", "")).strip()
    if direct:
        return direct
    for key in ["destinationPath", "route", "legacyUrl", "recommendedLegacyUrl", "urlPart"]:
        value = str(product.get(key, "")).strip()
        if not value:
            continue
        path = urlparse(value).path if value.startswith(("http://", "https://")) else value
        name = Path(path.rstrip("/")).name
        if name:
            return Path(name).stem
    return ""


def source_slug(item: dict) -> str:
    for key in ["destinationPath", "route", "legacyUrl", "recommendedLegacyUrl", "urlPart"]:
        value = str(item.get(key, "")).strip()
        if not value:
            continue
        path = urlparse(value).path if value.startswith(("http://", "https://")) else value
        name = Path(path.rstrip("/")).name
        if name:
            return Path(name).stem
    return ""


def first_path_part(path: str) -> str:
    return path.split("/", 1)[0]


def extract_canonical(text: str) -> str:
    match = CANONICAL_RE.search(text)
    return match.group(1).strip() if match else ""


def classify_noindex(path: str, text: str, canonical: str) -> tuple[str, str, str]:
    first = first_path_part(path)
    is_alias_dir = first in ALIAS_TOP_LEVEL_DIRS
    is_alias_like = bool(ALIAS_HINT_RE.search(text))
    if is_alias_dir or is_alias_like:
        return (
            "compatibility_alias",
            "Legacy inbound-link compatibility alias; excluded from public navigation and sitemap.xml.",
            "Remove after inbound-link value is no longer needed or replace with a canonical public page.",
        )
    if first in {"profile", "utility"}:
        return (
            "utility_or_account",
            "Utility or member-account route; not a customer-facing SEO page.",
            "Remove if the utility page becomes a public conversion page.",
        )
    if "staging" in path:
        return (
            "temporary_staging",
            "Temporary staging page.",
            "Remove before production launch or convert to an indexable canonical page.",
        )
    if canonical and canonical.rstrip("/") != path.rstrip("/"):
        return (
            "canonicalized_duplicate",
            "Duplicate page canonicalized to the listed target.",
            "Remove when duplicate path is retired.",
        )
    return (
        "unknown_noindex",
        "Noindex found without an approved class.",
        "Assign an owner-approved noindex reason or make the page indexable.",
    )


def generate_noindex_ledger(file_texts: dict[Path, str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path, text in sorted(file_texts.items(), key=lambda item: rel(item[0])):
        if not NOINDEX_RE.search(text):
            continue
        relative_path = rel(path)
        canonical = extract_canonical(text)
        kind, reason, removal_condition = classify_noindex(relative_path, text, canonical)
        rows.append(
            {
                "path": relative_path,
                "url": "/" + relative_path.replace("index.html", "").rstrip("/") if relative_path != "index.html" else "/",
                "classification": kind,
                "reason": reason,
                "canonical_target": canonical,
                "owner": "SEO/content owner",
                "removal_condition": removal_condition,
            }
        )
    NOINDEX_LEDGER_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return rows


def validate() -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not PUBLIC_DIR.exists():
        return False, [f"missing public output directory: {PUBLIC_DIR}"], warnings

    for file_name in REQUIRED_FILES:
        if not (PUBLIC_DIR / file_name).exists():
            errors.append(f"missing required public file: {file_name}")

    for item in PUBLIC_DIR.rglob("*"):
        if item.name in FORBIDDEN_PUBLIC_ARTIFACTS:
            errors.append(f"source/accounting artifact leaked into public bundle: {rel(item)}")
        if item.is_dir() and item.name in FORBIDDEN_PUBLIC_DIRS:
            errors.append(f"source/accounting directory leaked into public bundle: {rel(item)}")

    product_pages = sorted((PUBLIC_DIR / "products").glob("*.html")) if (PUBLIC_DIR / "products").exists() else []
    if len(product_pages) != 124:
        errors.append(f"product page count expected 124, got {len(product_pages)}")

    site_data = load_site_data()
    products = site_data.get("products", []) if isinstance(site_data, dict) else []
    if len(products) != 124:
        errors.append(f"site-data product count expected 124, got {len(products)}")

    exceptions = product_image_exceptions()
    category_fallbacks = Counter()
    missing_product_images: list[str] = []
    missing_product_slugs = 0
    non_product_specific_images: list[str] = []
    for product in products:
        slug = product_slug(product)
        if not slug:
            missing_product_slugs += 1
        image = str(product.get("image", ""))
        if not image:
            missing_product_images.append(slug)
        expected_prefix = f"assets/products/{slug}/" if slug else ""
        if slug and expected_prefix not in image and slug not in exceptions:
            non_product_specific_images.append(slug)
        if "assets/static.wixstatic.com/" in image and slug not in exceptions:
            category_fallbacks[image] += 1
    if missing_product_slugs:
        errors.append(f"products missing derivable slugs: {missing_product_slugs}")
    if missing_product_images:
        errors.append(f"products missing image paths: {len(missing_product_images)}")
    if non_product_specific_images:
        errors.append(
            "product-specific media gate failed: "
            f"{len(non_product_specific_images)} products do not use assets/products/<slug>/ media"
        )
    if category_fallbacks:
        errors.append(
            "product-specific media gate failed: product image paths still look like shared/category fallback assets "
            f"({sum(category_fallbacks.values())} products)"
        )

    searchable_files = [
        path
        for pattern in ("*.html", "*.js")
        for path in PUBLIC_DIR.rglob(pattern)
        if path.is_file()
    ]
    file_texts = {path: path.read_text(encoding="utf-8", errors="ignore") for path in searchable_files}
    combined_public_text = "\n".join(file_texts.values())

    noindex_rows = generate_noindex_ledger({path: text for path, text in file_texts.items() if path.suffix == ".html"})
    unknown_noindex = [row["path"] for row in noindex_rows if row["classification"] == "unknown_noindex"]
    if unknown_noindex:
        errors.append(f"noindex pages missing approved ledger classification: {len(unknown_noindex)}")
        warnings.extend(f"{path} :: unapproved noindex" for path in unknown_noindex[:30])

    canonical_noindex = [
        row["path"]
        for row in noindex_rows
        if first_path_part(row["path"]) in PUBLIC_TOP_LEVEL_DIRS
        and row["classification"] not in {"compatibility_alias", "utility_or_account", "temporary_staging", "canonicalized_duplicate"}
    ]
    if canonical_noindex:
        errors.append(f"canonical public pages are noindex without an approved exception: {len(canonical_noindex)}")
        warnings.extend(f"{path} :: canonical public noindex" for path in canonical_noindex[:30])

    sitemap_path = PUBLIC_DIR / "sitemap.xml"
    sitemap_text = sitemap_path.read_text(encoding="utf-8", errors="ignore") if sitemap_path.exists() else ""
    sitemap_paths = {
        urlparse(match).path.lstrip("/") or "index.html"
        for match in re.findall(r"<loc>(.*?)</loc>", sitemap_text)
    }
    normalized_sitemap_paths = set()
    for path in sitemap_paths:
        normalized_sitemap_paths.add(path)
        if path.endswith("/"):
            normalized_sitemap_paths.add(path + "index.html")
        elif not Path(path).suffix:
            normalized_sitemap_paths.add(path.rstrip("/") + "/index.html")
    alias_sitemap_hits = []
    for row in noindex_rows:
        if row["classification"] != "compatibility_alias":
            continue
        path = row["path"].lstrip("/")
        url_path = row["url"].lstrip("/")
        candidates = {path, url_path}
        if url_path and not Path(url_path).suffix:
            candidates.add(url_path.rstrip("/") + "/index.html")
        if candidates & normalized_sitemap_paths:
            alias_sitemap_hits.append(row["path"])
    if alias_sitemap_hits:
        errors.append(f"compatibility aliases appear in sitemap.xml: {len(alias_sitemap_hits)}")
        warnings.extend(f"{path} :: alias listed in sitemap.xml" for path in alias_sitemap_hits[:30])

    blog_index = PUBLIC_DIR / "blog" / "index.html"
    if not blog_index.exists():
        errors.append("missing canonical blog archive: blog/index.html")
    elif NOINDEX_RE.search(blog_index.read_text(encoding="utf-8", errors="ignore")):
        errors.append("canonical blog archive is noindex: blog/index.html")

    guide_records = site_data.get("guides", []) if isinstance(site_data, dict) else []
    blog_posts = [item for item in guide_records if item.get("type") == "blog_post"]
    missing_blog_posts: list[str] = []
    for post in blog_posts:
        slug = source_slug(post)
        if slug and not (PUBLIC_DIR / "blog" / f"{slug}.html").exists():
            missing_blog_posts.append(slug)
    if missing_blog_posts:
        errors.append(f"canonical blog post pages missing from /blog/: {len(missing_blog_posts)}")
        warnings.extend(f"blog/{slug}.html :: missing canonical blog post" for slug in missing_blog_posts[:30])

    missing_shop_markers = [
        name for name, markers in SHOP_REQUIRED_MARKERS.items() if not any(marker in combined_public_text for marker in markers)
    ]
    if missing_shop_markers:
        errors.append("shop catalog contract missing required controls: " + ", ".join(missing_shop_markers))

    shop_pagination_hits: list[str] = []
    for path, text in file_texts.items():
        for pattern in SHOP_FORBIDDEN_PATTERNS:
            if pattern.search(text):
                shop_pagination_hits.append(f"{rel(path)} :: {pattern.pattern}")
                break
    if shop_pagination_hits:
        errors.append(f"shop pagination or paged catalog language found in {len(shop_pagination_hits)} public files")
        warnings.extend(shop_pagination_hits[:30])

    copy_hits: list[str] = []
    runtime_hits: list[str] = []
    for path, text in file_texts.items():
        for pattern in FORBIDDEN_COPY_PATTERNS:
            if pattern.search(text):
                copy_hits.append(f"{rel(path)} :: {pattern.pattern}")
                break
        for marker in FORBIDDEN_RUNTIME_PATTERNS:
            if marker in text:
                runtime_hits.append(f"{rel(path)} :: {marker}")
                break
    if copy_hits:
        errors.append(f"public migration/audit copy is still present in {len(copy_hits)} files")
        warnings.extend(copy_hits[:30])
    if runtime_hits:
        errors.append(f"public runtime dependencies or non-local media markers found in {len(runtime_hits)} files")
        warnings.extend(runtime_hits[:30])

    return not errors, errors, warnings


def write_report(valid: bool, errors: list[str], warnings: list[str]) -> None:
    lines = ["PASS" if valid else "FAIL", ""]
    if errors:
        lines.append("Errors")
        lines.extend(f"- {error}" for error in errors)
        lines.append("")
    if warnings:
        lines.append("Evidence Samples")
        lines.extend(f"- {warning}" for warning in warnings)
        lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    valid, errors, warnings = validate()
    write_report(valid, errors, warnings)
    print("production readiness:", "PASS" if valid else "FAIL")
    print(f"report: {REPORT_PATH}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
