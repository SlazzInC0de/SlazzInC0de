"""Generate animated project cards (assets/card-*.svg) in the red matrix theme.

Deterministic, standard library only. Run: python3 scripts/cards.py
Every card uses CSS + SMIL animation only, so it plays inside GitHub's <img> sandbox.
"""
import os
from html import escape

OUT = os.environ.get("OUT_DIR", "assets")

W, H = 900, 370
FONT = "'JetBrains Mono', 'Fira Code', Consolas, Menlo, monospace"

BG = "#070101"
PANEL = "#0d0202"
NODE = "#120303"
LINE = "#3a0808"
EDGE = "#5a1010"
RED = "#ff2b2b"
HOT = "#ff5c5c"
TEXT = "#ffe3e3"
MUTED = "#a35a5a"
DIM = "#6e2222"

CW = 0.6  # monospace glyph width as a fraction of font size


def tw(s, size):
    return len(s) * size * CW


def esc(s):
    return escape(s, quote=True)


STYLE = f"""
    .t-id {{ font: 700 13px {FONT}; fill: {RED}; letter-spacing: 3px; }}
    .t-st {{ font: 500 10px {FONT}; fill: {MUTED}; letter-spacing: 2px; }}
    .t-rp {{ font: 500 11px {FONT}; fill: {MUTED}; letter-spacing: 1px; }}
    .t-hd {{ font: 800 22px {FONT}; fill: {TEXT}; }}
    .t-sb {{ font: 400 12.5px {FONT}; fill: {MUTED}; }}
    .t-ch {{ font: 700 10px {FONT}; fill: {TEXT}; letter-spacing: 1.5px; }}
    .t-nl {{ font: 700 11.5px {FONT}; fill: {TEXT}; letter-spacing: 1px; }}
    .t-ns {{ font: 400 9.5px {FONT}; fill: {MUTED}; }}
    .t-mv {{ font: 800 26px {FONT}; fill: {RED}; }}
    .t-ml {{ font: 500 9.5px {FONT}; fill: {DIM}; letter-spacing: 2.5px; }}
    .t-sm {{ font: 500 10px {FONT}; fill: {MUTED}; letter-spacing: 1.5px; }}
    .t-ok {{ font: 700 11px {FONT}; fill: {RED}; letter-spacing: 1px; }}
    .pulse {{ animation: pulse 1.6s ease-in-out infinite; }}
    @keyframes pulse {{ 50% {{ opacity: .25; }} }}
    .flow {{ stroke-dasharray: 4 5; animation: flow 1s linear infinite; }}
    @keyframes flow {{ to {{ stroke-dashoffset: -9; }} }}
    .scan {{ animation: scan 5s linear infinite; }}
    @keyframes scan {{ from {{ transform: translateX(-200px); }} to {{ transform: translateX({W}px); }} }}
    .blink {{ animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
"""


def chips(items, x, y):
    out, cx = [], x
    for c in items:
        w = tw(c, 10) + c.count(" ") * 0 + len(c) * 1.5 + 22
        out.append(
            f'<rect x="{cx}" y="{y}" width="{w:.0f}" height="22" fill="none" stroke="{EDGE}"/>'
            f'<text x="{cx + w / 2:.0f}" y="{y + 15}" text-anchor="middle" class="t-ch">{esc(c)}</text>'
        )
        cx += w + 10
    return "".join(out)


def node(x, y, w, h, label, sub="", hl=None):
    """A box with a label and optional sub-label. hl=(delay, period) lights it up in sequence."""
    anim = ""
    if hl:
        d, p = hl
        anim = (
            f'<animate attributeName="fill" values="{NODE};#3a0808;{NODE};{NODE}" keyTimes="0;0.1;0.25;1" '
            f'dur="{p}s" begin="{d}s" repeatCount="indefinite"/>'
            f'<animate attributeName="stroke" values="{EDGE};{RED};{EDGE};{EDGE}" keyTimes="0;0.1;0.25;1" '
            f'dur="{p}s" begin="{d}s" repeatCount="indefinite"/>'
        )
    cy = y + h / 2
    ly = cy - 2 if sub else cy + 4
    s = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{NODE}" stroke="{EDGE}">{anim}</rect>'
        f'<text x="{x + w / 2:.0f}" y="{ly:.0f}" text-anchor="middle" class="t-nl">{esc(label)}</text>'
    )
    if sub:
        s += f'<text x="{x + w / 2:.0f}" y="{cy + 13:.0f}" text-anchor="middle" class="t-ns">{esc(sub)}</text>'
    return s


