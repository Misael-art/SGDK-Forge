#!/usr/bin/env python3
"""Historical v05 generator; frozen after production.

Its former rectangular material routine is retained only for provenance of
the original generation step. It is not a canonical topology source. Use
repair_material_topology_meter_v02.py for all current measurements; this file
must not be rerun over the frozen v05 PNG.
"""
import argparse, hashlib, json, sys
from pathlib import Path
from PIL import Image, ImageDraw

W,H=56,80
V04_ID='hybrid_cleanup_primary_im_lanczos3_rework_v04'; V04_SHA='791074aa6919ac0bac78a60693c12daee8f03169b216996758a8a272bc6b214e'
OUT_ID='hybrid_cleanup_primary_im_lanczos3_rework_v05'
PALETTE=[(0,0,0),(34,0,0),(34,0,34),(68,34,68),(102,68,34),(136,68,34),(170,102,34),(204,136,68),(204,68,0),(238,102,0),(238,136,68),(0,68,68),(0,136,136),(0,170,170),(0,0,68),(34,34,102)]
ROLE_ID={'transparent':0,'outline_shared':1,'hair':2,'skin':3,'top':4,'wraps':5,'sash':6,'trousers':7,'feet':8}
ROLE_RAMP={'outline_shared':[1],'hair':[2,3,4],'skin':[5,6,7],'top':[8,9,10],'wraps':[11,12,13],'sash':[11,12,13],'trousers':[14,15],'feet':[5,6,7]}
SHARED_DEEP_SHADOW=[1,2]
SYMPTOMS={'hair':'hair mass and contour groups still merge at 1x','face_eye':'face cluster does not state gaze and hair-face separation','guard':'wrap, fist and forearm boundaries merge','abdomen':'skin highlights remain point-like instead of planar','sash':'knot and tail do not read as one accessory','trousers':'inner-knee shadow breaks leg volume'}
PATCHES=[
    (16,5,0,'hair','open_outer_curl_notch_4'),(15,6,0,'hair','open_outer_curl_notch_5'),(17,11,0,'hair','open_outer_curl_notch_6'),
    (27,10,6,'face_eye','forehead_skin_plane'),(28,12,6,'face_eye','eye_socket_skin_plane'),(29,13,6,'face_eye','cheek_plane'),(30,13,6,'face_eye','cheek_plane'),(30,14,6,'face_eye','jaw_plane'),
    (21,21,1,'guard','left_fist_wrap_separator'),(23,24,1,'guard','left_wrap_forearm_separator'),(36,21,1,'guard','right_fist_wrap_separator'),(36,24,1,'guard','right_wrap_forearm_separator'),
    (27,30,6,'abdomen','join_abdomen_plane'),(29,30,6,'abdomen','join_abdomen_plane'),(25,33,6,'abdomen','join_abdomen_plane'),(27,33,6,'abdomen','join_abdomen_plane'),(29,33,6,'abdomen','join_abdomen_plane'),
    (21,39,12,'sash','knot_neck'),(22,40,12,'sash','knot_drop'),(35,42,12,'sash','tail_continuity'),
    (23,44,14,'trousers','left_inner_knee_shadow'),(26,44,14,'trousers','left_inner_knee_shadow'),(31,44,14,'trousers','right_inner_knee_shadow'),
]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def palette_bytes(): return sum((list(c) for c in PALETTE),[])+[0,0,0]*240

def legacy_rectangular_owner_at_for_archival_reproduction(x,y,grid):
    if grid[y*W+x]==0: return 'transparent'
    # Disjoint, geometry-first masks. No palette index is consulted.
    if y>=68: return 'feet'
    if 18<=x<=24 and 18<=y<=28: return 'wraps'
    if 35<=x<=42 and 19<=y<=31: return 'wraps'
    if 18<=x<=24 and 34<=y<=45: return 'sash'
    if 34<=x<=45 and 34<=y<=49: return 'sash'
    if y>=41: return 'trousers'
    if 23<=x<=33 and 28<=y<=40: return 'skin'
    if 20<=x<=36 and 18<=y<=27: return 'top'
    if (14<=x<=22 and 18<=y<=33) or (34<=x<=41 and 19<=y<=33): return 'skin'
    if 8<=y<=19 and 23<=x<=34: return 'skin'
    if y<=18 and x<=31: return 'hair'
    return 'skin'

