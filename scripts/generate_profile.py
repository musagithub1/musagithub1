#!/usr/bin/env python3
"""Generate Mussa Khan's light and dark animated GitHub profile SVGs."""

from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AVATAR = ROOT / "assets" / "avatar.png"
DEFAULT_PROFILE = ROOT / "profile.json"

CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 670
ASCII_COLUMNS = 86
ASCII_LINE_HEIGHT = 8.65


THEMES = {
    "dark": {
        "bg_top": "#050816",
        "bg_bottom": "#0B1224",
        "titlebar": "#0D1526",
        "panel": "#08111F",
        "primary": "#22D3EE",
        "primary_soft": "#67E8F9",
        "secondary": "#8B5CF6",
        "accent": "#34D399",
        "text": "#E6F1FF",
        "muted": "#64748B",
        "branch": "#334155",
        "grid": "#1E293B",
        "shadow": "#020617",
        "red": "#F87171",
        "amber": "#FBBF24",
    },
    "light": {
        "bg_top": "#F8FCFF",
        "bg_bottom": "#EAF4FA",
        "titlebar": "#E7F1F7",
        "panel": "#FFFFFF",
        "primary": "#007C91",
        "primary_soft": "#0891B2",
        "secondary": "#6D28D9",
        "accent": "#047857",
        "text": "#172033",
        "muted": "#64748B",
        "branch": "#94A3B8",
        "grid": "#CBD5E1",
        "shadow": "#94A3B8",
        "red": "#DC2626",
        "amber": "#D97706",
    },
}


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def make_ascii_portrait(path: Path, columns: int = ASCII_COLUMNS) -> list[str]:
    """Convert the avatar into terminal-friendly ASCII with a transparent-looking background."""
    with Image.open(path) as source:
        source = ImageOps.exif_transpose(source).convert("RGB")
        rows = max(1, round((source.height / source.width) * columns * 0.58))
        gray = ImageOps.grayscale(source)
        gray = ImageOps.autocontrast(gray, cutoff=1)
        gray = ImageEnhance.Contrast(gray).enhance(1.18)
        gray = gray.resize((columns, rows), Image.Resampling.LANCZOS)

    palette = " .,:;irsXA253hMHGS#9B&@"
    lines: list[str] = []
    for y in range(gray.height):
        characters: list[str] = []
        for x in range(gray.width):
            value = gray.getpixel((x, y))
            if value <= 9:
                characters.append(" ")
                continue
            normalized = (value - 9) / 246
            index = min(len(palette) - 1, round(normalized * (len(palette) - 1)))
            characters.append(palette[index])
        lines.append("".join(characters).rstrip())
    return lines


def profile_lines(profile: dict) -> list[tuple[str, str, str]]:
    identity = profile["identity"]
    focus = profile["specialization"]
    tools = profile["toolchain"]
    builds = profile["build_log"]
    connect = profile["connect"]

    return [
        ("prompt", "mussa@ai-lab:~$", "./profile --live"),
        ("section", "IDENTITY", ""),
        ("row", "name", identity["name"]),
        ("row", "role", identity["role"]),
        ("row", "base", identity["base"]),
        ("row", "education", identity["education"]),
        ("row", "current", identity["current"]),
        ("section", "SPECIALIZATION", ""),
        ("row", "agentic_ai", focus["agentic_ai"]),
        ("row", "vision", focus["vision"]),
        ("row", "automation", focus["automation"]),
        ("row", "local_ai", focus["local_ai"]),
        ("section", "TOOLCHAIN", ""),
        ("row", "languages", tools["languages"]),
        ("row", "frameworks", tools["frameworks"]),
        ("row", "platforms", tools["platforms"]),
        ("section", "BUILD.LOG", ""),
        ("row", "01", builds["01"]),
        ("row", "02", builds["02"]),
        ("row", "03", builds["03"]),
        ("section", "CONNECT", ""),
        ("row", "email", connect["email"]),
        ("row", "linkedin", connect["linkedin"]),
        ("row", "github", connect["github"]),
        ("status", "status", connect["status"]),
    ]


