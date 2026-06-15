# Diversity Page Reorg Implementation Spec

## Goal

Transform the current homepage-heavy Diversity Tattoo site into a sectioned business site. The homepage should become a polished landing and showcase page with concise pointers to deeper pages. The detailed content currently living on the homepage should move into canonical sub-pages where visitors can browse, compare, and act without scrolling through one long master page.

This reorg is not a full redesign from scratch. It is a migration of existing homepage sections and generated content into a clearer information architecture, while preserving the current static-site generator, product truth, blog parity, compatibility aliases, and staging-first publication flow.

## Branch And Worktree Plan

- [ ] Base the work on `origin/staging`, not `main`.
- [ ] Create a feature branch named `staging-page-reorg`.
- [ ] Note: `staging/page-reorg` was the original target name, but the repository already has a local `staging` branch, so Git cannot also create a slash-nested `staging/page-reorg` ref.
- [ ] Create the feature branch in a sibling worktree so homepage image and formatting work can continue separately on `staging`.
- [ ] Use this setup command:

```powershell
cd "C:\Users\pgche\OneDrive\Documents\Diversity Website Scrapev2\v1.2 rebuild"
git fetch origin
git worktree add "..\w" -b staging-page-reorg origin/staging
```

- [ ] Record the starting branch tips for `staging`, `origin/staging`, `main`, and `origin/main`.
- [ ] Keep `main` untouched during this work.
- [ ] Before final validation, merge or rebase the latest `origin/staging` into `staging-page-reorg`.
- [ ] Resolve conflicts in `staging-page-reorg`, especially any homepage image or formatting conflicts.
- [ ] Merge the finished branch back to `staging` only after validation passes.

## Homepage Migration Model

The homepage should stop being the place where every full section lives. It should become a business overview with focused cards, previews, and calls to action.

### Keep On Homepage

- [ ] Keep the hero, business positioning, primary call button, and core studio facts.
- [ ] Keep broad overview anchors:
  - [ ] `#tattoo`
  - [ ] `#artists`
  - [ ] `#piercing`
  - [ ] `#shop-catalog`
  - [ ] `#blog`
  - [ ] `#reviews`
  - [ ] `#faq`
  - [ ] `#visit`
- [ ] Keep a compact tattoo/services overview that points to `/tattoo/`.
- [ ] Keep a compact artists/team preview that points to `/artists/`.
- [ ] Keep a piercing overview card that points to `/piercing/`.
- [ ] Keep a tooth gems overview card that points to `/tooth-gems/`.
- [ ] Keep a smoke shop overview card that points to `/smoke-shop/`.
- [ ] Keep shop category tiles that point to `/shop/` or pre-filtered shop/category routes.
- [ ] Keep the latest 3 blog posts only.
- [ ] Keep reviews and FAQ teaser sections.
- [ ] Keep Visit/contact information on the homepage.
- [ ] Keep studio information for now, but reduce duplicate copy once the deeper pages carry the detail.

### Move Out Of Homepage

- [ ] Move full tattoo/service detail from the homepage to `/tattoo/`.
- [ ] Move full artist/team browsing from the homepage to `/artists/`.
- [ ] Move piercing details, jewelry guidance, and piercing service copy to `/piercing/`.
- [ ] Move the full piercing price table to `/piercing/#pricing`.
- [ ] Move tooth gems detail to `/tooth-gems/`.
- [ ] Move smoke shop, detox, vaporizers, smoke accessories, and other-product browsing to `/smoke-shop/`.
- [ ] Move the full product catalog to `/shop/`.
- [ ] Move the full blog archive and filters to `/blog/`.
- [ ] Move review detail to `/reviews/`.
- [ ] Move FAQ detail to `/faq/`.

## Canonical Page Contract

### `/tattoo/`

- [ ] Generate an indexable top-level tattoo page.
- [ ] Use tattoo service content from the existing source data.
- [ ] Include tattoo service overview, custom work, cover-up positioning, artist/gallery pointers, and visit/call CTAs.
- [ ] Do not duplicate the entire homepage service grid.
- [ ] Link back to artists, gallery/source-backed tattoo material, blog posts, and visit information where relevant.

