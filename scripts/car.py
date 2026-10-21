"""Builds an animated 'car' SVG from a GitHub contribution graph.

A car drives along a road under the grid. Every column it passes changes
colour (purple -> cyan); on the next lap it drives through again and turns
them back. Loops forever.

Usage:
    python scripts/car.py <github_user> <out_dir>
    python scripts/car.py --demo <out_dir>      # random data, no network
"""
import random
import re
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

CELL, GAP = 12, 3
STEP = CELL + GAP
PAD_X, PAD_Y = 40, 70
DURATION = 14  # seconds for two laps (colour on, colour off)
FONT = "'JetBrains Mono','Fira Code',Consolas,Menlo,monospace"

THEMES = {
    "dark": {
        "bg": "#0B0E14", "text": "#C9D1D9", "muted": "#6E7681", "amber": "#F0A532",
        "a": ["#161B22", "#3B2470", "#5B34B0", "#8A55F0", "#B57BFF"],
        "b": ["#10232A", "#0B4F5C", "#0A7F91", "#00B4CC", "#00E5FF"],
        "car": "#B57BFF", "glass": "#1E293B", "road": "#111722", "lane": "#F0A532",
    },
    "light": {
        "bg": "#FFFFFF", "text": "#24292F", "muted": "#6E7781", "amber": "#BF7A12",
        "a": ["#EBEDF0", "#E3D2FF", "#C3A0FF", "#9B6BF2", "#7034D9"],
        "b": ["#E6F7FA", "#A8E9F2", "#5CCFE0", "#1BA6BD", "#0A7286"],
        "car": "#7034D9", "glass": "#DBEAFE", "road": "#E5E7EB", "lane": "#BF7A12",
    },
}


def fetch(user):
    req = urllib.request.Request(
        f"https://github.com/users/{user}/contributions",
        headers={"User-Agent": "Mozilla/5.0 (car-svg)"},
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    days = {}
    for tag in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html):
        d = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', tag)
        lv = re.search(r'data-level="(\d)"', tag)
        if d and lv:
            days[date.fromisoformat(d.group(1))] = int(lv.group(1))
    if len(days) < 300:
        raise SystemExit(f"Parsed only {len(days)} days — page format may have changed")
    return days


def demo():
    end = date.today()
    rnd = random.Random(7)
    return {end - timedelta(days=i): rnd.choices([0, 1, 2, 3, 4], [40, 25, 18, 10, 7])[0]
            for i in range(371)}


def to_grid(days):
    """Columns of 7 (Sun..Sat) like GitHub's calendar."""
    start = min(days)
    start -= timedelta(days=(start.weekday() + 1) % 7)
    cols = []
    cur = start
    end = max(days)
    while cur <= end:
        col = []
        for r in range(7):
            d = cur + timedelta(days=r)
            col.append(days.get(d, -1) if d <= end else -1)
        cols.append(col)
        cur += timedelta(days=7)
    return cols[-53:]


def car_shape(t):
    """Side-view sports car facing right, ~84 x 34, origin at rear-bottom."""
    body = t["car"]
    return f"""
<path d="M4 24 L6 15 Q8 12 14 11 L28 10 Q34 2 46 2 L56 2 Q63 2 68 9 L78 12 Q84 13 84 19 L84 24 Q84 27 81 27 L7 27 Q4 27 4 24Z" fill="{body}"/>
<path d="M32 10 Q37 4 46 4 L49 4 L49 10Z" fill="{t['glass']}"/>
<path d="M52 4 L56 4 Q61 4 65 10 L52 10Z" fill="{t['glass']}"/>
<rect x="6" y="17" width="76" height="2" fill="#FFFFFF" opacity=".25"/>
<rect x="79" y="14" width="5" height="4" rx="1.5" fill="#FFF3B0"/>
<rect x="4" y="15" width="4" height="4" rx="1.5" fill="#FF5F57"/>
<g class="wheel" style="transform-origin:20px 27px"><circle cx="20" cy="27" r="7.5" fill="#111827"/><circle cx="20" cy="27" r="3.6" fill="#9CA3AF"/>
<rect x="19.2" y="20" width="1.6" height="14" fill="#4B5563"/><rect x="13" y="26.2" width="14" height="1.6" fill="#4B5563"/></g>
<g class="wheel" style="transform-origin:66px 27px"><circle cx="66" cy="27" r="7.5" fill="#111827"/><circle cx="66" cy="27" r="3.6" fill="#9CA3AF"/>
<rect x="65.2" y="20" width="1.6" height="14" fill="#4B5563"/><rect x="59" y="26.2" width="14" height="1.6" fill="#4B5563"/></g>
<path class="beam" d="M84 15 L150 4 L150 30 Z" fill="#FFF3B0"/>
<circle class="puff p1" cx="-2" cy="23" r="3" fill="{t['muted']}"/>
<circle class="puff p2" cx="-6" cy="21" r="2.4" fill="{t['muted']}"/>
"""


