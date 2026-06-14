# Living Brand Website Template v1

This template defines how the rebuilt Diversity Tattoo site should function and where content belongs. It is based on the catalog in `../catalog/` and preserves the current content groups while making the site easier to navigate.

## Primary Navigation

- Home: brand overview, primary booking/contact actions, open-hours promise, and links into the main content categories.
- Tattoo: service overview, custom work, cover-ups, portfolio/gallery, artist routing, and tattoo preparation guides.
- Artists: artist index, individual artist profiles, specialties, portfolio links, and booking prompts.
- Piercing: piercing overview, $45 standard piercing offer, jewelry information, price list, aftercare, minors/policy FAQs, and tooth-gem routing.
- Smoke Shop: retail category overview, featured product categories, detox products, vaporizers, glass/accessories, and shop routing.
- Guides: tattoo aftercare, first tattoo, cover-up advice, detox articles, CBD/product education, and category filters.
- Reviews: customer proof, review highlights, review-source links, and trust markers.
- Visit: address, phone, hours, email, map/link-out, parking/location details, and contact flow.

## Homepage Function

The homepage should route visitors by intent:

- Get tattooed: send to Tattoo, Artists, Gallery, and booking/contact.
- Get pierced: send to Piercing, Price List, Tooth Gems, and FAQ.
- Shop retail: send to Smoke Shop and Shop/Product Catalog.
- Prepare or learn: send to Guides and FAQ.
- Visit today: send to Location/Contact and hours.

The homepage should not try to contain every detail. It should summarize each path and move users to the correct deeper section.

## Content Categories

### Tattoo Services

Belongs here:

- Tattoo overview copy from `home.html`.
- Tattoo safety and studio standards from `home.html` and `faq.html`.
- Gallery/portfolio route from `gallery.html`.
- Cover-up article from `post/tips-for-a-successful-cover-up-tattoo.html`.
- First tattoo guide from `post/firsttattoo.html`.
- Aftercare guide from `post/tattooaftercare.html`.

Functional requirements:

- Link to Artists from every tattoo service section.
- Link to Guides for preparation and aftercare content.
- Link to Contact/Visit for consultation or booking.

### Artists

Belongs here:

- Artist index from `artist.html`.
- Individual artist routes from `charlie.html` and `tank.html`.
- Portfolio/gallery references.

Functional requirements:

- Each artist profile should support name, bio, specialties, image, gallery items, and booking/contact CTA.
- Artist cards should filter or route by tattoo style when that data becomes available.

### Piercing

Belongs here:

- Body piercing overview from `bodypiercing.html`.
- Price list from `price-list-1.html`.
- Tooth gems from `toothgems.html`.
- Tattoo/piercing safety and minors/policy FAQ from `faq.html`.

Functional requirements:

- Price list should be structured as searchable rows, not a long static block.
- Tooth gems should be reachable from Piercing and from primary navigation.
- FAQ items should be grouped by safety, age/minors, jewelry, aftercare, and booking.

### Smoke Shop And Retail

Belongs here:

- Smoke shop overview from `smoke-shop.html`.
- Product catalog from `shop.html`, `shop?page=2`, `shop?page=3`, and all `product-page/*` routes.
- Product education articles from smoke-shop and detox-related posts.

Functional requirements:

- Product categories should include Smoke Accessories, Detox/Cleanses, Body Jewelry, Vaporizers, and Other Products.
- Product detail pages should share one reusable layout.
- Legacy product URLs should redirect to rebuilt product detail routes.

### Guides

Belongs here:

- All `post/*` articles.
- Blog category routes from `blog/categories/*`.
- Redirect-style legacy blog routes from `blog/*`.

Functional requirements:

- Articles should support category, excerpt, reading time, related services, related products, and next-step CTA.
- Blog redirects should point to their matching rebuilt article routes.

### Reviews

Belongs here:

- Current `reviews.html` content and any external review links.
- Future review snippets and source links.

Functional requirements:

- Reviews should route users to Tattoo, Piercing, Smoke Shop, or Visit depending on context.

### Visit And Contact

Belongs here:

- Address, phone, hours, and email from `contact.html` and `locations.html`.
- Social links from the current site.
- Map or directions link.
- Contact modal/form flow.

Functional requirements:

- Contact flow should let users choose Tattoo Consultation, Piercing Question, Retail/Product Question, or General Visit.
- Phone, email, address, and hours should be available from every page footer and from the mobile menu.

## Content Models

- Page: title, slug, section, summary, body sections, primary CTA, secondary CTA, media, SEO description, legacy URL aliases.
- Service: title, summary, eligible users, process steps, pricing references, related guides, related FAQs, CTA.
- Artist: name, slug, specialties, bio, portrait, gallery, booking CTA, legacy URL aliases.
- Product: title, slug, category, description, price if available, images, related guide, legacy URL aliases.
- Article: title, slug, category, excerpt, body, related service, related product, CTA, legacy URL aliases.
- FAQ Item: question, answer, category, related service, related CTA.
- Location: name, address, phone, hours, email, directions link, service availability.

## Redirect Rules

- `/` should resolve to the new homepage.
- `/home` should redirect to the new homepage.
- `/artist`, `/charlie`, and `/tank` should route to Artists.
- `/bodypiercing`, `/price-list-1`, and `/toothgems` should route to Piercing or the matching subpage.
- `/smoke-shop`, `/shop`, `/shop?page=2`, and `/shop?page=3` should route to Smoke Shop or Shop.
- `/product-page/*` should redirect to the matching rebuilt product detail page.
- `/post/*` should redirect to the matching rebuilt article page.
- `/blog/*` redirect pages should redirect to their matching rebuilt article or category route.
- `/contact` and `/locations` should route to Visit.
- `/profile/*` should be excluded from primary navigation unless account features are intentionally rebuilt.

## Rebuild Page Order

1. Homepage shell and global navigation.
2. Visit/Contact and footer data.
3. Tattoo, Artists, Piercing, Smoke Shop, and FAQ sections.
4. Product catalog and product details.
5. Guides/articles and legacy redirects.
6. Reviews and final content QA.

## Acceptance Criteria

- Every user-facing legacy route in `../catalog/content-inventory.csv` has a target destination.
- A visitor can reach Tattoo, Piercing, Smoke Shop, Guides, and Visit from the first viewport.
- Products and articles are reusable content records, not copied one-off layouts.
- Contact details are visible in the Visit section, footer, and mobile navigation.
- Missing media from `../catalog/media-inventory.csv` is reviewed before final migration.
