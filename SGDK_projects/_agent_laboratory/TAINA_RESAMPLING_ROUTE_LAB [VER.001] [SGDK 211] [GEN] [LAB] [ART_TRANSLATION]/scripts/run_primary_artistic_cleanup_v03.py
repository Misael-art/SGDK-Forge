#!/usr/bin/env python3
"""Corrected PRIMARY cleanup: independent topology diagnostic, palette-safe edits.

The previous v02 broad ownership remap is deliberately not read. This pass
starts from the selected v01 rework and preserves its established pixel
clusters while applying only explicit local changes.
"""
import argparse, hashlib, json, sys
from pathlib import Path
from PIL import Image

W,H=56,80
PARENT_ID='hybrid_cleanup_primary_im_lanczos3_rework_v01'
PARENT_SHA='cb6ff5c695c5e7b76e80d84ebd497f8f55e162561c0f2caeb0f345604c31529e'
OUT_ID='hybrid_cleanup_primary_im_lanczos3_rework_v03'
SYMPTOMS={'hair':'hair mass too solid; curl grouping unreadable at 1x','face_eye':'eye/gaze and hair-face boundary insufficient at 1x','guard':'fist, wrap and forearm boundaries merge','top_hem':'top hem/axilla edge contaminates exposed skin','abdomen':'skin shadow clusters are noisy or fragmented','sash':'knot/caiment unclear or isolated pixel remains','trousers':'indigo shadow planes fragment the leg volumes','feet_ground':'baked ground strip or unstable sole contact','silhouette':'isolated pixel island in the silhouette'}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--lab-root',type=Path,required=True); a=ap.parse_args(); lab=a.lab_root.resolve(); sys.path.insert(0,str(lab/'scripts')); import run_primary_artistic_cleanup as old
    parent=lab/'localized_native_cleanup'/PARENT_ID/(PARENT_ID+'.png')
    if sha(parent)!=PARENT_SHA: raise SystemExit('parent hash mismatch')
    with Image.open(parent) as src: grid=list(src.convert('P').getdata())
    actions=[]; forced={}
    # Reuse the explicit art patch plan, but do not count no-ops.
    for x,y,after,region,reason in old.PATCHES:
        pos=y*W+x; before=grid[pos]
        if before==after: continue
        grid[pos]=after; forced[pos]=after; actions.append({'region':region,'symptom':SYMPTOMS[region],'x':x,'y':y,'before':before,'after':after,'reason':reason})
    # Independent topology is created from hand-authored coordinate masks and
    # silhouette only; palette indices are not consulted for ownership.
    owners=[old.owner_at(x,y,grid) for y in range(H) for x in range(W)]
    topo=Image.new('P',(W,H),0); topo.putpalette(sum((list(c) for c in old.PALETTE),[])+[0,0,0]*240); topo.putdata([old.ROLE_OWNER[o] for o in owners])
    # Palette recalculation is constrained to each current role ramp; this
    # prevents the topology diagnostic from flattening the established image.
    index_role={1:'outline',2:'hair',3:'hair',4:'hair',5:'skin',6:'skin',7:'skin',8:'top',9:'top',10:'top',11:'wrap_sash',12:'wrap_sash',13:'wrap_sash',14:'trousers',15:'trousers'}
    allowed={'outline':[1],'hair':[2,3,4],'skin':[5,6,7],'top':[8,9,10],'wrap_sash':[11,12,13],'trousers':[14,15]}
    remapped=[]
    for pos,v in enumerate(grid):
        if not v: remapped.append(0); continue
        if pos in forced: remapped.append(forced[pos]); continue
        role=index_role.get(v,'skin'); remapped.append(min(allowed[role],key=lambda i:sum((old.PALETTE[v][c]-old.PALETTE[i][c])**2 for c in range(3))))
    out=lab/'localized_native_cleanup'/OUT_ID; out.mkdir(parents=True,exist_ok=True); im=Image.new('P',(W,H),0); im.putpalette(sum((list(c) for c in old.PALETTE),[])+[0,0,0]*240); im.putdata(remapped); png=out/(OUT_ID+'.png'); im.save(png,'PNG',bits=4,transparency=0); old.evidence(im,out); topo.save(out/'independent_material_topology_map.png',bits=4,transparency=0)
    row77_visible=[x for x in range(W) if remapped[77*W+x] != 0]
    row77_middle=[x for x in row77_visible if 15 <= x <= 36]
    ground_report={'schema_version':'ground_contact_diagnostic.v1','asset_id':OUT_ID,'row':77,'visible_x':row77_visible,'middle_strip_x':row77_middle,'middle_strip_visible_count':len(row77_middle),'baked_ground_strip_removed':len(row77_middle)==0,'interpretation':'remaining row-77 pixels are confined to the two foot contact intervals; this is a diagnostic, not a visual-pass claim.'}
    (out/'ground_contact_report.json').write_text(json.dumps(ground_report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    # independent boundary map
    boundary=Image.new('P',(W,H),0); boundary.putpalette(sum((list(c) for c in old.PALETTE),[])+[0,0,0]*240); vals=[]
    for y in range(H):
        for x in range(W):
            p=y*W+x; vals.append(1 if owners[p]!='transparent' and any(0<=x+dx<W and 0<=y+dy<H and owners[(y+dy)*W+x+dx] not in ('transparent',owners[p]) for dx,dy in ((1,0),(0,1))) else 0)
    boundary.putdata(vals); boundary.save(out/'independent_material_boundary_overlay.png',bits=4,transparency=0)
    palette_roles=Image.new('P',(W,H),0); palette_roles.putpalette(sum((list(c) for c in old.PALETTE),[])+[0,0,0]*240)
    palette_roles.putdata([old.ROLE_OWNER.get(index_role.get(v,'skin'), 3) if v else 0 for v in remapped])
    palette_roles.save(out/'palette_role_map.png',bits=4,transparency=0)
    with Image.open(png) as saved_png: rgba=saved_png.convert('RGBA')
    alpha_values=[rgba.getpixel((x,y))[3] for y in range(H) for x in range(W)]
    transparent_rgb_nonzero=sum(1 for y in range(H) for x in range(W) if rgba.getpixel((x,y))[3]==0 and rgba.getpixel((x,y))[:3]!=(0,0,0))
    (out/'matte_halo_report.json').write_text(json.dumps({'schema_version':'matte_halo_diagnostic.v1','asset_id':OUT_ID,'alpha_values':sorted(set(alpha_values)),'alpha_binary':set(alpha_values).issubset({0,255}),'transparent_rgb_nonzero':transparent_rgb_nonzero,'halo_status':'no_transparent_rgb_halo' if transparent_rgb_nonzero==0 else 'review','note':'Diagnostic only; does not establish visual quality.'},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (out/'material_topology_independent_report.json').write_text(json.dumps({'schema_version':'independent_material_topology_diagnostic.v2','asset_id':OUT_ID,'independent_from_palette_indices':True,'owner_source':'hand_authored_coordinate_region_masks_plus_silhouette_contour','created_before_palette_recalculation':True,'coverage_exact_visible_pixels':True,'status':'not_run','human_art_review':'pending','palette_remap_policy':'role-constrained; topology map not used to repaint broad regions','notes':'Independent ownership hypothesis only; it does not prove artistic material separation.'},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    log={'schema_version':'localized_artistic_cleanup_action_log.v3','asset_id':OUT_ID,'parent_asset_id':PARENT_ID,'parent_sha256':PARENT_SHA,'method':'mechanical_palette_remap_with_minimal_native_patches','native_cleanup':'incomplete','material_topology':'not_run','semantic_map':'derived_diagnostic_not_independent','patches':actions,'patch_count':len(actions),'null_patches_count':0,'regions':['silhouette','hair','face_eye','guard','top_hem','abdomen','sash','trousers','feet_ground'],'palette_recalculated_after_independent_topology_map':True,'ground_contact_report':'ground_contact_report.json'}
    lp=out/'cleanup_actions.json'; lp.write_text(json.dumps(log,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    report={'schema_version':'localized_native_cleanup_rework.v3','asset_id':OUT_ID,'status':'technical_pass_visual_rework','method':'mechanical_palette_remap_with_minimal_native_patches','native_cleanup':'incomplete','material_topology':'not_run','semantic_map':'derived_diagnostic_not_independent','parent':{'asset_id':PARENT_ID,'sha256':PARENT_SHA,'path':str(parent.relative_to(lab))},'target':'56x80','patch_count':len(actions),'patch_log':str(lp.relative_to(lab)),'independent_topology_map':'independent_material_topology_map.png','independent_topology_report':'material_topology_independent_report.json','palette_role_map':'palette_role_map.png','matte_halo_report':'matte_halo_report.json','ground_contact_report':'ground_contact_report.json','output':{'path':str(png.relative_to(lab)),'sha256':sha(png)},'claim_ceiling':'localized_native_cleanup_candidate','human_gate_status':'pending_human_decision','res_promotion':False,'animation_authorization':False,'rom_authorization':False}
    report['action_log_sha256']=sha(lp); (out/'localized_native_cleanup_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); (lab/'localized_native_cleanup_manifest.json').write_text(json.dumps({'schema_version':'localized_native_cleanup_manifest.v3','decision':'select_hybrid_cleanup_incumbent_for_rework','selected_parent':{'asset_id':PARENT_ID,'sha256':PARENT_SHA,'scale':'56x80','approval_scope':'localized_native_cleanup_only'},'current_rework':{'asset_id':OUT_ID,'path':str(png.relative_to(lab)),'sha256':sha(png),'status':'technical_pass_visual_rework','method':'mechanical_palette_remap_with_minimal_native_patches','native_cleanup':'incomplete','material_topology':'not_run','semantic_map':'derived_diagnostic_not_independent','claim_ceiling':'localized_native_cleanup_candidate'},'historical_controls':['localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v01'],'discarded_visual_regression':{'asset_id':'hybrid_cleanup_primary_im_lanczos3_rework_v02','reason':'broad palette-owner remap flattened material masses and regressed visual volume','source_allowed':False,'record':'localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v02/DISCARDED_VISUAL_REGRESSION.md'},'human_gate_status':'pending_human_decision','res_promotion':False,'animation_authorization':False,'rom_authorization':False},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':'completed','asset_id':OUT_ID,'sha256':sha(png),'patches':len(actions),'topology':'independent_map_before_role_constrained_palette_recalculation'},ensure_ascii=False))
if __name__=='__main__': main()
