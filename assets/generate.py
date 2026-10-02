"""Generates the custom SVG assets for the zaosdev profile README (Tokyo Night palette).

Run from anywhere: `python assets/generate.py`. Edit the card() calls at the bottom to change project cards."""
import os
from html import escape

OUT = os.path.dirname(os.path.abspath(__file__))

BG, BAR, BORDER = "#1a1b27", "#16161e", "#292e42"
FG, FG2, COMMENT, MUTED = "#c0caf5", "#a9b1d6", "#565f89", "#737aa2"
BLUE, CYAN, PURPLE, GREEN = "#7aa2f7", "#7dcfff", "#bb9af7", "#9ece6a"
ORANGE, RED, YELLOW, DEEP = "#ff9e64", "#f7768e", "#e0af68", "#3d59a1"
SANS = "'Segoe UI', Inter, -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'JetBrains Mono', 'Cascadia Code', Menlo, Consolas, monospace"

BASE_CSS = f"""
    .sans {{ font-family: {SANS}; }}
    .mono {{ font-family: {MONO}; }}
    @keyframes blink {{ 0%, 49% {{ opacity: 1; }} 50%, 100% {{ opacity: 0; }} }}
    @keyframes pulse {{ 0%, 100% {{ opacity: .35; }} 50% {{ opacity: 1; }} }}
    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    .pulse {{ animation: pulse 2.4s ease-in-out infinite; }}
"""
BREAKPOINT = 640  # rendered width (px) below which the SVGs switch to their phone layout
REDUCED = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"


def floor(vpx, hz, bottom, width, cls, speed=1.8, lines=14, spacing=150):
    """Synthwave-style perspective floor scrolling towards the viewer."""
    depth = bottom - hz
    k = depth * 1.2  # y = hz + k / z  ->  z = 1.2 sits on the bottom edge
    css, out = [], []
    for i in range(-18, 19):
        x0 = vpx + i * spacing * (3 / depth)
        out.append(f'<line x1="{x0:.1f}" y1="{hz + 3}" x2="{vpx + i * spacing:.1f}" y2="{bottom}"/>')
    steps = 8
    for n in range(lines):
        z = 1.2 + n
        y0 = hz + k / z
        frames = []
        for s in range(steps + 1):
            zz = z - s / steps
            dy = (hz + k / zz) - y0
            frames.append(f"{100 * s / steps:.1f}% {{ transform: translateY({dy:.2f}px); }}")
        css.append(f"@keyframes {cls}{n} {{ {' '.join(frames)} }} .{cls}{n} {{ animation: {cls}{n} {speed}s linear infinite; }}")
        out.append(f'<line class="{cls}{n}" x1="0" y1="{y0:.2f}" x2="{width}" y2="{y0:.2f}"/>')
    return "\n".join(css), "\n      ".join(out)


