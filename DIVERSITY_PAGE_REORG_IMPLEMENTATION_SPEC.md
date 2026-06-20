# Diversity Page Reorg Implementation Spec

## Goal

Transform the current homepage-heavy Diversity Tattoo site into a sectioned business site. The homepage should become a polished landing and showcase page with concise pointers to deeper pages. The detailed content currently living on the homepage should move into canonical sub-pages where visitors can browse, compare, and act without scrolling through one long master page.

This reorg is not a full redesign from scratch. It is a migration of existing homepage sections and generated content into a clearer information architecture, while preserving the current static-site generator, product truth, blog parity, compatibility aliases, and staging-first publication flow.

## Branch And Worktree Plan

- [x] Base the work on `origin/staging`, not `main`.
- [x] Use existing collision-free feature branch `staging-page-reorg-resume` in the requested sibling worktree.
- [x] Note: `staging/page-reorg` was the original target name, but the repository already has a local `staging` branch, so Git cannot also create a slash-nested `staging/page-reorg` ref.
- [x] Create the feature branch in a sibling worktree so homepage image and formatting work can continue separately on `staging`.
- [x] Use this setup command:

```powershell
cd "C:\Users\pgche\OneDrive\Documents\Diversity Website Scrapev2\v1.2 rebuild"
git fetch origin
git worktree add "..\worktrees\staging-page-reorg" -b staging-page-reorg-resume origin/staging
```

- [x] Record the starting branch tips for `staging`, `origin/staging`, `main`, and `origin/main`.
- [x] Keep `main` untouched during this work.
- [x] Fetch latest `origin/staging` before final validation and confirm it is already an ancestor of `staging-page-reorg-resume`.
- [x] Resolve conflicts in `staging-page-reorg-resume`; no conflicts were present because `origin/staging` had not moved.
- [ ] Merge the finished branch back to `staging` only after validation passes.

## Homepage Migration Model

The homepage should stop being the place where every full section lives. It should become a business overview with focused cards, previews, and calls to action.

### Keep On Homepage

- [x] Keep the hero, business positioning, primary call button, and core studio facts.
- [x] Keep broad overview anchors:
  - [x] `#tattoo`
  - [x] `#artists`
  - [x] `#piercing`
  - [x] `#shop-catalog`
  - [x] `#blog`
  - [x] `#reviews`
  - [x] `#faq`
  - [x] `#visit`
- [x] Keep a compact tattoo/services overview that points to `/tattoo/`.
- [x] Keep a compact artists/team preview that points to `/artists/`.
- [x] Keep a piercing overview card that points to `/piercing/`.
- [x] Keep a tooth gems overview card that points to `/tooth-gems/`.
- [x] Keep a smoke shop overview card that points to `/smoke-shop/`.
- [x] Keep shop category tiles that point to `/shop/` or pre-filtered shop/category routes.
- [x] Keep the latest 3 blog posts only.
- [x] Keep reviews and FAQ teaser sections.
- [x] Keep Visit/contact information on the homepage.
- [x] Keep studio information for now, but reduce duplicate copy once the deeper pages carry the detail.

### Move Out Of Homepage

- [x] Move full tattoo/service detail from the homepage to `/tattoo/`.
- [x] Move full artist/team browsing from the homepage to `/artists/`.
- [x] Move piercing details, jewelry guidance, and piercing service copy to `/piercing/`.
- [x] Move the full piercing price table to `/piercing/#pricing`.
- [x] Move tooth gems detail to `/tooth-gems/`.
- [x] Move smoke shop, detox, vaporizers, smoke accessories, and other-product browsing to `/smoke-shop/`.
- [x] Move the full product catalog to `/shop/`.
- [x] Move the full blog archive and filters to `/blog/`.
- [x] Move review detail to `/reviews/`.
- [x] Move FAQ detail to `/faq/`.

## Canonical Page Contract

### `/tattoo/`

- [x] Generate an indexable top-level tattoo page.
- [x] Use tattoo service content from the existing source data.
- [x] Include tattoo service overview, custom work, cover-up positioning, artist/gallery pointers, and visit/call CTAs.
- [x] Do not duplicate the entire homepage service grid.
- [x] Link back to artists, gallery/source-backed tattoo material, blog posts, and visit information where relevant.

### `/artists/`

- [x] Keep `/artists/` as the canonical artist/team page.
- [x] Use existing artist records from `site-data.js`.
- [x] Keep individual artist profile links.
- [x] Homepage should show a compact artist preview, not the full artist browsing experience.