def wire(d, packets=0, dur=2.4, begin=0.0):
    """Dashed flowing connector with optional packets riding along it."""
    s = f'<path d="{d}" fill="none" stroke="{RED}" stroke-opacity=".55" stroke-width="1.2" class="flow"/>'
    for i in range(packets):
        b = begin + i * dur / packets
        s += (
            f'<circle r="3" fill="{HOT}"><animateMotion dur="{dur}s" begin="{b:.2f}s" '
            f'repeatCount="indefinite" path="{d}"/></circle>'
        )
    return s


def metrics(items, y=302):
    col = (W - 80) / len(items)
    out = [f'<rect x="40" y="{y - 14}" width="{W - 80}" height="1" fill="{LINE}"/>']
    for i, (v, lab) in enumerate(items):
        cx = 40 + col * i + col / 2
        out.append(
            f'<text x="{cx:.0f}" y="{y + 26}" text-anchor="middle" class="t-mv">{esc(v)}</text>'
            f'<text x="{cx:.0f}" y="{y + 44}" text-anchor="middle" class="t-ml">{esc(lab)}</text>'
        )
    return "".join(out)


def card(idx, name, status, repo, headline, sub, chip_list, diagram, metric_items):
    id_txt = f"{idx:02d} · {name}"
    dot_x = 40 + tw(id_txt, 13) + len(id_txt) * 3 + 10
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="1" fill="#000" fill-opacity="0.35"/>
    </pattern>
    <linearGradient id="sweep" x1="0" x2="1">
      <stop offset="0" stop-color="{RED}" stop-opacity="0"/>
      <stop offset=".5" stop-color="{RED}" stop-opacity=".9"/>
      <stop offset="1" stop-color="{RED}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <style>{STYLE}</style>
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect x="12" y="12" width="{W - 24}" height="{H - 24}" fill="{PANEL}" stroke="{EDGE}"/>
  <text x="40" y="46" class="t-id">{esc(id_txt)}</text>
  <circle cx="{dot_x:.0f}" cy="42" r="4" fill="{RED}" class="pulse"/>
  <text x="{dot_x + 12:.0f}" y="46" class="t-st">{esc(status)}</text>
  <text x="{W - 40}" y="46" text-anchor="end" class="t-rp">-&gt; /{esc(repo)}</text>
  <rect x="40" y="60" width="{W - 80}" height="1" fill="{LINE}"/>
  <rect class="scan" x="40" y="59.5" width="200" height="2" fill="url(#sweep)"/>
  <text x="40" y="96" class="t-hd">{esc(headline)}</text>
  <text x="40" y="118" class="t-sb">{esc(sub)}</text>
  {chips(chip_list, 40, 134)}
  {diagram}
  {metrics(metric_items)}
  <rect width="{W}" height="{H}" fill="url(#scanlines)" pointer-events="none"/>
