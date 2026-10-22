"""Generate the red matrix-rain profile header (assets/header.svg).

Deterministic (seeded), standard library only. Run: python3 scripts/header.py
"""
import os
import random
from html import escape

W, H = 1200, 280
COL_W = 20
ROWS = 30
FONT = "'JetBrains Mono', 'Fira Code', Consolas, Menlo, monospace"
GLYPHS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789Z:.=*+-<>|"

NAME = "SURYANSH VERMA"
TAGLINE = "cloud  //  ai-ml  //  data"

rng = random.Random(1337)
OUT = os.environ.get("OUT_DIR", "assets")


def rain():
    cols = []
    for i in range(W // COL_W + 1):
        x = i * COL_W + 4
        dur = rng.uniform(5.5, 12.0)
        delay = -rng.uniform(0, dur)
        size = rng.choice([14, 15, 16, 16, 17, 18])
        depth = rng.uniform(0.35, 1.0)  # far columns are dimmer
        spans = []
        for r in range(ROWS):
            ch = escape(rng.choice(GLYPHS))
            # tail fades upward, head (last row) is brightest
            t = (r + 1) / ROWS
            if r == ROWS - 1:
                spans.append(f'<tspan x="{x}" dy="{COL_W}" class="hd">{ch}</tspan>')
            else:
                op = round(depth * t ** 1.6, 2)
                if op < 0.04:
                    continue
                flick = ' class="fl"' if rng.random() < 0.08 else ""
                spans.append(
                    f'<tspan x="{x}" y="{r * COL_W}" fill-opacity="{op}"{flick}>{ch}</tspan>'
                )
        cols.append(
            f'<text class="col" font-size="{size}" '
            f'style="animation-duration:{dur:.2f}s;animation-delay:{delay:.2f}s">'
            + "".join(spans)
            + "</text>"
        )
    return "\n    ".join(cols)


def build():
    span = ROWS * COL_W
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="14"/></clipPath>
    <radialGradient id="vignette" cx="0.5" cy="0.5" r="0.62">
      <stop offset="0" stop-color="#050000" stop-opacity="0.92"/>
      <stop offset="0.45" stop-color="#050000" stop-opacity="0.55"/>
      <stop offset="1" stop-color="#050000" stop-opacity="0"/>
    </radialGradient>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="1" fill="#000" fill-opacity="0.35"/>
    </pattern>
    <filter id="glow" x="-20%" y="-60%" width="140%" height="220%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="soft"><feGaussianBlur stdDeviation="0.6"/></filter>
  </defs>
  <style>
    .col {{ font-family: {FONT}; fill: #ff1f1f; animation: fall linear infinite; }}
    .hd {{ fill: #ffe3e3; fill-opacity: 1; }}
    .fl {{ animation: flick 1.7s steps(2) infinite; }}
    @keyframes fall {{ from {{ transform: translateY(-{span}px); }} to {{ transform: translateY({H + 40}px); }} }}
    @keyframes flick {{ 50% {{ fill: #ffb3b3; }} }}
    .name {{ font: 800 64px {FONT}; letter-spacing: 6px; }}
    .g1 {{ fill: #ff003c; opacity: .7; animation: g1 3.2s infinite steps(1); }}
    .g2 {{ fill: #7a0000; opacity: .8; animation: g2 3.2s infinite steps(1); }}
    @keyframes g1 {{ 0%,88%,100% {{ transform: none; }} 90% {{ transform: translate(-4px,1px); }} 93% {{ transform: translate(3px,-2px); }} 96% {{ transform: translate(-2px,0); }} }}
    @keyframes g2 {{ 0%,88%,100% {{ transform: none; }} 90% {{ transform: translate(4px,-1px); }} 93% {{ transform: translate(-3px,2px); }} 96% {{ transform: translate(2px,1px); }} }}
    .tag {{ font: 500 20px {FONT}; fill: #ff4d4d; letter-spacing: 3px; }}
    .cur {{ fill: #ff2b2b; animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    .meta {{ font: 400 12px {FONT}; fill: #8a2a2a; letter-spacing: 2px; }}
    .sweep {{ animation: sweep 6s linear infinite; }}
    @keyframes sweep {{ from {{ transform: translateY(-40px); }} to {{ transform: translateY({H + 40}px); }} }}
  </style>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="#050000"/>
    {rain()}
    <rect width="{W}" height="{H}" fill="url(#vignette)"/>
    <rect class="sweep" width="{W}" height="40" fill="#ff1f1f" fill-opacity="0.04"/>
    <rect width="{W}" height="{H}" fill="url(#scan)"/>
  </g>
  <text x="600" y="138" text-anchor="middle" class="name g2">{NAME}</text>
  <text x="600" y="138" text-anchor="middle" class="name g1">{NAME}</text>
  <text x="600" y="138" text-anchor="middle" class="name" fill="#ff2b2b" filter="url(#glow)">{NAME}</text>
  <text x="600" y="138" text-anchor="middle" class="name" fill="#fff0f0" fill-opacity="0.85" filter="url(#soft)">{NAME}</text>
  <text x="588" y="186" text-anchor="middle" class="tag">&gt; {escape(TAGLINE)}</text>
  <rect class="cur" x="{588 + (len(TAGLINE) + 2) * 7.5 - 26:.0f}" y="170" width="11" height="20"/>
  <text x="24" y="{H - 18}" class="meta">SYS://SLAZZINC0DE</text>
  <text x="{W - 24}" y="{H - 18}" text-anchor="end" class="meta">MIT_BENGALURU · CSE</text>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="#3a0808"/>
</svg>
"""


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "header.svg"), "w", encoding="utf-8") as f:
        f.write(build())
    print("header written")
