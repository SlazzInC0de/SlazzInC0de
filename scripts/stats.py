"""Generate self-hosted GitHub stats and top-languages SVG cards.

Runs inside GitHub Actions with GITHUB_TOKEN; standard library only.
"""
import json
import os
import urllib.request
from html import escape

USER = os.environ.get("GH_USER", "SlazzInC0de")
TOKEN = os.environ["GH_TOKEN"]
OUT = os.environ.get("OUT_DIR", "assets")

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      restrictedContributionsCount
      contributionCalendar { totalContributions }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""

BG = "#070101"
BORDER = "#3a0808"
TITLE = "#ff2b2b"
TEXT = "#ffe3e3"
MUTED = "#a35a5a"
FONT = "'JetBrains Mono', 'Fira Code', Consolas, Menlo, monospace"
# red ramp for language slices, brightest = most used
RAMP = ["#ff2b2b", "#d91e1e", "#ff6b6b", "#a31515", "#ff9e9e", "#6e0e0e"]


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.load(resp)
    if "errors" in body:
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]["user"]


def frame(width, height, title, inner):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <style>
    .t {{ font: 700 16px {FONT}; fill: {TITLE}; letter-spacing: 1px; }}
    .l {{ font: 400 13px {FONT}; fill: {MUTED}; }}
    .v {{ font: 700 13px {FONT}; fill: {TEXT}; }}
    .big {{ font: 800 30px {FONT}; fill: {TEXT}; }}
    .cap {{ font: 500 11px {FONT}; fill: {MUTED}; letter-spacing: 1.5px; }}
    .row {{ animation: fade .6s ease-out backwards; }}
    @keyframes fade {{ from {{ opacity: 0; transform: translateX(-6px); }} to {{ opacity: 1; transform: none; }} }}
    @keyframes grow {{ from {{ stroke-dashoffset: 251; }} }}
    .cur {{ animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
  </style>
  <defs><pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#ff2b2b" fill-opacity="0.025"/></pattern></defs>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" fill="url(#scan)"/>
  <text x="25" y="38" class="t">&gt; {escape(title)}<tspan class="cur">_</tspan></text>
{inner}
</svg>
"""


def stats_card(u):
    c = u["contributionsCollection"]
    repos = u["repositories"]
    stars = sum(r["stargazerCount"] for r in repos["nodes"])
    total = c["contributionCalendar"]["totalContributions"]
    rows = [
        ("Total Stars", stars),
        ("Commits (last year)", c["totalCommitContributions"]),
        ("Pull Requests", c["totalPullRequestContributions"]),
        ("Issues", c["totalIssueContributions"]),
        ("Public Repositories", repos["totalCount"]),
    ]
    inner = []
    for i, (label, value) in enumerate(rows):
        y = 76 + i * 26
        inner.append(
            f'  <g class="row" style="animation-delay:{150 + i * 120}ms">'
            f'<rect x="27" y="{y - 9}" width="8" height="8" fill="{TITLE}"/>'
            f'<text x="45" y="{y}" class="l">{label}</text>'
            f'<text x="255" y="{y}" class="v" text-anchor="end">{value}</text></g>'
        )
    # ring: contributions in the last year, fills toward a 365 target
    frac = min(total / 365, 1.0)
    dash = 251.2
    inner.append(
        f'  <g transform="translate(345,113)">'
        f'<circle r="40" fill="none" stroke="{BORDER}" stroke-width="8"/>'
        f'<circle r="40" fill="none" stroke="{TITLE}" stroke-width="8" stroke-linecap="butt" '
        f'stroke-dasharray="{dash}" stroke-dashoffset="{dash * (1 - frac):.1f}" transform="rotate(-90)" '
        f'style="animation: grow 1.2s ease-out"/>'
        f'<text y="10" class="big" text-anchor="middle">{total}</text>'
        f'<text y="64" class="cap" text-anchor="middle">CONTRIBUTIONS</text></g>'
    )
    return frame(450, 200, "GitHub Stats", "\n".join(inner))


def langs_card(u):
    totals = {}
    colors = {}
    for repo in u["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            totals[name] = totals.get(name, 0) + edge["size"]
    top = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:6]
    colors = {name: RAMP[i] for i, (name, _) in enumerate(top)}
    grand = sum(v for _, v in top) or 1

    inner = [f'  <clipPath id="bar"><rect x="25" y="58" width="400" height="10" rx="1"/></clipPath>',
             '  <g clip-path="url(#bar)">']
    x = 25.0
    for name, size in top:
        w = 400 * size / grand
        inner.append(f'    <rect x="{x:.2f}" y="58" width="{w + 0.5:.2f}" height="10" fill="{colors[name]}"/>')
        x += w
    inner.append("  </g>")

    for i, (name, size) in enumerate(top):
        col, row = i % 2, i // 2
        cx = 31 + col * 210
        cy = 102 + row * 32
        pct = 100 * size / grand
        inner.append(
            f'  <g class="row" style="animation-delay:{150 + i * 100}ms">'
            f'<rect x="{cx - 5}" y="{cy - 10}" width="10" height="10" fill="{colors[name]}"/>'
            f'<text x="{cx + 14}" y="{cy}" class="v">{escape(name)}</text>'
            f'<text x="{cx + 185}" y="{cy}" class="l" text-anchor="end">{pct:.1f}%</text></g>'
        )
    return frame(450, 200, "Most Used Languages", "\n".join(inner))


def main():
    u = fetch()
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "stats.svg"), "w", encoding="utf-8") as f:
        f.write(stats_card(u))
    with open(os.path.join(OUT, "langs.svg"), "w", encoding="utf-8") as f:
        f.write(langs_card(u))
    print("cards written")


if __name__ == "__main__":
    main()
