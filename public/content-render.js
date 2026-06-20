(() => {
  const data = window.DIVERSITY_SITE_DATA;
  if (!data) return;

  const $ = (selector) => document.querySelector(selector);
  const mobileQuery = window.matchMedia("(max-width: 640px)");
  const GUIDE_MOBILE_LIMIT = 6;
  const CATEGORY_ORDER = [
    "Shop - Body Jewelry",
    "Shop - Detox / Cleanses",
    "Shop - Smoke Accessories",
    "Shop - Vaporizers",
    "Shop - Other Products",
  ];
  const CATEGORY_LABELS = {
    "Shop - Body Jewelry": "Body Jewelry",
    "Shop - Detox / Cleanses": "Detox / Cleanses",
    "Shop - Smoke Accessories": "Smoke Accessories",
    "Shop - Vaporizers": "Vaporizers",
    "Shop - Other Products": "Other Products",
  };

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function normalizeKey(value) {
    return String(value || "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");
  }

  function setHtml(selector, html) {
    const node = $(selector);
    if (node) node.innerHTML = html;
  }

  function rebuildPath(path) {
    if (!path) return "#visit";
    if (/^https?:/.test(path) || path.startsWith("#")) return path;
    return pagePrefix() + path;
  }

  function pagePrefix() {
    const parts = window.location.pathname.split("/").filter(Boolean);
    const filePart = parts.length ? parts[parts.length - 1] : "";
    const depth = filePart.includes(".") ? parts.length - 1 : parts.length;
    return depth > 0 ? "../".repeat(depth) : "";
  }

  function assetPath(path) {
    if (!path || /^https?:/.test(path) || path.startsWith("/")) return path;
    return pagePrefix() + path;
  }

  function parsePrice(value) {
    const match = String(value || "").replace(/,/g, "").match(/[\d.]+/);
    return match ? Number(match[0]) : Number.POSITIVE_INFINITY;
  }

  function categoryRank(product) {
    const rank = CATEGORY_ORDER.indexOf(product.category);
    return rank === -1 ? CATEGORY_ORDER.length : rank;
  }

  function isMobileLayout() {
    return mobileQuery.matches;
  }

  function refreshLayout() {
    window.requestAnimationFrame(() => {
      window.ScrollTrigger?.refresh?.();
      window.dispatchEvent(new CustomEvent("diversity:content-updated"));
    });
  }

  function productImageDimensions(product) {
    return {
      width: Number(product.canonicalAssetWidth || product.imageWidth || 0),
      height: Number(product.canonicalAssetHeight || product.imageHeight || 0),
    };
  }

  function fitProductCardImages(scope = document) {
    window.requestAnimationFrame(() => {
      scope.querySelectorAll(".product-card[data-image-width][data-image-height]").forEach((card) => {
        const img = card.querySelector(":scope > img");
        if (!img) return;
        const sourceWidth = Number(card.dataset.imageWidth || img.naturalWidth || 0);
        const sourceHeight = Number(card.dataset.imageHeight || img.naturalHeight || 0);
        if (!sourceWidth || !sourceHeight) {
          card.dataset.imageFit = "dimension-missing";
          return;
        }
        const boxWidth = card.clientWidth;
        const mediaHeight = parseFloat(getComputedStyle(card).getPropertyValue("--card-media-height")) || img.clientHeight;
        if (!boxWidth || !mediaHeight) return;
        const sourceAspect = sourceHeight / sourceWidth;
        if (sourceAspect < 1.2) {
          img.style.removeProperty("--card-image-width");
          img.style.removeProperty("--card-image-height");
          card.dataset.imageFit = "cover";
          return;
        }
        const coverHeight = boxWidth * sourceAspect;
        const overflow = coverHeight - mediaHeight;
        if (overflow <= mediaHeight * 0.08) {
          img.style.removeProperty("--card-image-width");
          img.style.removeProperty("--card-image-height");
          card.dataset.imageFit = "cover";
          return;
        }
        const targetHeight = mediaHeight + overflow * 0.2;
        const minWidth = boxWidth * 0.82;
        const targetWidth = Math.max(minWidth, Math.min(boxWidth, targetHeight / sourceAspect));
        img.style.setProperty("--card-image-width", `${(targetWidth / boxWidth * 100).toFixed(2)}%`);
        img.style.setProperty("--card-image-height", `${Math.max(mediaHeight, targetWidth * sourceAspect).toFixed(2)}px`);
        card.dataset.imageFit = targetWidth < boxWidth * 0.98 ? "adjusted" : "cover";
      });
    });
  }

  function ensureExpandButton(anchor, id) {
    let button = document.getElementById(id);
    if (!button) {
      button = document.createElement("button");
      button.type = "button";
      button.id = id;
      button.className = "button secondary catalog-expand";
      anchor.insertAdjacentElement("afterend", button);
    }
    return button;
  }

  function renderStats() {
    setHtml(
      "#catalog-stat-grid",
      [
        ["services", "10+"],
        ["products", "Hundreds of"],
        ["happy customers", "Thousands of"],
      ]
        .map(
          ([label, value]) => `
            <article class="stat-tile is-visible">
              <strong>${escapeHtml(value)}</strong>
              <span>${escapeHtml(label)}</span>
            </article>
          `
        )
        .join("")
    );
  }

  function renderArtists() {
    setHtml(
      "#artist-profile-grid",
      data.artists
        .filter((artist) => artist.title !== "TATTOO Artists")
        .map(
          (artist) => `
            <article class="profile-card hover-lift is-visible">
              <img src="${escapeHtml(assetPath(artist.image))}" alt="${escapeHtml(artist.title)}" loading="lazy" />
              <div>
                <p>Artist profile</p>
                <h3>${escapeHtml(artist.title)}</h3>
                <p>${escapeHtml(artist.excerpt)}</p>
                <a href="${escapeHtml(rebuildPath(artist.destinationPath))}">View profile</a>
              </div>
            </article>
          `
        )
        .join("")
    );
  }

  function renderServiceMatrix() {
    const ordered = ["Tattoo Services", "Piercing", "Tooth Gems", "Smoke Shop", "Reviews", "FAQ"];
    const groups = ordered
      .map((category) => ({
        category,
        pages: data.servicePages.filter((page) => page.category === category),
      }))
      .filter((group) => group.pages.length);

    setHtml(
      "#service-matrix",
      groups
        .map(
          (group) => `
            <article class="service-record is-visible">
              <span>${escapeHtml(group.pages.length)} page${group.pages.length === 1 ? "" : "s"}</span>
              <h3>${escapeHtml(group.category)}</h3>
              <p>${escapeHtml(group.pages[0].excerpt)}</p>
              <div class="route-pills">
                ${group.pages
                  .map((page) => `<a href="${escapeHtml(rebuildPath(page.destinationPath))}">${escapeHtml(page.title)}</a>`)
                  .join("")}
              </div>
            </article>
          `
        )
        .join("")
    );
  }

  function renderPiercingPrices() {
    setHtml(
      "#piercing-price-body",
      data.piercingPrices
        .map(
          (row) => `
            <tr>
              <th scope="row">${escapeHtml(row.name)}</th>
              <td>${escapeHtml(row.price)}</td>
              <td>${escapeHtml(row.notes)}</td>
            </tr>
          `
        )
        .join("")
    );
  }

  function setupProducts() {
    const filterList = $("#product-category-filter-list") || $("#product-filter-list");
    const grid = $("#product-grid");
    const count = $("#product-filter-summary") || $("#product-count");
    const search = $("#product-search");
    const sort = $("#product-sort");
    const clear = $("#product-clear-filters");
    if (!filterList || !grid) return;

    const scopeCategories = (grid.dataset.productScope || grid.closest(".product-catalog")?.dataset.productScope || "")
      .split("|")
      .map((item) => item.trim())
      .filter(Boolean);
    const scopedProducts = scopeCategories.length
      ? data.products.filter((product) => scopeCategories.includes(product.category))
      : data.products;
    const categories = CATEGORY_ORDER.map((category) => ({
      category,
      total: scopedProducts.filter((product) => product.category === category).length,
    })).filter((item) => item.total);
    const filters = [{ category: "All", total: scopedProducts.length }, ...categories];
    let active = "All";
    let query = "";
    let sortMode = "category-name";

    const params = new URLSearchParams(window.location.search);
    const requestedCategory = params.get("category");
    const categoryBySlug = new Map(categories.map((item) => [normalizeKey(CATEGORY_LABELS[item.category] || item.category), item.category]));
    if (requestedCategory && categoryBySlug.has(normalizeKey(requestedCategory))) {
      active = categoryBySlug.get(normalizeKey(requestedCategory));
    }
    if (params.get("q") && search) {
      query = params.get("q").trim();
      search.value = query;
    }
    const allowedSorts = new Set(["category-name", "name-asc", "price-asc", "price-desc", "stock-first"]);
    if (params.get("sort") && allowedSorts.has(params.get("sort"))) {
      sortMode = params.get("sort");
      sort.value = sortMode;
    }
    const fullShopPath = /\/shop\/(?:index\.html)?$/.test(window.location.pathname);
    const shouldLandAtFilters = fullShopPath && (Boolean(requestedCategory) || window.location.hash === "#product-filters");

    filterList.innerHTML = filters
      .map(
        (filter) => `
          <button type="button" data-product-filter="${escapeHtml(filter.category)}" aria-pressed="${
          filter.category === active
        }">
            ${escapeHtml(filter.category === "All" ? "All" : CATEGORY_LABELS[filter.category] || filter.category.replace("Shop - ", ""))}
            <span>${escapeHtml(filter.total)}</span>
          </button>
        `
      )
      .join("");

    const updateUrlState = () => {
      const next = new URLSearchParams();
      if (active !== "All") next.set("category", normalizeKey(CATEGORY_LABELS[active] || active));
      if (sortMode !== "category-name") next.set("sort", sortMode);
      if (query) next.set("q", query);
      const nextQuery = next.toString();
      const hash = window.location.hash === "#product-filters" ? "#product-filters" : "";
      window.history.replaceState(null, "", `${window.location.pathname}${nextQuery ? `?${nextQuery}` : ""}${hash}`);
    };

    const scrollProductFiltersIntoView = (behavior = "auto") => {
      const target = $("#product-filters") || filterList;
      const header = document.querySelector("[data-sticky-header]");
      const offset = (header?.getBoundingClientRect().height || 0) + 12;
      const top = Math.max(0, target.getBoundingClientRect().top + window.scrollY - offset);
      window.scrollTo({ top, behavior });
    };

    const productMatches = (product) => {
      const haystack = [product.title, product.body, product.excerpt, product.categoryLabel].join(" ").toLowerCase();
      return haystack.includes(query.toLowerCase());
    };

    const sortProducts = (products) => {
      return [...products].sort((a, b) => {
        if (sortMode === "name-asc") return a.title.localeCompare(b.title);
        if (sortMode === "price-asc") return parsePrice(a.price) - parsePrice(b.price) || a.title.localeCompare(b.title);
        if (sortMode === "price-desc") return parsePrice(b.price) - parsePrice(a.price) || a.title.localeCompare(b.title);
        if (sortMode === "stock-first") return a.title.localeCompare(b.title);
        return categoryRank(a) - categoryRank(b) || a.title.localeCompare(b.title);
      });
    };

    const render = () => {
      const products = sortProducts(
        scopedProducts.filter((item) => (active === "All" || item.category === active) && productMatches(item))
      );
      if (count) {
        count.textContent = `Showing ${products.length} of ${scopedProducts.length} products`;
      }
      if (clear) clear.hidden = active === "All" && !query && sortMode === "category-name";
      grid.innerHTML = products.length
        ? products
        .map(
          (product) => {
            const dimensions = productImageDimensions(product);
            return `
            <a class="product-card hover-lift is-visible" data-category="${escapeHtml(normalizeKey(product.category))}" data-image-width="${dimensions.width}" data-image-height="${dimensions.height}" href="${escapeHtml(rebuildPath(product.destinationPath))}">
              <img src="${escapeHtml(assetPath(product.image))}" alt="${escapeHtml(product.title)}" loading="lazy" />
              <div>
                <span>${escapeHtml(CATEGORY_LABELS[product.category] || product.categoryLabel)}</span>
                <h3>${escapeHtml(product.title)}</h3>
                <p>${escapeHtml(product.excerpt)}</p>
                <div class="card-meta">
                  <strong>${escapeHtml(product.price)}</strong>
                  <span class="details-link">Details</span>
                </div>
              </div>
            </a>
          `;
          }
        )
        .join("")
        : `<article class="product-card is-visible"><div><span>No matches</span><h3>No products match these filters.</h3><p>Clear filters to return to the full catalog.</p><button class="button secondary" type="button" data-clear-empty>Clear filters</button></div></article>`;
      fitProductCardImages(grid);
      refreshLayout();
    };

    filterList.addEventListener("click", (event) => {
      const button = event.target.closest("[data-product-filter]");
      if (!button) return;
      active = button.dataset.productFilter;
      filterList.querySelectorAll("button").forEach((item) => {
        item.setAttribute("aria-pressed", String(item === button));
      });
      updateUrlState();
      render();
    });
    search?.addEventListener("input", () => {
      query = search.value.trim();
      updateUrlState();
      render();
    });
    sort?.addEventListener("change", () => {
      sortMode = sort.value;
      updateUrlState();
      render();
    });
    clear?.addEventListener("click", () => {
      active = "All";
      query = "";
      sortMode = "category-name";
      if (search) search.value = "";
      if (sort) sort.value = sortMode;
      filterList.querySelectorAll("button").forEach((item) => {
        item.setAttribute("aria-pressed", String(item.dataset.productFilter === "All"));
      });
      updateUrlState();
      render();
    });
    grid.addEventListener("click", (event) => {
      if (!event.target.closest("[data-clear-empty]")) return;
      clear?.click();
    });

    render();
    if (shouldLandAtFilters) {
      window.requestAnimationFrame(() => scrollProductFiltersIntoView("auto"));
      window.setTimeout(() => scrollProductFiltersIntoView("auto"), 120);
    }
  }

  function setupGuides() {
    const filterList = $("#guide-filter-list");
    const grid = $("#guide-library-grid");
    const count = $("#guide-count");
    if (!grid) return;
    const previewLimit = Number(grid.dataset.guideLimit || 0);
    const previewMode = previewLimit > 0;

    const categoryCounts = data.guides.reduce((acc, guide) => {
      acc.set(guide.category, (acc.get(guide.category) || 0) + 1);
      return acc;
    }, new Map());
    const filters = [{ label: "All Guides", value: "All", total: data.guides.length }];
    categoryCounts.forEach((total, category) => filters.push({ label: category, value: category, total }));
    let active = "All";
    let expanded = !isMobileLayout();
    const expandButton = previewMode ? null : ensureExpandButton(grid, "guide-expand-toggle");

    if (filterList) {
      filterList.innerHTML = filters
        .map(
          (filter) => `
          <button type="button" data-guide-filter="${escapeHtml(filter.value)}" aria-pressed="${filter.value === active}">
            ${escapeHtml(filter.label)}
            <span>${escapeHtml(filter.total)}</span>
          </button>
        `
        )
        .join("");
    }

    const render = () => {
      const guides = active === "All" ? data.guides : data.guides.filter((guide) => guide.category === active);
      const compact = isMobileLayout() && !expanded;
      const visibleGuides = previewMode ? guides.slice(0, previewLimit) : compact ? guides.slice(0, GUIDE_MOBILE_LIMIT) : guides;
      if (count) {
        count.textContent = previewMode
          ? `Latest ${visibleGuides.length} posts`
          : visibleGuides.length === guides.length
          ? `${guides.length} guide ${guides.length === 1 ? "record" : "records"} shown`
          : `${visibleGuides.length} of ${guides.length} guide records shown`;
      }
      if (expandButton) {
        expandButton.hidden = !isMobileLayout() || guides.length <= GUIDE_MOBILE_LIMIT;
        expandButton.textContent = expanded ? "Show fewer guides" : `Show all ${guides.length} guide records`;
        expandButton.setAttribute("aria-expanded", String(expanded));
      }
      grid.innerHTML = visibleGuides
        .map(
          (guide) => `
            <a class="guide-card hover-lift is-visible" href="${escapeHtml(rebuildPath(guide.destinationPath))}">
              <img src="${escapeHtml(assetPath(guide.image))}" alt="${escapeHtml(guide.title)}" loading="lazy" />
              <div>
                <span>${escapeHtml(guide.category)}</span>
                <h3>${escapeHtml(guide.title)}</h3>
                <p>${escapeHtml(guide.excerpt)}</p>
                <span class="details-link">Read post</span>
              </div>
            </a>
          `
        )
        .join("");
      refreshLayout();
    };

    filterList?.addEventListener("click", (event) => {
      const button = event.target.closest("[data-guide-filter]");
      if (!button) return;
      active = button.dataset.guideFilter;
      expanded = !isMobileLayout();
      filterList.querySelectorAll("button").forEach((item) => {
        item.setAttribute("aria-pressed", String(item === button));
      });
      render();
    });
    expandButton?.addEventListener("click", () => {
      expanded = !expanded;
      render();
    });
    mobileQuery.addEventListener("change", () => {
      expanded = !isMobileLayout();
      render();
    });

    render();
  }

  function renderContactDetails() {
    setHtml(
      "#contact-detail-list",
      `
        <li><strong>Address</strong><span>${escapeHtml(data.contact.address)}</span></li>
        <li><strong>Phone</strong><span>${escapeHtml(data.contact.phone)}</span></li>
        <li><strong>Hours</strong><span>${escapeHtml(data.contact.hours)}</span></li>
        <li><strong>Email</strong><span>${escapeHtml(data.contact.emails.join(" / "))}</span></li>
      `
    );
  }

  function renderVersion() {
    document.querySelectorAll("[data-site-version]").forEach((node) => {
      node.textContent = `v${data.version}`;
    });
  }

  function init() {
    renderVersion();
    renderStats();
    renderArtists();
    renderServiceMatrix();
    renderPiercingPrices();
    setupProducts();
    setupGuides();
    renderContactDetails();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
  window.addEventListener("resize", () => fitProductCardImages(document), { passive: true });
})();
