"""Compose the runtime life atlas from the authored HUD chassis and fill.

The chassis is the persisted blue/gold artwork.  The legacy bar is used only
as an authored fill-state source; no runtime geometry is generated.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
CHASSIS = ROOT / "res/sprite/hud/life_track_empty.png"
FILL = ROOT / "res/sprite/hud/energy_yellow.png"
OUT_P1 = ROOT / "res/sprite/hud/energy_authorial_p1.png"
OUT_P2 = ROOT / "res/sprite/hud/energy_authorial_p2.png"
REPORT = ROOT / "rascunho/authorial_energy_bar_report.json"


def build(mirror: bool = False) -> Image.Image:
    chassis = Image.open(CHASSIS).convert("P")
    fill = Image.open(FILL).convert("P")
    palette = fill.getpalette()
    atlas = Image.new("P", (128 * 13, 16), 0)
    atlas.putpalette(palette)
    for frame in range(13):
        base = chassis.copy()
        base.putpalette(palette)
        src = fill.crop((frame * 128, 0, (frame + 1) * 128, 16))
        # Keep the authored gold caps, top glint and blue lower rail visible.
        # The source fill supplies the yellow active field only in the inner
        # 112px well of the chassis.
        for y in range(2, 9):
            for x in range(1, 127):
                target_x = 8 + (x - 1)
                if target_x > 119:
                    break
                pixel = src.getpixel((x, y))
                if pixel != 0:
                    base.putpixel((target_x, y), pixel)
        if mirror:
            base = base.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        atlas.paste(base, (frame * 128, 0))
    return atlas


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT_P1.parent.mkdir(parents=True, exist_ok=True)
    build().save(OUT_P1, optimize=False, transparency=0)
    build(mirror=True).save(OUT_P2, optimize=False, transparency=0)
    report = {
        "source_chassis": str(CHASSIS.relative_to(ROOT)),
        "source_fill": str(FILL.relative_to(ROOT)),
        "frames": 13,
        "frame_size": [128, 16],
        "outputs": {
            "p1": {"path": str(OUT_P1.relative_to(ROOT)), "sha256": digest(OUT_P1)},
            "p2": {"path": str(OUT_P2.relative_to(ROOT)), "sha256": digest(OUT_P2)},
        },
        "acceptance_status": "placeholder",
        "visual_review_required": True,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