### `/piercing/`

- [x] Generate an indexable top-level piercing page.
- [x] Move piercing service copy from the homepage and current service pages into this page.
- [x] Move the full piercing price table here.
- [x] Add a stable `#pricing` anchor for direct links from homepage CTAs.
- [x] Add jewelry guidance and product browsing context.
- [x] Show a pre-filtered product grid for Body Jewelry only.
- [x] Do not show detox, vaporizers, smoke accessories, or other smoke-shop products on this page.
- [x] Treat `/bodypiercing/` as a noindex compatibility alias to `/piercing/`.

### `/tooth-gems/`

- [x] Generate an indexable top-level tooth gems page.
- [x] Move tooth gems service detail from the homepage/current service content into this page.
- [x] Use tooth-gem-specific/source-backed imagery if it can be localized from the source inventory.
- [x] If tooth-gem-specific imagery is unavailable, use the explicit `asset-not-found` placeholder and record the issue instead of substituting unrelated product imagery.
- [x] If source-backed tooth gem product records or assets exist, render a scoped product/visual section comparable to the jewelry page.
- [x] If no source-backed tooth gem product records exist, keep the page as service-focused with CTA and related links.
- [x] Treat `/toothgems/` as a noindex compatibility alias to `/tooth-gems/`.

### `/smoke-shop/`

- [x] Generate an indexable top-level smoke shop page.
- [x] Make this page own the current non-jewelry retail groups:
  - [x] Detox / Cleanses
  - [x] Vaporizers
  - [x] Smoke Accessories
  - [x] Other Products
- [x] Do not show Body Jewelry on `/smoke-shop/`.
- [x] Keep the current category labels for now.
- [x] Structure the code so these labels can be renamed or reorganized later without changing the page architecture.
- [x] Render a pre-filtered product grid for the owned categories, the same way `/piercing/` filters to Body Jewelry.
- [x] Include smoke shop and detox service/source copy where available.
- [x] Link to `/shop/` for the full catalog.

### `/shop/`

- [x] Keep `/shop/` as the only full catalog page.
- [x] Show all current products.
- [x] Keep category tiles, category filters, search, sort, clear filters, live result summary, and product detail links.
- [x] Preserve old shop query behavior such as `/shop/?page=2` opening the same full catalog surface.
- [x] Do not reintroduce pagination UI or paged product subsets.

### `/blog/`

- [x] Keep `/blog/` as the full blog archive.
- [x] Preserve the 15-post blog parity established from the feed/source repair work.
- [x] Keep archive filtering on the blog page.
- [x] Homepage should render exactly the latest 3 blog posts.
- [x] Add a centered `See more` button on the homepage linking to `/blog/`.
- [x] Replace homepage copy such as `Open blog archive` with the shorter `See more` CTA.

### `/reviews/`

- [x] Generate an indexable top-level reviews page.
- [x] Move review/trust detail out of the homepage teaser.
- [x] Keep homepage reviews as a concise trust pointer.
- [x] Treat old `/reviews/` compatibility behavior as canonical if the generated route now owns that path.

### `/faq/`

- [x] Generate an indexable top-level FAQ page.
- [x] Move FAQ detail out of the homepage teaser.
- [x] Keep homepage FAQ as a concise pointer.
- [x] Treat old `/faq/` compatibility behavior as canonical if the generated route now owns that path.

### Visit

- [x] Keep Visit on the homepage in this pass.
- [x] Do not create `/visit/` unless the scope changes.
- [x] Keep visit CTAs visible from every new top-level page.

## Generator And Data Tasks

- [x] Add a section-page configuration in `build_v1_2_content.py`.
- [x] Include route, title, eyebrow, source content, canonical path, hero image, CTA, homepage anchor, and product scope in the config.
- [x] Generate top-level section pages from the config instead of hand-copying static HTML.
- [x] Update `DETAIL_DIRS` and alias cleanup rules so canonical top-level pages do not get deleted as alias directories.
- [x] Update `row_destination` so current service/source rows map to the new canonical section pages where appropriate.
- [x] Update `canonical_url_map_rows` to include all new canonical section pages.
- [x] Update sitemap generation so new canonical section pages are included.
- [x] Update alias generation so legacy spellings remain noindex aliases.
- [x] Update route/accounting ledgers so each old route has a canonical target, compatibility alias, or explicit exception.
- [x] Preserve product-publication ledger behavior.
- [x] Preserve blog-post ledger behavior.
- [x] Preserve `asset-not-found` behavior for missing canonical assets.