def build_svg(theme_name: str, profile: dict, ascii_lines: list[str]) -> str:
    theme = THEMES[theme_name]
    lines = profile_lines(profile)
    name = escape(profile["identity"]["name"])

    clip_paths: list[str] = []
    rendered_lines: list[str] = []
    line_start_y = 102.0
    line_spacing = 20.35

    for index, (kind, key, value) in enumerate(lines):
        y = line_start_y + index * line_spacing
        begin = 0.52 + index * 0.095
        clip_paths.append(
            f'<clipPath id="line-{index}">'
            f'<rect x="497" y="{y - 17:.2f}" width="658" height="22">'
            f'<animate attributeName="width" from="0" to="658" dur="0.34s" '
            f'begin="{begin:.2f}s" fill="freeze"/>'
            f'</rect></clipPath>'
        )

        if kind == "prompt":
            content = (
                f'<tspan class="prompt">{escape(key)}</tspan>'
                f'<tspan class="muted"> </tspan>'
                f'<tspan class="command">{escape(value)}</tspan>'
            )
        elif kind == "section":
            rule_length = max(12, 48 - len(key))
            content = (
                f'<tspan class="section">[ {escape(key)} ]</tspan>'
                f'<tspan class="rule"> {"─" * rule_length}</tspan>'
            )
        else:
            padded_key = f"{key:<13}"
            value_class = "status-value" if kind == "status" else "value"
            branch = "└─" if kind == "status" else "├─"
            content = (
                f'<tspan class="branch">{branch} </tspan>'
                f'<tspan class="key">{escape(padded_key)}</tspan>'
                f'<tspan class="separator">::</tspan>'
                f'<tspan class="{value_class}"> {escape(value)}</tspan>'
            )

        rendered_lines.append(
            f'<g clip-path="url(#line-{index})">'
            f'<text x="500" y="{y:.2f}">{content}</text>'
            f'</g>'
        )

    portrait_tspans: list[str] = []
    portrait_y = 105.0
    for line in ascii_lines:
        portrait_tspans.append(
            f'<tspan x="38" y="{portrait_y:.2f}" xml:space="preserve">{escape(line)}</tspan>'
        )
        portrait_y += ASCII_LINE_HEIGHT

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_WIDTH}" height="{CANVAS_HEIGHT}" viewBox="0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">{name} - AI Engineer and AI/ML Instructor</title>
  <desc id="desc">Animated terminal profile with an ASCII portrait, skills, projects, and contact details.</desc>
  <defs>
    <linearGradient id="background" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{theme['bg_top']}"/>
      <stop offset="100%" stop-color="{theme['bg_bottom']}"/>
    </linearGradient>
    <linearGradient id="portrait-gradient" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{theme['primary']}">
        <animate attributeName="stop-color" values="{theme['primary']};{theme['secondary']};{theme['primary_soft']};{theme['primary']}" dur="8s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" stop-color="{theme['secondary']}">
        <animate attributeName="stop-color" values="{theme['secondary']};{theme['accent']};{theme['primary']};{theme['secondary']}" dur="8s" repeatCount="indefinite"/>
      </stop>
    </linearGradient>
    <linearGradient id="border-gradient" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{theme['secondary']}"/>
      <stop offset="50%" stop-color="{theme['primary']}"/>
      <stop offset="100%" stop-color="{theme['accent']}"/>
    </linearGradient>
    <linearGradient id="scan-gradient" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{theme['primary']}" stop-opacity="0"/>
      <stop offset="50%" stop-color="{theme['primary_soft']}" stop-opacity="0.42"/>
      <stop offset="100%" stop-color="{theme['secondary']}" stop-opacity="0"/>
    </linearGradient>
    <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse">
      <path d="M 28 0 L 0 0 0 28" fill="none" stroke="{theme['grid']}" stroke-width="0.7" opacity="0.18"/>
    </pattern>
    <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="7" stdDeviation="12" flood-color="{theme['shadow']}" flood-opacity="0.22"/>
    </filter>
    <mask id="portrait-reveal">
      <rect x="0" y="0" width="430" height="490" fill="white">
        <animate attributeName="height" from="0" to="490" dur="2.35s" begin="0.15s" fill="freeze"/>
      </rect>
    </mask>
    {''.join(clip_paths)}
    <style>
      text, tspan {{ white-space: pre; }}
      .ui {{ font-family: 'Courier New', Consolas, monospace; }}
      .portrait {{ font-family: 'Courier New', Consolas, monospace; font-size: 7.15px; letter-spacing: -0.22px; fill: url(#portrait-gradient); }}
      .panel-label {{ font-family: 'Courier New', Consolas, monospace; font-size: 10.5px; font-weight: 700; letter-spacing: 2.2px; fill: {theme['primary']}; opacity: 0.76; }}
      .prompt {{ font-family: 'Courier New', Consolas, monospace; font-size: 14px; font-weight: 700; fill: {theme['accent']}; }}
      .command {{ font-family: 'Courier New', Consolas, monospace; font-size: 14px; fill: {theme['text']}; }}
      .muted {{ font-family: 'Courier New', Consolas, monospace; font-size: 14px; fill: {theme['muted']}; }}
      .section {{ font-family: 'Courier New', Consolas, monospace; font-size: 13.5px; font-weight: 700; fill: {theme['secondary']}; }}
      .rule {{ font-family: 'Courier New', Consolas, monospace; font-size: 13.5px; fill: {theme['branch']}; }}
      .branch {{ font-family: 'Courier New', Consolas, monospace; font-size: 13.2px; fill: {theme['branch']}; }}
      .key {{ font-family: 'Courier New', Consolas, monospace; font-size: 13.2px; font-weight: 700; fill: {theme['primary']}; }}
      .separator {{ font-family: 'Courier New', Consolas, monospace; font-size: 13.2px; fill: {theme['muted']}; }}
      .value {{ font-family: 'Courier New', Consolas, monospace; font-size: 13.2px; fill: {theme['text']}; }}
      .status-value {{ font-family: 'Courier New', Consolas, monospace; font-size: 13.2px; font-weight: 700; fill: {theme['accent']}; }}
      .portrait-name {{ font-family: 'Courier New', Consolas, monospace; font-size: 23px; font-weight: 800; letter-spacing: 4px; fill: {theme['text']}; }}
      .portrait-role {{ font-family: 'Courier New', Consolas, monospace; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; fill: {theme['primary']}; }}
      .top-label {{ font-family: 'Courier New', Consolas, monospace; font-size: 12px; fill: {theme['muted']}; }}
      .scan-label {{ font-family: 'Courier New', Consolas, monospace; font-size: 10px; font-weight: 700; letter-spacing: 1.1px; fill: {theme['red']}; }}
      .footer {{ font-family: 'Courier New', Consolas, monospace; font-size: 10.5px; font-weight: 700; letter-spacing: 0.8px; fill: {theme['muted']}; }}
      .footer-active {{ font-family: 'Courier New', Consolas, monospace; font-size: 10.5px; font-weight: 700; letter-spacing: 0.8px; fill: {theme['accent']}; }}
    </style>
  </defs>

  <rect width="1200" height="670" rx="18" fill="url(#background)"/>
  <rect width="1200" height="670" rx="18" fill="url(#grid)"/>

  <g id="titlebar">
    <rect x="2" y="2" width="1196" height="40" rx="16" fill="{theme['titlebar']}" opacity="0.94"/>
    <circle cx="24" cy="21" r="5" fill="{theme['red']}"/>
    <circle cx="42" cy="21" r="5" fill="{theme['amber']}"/>
    <circle cx="60" cy="21" r="5" fill="{theme['accent']}"/>
    <text x="600" y="26" text-anchor="middle" class="top-label">mussa@ai-lab ~ ./profile --live</text>
    <circle cx="1115" cy="21" r="4" fill="{theme['red']}">
      <animate attributeName="opacity" values="1;0.18;1" dur="1.15s" repeatCount="indefinite"/>
    </circle>
    <text x="1126" y="25" class="scan-label">LIVE</text>
  </g>

  <g filter="url(#shadow)">
    <rect x="18" y="55" width="445" height="559" rx="14" fill="{theme['panel']}" fill-opacity="0.72" stroke="url(#border-gradient)" stroke-opacity="0.50"/>
    <rect x="478" y="55" width="704" height="559" rx="14" fill="{theme['panel']}" fill-opacity="0.72" stroke="url(#border-gradient)" stroke-opacity="0.50"/>
  </g>

  <text x="34" y="78" class="panel-label">PORTRAIT.STREAM</text>
  <text x="496" y="78" class="panel-label">SYSTEM.PROFILE</text>

  <g mask="url(#portrait-reveal)" filter="url(#glow)">
    <text x="38" y="105" class="portrait">{''.join(portrait_tspans)}</text>
  </g>
  <text x="241" y="570" text-anchor="middle" class="portrait-name">{name.upper()}</text>
  <text x="241" y="593" text-anchor="middle" class="portrait-role">AI ENGINEER // INSTRUCTOR // BUILDER</text>

  <g id="terminal-lines">{''.join(rendered_lines)}</g>
  <rect x="501" y="584" width="8" height="14" fill="{theme['primary']}" opacity="1">
    <animate attributeName="opacity" values="1;0;1" dur="0.92s" begin="2.9s" repeatCount="indefinite"/>
  </rect>

  <rect x="0" y="-64" width="1200" height="64" fill="url(#scan-gradient)" opacity="0.50">
    <animateTransform attributeName="transform" type="translate" from="0 48" to="0 700" dur="4.6s" repeatCount="indefinite"/>
  </rect>

  <g id="footer">
    <circle cx="28" cy="642" r="4" fill="{theme['accent']}">
      <animate attributeName="r" values="3.5;5;3.5" dur="1.8s" repeatCount="indefinite"/>
    </circle>
    <text x="40" y="646" class="footer-active">SYSTEM ONLINE</text>
    <text x="600" y="646" text-anchor="middle" class="footer">AGENTIC AI · LLMs · COMPUTER VISION · AUTOMATION</text>
    <text x="1170" y="646" text-anchor="end" class="footer">@musagithub1</text>
  </g>

  <rect x="2" y="2" width="1196" height="666" rx="16" fill="none" stroke="url(#border-gradient)" stroke-width="2" opacity="0.80">
    <animate attributeName="opacity" values="0.52;0.92;0.52" dur="3.4s" repeatCount="indefinite"/>
  </rect>
</svg>
'''
    return svg


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--avatar", type=Path, default=DEFAULT_AVATAR)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--output", type=Path, default=ROOT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    profile = load_profile(args.profile)
    portrait = make_ascii_portrait(args.avatar)
    args.output.mkdir(parents=True, exist_ok=True)

    for theme_name in THEMES:
        output_path = args.output / f"{theme_name}.svg"
        output_path.write_text(
            build_svg(theme_name, profile, portrait),
            encoding="utf-8",
        )
        print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
