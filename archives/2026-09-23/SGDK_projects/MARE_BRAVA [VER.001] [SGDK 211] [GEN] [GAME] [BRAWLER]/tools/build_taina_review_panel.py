from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "out" / "evidence" / "taina_native_lineart_editor_v01"
out.mkdir(parents=True, exist_ok=True)
items = [
    ("model sheet / direction", ROOT / "data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png", 0),
    ("construction reference (not asset)", ROOT / "data/source_art/concept/taina_pixel_model_sheet/construction_reference/taina_reseed_native_lineart_candidate_imagegen_v02.png", 0),
    ("native candidate 1x", ROOT / "data/processed/characters/taina/native_lineart/taina_reseed_native_lineart_editor_candidate_v01_indexed.png", 1),
    ("native candidate nearest 8x", ROOT / "data/processed/characters/taina/native_lineart/taina_reseed_native_lineart_editor_candidate_v01_indexed.png", 8),
]
font = ImageFont.load_default()
panel_w, panel_h = 1200, 860
panel = Image.new("RGB", (panel_w, panel_h), (28, 30, 38))
d = ImageDraw.Draw(panel)
cell_w, cell_h = 280, 390
for i, (label, path, scale) in enumerate(items):
    src = Image.open(path).convert("RGBA")
    if scale == 0:
        src.thumbnail((cell_w - 20, cell_h - 48), Image.Resampling.LANCZOS)
    else:
        src = src.resize((src.width * scale, src.height * scale), Image.Resampling.NEAREST)
        src.thumbnail((cell_w - 20, cell_h - 48), Image.Resampling.NEAREST)
    x = 20 + (i % 4) * 295
    y = 44
    bg = Image.new("RGB", (cell_w, cell_h), (238, 238, 230) if i < 2 else (180, 190, 202))
    px = ((cell_w - src.width) // 2, 28 + (cell_h - 48 - src.height) // 2)
    bg.paste(src, px, src)
    panel.paste(bg, (x, y))
    d.text((x, 16), label, fill=(255, 255, 255), font=font)
    d.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline=(110, 120, 135), width=2)
d.text((20, 470), "TAÍNA native lineart review panel — technical candidate only", fill=(255, 220, 120), font=font)
d.text((20, 500), "48×64 · 1 px hard edge · index 0 transparent · 1 visible ink color · human visual approval pending", fill=(220, 225, 232), font=font)
d.text((20, 540), "Technical gate: passed. Visual gate: pending/rework; no BASIC/ELITE or res promotion.", fill=(220, 225, 232), font=font)
d.text((20, 580), "Source and construction reference are shown for comparison only; candidate is separately authored in native grid.", fill=(180, 190, 202), font=font)
panel.save(out / "taina_native_lineart_review_panel_v01.png", optimize=True)
print(out / "taina_native_lineart_review_panel_v01.png")
