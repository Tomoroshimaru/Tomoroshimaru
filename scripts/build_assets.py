#!/usr/bin/env python3
"""Generate the SVG assets of the profile README, in light and dark variants.

Edit the content below, then run from anywhere:

    python3 scripts/build_assets.py

Brand icons come from Simple Icons (CC0) and live in scripts/icons/, next to a
few hand-drawn glyphs for tools that have no logo.
"""

import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ICONS_DIR = ROOT / "scripts" / "icons"
OUT_DIR = ROOT / "assets"

SERIF = "'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "light": {
        "page": "#FAF8F5",
        "surface": "#FFFFFF",
        "border": "#E7E2DA",
        "title": "#1C1917",
        "text": "#44403C",
        "muted": "#78716C",
        "accent": "#C93A1B",
        "is_dark": False,
        "tint": 0.10,
    },
    "dark": {
        "page": "#121110",
        "surface": "#1A1917",
        "border": "#3A3633",
        "title": "#F5F2EE",
        "text": "#D6D3D1",
        "muted": "#A8A29E",
        "accent": "#FF6B4A",
        "is_dark": True,
        "tint": 0.16,
    },
}

# ---------------------------------------------------------------- content

NAME = "Thomas Alaphilippe"
INITIALS = "TA"
ROLE_PREFIX = "Solutions Engineer at "
COMPANY = "Dust"
LOCATION = "Paris"

# Banner: an agent run, built from tools that exist in the projects below.
AGENT_PROMPT = "triage this week's escalations"
AGENT_TOOLS = ["zendesk.search_tickets", "dust.search_nodes", "notion.query_database"]
AGENT_RESULT = "4 replies drafted, 2 flagged"

PROJECTS = [
    {
        "slug": "dust-mcp",
        "title": "dust-mcp",
        "lines": [
            "MCP server that exposes the full Dust API to agents: 33 tools across agents,",
            "conversations, data sources, documents, tables and Dust apps.",
        ],
        "tags": ["Python", "FastMCP", "httpx"],
    },
    {
        "slug": "zendesk-mcp",
        "title": "zendesk-mcp",
        "lines": [
            "Gives Dust agents full access to Zendesk Support, built for an autonomous",
            "ticket-handling agent. Stateless, with OAuth handled by Dust.",
        ],
        "tags": ["Python", "FastMCP", "Docker", "OAuth"],
    },
    {
        "slug": "supplier-agents",
        "title": "Supplier certification agents",
        "lines": [
            "Four Dust agents that check supplier certificates against the official GOTS",
            "registry, enrich them from the web and report in Dust Frames. Built for LVMH.",
        ],
        "tags": ["Dust", "Selenium", "FastMCP"],
    },
    {
        "slug": "investment-agent",
        "title": "Investment agent",
        "lines": [
            "LangGraph workflow that reads a Notion fundraising database, lets a human pick",
            "the deals to enrich, searches the web and ships a PDF report to Google Drive.",
        ],
        "tags": ["LangGraph", "OpenAI", "Notion API"],
    },
    {
        "slug": "rag-app",
        "title": "Cross-lingual RAG",
        "lines": [
            "Streamlit app that answers questions over PDFs in French and English, with",
            "query rewriting, translation, FAISS search and reranking.",
        ],
        "tags": ["Streamlit", "FAISS", "GPT-4o-mini"],
    },
    {
        "slug": "dust-usage-cron",
        "title": "dust-usage-cron",
        "lines": [
            "Weekly job that pulls Dust usage analytics and pushes them back into a Dust",
            "folder, running serverless on Azure Container Apps Jobs.",
        ],
        "tags": ["Deno", "TypeScript", "Azure"],
    },
]

# (heading, caption lines, tools). A tool is (icon file, label, brand colour).
# Hand-drawn glyphs have no brand colour and use the accent instead.
TOOLBOX = [
    ("Agents & LLMs", ["what the agents", "run on"], [
        ("sparkle", "Dust", None),
        ("langgraph", "LangGraph", "7FC8FF"),
        ("langchain", "LangChain", "7FC8FF"),
        ("chat", "OpenAI API", None),
        ("file-search", "RAG", None),
        ("scatter", "FAISS", None),
        ("vectors", "Embeddings", None),
    ]),
    ("Integrations", ["where the agents", "take action"], [
        ("modelcontextprotocol", "MCP", "000000"),
        ("braces", "Dust API", None),
        ("zendesk", "Zendesk", "03363D"),
        ("notion", "Notion", "000000"),
        ("googledrive", "Drive", "4285F4"),
        ("googlesheets", "Sheets", "34A853"),
        ("search", "Serper", None),
        ("selenium", "Selenium", "43B02A"),
    ]),
    ("Build & ship", ["how it gets", "to production"], [
        ("python", "Python", "3776AB"),
        ("typescript", "TypeScript", "3178C6"),
        ("deno", "Deno", "000000"),
        ("pydantic", "Pydantic", "E92063"),
        ("duckdb", "DuckDB", "FFF000"),
        ("streamlit", "Streamlit", "FF4B4B"),
        ("docker", "Docker", "2496ED"),
        ("cloud", "Azure", None),
    ]),
]