### `/artists/`

- [ ] Keep `/artists/` as the canonical artist/team page.
- [ ] Use existing artist records from `site-data.js`.
- [ ] Keep individual artist profile links.
- [ ] Homepage should show a compact artist preview, not the full artist browsing experience.

### `/piercing/`

- [ ] Generate an indexable top-level piercing page.
- [ ] Move piercing service copy from the homepage and current service pages into this page.
- [ ] Move the full piercing price table here.
- [ ] Add a stable `#pricing` anchor for direct links from homepage CTAs.
- [ ] Add jewelry guidance and product browsing context.
- [ ] Show a pre-filtered product grid for Body Jewelry only.
- [ ] Do not show detox, vaporizers, smoke accessories, or other smoke-shop products on this page.
- [ ] Treat `/bodypiercing/` as a noindex compatibility alias to `/piercing/`.

### `/tooth-gems/`

- [ ] Generate an indexable top-level tooth gems page.
- [ ] Move tooth gems service detail from the homepage/current service content into this page.
- [ ] Use tooth-gem-specific/source-backed imagery if it can be localized from the source inventory.
- [ ] If tooth-gem-specific imagery is unavailable, use the explicit `asset-not-found` placeholder and record the issue instead of substituting unrelated product imagery.
- [ ] If source-backed tooth gem product records or assets exist, render a scoped product/visual section comparable to the jewelry page.
- [ ] If no source-backed tooth gem product records exist, keep the page as service-focused with CTA and related links.
- [ ] Treat `/toothgems/` as a noindex compatibility alias to `/tooth-gems/`.

### `/smoke-shop/`

- [ ] Generate an indexable top-level smoke shop page.
- [ ] Make this page own the current non-jewelry retail groups:
  - [ ] Detox / Cleanses
  - [ ] Vaporizers
  - [ ] Smoke Accessories
  - [ ] Other Products
- [ ] Do not show Body Jewelry on `/smoke-shop/`.
- [ ] Keep the current category labels for now.
- [ ] Structure the code so these labels can be renamed or reorganized later without changing the page architecture.
- [ ] Render a pre-filtered product grid for the owned categories, the same way `/piercing/` filters to Body Jewelry.
- [ ] Include smoke shop and detox service/source copy where available.
- [ ] Link to `/shop/` for the full catalog.

### `/shop/`

- [ ] Keep `/shop/` as the only full catalog page.
- [ ] Show all current products.
- [ ] Keep category tiles, category filters, search, sort, clear filters, live result summary, and product detail links.
- [ ] Preserve old shop query behavior such as `/shop/?page=2` opening the same full catalog surface.
- [ ] Do not reintroduce pagination UI or paged product subsets.

### `/blog/`

- [ ] Keep `/blog/` as the full blog archive.
- [ ] Preserve the 15-post blog parity established from the feed/source repair work.
- [ ] Keep archive filtering on the blog page.
- [ ] Homepage should render exactly the latest 3 blog posts.
- [ ] Add a centered `See more` button on the homepage linking to `/blog/`.
- [ ] Replace homepage copy such as `Open blog archive` with the shorter `See more` CTA.

### `/reviews/`

- [ ] Generate an indexable top-level reviews page.
- [ ] Move review/trust detail out of the homepage teaser.
- [ ] Keep homepage reviews as a concise trust pointer.
- [ ] Treat old `/reviews/` compatibility behavior as canonical if the generated route now owns that path.

### `/faq/`

- [ ] Generate an indexable top-level FAQ page.
- [ ] Move FAQ detail out of the homepage teaser.
- [ ] Keep homepage FAQ as a concise pointer.
- [ ] Treat old `/faq/` compatibility behavior as canonical if the generated route now owns that path.

### Visit

- [ ] Keep Visit on the homepage in this pass.
- [ ] Do not create `/visit/` unless the scope changes.
- [ ] Keep visit CTAs visible from every new top-level page.

