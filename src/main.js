(() => {
  "use strict";
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  const ease = (t) => 1 - Math.pow(1 - t, 4);
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, k) => a + (b - a) * k;
  const hasIO = "IntersectionObserver" in window;
  const root = document.documentElement;
  let menuOpen = false;

  /* =====================================================================================
     One scroll loop for everything. Positions are measured once (and again on resize /
     when content height changes), never during scrolling, so scrolling triggers no layout.
     ===================================================================================== */
  const scrollers = [];   // fn(y, vh, dt) run once per frame while scrolling or settling
  const measurers = [];   // fn() re-read positions; run on load, resize, content-size change
  let scrollY = window.scrollY, vh = window.innerHeight, ticking = false, lastFrame = performance.now();
  const docTop = (el) => { let y = 0; for (let n = el; n; n = n.offsetParent) y += n.offsetTop; return y; };
  const frame = (now) => {
    ticking = false;
    const dt = Math.min(64, now - lastFrame); lastFrame = now;
    scrollY = window.scrollY;
    for (const fn of scrollers) fn(scrollY, vh, dt);
  };
  const requestFrame = () => { if (!ticking) { ticking = true; requestAnimationFrame(frame); } };
  const measureAll = () => { vh = window.innerHeight; for (const fn of measurers) fn(); requestFrame(); };
  window.addEventListener("scroll", requestFrame, { passive: true });
  let resizeT;
  window.addEventListener("resize", () => { clearTimeout(resizeT); resizeT = setTimeout(measureAll, 120); });
  if ("ResizeObserver" in window) { let first = true; new ResizeObserver(() => { if (first) { first = false; return; } clearTimeout(resizeT); resizeT = setTimeout(measureAll, 120); }).observe(document.body); }

  /* ---------- Header: capsule fills in after scrolling, hides on the way down ---------- */
  const header = $(".site-header");
  let lastY = scrollY;
  scrollers.push((y) => {
    header.classList.toggle("scrolled", y > 24);
    if (!menuOpen) header.classList.toggle("hide", y > 560 && y > lastY + 4);
    if (y < lastY - 4 || y < 560) header.classList.remove("hide");
    lastY = y;
  });

  const steps = [];   // setup work, run in small chunks so no single task blocks input

  /* ---------- Active section: a blue pill slides behind the current link ---------- */
  steps.push(() => {
    const navLinks = $$(".nav-links a");
    const pill = $(".nav-pill");
    const movePill = (link) => {
      if (!pill) return;
      if (!link) { pill.style.opacity = "0"; return; }
      pill.style.width = link.offsetWidth + "px";
      pill.style.transform = `translateX(${link.offsetLeft}px)`;
      pill.style.opacity = "1";
    };
    const setActive = (id) => {
      let current = null;
      navLinks.forEach((a) => { const on = a.getAttribute("href") === "#" + id; a.setAttribute("aria-current", on ? "true" : "false"); if (on) current = a; });
      movePill(current);
    };
    if (hasIO) {
      const so = new IntersectionObserver((entries) => {
        entries.forEach((en) => { if (en.isIntersecting) setActive(en.target.id === "top" ? "" : en.target.id); });
      }, { rootMargin: "-45% 0px -50% 0px" });
      $$("main section[id]").forEach((s) => so.observe(s));
    }
    measurers.push(() => movePill($('.nav-links a[aria-current="true"]')));
  });

  /* ---------- Mobile menu: bottom sheet ---------- */
  steps.push(() => {
    const menuBtn = $(".menu-btn"), menu = $("#mobile-menu"), scrim = $(".scrim");
    if (!menuBtn || !menu) return;
    const setMenu = (open) => {
      menuOpen = open;
      menu.classList.toggle("open", open);
      scrim.classList.toggle("open", open);
      menuBtn.setAttribute("aria-expanded", String(open));
      menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      menu.setAttribute("aria-hidden", String(!open));
      $$("a", menu).forEach((a) => (a.tabIndex = open ? 0 : -1));
      root.style.overflow = open ? "hidden" : "";
      if (open) { header.classList.remove("hide"); setTimeout(() => $("a", menu)?.focus({ preventScroll: true }), 250); }
    };
    setMenu(false);
    menuBtn.addEventListener("click", () => setMenu(!menuOpen));
    scrim.addEventListener("click", () => setMenu(false));
    $$("a", menu).forEach((a) => a.addEventListener("click", () => setMenu(false)));
    document.addEventListener("keydown", (ev) => { if (ev.key === "Escape" && menuOpen) { setMenu(false); menuBtn.focus(); } });
    window.matchMedia("(min-width: 1220px)").addEventListener("change", (m) => { if (m.matches) setMenu(false); });
  });

  /* ---------- Reveals: headings rise word by word, groups stagger their children ---------- */
  const onEnter = (els, fn, opts = { rootMargin: "0px 0px -8% 0px", threshold: 0.05 }) => {
    if (!hasIO || !els.length) { els.forEach(fn); return; }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { fn(en.target); io.unobserve(en.target); } });
    }, opts);
    els.forEach((el) => io.observe(el));
  };
  steps.push(() => {
    $$("[data-stagger]").forEach((g) => Array.from(g.children).forEach((c, i) => c.style.setProperty("--si", i)));
    if (reduceMotion) return;
    // read every position first, then write: one layout, no thrashing
    const all = $$("[data-reveal]");
    const tops = all.map((el) => el.getBoundingClientRect().top);
    const pend = all.filter((el, i) => tops[i] > vh * 0.95);
    pend.forEach((el) => el.classList.add("reveal-pending"));
    onEnter(pend, (el) => el.classList.add("revealed"));

    const strips = $$(".cert .strip"), sTops = strips.map((s) => s.getBoundingClientRect().top);
    const sp = strips.filter((s, i) => sTops[i] > vh * 0.95);
    sp.forEach((el) => el.classList.add("pending"));
    onEnter(sp, (el) => setTimeout(() => el.classList.add("stuck"), 250), { threshold: 0.6 });

    const mark = $(".contact h2 .mark");
    if (mark && mark.getBoundingClientRect().top > vh * 0.95) { mark.classList.add("pending"); onEnter([mark], (m) => m.classList.add("stuck"), { threshold: 0.8 }); }
  });

  /* ---------- Research line drawings ---------- */
  steps.push(() => {
    const draws = $$(".study-art .draw");
    const lens = draws.map((p) => { try { return Math.ceil(p.getTotalLength()); } catch (_) { return 0; } });
    draws.forEach((p, i) => p.style.setProperty("--len", lens[i]));
    if (reduceMotion) return;
    const arts = $$(".study-art"), aTops = arts.map((a) => a.getBoundingClientRect().top);
    const pend = arts.filter((a, i) => aTops[i] > vh);
    pend.forEach((a) => $$(".draw", a).forEach((p) => p.classList.add("pending")));
    onEnter(pend, (a) => $$(".draw", a).forEach((p, i) => setTimeout(() => p.classList.add("drawn"), i * 140)), { threshold: 0.3 });
  });

  /* ---------- Scroll-linked timeline rails ---------- */
  steps.push(() => {
    const rails = $$("#timeline, #schools").map((wrap) => ({ wrap, fill: $(".rail i", wrap), items: $$(".job, .school", wrap), top: 0, h: 1, tops: [], lit: [] }));
    if (!rails.length) return;
    measurers.push(() => rails.forEach((r) => { r.top = docTop(r.wrap); r.h = r.wrap.offsetHeight || 1; r.tops = r.items.map(docTop); }));
    scrollers.push((y, h) => {
      const line = y + h * 0.62;
      rails.forEach((r) => {
        const p = clamp((line - r.top) / r.h, 0, 1);
        if (r.p === undefined || Math.abs(r.p - p) > 0.002 || (p === 1) !== (r.p === 1)) { r.p = p; r.fill.style.setProperty("--p", p.toFixed(3)); }
        r.items.forEach((it, i) => { const on = r.tops[i] < line; if (r.lit[i] !== on) { r.lit[i] = on; it.classList.toggle("lit", on); } });
      });
    });
  });

  /* ---------- Gait analysis: illustrative walking model drawn on canvas ---------- */
  const revealed = new Promise((res) => {
    if (!document.getElementById("loader")) res();
    else window.addEventListener("portfolio:revealed", res, { once: true });
  });
  steps.push(() => {
    const gauss = (c, mu, sd) => { let d = Math.abs(c - mu); d = Math.min(d, 1 - d); return Math.exp(-(d * d) / (2 * sd * sd)); };
    const angles = (c) => ({
      hip: 10 + 20 * Math.cos(2 * Math.PI * c),
      knee: 5 + 13 * gauss(c, 0.13, 0.06) + 57 * gauss(c, 0.72, 0.1),
      ankle: 9 * Math.sin(2 * Math.PI * (c - 0.12)) - 10 * gauss(c, 0.62, 0.06),
    });
    const css = (el, name) => getComputedStyle(el).getPropertyValue(name).trim();
    const makeGait = (canvas) => {
      const mini = canvas.dataset.gait === "mini";
      const host = canvas.closest(".gait-panel, .gait-card");
      const onDark = !!canvas.closest(".gait-panel");
      const outs = host ? $$("[data-readout]", host) : [];
      const ctx = canvas.getContext("2d");
      const minFrame = mini ? 1000 / 30 : 0;   // the small card is fine at 30 fps
      let w = 0, h = 0, dpr = 1;
      const trail = [];
      const size = () => {
        dpr = Math.min(window.devicePixelRatio || 1, mini ? 1.5 : 2);
        w = canvas.clientWidth; h = canvas.clientHeight;
        canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
        trail.length = 0;
      };
      const colors = () => ({
        ink: css(canvas, onDark ? "--on-dark" : "--ink"), muted: css(canvas, onDark ? "--on-dark-muted" : "--muted"),
        blue: css(canvas, "--blue"), coral: css(canvas, "--coral"), bg: css(canvas, onDark ? "--dark" : "--surface"),
      });
      let col = colors();
      const rad = (d) => (d * Math.PI) / 180;
      const leg = (hip, a, L) => {
        const th = rad(a.hip), sh = rad(a.hip - a.knee);
        const knee = [hip[0] + L.t * Math.sin(th), hip[1] + L.t * Math.cos(th)];
        const ank = [knee[0] + L.s * Math.sin(sh), knee[1] + L.s * Math.cos(sh)];
        const fa = rad(a.ankle) - sh * 0.35;
        return { hip, knee, ank, toe: [ank[0] + L.f * Math.cos(fa), ank[1] + L.f * Math.sin(fa)] };
      };
      const line = (pts, color, width) => {
        ctx.strokeStyle = color; ctx.lineWidth = width; ctx.lineCap = "round"; ctx.lineJoin = "round";
        ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]);
        for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
        ctx.stroke();
      };
      const dot = (p, r, fill, stroke) => {
        ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, Math.PI * 2);
        if (fill) { ctx.fillStyle = fill; ctx.fill(); }
        if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = Math.max(1.5, r * 0.4); ctx.stroke(); }
      };
      let count = 0;
      const last = {};
      const draw = (c) => {
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        ctx.clearRect(0, 0, w, h);
        const unit = Math.min(h / (mini ? 1.95 : 2.6), w / (mini ? 3 : 2.1));
        const L = { t: unit * 0.47, s: unit * 0.45, f: unit * 0.15, torso: unit * 0.68, arm: unit * 0.33, fore: unit * 0.29, head: unit * 0.1 };
        const ground = h - (mini ? 10 : unit * 0.22);
        const cx = mini ? w * 0.36 : w * 0.46;
        const near = angles(c), far = angles((c + 0.5) % 1);
        const hip = [cx, ground - (L.t + L.s) * 0.97 + unit * 0.025 * Math.cos(4 * Math.PI * c)];
        ctx.strokeStyle = col.muted; ctx.globalAlpha = 0.5; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(0, ground + 2); ctx.lineTo(w, ground + 2); ctx.stroke();
        const step = mini ? 18 : 26, off = ((c * step * 4) % step);
        for (let x = -off; x < w; x += step) { ctx.beginPath(); ctx.moveTo(x, ground + 6); ctx.lineTo(x - 5, ground + 11); ctx.stroke(); }
        ctx.globalAlpha = 1;
        const lf = leg(hip, far, L), ln = leg(hip, near, L);
        const lean = rad(4);
        const sh = [hip[0] + L.torso * Math.sin(lean), hip[1] - L.torso * Math.cos(lean)];
        const head = [sh[0] + L.head * 0.5, sh[1] - L.head * 2.3], neck = [sh[0] + L.head * 0.25, sh[1] - L.head * 1.2];
        const arm = (a) => {
          const ang = rad(-0.7 * a.hip + 6), el = [sh[0] + L.arm * Math.sin(ang), sh[1] + L.arm * Math.cos(ang)];
          const fang = ang + rad(18 + 10 * Math.sin(rad(a.hip) * 2));
          return [sh, el, [el[0] + L.fore * Math.sin(fang), el[1] + L.fore * Math.cos(fang)]];
        };
        const lw = mini ? 3.4 : 5;
        ctx.globalAlpha = 0.45;
        line(arm(near), col.muted, lw * 0.8);
        line([lf.hip, lf.knee, lf.ank, lf.toe], col.muted, lw);
        ctx.globalAlpha = 1;
        trail.push([ln.ank[0], ln.ank[1]]);
        if (trail.length > (mini ? 22 : 70)) trail.shift();
        for (let i = 1; i < trail.length; i++) { ctx.globalAlpha = (i / trail.length) * 0.9; line([trail[i - 1], trail[i]], col.coral, mini ? 1.5 : 2); }
        ctx.globalAlpha = 1;
        line([hip, sh, neck], col.ink, lw);
        dot(head, L.head, null, col.ink);
        line([ln.hip, ln.knee, ln.ank, ln.toe], col.ink, lw);
        line(arm(far), col.ink, lw * 0.8);
        const th = Math.atan2(ln.hip[0] - ln.knee[0], ln.hip[1] - ln.knee[1]);
        const sa = Math.atan2(ln.ank[0] - ln.knee[0], ln.ank[1] - ln.knee[1]);
        ctx.strokeStyle = col.blue; ctx.lineWidth = mini ? 1.5 : 2.5;
        ctx.beginPath(); ctx.arc(ln.knee[0], ln.knee[1], unit * 0.14, Math.PI / 2 - th, Math.PI / 2 - sa, true); ctx.stroke();
        const mr = mini ? 3.4 : 5.5;
        [lf.knee, lf.ank].forEach((p) => dot(p, mr * 0.8, col.bg, col.muted));
        [ln.hip, ln.knee, ln.ank, ln.toe, sh].forEach((p) => dot(p, mr, col.blue, col.bg));
        if (outs.length && count++ % 6 === 0) {
          outs.forEach((o) => {   // only touch the DOM when the shown value changes
            const k = o.dataset.readout;
            const txt = (mini ? k[0].toUpperCase() + k.slice(1) + " " : "") + Math.round(k === "hip" ? near.hip : k === "knee" ? near.knee : near.ankle) + "°";
            if (last[k] !== txt) { last[k] = txt; o.textContent = txt; }
          });
        }
      };
      size();
      let running = false, visible = false, raf = 0, t0 = performance.now(), cPaused = 0.72, lastDraw = 0;
      const loop = (now) => {
        if (!running) return;
        raf = requestAnimationFrame(loop);
        if (now - lastDraw < minFrame - 1) return;
        lastDraw = now;
        cPaused = (((now - t0) / 1150) % 1 + 1) % 1;
        draw(cPaused);
      };
      const start = () => { if (running || reduceMotion || !visible || document.hidden) return; running = true; t0 = performance.now() - cPaused * 1150; raf = requestAnimationFrame(loop); };
      const stop = () => { running = false; cancelAnimationFrame(raf); };
      draw(cPaused);
      if (hasIO && !reduceMotion) {
        new IntersectionObserver((en) => { visible = en[0].isIntersecting; revealed.then(() => (visible ? start() : stop())); }, { threshold: 0.05 }).observe(canvas);
      }
      document.addEventListener("visibilitychange", () => (document.hidden ? stop() : start()));
      measurers.push(() => { if (canvas.clientWidth !== w || canvas.clientHeight !== h) { size(); draw(cPaused); } });
      window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { col = colors(); draw(cPaused); });
      if (reduceMotion) for (let i = 0; i < 70; i++) draw((0.72 + i / 70) % 1);
    };
    $$("canvas[data-gait]").forEach(makeGait);
  });

  /* ---------- Body map ---------- */
  steps.push(() => {
    const cares = $$(".care"), caption = $("#body-caption"), bodyEls = $$(".body-map [data-areas]");
    const showArea = (key) => {
      bodyEls.forEach((el) => el.classList.toggle("on", (el.dataset.areas || "").split(" ").includes(key)));
      const active = cares.find((c) => c.dataset.area === key);
      if (caption && active && caption.textContent !== active.dataset.caption) {
        caption.textContent = active.dataset.caption;
        if (!reduceMotion) { caption.classList.remove("swap"); void caption.offsetWidth; caption.classList.add("swap"); }
      }
    };
    let pinned = cares[0]?.dataset.area;
    cares.forEach((c) => {
      $(".title", c).addEventListener("click", () => {
        pinned = c.dataset.area;
        cares.forEach((o) => { o.classList.toggle("on", o === c); $(".title", o).setAttribute("aria-pressed", String(o === c)); });
        showArea(pinned);
      });
      c.addEventListener("mouseenter", () => showArea(c.dataset.area));
      c.addEventListener("mouseleave", () => showArea(pinned));
    });
    if (pinned) showArea(pinned);
  });

  /* ---------- Goniometer dial ---------- */
  const polar = (cx, cy, r, deg) => { const t = (deg * Math.PI) / 180; return [cx - r * Math.cos(t), cy - r * Math.sin(t)]; };
  const tween = (from, to, ms, step, owner) => {
    const id = owner ? ++owner.id : 0;
    if (reduceMotion || ms === 0) { step(to); return; }
    const t0 = performance.now();
    const tick = (now) => {
      if (owner && owner.id !== id) return;
      const k = Math.min(1, (now - t0) / ms);
      step(from + (to - from) * ease(k));
      if (k < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  steps.push(() => {
    const dial = $("#dial");
    if (!dial || !window.STAGES) return;
    const svg = $("svg", dial), range = $("#dial-range");
    const arm = $(".arm", svg), knob = $(".knob", svg), fill = $(".arc-fill", svg), text = $(".angle-text", svg);
    const tabs = $$('[role="tab"]', dial), panel = $("#stage-panel");
    const cx = 260, cy = 262, r = 200, len = Math.PI * r;
    let angle = 0, stageIdx = 0, touched = false, shownDeg = null;
    const motion = { id: 0 };
    const renderStage = (i) => {
      if (i === stageIdx) return;
      stageIdx = i;
      const s = window.STAGES[i];
      tabs.forEach((t, k) => { t.setAttribute("aria-selected", String(k === i)); t.tabIndex = k === i ? 0 : -1; });
      panel.setAttribute("aria-labelledby", tabs[i].id);
      const stepsHtml = window.STAGES.map((_, k) => `<i class="${k <= i ? "on" : ""}"></i>`).join("");
      panel.innerHTML = `<div class="stage-steps" aria-hidden="true">${stepsHtml}</div>` +
        `<p class="deg-label swap">${s.angle}° on the dial</p><h3 class="swap">${s.title}</h3><p class="swap">${s.text}</p>`;
    };
    const set = (deg, fromRange) => {
      angle = clamp(deg, 0, 180);
      const [x, y] = polar(cx, cy, r, angle);
      arm.setAttribute("x2", x.toFixed(1)); arm.setAttribute("y2", y.toFixed(1));
      knob.setAttribute("cx", x.toFixed(1)); knob.setAttribute("cy", y.toFixed(1));
      fill.style.strokeDashoffset = String(len * (1 - angle / 180));
      const d = Math.round(angle);
      if (d !== shownDeg) {
        shownDeg = d; text.textContent = d + "°";
        if (!fromRange) range.value = String(d);
        range.setAttribute("aria-valuetext", `${d} degrees, ${window.STAGES[Math.round(angle / 45)].title}`);
      }
      renderStage(Math.round(angle / 45));
    };
    const animateTo = (deg, ms) => tween(angle, deg, ms, (v) => set(v), motion);
    set(0);
    range.addEventListener("input", () => { touched = true; motion.id++; set(Number(range.value), true); });
    tabs.forEach((t, i) => {
      t.addEventListener("click", () => { touched = true; animateTo(window.STAGES[i].angle, 750); });
      t.addEventListener("keydown", (ev) => {
        const dir = ev.key === "ArrowRight" ? 1 : ev.key === "ArrowLeft" ? -1 : 0;
        if (!dir) return;
        ev.preventDefault();
        const n = (i + dir + tabs.length) % tabs.length;
        tabs[n].focus(); tabs[n].click();
      });
    });
    const toAngle = (ev) => {
      const pt = svg.createSVGPoint(); pt.x = ev.clientX; pt.y = ev.clientY;
      const p = pt.matrixTransform(svg.getScreenCTM().inverse());
      let deg = (Math.atan2(cy - p.y, cx - p.x) * 180) / Math.PI;
      if (deg < 0) deg = p.x < cx ? 0 : 180;
      return deg;
    };
    let dragging = false;
    svg.addEventListener("pointerdown", (ev) => { dragging = true; touched = true; svg.setPointerCapture(ev.pointerId); animateTo(toAngle(ev), 280); });
    svg.addEventListener("pointermove", (ev) => { if (dragging) { motion.id++; set(toAngle(ev)); } });
    ["pointerup", "pointercancel"].forEach((n) => svg.addEventListener(n, () => { dragging = false; }));
    if (!reduceMotion && hasIO) {
      const io = new IntersectionObserver((en) => {
        if (!en[0].isIntersecting) return;
        io.disconnect();
        if (!touched && angle === 0) animateTo(90, 1700);
      }, { threshold: 0.6 });
      io.observe(svg);
    }
  });

  /* ---------- Copy buttons + toast ---------- */
  steps.push(() => {
    const toast = $(".toast");
    let toastTimer;
    const say = (msg) => {
      if (!toast) return;
      toast.textContent = msg; toast.classList.add("show");
      clearTimeout(toastTimer); toastTimer = setTimeout(() => toast.classList.remove("show"), 2200);
    };
    $$("[data-copy]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const value = btn.getAttribute("data-copy");
        const target = document.getElementById(btn.getAttribute("data-target"));
        const fallback = () => {
          if (target) { const rg = document.createRange(); rg.selectNodeContents(target); const sel = getSelection(); sel.removeAllRanges(); sel.addRange(rg); }
          say("Selected. Press Ctrl+C or ⌘C to copy");
        };
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(value).then(() => say("Copied " + value), fallback);
        else fallback();
      });
    });
    const yr = $("#year");
    if (yr) yr.textContent = String(new Date().getFullYear());
  });

  /* ---------- Back to top: a goniometer ring that fills as you read ---------- */
  steps.push(() => {
    const btn = $(".to-top");
    if (!btn) return;
    const ring = $(".tt-fill", btn), needle = $(".tt-needle", btn), RING = 2 * Math.PI * 22;
    let max = 1, showAt = 600, shown = null, lastP = -1, lastPct = -1;
    measurers.push(() => { max = Math.max(1, root.scrollHeight - vh); const hero = $(".hero"); showAt = hero ? hero.offsetHeight * 0.8 : 600; });
    scrollers.push((y) => {
      const p = clamp(y / max, 0, 1);
      if (Math.abs(p - lastP) > 0.002) {
        lastP = p;
        ring.style.strokeDashoffset = (RING * (1 - p)).toFixed(1);
        needle.style.transform = `rotate(${(p * 360).toFixed(1)}deg)`;
        const pct = Math.round(p * 100);
        if (pct !== lastPct) { lastPct = pct; btn.setAttribute("aria-label", `Back to top (${pct}% read)`); }
      }
      const on = y > showAt;
      if (on !== shown) { shown = on; btn.classList.toggle("show", on); btn.tabIndex = on ? 0 : -1; }
    });
    btn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
      setTimeout(() => $(".brand")?.focus({ preventScroll: true }), reduceMotion ? 0 : 700);
    });
  });

  /* ---------- Motion layer (skipped entirely for reduced motion) ---------- */
  if (!reduceMotion) {
    /* Pause looping CSS animations in sections that are off screen. */
    steps.push(() => {
      if (!hasIO) return;
      const io = new IntersectionObserver((entries) => entries.forEach((en) => en.target.classList.toggle("is-off", !en.isIntersecting)), { rootMargin: "80px 0px" });
      $$(".hero, .tape-band, #expertise, .contact").forEach((s) => io.observe(s));
    });

    /* Tape bands: the drift is a GPU-driven CSS loop; on desktop they also lean with scroll speed,
       updated only while scrolling and while settling back, never when idle. */
    if (finePointer) steps.push(() => {
      const bands = $$(".tape-band .band");
      if (!bands.length) return;
      let prevY = scrollY, vel = 0, skew = 0, settling = 0, live = false;
      if (hasIO) new IntersectionObserver((en) => { live = en.some((e) => e.isIntersecting) || $$(".tape-band").some((tb) => !tb.classList.contains("is-off")); }, { rootMargin: "100px 0px" })
        .observe($(".tape-band"));
      const apply = () => bands.forEach((b) => { b.style.transform = Math.abs(skew) < 0.02 ? "" : `skewX(${(b.classList.contains("b2") ? skew : -skew).toFixed(2)}deg)`; });
      const settle = () => {
        skew = lerp(skew, 0, 0.12); apply();
        settling = Math.abs(skew) > 0.02 ? requestAnimationFrame(settle) : 0;
        if (!settling) { skew = 0; apply(); }
      };
      scrollers.push((y, h, dt) => {
        const v = (y - prevY) / Math.max(dt, 1); prevY = y;
        vel = lerp(vel, clamp(v, -6, 6), 0.25);
        const nearBand = $$(".tape-band").some((tb) => !tb.classList.contains("is-off"));
        if (!nearBand) return;
        skew = clamp(vel * 1.4, -5, 5); apply();
        if (!settling) settling = requestAnimationFrame(settle);
      });
    });

    /* Hero: gentle depth on scroll, and a slight tilt toward the pointer on desktop. */
    steps.push(() => {
      const hero = $(".hero"), visual = $(".hero-visual");
      if (!hero || !visual) return;
      if (!finePointer || !window.matchMedia("(min-width: 961px)").matches) return;   // phones: no parallax or tilt
      let heroH = 800, lastT = null;
      measurers.push(() => { heroH = hero.offsetHeight; });
      scrollers.push((y) => {
        const t = Math.round(Math.min(y, heroH * 1.2) * 0.12);
        if (t !== lastT) { lastT = t; visual.style.translate = `0 ${t}px`; }
      });
      let tx = 0, ty = 0, rx = 0, ry = 0, raf = 0, rect = null;
      const step = () => {
        rx = lerp(rx, tx, 0.1); ry = lerp(ry, ty, 0.1);
        visual.style.transform = `perspective(1100px) rotateX(${rx.toFixed(2)}deg) rotateY(${ry.toFixed(2)}deg)`;
        raf = Math.abs(rx - tx) + Math.abs(ry - ty) > 0.02 ? requestAnimationFrame(step) : 0;
      };
      const kick = () => { if (!raf) raf = requestAnimationFrame(step); };
      hero.addEventListener("pointerenter", () => { rect = visual.getBoundingClientRect(); });
      hero.addEventListener("pointermove", (ev) => {
        if (!rect) rect = visual.getBoundingClientRect();
        tx = clamp(-((ev.clientY - (rect.top + rect.height / 2)) / rect.height) * 6, -5, 5);
        ty = clamp(((ev.clientX - (rect.left + rect.width / 2)) / rect.width) * 6, -5, 5);
        kick();
      });
      hero.addEventListener("pointerleave", () => { tx = 0; ty = 0; rect = null; kick(); });
    });

    /* Cards: a soft spotlight follows the pointer. Buttons lean toward it. */
    if (finePointer) steps.push(() => {
      $$(".spot").forEach((card) => {
        let rect = null;
        card.addEventListener("pointerenter", () => { rect = card.getBoundingClientRect(); });
        card.addEventListener("pointermove", (ev) => {
          if (!rect) rect = card.getBoundingClientRect();
          card.style.setProperty("--mx", (ev.clientX - rect.left).toFixed(0) + "px");
          card.style.setProperty("--my", (ev.clientY - rect.top).toFixed(0) + "px");
        });
        card.addEventListener("pointerleave", () => { rect = null; });
      });
      $$(".btn-resume, .btn.outline, .to-top").forEach((b) => {
        let rect = null;
        b.addEventListener("pointerenter", () => { rect = b.getBoundingClientRect(); });
        b.addEventListener("pointermove", (ev) => {
          if (!rect) rect = b.getBoundingClientRect();
          const dx = (ev.clientX - (rect.left + rect.width / 2)) * 0.16, dy = (ev.clientY - (rect.top + rect.height / 2)) * 0.22;
          b.style.translate = `${clamp(dx, -6, 6).toFixed(1)}px ${clamp(dy, -5, 5).toFixed(1)}px`;
        });
        b.addEventListener("pointerleave", () => { rect = null; b.style.translate = ""; });
      });
    });
  }

  /* ---------- Run setup in small chunks, then report to the loading screen ---------- */
  const yieldToMain = () => (window.scheduler && scheduler.yield ? scheduler.yield() : new Promise((r) => setTimeout(r, 0)));
  (async () => {
    for (const s of steps) {
      try { s(); } catch (err) { console.error(err); }
      await yieldToMain();
    }
    measureAll();
    window.addEventListener("load", measureAll, { once: true });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(measureAll);
    if (window.PortfolioLoader) window.PortfolioLoader.done("init");
  })();
})();
