# Diversity Tattoo V1.2 Production Implementation Spec

Maintained manually as the implementation handbook, milestone checklist and deployment runbook.

Generated ledgers and reports are separate evidence artifacts, including `route-map.json`, `alias-map.json`, `observed-404-ledger.json`, `observed-404-ledger.csv`, `media-review.json`, `noindex-ledger.json`, `validation.txt` and `production-readiness.txt`.

## Objective And Operating Principle

Make v1.2 a standalone, consumer-facing static site that can be committed to GitHub and deployed to Cloudflare Pages without relying on Cloudflare dashboard redirect rules or query-specific redirect logic.

The sitemap, scrape files and route ledgers are source inventory and coverage evidence. They are not the public information architecture. V1.2 must migrate business content into a modern structure organized around customer intent, SEO recovery and operational maintainability.

Legacy URLs exist only for inbound-link compatibility and audit accounting. They must not become navigation targets, sitemap targets, search targets or customer-journey requirements.

## Deployment Target

- GitHub repository: `https://github.com/ForkAroundAndFindOut/diversity_tattoo.git`
- Repository root: `C:\Users\pgche\OneDrive\Documents\Diversity Website Scrapev2\v1.2 rebuild`
- Deployable output directory: `public`
- Cloudflare Pages build command: leave blank after `public/` is committed.
- Cloudflare Pages output directory: `public`
- Cloudflare dashboard redirects/query rules: none.
- Production readiness gate: `python "v1.2 rebuild\scripts\validate_production.py"` must return `PASS`.

## Current Status

- `validation.txt` is a source-accounting validation, not a launch validation.
- The current generated pages still contain migration/audit language and category-style product media fallbacks.
- The project is not ready to push as a live business site until the production readiness gate passes.
- `public/` is the packaging target; source ledgers, generators, scrape evidence and QA notes stay outside that deployed folder.

## Source Inventory Snapshot

- Source routes accounted: 171
- Observed scrape 404s documented: 43
- Compatibility alias pages generated: 172
- Optional `_redirects` file remains as host enhancement only.
- Root `/` must serve `index.html` directly; do not redirect `/` to `/index.html`.
- `public/shop/index.html` is the only canonical shop catalog page.
- `/shop?page=2` through `/shop?page=7` are old compatibility inputs only; they must open the same full catalog surface and must not create pagination UI, page buttons, page counts or paged product subsets.

### Observed 404 Classes

- legacy_blog_category_html_alias: 2
- legacy_blog_html_alias: 7
- malformed_or_missing_media_url: 21
- missing_blog_hashtag_archive: 10
- missing_legacy_promo_page: 3

### Observed 404 Data Status

- legacy_blog_category_html_alias / canonical_content_available: 2
- legacy_blog_html_alias / canonical_content_available: 7
- malformed_or_missing_media_url / accounted_elsewhere: 12
- malformed_or_missing_media_url / missing_unmatched: 4
- malformed_or_missing_media_url / referenced_but_not_localized: 5
- missing_blog_hashtag_archive / not_in_sitemap_no_source_content: 10
- missing_legacy_promo_page / not_in_sitemap_no_source_content: 3

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
cd "C:\Users\pgche\OneDrive\Documents\Diversity Website Scrapev2"
python "v1.2 rebuild\build_v1_2_content.py"
python -m py_compile "v1.2 rebuild\build_v1_2_content.py"
node --check "v1.2 rebuild\content-render.js"
node --check "v1.2 rebuild\motion.js"
Get-Content "v1.2 rebuild\validation.txt"
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
- [ ] Convert the homepage-heavy page model into a sectioned site: homepage previews point to `/tattoo/`, `/artists/`, `/piercing/`, `/tooth-gems/`, `/smoke-shop/`, `/shop/`, `/blog/`, `/reviews/`, `/faq/`, and the homepage Visit section.
- [ ] Move full tattoo detail to `/tattoo/`, full piercing detail and pricing to `/piercing/`, tooth gems detail to `/tooth-gems/`, smoke shop retail browsing to `/smoke-shop/`, full catalog browsing to `/shop/`, full blog archive/filtering to `/blog/`, reviews to `/reviews/`, and FAQ to `/faq/`.
- [ ] Keep the homepage as a modern business showcase with highlighted cards, overview sections, latest 3 blog posts, a centered `See more` blog CTA, and concise CTAs into the dedicated section pages.
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
cd "C:\Users\pgche\OneDrive\Documents\Diversity Website Scrapev2"
python "v1.2 rebuild\build_v1_2_content.py"
python "v1.2 rebuild\scripts\extract_product_truth.py"
python "v1.2 rebuild\scripts\localize_product_media.py"
python "v1.2 rebuild\scripts\build_public_bundle.py"
python "v1.2 rebuild\scripts\validate_production.py"
Get-Content "v1.2 rebuild\production-readiness.txt"
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
cd "C:\Users\pgche\OneDrive\Documents\Diversity Website Scrapev2\v1.2 rebuild"
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
- `/piercing/` owns the pre-filtered Body Jewelry product view and should not show smoke shop categories.
- `/smoke-shop/` owns Detox / Cleanses, Vaporizers, Smoke Accessories and Other Products for now; it must not show Body Jewelry even if a jewelry category query parameter is manually added.
- `/tooth-gems/` should use source-backed imagery when available; if no tooth-gem-specific image is available, show the explicit `asset-not-found` placeholder and document the replacement need.
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