## Generator And Data Tasks

- [ ] Add a section-page configuration in `build_v1_2_content.py`.
- [ ] Include route, title, eyebrow, source content, canonical path, hero image, CTA, homepage anchor, and product scope in the config.
- [ ] Generate top-level section pages from the config instead of hand-copying static HTML.
- [ ] Update `DETAIL_DIRS` and alias cleanup rules so canonical top-level pages do not get deleted as alias directories.
- [ ] Update `row_destination` so current service/source rows map to the new canonical section pages where appropriate.
- [ ] Update `canonical_url_map_rows` to include all new canonical section pages.
- [ ] Update sitemap generation so new canonical section pages are included.
- [ ] Update alias generation so legacy spellings remain noindex aliases.
- [ ] Update route/accounting ledgers so each old route has a canonical target, compatibility alias, or explicit exception.
- [ ] Preserve product-publication ledger behavior.
- [ ] Preserve blog-post ledger behavior.
- [ ] Preserve `asset-not-found` behavior for missing canonical assets.

## Shared Renderer Tasks

- [ ] Extend `content-render.js` to support scoped product grids.
- [ ] Allow a page or container to declare an allowed category scope.
- [ ] Keep `/shop/` as the all-products grid.
- [ ] Make `/piercing/` render Body Jewelry only.
- [ ] Make `/smoke-shop/` render Detox / Cleanses, Vaporizers, Smoke Accessories, and Other Products only.
- [ ] Make `/smoke-shop/` exclude Body Jewelry even if query parameters request it.
- [ ] Add optional homepage preview limits for blog cards and any compact product/artist previews.
- [ ] Keep search, sort, result counts, clear-filter behavior, and accessibility states working on scoped grids.
- [ ] Avoid unsupported scoped-page filters showing empty or misleading category controls.
- [ ] Keep URL query updates useful on `/shop/`; scoped pages may omit or constrain category query behavior.

## Homepage Tasks

- [ ] Replace the current full product catalog section with shop category tiles.
- [ ] Add tiles for Body Jewelry, Detox / Cleanses, Vaporizers, Smoke Accessories, and Other Products where appropriate.
- [ ] Make tiles point to relevant canonical pages or filtered shop views.
- [ ] Replace the full homepage blog archive/filter UI with latest 3 posts.
- [ ] Add centered `See more` button under the latest 3 posts.
- [ ] Remove the piercing price table from the homepage.
- [ ] Add a homepage CTA from piercing overview to `/piercing/#pricing`.
- [ ] Ensure every homepage overview section has a clear next step.
- [ ] Keep the page visually balanced after removing large sections.
- [ ] Avoid leaving orphaned anchors or buttons that still point to removed in-page content.

## Public Bundle And Validator Tasks

- [ ] Update `scripts/build_public_bundle.py` canonical directories to include the new top-level pages.
- [ ] Update `scripts/validate_production.py` public top-level directory rules.
- [ ] Update alias top-level directory rules where a path changes from alias to canonical.
- [ ] Ensure canonical pages are not noindex.
- [ ] Ensure compatibility aliases are noindex.
- [ ] Ensure aliases do not appear in `sitemap.xml`.
- [ ] Ensure `sitemap.xml` includes the new canonical pages.
- [ ] Ensure forbidden audit/rebuild copy does not appear in public HTML.
- [ ] Ensure product image manifest checks still pass.
- [ ] Ensure blog body and image quality checks still pass.

## Documentation Tasks

- [ ] Update `V1_2_FULL_IMPLEMENTATION_SPEC.md` with the approved top-level page architecture.
- [ ] Document the homepage migration model.
- [ ] Document the category ownership rules for `/piercing/`, `/smoke-shop/`, `/shop/`, and `/tooth-gems/`.
- [ ] Document that Smoke Shop owns Detox / Cleanses, Vaporizers, Smoke Accessories, and Other Products for now.
- [ ] Document that category labels may be renamed later without changing ownership in this pass.
- [ ] Document that Visit remains homepage-only for now.
- [ ] Document that `main` is not part of this publication pass.