## Shared Renderer Tasks

- [x] Extend `content-render.js` to support scoped product grids.
- [x] Allow a page or container to declare an allowed category scope.
- [x] Keep `/shop/` as the all-products grid.
- [x] Make `/piercing/` render Body Jewelry only.
- [x] Make `/smoke-shop/` render Detox / Cleanses, Vaporizers, Smoke Accessories, and Other Products only.
- [x] Make `/smoke-shop/` exclude Body Jewelry even if query parameters request it.
- [x] Add optional homepage preview limits for blog cards and any compact product/artist previews.
- [x] Keep search, sort, result counts, clear-filter behavior, and accessibility states working on scoped grids.
- [x] Avoid unsupported scoped-page filters showing empty or misleading category controls.
- [x] Keep URL query updates useful on `/shop/`; scoped pages may omit or constrain category query behavior.

## Homepage Tasks

- [x] Replace the current full product catalog section with shop category tiles.
- [x] Add tiles for Body Jewelry, Detox / Cleanses, Vaporizers, Smoke Accessories, and Other Products where appropriate.
- [x] Make tiles point to relevant canonical pages or filtered shop views.
- [x] Replace the full homepage blog archive/filter UI with latest 3 posts.
- [x] Add centered `See more` button under the latest 3 posts.
- [x] Remove the piercing price table from the homepage.
- [x] Add a homepage CTA from piercing overview to `/piercing/#pricing`.
- [x] Ensure every homepage overview section has a clear next step.
- [x] Keep the page visually balanced after removing large sections.
- [x] Avoid leaving orphaned anchors or buttons that still point to removed in-page content.

## Public Bundle And Validator Tasks

- [x] Update `scripts/build_public_bundle.py` canonical directories to include the new top-level pages.
- [x] Update `scripts/validate_production.py` public top-level directory rules.
- [x] Update alias top-level directory rules where a path changes from alias to canonical.
- [x] Ensure canonical pages are not noindex.
- [x] Ensure compatibility aliases are noindex.
- [x] Ensure aliases do not appear in `sitemap.xml`.
- [x] Ensure `sitemap.xml` includes the new canonical pages.
- [x] Ensure forbidden audit/rebuild copy does not appear in public HTML.
- [x] Ensure product image manifest checks still pass.
- [x] Ensure blog body and image quality checks still pass.

## Documentation Tasks

- [x] Update `V1_2_FULL_IMPLEMENTATION_SPEC.md` with the approved top-level page architecture.
- [x] Document the homepage migration model.
- [x] Document the category ownership rules for `/piercing/`, `/smoke-shop/`, `/shop/`, and `/tooth-gems/`.
- [x] Document that Smoke Shop owns Detox / Cleanses, Vaporizers, Smoke Accessories, and Other Products for now.
- [x] Document that category labels may be renamed later without changing ownership in this pass.
- [x] Document that Visit remains homepage-only for now.
- [x] Document that `main` is not part of this publication pass.

## Merge Plan

- [x] Fetch latest remote refs before final validation.
- [x] Confirm latest `origin/staging` is already contained in `staging-page-reorg-resume`.
- [x] Resolve conflicts, preserving separately completed homepage image/formatting improvements; no conflicts were present.
- [x] Rerun generator and validation after the final `origin/staging` check.
- [ ] Merge `staging-page-reorg-resume` back into `staging`.
- [ ] Push `staging`.
- [x] Do not push or merge to `main` unless explicitly requested.

Suggested final merge commands:

```powershell
cd "C:\Users\pgche\OneDrive\Documents\Diversity Website Scrapev2\worktrees\staging-page-reorg"
git fetch origin
git switch staging-page-reorg-resume
git merge origin/staging

python build_v1_2_content.py
node --check content-render.js
node --check motion.js
python scripts/build_public_bundle.py
python scripts/validate_production.py

cd "C:\Users\pgche\OneDrive\Documents\Diversity Website Scrapev2\v1.2 rebuild"
git switch staging
git pull --ff-only origin staging
git merge --no-ff staging-page-reorg-resume
git push origin staging
```

## Validation Checklist

- [x] Run the generator:

```powershell
python build_v1_2_content.py
```

- [x] Check JavaScript syntax:

```powershell
node --check content-render.js
node --check motion.js
```

- [x] Build the public bundle:

```powershell
python scripts/build_public_bundle.py
```

- [x] Run production validation:

