# Diversity Rebuild V1.2 QA Checklist

Generated: 2026-06-14

## Inventory Targets

- Total legacy HTML routes represented: 171
- Product records rendered in the shop catalog: 124
- Shop compatibility inputs represented: 7
- Blog/guide routes represented: 22
- Blog posts rendered in the guide system: 15
- Blog category routes preserved: 2
- Blog redirect routes preserved: 4
- Member/profile routes flagged for utility handling: 4
- Media references cataloged: 1615
- External links cataloged: 6466

## Product Category Coverage

- Shop - Body Jewelry: 25
- Shop - Detox / Cleanses: 22
- Shop - Other Products: 31
- Shop - Smoke Accessories: 31
- Shop - Vaporizers: 15

## Future Section Coverage

- Artists: 3
- Blog / Guides: 22
- FAQ: 1
- Home: 2
- Location / Contact: 2
- Piercing: 2
- Reviews: 1
- Shop / Product Catalog: 131
- Smoke Shop: 1
- Tattoo Services: 1
- Tooth Gems: 1
- Utility / Member Account: 4

## Browser QA Pass

- [x] Hero loads with local media and first viewport communicates tattoo, piercing, retail, guide and visit paths.
- [x] Primary navigation reaches Tattoo, Artists, Piercing, Tooth Gems, Shop Catalog, Guides, Reviews, FAQ and Visit.
- [x] Product filter buttons update the 124-record product grid without layout overflow.
- [x] Guide filters expose posts, category routes, index route and redirect routes.
- [ ] Generated product, guide, artist, service, shop and utility detail pages open from v1.2 links.
- [x] Accordion, tabs, guide slider and contact modal remain keyboard-usable.
- [x] Mobile menu opens on narrow viewports and all generated sections fit without horizontal scrolling.
- [ ] Reduced-motion mode leaves all content visible without parallax, pinning or scrubbed motion.

## Media Risk Review

- none: 1466
- not found in scrape log; verify manually: 149

## External Link Review

- Approved for rebuild: 533
- Needs review/excluded runtime candidates: 5933

- www.facebook.com: 165
- www.instagram.com: 165
- www.atomiclashlounge.com: 165
- www.detoxify.com: 1

## Route Preservation Samples

- `artist.html` -> `artists/index.html` (rebuilt section page)
- `blog/categories/getting-started.html` -> `blog/index.html` (redirect to rebuilt destination)
- `blog/categories/your-community.html` -> `blog/index.html` (redirect to rebuilt destination)
- `blog/davinci-miqro.html` -> `blog/davinci-miqro.html` (redirect to rebuilt destination)
- `blog/kandypens-k-stick.html` -> `blog/kandypens-k-stick.html` (redirect to rebuilt destination)
- `blog/levo-oil-butter-maker.html` -> `blog/levo-oil-butter-maker.html` (redirect to rebuilt destination)
- `blog/now-in-store-dr-dabber-switch.html` -> `blog/now-in-store-dr-dabber-switch.html` (redirect to rebuilt destination)
- `blog.html` -> `blog/index.html` (rebuilt section page)
- `bodypiercing.html` -> `services/bodypiercing.html` (rebuilt detail page)
- `charlie.html` -> `artists/charlie.html` (rebuilt detail page)
- `contact.html` -> `services/contact.html` (rebuilt detail page)
- `faq.html` -> `services/faq.html` (rebuilt detail page)
- `gallery.html` -> `services/gallery.html` (rebuilt detail page)
- `home.html` -> `index.html` (rebuilt primary page)
- `index.html` -> `index.html` (rebuilt primary page)
- `locations.html` -> `services/locations.html` (rebuilt detail page)
- `post/are-detox-cleanses-permanent.html` -> `blog/are-detox-cleanses-permanent.html` (rebuilt detail page)
- `post/can-my-tattoo-be-covered-up.html` -> `blog/can-my-tattoo-be-covered-up.html` (rebuilt detail page)
- `post/cbdforpets.html` -> `blog/cbdforpets.html` (rebuilt detail page)
- `post/cbdforpets1.html` -> `blog/cbdforpets1.html` (rebuilt detail page)
- `post/cbdforpets2.html` -> `blog/cbdforpets2.html` (rebuilt detail page)
- `post/davinci-miqro.html` -> `blog/davinci-miqro.html` (rebuilt detail page)
- `post/firsttattoo.html` -> `blog/firsttattoo.html` (rebuilt detail page)
- `post/honeystick-beekeeper-conceal-essential-oil-vaporizer.html` -> `blog/honeystick-beekeeper-conceal-essential-oil-vaporizer.html` (rebuilt detail page)
- `post/kandypens-k-stick.html` -> `blog/kandypens-k-stick.html` (rebuilt detail page)
- `post/levo-oil-butter-maker.html` -> `blog/levo-oil-butter-maker.html` (rebuilt detail page)
- `post/now-in-store-dr-dabber-switch.html` -> `blog/now-in-store-dr-dabber-switch.html` (rebuilt detail page)
- `post/tattooaftercare.html` -> `blog/tattooaftercare.html` (rebuilt detail page)
- `post/tips-for-a-successful-cover-up-tattoo.html` -> `blog/tips-for-a-successful-cover-up-tattoo.html` (rebuilt detail page)
- `post/what-is-detox.html` -> `blog/what-is-detox.html` (rebuilt detail page)
- `post/what-to-do-if-your-tattoo-or-piercing-itches.html` -> `blog/what-to-do-if-your-tattoo-or-piercing-itches.html` (rebuilt detail page)
- `price-list-1.html` -> `services/price-list-1.html` (rebuilt detail page)
- `product-page/additive-x-stream-synthentic-urine.html` -> `products/additive-x-stream-synthentic-urine.html` (rebuilt detail page)
- `product-page/ascent-oil-jars.html` -> `products/ascent-oil-jars.html` (rebuilt detail page)
- `product-page/ascentst-g-adapter.html` -> `products/ascentst-g-adapter.html` (rebuilt detail page)
- `product-page/ascentst-u-adapter.html` -> `products/ascentst-u-adapter.html` (rebuilt detail page)

## Final QA Notes

- v1.2 is generated from the updated 171-route catalog.
- Wix runtime, analytics and framework assets remain excluded from user-facing rebuild content.
- Legacy product and blog URLs are represented through structured detail pages and `redirects.json`.
- Media rows with risks remain visible in `media-review.json` and the QA panel until replaced or approved.