## Merge Plan

- [ ] Fetch latest remote refs before final validation.
- [ ] Merge latest `origin/staging` into `staging-page-reorg`.
- [ ] Resolve conflicts, preserving separately completed homepage image/formatting improvements.
- [ ] Rerun generator and validation after conflict resolution.
- [ ] Merge `staging-page-reorg` back into `staging`.
- [ ] Push `staging`.
- [ ] Do not push or merge to `main` unless explicitly requested.

Suggested final merge commands:

```powershell
cd "C:\Users\pgche\OneDrive\Documents\Diversity Website Scrapev2\w"
git fetch origin
git switch staging-page-reorg
git merge origin/staging

python build_v1_2_content.py
node --check content-render.js
node --check motion.js
python scripts/build_public_bundle.py
python scripts/validate_production.py

cd "C:\Users\pgche\OneDrive\Documents\Diversity Website Scrapev2\v1.2 rebuild"
git switch staging
git pull --ff-only origin staging
git merge --no-ff staging-page-reorg
git push origin staging
```

## Validation Checklist

- [ ] Run the generator:

```powershell
python build_v1_2_content.py
```

- [ ] Check JavaScript syntax:

```powershell
node --check content-render.js
node --check motion.js
```

- [ ] Build the public bundle:

```powershell
python scripts/build_public_bundle.py
```

- [ ] Run production validation:

```powershell
python scripts/validate_production.py
```

- [ ] Confirm `production-readiness.txt` reports `PASS`.
- [ ] Serve `public/` locally.
- [ ] Check desktop layout for `/`.
- [ ] Check mobile layout for `/`.
- [ ] Check desktop and mobile layout for `/tattoo/`.
- [ ] Check desktop and mobile layout for `/artists/`.
- [ ] Check desktop and mobile layout for `/piercing/`.
- [ ] Check desktop and mobile layout for `/tooth-gems/`.
- [ ] Check desktop and mobile layout for `/smoke-shop/`.
- [ ] Check desktop and mobile layout for `/shop/`.
- [ ] Check desktop and mobile layout for `/blog/`.
- [ ] Check desktop and mobile layout for `/reviews/`.
- [ ] Check desktop and mobile layout for `/faq/`.
- [ ] Check desktop and mobile layout for one product detail page.
- [ ] Check desktop and mobile layout for one blog post page.
- [ ] Check `/bodypiercing/` alias behavior.
- [ ] Check `/toothgems/` alias behavior.
- [ ] Check one old `/post/*` alias.
- [ ] Confirm canonical pages are indexable.
- [ ] Confirm aliases are noindex.
- [ ] Confirm aliases are absent from `sitemap.xml`.
- [ ] Confirm no broken internal links from homepage CTAs.
- [ ] Confirm no broken images.
- [ ] Confirm no horizontal overflow on mobile.

## UI And Interaction QA

