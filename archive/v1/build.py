"""Builds Jessie J.'s portfolio from src/ into two outputs:

  dist/site/      a standard static website (index.html + assets) ready to deploy anywhere
  dist/artifact/  a single self-contained page for publishing as a claude.ai artifact

Run:  python3 build.py
"""
import base64, html, json, math, random, shutil, sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
import content as C  # noqa: E402

e = html.escape
FONTS = ("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300..600"
         "&family=Manrope:wght@400;500;600;700&display=swap")
TITLE = "Jessie J., Physiotherapist"
DESCRIPTION = ("Jessie J. is a physiotherapist in Chennai specialising in sports and orthopaedic "
               "rehabilitation, post-operative recovery, neuro rehab and home-based care.")
RESUME = "Jessie-J-Resume.pdf"


# ---------------------------------------------------------------- SVG helpers
def polar(cx, cy, r, deg):
    t = math.radians(deg)
    return cx - r * math.cos(t), cy - r * math.sin(t)


def f(n):
    return f"{n:.1f}".rstrip("0").rstrip(".")


ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
         'stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')
DOWN = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true"><path d="M12 4v12M6 11l6 6 6-6M5 20h14"/></svg>')
MINI_GONIO = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
              'aria-hidden="true"><path d="M3 18a9 9 0 0 1 18 0"/><path class="n" d="M12 18 12 9.5"/><circle cx="12" cy="18" r="1.6" fill="currentColor"/></svg>')
SEAL = ('<svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true"><circle cx="20" cy="20" r="17"/><circle cx="20" cy="20" r="12" '
        'stroke-dasharray="2 3"/><path d="M14.5 20.5l3.8 3.7 7.2-8"/></svg>')
BRAND = ('<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="16" fill="var(--ink)"/>'
         '<path d="M6 21a10 10 0 0 1 20 0" fill="none" stroke="var(--accent)" stroke-width="2.6" stroke-linecap="round"/>'
         '<path d="M16 21 22.4 13.6" stroke="var(--ground)" stroke-width="2.4" stroke-linecap="round"/>'
         '<circle cx="16" cy="21" r="2.4" fill="var(--ground)"/></svg>')
FAVICON = ('data:image/svg+xml,' + '%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E'
           '%3Ccircle cx=%2716%27 cy=%2716%27 r=%2716%27 fill=%27%2312221b%27/%3E'
           '%3Cpath d=%27M6 21a10 10 0 0 1 20 0%27 fill=%27none%27 stroke=%27%23b98a2e%27 stroke-width=%272.6%27 stroke-linecap=%27round%27/%3E'
           '%3Cpath d=%27M16 21 22.4 13.6%27 stroke=%27%23ebeee7%27 stroke-width=%272.4%27 stroke-linecap=%27round%27/%3E'
           '%3Ccircle cx=%2716%27 cy=%2721%27 r=%272.4%27 fill=%27%23ebeee7%27/%3E%3C/svg%3E')


