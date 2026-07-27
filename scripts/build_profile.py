#!/usr/bin/env python3
"""
Build script for Mohammad Al-Najjar's GitHub profile hero assets.

Generates:
  assets/mohammad.webp     - Optimized portrait
  assets/profile-dark.svg  - Dark mode hero (portrait embedded as base64)
  assets/profile-light.svg - Light mode hero (portrait embedded as base64)

Usage:
  python scripts/build_profile.py [--portrait PATH]

Requirements:
  pip install Pillow
"""

import argparse
import base64
import io
import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Run: pip install Pillow", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

DEFAULT_PORTRAIT = ASSETS / "mohammad.webp"
LOCAL_PORTRAIT = Path.home() / "Desktop" / "portfolio" / "images" / "profile.jpg.jpeg"

DARK_COLORS = {
    "bg": "#0D1117",
    "border": "#30363D",
    "separator": "#21262D",
    "brand": "#58A6FF",
    "name": "#F0F6FC",
    "title": "#8B949E",
    "label": "#58A6FF",
    "value": "#C9D1D9",
    "footer": "#8B949E",
    "dot_sep": "#484F58",
    "status": "#3FB950",
}

LIGHT_COLORS = {
    "bg": "#FFFFFF",
    "border": "#D0D7DE",
    "separator": "#D8DEE4",
    "brand": "#0969DA",
    "name": "#1F2328",
    "title": "#656D76",
    "label": "#0969DA",
    "value": "#1F2328",
    "footer": "#656D76",
    "dot_sep": "#AFB8C1",
    "status": "#1A7F37",
}


def process_portrait(src: Path, dst: Path) -> str:
    """Convert portrait to optimized webp and return base64-encoded PNG for SVG embedding."""
    img = Image.open(src)

    # Optimized webp
    webp = img.copy()
    webp.thumbnail((600, 800), Image.LANCZOS)
    webp.save(dst, "WEBP", quality=85)

    # Square crop for SVG
    w, h = img.size
    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    cropped = img.crop((left, top, left + side, top + side))
    cropped.thumbnail((400, 400), Image.LANCZOS)

    buf = io.BytesIO()
    cropped.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def build_svg(b64: str, colors: dict, suffix: str) -> str:
    """Generate the hero SVG with embedded portrait."""
    clip_id = f"portrait-clip{suffix}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 280" role="img" aria-labelledby="hero-title{suffix} hero-desc{suffix}">
  <title id="hero-title{suffix}">Mohammad Al-Najjar — Software Engineer</title>
  <desc id="hero-desc{suffix}">Developer identity card for Mohammad Al-Najjar</desc>

  <defs>
    <clipPath id="{clip_id}">
      <rect x="28" y="20" width="160" height="240" rx="8" ry="8"/>
    </clipPath>
  </defs>

  <rect width="850" height="280" rx="12" fill="{colors['bg']}"/>
  <rect x="1" y="1" width="848" height="278" rx="11" fill="none" stroke="{colors['border']}" stroke-width="1"/>

  <image x="28" y="20" width="160" height="240" clip-path="url(#{clip_id})" href="data:image/png;base64,{b64}" preserveAspectRatio="xMidYMid slice"/>
  <rect x="28" y="20" width="160" height="240" rx="8" ry="8" fill="none" stroke="{colors['border']}" stroke-width="1.5"/>

  <text x="218" y="42" font-family="monospace" font-size="11" fill="{colors['brand']}" letter-spacing="2.5" font-weight="500">MOHAMMAD.DEV</text>

  <text x="218" y="78" font-family="sans-serif" font-size="28" fill="{colors['name']}" font-weight="600" letter-spacing="-0.5">Mohammad Al-Najjar</text>

  <text x="218" y="102" font-family="monospace" font-size="12" fill="{colors['title']}" letter-spacing="3">SOFTWARE ENGINEER</text>

  <line x1="218" y1="118" x2="820" y2="118" stroke="{colors['separator']}" stroke-width="1"/>

  <text x="218" y="142" font-family="monospace" font-size="10" fill="{colors['label']}" letter-spacing="1.5" font-weight="500">FOCUS</text>
  <text x="290" y="142" font-family="sans-serif" font-size="12" fill="{colors['value']}">Full-Stack Engineering · Database Systems · Problem Solving</text>

  <text x="218" y="164" font-family="monospace" font-size="10" fill="{colors['label']}" letter-spacing="1.5" font-weight="500">CURRENT</text>
  <text x="298" y="164" font-family="sans-serif" font-size="12" fill="{colors['value']}">Full-Stack Developer Trainee @ Daleel Academy</text>

  <text x="218" y="186" font-family="monospace" font-size="10" fill="{colors['label']}" letter-spacing="1.5" font-weight="500">EDUCATION</text>
  <text x="308" y="186" font-family="sans-serif" font-size="12" fill="{colors['value']}">B.Sc. Computer Science — Jadara University</text>

  <text x="218" y="208" font-family="monospace" font-size="10" fill="{colors['label']}" letter-spacing="1.5" font-weight="500">LEARNING</text>
  <text x="304" y="208" font-family="sans-serif" font-size="12" fill="{colors['value']}">Oracle SQL · Algorithms &amp; Data Structures · Software Design</text>

  <line x1="28" y1="240" x2="820" y2="240" stroke="{colors['separator']}" stroke-width="1"/>

  <text x="28" y="262" font-family="sans-serif" font-size="11" fill="{colors['footer']}">Jordan</text>
  <text x="92" y="262" font-family="sans-serif" font-size="11" fill="{colors['dot_sep']}">·</text>
  <text x="108" y="262" font-family="monospace" font-size="11" fill="{colors['footer']}">github.com/mohammadalnajjar04</text>

  <circle cx="800" cy="258" r="4" fill="{colors['status']}"/>
  <text x="810" y="262" font-family="monospace" font-size="10" fill="{colors['status']}" letter-spacing="1" font-weight="500">BUILDING</text>
</svg>'''


def main():
    parser = argparse.ArgumentParser(description="Build profile hero assets")
    parser.add_argument("--portrait", type=Path, default=None, help="Path to portrait image")
    args = parser.parse_args()

    if args.portrait is None:
        if LOCAL_PORTRAIT.exists():
            args.portrait = LOCAL_PORTRAIT
        elif DEFAULT_PORTRAIT.exists():
            args.portrait = DEFAULT_PORTRAIT
        else:
            print("Error: No portrait found. Provide --portrait or place image at assets/mohammad.webp", file=sys.stderr)
            sys.exit(1)

    if not args.portrait.exists():
        print(f"Error: Portrait not found at {args.portrait}", file=sys.stderr)
        sys.exit(1)

    print(f"Processing portrait: {args.portrait}")
    b64 = process_portrait(args.portrait, ASSETS / "mohammad.webp")
    print(f"  WebP: {(ASSETS / 'mohammad.webp').stat().st_size:,} bytes")

    dark = build_svg(b64, DARK_COLORS, "")
    (ASSETS / "profile-dark.svg").write_text(dark, encoding="utf-8")
    print(f"  Dark SVG:  {len(dark):,} bytes")

    light = build_svg(b64, LIGHT_COLORS, "-l")
    (ASSETS / "profile-light.svg").write_text(light, encoding="utf-8")
    print(f"  Light SVG: {len(light):,} bytes")

    print("Build complete.")


if __name__ == "__main__":
    main()