- [ ] Confirm the new section pages use the same modern visual language as the homepage: sticky header, strong hero treatment, polished service cards, consistent typography, consistent buttons, intentional spacing, and source-backed imagery.
- [ ] Confirm moved sections do not feel like raw detail pages; each top-level page should feel like a designed business landing page for that service/category.
- [ ] Confirm desktop layouts look balanced at common widths such as 1440px, 1280px, and 1024px.
- [ ] Confirm mobile layouts look balanced at common widths such as 390px, 375px, and 320px.
- [ ] Confirm tablet/narrow-desktop layouts do not create awkward two-column wrapping, clipped cards, or oversized empty gaps.
- [ ] Confirm cards, buttons, filters, search inputs, select menus, and links have visible hover/focus states.
- [ ] Confirm keyboard navigation can reach primary nav links, CTAs, product filters, search, sort, clear filters, and card links.
- [ ] Confirm mobile navigation opens, closes, fits on screen, and does not cover important content after a link is selected.
- [ ] Confirm animations and reveal effects still run smoothly after content is moved out of the homepage.
- [ ] Confirm scroll-triggered effects do not leave blank space, hidden content, or stale layout positions after dynamic product/blog rendering.
- [ ] Confirm product grid filtering works on `/shop/`, `/piercing/`, and `/smoke-shop/`.
- [ ] Confirm scoped product pages never show out-of-scope filter buttons or misleading result counts.
- [ ] Confirm `/piercing/` product cards are jewelry-only.
- [ ] Confirm `/smoke-shop/` product cards are Detox / Cleanses, Vaporizers, Smoke Accessories, or Other Products only.
- [ ] Confirm `/smoke-shop/` does not show Body Jewelry even if a jewelry category query parameter is manually added.
- [ ] Confirm homepage blog preview shows exactly 3 posts and the `See more` button is centered and links to `/blog/`.
- [ ] Confirm all page CTAs point to canonical destinations rather than old service aliases.
- [ ] Confirm image rendering quality is acceptable on desktop and mobile, with no stretched, blurry, unrelated, or badly cropped primary images.
- [ ] Confirm every missing tooth-gem-specific image uses the explicit `asset-not-found` placeholder and is documented for later asset replacement.
- [ ] Confirm no text overlaps images, buttons, cards, nav, filters, tables, or adjacent sections.
- [ ] Confirm no button or card label overflows its container at mobile widths.
- [ ] Confirm the piercing pricing table is readable on mobile and does not force horizontal page overflow.
- [ ] Confirm detail pages and top-level section pages visually match the homepage quality level, not the older generic generated detail-page style.
- [ ] Confirm Chrome and Edge pass local browser QA on Windows.
- [ ] Confirm Firefox if available locally.
- [ ] Record Safari as not natively testable in the local Windows environment unless a remote Safari, BrowserStack-style service, or separate macOS/iOS device is available.
- [ ] If Safari access is available, check layout, sticky header behavior, mobile nav, product filters, image rendering, and animation behavior in Safari before final staging merge.

## Optional Public Preview

- [ ] Serve `public/` locally.
- [ ] Start Cloudflare Quick Tunnel with `cloudflared`.
- [ ] Extract the `trycloudflare.com` URL from the `cloudflared` stderr log.
- [ ] Verify public HTTP 200 responses before reporting the URL.
- [ ] Spot-check `/`, `/piercing/`, `/smoke-shop/`, `/shop/`, and `/blog/` through the public URL.
- [ ] Keep local server and tunnel processes alive while the preview is needed.

## Done Looks Like

- [ ] Homepage reads as a landing page and business showcase, not the whole site compressed into one page.
- [ ] Every homepage section has a clear CTA to its dedicated page.
- [ ] Full tattoo details live on `/tattoo/`.
- [ ] Full artist/team browsing lives on `/artists/`.
- [ ] Piercing service detail, piercing prices, and Body Jewelry browsing live on `/piercing/`.
- [ ] `/piercing/` does not show smoke-shop product categories.
- [ ] Tooth gems content lives on `/tooth-gems/`.
- [ ] `/tooth-gems/` uses source-backed imagery when available and a documented placeholder when not available.
- [ ] `/smoke-shop/` owns Detox / Cleanses, Vaporizers, Smoke Accessories, and Other Products.
- [ ] `/smoke-shop/` shows no Body Jewelry.
- [ ] `/shop/` remains the only full catalog page.
- [ ] `/blog/` owns the full archive and filters.
- [ ] Homepage shows exactly 3 blog posts and a centered `See more` button.
- [ ] `/reviews/` is a canonical top-level reviews page.
- [ ] `/faq/` is a canonical top-level FAQ page.
- [ ] Visit remains on the homepage.
- [ ] New canonical pages are included in `sitemap.xml`.
- [ ] New canonical pages are not noindex.
- [ ] Legacy aliases still work.
- [ ] Legacy aliases are noindex.
- [ ] Legacy aliases are not in `sitemap.xml`.
- [ ] Production validation passes.
- [ ] Runtime QA passes on desktop and mobile.
- [ ] Final publication target is `staging`.
- [ ] `main` remains untouched unless explicitly requested.
