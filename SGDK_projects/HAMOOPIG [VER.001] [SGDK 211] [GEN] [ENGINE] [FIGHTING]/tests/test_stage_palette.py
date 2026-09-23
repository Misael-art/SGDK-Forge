#!/usr/bin/env python3
"""Static VDP palette contract; not a runtime fidelity/budget verdict."""
import hashlib
import json
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
path = root / 'res/gfx/showdown.png'
report = json.loads(path.with_suffix('.json').read_text())
im = Image.open(path)
assert im.mode == 'P' and im.size == (512, 256)
indices = set(im.get_flattened_data())
assert 0 not in indices, 'BG_B zero reveals backdrop instead of opaque source'
assert min(indices) >= 1 and max(indices) <= 14
palette = im.getpalette()
assert all(palette[3*i+c] % 34 == 0 for i in indices for c in range(3))
assert report['output_sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
assert report['source_sha256'] == hashlib.sha256((root/report['source']).read_bytes()).hexdigest()
assert report['unique_output_tiles'] == 864
assert report['source'] == 'rascunho/showdown_native_crop_preview.png'
assert report['refine_iterations'] == 4
print('PASS: opaque indices 1..14, 9-bit palette, source/output binding, 864-tile report')
