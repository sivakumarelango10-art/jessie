(() => {
  "use strict";
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const ease = (t) => 1 - Math.pow(1 - t, 4);

  /* ---------- Header: hide on scroll down, show on scroll up ---------- */
  const header = $(".site-header");
  let lastY = window.scrollY;
  let menuOpen = false;
  window.addEventListener("scroll", () => {
    const y = window.scrollY;
    if (!menuOpen) header.classList.toggle("hide", y > 480 && y > lastY + 4);
    if (y < lastY - 4 || y < 480) header.classList.remove("hide");
    lastY = y;
  }, { passive: true });

  /* ---------- Active section in nav ---------- */
  const navLinks = $$(".nav-links a");
  const dot = $(".nav-dot");
  const moveDot = (link) => {
    if (!dot) return;
    if (!link) { dot.style.opacity = "0"; return; }
    const parent = link.parentElement.getBoundingClientRect();
    const r = link.getBoundingClientRect();
    dot.style.transform = `translateX(${r.left - parent.left + r.width / 2 - 3}px)`;
    dot.style.opacity = "1";
  };
  const setActive = (id) => {
    let current = null;
    navLinks.forEach((a) => {
      const on = a.getAttribute("href") === "#" + id;
      a.setAttribute("aria-current", on ? "true" : "false");
      if (on) current = a;
    });
    moveDot(current);
  };
  const sections = $$("main section[id]");
  if ("IntersectionObserver" in window) {
    const so = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) setActive(e.target.id); });
    }, { rootMargin: "-45% 0px -50% 0px" });
    sections.forEach((s) => so.observe(s));
  }
  window.addEventListener("resize", () => moveDot($('.nav-links a[aria-current="true"]')));

  /* ---------- Mobile menu ---------- */
  const menuBtn = $(".menu-btn");
  const menu = $("#mobile-menu");
  const setMenu = (open) => {
    menuOpen = open;
    menu.classList.toggle("open", open);
    header.classList.toggle("menu-open", open);
    menuBtn.setAttribute("aria-expanded", String(open));
    menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    menu.setAttribute("aria-hidden", String(!open));
    $$("a", menu).forEach((a) => (a.tabIndex = open ? 0 : -1));
    document.documentElement.style.overflow = open ? "hidden" : "";
    if (open) { header.classList.remove("hide"); setTimeout(() => $("a", menu)?.focus(), 200); }
  };
  if (menuBtn && menu) {
    setMenu(false);
    menuBtn.addEventListener("click", () => setMenu(!menuOpen));
    $$("a", menu).forEach((a) => a.addEventListener("click", () => setMenu(false)));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && menuOpen) { setMenu(false); menuBtn.focus(); }
    });
    window.matchMedia("(min-width: 1081px)").addEventListener("change", (m) => { if (m.matches) setMenu(false); });
  }

  /* ---------- Scroll reveals (only for content below the first screen) ---------- */
  const revealables = $$("[data-reveal]");
  if (!reduceMotion && "IntersectionObserver" in window) {
    const vh = window.innerHeight;
    const ro = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) { e.target.classList.add("revealed"); ro.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    revealables.forEach((el) => {
      if (el.getBoundingClientRect().top > vh * 0.95) {
        el.classList.add("reveal-pending");
        ro.observe(el);
      }
    });
  }

  /* ---------- Research line drawings ---------- */
  const draws = $$(".study-art .draw");
  draws.forEach((p) => {
    try { p.style.setProperty("--len", Math.ceil(p.getTotalLength())); } catch (_) { /* not a geometry element */ }
  });
  if (!reduceMotion && "IntersectionObserver" in window) {
    const vh = window.innerHeight;
    const dob = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        $$(".draw", e.target).forEach((p, i) => setTimeout(() => p.classList.add("drawn"), i * 120));
        dob.unobserve(e.target);
      });
    }, { threshold: 0.3 });
    $$(".study-art").forEach((art) => {
      if (art.getBoundingClientRect().top > vh) {
        $$(".draw", art).forEach((p) => p.classList.add("pending"));
        dob.observe(art);
      }
    });
  }

  /* ---------- Goniometer helpers ---------- */
  // 0 degrees points left (the fixed arm), 180 degrees points right; the arc opens upward.
  const polar = (cx, cy, r, deg) => {
    const t = (deg * Math.PI) / 180;
    return [cx - r * Math.cos(t), cy - r * Math.sin(t)];
  };
  const tween = (from, to, ms, step, done, owner) => {
    const id = owner ? ++owner.id : 0;
    if (reduceMotion || ms === 0) { step(to); done && done(); return; }
    const t0 = performance.now();
    const tick = (now) => {
      if (owner && owner.id !== id) return; // a newer interaction took over
      const k = Math.min(1, (now - t0) / ms);
      step(from + (to - from) * ease(k));
      if (k < 1) requestAnimationFrame(tick); else done && done();
    };
    requestAnimationFrame(tick);
  };

  /* Hero card: the needle sweeps to full knee flexion on load */
  const heroG = $("#hero-gonio");
  if (heroG) {
    const needle = $(".needle", heroG);
    const fill = $(".sweep", heroG);
    const out = $("#hero-deg");
    const cx = 100, cy = 100, r = 84;
    const len = Math.PI * r;
    fill.style.strokeDasharray = `${len} ${len}`;
    const set = (deg) => {
      const [x, y] = polar(cx, cy, r - 6, deg);
      needle.setAttribute("x2", x.toFixed(1));
      needle.setAttribute("y2", y.toFixed(1));
      fill.style.strokeDashoffset = String(len * (1 - deg / 180));
      out.textContent = Math.round(deg) + "°";
    };
    set(0);
    setTimeout(() => tween(0, 135, 2200, set), reduceMotion ? 0 : 900);
  }

  /* Approach: draggable goniometer that walks through the care pathway */
  const dial = $("#dial");
  if (dial && window.STAGES) {
    const svg = $("svg", dial);
    const range = $("#dial-range");
    const arm = $(".arm", svg);
    const knob = $(".knob", svg);
    const fill = $(".arc-fill", svg);
    const text = $(".angle-text", svg);
    const tabs = $$('[role="tab"]', dial.parentElement);
    const panel = $("#stage-panel");
    const cx = 260, cy = 262, r = 200;
    const len = Math.PI * r;
    fill.style.strokeDasharray = `${len} ${len}`;
    let angle = 0;
    let stageIdx = -1;
    let touched = false;
    const motion = { id: 0 };
    const animateTo = (deg, ms) => tween(angle, deg, ms, (d) => set(d), null, motion);

    const renderStage = (i) => {
      if (i === stageIdx) return;
      stageIdx = i;
      const s = window.STAGES[i];
      tabs.forEach((t, k) => {
        t.setAttribute("aria-selected", String(k === i));
        t.tabIndex = k === i ? 0 : -1;
      });
      panel.setAttribute("aria-labelledby", tabs[i].id);
      panel.innerHTML =
        `<div class="swap"><p class="deg-label">${s.angle}° on the dial</p></div>` +
        `<h3 class="swap">${s.title}</h3><p class="swap">${s.text}</p>`;
    };
    const set = (deg, fromRange) => {
      angle = Math.max(0, Math.min(180, deg));
      const [x, y] = polar(cx, cy, r, angle);
      const [kx, ky] = polar(cx, cy, r, angle);
      arm.setAttribute("x2", x.toFixed(1));
      arm.setAttribute("y2", y.toFixed(1));
      knob.setAttribute("cx", kx.toFixed(1));
      knob.setAttribute("cy", ky.toFixed(1));
      fill.style.strokeDashoffset = String(len * (1 - angle / 180));
      text.textContent = Math.round(angle) + "°";
      if (!fromRange) range.value = String(Math.round(angle));
      range.setAttribute("aria-valuetext", `${Math.round(angle)} degrees, ${window.STAGES[Math.round(angle / 45)].title}`);
      renderStage(Math.round(angle / 45));
    };
    set(0);

    range.addEventListener("input", () => { touched = true; motion.id++; set(Number(range.value), true); });
    tabs.forEach((t, i) => {
      t.addEventListener("click", () => { touched = true; animateTo(window.STAGES[i].angle, 700); });
      t.addEventListener("keydown", (e) => {
        const dir = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (!dir) return;
        e.preventDefault();
        const n = (i + dir + tabs.length) % tabs.length;
        tabs[n].focus();
        tabs[n].click();
      });
    });

    const toAngle = (evt) => {
      const pt = svg.createSVGPoint();
      pt.x = evt.clientX; pt.y = evt.clientY;
      const p = pt.matrixTransform(svg.getScreenCTM().inverse());
      let deg = (Math.atan2(cy - p.y, cx - p.x) * 180) / Math.PI;
      if (deg < 0) deg = p.x < cx ? 0 : 180;
      return deg;
    };
    let dragging = false;
    svg.addEventListener("pointerdown", (e) => {
      dragging = true; touched = true;
      svg.setPointerCapture(e.pointerId);
      animateTo(toAngle(e), 260);
    });
    svg.addEventListener("pointermove", (e) => { if (dragging) { motion.id++; set(toAngle(e)); } });
    const stop = () => { dragging = false; };
    svg.addEventListener("pointerup", stop);
    svg.addEventListener("pointercancel", stop);

    // A gentle demonstration sweep the first time the dial comes into view.
    if (!reduceMotion && "IntersectionObserver" in window) {
      const io = new IntersectionObserver((entries) => {
        if (!entries[0].isIntersecting) return;
        io.disconnect();
        if (!touched && angle === 0) animateTo(90, 1600);
      }, { threshold: 0.6 });
      io.observe(svg);
    }
  }

  /* ---------- Copy buttons ---------- */
  const toast = $(".toast");
  let toastTimer;
  const say = (msg) => {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 2200);
  };
  const selectText = (el) => {
    const range = document.createRange();
    range.selectNodeContents(el);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
  };
  $$("[data-copy]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const value = btn.getAttribute("data-copy");
      const target = document.getElementById(btn.getAttribute("data-target"));
      const fallback = () => { if (target) selectText(target); say("Selected. Press Ctrl+C or ⌘C to copy"); };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(value).then(() => say("Copied " + value), fallback);
      } else {
        fallback();
      }
    });
  });

  /* ---------- Footer year ---------- */
  const yr = $("#year");
  if (yr) yr.textContent = String(new Date().getFullYear());
})();
