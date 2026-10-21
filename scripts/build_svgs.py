"""Generates the animated SVGs for the MrithikaOS profile README."""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

FONT = "'JetBrains Mono','Fira Code','Cascadia Code',Consolas,Menlo,monospace"
BG, BAR, PANE, EDGE = "#0B0E14", "#161B24", "#0F131C", "#222A38"
AMBER, VIOLET, CYAN, GREEN = "#F0A532", "#B57BFF", "#00D8F0", "#3DDC97"
WHITE, TEXT, DIM, MUTED = "#E6EDF3", "#C9D1D9", "#484F58", "#6E7681"

W, H = 1000, 640


def neural_net(x0, y0):
    """Self-drawing 3-4-4-2 network inside the left pane."""
    xs = [x0 + 30, x0 + 90, x0 + 150, x0 + 210]
    layers = [
        [y0 + 70, y0 + 130, y0 + 190],
        [y0 + 40, y0 + 100, y0 + 160, y0 + 220],
        [y0 + 40, y0 + 100, y0 + 160, y0 + 220],
        [y0 + 100, y0 + 160],
    ]
    colors = [CYAN, "#7AA2FF", "#9B8CFF", VIOLET]
    out = []
    for li in range(3):
        delay = 0.4 + li * 0.9
        for a in layers[li]:
            for b in layers[li + 1]:
                out.append(
                    f'<line class="e" style="animation-delay:{delay:.1f}s" pathLength="100" '
                    f'x1="{xs[li]}" y1="{a}" x2="{xs[li+1]}" y2="{b}"/>'
                )
    for li, ys in enumerate(layers):
        r = 8 if li == 3 else 7
        for y in ys:
            out.append(
                f'<circle class="n" style="animation-delay:{0.2 + li*0.9:.1f}s" '
                f'cx="{xs[li]}" cy="{y}" r="{r}" fill="{colors[li]}"/>'
            )
    for y in layers[3]:
        out.append(f'<circle class="glow" cx="{xs[3]}" cy="{y}" r="15"/>')
    paths = [
        (CYAN, 3.4, [(0, 0), (1, 1), (2, 2), (3, 0)]),
        (VIOLET, 3.9, [(0, 2), (1, 2), (2, 0), (3, 1)]),
        (GREEN, 4.4, [(0, 1), (1, 0), (2, 3), (3, 0)]),
        (AMBER, 4.9, [(0, 0), (1, 3), (2, 1), (3, 1)]),
    ]
    for color, begin, pts in paths:
        d = "M" + " L".join(f"{xs[l]} {layers[l][i]}" for l, i in pts)
        out.append(
            f'<circle r="3" fill="{color}"><animateMotion dur="1.8s" begin="{begin}s" '
            f'repeatCount="indefinite" path="{d}"/></circle>'
        )
    return "\n".join(out)


PORTRAIT = (Path(__file__).resolve().parent.parent / "assets" / "portrait.txt").read_text(encoding="utf-8").rstrip("\n").split("\n")
PCOLS = max(len(r) for r in PORTRAIT)
P_W = 340                       # rendered width of the portrait block
P_ADV = P_W / PCOLS             # per-character advance
P_LH = P_ADV / 0.55             # line height matching the converter's aspect
P_FS = P_ADV / 0.6
PBOTTOM = 106 + len(PORTRAIT) * P_LH


def portrait(x, y):
    rows = []
    for i, r in enumerate(PORTRAIT):
        if not r.strip():
            continue
        r = r.ljust(PCOLS)
        rows.append(f'<text x="{x}" y="{y + i*P_LH:.2f}" class="pr" style="animation-delay:{0.2 + i*0.045:.2f}s" '
                    f'textLength="{P_W}" lengthAdjust="spacing" xml:space="preserve">{escape(r)}</text>')
    h = len(PORTRAIT) * P_LH
    return (f'<g class="float"><g fill="url(#pg)">{"".join(rows)}</g></g>'
            f'<rect class="scan" x="{x-6}" y="{y-8}" width="{P_W+12}" height="2" fill="{CYAN}" opacity="0"/>'
            f'<defs><linearGradient id="pg" x1="{x}" y1="{y}" x2="{x+P_W}" y2="{y+h:.0f}" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="#E6F4FF"/><stop offset=".55" stop-color="{CYAN}"/>'
            f'<stop offset="1" stop-color="{VIOLET}"/></linearGradient></defs>')


def kv(key, val, keyw=12):
    dots = "." * max(2, keyw - len(key))
    return (f'<tspan class="k">{escape(key)}</tspan> <tspan class="d">{dots}</tspan> '
            f'<tspan class="v">{escape(val)}</tspan>')


def section(title, total=56):
    rule = "─" * max(4, total - len(title) - 5)
    return f'<tspan class="d">───</tspan> <tspan class="h">{escape(title)}</tspan> <tspan class="d">{rule}</tspan>'