# ---------------------------------------------------------------- helpers


def style_block(extra=""):
    return (
        "<style>"
        f".serif {{ font-family: {SERIF}; }}"
        f".sans {{ font-family: {SANS}; }}"
        f".mono {{ font-family: {MONO}; }}"
        f"{extra}"
        "</style>"
    )


def svg(width, height, title, body):
    label = escape(title, {'"': "&quot;"})
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{label}">\n'
        f"<title>{escape(title)}</title>\n{body}\n</svg>\n"
    )


def pill_width(label, char_width=7.2, padding=24):
    # Monospace glyphs are ~0.6em wide, so the width is predictable.
    return round(len(label) * char_width + padding)


def icon(name, x, y, size, color):
    source = (ICONS_DIR / f"{name}.svg").read_text()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", source, re.S).group(1)
    inner = re.sub(r"<title>.*?</title>", "", inner)
    return (
        f'<g transform="translate({x:g} {y:g}) scale({size / 24:g})" '
        f'fill="{color}" color="{color}">{inner}</g>'
    )


def luminance(hex_color):
    def channel(c):
        c = int(c, 16) / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(hex_color[i:i + 2]) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def brand_color(hex_color, t):
    # Keep brand colours, but rescue the ones that vanish on the page
    # background: yellows on light, near-blacks on dark.
    if hex_color is None:
        return t["accent"]
    if not t["is_dark"] and luminance(hex_color) > 0.45:
        r, g, b = (round(int(hex_color[i:i + 2], 16) * 0.55) for i in (0, 2, 4))
        return f"#{r:02X}{g:02X}{b:02X}"
    if t["is_dark"] and luminance(hex_color) < 0.06:
        return t["title"]
    return f"#{hex_color}"


def pill(x, y, label, t):
    width = pill_width(label)
    return width, (
        f'<rect x="{x:g}" y="{y}" width="{width}" height="28" rx="14" fill="none" stroke="{t["border"]}"/>'
        f'<text x="{x + width / 2:g}" y="{y + 18.5:g}" class="mono" font-size="12" text-anchor="middle" '
        f'fill="{t["text"]}">{escape(label)}</text>'
    )


# ---------------------------------------------------------------- banner


def banner(t):
    w, h = 1200, 320
    panel_x, panel_y, panel_w, panel_h = 640, 44, 500, 232
    inner_x, right_x = panel_x + 24, panel_x + panel_w - 24

    # Each trace line fades in one after the other, then the run starts over.
    animation = (
        ".step { animation: reveal 9s ease-out infinite both; }"
        "@keyframes reveal { 0% { opacity: 0; transform: translateY(4px); }"
        " 5% { opacity: 1; transform: none; } 85% { opacity: 1; } 95%, 100% { opacity: 0; } }"
        ".live { animation: blink 1.6s ease-in-out infinite; }"
        "@keyframes blink { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }"
        "@media (prefers-reduced-motion: reduce) { .step, .live { animation: none; } }"
    )

    body = [
        style_block(animation),
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="15.5" fill="{t["page"]}" stroke="{t["border"]}"/>',
        # Seal with initials
        '<g transform="rotate(-6 100 104)">',
        f'<rect x="72" y="76" width="56" height="56" rx="10" fill="{t["accent"]}"/>',
        f'<rect x="77" y="81" width="46" height="46" rx="7" fill="none" stroke="{t["page"]}" stroke-opacity="0.55"/>',
        f'<text x="100" y="113" class="serif" font-size="23" font-weight="700" text-anchor="middle" '
        f'fill="{t["page"]}">{escape(INITIALS)}</text>',
        "</g>",
        # Identity
        f'<text x="70" y="198" class="serif" font-size="54" fill="{t["title"]}">{escape(NAME)}</text>',
        f'<text x="72" y="238" class="sans" font-size="21" fill="{t["text"]}">{escape(ROLE_PREFIX)}'
        f'<tspan fill="{t["accent"]}">{escape(COMPANY)}</tspan>'
        f'<tspan fill="{t["muted"]}">  ·  {escape(LOCATION)}</tspan></text>',
        # Agent run panel
        f'<rect x="{panel_x}" y="{panel_y}" width="{panel_w}" height="{panel_h}" rx="12" '
        f'fill="{t["surface"]}" stroke="{t["border"]}"/>',
        f'<text x="{inner_x}" y="{panel_y + 28}" class="mono" font-size="13" letter-spacing="1" '
        f'fill="{t["muted"]}">agent run</text>',
        f'<circle cx="{right_x - 44}" cy="{panel_y + 24}" r="3.5" fill="{t["accent"]}" class="live"/>',
        f'<text x="{right_x}" y="{panel_y + 28}" class="mono" font-size="13" text-anchor="end" '
        f'fill="{t["muted"]}">live</text>',
        f'<path d="M{panel_x} {panel_y + 44} H{panel_x + panel_w}" stroke="{t["border"]}"/>',
        '<g class="mono" font-size="16">',
    ]

    steps = [
        f'<tspan fill="{t["accent"]}">›</tspan> <tspan fill="{t["title"]}">{escape(AGENT_PROMPT)}</tspan>'
    ]
    steps += [f'<tspan fill="{t["muted"]}">  ↳ {escape(tool)}</tspan>' for tool in AGENT_TOOLS]
    steps.append(f'<tspan fill="{t["accent"]}">●</tspan> <tspan fill="{t["text"]}">{escape(AGENT_RESULT)}</tspan>')

    for i, step in enumerate(steps):
        y = panel_y + 80 + i * 32
        line = f'<text x="{inner_x}" y="{y}">{step}</text>'
        if 0 < i <= len(AGENT_TOOLS):
            line += f'<text x="{right_x}" y="{y}" text-anchor="end" fill="{t["accent"]}">✓</text>'
        body.append(f'<g class="step" style="animation-delay: {i * 0.9:g}s">{line}</g>')
    body.append("</g>")

    return svg(w, h, f"{NAME}, {ROLE_PREFIX}{COMPANY}", "\n".join(body))


