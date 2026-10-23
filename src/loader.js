/* Loading progress manager.
 *
 * Runs inline straight after the loader markup, before the rest of the page has even arrived, so it can
 * watch the page load as it happens. Progress is the weighted share of real tasks that have finished:
 *
 *   page sections   one task per section; a section counts once the next one has arrived (or the
 *                   document has finished parsing), i.e. once it is fully in the page
 *   typefaces       each self-hosted typeface the site uses, via document.fonts.load()
 *   portrait        the hero photo downloaded and decoded
 *   interactive     main.js finished setting up navigation, dial, body map, canvases (it calls done("init"))
 *
 * There are no timers that move the number. Timeouts exist only so a stuck or failed request can never keep
 * the screen up: a task that fails or times out is closed and the page opens without it. The displayed
 * number eases toward the measured value but never passes it and never goes backwards; 100% appears only
 * when every task is closed.
 */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement, el = doc.getElementById("loader");
  if (!el) return;
  root.style.overflow = "hidden";   // scroll lock while covered (scrollbar-gutter keeps the layout still)
  var reduce = !!(window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches);
  var pctNum = el.querySelector(".ld-pct b"), bar = el.querySelector(".ld-bar i"), status = el.querySelector(".ld-status"),
      meter = el.querySelector(".ld-progress"), shank = el.querySelector(".ld-shank"), arc = el.querySelector(".ld-arc");
  var ARC = 50.3, RANGE = 90; // knee travels from 90° flexion to full extension

  var SECTIONS = ["#top", "#about", "#approach", "#expertise", "#experience", "#research", "#education", "#contact", ".site-footer"];
  var FONTS = [   // [descriptor, key, weight]: one self-hosted file each
    ['700 40px "Bricolage Grotesque"', "display", 12], ['400 16px "Plus Jakarta Sans"', "body", 10], ['500 12px "IBM Plex Mono"', "labels", 7]
  ];
  var tasks = [], byKey = {};
  function add(key, weight, label) { var t = { key: key, w: weight, label: label, done: false, failed: false }; tasks.push(t); byKey[key] = t; }
  SECTIONS.forEach(function (s) { add("section:" + s, 4, "Building the page"); });
  FONTS.forEach(function (f) { add("font:" + f[1], f[2], "Loading typefaces"); });
  add("portrait", 21, "Loading portrait");
  add("init", 14, "Setting up interactive sections");

  var target = 0, shown = 0, raf = 0, last = 0, finished = false, timers = [], log = [];
  var t0 = performance.now();

  function close(key, failed) {
    var t = byKey[key];
    if (!t || t.done || finished) return;
    t.done = true; t.failed = !!failed;
    var sum = 0, tot = 0;
    for (var i = 0; i < tasks.length; i++) { tot += tasks[i].w; if (tasks[i].done) sum += tasks[i].w; }
    var v = sum === tot ? 100 : Math.floor((sum / tot) * 100);
    if (v > target) target = v;
    log.push({ t: Math.round(performance.now() - t0), key: key, failed: !!failed, target: target });
    if (key === "font:display") showName();
    var next = null;
    for (var j = 0; j < tasks.length; j++) if (!tasks[j].done) { next = tasks[j]; break; }
    if (next) status.textContent = next.label; // "Ready" only once the number itself reaches 100
    if (!raf) { last = performance.now(); raf = requestAnimationFrame(frame); }
  }
  function later(ms, fn) { timers.push(setTimeout(fn, ms)); }
  // The name reveals once its typeface is in, or after 1 s in the fallback face on slow connections.
  var nameAt = 0;
  function showName() { if (!nameAt) { nameAt = performance.now(); el.classList.add("text-in"); } }

  var lastInt = -1;
  function render(v) {
    var shownInt = Math.floor(v);
    bar.style.transform = "scaleX(" + (v / 100).toFixed(4) + ")";
    shank.style.transform = "rotate(" + (-RANGE * v / 100).toFixed(2) + "deg)";
    arc.style.strokeDashoffset = (ARC * (1 - v / 100)).toFixed(2);
    if (shownInt !== lastInt) {   // text and ARIA only when the whole number changes
      lastInt = shownInt;
      pctNum.textContent = String(shownInt);
      meter.setAttribute("aria-valuenow", String(shownInt));
      meter.setAttribute("aria-valuetext", shownInt + "%, " + status.textContent.toLowerCase());
    }
  }
  function frame(now) {
    raf = 0;
    var dt = Math.max(0, Math.min(64, now - last)); last = Math.max(last, now); // frame timestamps can precede the update
    var gap = target - shown, next;
    if (reduce) next = target;
    else next = shown + Math.min(gap, Math.max(gap * (1 - Math.exp(-dt / 170)), dt * 0.03)); // ease in, never overshoot
    if (target - next < 0.05) next = target;
    shown = Math.min(target, Math.max(shown, next)); // never backwards, never ahead
    render(shown);
    if (shown < target) raf = requestAnimationFrame(frame);
    else if (target === 100) complete();
  }

  function complete() {
    if (finished) return;
    finished = true;
    el.classList.add("complete");
    status.textContent = "Ready";
    render(100);
    showName();
    // Hold the final pose just long enough to read 100%. If the name only just began to appear, let it finish.
    var nameLeft = reduce ? 0 : Math.max(0, nameAt + 900 - performance.now());
    later(Math.max(reduce ? 150 : 380, nameLeft), lift);
  }
  function lift() {
    finished = true;
    timers.forEach(clearTimeout);
    if (raf) cancelAnimationFrame(raf);
    el.classList.add("leaving");
    root.style.overflow = "";
    var hero = doc.querySelector(".hero.is-held");
    if (hero) hero.classList.remove("is-held");   // only the hero restyles, not the whole page
    var main = doc.getElementById("main");
    if (main) main.removeAttribute("aria-busy");
    try { window.dispatchEvent(new Event("portfolio:revealed")); } catch (e) { /* very old browsers */ }
    var remove = function () { if (el.parentNode) el.parentNode.removeChild(el); };
    el.addEventListener("transitionend", function (ev) { if (ev.target === el && ev.propertyName === "opacity") remove(); });
    setTimeout(remove, 1200);
    if (mo) mo.disconnect();
  }

  /* ---- page sections, observed while the HTML streams in ---- */
  var seen = 0, mo = null;
  function scanSections(final) {
    while (seen < SECTIONS.length && doc.querySelector(SECTIONS[seen])) {
      if (seen > 0) close("section:" + SECTIONS[seen - 1]); // the previous section is complete once the next exists
      seen++;
    }
    if (final) for (var i = 0; i < SECTIONS.length; i++) close("section:" + SECTIONS[i]);
    var main = doc.getElementById("main");
    if (main && !main.hasAttribute("data-busy-set")) { main.setAttribute("aria-busy", "true"); main.setAttribute("data-busy-set", ""); }
    watchPortrait();
  }

  /* ---- portrait ---- */
  var img = null;
  function watchPortrait() {
    if (img) return;
    img = doc.querySelector(".photo-card img");
    if (!img) return;
    var ok = function () {
      var p = img.decode ? img.decode() : Promise.resolve();
      p.then(function () { close("portrait"); }, function () { fail(); });
    };
    var fail = function () { var card = img.closest(".photo-card"); if (card) card.classList.add("photo-failed"); close("portrait", true); };
    if (img.complete) { img.naturalWidth ? ok() : fail(); }
    else { img.addEventListener("load", ok, { once: true }); img.addEventListener("error", fail, { once: true }); }
    later(20000, function () { close("portrait", true); });
  }

  if ("MutationObserver" in window && doc.readyState === "loading") {
    mo = new MutationObserver(function () { scanSections(false); });
    mo.observe(root, { childList: true, subtree: true });
  }
  function onParsed() { if (mo) { mo.disconnect(); mo = null; } scanSections(true); }
  if (doc.readyState === "loading") doc.addEventListener("DOMContentLoaded", onParsed, { once: true }); else onParsed();

  /* ---- fonts: self-hosted and declared in the critical CSS, so they can be requested straight away ---- */
  if (!doc.fonts || !doc.fonts.load) FONTS.forEach(function (f) { close("font:" + f[1], true); });
  else FONTS.forEach(function (f) {
    doc.fonts.load(f[0], "Jessie - Physiotherapist 0123456789%").then(
      function (faces) { close("font:" + f[1], !faces || !faces.length); },
      function () { close("font:" + f[1], true); });
    later(12000, function () { close("font:" + f[1], true); });
  });

  /* ---- interactive setup: main.js reports in; if it never does, don't wait for it ---- */
  window.addEventListener("load", function () { later(2500, function () { close("init", true); }); }, { once: true });

  /* ---- last resort: never keep the page hidden; lifts at the real value, without claiming 100% ---- */
  later(25000, function () { if (!finished) { status.textContent = "Opening the site"; lift(); } });

  render(0);
  later(1000, showName);
  window.PortfolioLoader = {
    done: function (key) { close(key); },
    state: function () { return { target: target, shown: shown, finished: finished, log: log.slice(),
      pending: tasks.filter(function (t) { return !t.done; }).map(function (t) { return t.key; }) }; }
  };
})();