def ring_svg():
    """Goniometer scale ring that slowly turns behind the portrait."""
    cx = cy = 200
    parts = []
    for d in range(0, 360, 5):
        major = d % 30 == 0
        x1, y1 = polar(cx, cy, 190, d)
        x2, y2 = polar(cx, cy, 190 - (18 if major else 9), d)
        parts.append(f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke-width="{2 if major else 1.2}"/>')
    return ('<svg class="ring" viewBox="0 0 400 400" fill="none" stroke="currentColor" aria-hidden="true">'
            '<circle cx="200" cy="200" r="190" stroke-width="1.5"/><circle cx="200" cy="200" r="140" stroke-width="1"/>'
            + "".join(parts) + "</svg>")


def hero_gonio_svg():
    cx, cy, r = 100, 100, 84
    ticks = []
    for d in range(0, 181, 15):
        major = d % 45 == 0
        x1, y1 = polar(cx, cy, r + 6, d)
        x2, y2 = polar(cx, cy, r + (14 if major else 10), d)
        ticks.append(f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="var(--ink)" '
                     f'stroke-width="{1.6 if major else 1}" stroke-opacity="{1 if major else .5}"/>')
    labels = []
    for d in (0, 90, 180):
        x, y = polar(cx, cy, r - 16, d)
        anchor = "start" if d == 0 else "end" if d == 180 else "middle"
        labels.append(f'<text x="{f(x)}" y="{f(y - 7 if d != 90 else y + 6)}" text-anchor="{anchor}" '
                      f'font-size="10" font-weight="600" fill="var(--muted)" font-family="var(--body)">{d}</text>')
    arc = f"M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}"
    return (f'<svg id="hero-gonio" viewBox="-2 -2 204 108" role="img" aria-label="Goniometer showing knee flexion">'
            f'<path d="{arc}" fill="none" stroke="var(--surface)" stroke-width="10"/>'
            f'<path class="sweep" d="{arc}" fill="none" stroke="var(--accent)" stroke-width="10" '
            f'style="stroke-dasharray:{math.pi * r:.1f} {math.pi * r:.1f};stroke-dashoffset:{math.pi * r / 4:.1f}"/>'
            + "".join(ticks) + "".join(labels) +
            f'<line x1="{cx}" y1="{cy}" x2="{cx - r + 6}" y2="{cy}" stroke="var(--ink)" stroke-width="3" stroke-linecap="round"/>'
            f'<line class="needle" x1="{cx}" y1="{cy}" x2="{f(polar(cx, cy, r - 6, 135)[0])}" y2="{f(polar(cx, cy, r - 6, 135)[1])}" stroke="var(--ink)" stroke-width="3" stroke-linecap="round"/>'
            f'<circle cx="{cx}" cy="{cy}" r="5" fill="var(--ink)"/></svg>')


def dial_svg():
    cx, cy, r = 260, 262, 200
    parts = []
    for d in range(0, 181, 5):
        major = d % 45 == 0
        x1, y1 = polar(cx, cy, r - 24, d)
        x2, y2 = polar(cx, cy, r - (44 if major else 32), d)
        parts.append(f'<line class="tick{" major" if major else ""}" x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" '
                     f'stroke-width="{2 if major else 1}"/>')
    for s in C.STAGES:
        d = s["angle"]
        x, y = polar(cx, cy, r - 64, d)
        anchor = "start" if d < 45 else "end" if d > 135 else "middle"
        if d == 45: anchor = "start"
        if d == 135: anchor = "end"
        parts.append(f'<text class="lbl" x="{f(x)}" y="{f(y - 14 if d in (0, 180) else y + 5)}" text-anchor="{anchor}">{d}°</text>')
        lx, ly = polar(cx, cy, r + 30, d)
        anchor = "end" if d < 45 else "start" if d > 135 else "middle"
        if d == 45: anchor = "end"
        if d == 135: anchor = "start"
        parts.append(f'<text class="lbl" x="{f(lx)}" y="{f(ly + (5 if d in (0, 180) else 0))}" text-anchor="{anchor}" '
                     f'style="fill:var(--ink)">{e(s["title"])}</text>')
    arc = f"M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}"
    return (f'<svg viewBox="-60 -40 640 400" aria-hidden="true">'
            f'<path class="arc-bg" d="{arc}" fill="none" stroke-width="20"/>'
            f'<path class="arc-fill" d="{arc}" fill="none" stroke-width="20" style="stroke-dasharray:{math.pi * r:.1f} {math.pi * r:.1f};stroke-dashoffset:{math.pi * r:.1f}"/>'
            + "".join(parts) +
            f'<line x1="{cx}" y1="{cy}" x2="{cx - r}" y2="{cy}" class="arm-fixed" stroke="var(--ink)" stroke-width="7" stroke-linecap="round"/>'
            f'<line class="arm" x1="{cx}" y1="{cy}" x2="{cx - r}" y2="{cy}" stroke-width="7" stroke-linecap="round"/>'
            f'<circle class="hub" cx="{cx}" cy="{cy}" r="12"/>'
            f'<circle class="knob" cx="{cx - r}" cy="{cy}" r="16" stroke-width="5"/>'
            f'<text class="angle-text" x="{cx}" y="{cy + 78}" text-anchor="middle">0°</text></svg>')


def knee_art():
    random.seed(7)
    pts = []
    for i in range(160):
        t = i / 160 * math.tau * 3
        x = 290 + 34 * math.sin(t * 1.3) * math.cos(t * 0.21) + random.uniform(-3, 3)
        y = 206 + 22 * math.sin(t * 0.9 + 1) + random.uniform(-3, 3)
        pts.append(f"{f(x)} {f(y)}")
    sway = "M " + " L ".join(pts)
    ax, ay = 186, 146
    a1x, a1y = ax - 22 * math.sin(math.radians(17)), ay - 22 * math.cos(math.radians(17))
    return (
        '<svg viewBox="0 0 380 300" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path class="draw" d="M150 26 L186 146" stroke-width="5"/>'
        '<path class="draw" d="M186 146 L168 266" stroke-width="5"/>'
        '<path class="draw" d="M140 270 L232 270" stroke-width="3"/>'
        f'<circle cx="{ax}" cy="{ay}" r="13" stroke="var(--accent)" stroke-width="3" fill="var(--deep)"/>'
        f'<path class="draw" d="M{f(a1x)} {f(a1y)} A 30 30 0 0 0 {ax - 30 * math.sin(math.radians(-8)):.1f} {ay + 30 * math.cos(math.radians(-8)):.1f}" stroke="var(--accent)" stroke-width="2"/>'
        f'<path class="draw" d="{sway}" stroke="var(--accent)" stroke-width="1.6" stroke-opacity=".9"/>'
        '<circle cx="290" cy="206" r="58" stroke-width="1" stroke-dasharray="3 5" stroke-opacity=".5"/>'
        '<text x="290" y="126" text-anchor="middle" fill="currentColor" stroke="none" font-size="12" font-family="var(--body)" opacity=".7">postural sway</text>'
        '</svg>')


def orofacial_art():
    parts = []
    for i, rr in enumerate(range(36, 190, 30)):
        x1, y1 = 96 + rr * math.cos(math.radians(-55)), 150 + rr * math.sin(math.radians(-55))
        x2, y2 = 96 + rr * math.cos(math.radians(55)), 150 + rr * math.sin(math.radians(55))
        op = 1 - i * 0.14
        parts.append(f'<path class="draw" d="M{f(x1)} {f(y1)} A {rr} {rr} 0 0 1 {f(x2)} {f(y2)}" stroke-width="2.2" stroke-opacity="{op:.2f}"/>')
    wave = []
    for i in range(0, 241):
        x = 120 + i
        y = 248 + 10 * math.sin(i / 240 * math.tau * 4)
        wave.append(f"{f(x)} {f(y)}")
    return (
        '<svg viewBox="0 0 380 300" fill="none" stroke="currentColor" stroke-linecap="round" aria-hidden="true">'
        + "".join(parts) +
        '<circle cx="96" cy="150" r="14" fill="var(--accent)" stroke="none"/>'
        f'<path class="draw" d="M {" L ".join(wave)}" stroke="var(--accent)" stroke-width="2.4"/>'
        '<text x="360" y="288" text-anchor="end" fill="currentColor" stroke="none" font-size="12" font-family="var(--body)" opacity=".7">rhythmic oral motor work</text>'
        '</svg>')


# ---------------------------------------------------------------- page sections
def nav_links():
    return "".join(f'<a href="#{k}">{e(v)}</a>' for k, v in C.NAV)


def resume_link(cls, label, mode):
    extra = ' download' if mode == "site" else ' target="_blank" rel="noopener"'
    return f'<a class="btn {cls}" href="{RESUME}"{extra}><span>{e(label)}</span>{DOWN}</a>'


def job_card(j):
    bullets = "".join(f"<li>{e(b)}</li>" for b in j["bullets"])
    return f'''
        <article class="job" data-reveal>
          <div class="job-top">
            <h4>{e(j["role"])}</h4>
            <span class="dates">{e(j["dates"])}</span>
          </div>
          <p class="where">{e(j["org"])} · {e(j["place"])}</p>
          <p class="summary">{e(j["summary"])}</p>
          <details>
            <summary><span class="plus" aria-hidden="true">+</span>All responsibilities ({len(j["bullets"])})</summary>
            <ul>{bullets}</ul>
          </details>
        </article>'''


def page(mode, photo_src):
    P = C.PERSON
    facts = "".join(f'<li class="enter" style="--d:{6 + i}"><span class="k">{e(k)}</span><span class="v">{e(v)}</span></li>'
                    for i, (k, v) in enumerate(C.FACTS))
    marquee_items = "".join(f"<li>{e(m)}</li>" for m in C.MARQUEE)
    tabs = "".join(
        f'<button type="button" role="tab" id="tab-{s["key"]}" aria-controls="stage-panel" '
        f'aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}">{e(s["title"])}</button>'
        for i, s in enumerate(C.STAGES))
    s0 = C.STAGES[0]
    areas = "".join(f'''
        <article class="area" data-reveal style="--d:{i % 3}">
          <h3>{MINI_GONIO}<span>{e(a["title"])}</span></h3>
          <p>{e(a["text"])}</p>
          <ul>{"".join(f"<li>{e(x)}</li>" for x in a["items"])}</ul>
        </article>''' for i, a in enumerate(C.EXPERTISE))
    practice = "".join(job_card(j) for j in C.PRACTICE)
    interns = "".join(job_card(j) for j in C.INTERNSHIPS)
    rotations = "".join(f"<li>{e(r)}</li>" for r in C.ROTATION_SITES)
    arts = {"knee": knee_art(), "parkinsons": orofacial_art()}
    studies = "".join(f'''
        <article class="study" data-reveal>
          <div class="study-art">{arts[s["key"]]}<span class="note">Illustration</span></div>
          <div class="study-body">
            <h3>{e(s["title"])}</h3>
            <p>{e(s["lead"])}</p>
            <dl>{"".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in s["rows"])}</dl>
          </div>
        </article>''' for s in C.RESEARCH)
    schools = "".join(f'''
          <div class="school{" primary" if i == 0 else ""}" data-reveal style="--d:{i}">
            <span class="yrs">{e(y)}</span>
            <div><h3>{e(deg)}</h3><p>{e(sch)}, {e(loc)}</p></div>
          </div>''' for i, (y, deg, sch, loc) in enumerate(C.EDUCATION))
    certs = "".join(f"<li>{SEAL}<div><strong>{e(n)}</strong><span>{e(d)}</span></div></li>" for n, d in C.CERTIFICATIONS)
    langs = "".join(f"<li><span>{e(n)}</span><span>{e(l)}</span></li>" for n, l in C.LANGUAGES)
    mobile_links = "".join(f'<li><a class="big" href="#{k}" style="--i:{i}">{e(v)}</a></li>' for i, (k, v) in enumerate(C.NAV))

    return f'''
<a class="skip" href="#main">Skip to content</a>

<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="#top" aria-label="Jessie J., back to top">{BRAND}<span>Jessie J.</span></a>
    <nav class="nav-links" aria-label="Sections">{nav_links()}<span class="nav-dot" aria-hidden="true"></span></nav>
    <div class="header-cta">
      {resume_link("dark", "Résumé", mode)}
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Open menu"><span></span><span></span></button>
    </div>
  </div>
</header>

<div class="mobile-menu" id="mobile-menu" aria-hidden="true">
  <nav aria-label="Sections, mobile"><ul>{mobile_links}<li><a class="big" href="{RESUME}" style="--i:{len(C.NAV)}" {"download" if mode == "site" else 'target="_blank" rel="noopener"'}>Résumé (PDF)</a></li></ul></nav>
  <div class="menu-foot"><span>{e(P["email"])}</span><span>{e(P["phone_display"])}</span><span>{e(P["city"])}</span></div>
</div>

<main id="main">
  <section class="hero" id="top" aria-labelledby="hero-title">
    <div class="wrap">
      <div class="hero-grid">
        <div class="hero-copy">
          <p class="hero-role enter" style="--d:0"><span>{e(P["role"])}</span><span class="sep" aria-hidden="true"></span><span>{e(P["focus"])}</span></p>
          <h1 id="hero-title"><span class="line"><span style="--d:1">Jessie</span></span><span class="line"><span style="--d:2">J.</span></span></h1>
          <p class="thesis enter" style="--d:3">Bridging the gap between injury and peak performance.</p>
          <p class="intro enter" style="--d:4">I'm a physiotherapist in Chennai who helps people recover from sports injuries,
            surgery and neurological conditions, with plans built on careful assessment and a clear route back to everyday activity.</p>
          <div class="hero-actions enter" style="--d:5">
            <a class="btn gold" href="#experience"><span>View my experience</span>{ARROW}</a>
            <a class="btn quiet" href="#contact"><span>Contact me</span></a>
            {resume_link("quiet", "Download résumé", mode)}
          </div>
        </div>
        <figure class="portrait" style="margin:0">
          <div class="arch">{ring_svg()}</div>
          <div class="clip"><img src="{photo_src}" width="820" height="930" alt="Portrait of Jessie J., smiling, wearing a gold silk saree" fetchpriority="high"></div>
          <figcaption class="gonio-card">
            {hero_gonio_svg()}
            <div class="readout"><span class="deg" id="hero-deg">135°</span><span class="cap">Knee flexion,<br>full range</span></div>
          </figcaption>
        </figure>
      </div>
      <ul class="facts" aria-label="At a glance">{facts}</ul>
    </div>
  </section>

  <div class="marquee" aria-label="Focus areas">
    <div class="marquee-track"><ul>{marquee_items}</ul><ul aria-hidden="true">{marquee_items}</ul></div>
  </div>

  <section class="section" id="about" aria-labelledby="about-title">
    <div class="wrap">
      <div class="section-head" data-reveal><h2 id="about-title">Recovery, one step at a time.</h2></div>
      <div class="about-grid">
        <div class="about-aside" data-reveal>
          <p class="about-lead">I work with patients from their first assessment to their return to activity, with a special interest in sports and orthopaedic rehabilitation.</p>
          <div class="about-quote">
            <p>“Driven to bridge the gap between injury and peak performance through targeted rehab and patient education.”</p>
            <span>From my professional profile</span>
          </div>
        </div>
        <div class="about-body" data-reveal style="--d:1">
          <p>My clinical work covers <strong>sports injuries, recovery after surgery, and neurological rehabilitation</strong>, along with paediatric and geriatric care. I treat patients in a rehab centre and in their own homes, including residential elderly care settings.</p>
          <p>Every programme starts with a thorough assessment of strength, range of motion, balance, gait and how a person moves. From there I build a plan around their goals and adjust it at each reassessment.</p>
          <p>Teaching is part of treatment. Patients and caregivers leave with home exercise programmes and a clear picture of how to protect their recovery. I also mentor <strong>junior physiotherapists and interns</strong> in assessment, treatment planning and clinical reasoning.</p>
          <p>I studied for my <strong>Bachelor of Physiotherapy at Saveetha College of Physiotherapy, SIMATS</strong> (2021 – 2026), and hold certifications in cupping therapy, trigger point release and muscle energy technique.</p>
          <div class="langs"><h3>Languages</h3><ul>{langs}</ul></div>
        </div>
      </div>
    </div>
  </section>

  <section class="section tone" id="approach" aria-labelledby="approach-title">
    <div class="wrap">
      <div class="section-head" data-reveal>
        <h2 id="approach-title">How a plan comes together.</h2>
        <p>A goniometer measures how far a joint can move. Drag the arm, or pick a stage, to walk through the way I take a patient from assessment back to full activity.</p>
      </div>
      <div class="approach-grid">
        <div class="dial" id="dial" data-reveal>
          {dial_svg()}
          <label class="sr-only" for="dial-range">Dial angle, in degrees</label>
          <input id="dial-range" type="range" min="0" max="180" step="1" value="0">
          <div class="stage-tabs" role="tablist" aria-label="Stages of care">{tabs}</div>
        </div>
        <div class="stage-panel" id="stage-panel" role="tabpanel" aria-live="polite" aria-labelledby="tab-{s0["key"]}" data-reveal style="--d:1">
          <div><p class="deg-label">{s0["angle"]}° on the dial</p></div>
          <h3>{e(s0["title"])}</h3>
          <p>{e(s0["text"])}</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section" id="expertise" aria-labelledby="expertise-title">
    <div class="wrap">
      <div class="section-head" data-reveal>
        <h2 id="expertise-title">Areas of care.</h2>
        <p>The conditions and people I work with most, across clinic, hospital and home-based practice.</p>
      </div>
      <div class="areas">{areas}</div>
    </div>
  </section>

  <section class="section deep" id="experience" aria-labelledby="experience-title">
    <div class="wrap exp-layout">
      <div class="exp-side" data-reveal>
        <h2 id="experience-title">Clinical experience.</h2>
        <p>In practice since 2022 across a multispeciality clinic, a dedicated rehab centre and home-based care, with hospital internships alongside my degree.</p>
        <div class="rotations"><h3>Undergraduate clinical rotations</h3><ul>{rotations}</ul></div>
      </div>
      <div>
        <div class="exp-group"><h3>Practice</h3><div class="jobs">{practice}</div></div>
        <div class="exp-group"><h3>Hospital internships</h3><div class="jobs">{interns}</div></div>
      </div>
    </div>
  </section>

  <section class="section" id="research" aria-labelledby="research-title">
    <div class="wrap">
      <div class="section-head" data-reveal>
        <h2 id="research-title">Research.</h2>
        <p>Two research projects, each testing a practical, hands-on intervention for a specific group of patients.</p>
      </div>
      <div class="studies">{studies}</div>
    </div>
  </section>

  <section class="section tone" id="education" aria-labelledby="education-title">
    <div class="wrap">
      <div class="section-head" data-reveal>
        <h2 id="education-title">Education and training.</h2>
      </div>
      <div class="edu-grid">
        <div class="schools">{schools}</div>
        <div class="certs" data-reveal style="--d:1">
          <h3>Certifications</h3>
          <ul style="display:grid;gap:20px">{certs}</ul>
        </div>
      </div>
    </div>
  </section>

  <section class="section contact" id="contact" aria-labelledby="contact-title">
    <div class="wrap contact-grid">
      <div data-reveal>
        <h2 id="contact-title">Let's get you moving.</h2>
        <p class="lead">For consultations, home visits or professional opportunities, email or call me. I'm based in Chennai and see patients in the clinic and at home.</p>
      </div>
      <div class="channels" data-reveal style="--d:1">
        <div class="channel">
          <span class="k">Email</span>
          <div class="row"><span class="v" id="c-email">{e(P["email"])}</span>
            <span class="acts"><button class="chip-btn" type="button" data-copy="{e(P["email"])}" data-target="c-email">Copy</button><a class="chip-btn" href="mailto:{e(P["email"])}">Write</a></span></div>
        </div>
        <div class="channel">
          <span class="k">Phone and WhatsApp</span>
          <div class="row"><span class="v" id="c-phone">{e(P["phone_display"])}</span>
            <span class="acts"><button class="chip-btn" type="button" data-copy="{e(P["phone_display"])}" data-target="c-phone">Copy</button><a class="chip-btn" href="{P["whatsapp"]}" target="_blank" rel="noopener">WhatsApp</a></span></div>
        </div>
        <div style="margin-top:12px">{resume_link("dark", "Download résumé (PDF)", mode)}</div>
      </div>
    </div>
  </section>
</main>

<footer class="site-footer">
  <div class="wrap footer-row">
    <a class="brand" href="#top">{BRAND}<span>Jessie J.</span></a>
    <span>Physiotherapist · {e(P["city"])}</span>
    <span>© <span id="year">2026</span> Jessie J. · <a href="#top">Back to top ↑</a></span>
  </div>
</footer>
<div class="toast" role="status" aria-live="polite"></div>
'''


def build():
    css = (SRC / "styles.css").read_text()
    js = (SRC / "main.js").read_text()
    stages = json.dumps([{k: s[k] for k in ("angle", "title", "text")} for s in C.STAGES])
    scripts = f"<script>window.STAGES={stages};</script>\n<script>\n{js}\n</script>"
    fonts = (f'<link rel="preconnect" href="https://fonts.googleapis.com">'
             f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             f'<link rel="stylesheet" href="{FONTS}">')

    # --- deployable static site
    site = ROOT / "dist" / "site"
    if site.exists(): shutil.rmtree(site)
    (site / "assets").mkdir(parents=True)
    shutil.copy(SRC / "assets" / "jessie-cutout.webp", site / "assets" / "jessie.webp")
    shutil.copy(SRC / "assets" / "Jessie-J-Resume-public.pdf", site / RESUME)
    make_og(site / "assets" / "og.jpg")
    head = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE}</title>