```powershell
python scripts/validate_production.py
```

- [x] Confirm `production-readiness.txt` reports `PASS`.
- [x] Serve `public/` locally.
- [x] Check desktop layout for `/`.
- [x] Check mobile layout for `/`.
- [x] Check desktop and mobile layout for `/tattoo/`.
- [x] Check desktop and mobile layout for `/artists/`.
- [x] Check desktop and mobile layout for `/piercing/`.
- [x] Check desktop and mobile layout for `/tooth-gems/`.
- [x] Check desktop and mobile layout for `/smoke-shop/`.
- [x] Check desktop and mobile layout for `/shop/`.
- [x] Check desktop and mobile layout for `/blog/`.
- [x] Check desktop and mobile layout for `/reviews/`.
- [x] Check desktop and mobile layout for `/faq/`.
- [x] Check desktop and mobile layout for one product detail page.
- [x] Check desktop and mobile layout for one blog post page.
- [x] Check `/bodypiercing/` alias behavior.
- [x] Check `/toothgems/` alias behavior.
- [x] Check one old `/post/*` alias.
- [x] Confirm canonical pages are indexable.
- [x] Confirm aliases are noindex.
- [x] Confirm aliases are absent from `sitemap.xml`.
- [x] Confirm no broken internal links from homepage CTAs.
- [x] Confirm no broken images.
- [x] Confirm no horizontal overflow on mobile.

## UI And Interaction QA

- [x] Confirm the new section pages use the same modern visual language as the homepage: sticky header, strong hero treatment, polished service cards, consistent typography, consistent buttons, intentional spacing, and source-backed imagery.
- [x] Confirm moved sections do not feel like raw detail pages; each top-level page should feel like a designed business landing page for that service/category.
- [x] Confirm desktop layouts look balanced at common widths such as 1440px, 1280px, and 1024px.
- [x] Confirm mobile layouts look balanced at common widths such as 390px, 375px, and 320px.
- [x] Confirm tablet/narrow-desktop layouts do not create awkward two-column wrapping, clipped cards, or oversized empty gaps.
- [x] Confirm cards, buttons, filters, search inputs, select menus, and links have visible hover/focus states.
- [x] Confirm keyboard navigation can reach primary nav links, CTAs, product filters, search, sort, clear filters, and card links.
- [x] Confirm mobile navigation opens, closes, fits on screen, and does not cover important content after a link is selected.
- [x] Confirm animations and reveal effects still run smoothly after content is moved out of the homepage.
- [x] Confirm scroll-triggered effects do not leave blank space, hidden content, or stale layout positions after dynamic product/blog rendering.
- [x] Confirm product grid filtering works on `/shop/`, `/piercing/`, and `/smoke-shop/`.
- [x] Confirm scoped product pages never show out-of-scope filter buttons or misleading result counts.
- [x] Confirm `/piercing/` product cards are jewelry-only.
- [x] Confirm `/smoke-shop/` product cards are Detox / Cleanses, Vaporizers, Smoke Accessories, or Other Products only.
- [x] Confirm `/smoke-shop/` does not show Body Jewelry even if a jewelry category query parameter is manually added.
- [x] Confirm homepage blog preview shows exactly 3 posts and the `See more` button is centered and links to `/blog/`.
- [x] Confirm all page CTAs point to canonical destinations rather than old service aliases.
- [x] Confirm image rendering quality is acceptable on desktop and mobile, with no stretched, blurry, unrelated, or badly cropped primary images.
- [x] Confirm every missing tooth-gem-specific image uses the explicit `asset-not-found` placeholder and is documented for later asset replacement.
- [x] Confirm no text overlaps images, buttons, cards, nav, filters, tables, or adjacent sections.
- [x] Confirm no button or card label overflows its container at mobile widths.
- [x] Confirm the piercing pricing table is readable on mobile and does not force horizontal page overflow.
- [x] Confirm detail pages and top-level section pages visually match the homepage quality level, not the older generic generated detail-page style.
- [x] Confirm Chrome passes local browser QA on Windows.
- [x] Confirm the homepage hero eyebrow desktop gap is tightened to the normal section/header rhythm after the large-logo polish.
- [x] Confirm the homepage Visit intent card is removed from the services card grid while the real `#visit` section and `/#visit` navigation remain.
- [x] Confirm the follow-up homepage polish still has no horizontal overflow at 1440px, 1024px, 390px, and 320px.
- [x] Confirm the follow-up homepage polish keeps the previous artist-card, service-card, magnetic-scroll, and reduced-motion behavior intact.
- [x] Confirm fixed-header clearance prevents first visible content from sitting under the header on `/`, `/index.html#top`, `/shop/`, all canonical section pages, one product page, and one artist page.
- [x] Confirm homepage and generated-page headers use the same canonical nav labels and order, including Tooth Gems and Smoke Shop.
- [x] Confirm the homepage `#service-system` section is removed while Reviews, FAQ, and Visit remain available.
- [x] Confirm the nav collapse breakpoint prevents wrapped desktop nav from covering content with the enlarged logo.
- [x] Confirm `/shop/` product lane tiles preserve category filters and land the product controls directly below the fixed header.
- [x] Confirm direct `/shop/index.html?category=...#product-filters` URLs activate the matching filter and land below the fixed header at 1440px, 1024px, 390px, and 320px.
- [ ] Confirm Edge passes local browser QA on Windows.
- [ ] Confirm Firefox if available locally.
- [x] Record Safari as not natively testable in the local Windows environment unless a remote Safari, BrowserStack-style service, or separate macOS/iOS device is available.
- [ ] If Safari access is available, check layout, sticky header behavior, mobile nav, product filters, image rendering, and animation behavior in Safari before final staging merge.