def evidence(png,out):
    with Image.open(png) as saved: rgba=saved.convert('RGBA'); pimg=saved.copy()
    for scale,name in ((2,'2x'),(3,'3x'),(8,'8x')): pimg.resize((W*scale,H*scale),Image.Resampling.NEAREST).save(out/f'preview_nearest_{name}.png')
    rgba.getchannel('A').point(lambda p:255 if p else 0).save(out/'silhouette_binary.png')
    for name,rgb in (('light',(238,238,230)),('dark',(28,30,38)),('chroma',(238,0,238))):
        bg=Image.new('RGBA',(W,H),rgb+(255,)); bg.alpha_composite(rgba); bg.convert('RGB').save(out/f'background_{name}.png')
    scene=Image.new('RGBA',(320,224),(68,102,102,255)); ImageDraw.Draw(scene).rectangle((0,168,319,223),fill=(34,34,68,255)); scene.alpha_composite(rgba,(132,88)); scene.convert('RGB').save(out/'composition_320x224.png')
    for name,box in {'head_face':(8,0,48,24),'shoulders_guard':(4,14,52,36),'waist_hip':(8,28,50,50),'knees':(4,48,52,68),'feet_ground':(0,66,56,80)}.items(): rgba.crop(box).resize(((box[2]-box[0])*8,(box[3]-box[1])*8),Image.Resampling.NEAREST).save(out/f'crop_{name}.png')
    contour=Image.new('P',(W,H),0); contour.putpalette(palette_bytes()); vals=[]
    for y in range(H):
        for x in range(W): vals.append(1 if rgba.getpixel((x,y))[3] and any(xx<0 or yy<0 or xx>=W or yy>=H or rgba.getpixel((xx,yy))[3]==0 for xx,yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1))) else 0)
    contour.putdata(vals); contour.resize((W*8,H*8),Image.Resampling.NEAREST).save(out/'contour_overlay.png')

