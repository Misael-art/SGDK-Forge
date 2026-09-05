#!/usr/bin/env python3
"""Permanent adversarial fixtures for the independent material meter."""
import json, tempfile, sys
from pathlib import Path
from PIL import Image

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import repair_material_topology_meter_v02 as meter

LAB=HERE.parent
OUT=LAB/'localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v05'
PNG=OUT/'hybrid_cleanup_primary_im_lanczos3_rework_v05.png'
MAP=OUT/'material_owner_map_v01.json'

def load_map():
    obj=json.loads(MAP.read_text())
    rev=obj['owner_encoding']
    rows=obj['rows']
    assert len(rows)==meter.H and all(len(row)==meter.W for row in rows)
    return [rev[ch] for row in rows for ch in row]
def synthetic(changes):
    with Image.open(PNG) as src:
        im=src.copy(); vals=list(im.getdata()); pal=im.getpalette()
    for x,y,index in changes: vals[y*meter.W+x]=index
    im.putdata(vals)
    f=tempfile.NamedTemporaryFile(suffix='.png',delete=False); f.close()
    path=Path(f.name); im.save(path,'PNG',bits=4,transparency=0); return path

def main():
    owners=load_map(); base=meter.evaluate(PNG,owners,MAP)
    # Full coverage is not enough: a rectangular/all-skin map fails anchors.
    rectangle=['skin' if o!='transparent' else 'transparent' for o in owners]
    assert meter.evaluate(PNG,rectangle,MAP)['ownership_annotation_error']>0
    # One accidental contact cannot satisfy an expected boundary segment.
    broken=owners[:]; (ax,ay),(bx,by)=meter.BOUNDARIES['hair_skin'][0]; broken[by*meter.W+bx]=broken[ay*meter.W+ax]
    assert not meter.boundary_results(broken)['hair_skin']['status']
    # Removing explicit outline ownership is a hard failure.
    no_outline=['skin' if o=='outline_shared' else o for o in owners]
    assert meter.evaluate(PNG,no_outline,MAP)['ownership_annotation_error']>0
    # Index 2 is not a globally shared shadow; placing it in skin is leakage.
    bad_shadow=synthetic([(27,12,2)])
    try:
        bad=meter.evaluate(bad_shadow,owners,MAP); assert bad['shared_family_valid']['index_2_global_shadow_reuse']
    finally: bad_shadow.unlink(missing_ok=True)
    # Semantic wraps and sash may share the teal family; feet may share skin.
    assert base['shared_family_valid']['wraps_and_sash_share_teal_fabric']
    assert base['shared_family_valid']['feet_share_skin']
    # Orange inside a skin-owned coordinate is a real palette leak.
    bad_orange=synthetic([(27,12,8)])
    try: assert meter.evaluate(bad_orange,owners,MAP)['material_palette_leakage']>base['material_palette_leakage']
    finally: bad_orange.unlink(missing_ok=True)
    # No-op attempts remain visible in the accounting, not silently discarded.
    actions=json.loads((OUT/'cleanup_actions.json').read_text())
    assert actions['patches_attempted']==23 and actions['patches_effective']==18 and actions['patches_noop']==5
    print(json.dumps({'status':'passed','fixtures':8,'base_status':base['status'],'base_ownership_annotation_error':base['ownership_annotation_error'],'base_material_palette_leakage':base['material_palette_leakage']},ensure_ascii=False))
if __name__=='__main__': main()