## Optional Public Preview

- [x] Serve `public/` locally.
- [ ] Start Cloudflare Quick Tunnel with `cloudflared`.
- [ ] Extract the `trycloudflare.com` URL from the `cloudflared` stderr log.
- [ ] Verify public HTTP 200 responses before reporting the URL.
- [ ] Spot-check `/`, `/piercing/`, `/smoke-shop/`, `/shop/`, and `/blog/` through the public URL.
- [ ] Keep local server and tunnel processes alive while the preview is needed.

## Verified Post-Reorg Polish Pass

- [x] Use cropped logo asset `8d0ab0_6a77779840c44b9586da1fefe272017b_mv2_d_3300_1480_s_4_2.png`.
- [x] Preserve the cropped logo through generator-managed asset rebuilds and the public bundle.
- [x] Increase desktop logo display width to 264px and use a mobile-safe cap at narrow widths.
- [x] Change `.site-nav` font size to `1.4rem`.
- [x] Update homepage header navigation so page links go to canonical routes such as `/tattoo/`, `/artists/`, `/piercing/`, `/shop/`, `/blog/`, `/reviews/`, and `/faq/` instead of homepage section anchors.
- [x] Keep Visit as the homepage route `/#visit`; no `/visit/` page was created.
- [x] Update footer navigation to use the same canonical route set and the same `.site-nav` sizing/alignment treatment as the header links.
- [x] Constrain homepage Shop and Visit content to the shared section side rails while keeping `.marquee-section` full-bleed.
- [x] Add a PNG favicon link using the cropped logo asset so local Chrome QA has no default favicon 404.
- [x] Verify served cropped logo URL returns HTTP 200 from `http://localhost:4211/`.
- [x] Verify no generated HTML references the old `3300_2550` logo filename.
- [x] Verify homepage header/footer page-nav links do not use old section anchors for Tattoo, Artists, Piercing, Shop, Blog, Reviews, or FAQ.
- [x] Verify desktop 1440, tablet 1024, mobile 390, and mobile 320 Chrome QA: no horizontal overflow, no console errors, no failed responses, and Shop/Visit rails aligned.
- [x] Verify header navigation uses `Shop all` instead of `Shop` across homepage, generated section pages, detail pages, and utility pages.
- [x] Verify generated pages include the same header `Call` CTA as the homepage so header grid columns and nav button placement are universal.
- [x] Verify `.site-nav` links render as bordered, clearly delineated buttons in desktop headers and separated rows in the mobile menu.
- [x] Verify 1440px rendered header geometry is identical across `/`, `/index.html#top`, `/shop/`, `/tattoo/`, `/artists/`, `/piercing/`, `/tooth-gems/`, `/smoke-shop/`, `/blog/`, `/reviews/`, `/faq/`, one product page, one artist page, and one utility page.
- [x] Verify stable scrollbar gutter prevents header/nav button position drift between long and short pages.

## Verified Homepage Layout And Scroll Polish Pass

