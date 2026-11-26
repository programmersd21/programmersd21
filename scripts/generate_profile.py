import json
import os
import urllib.request
from xml.sax.saxutils import escape

OWNER = "programmersd21"
PROJECTS = [
    ("flow", "Network throughput, made readable", "Go · terminal", "#18A999", "F"),
    ("wallr", "Animated wallpapers for Wayland", "Rust · Wayland", "#8267E8", "W"),
    ("pyratatui", "Ratatui, with a Python API", "Python · Rust", "#477DE0", "P"),
    ("mew", "A compact terminal project card", "Rust · terminal", "#D66C91", "M"),
    ("ratatui-skill", "Better Ratatui apps from AI assistants", "Rust · agent skills", "#B58AE8", "R"),
    ("scribe", "Offline speech-to-text in the terminal", "Rust · whisper.cpp", "#D98752", "S"),
]

def fetch_repo(name):
    request = urllib.request.Request(
        f"https://api.github.com/repos/{OWNER}/{name}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "programmersd21-profile-generator",
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.load(response)
    return data["stargazers_count"], data["forks_count"]

def build_svg(stats):
    total_stars = sum(value[0] for value in stats.values())
    total_forks = sum(value[1] for value in stats.values())
    cards = []
    for index, (name, description, stack, accent, initial) in enumerate(PROJECTS):
        stars, forks = stats[name]
        x = 48 + (index % 2) * 480
        y = 188 + (index // 2) * 166
        delay = index * 0.12
        cards.append(f"""
        <g class="project" transform="translate({x} {y})" style="--accent:{accent}">
          <rect class="card" width="448" height="142" rx="20"/>
          <rect class="card-edge" x=".5" y=".5" width="447" height="141" rx="19.5"/>
          <rect class="accent-wash" width="4" height="142" rx="2"/>
          <g class="intro" style="--delay:{delay}s">
            <rect x="22" y="22" width="44" height="44" rx="13" class="mark"/>
            <text x="44" y="51" text-anchor="middle" class="mark-letter">{escape(initial)}</text>
            <text x="82" y="39" class="project-name">{escape(name)}</text>
            <text x="82" y="61" class="project-stack">{escape(stack)}</text>
            <text x="22" y="94" class="description">{escape(description)}</text>
            <g class="stats" transform="translate(22 119)">
              <path d="M7 -7 L9.1 -2.4 L14 -2 L10.3 1.2 L11.5 6 L7 3.4 L2.5 6 L3.7 1.2 L0 -2 L4.9 -2.4 Z" class="star"/>
              <text x="20" y="4" class="stat-number">{stars:,}</text>
              <path d="M103 -5 C99 -5 97 -2 97 1 C97 4 99 6 102 6 L105 6 L105 3 L102 3 C101 3 100 2 100 1 C100 0 101 -1 102 -1 L105 -1 L105 -5 Z M111 -5 L108 -5 L108 -1 L111 -1 C112 -1 113 0 113 1 C113 2 112 3 111 3 L108 3 L108 6 L111 6 C114 6 116 4 116 1 C116 -2 114 -5 111 -5 Z M103 0 L109 0 L109 2 L103 2 Z" class="fork"/>
              <text x="124" y="4" class="stat-number">{forks:,}</text>
            </g>
          </g>
          <path class="glint" d="M-110 0 L-30 0 L-110 142 L-190 142 Z">
            <animateTransform attributeName="transform" type="translate" values="0 0;650 0;650 0" keyTimes="0;0.22;1" dur="32s" begin="{index * 1.7}s" repeatCount="indefinite"/>
          </path>
          <rect class="focus-line" x="22" y="139" width="0" height="2" rx="1">
            <animate attributeName="width" values="0;0;404;404;0" keyTimes="0;0.08;0.18;0.82;1" dur="32s" begin="{index * 1.7}s" repeatCount="indefinite"/>
          </rect>
        </g>""")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="744" viewBox="0 0 1040 744" role="img" aria-labelledby="title desc">
<title id="title">programmersd21 — selected projects</title>
<desc id="desc">A live overview of six open-source projects, with current GitHub star and fork counts.</desc>
<defs>
  <linearGradient id="canvas" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#FCFBF9"/><stop offset="1" stop-color="#F1F0ED"/></linearGradient>
  <radialGradient id="ambient" cx="85%" cy="0%" r="85%"><stop stop-color="#DCD5F7" stop-opacity=".48"/><stop offset="1" stop-color="#DCD5F7" stop-opacity="0"/></radialGradient>
  <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#FFFFFF" stop-opacity=".96"/><stop offset="1" stop-color="#FFFFFF" stop-opacity=".76"/></linearGradient>
  <linearGradient id="glint" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#FFFFFF" stop-opacity="0"/><stop offset=".5" stop-color="#FFFFFF" stop-opacity=".72"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>
  <filter id="shadow" x="-15%" y="-20%" width="130%" height="150%"><feDropShadow dx="0" dy="9" stdDeviation="15" flood-color="#292633" flood-opacity=".075"/></filter>
  <style>
    .sans{{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
    .mono{{font-family:ui-monospace,"SFMono-Regular",Consolas,monospace}}
    .eyebrow{{font:11px ui-monospace,monospace;letter-spacing:1.5px;fill:#898693}}
    .headline{{font:650 35px Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;letter-spacing:-1.5px;fill:#292733}}
    .subhead{{font:14px Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#777481}}
    .metric-label{{font:11px Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#898693}}
    .metric-value{{font:600 19px Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#302E39}}
    .card{{fill:url(#glass);filter:url(#shadow)}}
    .card-edge{{fill:none;stroke:#FFFFFF;stroke-width:1}}
    .accent-wash{{fill:var(--accent);opacity:.9}}
    .mark{{fill:var(--accent);fill-opacity:.11;stroke:var(--accent);stroke-opacity:.17}}
    .mark-letter{{font:600 19px Inter,sans-serif;fill:var(--accent)}}
    .project-name{{font:600 18px Inter,sans-serif;letter-spacing:-.35px;fill:#302E39}}
    .project-stack{{font:11px ui-monospace,monospace;fill:#898693}}
    .description{{font:13px Inter,sans-serif;fill:#64616D}}
    .star{{fill:#D69A35}}
    .fork{{fill:#9A96A3}}
    .stat-number{{font:12px ui-monospace,monospace;fill:#696673}}
    .glint{{fill:url(#glint);opacity:.55}}
    .focus-line{{fill:var(--accent);opacity:.7}}
    .intro{{opacity:0;animation:rise .9s cubic-bezier(.16,1,.3,1) forwards;animation-delay:var(--delay)}}
    @keyframes rise{{from{{opacity:0;transform:translateY(9px)}}to{{opacity:1;transform:translateY(0)}}}}
    @media (prefers-reduced-motion: reduce){{.intro{{animation:none;opacity:1}}}}
  </style>
</defs>
<rect width="1040" height="744" rx="28" fill="url(#canvas)"/>
<rect width="1040" height="744" rx="28" fill="url(#ambient)"/>
<circle cx="975" cy="690" r="220" fill="#D9E9E6" opacity=".22">
  <animate attributeName="opacity" values=".14;.28;.14" dur="18s" repeatCount="indefinite"/>
</circle>
<g class="sans">
  <text x="48" y="52" class="eyebrow">INDEPENDENT SOFTWARE / OPEN SOURCE</text>
  <text x="48" y="104" class="headline">Built with curiosity.</text>
  <text x="48" y="132" class="subhead">A small collection of tools for terminals, systems and better developer workflows.</text>
  <g transform="translate(752 48)">
    <rect width="240" height="94" rx="18" fill="#FFFFFF" fill-opacity=".66" stroke="#FFFFFF" filter="url(#shadow)"/>
    <text x="20" y="29" class="metric-label">COMMUNITY</text>
    <text x="20" y="57" class="metric-value">{total_stars:,} stars</text>
    <text x="20" y="78" class="metric-label">{total_forks:,} forks · across {len(PROJECTS)} projects</text>
    <circle cx="216" cy="24" r="4" fill="#3EAD85">
      <animate attributeName="opacity" values=".45;1;.45" dur="3.6s" repeatCount="indefinite"/>
    </circle>
  </g>
</g>
<g>{''.join(cards)}</g>
<path d="M48 708 H992" stroke="#DCD9D4" stroke-width="1"/>
<text x="48" y="728" class="mono" font-size="10.5" fill="#96929D">github.com/programmersd21</text>
<text x="992" y="728" text-anchor="end" class="mono" font-size="10.5" fill="#96929D">LIVE REPOSITORY METRICS · REFRESHED BY GITHUB ACTIONS</text>
</svg>'''

def main():
    stats = {name: fetch_repo(name) for name, *_ in PROJECTS}
    with open("profile.svg", "w", encoding="utf-8") as file:
        file.write(build_svg(stats) + "\n")

if __name__ == "__main__":
    main()
