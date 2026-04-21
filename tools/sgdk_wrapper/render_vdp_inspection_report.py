#!/usr/bin/env python3
"""
Render VDP Inspection Report — HTML visual report from vdp_inspection.json.

Part of the AAA agent ecosystem. Reads the VDP inspection artifact and
generates a human-readable HTML report with palette visualization,
tile usage charts, and sprite layout overview.

This script does NOT modify any existing wrapper behavior.
It writes only to out/reports/.

Usage:
    python render_vdp_inspection_report.py --input <json> --output <html>
"""

import argparse
import json
import os
import sys
from datetime import datetime


def hex_to_style(hex_rgb: str) -> str:
    """Convert #RRGGBB to CSS background style."""
    return f"background-color:{hex_rgb};width:20px;height:20px;display:inline-block;border:1px solid #333;"


def render_palette_html(palette_data: dict) -> str:
    """Render palette swatches as HTML."""
    if not palette_data or "palettes" not in palette_data:
        return "<p>No palette data available.</p>"

    lines = ['<div class="section"><h2>Palettes (CRAM)</h2>']
    for pal in palette_data["palettes"]:
        idx = pal.get("index", "?")
        unique = pal.get("unique_colors", 0)
        lines.append(f'<h3>Palette {idx} ({unique} unique colors)</h3>')
        lines.append('<div class="palette-row">')
        for entry in pal.get("entries", []):
            hex_rgb = entry.get("hex_rgb", "#000000")
            raw = entry.get("raw_value", 0)
            title = f"#{entry.get('index',0)}: {hex_rgb} (raw=0x{raw:03X})"
            lines.append(f'<span style="{hex_to_style(hex_rgb)}" title="{title}"></span>')
        lines.append("</div>")
    lines.append("</div>")
    return "\n".join(lines)


def render_tile_html(tile_data: dict) -> str:
    """Render tile usage stats as HTML."""
    if not tile_data:
        return "<p>No tile data available.</p>"

    total = tile_data.get("total_tiles", 0)
    used = tile_data.get("used_tiles", 0)
    unique = tile_data.get("unique_tiles", 0)
    dup = tile_data.get("duplicate_tiles", 0)
    frac = tile_data.get("usage_fraction", 0)
    pct = round(frac * 100, 1)

    bar_width = min(100, int(pct))
    color = "#4CAF50" if pct < 80 else "#FF9800" if pct < 95 else "#F44336"

    return f"""
    <div class="section">
        <h2>Tile Usage (VRAM)</h2>
        <div class="progress-bar" style="width:400px;height:24px;background:#ddd;border-radius:4px;overflow:hidden;">
            <div style="width:{bar_width}%;height:100%;background:{color};"></div>
        </div>
        <p>{used}/{total} tiles used ({pct}%) — {unique} unique, {dup} duplicate</p>
    </div>
    """


def render_sprite_html(sprite_data: dict) -> str:
    """Render sprite table summary as HTML."""
    if not sprite_data:
        return "<p>No sprite data available.</p>"

    count = sprite_data.get("sprite_count", 0)
    max_sl = sprite_data.get("max_sprites_per_scanline", 0)
    hotspots = sprite_data.get("hotspot_scanlines", [])

    lines = [
        '<div class="section">',
        "<h2>Sprites (SAT)</h2>",
        f"<p><strong>{count}/80</strong> active sprites, <strong>{max_sl}/20</strong> max per scanline</p>",
    ]

    if hotspots:
        lines.append("<h3>Hotspot Scanlines</h3><table><tr><th>Scanline</th><th>Sprites</th></tr>")
        for hs in hotspots[:10]:
            sl = hs.get("scanline", "?")
            sc = hs.get("sprite_count", 0)
            warn = ' style="color:red;font-weight:bold;"' if sc >= 20 else ""
            lines.append(f"<tr><td>{sl}</td><td{warn}>{sc}</td></tr>")
        lines.append("</table>")

    # Sprite detail table
    sprites = sprite_data.get("sprites", [])
    if sprites:
        lines.append("<h3>Sprite Table</h3><table>")
        lines.append("<tr><th>#</th><th>X</th><th>Y</th><th>Size</th><th>Tile</th><th>Pal</th><th>Pri</th><th>Flip</th><th>Link</th></tr>")
        for s in sprites[:80]:
            flip = ""
            if s.get("h_flip"):
                flip += "H"
            if s.get("v_flip"):
                flip += "V"
            if not flip:
                flip = "-"
            lines.append(
                f"<tr><td>{s.get('index',0)}</td><td>{s.get('x',0)}</td><td>{s.get('y',0)}</td>"
                f"<td>{s.get('width_tiles',1)}x{s.get('height_tiles',1)}</td>"
                f"<td>{s.get('tile_index',0)}</td><td>{s.get('palette',0)}</td>"
                f"<td>{'Y' if s.get('priority') else 'N'}</td><td>{flip}</td>"
                f"<td>{s.get('link',0)}</td></tr>"
            )
        lines.append("</table>")

    lines.append("</div>")
    return "\n".join(lines)


def render_report(data: dict) -> str:
    """Render complete HTML report."""
    scene_id = data.get("scene_id", "unknown")
    status = data.get("inspection_status", "?")
    generated = data.get("generated_at", "?")
    notes = data.get("inspection_notes", "")

    status_color = {"ok": "#4CAF50", "warn": "#FF9800", "error": "#F44336"}.get(status, "#999")

    palette_html = render_palette_html(data.get("palette_snapshots"))
    tile_html = render_tile_html(data.get("tile_usage"))
    sprite_html = render_sprite_html(data.get("sprite_snapshot"))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>VDP Inspection: {scene_id}</title>
<style>
    body {{ font-family: 'Consolas', 'Courier New', monospace; background: #1a1a2e; color: #eee; margin: 20px; }}
    h1 {{ color: #e94560; }}
    h2 {{ color: #0f3460; background: #16213e; padding: 8px 12px; border-left: 4px solid #e94560; }}
    h3 {{ color: #ccc; }}
    .status {{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-weight: bold;
               background: {status_color}; color: white; }}
    .section {{ margin: 20px 0; padding: 12px; background: #16213e; border-radius: 6px; }}
    .palette-row {{ display: flex; gap: 2px; margin: 8px 0; }}
    table {{ border-collapse: collapse; margin: 8px 0; }}
    th, td {{ border: 1px solid #333; padding: 4px 8px; text-align: center; }}
    th {{ background: #0f3460; }}
    tr:nth-child(even) {{ background: #1a1a3e; }}
    .meta {{ color: #888; font-size: 0.85em; }}
</style>
</head>
<body>
<h1>VDP Inspection: {scene_id}</h1>
<p>Status: <span class="status">{status.upper()}</span></p>
<p class="meta">Generated: {generated} | Tool: inspect_vdp_scene_state v{data.get('tool_version', '?')}</p>
{"<p><strong>Notes:</strong> " + notes + "</p>" if notes else ""}

{palette_html}
{tile_html}
{sprite_html}

<hr>
<p class="meta">Report generated by render_vdp_inspection_report.py — AAA Agent Ecosystem</p>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Render VDP inspection report as HTML")
    parser.add_argument("--input", required=True, help="Path to vdp_inspection.json")
    parser.add_argument("--output", required=True, help="Path for output HTML file")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[ERROR] Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    html = render_report(data)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK]    HTML report written to: {args.output}")


if __name__ == "__main__":
    main()