<meta name="description" content="{e(DESCRIPTION)}">
<meta name="author" content="Jessie J.">
<meta name="theme-color" content="#12221b">
<meta property="og:type" content="profile">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{e(DESCRIPTION)}">
<meta property="og:image" content="assets/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{FAVICON}">
<link rel="preload" as="image" href="assets/jessie.webp">
{fonts}
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "Person", "name": "Jessie J.", "jobTitle": "Physiotherapist", "address": {"@type": "PostalAddress", "addressLocality": "Chennai", "addressCountry": "IN"}, "alumniOf": "Saveetha College of Physiotherapy, SIMATS", "email": "mailto:" + C.PERSON["email"]})}</script>
<style>
{css}
</style>
</head>
<body>'''
    (site / "index.html").write_text(head + page("site", "assets/jessie.webp") + scripts + "\n</body>\n</html>\n")

    # --- single-file artifact (wrapped in a skeleton at publish time)
    art = ROOT / "dist" / "artifact"
    if art.exists(): shutil.rmtree(art)
    art.mkdir(parents=True)
    photo = "data:image/webp;base64," + base64.b64encode((SRC / "assets" / "jessie-cutout.webp").read_bytes()).decode()
    shutil.copy(SRC / "assets" / "Jessie-J-Resume-public.pdf", art / RESUME)
    art_head = (f'<title>Jessie J. Physiotherapist</title>\n'
                f'<meta name="claude:viewport-fit-sides" content="cover">\n'
                f'<meta name="description" content="{e(DESCRIPTION)}">\n{fonts}\n<style>\n{css}\n</style>\n')
    (art / "index.html").write_text(art_head + page("artifact", photo) + scripts + "\n")
    print("built", site / "index.html", art / "index.html")


def make_og(path):
    from PIL import Image
    og = Image.new("RGB", (1200, 630), (18, 34, 27))
    sand = Image.new("RGB", (520, 630), (222, 210, 182))
    og.paste(sand, (680, 0))
    ph = Image.open(SRC / "assets" / "jessie-cutout.webp").convert("RGBA")
    ph = ph.resize((520, int(ph.height * 520 / ph.width)))
    og.paste(ph, (680, 630 - ph.height + 40), ph)
    og.save(path, quality=84)


if __name__ == "__main__":
    build()
