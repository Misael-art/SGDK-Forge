#!/usr/bin/env python3
"""Apply the selected incumbent's localized native cleanup in the lab."""
import argparse, hashlib, json, sys, time
from pathlib import Path
from PIL import Image

W,H=56,80
INCUMBENT="hybrid_cleanup_primary_im_lanczos3_v01"
INCUMBENT_SHA="3e60cd9efb233d0ce715c543e9cacdaacbe044b253c088dd06ada52f131b4cf1"
OUT_ID="hybrid_cleanup_primary_im_lanczos3_rework_v01"
# Explicit native-grid changes only; no shape primitive, resize or source replacement.
PATCHES=[]
for x in range(15,37): PATCHES.append((x,77,0,"remove_baked_ground_shadow_between_feet"))
PATCHES += [
    (31,13,1,"close_face_side_contour_at_eye_line"),
    (40,27,1,"separate_guard_wrap_from_background_edge"),
    (18,38,12,"close_sash_knot_boundary"),
    (19,38,1,"outline_sash_knot_boundary"),
    (42,41,0,"remove_isolated_sash_edge_pixel"),
]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--lab-root",type=Path,required=True); a=ap.parse_args(); lab=a.lab_root.resolve(); start=time.perf_counter()
    sys.path.insert(0,str(lab/"scripts")); import run_hybrid_cleanup_shootout as base
    parent=lab/"hybrid_cleanup_shootout"/INCUMBENT/(INCUMBENT+".png")
    if sha(parent)!=INCUMBENT_SHA: raise SystemExit("incumbent hash mismatch")
    with Image.open(parent) as source: im=source.convert("P"); grid=list(im.getdata())
    actions=[]
    for x,y,after,reason in PATCHES:
        pos=y*W+x; before=grid[pos]; grid[pos]=after; actions.append({"kind":"native_pixel_patch","x":x,"y":y,"before":before,"after":after,"reason":reason})
    out=lab/"localized_native_cleanup"/OUT_ID; out.mkdir(parents=True,exist_ok=True); png=out/(OUT_ID+".png")
    result=Image.new("P",(W,H),0); result.putpalette(base.palette_bytes()); result.putdata(grid); result.save(png,"PNG",bits=4,transparency=0); base.evidence(result,out)
    log={"schema_version":"localized_native_cleanup_action_log.v1","asset_id":OUT_ID,"parent_asset_id":INCUMBENT,"parent_sha256":INCUMBENT_SHA,"scope":"localized_native_cleanup_only","source_pixels_reused":True,"actions":actions,"regions":["face_eye","shoulder_arm_attachment","diagonal_guard","sash_knot","feet_ground"],"ground_shadow_between_feet_removed":True,"elapsed_seconds":round(time.perf_counter()-start,6),"human_approval":"pending"}
    lp=out/"cleanup_actions.json"; lp.write_text(json.dumps(log,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    report={"schema_version":"localized_native_cleanup_rework.v1","asset_id":OUT_ID,"status":"localized_native_cleanup_candidate","parent":{"asset_id":INCUMBENT,"sha256":INCUMBENT_SHA,"path":str(parent.relative_to(lab))},"selected_by":"contracts/human_hybrid_cleanup_shootout_selection_v01.json","target":"56x80","scope":"localized_native_cleanup_only","geometry_policy":"parent silhouette retained except removal of baked ground-shadow strip between feet; no resize or primitives","modified_regions":log["regions"],"patch_count":len(actions),"ground_shadow_between_feet_removed":True,"claim_ceiling":"localized_native_cleanup_candidate","human_gate_status":"pending_human_decision","res_promotion":False,"animation_authorization":False,"output":{"path":str(png.relative_to(lab)),"sha256":sha(png)},"action_log":{"path":str(lp.relative_to(lab)),"sha256":sha(lp)}}
    (out/"localized_native_cleanup_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (lab/"localized_native_cleanup_manifest.json").write_text(json.dumps({"schema_version":"localized_native_cleanup_manifest.v1","decision":"select_hybrid_cleanup_incumbent_for_rework","asset_id":INCUMBENT,"sha256":INCUMBENT_SHA,"scale":"56x80","approval_scope":"localized_native_cleanup_only","res_promotion":False,"animation_authorization":False,"incumbent_rework":{"asset_id":OUT_ID,"path":str(png.relative_to(lab)),"sha256":sha(png),"claim_ceiling":"localized_native_cleanup_candidate"},"human_gate_status":"pending_human_decision"},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":"completed","asset_id":OUT_ID,"sha256":sha(png),"patches":len(actions)},ensure_ascii=False))
if __name__=="__main__": main()
