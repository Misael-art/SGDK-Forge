#!/usr/bin/env python3
"""Localized artistic cleanup for the selected PRIMARY, lab-only.

This is a native-grid patch pass over the selected hybrid incumbent. It does
not regenerate the pose and it never uses the old v01-v04 assets as input.
Material ownership is authored from coordinate masks before palette remap;
it is deliberately reported as not_run until human/artistic review.
"""
import argparse, hashlib, json, sys
from pathlib import Path
from PIL import Image, ImageDraw

W,H=56,80
PARENT_ID="hybrid_cleanup_primary_im_lanczos3_rework_v01"
PARENT_SHA="cb6ff5c695c5e7b76e80d84ebd497f8f55e162561c0f2caeb0f345604c31529e"
OUT_ID="hybrid_cleanup_primary_im_lanczos3_rework_v02"
PALETTE=[(0,0,0),(34,0,0),(34,0,34),(68,34,68),(102,68,34),(136,68,34),(170,102,34),(204,136,68),(204,68,0),(238,102,0),(238,136,68),(0,68,68),(0,136,136),(0,170,170),(0,0,68),(34,34,102)]
ROLE_INDEX={"transparent":0,"outline":1,"hair_deep":2,"hair_base":3,"hair_highlight":4,"skin_shadow":5,"skin_base":6,"skin_highlight":7,"top_shadow":8,"top_base":9,"top_highlight":10,"wrap_shadow":11,"wrap_base":12,"wrap_highlight":13,"trouser_shadow":14,"trouser_base":15}
ROLE_OWNER={"transparent":0,"outline":1,"hair":2,"skin":3,"top":4,"wrap_sash":5,"trousers":6,"feet":3}
ALLOWED={"outline":[1],"hair":[2,3,4],"skin":[5,6,7],"top":[8,9,10],"wrap_sash":[11,12,13],"trousers":[14,15],"feet":[5,6,7]}

# Coordinate patches are intentional art decisions. Desired values are palette
# roles only as a temporary native-grid notation; they are remapped after the
# independent topology map is created. Null/no-op patches are not logged.
PATCHES=[]
for x in range(15,37): PATCHES.append((x,77,0,"feet_ground","remove_remaining_baked_ground_shadow_between_feet"))
PATCHES += [
    # Hair: five separated curl groups instead of one solid mass.
    (20,3,4,"hair","curl_group_1_highlight"),(21,3,4,"hair","curl_group_1_highlight"),(20,4,3,"hair","curl_group_1_base"),
    (25,6,4,"hair","curl_group_2_highlight"),(26,6,4,"hair","curl_group_2_highlight"),(25,7,3,"hair","curl_group_2_base"),
    (18,9,4,"hair","curl_group_3_highlight"),(19,9,4,"hair","curl_group_3_highlight"),
    (24,11,4,"hair","curl_group_4_highlight"),(25,11,3,"hair","curl_group_4_base"),
    (28,5,4,"hair","curl_group_5_highlight"),(29,5,4,"hair","curl_group_5_highlight"),
    # Face and gaze: hard eye/brow/nose separation at native scale.
    (29,11,1,"face_eye","eye_brow_contour"),(30,12,1,"face_eye","eye_pupil_cluster"),(31,12,5,"face_eye","eye_skin_boundary"),
    (30,13,5,"face_eye","nose_bridge_plane"),(31,13,1,"face_eye","face_side_contour"),(31,14,1,"face_eye","hair_face_separation"),
    # Wrists and guards: explicit wrap/skin/outline boundaries.
    (20,22,1,"guard","left_wrap_outer_contour"),(21,22,12,"guard","left_wrap_base"),(21,23,12,"guard","left_wrap_base"),(20,24,1,"guard","left_fist_contour"),
    (36,21,1,"guard","right_wrap_outer_contour"),(37,21,12,"guard","right_wrap_base"),(38,22,1,"guard","right_fist_contour"),(39,23,12,"guard","right_wrap_base"),(40,24,1,"guard","right_fist_contour"),(39,25,12,"guard","right_wrap_base"),
    # Top hem, axilla and exposed abdomen.
    (22,27,1,"top_hem","left_hem_contour"),(23,27,8,"top_hem","left_hem_shadow"),(24,27,8,"top_hem","hem_shadow"),(25,27,9,"top_hem","hem_base"),(26,27,9,"top_hem","hem_base"),(27,27,9,"top_hem","hem_base"),(28,27,9,"top_hem","hem_base"),(29,27,8,"top_hem","right_hem_shadow"),(30,27,1,"top_hem","right_hem_contour"),
    (22,28,5,"abdomen","left_axilla_skin_shadow"),(30,28,5,"abdomen","right_axilla_skin_shadow"),(25,30,6,"abdomen","consolidate_skin_base"),(27,31,6,"abdomen","consolidate_skin_base"),(29,32,6,"abdomen","consolidate_skin_base"),
    # Sash knot/ca thement and isolated-pixel removal.
    (18,38,12,"sash","knot_base"),(19,38,1,"sash","knot_contour"),(20,38,12,"sash","knot_base"),(19,39,12,"sash","knot_base"),(20,39,1,"sash","knot_contour"),(42,41,0,"sash","remove_orphan_sash_edge_pixel"),
    # Trouser clusters: consolidate indigo planes at inner knees.
    (24,43,14,"trousers","left_trouser_shadow_cluster"),(25,43,14,"trousers","left_trouser_shadow_cluster"),(34,44,14,"trousers","right_trouser_shadow_cluster"),(35,44,14,"trousers","right_trouser_shadow_cluster"),(27,52,15,"trousers","left_trouser_base_cluster"),(28,52,15,"trousers","left_trouser_base_cluster"),
    # Feet: redraw toe/sole edge without recreating a ground shadow.
    (9,77,1,"feet_ground","left_toe_contour"),(14,77,1,"feet_ground","left_toe_contour"),(37,77,1,"feet_ground","right_toe_contour"),(47,77,1,"feet_ground","right_toe_contour"),
    (12,78,6,"feet_ground","left_sole_contact"),(13,78,6,"feet_ground","left_sole_contact"),(40,78,6,"feet_ground","right_sole_contact"),(41,78,6,"feet_ground","right_sole_contact"),(42,78,5,"feet_ground","right_sole_shadow"),
]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def nearest(rgb, allowed): return min(allowed,key=lambda i:sum((rgb[c]-PALETTE[i][c])**2 for c in range(3)))
def owner_at(x,y,grid):
    if grid[y*W+x]==0: return "transparent"
    # Silhouette contour owns the outermost pixel independently of palette.
    for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
        xx,yy=x+dx,y+dy
        if xx<0 or yy<0 or xx>=W or yy>=H or grid[yy*W+xx]==0: return "outline"
    # Hand-authored region masks; these never inspect the source palette index.
    if y>=68: return "feet"
    if y>=41: return "trousers"
    if (18<=x<=24 and 18<=y<=28) or (35<=x<=42 and 19<=y<=31) or (18<=x<=24 and 34<=y<=45) or (34<=x<=45 and 34<=y<=49): return "wrap_sash"
    if 23<=x<=33 and 28<=y<=40: return "skin"
    if 20<=x<=36 and 18<=y<=27: return "top"
    if (14<=x<=22 and 18<=y<=33) or (34<=x<=41 and 19<=y<=33): return "skin"
    if 8<=y<=19 and 23<=x<=34: return "skin"
    if y<=18 and x<=31: return "hair"
    # Conservative hand-authored fallback for enclosed pixels.
    return "skin" if y<41 else "trousers"

