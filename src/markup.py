"""Page markup and illustrations for Jessie J.'s portfolio (redesign v2: tape-blue clinical editorial)."""
import html, math, random
import content as C

e = html.escape
RESUME = "Jessie_Physiotherapist_Resume.pdf"
BRAND_NAME = "Jessie - Physiotherapist"


def polar(cx, cy, r, deg):
    t = math.radians(deg)
    return cx - r * math.cos(t), cy - r * math.sin(t)


def f(n):
    return f"{n:.1f}".rstrip("0").rstrip(".")


def icon(d, cls=""):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>')


ARROW = icon('<path d="M5 12h14M13 6l6 6-6 6"/>', "arrow")
DOWN = icon('<path d="M12 4v12M6 11l6 6 6-6M5 20h14"/>', "down")
# Brand mark: a strip of kinesio tape across a joint marker.
BRAND = ('<span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 24 24">'
         '<circle cx="12" cy="12" r="4.2" fill="none" stroke="var(--on-blue)" stroke-width="2"/>'
         '<rect x="1.5" y="9.6" width="21" height="4.8" rx="2.4" fill="var(--on-blue)" opacity=".38" transform="rotate(-35 12 12)"/>'
         '<circle cx="12" cy="12" r="1.6" fill="var(--on-blue)"/></svg></span>')
FAVICON = ('data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E'
           '%3Crect width=%2732%27 height=%2732%27 rx=%278%27 fill=%27%232447df%27/%3E'
           '%3Crect x=%274%27 y=%2713%27 width=%2724%27 height=%276%27 rx=%273%27 fill=%27%23fff%27 opacity=%27.38%27 transform=%27rotate(-35 16 16)%27/%3E'
           '%3Ccircle cx=%2716%27 cy=%2716%27 r=%275.4%27 fill=%27none%27 stroke=%27%23fff%27 stroke-width=%272.6%27/%3E'
           '%3Ccircle cx=%2716%27 cy=%2716%27 r=%272%27 fill=%27%23fff%27/%3E%3C/svg%3E')


# ---------------------------------------------------------------- illustrations
def dial_svg():
    """Interactive goniometer for the care pathway."""
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
        anchor = {0: "start", 45: "start", 90: "middle", 135: "end", 180: "end"}[d]
        parts.append(f'<text class="lbl" x="{f(x)}" y="{f(y - 14 if d in (0, 180) else y + 5)}" text-anchor="{anchor}">{d}°</text>')
        lx, ly = polar(cx, cy, r + 30, d)
        anchor = {0: "end", 45: "end", 90: "middle", 135: "start", 180: "start"}[d]
        parts.append(f'<text class="lbl stage" x="{f(lx)}" y="{f(ly + (5 if d in (0, 180) else 0))}" text-anchor="{anchor}">{e(s["title"])}</text>')
    arc = f"M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}"
    L = math.pi * r
    return (f'<svg viewBox="-60 -40 640 400" aria-hidden="true">'
            f'<path class="arc-bg" d="{arc}" fill="none" stroke-width="22"/>'
            f'<path class="arc-fill" d="{arc}" fill="none" stroke-width="22" style="stroke-dasharray:{L:.1f} {L:.1f};stroke-dashoffset:{L:.1f}"/>'
            + "".join(parts) +
            f'<line class="arm-fixed" x1="{cx}" y1="{cy}" x2="{cx - r}" y2="{cy}" stroke-width="7" stroke-linecap="round"/>'
            f'<line class="arm" x1="{cx}" y1="{cy}" x2="{cx - r}" y2="{cy}" stroke-width="7" stroke-linecap="round"/>'
            f'<circle class="hub" cx="{cx}" cy="{cy}" r="12"/>'
            f'<circle class="knob" cx="{cx - r}" cy="{cy}" r="16" stroke-width="5"/>'
            f'<text class="angle-text" x="{cx}" y="{cy + 80}" text-anchor="middle">0°</text></svg>')