def hero():
    px, rx = 20, 420
    lines = []  # (y, inner_markup)
    y = 186
    for k, v in [
        ("Role", "AI/ML & Full Stack Developer"),
        ("Education", "B.Tech CSE · 2024–2028"),
        ("College", "SRMIST Kattankulathur, Chennai"),
        ("Focus", "GenAI · Agentic AI · Scalable Web Apps"),
    ]:
        lines.append((y, kv(k, v))); y += 20
    y += 12
    lines.append((y, section("Internships"))); y += 24
    for role, org, when in [
        ("IT Department Intern", "Integral Coach Factory (ICF) / Indian Railways", "Jun 2026"),
        ("Deep Learning & ML Research Intern", "AI Quantum Smart Solutions Pvt. Ltd.", "May–Jul 2026"),
        ("Remote Sensing & GIS Intern", "India Space Academy", "Jan 2026"),
    ]:
        lines.append((y, f'<tspan class="g">▸</tspan> <tspan class="k">{escape(role)}</tspan> '
                         f'<tspan class="m">· {escape(when)}</tspan>')); y += 18
        lines.append((y, f'<tspan class="v" dx="18">{escape(org)}</tspan>')); y += 24
    y += 4
    lines.append((y, section("Stack"))); y += 24
    for k, v in [
        ("Languages", "Python, Java, JavaScript, TypeScript, C"),
        ("Frontend", "React, Next.js, React Native, Vite"),
        ("Backend", "FastAPI, Flask, Node.js, Express, Spring Boot"),
        ("AI / ML", "PyTorch, TensorFlow, Keras, scikit-learn, OpenCV"),
        ("Data", "PostgreSQL, MySQL, Oracle, Neo4j, SQLite"),
        ("Cloud", "AWS, GCP, Docker, Git, Linux"),
    ]:
        lines.append((y, kv(k, v))); y += 20
    y += 12
    lines.append((y, section("Contact"))); y += 24
    for k, v in [
        ("LinkedIn", "in/mrithika-kumar-a12865316"),
        ("Mail", "mrithikakumar1112@gmail.com"),
        ("GitHub", "github.com/Mrithikahub"),
    ]:
        lines.append((y, kv(k, v))); y += 20
    prompt_y = y + 18
    height = prompt_y + 30

    body = []
    for i, (ly, inner) in enumerate(lines):
        body.append(f'<text class="ln" x="{rx}" y="{ly}" style="animation-delay:{1.6 + i*0.07:.2f}s">{inner}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="Mrithika K - AI/ML and Full Stack Developer">
<title>Mrithika K — AI/ML &amp; Full Stack Developer</title>
<style>
text{{font-family:{FONT};font-size:13px}}
.k{{fill:{WHITE};font-weight:700}} .v{{fill:{TEXT}}} .d{{fill:{DIM}}} .h{{fill:{AMBER};font-weight:700}}
.m{{fill:{MUTED}}} .g{{fill:{GREEN}}} .c{{fill:{CYAN}}} .p{{fill:{VIOLET}}}
.tb{{fill:{MUTED};font-size:12px}}
.pr{{font-size:{P_FS:.2f}px;font-weight:700;opacity:0;animation:fi .3s ease forwards}}
.float{{animation:fl 6s ease-in-out infinite 2.5s}}
.scan{{animation:sc 4.5s linear infinite 2.2s}}
@keyframes fl{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-3px)}}}}
@keyframes sc{{0%{{opacity:.5;transform:translateY(0)}}100%{{opacity:.5;transform:translateY({len(PORTRAIT)*P_LH+10:.0f}px)}}}}
.name{{font-size:34px;font-weight:800;fill:{WHITE};letter-spacing:1px}}
.ln{{opacity:0;animation:fi .35s ease forwards}}
.e{{stroke:#2C3A55;stroke-width:1;fill:none;stroke-dasharray:100;stroke-dashoffset:100;animation:dr 1s ease forwards}}
.n{{opacity:0;animation:fi .4s forwards}}
.glow{{fill:none;stroke:{VIOLET};stroke-width:1.2;opacity:0;animation:pu 2s infinite 3.4s}}
.bar{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:gr 7s linear infinite 3s}}
.cur{{animation:bl 1s steps(1) infinite}}
.typed{{animation:ty 1.6s steps(10) forwards .3s}}
.r1,.r2,.r3{{opacity:0;animation:rc 9s infinite}}
.r1{{animation-delay:1.9s}} .r2{{animation-delay:4.9s}} .r3{{animation-delay:7.9s}}
@keyframes fi{{to{{opacity:1}}}}
@keyframes dr{{to{{stroke-dashoffset:0}}}}
@keyframes pu{{0%,100%{{opacity:0}}50%{{opacity:1}}}}
@keyframes gr{{0%{{transform:scaleX(0)}}75%,100%{{transform:scaleX(1)}}}}
@keyframes bl{{50%{{opacity:0}}}}
@keyframes ty{{from{{width:0}}to{{width:230px}}}}
@keyframes rc{{0%{{opacity:0}}3%{{opacity:1}}31%{{opacity:1}}34%,100%{{opacity:0}}}}
</style>
<defs><clipPath id="nameclip"><rect class="typed" x="{rx}" y="88" width="0" height="50"/></clipPath></defs>
<rect width="{W}" height="{height}" rx="14" fill="{BG}" stroke="{EDGE}"/>
<path d="M14 0 H{W-14} A14 14 0 0 1 {W} 14 V38 H0 V14 A14 14 0 0 1 14 0 Z" fill="{BAR}"/>
<circle cx="24" cy="19" r="6" fill="#FF5F57"/><circle cx="44" cy="19" r="6" fill="#FEBC2E"/><circle cx="64" cy="19" r="6" fill="#28C840"/>
<text class="tb" x="{W/2}" y="23" text-anchor="middle">mrithika — ~/about_me — zsh — 120×42</text>

<rect x="{px}" y="56" width="370" height="{height-76}" rx="10" fill="{PANE}" stroke="{EDGE}"/>
<text x="{px+18}" y="82" class="c" font-weight="700" letter-spacing="2" font-size="11">VISUAL.MAP</text>
<text x="{px+352}" y="82" class="m" font-size="11" text-anchor="end">ascii · {PCOLS}×{len(PORTRAIT)}</text>
{portrait(px + 15, 106)}
<text x="{px+185}" y="{PBOTTOM + 34}" class="v" text-anchor="middle" font-size="12"><tspan class="g">~/mrithika $</tspan> ./render --ascii</text>
<text x="{px+18}" y="{PBOTTOM + 78}" class="g">model.fit(<tspan class="p">mrithika</tspan>) · epoch 42/42</text>
<rect x="{px+18}" y="{PBOTTOM + 90}" width="334" height="8" rx="3" fill="#1C2433"/>
<rect class="bar" x="{px+18}" y="{PBOTTOM + 90}" width="334" height="8" rx="3" fill="{GREEN}"/>
<text class="m" x="{px+18}" y="{PBOTTOM + 122}" font-size="12">status: <tspan class="g">ready to ship ✓</tspan></text>

<text x="{rx}" y="74"><tspan class="h">mrithika</tspan><tspan class="v">@</tspan><tspan class="h">srmist</tspan> <tspan class="d">{"─"*38}</tspan></text>
<text class="name" x="{rx}" y="124" clip-path="url(#nameclip)">Mrithika <tspan class="p">K</tspan></text>
<rect class="cur" x="{rx+236}" y="98" width="12" height="30" fill="{AMBER}" opacity="0.9"/>
<text class="r1" x="{rx}" y="150"><tspan class="c">❯</tspan> <tspan class="v">AI/ML Engineer — models that learn</tspan></text>
<text class="r2" x="{rx}" y="150"><tspan class="c">❯</tspan> <tspan class="v">Full Stack Developer — apps that ship</tspan></text>
<text class="r3" x="{rx}" y="150"><tspan class="c">❯</tspan> <tspan class="v">Building GenAI &amp; agentic systems</tspan></text>
{chr(10).join(body)}
<text class="ln" x="{rx}" y="{prompt_y}" style="animation-delay:{1.6 + len(lines)*0.07:.2f}s"><tspan class="h">mrithika</tspan><tspan class="v">@</tspan><tspan class="h">github</tspan> <tspan class="v">~ %</tspan></text>
<rect class="cur" x="{rx+160}" y="{prompt_y-12}" width="8" height="15" fill="{AMBER}"/>
</svg>'''
    (OUT / "hero.svg").write_text(svg, encoding="utf-8")


def divider(name, label, icon_color=VIOLET):
    w, h = 900, 64
    spaced = " ".join(label.upper())
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">
<style>
text{{font-family:{FONT}}}
.l{{stroke:{EDGE};stroke-width:1.5}}
.t{{font-size:20px;font-weight:800;fill:{AMBER}}}
.s{{font-size:13px;fill:{MUTED}}}
.dot{{animation:pu 1.6s ease-in-out infinite}}
@keyframes pu{{0%,100%{{opacity:.3}}50%{{opacity:1}}}}
@keyframes sweep{{from{{stroke-dashoffset:300}}to{{stroke-dashoffset:0}}}}
.sw{{stroke:{icon_color};stroke-width:1.5;stroke-dasharray:40 260;animation:sweep 3s linear infinite}}
</style>
<line class="l" x1="40" y1="32" x2="300" y2="32"/><line class="l" x1="600" y1="32" x2="860" y2="32"/>
<line class="sw" x1="40" y1="32" x2="300" y2="32"/><line class="sw" x1="600" y1="32" x2="860" y2="32"/>
<circle class="dot" cx="310" cy="32" r="4" fill="{icon_color}"/><circle class="dot" cx="590" cy="32" r="4" fill="{icon_color}" style="animation-delay:.8s"/>
<text class="t" x="450" y="39" text-anchor="middle">{escape(spaced)}</text>
</svg>'''
    (OUT / f"div-{name}.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    hero()
    for n, l, c in [("tools", "Tools", VIOLET), ("experience", "Experience", CYAN),
                    ("projects", "Projects", GREEN), ("stats", "Stats", AMBER)]:
        divider(n, l, c)
    print("built:", sorted(p.name for p in OUT.iterdir()))
