(() => {
  "use strict";
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const ease = (t) => 1 - Math.pow(1 - t, 4);
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const hasIO = "IntersectionObserver" in window;

  /* ---------- Header: capsule fills in after scrolling, hides on the way down ---------- */
  const header = $(".site-header");
  let lastY = window.scrollY;
  let menuOpen = false;
  const onHeaderScroll = () => {
    const y = window.scrollY;
    header.classList.toggle("scrolled", y > 24);
    if (!menuOpen) header.classList.toggle("hide", y > 560 && y > lastY + 4);
    if (y < lastY - 4 || y < 560) header.classList.remove("hide");
    lastY = y;
  };
  window.addEventListener("scroll", onHeaderScroll, { passive: true });
  onHeaderScroll();

  /* ---------- Active section: a blue pill slides behind the current link ---------- */
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
    navLinks.forEach((a) => {
      const on = a.getAttribute("href") === "#" + id;
      a.setAttribute("aria-current", on ? "true" : "false");
      if (on) current = a;
    });
    movePill(current);
  };
  if (hasIO) {
    const so = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) setActive(en.target.id === "top" ? "" : en.target.id); });
    }, { rootMargin: "-45% 0px -50% 0px" });
    $$("main section[id]").forEach((s) => so.observe(s));
  }
  window.addEventListener("resize", () => movePill($('.nav-links a[aria-current="true"]')));

  /* ---------- Mobile menu: bottom sheet ---------- */
  const menuBtn = $(".menu-btn");
  const menu = $("#mobile-menu");
  const scrim = $(".scrim");
  const setMenu = (open) => {
    menuOpen = open;
    menu.classList.toggle("open", open);
    scrim.classList.toggle("open", open);
    menuBtn.setAttribute("aria-expanded", String(open));
    menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    menu.setAttribute("aria-hidden", String(!open));
    $$("a", menu).forEach((a) => (a.tabIndex = open ? 0 : -1));
    document.documentElement.style.overflow = open ? "hidden" : "";
    if (open) { header.classList.remove("hide"); setTimeout(() => $("a", menu)?.focus({ preventScroll: true }), 250); }
  };
  if (menuBtn && menu) {
    setMenu(false);
    menuBtn.addEventListener("click", () => setMenu(!menuOpen));
    scrim.addEventListener("click", () => setMenu(false));
    $$("a", menu).forEach((a) => a.addEventListener("click", () => setMenu(false)));
    document.addEventListener("keydown", (ev) => { if (ev.key === "Escape" && menuOpen) { setMenu(false); menuBtn.focus(); } });
    window.matchMedia("(min-width: 1101px)").addEventListener("change", (m) => { if (m.matches) setMenu(false); });
  }

  /* ---------- Scroll reveals: only content that starts below the first screen ---------- */
  const below = (el, k = 0.95) => el.getBoundingClientRect().top > window.innerHeight * k;
  const onEnter = (els, cls, fn, opts = { rootMargin: "0px 0px -8% 0px", threshold: 0.05 }) => {
    if (reduceMotion || !hasIO) return;
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { fn ? fn(en.target) : en.target.classList.add(cls); io.unobserve(en.target); } });
    }, opts);
    els.forEach((el) => io.observe(el));
  };
  if (!reduceMotion) {
    const pend = $$("[data-reveal]").filter((el) => below(el));
    pend.forEach((el) => el.classList.add("reveal-pending"));
    onEnter(pend, "revealed");

    const strips = $$(".cert .strip").filter((el) => below(el));
    strips.forEach((el) => el.classList.add("pending"));
    onEnter(strips, null, (el) => setTimeout(() => el.classList.add("stuck"), 250), { threshold: 0.6 });

    const mark = $(".contact h2 .mark");
    if (mark && below(mark)) { mark.classList.add("pending"); onEnter([mark], "stuck", null, { threshold: 0.8 }); }
  }

  /* ---------- Research line drawings ---------- */
  $$(".study-art .draw").forEach((p) => { try { p.style.setProperty("--len", Math.ceil(p.getTotalLength())); } catch (_) { /* skip */ } });
  if (!reduceMotion) {
    const arts = $$(".study-art").filter((a) => below(a, 1));
    arts.forEach((a) => $$(".draw", a).forEach((p) => p.classList.add("pending")));
    onEnter(arts, null, (a) => $$(".draw", a).forEach((p, i) => setTimeout(() => p.classList.add("drawn"), i * 140)), { threshold: 0.3 });
  }

  /* ---------- Scroll-linked timeline rails ---------- */
  const rails = $$("#timeline, #schools").map((wrap) => ({ wrap, fill: $(".rail i", wrap), items: $$(".job, .school", wrap) }));
  let railTick = false;
  const updateRails = () => {
    railTick = false;
    const line = window.innerHeight * 0.62;
    rails.forEach(({ wrap, fill, items }) => {
      const r = wrap.getBoundingClientRect();
      const p = clamp((line - r.top) / r.height, 0, 1);
      fill.style.setProperty("--p", p.toFixed(3));
      items.forEach((it) => it.classList.toggle("lit", it.getBoundingClientRect().top < line));
    });
  };
  if (rails.length) {
    window.addEventListener("scroll", () => { if (!railTick) { railTick = true; requestAnimationFrame(updateRails); } }, { passive: true });
    window.addEventListener("resize", updateRails);
    updateRails();
  }

  /* ---------- Gait analysis: illustrative walking model drawn on canvas ---------- */
  const gauss = (c, mu, sd) => {
    let d = Math.abs(c - mu); d = Math.min(d, 1 - d);
    return Math.exp(-(d * d) / (2 * sd * sd));
  };
  // Joint angles in degrees for a point c (0..1) in the gait cycle, starting at heel strike.
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
    let w = 0, h = 0, dpr = 1;
    const trail = [];
    const size = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.clientWidth; h = canvas.clientHeight;
      canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
      trail.length = 0;
    };
    const colors = () => ({
      ink: css(canvas, onDark ? "--on-dark" : "--ink"),
      muted: css(canvas, onDark ? "--on-dark-muted" : "--muted"),
      blue: css(canvas, "--blue"),
      coral: css(canvas, "--coral"),
      bg: css(canvas, onDark ? "--dark" : "--surface"),
    });
    let col = colors();
    const rad = (d) => (d * Math.PI) / 180;

    const leg = (hip, a, L) => {
      const th = rad(a.hip), sh = rad(a.hip - a.knee);
      const knee = [hip[0] + L.t * Math.sin(th), hip[1] + L.t * Math.cos(th)];
      const ank = [knee[0] + L.s * Math.sin(sh), knee[1] + L.s * Math.cos(sh)];
      const fa = rad(a.ankle) - sh * 0.35;
      const toe = [ank[0] + L.f * Math.cos(fa), ank[1] + L.f * Math.sin(fa)];
      return { hip, knee, ank, toe };
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

    let frame = 0;
    const draw = (c) => {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      const unit = Math.min(h / (mini ? 1.95 : 2.6), w / (mini ? 3 : 2.1));
      const L = { t: unit * 0.47, s: unit * 0.45, f: unit * 0.15, torso: unit * 0.68, arm: unit * 0.33, fore: unit * 0.29, head: unit * 0.1 };
      const ground = h - (mini ? 10 : unit * 0.22);
      const cx = mini ? w * 0.36 : w * 0.46;
      const near = angles(c), far = angles((c + 0.5) % 1);
      const bob = unit * 0.025 * Math.cos(4 * Math.PI * c);
      const hip = [cx, ground - (L.t + L.s) * 0.97 + bob];

      // ground with moving treadmill ticks
      ctx.strokeStyle = col.muted; ctx.globalAlpha = 0.5; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(0, ground + 2); ctx.lineTo(w, ground + 2); ctx.stroke();
      const step = mini ? 18 : 26, off = ((c * step * 4) % step);
      for (let x = -off; x < w; x += step) { ctx.beginPath(); ctx.moveTo(x, ground + 6); ctx.lineTo(x - 5, ground + 11); ctx.stroke(); }
      ctx.globalAlpha = 1;

      const lf = leg(hip, far, L), ln = leg(hip, near, L);
      const lean = rad(4);
      const sh = [hip[0] + L.torso * Math.sin(lean), hip[1] - L.torso * Math.cos(lean)];
      const head = [sh[0] + L.head * 0.5, sh[1] - L.head * 2.3];
      const neck = [sh[0] + L.head * 0.25, sh[1] - L.head * 1.2];
      const arm = (a) => {
        const ang = rad(-0.7 * a.hip + 6), el = [sh[0] + L.arm * Math.sin(ang), sh[1] + L.arm * Math.cos(ang)];
        const fang = ang + rad(18 + 10 * Math.sin(rad(a.hip) * 2)), wr = [el[0] + L.fore * Math.sin(fang), el[1] + L.fore * Math.cos(fang)];
        return [sh, el, wr];
      };
      const lw = mini ? 3.4 : 5;

      // far side, muted
      ctx.globalAlpha = 0.45;
      line(arm(near), col.muted, lw * 0.8);
      line([lf.hip, lf.knee, lf.ank, lf.toe], col.muted, lw);
      ctx.globalAlpha = 1;

      // ankle trail of the near leg
      trail.push([ln.ank[0], ln.ank[1]]);
      if (trail.length > (mini ? 40 : 70)) trail.shift();
      for (let i = 1; i < trail.length; i++) {
        ctx.globalAlpha = (i / trail.length) * 0.9;
        line([trail[i - 1], trail[i]], col.coral, mini ? 1.5 : 2);
      }
      ctx.globalAlpha = 1;

      // torso, head, near limbs
      line([hip, sh, neck], col.ink, lw);
      dot(head, L.head, null, col.ink);
      line([ln.hip, ln.knee, ln.ank, ln.toe], col.ink, lw);
      line(arm(far), col.ink, lw * 0.8);

      // knee angle arc
      const th = Math.atan2(ln.hip[0] - ln.knee[0], ln.hip[1] - ln.knee[1]);
      const sa = Math.atan2(ln.ank[0] - ln.knee[0], ln.ank[1] - ln.knee[1]);
      ctx.strokeStyle = col.blue; ctx.lineWidth = mini ? 1.5 : 2.5;
      ctx.beginPath();
      const r = unit * 0.14;
      ctx.arc(ln.knee[0], ln.knee[1], r, Math.PI / 2 - th, Math.PI / 2 - sa, true);
      ctx.stroke();

      // motion-capture markers
      const mr = mini ? 3.4 : 5.5;
      [lf.knee, lf.ank].forEach((p) => dot(p, mr * 0.8, col.bg, col.muted));
      [ln.hip, ln.knee, ln.ank, ln.toe, sh].forEach((p) => dot(p, mr, col.blue, col.bg));

      if (outs.length && frame++ % 5 === 0) {
        outs.forEach((o) => {
          const k = o.dataset.readout;
          const v = Math.round(k === "hip" ? near.hip : k === "knee" ? near.knee : near.ankle);
          o.textContent = (mini ? k[0].toUpperCase() + k.slice(1) + " " : "") + v + "°";
        });
      }
    };

    size();
    let running = false, raf = 0, t0 = performance.now(), cPaused = 0.72;
    const loop = (now) => {
      if (!running) return;
      const c = (((now - t0) / 1150) % 1 + 1) % 1;
      cPaused = c;
      draw(c);
      raf = requestAnimationFrame(loop);
    };
    const start = () => { if (running || reduceMotion) return; running = true; t0 = performance.now() - cPaused * 1150; raf = requestAnimationFrame(loop); };
    const stop = () => { running = false; cancelAnimationFrame(raf); };
    draw(cPaused);
    if (hasIO && !reduceMotion) {
      new IntersectionObserver((en) => (en[0].isIntersecting ? start() : stop()), { threshold: 0.05 }).observe(canvas);
    }
    document.addEventListener("visibilitychange", () => (document.hidden ? stop() : null));
    let rT;
    window.addEventListener("resize", () => { clearTimeout(rT); rT = setTimeout(() => { size(); draw(cPaused); }, 120); });
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { col = colors(); draw(cPaused); });
    if (reduceMotion) for (let i = 0; i < 70; i++) draw((0.72 + i / 70) % 1); // build a static trail
  };
  $$("canvas[data-gait]").forEach(makeGait);

  /* ---------- Body map ---------- */
  const cares = $$(".care");
  const caption = $("#body-caption");
  const bodyEls = $$(".body-map [data-areas]");
  const showArea = (key) => {
    bodyEls.forEach((el) => el.classList.toggle("on", (el.dataset.areas || "").split(" ").includes(key)));
    const active = cares.find((c) => c.dataset.area === key);
    if (caption && active) caption.textContent = active.dataset.caption;
  };
  let pinned = cares[0]?.dataset.area;
  cares.forEach((c) => {
    const btn = $(".title", c);
    btn.addEventListener("click", () => {
      pinned = c.dataset.area;
      cares.forEach((o) => { o.classList.toggle("on", o === c); $(".title", o).setAttribute("aria-pressed", String(o === c)); });
      showArea(pinned);
    });
    c.addEventListener("mouseenter", () => showArea(c.dataset.area));
    c.addEventListener("mouseleave", () => showArea(pinned));
  });
  if (pinned) showArea(pinned);

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
  const dial = $("#dial");
  if (dial && window.STAGES) {
    const svg = $("svg", dial);
    const range = $("#dial-range");
    const arm = $(".arm", svg), knob = $(".knob", svg), fill = $(".arc-fill", svg), text = $(".angle-text", svg);
    const tabs = $$('[role="tab"]', dial);
    const panel = $("#stage-panel");
    const cx = 260, cy = 262, r = 200, len = Math.PI * r;
    let angle = 0, stageIdx = 0, touched = false;
    const motion = { id: 0 };
    const renderStage = (i) => {
      if (i === stageIdx) return;
      stageIdx = i;
      const s = window.STAGES[i];
      tabs.forEach((t, k) => { t.setAttribute("aria-selected", String(k === i)); t.tabIndex = k === i ? 0 : -1; });
      panel.setAttribute("aria-labelledby", tabs[i].id);
      const steps = window.STAGES.map((_, k) => `<i class="${k <= i ? "on" : ""}"></i>`).join("");
      panel.innerHTML = `<div class="stage-steps" aria-hidden="true">${steps}</div>` +
        `<p class="deg-label swap">${s.angle}° on the dial</p><h3 class="swap">${s.title}</h3><p class="swap">${s.text}</p>`;
    };
    const set = (deg, fromRange) => {
      angle = clamp(deg, 0, 180);
      const [x, y] = polar(cx, cy, r, angle);
      arm.setAttribute("x2", x.toFixed(1)); arm.setAttribute("y2", y.toFixed(1));
      knob.setAttribute("cx", x.toFixed(1)); knob.setAttribute("cy", y.toFixed(1));
      fill.style.strokeDashoffset = String(len * (1 - angle / 180));
      text.textContent = Math.round(angle) + "°";
      if (!fromRange) range.value = String(Math.round(angle));
      const idx = Math.round(angle / 45);
      range.setAttribute("aria-valuetext", `${Math.round(angle)} degrees, ${window.STAGES[idx].title}`);
      renderStage(idx);
    };
    const animateTo = (deg, ms) => tween(angle, deg, ms, (d) => set(d), motion);
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
  }

  /* ---------- Copy buttons ---------- */
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

  /* Everything interactive is set up: tell the loading screen (a real progress task). */
  const fontLink = document.getElementById("font-css");
  if (fontLink && fontLink.media !== "all") fontLink.media = "all";
  if (window.PortfolioLoader) window.PortfolioLoader.done("init");
})();