# Front-view motion-capture skeleton. Markers are tagged with the care areas they belong to.
BODY_MARKERS = [
    ("head", 100, 34, "neuro"),
    ("c7", 100, 62, "neuro hands"),
    ("sh-l", 66, 72, "ortho hands"), ("sh-r", 134, 72, "ortho hands"),
    ("el-l", 57, 120, ""), ("el-r", 143, 120, ""),
    ("wr-l", 51, 165, ""), ("wr-r", 149, 165, ""),
    ("t8", 100, 106, "neuro hands"),
    ("l4", 100, 146, "ortho hands"),
    ("hip-l", 84, 158, "ortho lifespan"), ("hip-r", 116, 158, "ortho lifespan"),
    ("kn-l", 80, 236, "sports ortho"), ("kn-r", 120, 236, "sports ortho"),
    ("an-l", 78, 306, "sports lifespan"), ("an-r", 122, 306, "sports lifespan"),
]
BODY_BONES = [
    ("c7", "t8"), ("t8", "l4"), ("sh-l", "sh-r"), ("hip-l", "hip-r"),
    ("sh-l", "el-l"), ("el-l", "wr-l"), ("sh-r", "el-r"), ("el-r", "wr-r"),
    ("hip-l", "kn-l"), ("kn-l", "an-l"), ("hip-r", "kn-r"), ("kn-r", "an-r"),
]


def body_map_svg():
    pos = {k: (x, y) for k, x, y, _ in BODY_MARKERS}
    bones = "".join(f'<line class="bone" x1="{pos[a][0]}" y1="{pos[a][1]}" x2="{pos[b][0]}" y2="{pos[b][1]}"/>' for a, b in BODY_BONES)
    bones += ('<line class="bone" x1="100" y1="51" x2="100" y2="62"/>'
              '<path class="bone" d="M78 306 L66 318 M122 306 L134 318 M51 165 L48 180 M149 165 L152 180"/>')
    marks = []
    for k, x, y, areas in BODY_MARKERS:
        if k == "head":
            marks.append(f'<circle class="head" cx="{x}" cy="{y}" r="17"/>')
            marks.append(f'<circle class="halo" data-areas="{areas}" cx="{x}" cy="{y}" r="10"/>'
                         f'<circle class="mk" data-areas="{areas}" cx="{x}" cy="{y}" r="5.5"/>')
            continue
        marks.append(f'<circle class="halo" data-areas="{areas}" cx="{x}" cy="{y}" r="9"/>'
                     f'<circle class="mk" data-areas="{areas}" cx="{x}" cy="{y}" r="5.5"/>')
    return ('<svg viewBox="20 6 160 330" role="img" aria-label="Body map showing the joints each area of care focuses on">'
            '<line class="ground" x1="30" y1="324" x2="170" y2="324" stroke-width="1.5"/>'
            '<ellipse class="sway" data-areas="lifespan neuro" cx="100" cy="324" rx="40" ry="8"/>'
            + bones + "".join(marks) + "</svg>")


def knee_art():
    """Single-leg stance on a balance board with a postural-sway trace (knee OA study)."""
    random.seed(11)
    pts = []
    for i in range(170):
        t = i / 170 * math.tau * 3
        x = 300 + 36 * math.sin(t * 1.3) * math.cos(t * 0.21) + random.uniform(-3, 3)
        y = 120 + 24 * math.sin(t * 0.9 + 1) + random.uniform(-3, 3)
        pts.append(f"{f(x)} {f(y)}")
    hip, knee, ank = (150, 34), (176, 132), (158, 226)
    th = math.atan2(hip[0] - knee[0], hip[1] - knee[1])
    sh = math.atan2(ank[0] - knee[0], ank[1] - knee[1])
    a1 = (knee[0] + 30 * math.sin(th), knee[1] + 30 * math.cos(th))
    a2 = (knee[0] + 30 * math.sin(sh), knee[1] + 30 * math.cos(sh))
    return (
        '<svg viewBox="0 0 400 260" fill="none" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        f'<path class="draw" d="M{hip[0]} {hip[1]} L{knee[0]} {knee[1]} L{ank[0]} {ank[1]} L192 232" stroke="var(--ink)" stroke-width="5"/>'
        f'<path class="draw" d="M{f(a1[0])} {f(a1[1])} A30 30 0 0 0 {f(a2[0])} {f(a2[1])}" stroke="var(--blue)" stroke-width="2.5"/>'
        '<path class="draw" d="M96 244 L236 244" stroke="var(--ink)" stroke-width="4"/>'
        '<path class="draw" d="M120 244 Q166 262 212 244" stroke="var(--muted)" stroke-width="2"/>'
        f'<rect x="{knee[0] - 40}" y="{knee[1] - 9}" width="80" height="18" rx="9" fill="var(--coral)" opacity=".9" transform="rotate(-62 {knee[0]} {knee[1]})"/>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="6" fill="var(--surface)" stroke="var(--ink)" stroke-width="2.5"/>' for x, y in (hip, knee, ank)) +
        f'<path class="draw" d="M {" L ".join(pts)}" stroke="var(--blue)" stroke-width="1.6"/>'
        '<circle cx="300" cy="120" r="64" stroke="var(--muted)" stroke-width="1" stroke-dasharray="3 5" opacity=".6"/>'
        '<text x="300" y="40" text-anchor="middle" fill="var(--muted)" font-size="11" font-family="var(--f-label)" letter-spacing="1">SWAY TRACE</text>'
        '</svg>')


