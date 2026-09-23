#!/usr/bin/env python3
"""Stage-2 manual semantic palette probes for selected geometry routes."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw

PALETTE = [(0,0,0),(34,0,0),(34,0,34),(68,34,68),(102,68,34),(136,68,34),(170,102,34),(204,136,68),(204,68,0),(238,102,0),(238,136,68),(0,68,68),(0,136,136),(0,170,170),(0,0,68),(34,34,102)]
ROLES = ["transparent0","outline_deep_shadow","hair_deep","hair_base","hair_highlight","skin_shadow","skin_base","skin_highlight","top_shadow","top_base","top_highlight","teal_shadow","teal_base","teal_highlight","indigo_shadow","indigo_base"]
MATERIAL = {1:"outline",2:"hair",3:"hair",4:"hair",5:"hair",6:"skin",7:"skin",8:"skin",9:"orange_top",10:"orange_top",11:"orange_top",12:"teal_cloth",13:"teal_cloth",14:"teal_cloth",15:"indigo_trousers",16:"indigo_trousers"}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def nearest(rgb): return min(range(1,16), key=lambda i: sum((rgb[c]-PALETTE[i][c])**2 for c in range(3)))
def unpremultiply(px, a): return tuple(min(255, int(px[c]*255/a)) for c in range(3)) if a else (0,0,0)
def save_probe(src, out):
    src = src.convert("RGBA"); vals=[]; owners=[]; partial=0
    for r,g,b,a in src.getdata():
        if a == 0: vals.append(0); owners.append(0); continue
        if a < 255: partial += 1
        idx=nearest(unpremultiply((r,g,b),a)); vals.append(idx); owners.append({1:1,2:2,3:2,4:2,5:2,6:3,7:3,8:3,9:4,10:4,11:4,12:5,13:5,14:5,15:6}.get(idx,0))
    im=Image.new("P",(56,80),0); flat=sum((list(v) for v in PALETTE),[])+[0,0,0]*240; im.putpalette(flat); im.putdata(vals); im.save(out,"PNG",bits=4,transparency=0)
    return im, owners, partial
def evidence(im, directory):
    directory.mkdir(parents=True,exist_ok=True); rgba=im.convert("RGBA");
    for name,rgb in (("light",(238,238,230)),("dark",(28,30,38)),("chroma",(238,0,238))):
        bg=Image.new("RGBA",im.size,rgb+(255,)); bg.alpha_composite(rgba); bg.convert("RGB").save(directory/f"background_{name}.png")
    im.resize((448,640),Image.Resampling.NEAREST).save(directory/"preview_nearest_8x.png")
    rgba.getchannel("A").point(lambda p:255 if p else 0).save(directory/"silhouette_binary.png")
    scene=Image.new("RGBA",(320,224),(68,102,102,255)); ImageDraw.Draw(scene).rectangle((0,168,319,223),fill=(34,34,68,255)); scene.alpha_composite(rgba,(132,88)); scene.convert("RGB").save(directory/"composition_320x224.png")
    for name,box in {"head_face":(8,0,48,24),"shoulders_guard":(4,14,52,36),"waist_hip":(8,28,50,50),"knees":(4,48,52,68),"feet_ground":(0,66,56,80)}.items(): rgba.crop(box).resize(((box[2]-box[0])*8,(box[3]-box[1])*8),Image.Resampling.NEAREST).save(directory/f"crop_{name}.png")
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--lab-root",type=Path,required=True); args=ap.parse_args(); lab=args.lab_root.resolve(); routes=["im_nearest","im_box_area","pil_lanczos","cv_area"]; reports=[]
    for rid in routes:
        inp=lab/"route_reports"/rid/"raw_rgba_56x80.png"; out=lab/"palette_probe_reports"/rid; out.mkdir(parents=True,exist_ok=True)
        if not inp.is_file(): reports.append({"route_id":rid,"status":"skipped","warning":"stage-1 route did not produce a raw probe"}); continue
        with Image.open(inp) as src: probe, owners, partial=save_probe(src,out/"technical_palette_probe_56x80.png")
        evidence(probe, out); owner_im=Image.new("P",(56,80),0); owner_im.putpalette(sum((list(v) for v in PALETTE),[])+[0,0,0]*240); owner_im.putdata(owners); owner_im.save(out/"material_region_map.png",bits=4,transparency=0)
        boundary=Image.new("P",(56,80),0); boundary.putpalette(sum((list(v) for v in PALETTE),[])+[0,0,0]*240); boundary.putdata([1 if owners[p] and ((p%56<55 and owners[p+1] not in (0,owners[p])) or (p//56<79 and owners[p+56] not in (0,owners[p]))) else (2 if owners[p] else 0) for p in range(4480)]); boundary.save(out/"material_boundary_overlay.png",bits=4,transparency=0)
        report={"schema_version":"technical_palette_probe.v1","route_id":rid,"status":"technical_palette_probe","input_raw":{"path":str(inp.relative_to(lab)),"sha256":sha(inp)},"output":{"path":str((out/"technical_palette_probe_56x80.png").relative_to(lab)),"sha256":sha(out/"technical_palette_probe_56x80.png")},"target":"56x80","palette":{"visible_colors":15,"rgb333":True,"roles":dict(enumerate(ROLES))},"alpha_policy":"index0_from_raw_alpha_zero; silhouette_support_preserved_for_all_alpha_nonzero","partial_alpha_input_pixels":partial,"material_region_map":{"path":str((out/"material_region_map.png").relative_to(lab)),"sha256":sha(out/"material_region_map.png"),"status":"diagnostic_owner_map"},"material_boundary_overlay":{"path":str((out/"material_boundary_overlay.png").relative_to(lab)),"sha256":sha(out/"material_boundary_overlay.png")},"matte_halo":{"status":"diagnostic","partial_alpha_input_pixels":partial,"halo_cleaning":"not_applied"},"claim_ceiling":"technical_palette_probe","not_native_candidate":True}
        (out/"palette_probe_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); reports.append(report)
    (lab/"palette_probe_matrix.json").write_text(json.dumps({"schema_version":"palette_probe_matrix.v1","routes":reports,"selected_count":sum(r.get("status")=="technical_palette_probe" for r in reports),"max_survivors":4,"no_native_candidate":True},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"selected":sum(r.get("status")=="technical_palette_probe" for r in reports),"skipped":sum(r.get("status")=="skipped" for r in reports)},ensure_ascii=False))
if __name__=="__main__": main()