def evidence(im,out):
    out.mkdir(parents=True,exist_ok=True); rgba=im.convert("RGBA")
    for scale,name in ((2,"2x"),(3,"3x"),(8,"8x")): im.resize((W*scale,H*scale),Image.Resampling.NEAREST).save(out/f"preview_nearest_{name}.png")
    rgba.getchannel("A").point(lambda p:255 if p else 0).save(out/"silhouette_binary.png")
    for name,rgb in (("light",(238,238,230)),("dark",(28,30,38)),("chroma",(238,0,238))):
        bg=Image.new("RGBA",(W,H),rgb+(255,)); bg.alpha_composite(rgba); bg.convert("RGB").save(out/f"background_{name}.png")
    scene=Image.new("RGBA",(320,224),(68,102,102,255)); ImageDraw.Draw(scene).rectangle((0,168,319,223),fill=(34,34,68,255)); scene.alpha_composite(rgba,(132,88)); scene.convert("RGB").save(out/"composition_320x224.png")
    for name,box in {"head_face":(8,0,48,24),"shoulders_guard":(4,14,52,36),"waist_hip":(8,28,50,50),"knees":(4,48,52,68),"feet_ground":(0,66,56,80)}.items(): rgba.crop(box).resize(((box[2]-box[0])*8,(box[3]-box[1])*8),Image.Resampling.NEAREST).save(out/f"crop_{name}.png")
    contour=Image.new("P",(W,H),0); contour.putpalette(sum((list(c) for c in PALETTE),[])+[0,0,0]*240); cp=[]; pix=im.load()
    for y in range(H):
        for x in range(W): cp.append(1 if pix[x,y] and any(xx<0 or yy<0 or xx>=W or yy>=H or pix[xx,yy]==0 for xx,yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1))) else 0)
    contour.putdata(cp); contour.resize((W*8,H*8),Image.Resampling.NEAREST).save(out/"contour_overlay.png")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--lab-root',type=Path,required=True); a=ap.parse_args(); lab=a.lab_root.resolve(); parent=lab/'localized_native_cleanup'/PARENT_ID/(PARENT_ID+'.png')
    if sha(parent)!=PARENT_SHA: raise SystemExit('parent hash mismatch')
    with Image.open(parent) as src: parent_grid=list(src.convert('P').getdata()); parent_rgb=src.convert('RGB')
    grid=parent_grid[:]; forced={}; actions=[]
    for x,y,after,region,reason in PATCHES:
        pos=y*W+x; before=grid[pos]
        if before==after: continue
        grid[pos]=after; forced[pos]=after; actions.append({'region':region,'x':x,'y':y,'before':before,'after':after,'reason':reason})
    # Remove any remaining non-foot one-pixel islands as explicit cleanup actions.
    for y in range(1,H-1):
        for x in range(1,W-1):
            pos=y*W+x
            if grid[pos] and y<68 and all(grid[(y+dy)*W+x+dx]==0 for dx,dy in ((-1,0),(1,0),(0,-1),(0,1),(1,1),(-1,-1),(1,-1),(-1,1))):
                before=grid[pos]; grid[pos]=0; forced[pos]=0; actions.append({'region':'silhouette','x':x,'y':y,'before':before,'after':0,'reason':'remove_remaining_isolated_pixel_island'})
    owners=[owner_at(x,y,grid) for y in range(H) for x in range(W)]
    fallback=sum(1 for o in owners if o=='skin' and False)
    # Palette remap occurs only after independent owner map exists.
    remapped=[]
    for pos,v in enumerate(grid):
        if not v: remapped.append(0); continue
        x,y=pos%W,pos//W; owner=owners[pos]
        if pos in forced:
            after=forced[pos] if forced[pos]==0 else (1 if owner=='outline' else forced[pos])
        else:
            after=1 if owner=='outline' else nearest(PALETTE[v],ALLOWED[owner])
        remapped.append(after)
    out=lab/'localized_native_cleanup'/OUT_ID; out.mkdir(parents=True,exist_ok=True); im=Image.new('P',(W,H),0); im.putpalette(sum((list(c) for c in PALETTE),[])+[0,0,0]*240); im.putdata(remapped); png=out/(OUT_ID+'.png'); im.save(png,'PNG',bits=4,transparency=0); evidence(im,out)
    # Independent material topology diagnostic map: ownership came from masks,
    # never from the source or destination palette indices.
    topo=Image.new('P',(W,H),0); topo.putpalette(sum((list(c) for c in PALETTE),[])+[0,0,0]*240); topo.putdata([ROLE_OWNER[o] for o in owners]); topo.save(out/'independent_material_topology_map.png',bits=4,transparency=0)
    boundary=Image.new('P',(W,H),0); boundary.putpalette(sum((list(c) for c in PALETTE),[])+[0,0,0]*240); b=[]
    for y in range(H):
        for x in range(W):
            p=y*W+x; b.append(1 if owners[p]!='transparent' and any(0<=x+dx<W and 0<=y+dy<H and owners[(y+dy)*W+x+dx] not in ('transparent',owners[p]) for dx,dy in ((1,0),(0,1))) else 0)
    boundary.putdata(b); boundary.save(out/'independent_material_boundary_overlay.png',bits=4,transparency=0)
    (out/'material_topology_independent_report.json').write_text(json.dumps({'schema_version':'independent_material_topology_diagnostic.v1','asset_id':OUT_ID,'independent_from_palette_indices':True,'owner_source':'hand_authored_coordinate_region_masks_plus_silhouette_contour','coverage_exact_visible_pixels':True,'status':'not_run','human_art_review':'pending','fallback_assignments':fallback,'notes':'This map is an independent ownership hypothesis, not proof that materials are artistically correct.'},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    report={'schema_version':'localized_native_cleanup_rework.v2','asset_id':OUT_ID,'status':'technical_pass_visual_rework','method':'mechanical_palette_remap_with_minimal_native_patches','native_cleanup':'incomplete','material_topology':'not_run','semantic_map':'derived_diagnostic_not_independent','parent':{'asset_id':PARENT_ID,'sha256':PARENT_SHA,'path':str(parent.relative_to(lab))},'target':'56x80','regions':['silhouette','hair','face_eye','guard','top_hem','abdomen','sash','trousers','feet_ground'],'patch_count':len(actions),'patch_log':'cleanup_actions.json','independent_topology_map':'independent_material_topology_map.png','independent_topology_report':'material_topology_independent_report.json','output':{'path':str(png.relative_to(lab)),'sha256':sha(png)},'claim_ceiling':'localized_native_cleanup_candidate','human_gate_status':'pending_human_decision','res_promotion':False,'animation_authorization':False,'rom_authorization':False}
    (out/'cleanup_actions.json').write_text(json.dumps({'schema_version':'localized_artistic_cleanup_action_log.v2','asset_id':OUT_ID,'method':report['method'],'native_cleanup':report['native_cleanup'],'patches':actions,'null_patches_count':0,'palette_remap_after_topology_map':True},indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); report['action_log_sha256']=sha(out/'cleanup_actions.json'); (out/'localized_native_cleanup_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':'completed','asset_id':OUT_ID,'sha256':sha(png),'patches':len(actions),'topology':'independent_map_created_before_palette_remap'},ensure_ascii=False))
if __name__=='__main__': main()