def orofacial_art():
    """Face-profile line with oral-motor rhythm (Parkinson's sialorrhea study)."""
    profile = ("M150 30 C120 30 100 50 98 80 C97 92 92 100 86 110 C82 116 86 120 92 121 L96 122 "
               "C94 128 95 133 99 136 C96 140 96 145 100 148 C102 156 100 166 106 172 C114 180 132 178 146 174 "
               "L152 214")
    arcs = []
    for i, rr in enumerate(range(26, 140, 26)):
        x1, y1 = 104 - rr * math.cos(math.radians(-40)), 146 + rr * math.sin(math.radians(-40))
        x2, y2 = 104 - rr * math.cos(math.radians(40)), 146 + rr * math.sin(math.radians(40))
        arcs.append(f'<path class="draw" d="M{f(x1)} {f(y1)} A{rr} {rr} 0 0 0 {f(x2)} {f(y2)}" stroke="var(--blue)" stroke-width="2" opacity="{1 - i * .17:.2f}"/>')
    wave = " L ".join(f"{f(200 + i)} {f(200 + 9 * math.sin(i / 160 * math.tau * 4))}" for i in range(0, 161))
    return (
        '<svg viewBox="0 0 400 260" fill="none" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        f'<path class="draw" d="{profile}" stroke="var(--ink)" stroke-width="3.5" transform="translate(150 0) scale(-1 1) translate(-260 0)"/>'
        + "".join(a.replace('d="M', 'transform="translate(150 0) scale(-1 1) translate(-260 0)" d="M') for a in arcs) +
        '<circle cx="306" cy="146" r="7" fill="var(--coral)"/>'
        f'<path class="draw" d="M {wave}" stroke="var(--coral)" stroke-width="2.5" transform="translate(-170 30)"/>'
        '<text x="30" y="210" fill="var(--muted)" font-size="11" font-family="var(--f-label)" letter-spacing="1">ORAL MOTOR RHYTHM</text>'
        '</svg>')


# ---------------------------------------------------------------- page
def resume_button(mode):
    """The one résumé download control, used everywhere it appears.

    On the deployed site it downloads the PDF under a clear filename. Inside the claude.ai preview the
    sandbox blocks downloads, so there it opens the same PDF in a new tab instead.
    """
    attrs = f' download="{RESUME}" type="application/pdf"' if mode == "site" else ' target="_blank" rel="noopener"'
    return f'<a class="btn btn-resume" href="{RESUME}"{attrs}><span>Download Résumé (PDF)</span>{DOWN}</a>'


def brand(label):
    """Header and footer branding. Visible text is exactly BRAND_NAME."""
    return (f'<a class="brand" href="#top" aria-label="{e(BRAND_NAME)}, {label}">{BRAND}'
            f'<span class="brand-text"><b>Jessie</b> - Physiotherapist</span></a>')


def job_card(j):
    bullets = "".join(f"<li>{e(b)}</li>" for b in j["bullets"])
    return f'''
        <article class="job" data-reveal>
          <div class="job-top"><h4>{e(j["role"])}</h4><span class="dates">{e(j["dates"])}</span></div>
          <p class="where">{e(j["org"])} · {e(j["place"])}</p>
          <p class="summary">{e(j["summary"])}</p>
          <details>
            <summary><span class="plus" aria-hidden="true">+</span>All responsibilities ({len(j["bullets"])})</summary>
            <ul>{bullets}</ul>
          </details>
        </article>'''


def section_head(label, title, tid, text=""):
    p = f"<p>{text}</p>" if text else ""
    return f'<div class="section-head" data-reveal><span class="label">{e(label)}</span><h2 id="{tid}">{title}</h2>{p}</div>'