</svg>
"""


# ----------------------------------------------------------------- diagrams

def d_stratoflow():
    y, h = 178, 44
    xs = [40, 205, 370, 555, 720]
    ws = [140, 140, 160, 140, 140]
    labels = [("CSV UPLOAD", "blob storage"), ("TRIGGER", "azure function"),
              ("VALIDATE", "pandera schemas"), ("PARQUET", "columnar sink"),
              ("SYNAPSE SQL", "openrowset")]
    s = []
    for i in range(4):
        x1 = xs[i] + ws[i]
        x2 = xs[i + 1]
        s.append(wire(f"M{x1},{y + h / 2} L{x2},{y + h / 2}", packets=2, dur=1.6, begin=i * 0.4))
    for i, (lab, sb) in enumerate(labels):
        s.append(node(xs[i], y, ws[i], h, lab, sb, hl=(i * 0.8, 4.0)))
    # quarantine branch for malformed rows
    qx = xs[2] + ws[2] / 2
    s.append(wire(f"M{qx},{y + h} L{qx},{y + h + 30} L{qx + 130},{y + h + 30}", packets=1, dur=2.4, begin=1.2))
    s.append(f'<rect x="{qx + 130}" y="{y + h + 18}" width="150" height="26" fill="none" stroke="{RED}" stroke-dasharray="3 3"/>')
    s.append(f'<text x="{qx + 205}" y="{y + h + 35}" text-anchor="middle" class="t-ok">QUARANTINE</text>')
    s.append(f'<text x="{qx + 292}" y="{y + h + 35}" class="t-sm">bad rows split out</text>')
    return "".join(s)


def d_drawtomata():
    y, h = 178, 40
    forms = ["REGEX", "λ-NFA", "NFA", "DFA", "MIN-DFA"]
    w, gap = 128, 45
    total = len(forms) * w + (len(forms) - 1) * gap
    x0 = (W - total) / 2
    s = []
    for i in range(len(forms) - 1):
        x1 = x0 + i * (w + gap) + w
        s.append(wire(f"M{x1:.0f},{y + h / 2} L{x1 + gap:.0f},{y + h / 2}", packets=1, dur=1.0, begin=i * 1.0))
    for i, f in enumerate(forms):
        s.append(node(round(x0 + i * (w + gap)), y, w, h, f, hl=(i * 1.0, 5.0)))
    # equivalence check bar
    by = y + h + 26
    s.append(f'<text x="{x0:.0f}" y="{by + 4}" class="t-sm">EQUIVALENCE CHECK</text>')
    bx = x0 + 160
    bw = total - 160 - 150
    s.append(f'<rect x="{bx:.0f}" y="{by - 6}" width="{bw:.0f}" height="12" fill="none" stroke="{EDGE}"/>')
    s.append(
        f'<rect x="{bx + 2:.0f}" y="{by - 4}" height="8" fill="{RED}" width="0">'
        f'<animate attributeName="width" values="0;{bw - 4:.0f};{bw - 4:.0f};0" keyTimes="0;0.7;0.95;1" dur="5s" repeatCount="indefinite"/></rect>'
    )
    s.append(
        f'<text x="{bx + bw + 14:.0f}" y="{by + 4}" class="t-ok" opacity="0">L(in) = L(out)  OK'
        f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.69;0.71;0.95;1" dur="5s" repeatCount="indefinite"/></text>'
    )
    return "".join(s)


def d_imazin():
    y, h = 176, 44
    s = []
    # query box with typing reveal
    q = "dark detective in a corrupt city"
    qw = 300
    s.append(f'<clipPath id="qclip"><rect x="52" y="{y}" height="{h}" width="0">'
             f'<animate attributeName="width" values="0;{qw - 24};{qw - 24};0" keyTimes="0;0.35;0.95;1" dur="6s" repeatCount="indefinite"/>'
             f'</rect></clipPath>')
    s.append(f'<rect x="40" y="{y}" width="{qw}" height="{h}" fill="{NODE}" stroke="{EDGE}"/>')
    s.append(f'<text x="52" y="{y + 14}" class="t-ns">query</text>')
    s.append(f'<text x="52" y="{y + 32}" class="t-nl" clip-path="url(#qclip)">{esc(q)}</text>')
    s.append(wire(f"M{40 + qw},{y + h / 2} L{410},{y + h / 2}", packets=1, dur=1.2))
    s.append(node(410, y, 150, h, "EMBED", "sentence vectors", hl=(2.1, 6.0)))
    s.append(wire(f"M560,{y + h / 2} L600,{y + h / 2}", packets=1, dur=1.2, begin=0.6))
    s.append(node(600, y, 260, h, "HYBRID RANK", "cosine + title + nickname", hl=(2.6, 6.0)))
    # ranked results with bars growing
    scores = [0.94, 0.88, 0.81, 0.73]
    ry = y + h + 22
    for i, sc in enumerate(scores):
        yy = ry + i * 0  # single row of four results
        x = 40 + i * 205
        bw = 120 * sc
        s.append(f'<text x="{x}" y="{yy + 10}" class="t-sm">#{i + 1}</text>')
        s.append(f'<rect x="{x + 28}" y="{yy + 1}" width="120" height="10" fill="none" stroke="{EDGE}"/>')
        s.append(
            f'<rect x="{x + 29}" y="{yy + 2}" height="8" width="0" fill="{RED}">'
            f'<animate attributeName="width" values="0;0;{bw - 2:.0f};{bw - 2:.0f};0" '
            f'keyTimes="0;{0.5 + i * 0.04:.2f};{0.65 + i * 0.04:.2f};0.95;1" dur="6s" repeatCount="indefinite"/></rect>'
        )
        s.append(f'<text x="{x + 156}" y="{yy + 10}" class="t-ok">{sc:.2f}</text>')
    return "".join(s)


def d_shortlist():
    y = 172
    s = []
    s.append(node(40, y, 150, 30, "RESUMES", hl=(0, 5.0)))
    s.append(node(40, y + 40, 150, 30, "JOB DESC", hl=(0, 5.0)))
    s.append(wire(f"M190,{y + 15} L250,{y + 15}", packets=1, dur=1.2))
    s.append(wire(f"M190,{y + 55} L250,{y + 55}", packets=1, dur=1.2, begin=0.6))
    s.append(node(250, y, 190, 30, "SKILL PARSE", hl=(1.0, 5.0)))
    s.append(node(250, y + 40, 190, 30, "MINILM EMBED", hl=(1.0, 5.0)))
    s.append(wire(f"M440,{y + 15} L475,{y + 15} L475,{y + 35} L510,{y + 35}", packets=1, dur=1.4, begin=0.3))
    s.append(wire(f"M440,{y + 55} L475,{y + 55} L475,{y + 35} L510,{y + 35}", packets=1, dur=1.4, begin=0.9))
    s.append(node(510, y + 12, 150, 46, "HYBRID SCORE", "exact + semantic", hl=(2.0, 5.0)))
    s.append(wire(f"M660,{y + 35} L700,{y + 35}", packets=1, dur=1.0, begin=0.5))
    for i, sc in enumerate([0.91, 0.84, 0.77]):
        yy = y + 2 + i * 24
        s.append(f'<text x="708" y="{yy + 13}" class="t-sm">TOP {i + 1}</text>')
        s.append(
            f'<rect x="762" y="{yy + 4}" height="10" width="0" fill="{RED}">'
            f'<animate attributeName="width" values="0;0;{90 * sc:.0f};{90 * sc:.0f};0" '
            f'keyTimes="0;{0.45 + i * 0.05:.2f};{0.6 + i * 0.05:.2f};0.95;1" dur="5s" repeatCount="indefinite"/></rect>'
        )
    s.append(f'<text x="250" y="{y + 100}" class="t-sm">each pick ships with a written reason: matched skills + semantic overlap</text>')
    return "".join(s)


def d_gradintern():
    y, h = 178, 44
    labels = [("REQUEST", "react client"), ("JWT VERIFY", "stateless auth"),
              ("RBAC GUARD", "student/recruiter/admin"), ("EXPRESS 5", "rest route"),
              ("MONGODB", "atlas")]
    w, gap = 140, 30
    s = []
    for i in range(len(labels) - 1):
        x1 = 40 + i * (w + gap) + w
        s.append(wire(f"M{x1},{y + h / 2} L{x1 + gap},{y + h / 2}", packets=1, dur=0.9, begin=i * 0.6))
    for i, (lab, sb) in enumerate(labels):
        s.append(node(40 + i * (w + gap), y, w, h, lab, sb, hl=(i * 0.6, 4.0)))
    # a rejected request bouncing off the RBAC guard
    gx = 40 + 2 * (w + gap) + w / 2
    s.append(f'<path d="M{gx},{y + h} L{gx},{y + h + 26}" stroke="{RED}" stroke-dasharray="3 3" fill="none"/>')
    s.append(f'<text x="{gx + 10}" y="{y + h + 24}" class="t-ok">403  wrong role, write blocked</text>')
    return "".join(s)


def d_brofessor():
    y = 172
    s = []
    steps = [("SLIDES / PDF", "your material"), ("CONCEPTS", "scan + plan"),
             ("BOARD PLAN", "what to draw")]
    w, gap = 132, 26
    for i in range(len(steps) - 1):
        x1 = 40 + i * (w + gap) + w
        s.append(wire(f"M{x1},{y + 22} L{x1 + gap},{y + 22}", packets=1, dur=1.0, begin=i * 0.7))
    for i, (lab, sb) in enumerate(steps):
        s.append(node(40 + i * (w + gap), y, w, 44, lab, sb, hl=(i * 0.7, 6.0)))
    s.append(wire(f"M{40 + 3 * w + 2 * gap},{y + 22} L{530},{y + 22}", packets=1, dur=1.0, begin=1.4))
    # the whiteboard: strokes get drawn, held, then wiped
    bx, by, bw, bh = 530, y - 10, 330, 118
    s.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#0a0101" stroke="{EDGE}"/>')
    strokes = [
        f"M{bx + 30},{by + 30} h70 v36 h-70 z",
        f"M{bx + 100},{by + 48} h60",
        f"M{bx + 150},{by + 42} l10,6 l-10,6",
        f"M{bx + 170},{by + 30} h80 v36 h-80 z",
        f"M{bx + 30},{by + 92} c20,-14 40,14 60,0 s40,-14 60,0 s40,14 60,0",
        f"M{bx + 250},{by + 92} h40",
    ]
    for i, d in enumerate(strokes):
        a, b = 0.08 + i * 0.1, 0.16 + i * 0.1
        s.append(
            f'<path d="{d}" fill="none" stroke="{TEXT}" stroke-width="1.6" stroke-linecap="round" '
            f'stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
            f'<animate attributeName="stroke-dashoffset" values="1;1;0;0;1" keyTimes="0;{a:.2f};{b:.2f};0.92;1" '
            f'dur="7s" repeatCount="indefinite"/></path>'
        )
    s.append(f'<text x="{bx + 65}" y="{by + 52}" text-anchor="middle" class="t-ns">input</text>')
    s.append(f'<text x="{bx + 210}" y="{by + 52}" text-anchor="middle" class="t-ns">output</text>')
    s.append(f'<text x="40" y="{y + 72}" class="t-sm">no generated images. every diagram is drawn stroke by stroke,</text>')
    s.append(f'<text x="40" y="{y + 88}" class="t-sm">narrated live, and pauses when you ask a doubt.</text>')
    return "".join(s)


CARDS = {
    "stratoflow": dict(
        name="STRATOFLOW", status="PIPELINE · AZURE", repo="stratoflow",
        headline="Serverless ETL that refuses to drop a batch.",
        sub="Upload a CSV, an Azure Function validates, transforms and lands it as queryable Parquet.",
        chip_list=["AZURE FUNCTIONS", "PANDERA", "PARQUET", "SYNAPSE SQL", "TERRAFORM"],
        diagram=d_stratoflow,
        metric_items=[("61.7%", "SMALLER STORAGE"), ("96%", "TEST COVERAGE"), ("100%", "INFRA AS CODE")],
    ),
    "drawtomata": dict(
        name="DRAWTOMATA", status="LIVE · VERCEL", repo="drawtomata",
        headline="Automata conversions, every step on screen.",
        sub="Regex, finite automata, grammars and NPDAs. Every output is equivalence-checked.",
        chip_list=["THEORY OF COMPUTATION", "STEP-BY-STEP", "EQUIVALENCE-VERIFIED", "CI"],
        diagram=d_drawtomata,
        metric_items=[("4", "AUTOMATON FORMS"), ("100%", "OUTPUTS VERIFIED"), ("LIVE", "DRAWTOMATA.VERCEL.APP")],
    ),
    "imazin": dict(
        name="IMAZINTHECOMICS", status="SEARCH · SEMANTIC", repo="imazinthecomicz",
        headline="Describe the story. Get the comic.",
        sub="Sentence embeddings + a hybrid ranker over manga, manhwa, Marvel, DC and Western titles.",
        chip_list=["SENTENCE EMBEDDINGS", "HYBRID RANKING", "FASTAPI", "NEXT.JS"],
        diagram=d_imazin,
        metric_items=[("3,500+", "TITLES INDEXED"), ("2", "DATA SOURCES"), ("5", "CATALOGUES")],
    ),
    "shortlist": dict(
        name="SMART SHORTLISTING ENGINE", status="HACKATHON · INTERNLOOM", repo="smart-shortlisting-engine",
        headline="Rank resumes against a JD. Explain every pick.",
        sub="Exact skill parsing fused with local semantic matching. Nothing leaves the machine.",
        chip_list=["ALL-MINILM-L6-V2", "HYBRID NLP", "PRIVACY-FIRST"],
        diagram=d_shortlist,
        metric_items=[("0", "EXTERNAL API CALLS"), ("100%", "LOCAL INFERENCE"), ("TOP 3", "EXPLAINED")],
    ),
    "gradintern": dict(
        name="GRADINTERN", status="FULL-STACK · REST", repo="gradintern",
        headline="An internship portal with real access control.",
        sub="Three roles, stateless JWT auth and RBAC middleware guarding every write route.",
        chip_list=["REACT 19", "EXPRESS 5", "MONGODB ATLAS", "JWT + RBAC"],
        diagram=d_gradintern,
        metric_items=[("15", "API TESTS"), ("100%", "ROUTE COVERAGE"), ("~1 ms", "P50 API OVERHEAD")],
    ),
    "brofessor": dict(
        name="BROFESSOR", status="IN DEVELOPMENT", repo="Brofessor",
        headline="An AI tutor that teaches on a whiteboard.",
        sub="Feed it slides or a PDF. It plans the lesson, draws it and explains it like a professor.",
        chip_list=["AI TUTOR", "STROKE RENDERING", "EN / HINGLISH", "DOUBT CHAT"],
        diagram=d_brofessor,
        metric_items=[("0", "GENERATED IMAGES"), ("2", "NARRATION LANGUAGES"), ("PDF/PPT", "INPUT MATERIAL")],
    ),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for i, (key, c) in enumerate(CARDS.items(), start=1):
        svg = card(i, c["name"], c["status"], c["repo"], c["headline"], c["sub"],
                   c["chip_list"], c["diagram"](), c["metric_items"])
        with open(os.path.join(OUT, f"card-{key}.svg"), "w", encoding="utf-8") as f:
            f.write(svg)
    print(f"{len(CARDS)} cards written")


if __name__ == "__main__":
    main()
