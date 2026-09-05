#!/usr/bin/env python3
"""Run the approved hybrid-cleanup shootout inside the isolated lab.

The selected route pixels may survive as a starting raster, but the output is
not blind promotion: alpha/matte cleanup, semantic palette ownership and a
small explicit native-grid patch list are recorded for human review.
No v01-v04 pixels are read and no character shape is drawn from primitives.
"""
import argparse, hashlib, json, time
from pathlib import Path
from PIL import Image, ImageDraw

W, H = 56, 80
PALETTE = [(0,0,0),(34,0,0),(34,0,34),(68,34,68),(102,68,34),(136,68,34),(170,102,34),(204,136,68),(204,68,0),(238,102,0),(238,136,68),(0,68,68),(0,136,136),(0,170,170),(0,0,68),(34,34,102)]
ROLES = ["transparent0","outline_deep_shadow","hair_deep","hair_base","hair_highlight","skin_shadow","skin_base","skin_highlight","top_shadow","top_base","top_highlight","teal_shadow","teal_base","teal_highlight","indigo_shadow","indigo_base"]
OWNER = {0: "transparent", 1: "outline", 2: "hair", 3: "hair", 4: "hair", 5: "skin", 6: "skin", 7: "skin", 8: "orange_top", 9: "orange_top", 10: "orange_top", 11: "teal_wrap_sash", 12: "teal_wrap_sash", 13: "teal_wrap_sash", 14: "indigo_trousers", 15: "indigo_trousers"}
OWNER_CODE = {"transparent":0,"outline":1,"hair":2,"skin":3,"orange_top":4,"teal_wrap_sash":5,"indigo_trousers":6}
ROUTES = {
    "hybrid_cleanup_primary_im_lanczos3_v01": {"route_id":"im_lanczos3", "sha256":"933caee8829970d0f8877712396b19b57e5843ef73481aceb047cf338cde72be", "alpha_threshold":128, "patches":[(30,12,1,"eye_outline"),(31,12,5,"eye_skin_boundary"),(25,18,1,"neck_outline"),(39,27,12,"guard_wrap_boundary"),(18,38,12,"sash_knot_boundary")]},
    "hybrid_cleanup_challenger_im_mitchell_netravali_v01": {"route_id":"im_mitchell_netravali", "sha256":"ee524888bd0be4e146a3236a9480565772b8fa8e752818bf2c9717bf702b17b5", "alpha_threshold":128, "patches":[(30,12,1,"eye_outline"),(31,12,5,"eye_skin_boundary"),(25,18,1,"neck_outline"),(39,27,12,"guard_wrap_boundary"),(18,38,12,"sash_knot_boundary"),(42,40,13,"sash_tail_highlight")]},
    "hybrid_cleanup_control_im_catmull_rom_v01": {"route_id":"im_catmull_rom", "sha256":"169426ebbf40eb01631154610cd73fff959afde8540dfa5943c3528225b20cd5", "alpha_threshold":128, "patches":[(30,12,1,"eye_outline"),(31,12,5,"eye_skin_boundary"),(25,18,1,"neck_outline")]}
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def nearest(rgb): return min(range(1,16), key=lambda i: sum((rgb[c]-PALETTE[i][c])**2 for c in range(3)))
def unpremultiply(rgb, a): return tuple(min(255, int(rgb[c]*255/a)) for c in range(3)) if a else (0,0,0)
def palette_bytes(): return sum((list(c) for c in PALETTE), []) + [0,0,0]*240

def make_grid(src, threshold, patches):
    grid=[]; actions=[]
    for pos,(r,g,b,a) in enumerate(src.getdata()):
        x, y = pos % W, pos // W
        before=0
        if a >= threshold:
            before=nearest(unpremultiply((r,g,b),a))
        grid.append(before)
        if a and a < threshold: actions.append({"kind":"matte_drop","x":x,"y":y,"before_alpha":a,"after":0})
    for x,y,idx,reason in patches:
        if 0 <= x < W and 0 <= y < H:
            pos=y*W+x; before=grid[pos]; grid[pos]=idx
            actions.append({"kind":"native_pixel_patch","x":x,"y":y,"before":before,"after":idx,"reason":reason})
    return grid, actions

def evidence(im, out):
    out.mkdir(parents=True, exist_ok=True); rgba=im.convert("RGBA")
    im.resize((112,160),Image.Resampling.NEAREST).save(out/"preview_nearest_2x.png")
    im.resize((168,240),Image.Resampling.NEAREST).save(out/"preview_nearest_3x.png")
    im.resize((448,640),Image.Resampling.NEAREST).save(out/"preview_nearest_8x.png")
    rgba.getchannel("A").point(lambda p:255 if p else 0).save(out/"silhouette_binary.png")
    for name, rgb in (("light",(238,238,230)),("dark",(28,30,38)),("chroma",(238,0,238))):
        bg=Image.new("RGBA",(W,H),rgb+(255,)); bg.alpha_composite(rgba); bg.convert("RGB").save(out/f"background_{name}.png")
    scene=Image.new("RGBA",(320,224),(68,102,102,255)); ImageDraw.Draw(scene).rectangle((0,168,319,223),fill=(34,34,68,255)); scene.alpha_composite(rgba,(132,88)); scene.convert("RGB").save(out/"composition_320x224.png")
    for name, box in {"head_face":(8,0,48,24),"shoulders_guard":(4,14,52,36),"waist_hip":(8,28,50,50),"knees":(4,48,52,68),"feet_ground":(0,66,56,80)}.items():
        rgba.crop(box).resize(((box[2]-box[0])*8,(box[3]-box[1])*8),Image.Resampling.NEAREST).save(out/f"crop_{name}.png")
    # Diagnostic contour/material views, intentionally derived from the candidate.
    contour=Image.new("RGBA",(W,H),(0,0,0,0)); pix=im.load(); cp=contour.load()
    for y in range(H):
        for x in range(W):
            v=pix[x,y]
            if v and (x==0 or y==0 or x==W-1 or y==H-1 or pix[x-1,y]!=v or pix[x+1,y]!=v or pix[x,y-1]!=v or pix[x,y+1]!=v): cp[x,y]=(255,255,255,255)
    contour.resize((448,640),Image.Resampling.NEAREST).save(out/"contour_overlay.png")
    role=Image.new("P",(W,H),0); role.putpalette(palette_bytes()); role.putdata([min(v,15) for v in im.getdata()]); role.save(out/"palette_role_map.png",bits=4,transparency=0)
    derived=Image.new("P",(W,H),0); derived.putpalette(palette_bytes()); derived.putdata([OWNER_CODE.get(OWNER.get(v,"transparent"),0) for v in im.getdata()]); derived.save(out/"derived_diagnostic_palette_owner_map.png",bits=4,transparency=0)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--lab-root",type=Path,required=True); args=ap.parse_args(); lab=args.lab_root.resolve(); rows=[]
    for asset, cfg in ROUTES.items():
        start=time.perf_counter(); src_path=lab/"route_reports"/cfg["route_id"]/"raw_rgba_56x80.png"
        if sha(src_path)!=cfg["sha256"]: raise SystemExit(f"source hash mismatch: {cfg['route_id']}")
        with Image.open(src_path) as raw: src=raw.convert("RGBA")
        grid, actions=make_grid(src,cfg["alpha_threshold"],cfg["patches"])
        out=lab/"hybrid_cleanup_shootout"/asset; out.mkdir(parents=True,exist_ok=True); png=out/(asset+".png")
        im=Image.new("P",(W,H),0); im.putpalette(palette_bytes()); im.putdata(grid); im.save(png,"PNG",bits=4,transparency=0); evidence(im,out)
        changed=sum(1 for a in actions if a["kind"]=="native_pixel_patch"); dropped=sum(1 for a in actions if a["kind"]=="matte_drop")
        report={"schema_version":"hybrid_cleanup_candidate.v1","asset_id":asset,"status":"hybrid_cleanup_candidate","route_id":cfg["route_id"],"source_raw":{"path":str(src_path.relative_to(lab)),"sha256":sha(src_path),"pixels_may_survive":True},"target":"56x80","method":"mechanical_palette_remap_with_minimal_native_patches","native_cleanup":"incomplete","material_topology":"not_run","semantic_map":"derived_diagnostic_not_independent","alpha_policy":"binary_index0; source pixels below threshold removed; transparent RGB zero","alpha_threshold":cfg["alpha_threshold"],"palette":{"visible_colors":len(set(grid)-{0}),"rgb333":True,"roles":dict(enumerate(ROLES))},"native_pixel_patch_count":changed,"matte_drop_count":dropped,"action_log":"cleanup_actions.json","claim_ceiling":"hybrid_cleanup_candidate","blind_pixel_promotion":False,"human_approval":"pending"}
        (out/"cleanup_actions.json").write_text(json.dumps({"schema_version":"hybrid_cleanup_action_log.v1","asset_id":asset,"source_pixels_may_survive":True,"actions":actions,"patches":cfg["patches"],"elapsed_seconds":round(time.perf_counter()-start,6)},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        report["output"]={"path":str(png.relative_to(lab)),"sha256":sha(png)}; report["action_log_sha256"]=sha(out/"cleanup_actions.json"); report["evidence"]={"nearest_2x":str((out/"preview_nearest_2x.png").relative_to(lab)),"nearest_3x":str((out/"preview_nearest_3x.png").relative_to(lab)),"nearest_8x":str((out/"preview_nearest_8x.png").relative_to(lab)),"light":str((out/"background_light.png").relative_to(lab)),"dark":str((out/"background_dark.png").relative_to(lab)),"chroma":str((out/"background_chroma.png").relative_to(lab)),"composition":str((out/"composition_320x224.png").relative_to(lab))}; (out/"hybrid_cleanup_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); rows.append(report)
    manifest={"schema_version":"hybrid_cleanup_shootout.v1","decision":"approve_hybrid_cleanup_shootout","scale":"56x80","primary_route":"im_lanczos3","primary_sha256":ROUTES[next(k for k in ROUTES if "primary" in k)]["sha256"],"challenger_route":"im_mitchell_netravali","challenger_sha256":ROUTES[next(k for k in ROUTES if "challenger" in k)]["sha256"],"control_route":"im_catmull_rom","control_sha256":ROUTES[next(k for k in ROUTES if "control" in k)]["sha256"],"selected_base_pixels_may_survive":True,"blind_pixel_promotion":False,"res_promotion":False,"normal_production_paused":True,"candidates":rows,"human_gate_status":"pending_human_decision","claim_ceiling":"hybrid_cleanup_candidate"}
    (lab/"hybrid_cleanup_shootout_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); print(json.dumps({"status":"completed","candidates":len(rows),"claim_ceiling":manifest["claim_ceiling"]},ensure_ascii=False))
if __name__=="__main__": main()