def page(mode, photo_src):
    P = C.PERSON
    nav = "".join(f'<a href="#{k}">{e(v)}</a>' for k, v in C.NAV)
    mobile = "".join(f'<li><a class="big" href="#{k}" style="--i:{i}">{e(v)}</a></li>' for i, (k, v) in enumerate(C.NAV))
    meta = "".join(f'<div><span class="label">{e(k)}</span><strong>{e(v)}</strong></div>' for k, v in C.FACTS)
    band_items = "".join(f"<li>{e(m)}</li>" for m in C.MARQUEE)
    band2 = "".join(f"<li>{e(m)}</li>" for m in reversed(C.MARQUEE))
    tabs = "".join(
        f'<button type="button" role="tab" id="tab-{s["key"]}" aria-controls="stage-panel" '
        f'aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}">{e(s["title"])}</button>'
        for i, s in enumerate(C.STAGES))
    s0 = C.STAGES[0]
    steps = "".join(f'<i class="{"on" if i == 0 else ""}"></i>' for i in range(len(C.STAGES)))
    cares = "".join(f'''
          <article class="care{" on" if i == 0 else ""}" data-area="{a["key"]}" data-caption="{e(a["caption"])}" data-reveal style="--d:{i % 3}">
            <span class="ix">{i + 1:02d}</span>
            <button class="title" type="button" aria-pressed="{"true" if i == 0 else "false"}"><h3>{e(a["title"])}</h3></button>
            <div class="more"><p>{e(a["text"])}</p><ul class="chips">{"".join(f"<li>{e(x)}</li>" for x in a["items"])}</ul></div>
          </article>''' for i, a in enumerate(C.EXPERTISE))
    practice = "".join(job_card(j) for j in C.PRACTICE)
    interns = "".join(job_card(j) for j in C.INTERNSHIPS)
    rotations = "".join(f"<li>{e(r)}</li>" for r in C.ROTATION_SITES)
    arts = {"knee": knee_art(), "parkinsons": orofacial_art()}
    tags = {"knee": "Orthopaedics · Balance", "parkinsons": "Neurology · Oral motor"}
    studies = "".join(f'''
          <article class="study" data-reveal style="--d:{i}">
            <div class="study-art graph"><div class="zoom">{arts[s["key"]]}</div><span class="tag label">{tags[s["key"]]}</span><span class="note label">Illustration</span></div>
            <div class="study-body">
              <h3>{e(s["title"])}</h3>
              <p>{e(s["lead"])}</p>
              <dl>{"".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in s["rows"])}</dl>
            </div>
          </article>''' for i, s in enumerate(C.RESEARCH))
    schools = "".join(f'''
            <div class="school{" primary" if i == 0 else ""}" data-reveal style="--d:{i}">
              <span class="label">{e(y)}</span><h3>{e(deg)}</h3><p>{e(sch)}, {e(loc)}</p>
            </div>''' for i, (y, deg, sch, loc) in enumerate(C.EDUCATION))
    certs = "".join(f'<li class="cert"><span class="strip">{e(n)}</span><p>{e(d)}</p></li>' for n, d in C.CERTIFICATIONS)
    langs = "".join(f"<li><b>{e(n)}</b><span>{e(l)}</span></li>" for n, l in C.LANGUAGES)

    return f'''
<a class="skip" href="#main">Skip to content</a>

<header class="site-header">
  <div class="wrap">
    <div class="nav-shell">
      {brand("back to top")}
      <nav class="nav-links" aria-label="Sections">{nav}<span class="nav-pill" aria-hidden="true"></span></nav>
      <div class="header-cta">
        {resume_button(mode)}
        <button class="menu-btn" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Open menu"><span></span><span></span></button>
      </div>
    </div>
  </div>
</header>
<div class="scrim" aria-hidden="true"></div>
<div class="mobile-menu" id="mobile-menu" aria-hidden="true">
  <nav aria-label="Sections, mobile"><ul>{mobile}<li class="menu-resume" style="--i:{len(C.NAV)}">{resume_button(mode)}</li></ul></nav>
  <div class="menu-foot"><span>{e(P["email"])}</span><span>{e(P["phone_display"])} · {e(P["city"])}</span></div>
</div>

<main id="main">
  <section class="hero" id="top" aria-labelledby="hero-title">
    <div class="hero-bg graph" aria-hidden="true"></div>
    <div class="hero-glow" aria-hidden="true"></div>
    <div class="wrap hero-grid">
      <div class="hero-copy">
        <div class="hero-tag enter" style="--d:0"><span class="status"><i aria-hidden="true"></i>Clinic and home visits · Chennai</span></div>
        <h1 id="hero-title">
          <span class="line"><span style="--d:1">Jessie J</span></span>
          <span class="line"><span class="role" style="--d:2">Physiotherapist in <b>sports &amp; orthopaedic</b> rehabilitation</span></span>
        </h1>
        <p class="thesis enter" style="--d:3">Bridging the gap between <strong>injury and peak performance</strong>. I help people recover from sports injuries, surgery and neurological conditions, with plans built on careful assessment and a clear route back to everyday activity.</p>
        <div class="hero-actions enter" style="--d:4">
          {resume_button(mode)}
          <a class="btn outline" href="#experience"><span>View my experience</span>{ARROW}</a>
          <a class="btn ghost" href="#contact"><span>Contact me</span></a>
        </div>
        <div class="hero-meta enter" style="--d:5">{meta}</div>
      </div>
      <figure class="hero-visual" style="margin:0">
        <div class="photo-card graph">
          <img src="{photo_src}" width="820" height="930" alt="Portrait of Jessie, physiotherapist, smiling and wearing a gold silk saree" fetchpriority="high">
          <div class="axis"><span class="label">Physiotherapist</span><span class="label">BPT · 2021–26</span></div>
        </div>
        <span class="tape t1" aria-hidden="true"></span>
        <span class="tape coral t2" aria-hidden="true"></span>
        <figcaption class="gait-card">
          <div class="row"><span class="label">Gait cycle</span><b data-readout="knee">Knee 0°</b></div>
          <canvas data-gait="mini" aria-hidden="true"></canvas>
        </figcaption>
      </figure>
    </div>
  </section>

  <div class="tape-band" aria-label="Focus areas">
    <div class="band b2" aria-hidden="true"><div class="band-track"><ul>{band2}</ul><ul>{band2}</ul></div></div>
    <div class="band b1"><div class="band-track"><ul>{band_items}</ul><ul aria-hidden="true">{band_items}</ul></div></div>
  </div>

  <section class="section" id="about" aria-labelledby="about-title">
    <div class="wrap about-grid">
      <aside class="gait-panel" data-reveal aria-label="Gait analysis illustration">
        <div class="top"><span class="label">Gait analysis</span><span class="label live"><i aria-hidden="true"></i>Motion model</span></div>
        <canvas data-gait="full" aria-hidden="true"></canvas>
        <div class="readouts">
          <div><span>Hip</span><b data-readout="hip">0°</b></div>
          <div><span>Knee</span><b data-readout="knee">0°</b></div>
          <div><span>Ankle</span><b data-readout="ankle">0°</b></div>
        </div>
        <p class="caption">An illustrative walking model. Assessing gait, balance and movement like this is where every plan of mine begins.</p>
      </aside>
      <div class="about-copy">
        {section_head("About", "Recovery, one step at a time.", "about-title")}
        <p class="lead" data-reveal>I work with patients from their first assessment to their return to activity, with a special interest in sports and orthopaedic rehabilitation.</p>
        <div class="body" data-reveal>
          <p>My clinical work covers <strong>sports injuries, recovery after surgery and neurological rehabilitation</strong>, along with paediatric and geriatric care. I treat patients in a rehab centre and in their own homes, including residential elderly care settings.</p>
          <p>Every programme starts with a thorough assessment of strength, range of motion, balance, gait and how a person moves. From there I build a plan around their goals and adjust it at each reassessment.</p>
          <p>Teaching is part of treatment. Patients and caregivers leave with home exercise programmes and a clear picture of how to protect their recovery. I also mentor <strong>junior physiotherapists and interns</strong> in assessment, treatment planning and clinical reasoning.</p>
        </div>
        <div class="quote" data-reveal>
          <span class="tape" aria-hidden="true"></span>
          <p>“Driven to bridge the gap between injury and peak performance through targeted rehab and patient education.”</p>
          <span class="label">From my professional profile</span>
        </div>
        <div data-reveal style="display:grid;gap:12px"><span class="label">Languages</span><ul class="langs">{langs}</ul></div>
      </div>
    </div>
  </section>

  <section class="section approach" id="approach" aria-labelledby="approach-title">
    <div class="wrap">
      {section_head("Care pathway", "How a plan comes together.", "approach-title", "A goniometer measures how far a joint can move. Drag the arm, or pick a stage, to walk through how I take a patient from assessment back to full activity.")}
      <div class="approach-grid">
        <div class="dial" id="dial" data-reveal>
          {dial_svg()}
          <label class="sr-only" for="dial-range">Dial angle, in degrees</label>
          <input id="dial-range" type="range" min="0" max="180" step="1" value="0">
          <div class="stage-tabs" role="tablist" aria-label="Stages of care">{tabs}</div>
        </div>
        <div class="stage-panel" id="stage-panel" role="tabpanel" aria-live="polite" aria-labelledby="tab-{s0["key"]}" data-reveal style="--d:1">
          <div class="stage-steps" aria-hidden="true">{steps}</div>
          <p class="deg-label">{s0["angle"]}° on the dial</p>
          <h3>{e(s0["title"])}</h3>
          <p>{e(s0["text"])}</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section" id="expertise" aria-labelledby="expertise-title">
    <div class="wrap">
      {section_head("Expertise", "Where I can help.", "expertise-title", "The conditions and people I work with most, across clinic, hospital and home-based practice. Select an area to see where on the body it focuses.")}
      <div class="care-grid">
        <div class="body-map graph" data-reveal>
          {body_map_svg()}
          <p class="caption" id="body-caption" aria-live="polite">{e(C.EXPERTISE[0]["caption"])}</p>
        </div>
        <div class="care-list">{cares}</div>
      </div>
    </div>
  </section>

  <section class="section experience" id="experience" aria-labelledby="experience-title">
    <div class="wrap">
      <div class="exp-head">
        {section_head("Experience", "Clinic, rehab centre, home and hospital.", "experience-title", "In practice since 2022, with hospital internships alongside my degree.")}
        <div class="rotations" data-reveal><span class="label">Undergraduate clinical rotations</span><ul>{rotations}</ul></div>
      </div>
      <div class="timeline" id="timeline">
        <div class="rail" aria-hidden="true"><i></i></div>
        <h3 class="tl-group">Practice</h3>
        {practice}
        <h3 class="tl-group">Hospital internships</h3>
        {interns}
      </div>
    </div>
  </section>

  <section class="section" id="research" aria-labelledby="research-title">
    <div class="wrap">
      {section_head("Research", "Two research projects.", "research-title", "Each one tests a practical, hands-on intervention for a specific group of patients.")}
      <div class="studies">{studies}</div>
    </div>
  </section>

  <section class="section education" id="education" aria-labelledby="education-title">
    <div class="wrap">
      {section_head("Education", "Education and training.", "education-title")}
      <div class="edu-grid">
        <div class="schools" id="schools"><div class="rail" aria-hidden="true"><i></i></div>{schools}</div>
        <div class="certs" data-reveal style="--d:1">
          <h3>Certifications</h3>
          <ul style="display:grid;gap:22px">{certs}</ul>
        </div>
      </div>
    </div>
  </section>

  <section class="section contact" id="contact" aria-labelledby="contact-title">
    <span class="tape c1" aria-hidden="true"></span><span class="tape coral c2" aria-hidden="true"></span>
    <div class="wrap contact-grid">
      <div data-reveal>
        <div class="section-head" style="margin-bottom:0"><span class="label">Contact</span>
        <h2 id="contact-title">Let's get you <span class="mark">moving.</span></h2></div>
        <p class="lead">For consultations, home visits or professional opportunities, email or call me. I'm based in Chennai and see patients in the clinic and at home.</p>
      </div>
      <div class="channels" data-reveal style="--d:1">
        <div class="channel">
          <span class="label">Email</span>
          <div class="row"><span class="v" id="c-email">{e(P["email"])}</span>
            <span class="acts"><button class="chip-btn" type="button" data-copy="{e(P["email"])}" data-target="c-email">Copy</button><a class="chip-btn" href="mailto:{e(P["email"])}">Write</a></span></div>
        </div>
        <div class="channel">
          <span class="label">Phone and WhatsApp</span>
          <div class="row"><span class="v" id="c-phone">{e(P["phone_display"])}</span>
            <span class="acts"><button class="chip-btn" type="button" data-copy="{e(P["phone_display"])}" data-target="c-phone">Copy</button><a class="chip-btn" href="{P["whatsapp"]}" target="_blank" rel="noopener">WhatsApp</a></span></div>
        </div>
        <div class="channel-cta">{resume_button(mode)}</div>
      </div>
    </div>
  </section>
</main>

<footer class="site-footer">
  <div class="wrap footer-row">
    {brand("back to top")}
    <span>Physiotherapist · {e(P["city"])}</span>
    <span>© <span id="year">2026</span> Jessie J. · <a href="#top">Back to top ↑</a></span>
  </div>
</footer>
<div class="toast" role="status" aria-live="polite"></div>
'''