# ---------------------------------------------------------------- project rows


def project_row(project, index, t, last):
    w, h = 860, 116
    body = [
        style_block(),
        f'<text x="4" y="48" class="serif" font-size="28" fill="{t["accent"]}">{index:02d}</text>',
        f'<text x="64" y="46" class="serif" font-size="22" fill="{t["title"]}">{escape(project["title"])}</text>',
        # "Open" arrow on the right
        f'<path d="M{w - 16} 40 L{w - 6} 30 M{w - 13} 30 H{w - 6} V37" fill="none" stroke="{t["muted"]}" '
        f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>',
    ]
    # The section heading already draws a rule above the first row.
    if index > 1:
        body.append(f'<path d="M0 0.5 H{w}" stroke="{t["border"]}"/>')
    if last:
        body.append(f'<path d="M0 {h - 0.5} H{w}" stroke="{t["border"]}"/>')
    for i, line in enumerate(project["lines"]):
        body.append(
            f'<text x="64" y="{76 + i * 21}" class="sans" font-size="14" fill="{t["text"]}">{escape(line)}</text>'
        )
    # Tags are right-aligned on the title line, left of the arrow.
    x = w - 32
    for tag in reversed(project["tags"]):
        x -= pill_width(tag)
        _, element = pill(x, 22, tag, t)
        body.append(element)
        x -= 8

    summary = f'{project["title"]}: {" ".join(project["lines"])}'
    return svg(w, h, summary, "\n".join(body))


# ---------------------------------------------------------------- toolbox


def toolbox(t):
    w, label_w, row_h, box = 860, 200, 128, 52
    slot_w = (w - label_w) / max(len(tools) for _, _, tools in TOOLBOX)
    body = [style_block()]
    for row, (heading, caption, tools) in enumerate(TOOLBOX):
        top = row * row_h
        if row:  # the section heading already draws a rule above the first row
            body.append(f'<path d="M0 {top + 0.5} H{w}" stroke="{t["border"]}"/>')
        body.append(
            f'<text x="4" y="{top + 50}" class="serif" font-size="21" font-style="italic" '
            f'fill="{t["title"]}">{escape(heading)}</text>'
        )
        for i, line in enumerate(caption):
            body.append(
                f'<text x="4" y="{top + 74 + i * 18}" class="sans" font-size="13" '
                f'fill="{t["muted"]}">{escape(line)}</text>'
            )
        for i, (icon_name, label, hex_color) in enumerate(tools):
            color = brand_color(hex_color, t)
            cx = label_w + slot_w * (i + 0.5)
            box_y = top + 24
            body.append(
                f'<rect x="{cx - box / 2:g}" y="{box_y}" width="{box}" height="{box}" rx="14" '
                f'fill="{color}" fill-opacity="{t["tint"]}"/>'
            )
            body.append(icon(icon_name, cx - 13, box_y + 13, 26, color))
            body.append(
                f'<text x="{cx:g}" y="{box_y + box + 22}" class="mono" font-size="11.5" '
                f'text-anchor="middle" fill="{t["text"]}">{escape(label)}</text>'
            )
    h = len(TOOLBOX) * row_h
    body.append(f'<path d="M0 {h - 0.5} H{w}" stroke="{t["border"]}"/>')

    summary = "Toolbox. " + "; ".join(
        f"{heading}: {', '.join(label for _, label, _ in tools)}" for heading, _, tools in TOOLBOX
    )
    return svg(w, h, summary, "\n".join(body))


# ---------------------------------------------------------------- build


def main():
    OUT_DIR.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        (OUT_DIR / f"banner-{name}.svg").write_text(banner(t))
        (OUT_DIR / f"toolbox-{name}.svg").write_text(toolbox(t))
        for i, project in enumerate(PROJECTS, start=1):
            row = project_row(project, i, t, last=i == len(PROJECTS))
            (OUT_DIR / f"project-{project['slug']}-{name}.svg").write_text(row)
    print(f"Wrote {len(list(OUT_DIR.glob('*.svg')))} files to {OUT_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