def build(cols, theme, total):
    t = THEMES[theme]
    n = len(cols)
    w = PAD_X * 2 + n * STEP - GAP
    grid_bottom = PAD_Y + 7 * STEP - GAP
    road_y = grid_bottom + 18
    h = road_y + 70
    span = n * STEP
    start_x, end_x = PAD_X - 100, PAD_X + span - 20   # car's front reaches past the last column
    travel = end_x - start_x
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="A car driving past my contribution graph, recolouring it">',
        "<style>",
        f"text{{font-family:{FONT}}}",
        f".tt{{font-size:14px;font-weight:700;fill:{t['amber']}}} .sub{{font-size:12px;fill:{t['muted']}}}",
        f".car{{animation:drive {DURATION}s linear infinite}}",
        f"@keyframes drive{{0%{{transform:translateX(0)}}49.99%{{transform:translateX({travel}px)}}"
        f"50%{{transform:translateX(0)}}100%{{transform:translateX({travel}px)}}}}",
        ".bob{animation:bob .35s ease-in-out infinite}",
        "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-1px)}}",
        ".wheel{animation:spin .45s linear infinite}",
        "@keyframes spin{to{transform:rotate(360deg)}}",
        ".beam{opacity:.18;animation:beam 1.4s ease-in-out infinite}",
        "@keyframes beam{0%,100%{opacity:.12}50%{opacity:.26}}",
        ".puff{opacity:0;animation:puff .9s linear infinite}.p2{animation-delay:.45s}",
        "@keyframes puff{0%{opacity:.5;transform:translate(0,0)}100%{opacity:0;transform:translate(-14px,-6px)}}",
        f".lane{{stroke-dasharray:18 14;animation:lane .6s linear infinite}}",
        "@keyframes lane{to{stroke-dashoffset:32}}",
    ]
    car_front_offset = 84  # front bumper relative to car origin
    for c in range(n):
        col_x = PAD_X + c * STEP + CELL / 2
        frac = (col_x - start_x - car_front_offset) / travel
        frac = min(max(frac, 0.0), 1.0)
        p1 = frac * 50
        p2 = 50 + frac * 50
        out.append(
            f".c{c}{{opacity:0;animation:k{c} {DURATION}s linear infinite}}"
            f"@keyframes k{c}{{0%,{max(p1-0.3,0):.2f}%{{opacity:0}}{p1:.2f}%,{max(p2-0.3,p1):.2f}%{{opacity:1}}"
            f"{p2:.2f}%,100%{{opacity:0}}}}"
        )
    out.append("</style>")
    out.append(f'<rect width="{w}" height="{h}" rx="12" fill="{t["bg"]}"/>')
    out.append(f'<text class="tt" x="{PAD_X}" y="32">~/contributions $ <tspan fill="{t["text"]}" font-weight="400">./drive --repaint</tspan></text>')
    out.append(f'<text class="sub" x="{PAD_X}" y="52">{total} active days in the last year</text>')

    base, over = [], []
    for c, col in enumerate(cols):
        x = PAD_X + c * STEP
        for r, lv in enumerate(col):
            if lv < 0:
                continue
            y = PAD_Y + r * STEP
            base.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{t["a"][lv]}"/>')
            over.append(f'<rect class="c{c}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{t["b"][lv]}"/>')
    out += base + over

    # road
    out.append(f'<rect x="{PAD_X-10}" y="{road_y}" width="{span+20}" height="34" rx="6" fill="{t["road"]}"/>')
    out.append(f'<line class="lane" x1="{PAD_X}" y1="{road_y+17}" x2="{PAD_X+span}" y2="{road_y+17}" stroke="{t["lane"]}" stroke-width="2"/>')
    # car (clipped to the road area so it enters/leaves cleanly)
    out.append(f'<clipPath id="roadclip"><rect x="{PAD_X-10}" y="{road_y-40}" width="{span+20}" height="80"/></clipPath>')
    out.append(f'<g clip-path="url(#roadclip)"><g class="car"><g transform="translate({start_x} {road_y-12})"><g class="bob">{car_shape(t)}</g></g></g></g>')

    lx = w - PAD_X - 230
    ly = h - 20
    out.append(f'<text class="sub" x="{lx}" y="{ly+9}">before</text>')
    for i, col in enumerate(t["a"]):
        out.append(f'<rect x="{lx+50+i*14}" y="{ly}" width="10" height="10" rx="2" fill="{col}"/>')
    out.append(f'<text class="sub" x="{lx+128}" y="{ly+9}">after</text>')
    for i, col in enumerate(t["b"][1:]):
        out.append(f'<rect x="{lx+168+i*14}" y="{ly}" width="10" height="10" rx="2" fill="{col}"/>')
    out.append("</svg>")
    return "\n".join(out)


def main():
    args = sys.argv[1:]
    if args and args[0] == "--demo":
        days, out_dir = demo(), Path(args[1])
    else:
        days, out_dir = fetch(args[0]), Path(args[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    cols = to_grid(days)
    total = sum(1 for col in cols for lv in col if lv > 0)
    for theme in THEMES:
        (out_dir / f"car-{theme}.svg").write_text(build(cols, theme, total), encoding="utf-8")
    print(f"wrote car SVGs ({len(cols)} weeks, {total} active days) to {out_dir}")


if __name__ == "__main__":
    main()