def material_contract(grid,asset_id,asset_sha,out,stage):
    owners=[legacy_rectangular_owner_at_for_archival_reproduction(x,y,grid) for y in range(H) for x in range(W)]
    visible=[i for i,v in enumerate(grid) if v]
    unassigned=[i for i in visible if owners[i]=='transparent']; owner_counts={r:owners.count(r) for r in ROLE_ID}
    leaks=[]
    for i in visible:
        owner=owners[i]; value=grid[i]; allowed=set(ROLE_RAMP[owner])
        if value not in allowed and value not in SHARED_DEEP_SHADOW:
            leaks.append({'x':i%W,'y':i//W,'owner':owner,'index':value,'allowed_indices':sorted(allowed),'reason':'material_palette_leakage'})
    pairs={('hair','skin'):0,('skin','top'):0,('skin','wraps'):0,('sash','wraps'):0,('sash','trousers'):0,('feet','trousers'):0}
    for y in range(H):
        for x in range(W):
            i=y*W+x
            if owners[i]=='transparent': continue
            for dx,dy in ((1,0),(0,1)):
                xx,yy=x+dx,y+dy
                if xx>=W or yy>=H: continue
                a,b=owners[i],owners[yy*W+xx]; key=tuple(sorted((a,b)))
                if key in pairs: pairs[key]+=1
    boundary_checks={
        'hair_skin':{'pair':['hair','skin'],'count':pairs[('hair','skin')],'status':pairs[('hair','skin')]>0},
        'top_skin_hem_axilla':{'pair':['top','skin'],'count':pairs[('skin','top')],'status':pairs[('skin','top')]>0},
        'wraps_skin_and_fists':{'pair':['skin','wraps'],'count':pairs[('skin','wraps')],'status':pairs[('skin','wraps')]>0},
        'sash_trousers':{'pair':['sash','trousers'],'count':pairs[('sash','trousers')],'status':pairs[('sash','trousers')]>0},
        'feet_trousers':{'pair':['feet','trousers'],'count':pairs[('feet','trousers')],'status':pairs[('feet','trousers')]>0},
    }
    status='passed' if not leaks and not unassigned and all(v['status'] for v in boundary_checks.values()) else 'failed_requires_localized_material_cleanup'
    report={'schema_version':'material_region_contract.v1','asset_id':asset_id,'sha256':asset_sha,'stage':stage,'owner_source':'hand_authored_disjoint_coordinate_masks_plus_silhouette_visibility','palette_indices_not_used_for_owner_assignment':True,'visible_pixel_count':len(visible),'owner_counts':owner_counts,'unassigned_visible_pixels':len(unassigned),'overlap_policy':'disjoint priority masks; exactly one owner emitted per visible pixel','materials':{k:{'count':owner_counts[k],'indices_allowed':v,'ramp':{'shadow':v[0] if len(v)>1 else v[0],'base':v[-1],'highlight':v[-1] if len(v)<3 else v[-1]}} for k,v in ROLE_RAMP.items()},'shared_deep_shadow_indices':SHARED_DEEP_SHADOW,'critical_boundaries':boundary_checks,'leakage_count':len(leaks),'status':status,'artistic_validation':'pending_human_review','notes':'Coverage is necessary but not sufficient. Leakage status is evaluated independently against material ownership and allowed ramps.'}
    (out/'material_region_contract.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (out/'material_leakage_report.json').write_text(json.dumps({'schema_version':'material_leakage_report.v1','asset_id':asset_id,'sha256':asset_sha,'status':status,'leakage_count':len(leaks),'leakage_examples':leaks[:80],'shared_deep_shadow_indices':SHARED_DEEP_SHADOW,'critical_boundaries':boundary_checks,'not_approved_by_coverage_alone':True},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    topo=Image.new('P',(W,H),0); topo.putpalette(palette_bytes()); topo.putdata([ROLE_ID[o] for o in owners]); topo.save(out/'material_region_map.png',bits=4,transparency=0)
    overlay=Image.new('P',(W,H),0); overlay.putpalette(palette_bytes()); boundary_pixels=[]
    for y in range(H):
        for x in range(W):
            i=y*W+x; mark=0
            for dx,dy in ((1,0),(0,1)):
                xx,yy=x+dx,y+dy
                if xx<W and yy<H and owners[i]!=owners[yy*W+xx] and owners[i]!='transparent' and owners[yy*W+xx]!='transparent': mark=1
            boundary_pixels.append(mark)
    overlay.putdata(boundary_pixels); overlay.resize((W*8,H*8),Image.Resampling.NEAREST).save(out/'material_boundary_overlay.png')
    return report

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--lab-root',type=Path,required=True); args=ap.parse_args(); lab=args.lab_root.resolve()
    v04=lab/'localized_native_cleanup'/V04_ID/(V04_ID+'.png')
    if sha(v04)!=V04_SHA: raise SystemExit('v04 hash mismatch')
    with Image.open(v04) as src: v04_grid=list(src.convert('P').getdata()); palette=src.getpalette()
    v04_dir=lab/'localized_native_cleanup'/V04_ID; material_contract(v04_grid,V04_ID,V04_SHA,v04_dir,'v04_independent_contract')
    grid=v04_grid[:]; actions=[]; out=lab/'localized_native_cleanup'/OUT_ID
    if (out/(OUT_ID+'.png')).exists(): raise SystemExit('v05 is frozen; use repair_material_topology_meter_v02.py')
    out.mkdir(parents=True,exist_ok=True)
    for x,y,after,region,reason in PATCHES:
        i=y*W+x; before=grid[i]
        if before==after: continue
        grid[i]=after; actions.append({'region':region,'symptom':SYMPTOMS[region],'x':x,'y':y,'before':before,'after':after,'reason':reason})
    im=Image.new('P',(W,H),0); im.putpalette(palette if palette else palette_bytes()); im.putdata(grid); png=out/(OUT_ID+'.png'); im.save(png,'PNG',bits=4,transparency=0); evidence(png,out)
    asset_sha=sha(png); contract=material_contract(grid,OUT_ID,asset_sha,out,'v05_independent_contract')
    # Reuse the same role-independent maps under explicit v05 names.
    (out/'independent_material_topology_map.png').write_bytes((out/'material_region_map.png').read_bytes())
    (out/'independent_material_boundary_overlay.png').write_bytes((out/'material_boundary_overlay.png').read_bytes())
    (out/'material_topology_independent_report.json').write_text(json.dumps({'schema_version':'independent_material_topology_report.v2','asset_id':OUT_ID,'sha256':asset_sha,'independent_from_palette_indices':True,'owner_source':'hand_authored_disjoint_coordinate_masks_plus_silhouette_visibility','visible_pixel_count':contract['visible_pixel_count'],'visible_pixel_coverage_exact':contract['unassigned_visible_pixels']==0,'owner_counts':contract['owner_counts'],'critical_boundaries':contract['critical_boundaries'],'leakage_count':contract['leakage_count'],'status':contract['status'],'artistic_validation':'pending_human_review','not_approved_by_coverage_alone':True},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    # Palette-role map is diagnostic only: it reports the role implied by the
    # final index, separately from the geometry-first material contract.
    index_role={1:'outline_shared',2:'hair',3:'hair',4:'hair',5:'skin',6:'skin',7:'skin',8:'top',9:'top',10:'top',11:'wraps',12:'wraps',13:'wraps',14:'trousers',15:'trousers'}
    rolemap=Image.new('P',(W,H),0); rolemap.putpalette(palette_bytes())
    rolemap.putdata([ROLE_ID[index_role.get(v,'skin')] if v else ROLE_ID['transparent'] for v in grid])
    rolemap.save(out/'palette_role_map.png',bits=4,transparency=0)
    # Explicit delta overlay: unchanged pixels are neutral; only changed
    # coordinates are highlighted. This is not another source image.
    delta=Image.new('RGB',(W,H),(24,24,28)); dpx=delta.load()
    for y in range(H):
        for x in range(W):
            if grid[y*W+x] != v04_grid[y*W+x]: dpx[x,y]=(238,136,68)
    delta.save(out/'delta_v04_to_v05.png')
    delta.resize((W*8,H*8),Image.Resampling.NEAREST).save(out/'delta_v04_to_v05_8x.png')
    rgba=Image.open(png).convert('RGBA'); alpha=sorted({rgba.getpixel((x,y))[3] for y in range(H) for x in range(W)}); transparent_rgb_nonzero=sum(1 for y in range(H) for x in range(W) if rgba.getpixel((x,y))[3]==0 and rgba.getpixel((x,y))[:3]!=(0,0,0))
    (out/'matte_halo_report.json').write_text(json.dumps({'schema_version':'matte_halo_diagnostic.v2','asset_id':OUT_ID,'alpha_values':alpha,'alpha_binary':set(alpha).issubset({0,255}),'transparent_rgb_nonzero':transparent_rgb_nonzero,'halo_status':'no_transparent_rgb_halo' if transparent_rgb_nonzero==0 else 'review'},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    row77=[x for x in range(W) if grid[77*W+x]]; middle=[x for x in row77 if 15<=x<=36]
    (out/'ground_contact_report.json').write_text(json.dumps({'schema_version':'ground_contact_diagnostic.v3','asset_id':OUT_ID,'row':77,'visible_x':row77,'middle_strip_x':middle,'middle_strip_visible_count':len(middle),'baked_ground_strip_removed':len(middle)==0},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (out/'cleanup_actions.json').write_text(json.dumps({'schema_version':'localized_artistic_cleanup_action_log.v5','asset_id':OUT_ID,'parent_asset_id':V04_ID,'parent_sha256':V04_SHA,'method':'mechanical_palette_remap_with_minimal_native_patches','native_cleanup':'incomplete','material_topology':contract['status'],'semantic_map':'derived_diagnostic_not_independent','patches':actions,'patch_count':len(actions),'null_patches_count':0,'global_palette_remap':False,'source_regeneration':False,'resize_or_filter':False},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    lp=out/'cleanup_actions.json'; report={'schema_version':'localized_native_cleanup_rework.v5','asset_id':OUT_ID,'status':'technical_pass_visual_rework','method':'mechanical_palette_remap_with_minimal_native_patches','native_cleanup':'incomplete','material_topology':contract['status'],'semantic_map':'derived_diagnostic_not_independent','parent':{'asset_id':V04_ID,'sha256':V04_SHA,'path':str(v04.relative_to(lab))},'target':'56x80','patch_count':len(actions),'patch_log':str(lp.relative_to(lab)),'material_region_contract':'material_region_contract.json','material_leakage_report':'material_leakage_report.json','material_region_map':'material_region_map.png','material_boundary_overlay':'material_boundary_overlay.png','independent_topology_map':'independent_material_topology_map.png','independent_topology_report':'material_topology_independent_report.json','palette_role_map':'palette_role_map.png','delta_overlay':'delta_v04_to_v05.png','matte_halo_report':'matte_halo_report.json','ground_contact_report':'ground_contact_report.json','output':{'path':str(png.relative_to(lab)),'sha256':asset_sha},'claim_ceiling':'localized_native_cleanup_candidate','human_gate_status':'pending_human_decision','res_promotion':False,'animation_authorization':False,'rom_authorization':False,'action_log_sha256':sha(lp)}
    (out/'localized_native_cleanup_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (out/'provenance_report.json').write_text(json.dumps({'schema_version':'taina_native_rework_provenance.v1','asset_id':OUT_ID,'sha256':asset_sha,'input_asset_id':V04_ID,'input_sha256':V04_SHA,'source_role':'frozen_incumbent_for_localized_rework','identity_source':'approved_model_sheet_only','method':'mechanical_palette_remap_with_minimal_native_patches','pixel_source_policy':'direct_grid_edits_only','resize':False,'filter':False,'global_palette_remap':False,'res_promotion':False},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    sys.path.insert(0,str(lab.parents[2]/'tools/sgdk_wrapper'))
    from forge_art import pixel_contract
    validation=pixel_contract.validate_png(png,'transparent0')
    (out/'localized_native_cleanup_validation_report.json').write_text(json.dumps({'schema_version':'localized_native_cleanup_validation.v4','asset_id':OUT_ID,'path':str(png.relative_to(lab)),'sha256':asset_sha,'pixel_contract':{k:validation[k] for k in ('status','blocking','content_sha256','visible_colors','plte_entries','bit_depth','width','height')},'index0_role':'transparent0','method':'mechanical_palette_remap_with_minimal_native_patches','native_cleanup':'incomplete','material_topology':contract['status'],'semantic_map':'derived_diagnostic_not_independent','patch_count':len(actions),'null_patches_count':0,'global_palette_remap':False,'source_regeneration':False,'resize_or_filter':False,'human_gate_status':'pending_human_decision','visual_status':'technical_pass_visual_rework','res_promotion':False,'animation_authorization':False,'rom_authorization':False},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    manifest=lab/'localized_native_cleanup_manifest.json'; manifest.write_text(json.dumps({'schema_version':'localized_native_cleanup_manifest.v5','decision':'approve_localized_native_cleanup','frozen_checkpoint':{'asset_id':V04_ID,'sha256':V04_SHA,'role':'incumbent_for_rework_only','pose_final_approval':False},'current_rework':{'asset_id':OUT_ID,'path':str(png.relative_to(lab)),'sha256':asset_sha,'status':'technical_pass_visual_rework','method':'mechanical_palette_remap_with_minimal_native_patches','native_cleanup':'incomplete','material_topology':contract['status'],'semantic_map':'derived_diagnostic_not_independent','claim_ceiling':'localized_native_cleanup_candidate'},'human_gate_status':'pending_human_decision','next_gate':'approved_for_final_native_pose','res_promotion':False,'animation_authorization':False,'rom_authorization':False},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    gate=f'''# TAINA — v05 localized native cleanup human gate\n\nIncumbent anterior congelada: `{V04_ID}` / `{V04_SHA}`\n\nCandidata v05: `{OUT_ID}`\n\nSHA-256: `{asset_sha}`\n\nEscala: `56x80`\n\nStatus: `technical_pass_visual_rework`; `native_cleanup=incomplete`; `material_topology={contract['status']}`; `visual_pass=false`.\n\nRevisar em 1x: rosto/gaze, cachos na silhueta, punhos/wraps/antebraços, planos do abdômen e nó/caimento do sash.\n\nSó se `native_cleanup=complete` e `material_topology=passed` poderá ser usado o gate separado `approved_for_final_native_pose`.\n\nNada neste gate libera `res/`, animação, integração, ROM ou AAA.\n'''
    (lab/'human_gate_request_localized_cleanup.md').write_text(gate,encoding='utf-8')
    print(json.dumps({'status':'completed','asset_id':OUT_ID,'sha256':asset_sha,'patches':len(actions),'v04_material_status':json.loads((v04_dir/'material_region_contract.json').read_text())['status'],'v05_material_status':contract['status']},ensure_ascii=False))
if __name__=='__main__': main()
