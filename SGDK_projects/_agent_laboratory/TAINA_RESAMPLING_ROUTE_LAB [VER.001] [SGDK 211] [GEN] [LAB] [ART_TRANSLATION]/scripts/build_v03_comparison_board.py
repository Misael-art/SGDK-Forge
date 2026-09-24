#!/usr/bin/env python3
import argparse
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def font(size):
    try:
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size)
    except OSError:
        return ImageFont.load_default()

def thumb(path, size, bg):
    image = Image.open(path).convert('RGBA')
    image.thumbnail(size, Image.Resampling.NEAREST)
    out = Image.new('RGBA', size, bg + (255,))
    out.alpha_composite(image, ((size[0]-image.width)//2, (size[1]-image.height)//2))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lab-root', type=Path, required=True)
    args = ap.parse_args()
    lab = args.lab_root.resolve()
    parent = lab/'localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v01'
    current = lab/'localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v03'
    board = Image.new('RGBA', (1120, 760), (10, 12, 18, 255))
    draw = ImageDraw.Draw(board)
    draw.text((24, 18), 'TAINA — PRIMARY / LOCALIZED ARTISTIC REWORK', fill=(245, 240, 220), font=font(18))
    draw.text((24, 48), 'Parent control vs v03; 56x80; technical pass, visual rework; human pending.', fill=(180, 190, 205), font=font(12))
    entries = [
        ('PARENT CONTROL / v01', parent/'preview_nearest_8x.png', '27-patch localized control; not current'),
        ('CURRENT REWORK / v03', current/'preview_nearest_8x.png', '44 non-null patches; ground strip removed; map independent'),
    ]
    for index, (label, path, note) in enumerate(entries):
        x = 24 + index*536
        draw.rectangle((x, 82, x+512, 700), outline=(72, 82, 104), width=1)
        draw.text((x+14, 96), label, fill=(240, 235, 215), font=font(13))
        board.alpha_composite(thumb(path, (480, 560), (235, 235, 235) if index == 0 else (24, 26, 32)), (x+16, 124))
        draw.text((x+14, 644), note, fill=(205, 210, 220), font=font(12))
        draw.text((x+14, 668), 'No res/ • no animation • no runtime • no visual_pass', fill=(225, 180, 110), font=font(11))
    board.convert('RGB').save(lab/'localized_native_cleanup_v03_comparison_board.png')
    sys.path.insert(0, str(lab.parents[2]/'tools/sgdk_wrapper'))
    from forge_art import pixel_contract
    output = current/'hybrid_cleanup_primary_im_lanczos3_rework_v03.png'
    validation = pixel_contract.validate_png(output, 'transparent0')
    validation_report = {
        'schema_version': 'localized_native_cleanup_validation.v2',
        'asset_id': 'hybrid_cleanup_primary_im_lanczos3_rework_v03',
        'path': str(output.relative_to(lab)),
        'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
        'pixel_contract': {key: validation[key] for key in ('status','blocking','content_sha256','visible_colors','plte_entries','bit_depth','width','height')},
        'index0_role': 'transparent0',
        'method': 'mechanical_palette_remap_with_minimal_native_patches',
        'native_cleanup': 'incomplete',
        'material_topology': 'not_run',
        'semantic_map': 'derived_diagnostic_not_independent',
        'independent_topology_map': 'independent_material_topology_map.png',
        'patch_log': 'cleanup_actions.json',
        'patch_count': 44,
        'null_patches_count': 0,
        'ground_contact_report': 'ground_contact_report.json',
        'human_gate_status': 'pending_human_decision',
        'visual_status': 'technical_pass_visual_rework',
        'res_promotion': False,
        'animation_authorization': False,
        'rom_authorization': False,
        'notes': [
            'v03 starts from the v01 parent control and preserves macrogeometry.',
            'v02 is discarded as a broad-remap visual regression and is not a source.',
            'the independent map is a diagnostic ownership hypothesis, not proof of artistic material separation.'
        ]
    }
    (current/'localized_native_cleanup_validation_report.json').write_text(json.dumps(validation_report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    gate = '''# TAINA — PRIMARY localized cleanup human gate

Rework vigente: `hybrid_cleanup_primary_im_lanczos3_rework_v03`

PNG: `localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v03/hybrid_cleanup_primary_im_lanczos3_rework_v03.png`

SHA-256: `99160ec422010d2ac68fbb4b10cc03db72012316508882e1b9b8cf336ec51a33`

Escala: `56x80`

Escopo: `localized_native_cleanup_only`

Status honesto: `technical_pass_visual_rework`; `native_cleanup=incomplete`; `material_topology=not_run`; `semantic_map=derived_diagnostic_not_independent`.

Verificar em 1x: rosto/olho e direção do olhar, cachos e separação cabelo-rosto, punhos/wraps/antebraços, hem/axilas/abdômen, nó e caimento do sash, calças, pés e ausência de faixa de chão assada. A v02 está descartada por regressão visual.

Resposta aceita:

```text
decision=approve_localized_native_cleanup
asset_id=hybrid_cleanup_primary_im_lanczos3_rework_v03
sha256=99160ec422010d2ac68fbb4b10cc03db72012316508882e1b9b8cf336ec51a33
scale=56x80
```

ou:

```text
decision=reject_localized_native_cleanup
reason=<motivo observável>
```

Nada neste gate libera `res/`, animação, runtime, ROM, `visual_pass` ou AAA.
'''
    (lab/'human_gate_request_localized_cleanup.md').write_text(gate, encoding='utf-8')

if __name__ == '__main__':
    main()