# ─────────────────────────────── HEADER ───────────────────────────────
def header():
    W, H, HZ = 1200, 440, 376
    floor_css, floor_lines = floor(990, HZ, H, W, "fl")

    # neural network
    layers = [(870, [128, 188, 248, 308], CYAN), (990, [104, 160, 216, 272, 328], BLUE), (1110, [156, 216, 276], PURPLE)]
    edges, pulses, nodes = [], [], []
    pulse_pairs = {(0, 0, 1), (0, 1, 3), (0, 2, 0), (0, 3, 4), (0, 1, 2), (1, 0, 0), (1, 1, 1), (1, 3, 2), (1, 4, 1), (1, 2, 0)}
    for li in range(2):
        (x1, ys1, _), (x2, ys2, _) = layers[li], layers[li + 1]
        for a, y1 in enumerate(ys1):
            for b, y2 in enumerate(ys2):
                edges.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
                if (li, a, b) in pulse_pairs:
                    delay = (a * 0.37 + b * 0.21) % 1.3 + li * 1.3
                    pulses.append(f'<line class="sig" style="animation-delay:{delay:.2f}s" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    for li, (x, ys, col) in enumerate(layers):
        for j, y in enumerate(ys):
            nodes.append(
                f'<circle cx="{x}" cy="{y}" r="10" fill="{BG}" stroke="{col}" stroke-width="2.2"/>'
                f'<circle class="pulse" style="animation-delay:{(li * 0.6 + j * 0.45) % 2.4:.2f}s" cx="{x}" cy="{y}" r="4" fill="{col}"/>'
            )

    chips, x = [], 64
    for label, col in [("WEB & MOBILE", CYAN), ("3D / VR", PURPLE), ("DEEP LEARNING", ORANGE), ("SELF-HOSTED INFRA", GREEN)]:
        w = len(label) * 10 + 32
        chips.append(
            f'<rect x="{x}" y="316" width="{w:.0f}" height="34" rx="17" fill="{col}" fill-opacity=".08" stroke="{col}" stroke-opacity=".45"/>'
            f'<text x="{x + w / 2:.1f}" y="338.5" text-anchor="middle" class="mono" font-size="15" letter-spacing="1" fill="{col}">{escape(label)}</text>'
        )
        x += w + 10

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
  <title id="title">Juan Manuel González Santos</title>
  <desc id="desc">Full-Stack Software Engineer and Multimedia Engineer with an MSc in AI, based in Alicante, Spain. Web and mobile, 3D/VR, deep learning and self-hosted infrastructure.</desc>
  <defs>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="20"/></clipPath>
    <radialGradient id="glowR" cx="0.83" cy="0.48" r="0.42"><stop offset="0" stop-color="{BLUE}" stop-opacity=".20"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
    <radialGradient id="glowL" cx="0.05" cy="0.1" r="0.55"><stop offset="0" stop-color="{PURPLE}" stop-opacity=".10"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>
    <linearGradient id="fade" gradientUnits="userSpaceOnUse" x1="0" y1="{HZ}" x2="0" y2="{H}"><stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient>
    <mask id="floorMask"><rect x="0" y="{HZ}" width="{W}" height="{H - HZ}" fill="url(#fade)"/></mask>
    <linearGradient id="horizon" x1="0" x2="1"><stop offset="0" stop-color="{PURPLE}" stop-opacity="0"/><stop offset=".55" stop-color="{PURPLE}" stop-opacity=".7"/><stop offset=".82" stop-color="{BLUE}"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient>
    <linearGradient id="nameGrad" x1="0" x2="1"><stop offset="0" stop-color="{BLUE}"/><stop offset="1" stop-color="{PURPLE}"/></linearGradient>
  </defs>
  <style>{BASE_CSS}
    .grid line {{ stroke: {BLUE}; stroke-opacity: .55; stroke-width: 1; }}
    .edges line {{ stroke: {DEEP}; stroke-opacity: .55; stroke-width: 1.2; }}
    .sig {{ stroke: {CYAN}; stroke-width: 2.6; stroke-linecap: round; stroke-dasharray: 14 1000; stroke-dashoffset: 14; animation: sig 2.6s linear infinite; }}
    @keyframes sig {{ from {{ stroke-dashoffset: 14; }} to {{ stroke-dashoffset: -260; }} }}
    {floor_css}
    /* phone layout: the query sees the image's rendered width, not the page's */
    .m {{ display: none; }}
    @media (max-width: {BREAKPOINT}px) {{ .d {{ display: none; }} .m {{ display: inline; }} }}
    {REDUCED}
  </style>
  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{H}" fill="url(#glowL)"/>
    <rect width="{W}" height="{H}" fill="url(#glowR)"/>

    <!-- perspective floor -->
    <g class="grid" mask="url(#floorMask)">
      {floor_lines}
    </g>
    <rect x="0" y="{HZ - 1}" width="{W}" height="1.5" fill="url(#horizon)"/>

    <!-- terminal title bar -->
    <rect width="{W}" height="52" fill="{BAR}"/>
    <rect y="52" width="{W}" height="1" fill="{BORDER}"/>

    <g class="d">
      <circle cx="30" cy="26" r="6.5" fill="{RED}" fill-opacity=".85"/>
      <circle cx="52" cy="26" r="6.5" fill="{YELLOW}" fill-opacity=".85"/>
      <circle cx="74" cy="26" r="6.5" fill="{GREEN}" fill-opacity=".85"/>
      <text x="{W / 2}" y="31" text-anchor="middle" class="mono" font-size="13" fill="{MUTED}">~/zaosdev</text>
      <text x="{W - 28}" y="31" text-anchor="end" class="mono" font-size="13" fill="{MUTED}">alicante, es · utc+1</text>

      <text x="64" y="112" class="mono" font-size="18" fill="{FG2}"><tspan fill="{GREEN}">$</tspan> whoami <tspan class="cursor" fill="{BLUE}">▌</tspan></text>
      <text x="62" y="186" class="sans" font-size="62" font-weight="700" fill="{FG}" letter-spacing="-1">Juan Manuel</text>
      <text x="62" y="254" class="sans" font-size="62" font-weight="700" fill="url(#nameGrad)" letter-spacing="-1">González Santos</text>
      <text x="64" y="294" class="sans" font-size="22" fill="{FG2}">Full-Stack Software Engineer <tspan fill="{COMMENT}">·</tspan> Multimedia Engineer <tspan fill="{COMMENT}">·</tspan> MSc in AI</text>
      {''.join(chips)}

      <g class="edges">{''.join(edges)}</g>
      <g>{''.join(pulses)}</g>
      {''.join(nodes)}
    </g>

    <g class="m">
      <circle cx="36" cy="26" r="11" fill="{RED}" fill-opacity=".85"/>
      <circle cx="70" cy="26" r="11" fill="{YELLOW}" fill-opacity=".85"/>
      <circle cx="104" cy="26" r="11" fill="{GREEN}" fill-opacity=".85"/>
      <text x="{W - 40}" y="38" text-anchor="end" class="mono" font-size="34" fill="{MUTED}">alicante, es</text>

      <text x="64" y="112" class="mono" font-size="44" fill="{FG2}"><tspan fill="{GREEN}">$</tspan> whoami <tspan class="cursor" fill="{BLUE}">▌</tspan></text>
      <text x="58" y="206" class="sans" font-size="104" font-weight="700" fill="{FG}" letter-spacing="-2">Juan Manuel</text>
      <text x="58" y="304" class="sans" font-size="104" font-weight="700" fill="url(#nameGrad)" letter-spacing="-2">González Santos</text>
      <text x="64" y="354" class="sans" font-size="46" fill="{FG2}">Full-Stack Engineer <tspan fill="{COMMENT}">·</tspan> MSc in AI</text>
    </g>
  </g>
  <rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="19.5" fill="none" stroke="{BORDER}" stroke-width="1.5"/>
</svg>
"""
    open(f"{OUT}/header.svg", "w", encoding="utf-8", newline="\n").write(svg)


# ─────────────────────────────── FOOTER ───────────────────────────────
def footer():
    W, H, HZ = 1200, 130, 78
    floor_css, floor_lines = floor(600, HZ, H, W, "ff", lines=10, spacing=120)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title">
  <title id="title">Thanks for stopping by!</title>
  <defs>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
    <linearGradient id="fade" gradientUnits="userSpaceOnUse" x1="0" y1="{HZ}" x2="0" y2="{H}"><stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient>
    <mask id="floorMask"><rect x="0" y="{HZ}" width="{W}" height="{H - HZ}" fill="url(#fade)"/></mask>
    <linearGradient id="horizon" x1="0" x2="1"><stop offset="0" stop-color="{PURPLE}" stop-opacity="0"/><stop offset=".5" stop-color="{BLUE}"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></linearGradient>
    <radialGradient id="glow" cx=".5" cy=".6" r=".5"><stop offset="0" stop-color="{BLUE}" stop-opacity=".16"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
  </defs>
  <style>{BASE_CSS}
    .grid line {{ stroke: {BLUE}; stroke-opacity: .5; stroke-width: 1; }}
    {floor_css}
    .m {{ display: none; }}
    @media (max-width: {BREAKPOINT}px) {{ .d {{ display: none; }} .m {{ display: inline; }} }}
    {REDUCED}
  </style>
  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{H}" fill="url(#glow)"/>
    <g class="grid" mask="url(#floorMask)">
      {floor_lines}
    </g>
    <rect x="0" y="{HZ - 1}" width="{W}" height="1.5" fill="url(#horizon)"/>
    <text class="d mono" x="{W / 2}" y="50" text-anchor="middle" font-size="17" fill="{FG2}"><tspan fill="{GREEN}">$</tspan> echo <tspan fill="{GREEN}">"Thanks for stopping by!"</tspan> <tspan class="cursor" fill="{BLUE}">▌</tspan></text>
    <text class="m mono" x="{W / 2}" y="58" text-anchor="middle" font-size="44" fill="{FG2}"><tspan fill="{GREEN}">$</tspan> echo <tspan fill="{GREEN}">"Thanks for stopping by!"</tspan></text>
  </g>
  <rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="17.5" fill="none" stroke="{BORDER}" stroke-width="1.5"/>
</svg>
"""
    open(f"{OUT}/footer.svg", "w", encoding="utf-8", newline="\n").write(svg)


# ─────────────────────────────── PROJECT CARDS ───────────────────────────────
ICONS = {
    "vr": f"""<path d="M9 13h22a5 5 0 0 1 5 5v5a5 5 0 0 1-5 5h-6l-3-4h-4l-3 4H9a5 5 0 0 1-5-5v-5a5 5 0 0 1 5-5Z" fill="none" stroke="{CYAN}" stroke-width="2.2" stroke-linejoin="round"/>
      <circle class="pulse" cx="13.5" cy="20.5" r="3" fill="{CYAN}"/><circle class="pulse" style="animation-delay:.3s" cx="26.5" cy="20.5" r="3" fill="{CYAN}"/>""",
    "candles": f"""<g stroke-width="1.6"><line x1="10" y1="11" x2="10" y2="31" stroke="{GREEN}"/><line x1="17" y1="8" x2="17" y2="25" stroke="{RED}"/><line x1="24" y1="14" x2="24" y2="32" stroke="{GREEN}"/><line x1="31" y1="6" x2="31" y2="22" stroke="{GREEN}"/></g>
      <rect x="8" y="16" width="4" height="10" rx="1" fill="{GREEN}"/><rect x="15" y="12" width="4" height="8" rx="1" fill="{RED}"/><rect x="22" y="18" width="4" height="10" rx="1" fill="{GREEN}"/><rect x="29" y="9" width="4" height="8" rx="1" fill="{GREEN}"/>
      <polyline points="6,30 13,24 20,26 27,17 35,9" fill="none" stroke="{PURPLE}" stroke-width="1.6" stroke-dasharray="2 2.5"/>""",
    "terminal": f"""<path d="M10 14l7 6-7 6" fill="none" stroke="{BLUE}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
      <rect class="cursor" x="20" y="25" width="11" height="2.8" rx="1.2" fill="{BLUE}"/>""",
    "escape": f"""<rect x="31" y="7" width="5" height="26" rx="1" fill="{GREEN}" fill-opacity=".55"/>
      <rect x="5" y="23" width="8" height="8" rx="1" fill="{YELLOW}"/>
      <rect class="bounce" x="15" y="8" width="6" height="6" rx="1" fill="{RED}"/>
      <rect class="bounce" style="animation-delay:-.6s" x="23" y="8" width="6" height="6" rx="1" fill="{CYAN}"/>""",
    "flame": f"""<path class="flicker" d="M20 6c1.5 5 9 8.5 9 17a9 9 0 0 1-18 0c0-4.5 2.5-7 4-9 .6 3 2 4.5 4 5-1.2-4.6-.6-9.2 1-13Z" fill="url(#flame)"/>
      <path class="flicker" style="animation-delay:-.4s" d="M20 19c1 2.6 4 4 4 7.5a4 4 0 0 1-8 0c0-2 1-3.2 2-4.2.4 1.2 1 1.8 2 2-.5-1.8-.4-3.6 0-5.3Z" fill="{YELLOW}"/>""",
    "eq": "".join(
        f'<rect class="eq" style="animation-delay:{d}s" x="{x}" y="9" width="4" height="22" rx="2" fill="{c}"/>'
        for x, d, c in [(8, 0, ORANGE), (14, .25, RED), (20, .5, ORANGE), (26, .15, RED), (32, .4, ORANGE)]
    ),
}


def card(fname, icon, accent, pill, title, subtitle, lines, chips=None, link=None):
    # Sized to stay legible both two-up on desktop (~400px each) and full width on phones (~330px).
    # M is a transparent margin that doubles as the gutter between cards in the README.
    W, H, M, P = 440, 280, 6, 24
    pill_text, pill_color, pill_kind = pill
    pw = len(pill_text) * 8.1 + 40
    px = W - 22 - pw
    if pill_kind == "star":
        mark = f'<path transform="translate({px + 16:.1f},42) scale(.7) translate(-8,-8.4)" d="M8 0l2.4 5 5.6.8-4 3.9 1 5.5L8 12.6 3 15.2l1-5.5-4-3.9L5.6 5Z" fill="{pill_color}"/>'
    elif pill_kind == "play":
        mark = f'<path d="M{px + 12:.1f} 37l9 5-9 5Z" fill="{pill_color}"/>'
    else:
        mark = f'<circle class="pulse" cx="{px + 16:.1f}" cy="42" r="4.5" fill="{pill_color}"/>'

    body = "".join(
        f'<text x="{P}" y="{172 + i * 25}" class="sans" font-size="16.5" fill="{FG2}">{escape(t)}</text>' for i, t in enumerate(lines)
    )

    bottom = ""
    if chips:
        x = P
        for label, col in chips:
            w = len(label) * 7.8 + 32
            bottom += (
                f'<rect x="{x:.1f}" y="238" width="{w:.1f}" height="28" rx="14" fill="{FG}" fill-opacity=".04" stroke="{BORDER}"/>'
                f'<circle cx="{x + 14:.1f}" cy="252" r="4.5" fill="{col}"/>'
                f'<text x="{x + 24:.1f}" y="256.5" class="mono" font-size="13" fill="{FG2}">{escape(label)}</text>'
            )
            x += w + 8
        assert x - 8 <= W - P, f"chips overflow in {fname}: {x - 8:.0f} > {W - P}"
    if link:
        bottom += f'<text x="{P}" y="258" class="mono" font-size="15" fill="{BLUE}">→ {escape(link)}</text>'

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W + 2 * M}" height="{H + 2 * M}" viewBox="{-M} {-M} {W + 2 * M} {H + 2 * M}" role="img" aria-labelledby="title desc">
  <title id="title">{escape(title)}</title>
  <desc id="desc">{escape(subtitle)}. {escape(' '.join(lines))}</desc>
  <defs>
    <clipPath id="frame"><rect width="{W}" height="{H}" rx="14"/></clipPath>
    <radialGradient id="glow" cx="0" cy="0" r=".9"><stop offset="0" stop-color="{accent}" stop-opacity=".16"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
    <linearGradient id="flame" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{RED}"/><stop offset="1" stop-color="{ORANGE}"/></linearGradient>
  </defs>
  <style>{BASE_CSS}
    .eq {{ transform-box: fill-box; transform-origin: bottom; animation: eq 1.1s ease-in-out infinite alternate; }}
    @keyframes eq {{ 0% {{ transform: scaleY(.25); }} 100% {{ transform: scaleY(1); }} }}
    .bounce {{ animation: bounce 1.2s ease-in-out infinite alternate; }}
    @keyframes bounce {{ to {{ transform: translateY(18px); }} }}
    .flicker {{ transform-box: fill-box; transform-origin: bottom; animation: flicker .9s ease-in-out infinite alternate; }}
    @keyframes flicker {{ 0% {{ transform: scale(1, 1); }} 100% {{ transform: scale(.94, 1.08); }} }}
    {REDUCED}
  </style>
  <g clip-path="url(#frame)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{H}" fill="url(#glow)"/>
    <g transform="translate(22,20) scale(1.1)">
      <rect width="40" height="40" rx="10" fill="{accent}" fill-opacity=".10" stroke="{accent}" stroke-opacity=".35"/>
      {icon}
    </g>
    <rect x="{px:.1f}" y="28" width="{pw:.1f}" height="28" rx="14" fill="{pill_color}" fill-opacity=".10" stroke="{pill_color}" stroke-opacity=".45"/>
    {mark}
    <text x="{px + 29:.1f}" y="46.5" class="mono" font-size="12.5" letter-spacing=".6" fill="{pill_color}">{escape(pill_text)}</text>
    <text x="{P}" y="110" class="sans" font-size="27" font-weight="700" fill="{FG}">{escape(title)}</text>
    <text x="{P}" y="136" class="mono" font-size="14" fill="{MUTED}">{escape(subtitle)}</text>
    {body}
    {bottom}
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="13.5" fill="none" stroke="{BORDER}"/>
</svg>
"""
    open(f"{OUT}/{fname}.svg", "w", encoding="utf-8", newline="\n").write(svg)


header()
footer()
card(
    "project-vidareal", ICONS["vr"], CYAN, ("IN PRODUCTION", GREEN, "dot"),
    "Vidareal", "vidareal.es · VR for elderly care",
    ["VR cognitive stimulation for elderly care,",
     "on Meta Quest & Pico. Staff drive several",
     "headsets live from a phone; video via Mux."],
    chips=[("A-Frame", "#EF2D5E"), ("WebSockets", CYAN), ("Mux", "#FA50B5"), ("Bun + Hono", ORANGE)],
)
card(
    "project-tfm", ICONS["candles"], PURPLE, ("GRADE 10/10", YELLOW, "star"),
    "Deep Learning for Markets", "MSc thesis · University of Alicante",
    ["Neural network architectures for stock",
     "price prediction, trained on large-scale",
     "historical time series and benchmarked."],
    chips=[("Python", "#4B8BBE"), ("PyTorch", "#EE4C2C"), ("pandas", "#FFCA00"), ("Time series", PURPLE)],
)
card(
    "project-zaosdev", ICONS["terminal"], BLUE, ("IN DEVELOPMENT", BLUE, "dot"),
    "zaos.dev", "Portfolio & project hub",
    ["My portfolio and the home for everything",
     "I build, from VR experiences to AI models.",
     "Under construction. Shipping soon."],
    link="zaos.dev",
)
card(
    "project-geometry-escape", ICONS["escape"], GREEN, ("CPCRETRODEV 2022", GREEN, "play"),
    "Geometry Escape", "Amstrad CPC · gameplay & graphics",
    ["Arcade escape game for the 1984 Amstrad CPC,",
     "written in Z80 assembly for a 4 MHz CPU",
     "and 64 KB of RAM. Runs on real hardware."],
    chips=[("Z80 assembly", YELLOW), ("CPCtelera", CYAN), ("Pixel art", RED)],
)
card(
    "project-hellgeon", ICONS["flame"], RED, ("YEAR-LONG PROJECT", ORANGE, "play"),
    "Hellgeon", "Team of 5 · built before AI assistants",
    ["Low-poly 3D bullet hell built from scratch",
     "in a year on our own ECS engine in C++",
     "and OpenGL, plus gameplay, models and audio."],
    chips=[("C++", "#f34b7d"), ("OpenGL", "#5586A4"), ("Blender", "#F5792A"), ("Win + Linux", FG)],
)
card(
    "project-boxbeats", ICONS["eq"], ORANGE, ("GRADE 9/10", YELLOW, "star"),
    "Box Beats", "BSc thesis · VR rhythm game",
    ["Beat Saber-inspired VR rhythm game: punch",
     "blocks to the beat, with punching bag and",
     "speed ball modes and a global leaderboard."],
    chips=[("Unreal Engine 5", FG), ("VR", PURPLE), ("REST API", CYAN)],
)
print("done:", sorted(os.listdir(OUT)))