- [x] Continue work in the current active worktree and current branch `staging-page-reorg-resume`; no branch switch, merge, or push was performed.
- [x] Constrain the homepage artist preview grid to the shared site rail.
- [x] Make homepage artist cards wrap with responsive tracks instead of overflowing horizontally.
- [x] Hide the `TATTOO Artists` card from the homepage artist preview without deleting the source artist record or canonical `/artists/` route.
- [x] Hide the `Location / Contact` / Visit planning card from the homepage services matrix while keeping the real homepage `#visit` section.
- [x] Tighten homepage section spacing globally, including intro-only sections.
- [x] Add homepage-only magnetic eyebrow scroll assist.
- [x] Exclude the marquee from magnetic scroll targets.
- [x] Disable magnetic scroll under reduced-motion mode and during hash navigation, nav lock, modal display, or focused interactive controls.
- [x] Verify desktop 1440 and tablet 1024 Chrome QA: artists rail aligned at 1180px/968px, max section gap 118px, no horizontal overflow, no console errors, and no failed responses.
- [x] Verify mobile 390 and 320 Chrome QA: artists rail aligned at 354px/284px, max section gap 88px, no horizontal overflow, no console errors, and no failed responses.
- [x] Verify rendered homepage artist titles are only `Diversity Tattoo LV | United States` and `Tank`.
- [x] Verify rendered homepage service titles are only `Tattoo Services`, `Piercing`, `Tooth Gems`, `Smoke Shop`, `Reviews`, and `FAQ`.
- [x] Verify magnetic scroll lands the next eyebrow below the sticky header.
- [x] Verify reduced-motion mode applies `.reduced-motion` and does not magnetically snap to an eyebrow.

## Verified Card Wrap And Product Jump Button Polish Pass

- [x] Continue work in the current active worktree and current branch `staging-page-reorg-resume`; no branch switch, merge, push, deploy, or cleanup was performed.
- [x] Cap homepage service cards with auto-wrapping grid tracks so they no longer stretch ultra-wide.
- [x] Cap repeated generated card grids with auto-wrapping tracks and remove those grids from the 1240px forced one-column rule.
- [x] Preserve structural one-column behavior for layout containers such as section-page heroes, sticky stories, split features, sliders, and QA layouts.
- [x] Change the `/smoke-shop/` secondary hero action to `Explore items` and point it to local `#product-filters`.
- [x] Add the `/piercing/` `See Jewelry` hero action and point it to local `#product-filters` while keeping `Jump to pricing`.
- [x] Verify homepage service cards at 1440, 1037, 768, 638, 390, and 320 widths: max card width is 280px except the 320px viewport where the rail constrains cards to 269px, cards wrap cleanly, and no horizontal overflow appears.
- [x] Verify `/smoke-shop/` `Explore items` lands the product toolbar 14px below the fixed header and the page renders 99 scoped non-jewelry products.
- [x] Verify `/piercing/` `See Jewelry` lands the product toolbar 14px below the fixed header and the page renders 25 scoped Body Jewelry products.
- [x] Verify `/`, `/smoke-shop/`, and `/piercing/` have no console errors in focused Chrome QA.

## Done Looks Like

- [x] Homepage reads as a landing page and business showcase, not the whole site compressed into one page.
- [x] Every homepage section has a clear CTA to its dedicated page.
- [x] Full tattoo details live on `/tattoo/`.
- [x] Full artist/team browsing lives on `/artists/`.
- [x] Piercing service detail, piercing prices, and Body Jewelry browsing live on `/piercing/`.
- [x] `/piercing/` does not show smoke-shop product categories.
- [x] Tooth gems content lives on `/tooth-gems/`.
- [x] `/tooth-gems/` uses source-backed imagery when available and a documented placeholder when not available.
- [x] `/smoke-shop/` owns Detox / Cleanses, Vaporizers, Smoke Accessories, and Other Products.
- [x] `/smoke-shop/` shows no Body Jewelry.
- [x] `/shop/` remains the only full catalog page.
- [x] `/blog/` owns the full archive and filters.
- [x] Homepage shows exactly 3 blog posts and a centered `See more` button.
- [x] `/reviews/` is a canonical top-level reviews page.
- [x] `/faq/` is a canonical top-level FAQ page.
- [x] Visit remains on the homepage.
- [x] New canonical pages are included in `sitemap.xml`.
- [x] New canonical pages are not noindex.
- [x] Legacy aliases still work.
- [x] Legacy aliases are noindex.
- [x] Legacy aliases are not in `sitemap.xml`.
- [x] Production validation passes.
- [x] Runtime QA passes on desktop and mobile.
- [x] Final publication target is `staging`.
- [x] `main` remains untouched unless explicitly requested.
