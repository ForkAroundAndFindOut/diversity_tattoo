(() => {
  const root = document.querySelector("[data-motion-root]");
  const reducedMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  const desktopMotionQuery = window.matchMedia("(min-width: 900px)");
  const hasGsap = Boolean(window.gsap && window.ScrollTrigger);

  function splitText() {
    document.querySelectorAll("[data-split]").forEach((node) => {
      if (node.dataset.splitReady) return;
      const words = node.textContent.trim().split(/\s+/);
      node.textContent = "";
      words.forEach((word, index) => {
        const span = document.createElement("span");
        span.className = "word";
        span.style.setProperty("--word-index", index);
        span.textContent = word;
        node.appendChild(span);
        if (index < words.length - 1) {
          node.appendChild(document.createTextNode(" "));
        }
      });
      node.dataset.splitReady = "true";
    });
  }

  function setupHeader() {
    const header = document.querySelector("[data-sticky-header]");
    const toggle = document.querySelector(".menu-toggle");
    if (!header) return;
    const update = () => header.classList.toggle("is-stuck", window.scrollY > 18);
    const closeMenu = () => {
      header.classList.remove("nav-open");
      toggle?.setAttribute("aria-expanded", "false");
      document.body.classList.remove("nav-lock");
    };
    update();
    window.addEventListener("scroll", update, { passive: true });
    if (toggle) {
      toggle.addEventListener("click", () => {
        const open = header.classList.toggle("nav-open");
        toggle.setAttribute("aria-expanded", String(open));
        document.body.classList.toggle("nav-lock", open);
      });
    }
    header.querySelectorAll(".site-nav a").forEach((link) => {
      link.addEventListener("click", closeMenu);
    });
    window.addEventListener("resize", () => {
      if (window.innerWidth > 980) closeMenu();
    });
  }

  function setupRevealFallback() {
    const revealNodes = [
      ...document.querySelectorAll("[data-reveal]"),
      ...document.querySelectorAll("[data-split]"),
      ...document.querySelectorAll("[data-stagger] > *")
    ];
    const revealVisibleNodes = () => {
      const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0;
      revealNodes.forEach((node) => {
        if (node.classList.contains("is-visible")) return;
        const rect = node.getBoundingClientRect();
        if (rect.top < viewportHeight * 0.94 && rect.bottom > 0) {
          node.classList.add("is-visible");
        }
      });
    };
    if (!("IntersectionObserver" in window)) {
      revealNodes.forEach((node) => node.classList.add("is-visible"));
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.16, rootMargin: "0px 0px -8% 0px" }
    );
    revealNodes.forEach((node) => observer.observe(node));
    revealVisibleNodes();
    window.setTimeout(revealVisibleNodes, 120);
    window.addEventListener("hashchange", () => window.setTimeout(revealVisibleNodes, 80));
  }

  function setupParallaxFallback() {
    const layers = [...document.querySelectorAll("[data-parallax-layer]")];
    const tracks = [...document.querySelectorAll("[data-horizontal-track]")];
    let frame = 0;

    const update = () => {
      frame = 0;
      const viewportHeight = window.innerHeight || 1;
      layers.forEach((layer) => {
        const scene = layer.closest("[data-parallax-scene]") || layer;
        const rect = scene.getBoundingClientRect();
        const depth = Number(layer.dataset.depth || 1);
        const progress = Math.min(1, Math.max(0, (viewportHeight - rect.top) / (viewportHeight + rect.height)));
        const y = (progress - 0.5) * 54 * depth;
        layer.style.transform = `translate3d(0, ${y.toFixed(2)}px, 0)`;
      });

      tracks.forEach((track) => {
        if (!desktopMotionQuery.matches) {
          track.style.transform = "none";
          return;
        }
        const scene = track.closest("[data-horizontal-scene]");
        if (!scene) return;
        const rect = scene.getBoundingClientRect();
        const progress = Math.min(1, Math.max(0, (viewportHeight - rect.top) / (viewportHeight + rect.height)));
        const maxShift = Math.max(0, track.scrollWidth - scene.clientWidth + 56);
        track.style.transform = `translate3d(${-maxShift * progress}px, 0, 0)`;
      });
    };

    const schedule = () => {
      if (frame) return;
      frame = window.requestAnimationFrame(update);
    };

    update();
    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule);
  }

  function forceRevealInViewport() {
    const revealNodes = [
      ...document.querySelectorAll("[data-reveal]"),
      ...document.querySelectorAll("[data-split]"),
      ...document.querySelectorAll("[data-stagger] > *")
    ];
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0;
    revealNodes.forEach((node) => {
      const rect = node.getBoundingClientRect();
      if (rect.top >= viewportHeight * 0.94 || rect.bottom <= 0) return;
      node.classList.add("is-visible");
      if (window.gsap) {
        window.gsap.set(node, { autoAlpha: 1, x: 0, y: 0 });
        if (node.matches("[data-split]")) {
          window.gsap.set(node.querySelectorAll(".word"), { autoAlpha: 1, y: 0 });
        }
      }
    });
  }

  function setupGsapMotion() {
    window.gsap.registerPlugin(window.ScrollTrigger);
    const gsap = window.gsap;
    const ScrollTrigger = window.ScrollTrigger;

    gsap.utils.toArray("[data-reveal]").forEach((element) => {
      const direction = element.dataset.reveal || "up";
      const x = direction === "left" ? -36 : direction === "right" ? 36 : 0;
      const y = direction === "down" ? -28 : direction === "none" ? 0 : 28;
      gsap.fromTo(
        element,
        { autoAlpha: 0, x, y },
        {
          autoAlpha: 1,
          x: 0,
          y: 0,
          duration: 0.76,
          ease: "power3.out",
          scrollTrigger: { trigger: element, start: "top 84%", once: true }
        }
      );
    });

    gsap.utils.toArray("[data-stagger]").forEach((container) => {
      gsap.fromTo(
        container.children,
        { autoAlpha: 0, y: 24 },
        {
          autoAlpha: 1,
          y: 0,
          duration: 0.72,
          stagger: 0.09,
          ease: "power3.out",
          scrollTrigger: { trigger: container, start: "top 82%", once: true }
        }
      );
    });

    gsap.utils.toArray("[data-split]").forEach((node) => {
      const words = node.querySelectorAll(".word");
      if (!desktopMotionQuery.matches) {
        gsap.set(words, { autoAlpha: 1, y: 0 });
        return;
      }
      gsap.fromTo(
        words,
        { autoAlpha: 0, y: 24 },
        {
          autoAlpha: 1,
          y: 0,
          duration: 0.72,
          stagger: 0.045,
          ease: "power3.out",
          scrollTrigger: { trigger: node, start: "top 84%", once: true }
        }
      );
    });

    gsap.utils.toArray("[data-parallax-layer]").forEach((layer) => {
      const scene = layer.closest("[data-parallax-scene]") || layer;
      const depth = Number(layer.dataset.depth || 1);
      gsap.to(layer, {
        y: 52 * depth,
        ease: "none",
        scrollTrigger: { trigger: scene, start: "top bottom", end: "bottom top", scrub: true }
      });
    });

    if (desktopMotionQuery.matches) {
      gsap.utils.toArray("[data-pin-scene]").forEach((scene) => {
        const target = scene.querySelector("[data-pin-target]") || scene;
        ScrollTrigger.create({
          trigger: scene,
          start: "top top+=96",
          end: "bottom center",
          pin: target,
          pinSpacing: false
        });
      });
    }

    if (desktopMotionQuery.matches) {
      gsap.utils.toArray("[data-horizontal-scene]").forEach((scene) => {
        const track = scene.querySelector("[data-horizontal-track]");
        if (!track) return;
        gsap.to(track, {
          x: () => -Math.max(0, track.scrollWidth - scene.clientWidth + 56),
          ease: "none",
          scrollTrigger: { trigger: scene, start: "top 72%", end: "bottom top", scrub: true, invalidateOnRefresh: true }
        });
      });
    } else {
      gsap.utils.toArray("[data-horizontal-track]").forEach((track) => window.gsap.set(track, { clearProps: "transform" }));
    }
  }

  function getHashTarget() {
    const id = decodeURIComponent(window.location.hash.replace(/^#/, ""));
    if (!id) return null;
    return document.getElementById(id);
  }

  function scrollToHashTarget() {
    const target = getHashTarget();
    if (!target) return;
    const header = document.querySelector("[data-sticky-header]");
    const offset = header ? header.getBoundingClientRect().height + 14 : 0;
    const top = Math.max(0, target.getBoundingClientRect().top + window.scrollY - offset);
    window.scrollTo({ top, behavior: "auto" });
    window.setTimeout(forceRevealInViewport, 80);
  }

  function setupAnchorNavigation() {
    if (window.location.hash) {
      window.setTimeout(scrollToHashTarget, 80);
      window.setTimeout(scrollToHashTarget, 520);
    }
    window.addEventListener("hashchange", () => {
      window.setTimeout(scrollToHashTarget, 80);
    });
    window.addEventListener("diversity:content-updated", () => {
      window.ScrollTrigger?.refresh?.();
      forceRevealInViewport();
    });
  }

  function setupTabs() {
    document.querySelectorAll("[data-tabs]").forEach((tabs) => {
      const buttons = [...tabs.querySelectorAll('[role="tab"]')];
      const panels = [...tabs.querySelectorAll('[role="tabpanel"]')];
      buttons.forEach((button, index) => {
        button.addEventListener("click", () => {
          buttons.forEach((item, itemIndex) => item.setAttribute("aria-selected", String(itemIndex === index)));
          panels.forEach((panel, itemIndex) => {
            panel.hidden = itemIndex !== index;
            panel.classList.toggle("is-active", itemIndex === index);
          });
        });
      });
    });
  }

  function setupAccordion() {
    document.querySelectorAll("[data-accordion] article").forEach((item) => {
      const button = item.querySelector("button");
      const panel = item.querySelector(".accordion-panel");
      if (!button || !panel) return;
      button.addEventListener("click", () => {
        const open = button.getAttribute("aria-expanded") === "true";
        button.setAttribute("aria-expanded", String(!open));
        panel.hidden = open;
      });
    });
  }

  function setupSlider() {
    document.querySelectorAll("[data-slider]").forEach((slider) => {
      const slides = [...slider.querySelectorAll(".slide")];
      const prev = slider.querySelector("[data-slider-prev]");
      const next = slider.querySelector("[data-slider-next]");
      const status = slider.querySelector("[data-slider-status]");
      let active = 0;

      const render = () => {
        slides.forEach((slide, index) => slide.classList.toggle("is-active", index === active));
        if (status) status.textContent = `${active + 1} / ${slides.length}`;
      };

      prev?.addEventListener("click", () => {
        active = (active - 1 + slides.length) % slides.length;
        render();
      });
      next?.addEventListener("click", () => {
        active = (active + 1) % slides.length;
        render();
      });
      render();
    });
  }

  function setupModal() {
    const modal = document.getElementById("contact-modal");
    if (!modal) return;
    const openers = document.querySelectorAll('[data-modal-open="contact-modal"]');
    const closers = modal.querySelectorAll("[data-modal-close]");
    let lastFocus = null;

    const open = () => {
      lastFocus = document.activeElement;
      modal.hidden = false;
      window.requestAnimationFrame(() => modal.classList.add("is-open"));
      modal.querySelector(".modal-close")?.focus();
      document.body.style.overflow = "hidden";
    };

    const close = () => {
      modal.classList.remove("is-open");
      window.setTimeout(() => {
        modal.hidden = true;
        document.body.style.overflow = "";
        lastFocus?.focus?.();
      }, 220);
    };

    openers.forEach((button) => button.addEventListener("click", open));
    closers.forEach((button) => button.addEventListener("click", close));
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !modal.hidden) close();
    });
  }

  function initMotion() {
    splitText();
    setupHeader();
    setupTabs();
    setupAccordion();
    setupSlider();
    setupModal();

    if (reducedMotionQuery.matches) {
      document.documentElement.classList.add("reduced-motion");
      document.querySelectorAll("[data-reveal], [data-split], [data-stagger] > *").forEach((node) => {
        node.classList.add("is-visible");
      });
      setupAnchorNavigation();
      return;
    }

    if (hasGsap) {
      setupGsapMotion();
    } else {
      setupRevealFallback();
      setupParallaxFallback();
    }

    forceRevealInViewport();
    window.setTimeout(forceRevealInViewport, 160);
    window.setTimeout(forceRevealInViewport, 520);
    window.addEventListener("hashchange", () => window.setTimeout(forceRevealInViewport, 80));
    let revealFrame = 0;
    const scheduleForceReveal = () => {
      if (revealFrame) return;
      revealFrame = window.requestAnimationFrame(() => {
        revealFrame = 0;
        forceRevealInViewport();
      });
    };
    window.addEventListener("scroll", scheduleForceReveal, { passive: true });
    window.addEventListener("resize", scheduleForceReveal);
    setupAnchorNavigation();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initMotion);
  } else {
    initMotion();
  }
})();
