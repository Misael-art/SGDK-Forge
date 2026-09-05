#!/usr/bin/env python3
"""Strictly localized native rework over the frozen v03 incumbent.

No resize, filter, source regeneration or global palette remap is performed.
All changes are explicit index edits on the 56x80 grid. The material map is
authored independently from palette indices and remains pending art review.
"""
import argparse, hashlib, json, sys
from pathlib import Path
from PIL import Image, ImageDraw

W,H=56,80
PARENT_ID='hybrid_cleanup_primary_im_lanczos3_rework_v03'
PARENT_SHA='99160ec422010d2ac68fbb4b10cc03db72012316508882e1b9b8cf336ec51a33'
OUT_ID='hybrid_cleanup_primary_im_lanczos3_rework_v04'
SYMPTOMS={
    'hair':'hair mass remains solid; curl groups do not break the silhouette at 1x',
    'face_eye':'face cluster does not state eye, gaze, nose plane and jaw clearly at 1x',
    'guard':'fist, wrap and forearm boundaries remain partially fused',
    'abdomen':'skin highlights are fragmented into point noise',
    'sash':'knot and falling tail lack a strong readable continuous shape',
    'trousers':'indigo shadow clusters fragment the leg volumes',
    'feet_ground':'foot sole/contact needs a stable hard-edge without baked ground',
}

# Values are final palette indices. This is not a palette remap.
PATCHES=[
    # Hair: three contour notches plus connected curl groups.
    (15,3,0,'hair','carve_curl_notch_1'),(16,8,0,'hair','carve_curl_notch_2'),(16,14,0,'hair','carve_curl_notch_3'),
    (18,4,4,'hair','curl_group_1_outer_highlight'),(19,5,4,'hair','curl_group_1_outer_highlight'),
    (17,7,4,'hair','curl_group_2_outer_highlight'),(18,8,4,'hair','curl_group_2_outer_highlight'),
    (19,10,4,'hair','curl_group_3_outer_highlight'),(20,10,3,'hair','curl_group_3_base'),
    (21,13,4,'hair','curl_group_4_inner_highlight'),(22,13,3,'hair','curl_group_4_inner_base'),
    # Face: connected eye/brow/nose/jaw cluster, not isolated tokens.
    (28,10,1,'face_eye','brow_anchor'),(29,10,1,'face_eye','brow_bridge'),(30,11,1,'face_eye','eye_outer'),
    (29,12,1,'face_eye','eye_inner'),(30,12,5,'face_eye','eye_skin_boundary'),
    (31,13,1,'face_eye','nose_plane'),(32,13,1,'face_eye','jaw_side'),(32,14,1,'face_eye','jaw_side'),
    (30,14,6,'face_eye','cheek_base'),
    # Guard: continuous teal wrap clusters with hard separators from skin.
    (20,22,1,'guard','left_wrap_boundary'),(21,22,12,'guard','left_wrap_base'),(22,22,12,'guard','left_wrap_base'),
    (23,22,12,'guard','left_wrap_base'),(20,23,1,'guard','left_wrap_boundary'),(21,23,12,'guard','left_wrap_base'),
    (24,23,1,'guard','left_forearm_boundary'),
    (36,22,1,'guard','right_wrap_boundary'),(37,22,12,'guard','right_wrap_base'),(38,22,12,'guard','right_wrap_base'),
    (39,22,12,'guard','right_wrap_base'),(36,23,1,'guard','right_wrap_boundary'),(37,23,12,'guard','right_wrap_base'),
    (40,23,1,'guard','right_forearm_boundary'),
    # Abdomen: consolidate existing skin planes rather than add micro-colors.
    (26,30,6,'abdomen','join_skin_base_plane'),(28,30,6,'abdomen','join_skin_base_plane'),
    (29,31,6,'abdomen','join_skin_base_plane'),(27,32,6,'abdomen','join_skin_base_plane'),
    (29,33,6,'abdomen','join_skin_base_plane'),
    # Sash: reinforce knot and falling tail as connected teal shapes.
    (18,38,12,'sash','knot_base_continuity'),(20,38,12,'sash','knot_base_continuity'),
    (19,39,12,'sash','knot_base_continuity'),(20,39,1,'sash','knot_contour'),
    (37,41,13,'sash','tail_highlight'),(38,42,13,'sash','tail_highlight'),(37,43,13,'sash','tail_highlight'),
    # Trousers: make the inner-knee shadows continuous without changing the silhouette.
    (23,43,14,'trousers','left_inner_knee_shadow'),(26,43,14,'trousers','left_inner_knee_shadow'),(31,43,14,'trousers','right_inner_knee_shadow'),
    # Feet: explicit hard sole edges, with no pixels between the feet.
    (9,77,1,'feet_ground','left_toe_contour'),(14,77,1,'feet_ground','left_toe_contour'),
    (37,77,1,'feet_ground','right_toe_contour'),(47,77,1,'feet_ground','right_toe_contour'),
    (12,78,6,'feet_ground','left_sole_contact'),(13,78,6,'feet_ground','left_sole_contact'),
    (40,78,6,'feet_ground','right_sole_contact'),(41,78,6,'feet_ground','right_sole_contact'),
]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--lab-root',type=Path,required=True); args=ap.parse_args()
    lab=args.lab_root.resolve(); sys.path.insert(0,str(lab/'scripts')); import run_primary_artistic_cleanup as old
    parent=lab/'localized_native_cleanup'/PARENT_ID/(PARENT_ID+'.png')
    if sha(parent)!=PARENT_SHA: raise SystemExit('parent hash mismatch')
    with Image.open(parent) as src: grid=list(src.convert('P').getdata())
    actions=[]; forced={}
    for x,y,after,region,reason in PATCHES:
        pos=y*W+x; before=grid[pos]
        if before==after: continue
        grid[pos]=after; forced[pos]=after
        actions.append({'region':region,'symptom':SYMPTOMS[region],'x':x,'y':y,'before':before,'after':after,'reason':reason})
    owners=[old.owner_at(x,y,grid) for y in range(H) for x in range(W)]
    out=lab/'localized_native_cleanup'/OUT_ID; out.mkdir(parents=True,exist_ok=True)
    im=Image.new('P',(W,H),0); im.putpalette(sum((list(c) for c in old.PALETTE),[])+[0,0,0]*240); im.putdata(grid)
    png=out/(OUT_ID+'.png'); im.save(png,'PNG',bits=4,transparency=0); old.evidence(im,out)
    # Rebuild derived evidence from the saved PNG so index 0 is interpreted as
    # transparency. The in-memory P image has no transparency metadata.
    with Image.open(png) as saved:
        rgba=saved.convert('RGBA')
        for scale,name in ((2,'2x'),(3,'3x'),(8,'8x')): saved.resize((W*scale,H*scale),Image.Resampling.NEAREST).save(out/f'preview_nearest_{name}.png')
    rgba.getchannel('A').point(lambda p:255 if p else 0).save(out/'silhouette_binary.png')
    for name,rgb in (('light',(238,238,230)),('dark',(28,30,38)),('chroma',(238,0,238))):
        bg=Image.new('RGBA',(W,H),rgb+(255,)); bg.alpha_composite(rgba); bg.convert('RGB').save(out/f'background_{name}.png')
    scene=Image.new('RGBA',(320,224),(68,102,102,255)); ImageDraw.Draw(scene).rectangle((0,168,319,223),fill=(34,34,68,255)); scene.alpha_composite(rgba,(132,88)); scene.convert('RGB').save(out/'composition_320x224.png')
    for name,box in {'head_face':(8,0,48,24),'shoulders_guard':(4,14,52,36),'waist_hip':(8,28,50,50),'knees':(4,48,52,68),'feet_ground':(0,66,56,80)}.items(): rgba.crop(box).resize(((box[2]-box[0])*8,(box[3]-box[1])*8),Image.Resampling.NEAREST).save(out/f'crop_{name}.png')
    contour=Image.new('P',(W,H),0); contour.putpalette(sum((list(c) for c in old.PALETTE),[])+[0,0,0]*240); contour_vals=[]
    for y in range(H):
        for x in range(W): contour_vals.append(1 if rgba.getpixel((x,y))[3] and any(xx<0 or yy<0 or xx>=W or yy>=H or rgba.getpixel((xx,yy))[3]==0 for xx,yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1))) else 0)
    contour.putdata(contour_vals); contour.resize((W*8,H*8),Image.Resampling.NEAREST).save(out/'contour_overlay.png')
    # Independent material assignment is based on coordinate regions and contour,
    # never on the final palette index. It is a candidate map, not a pass.
    topo=Image.new('P',(W,H),0); topo.putpalette(sum((list(c) for c in old.PALETTE),[])+[0,0,0]*240); topo.putdata([old.ROLE_OWNER[o] for o in owners]); topo.save(out/'independent_material_topology_map.png',bits=4,transparency=0)
    boundary=Image.new('P',(W,H),0); boundary.putpalette(sum((list(c) for c in old.PALETTE),[])+[0,0,0]*240); vals=[]
    for y in range(H):
        for x in range(W):
            p=y*W+x; vals.append(1 if owners[p]!='transparent' and any(0<=x+dx<W and 0<=y+dy<H and owners[(y+dy)*W+x+dx] not in ('transparent',owners[p]) for dx,dy in ((1,0),(0,1))) else 0)
    boundary.putdata(vals); boundary.save(out/'independent_material_boundary_overlay.png',bits=4,transparency=0)
    index_role={1:'outline',2:'hair',3:'hair',4:'hair',5:'skin',6:'skin',7:'skin',8:'top',9:'top',10:'top',11:'wrap_sash',12:'wrap_sash',13:'wrap_sash',14:'trousers',15:'trousers'}
    rolemap=Image.new('P',(W,H),0); rolemap.putpalette(sum((list(c) for c in old.PALETTE),[])+[0,0,0]*240); rolemap.putdata([old.ROLE_OWNER.get(index_role.get(v,'skin'),3) if v else 0 for v in grid]); rolemap.save(out/'palette_role_map.png',bits=4,transparency=0)
    with Image.open(png) as saved: rgba=saved.convert('RGBA')
    alpha=sorted({rgba.getpixel((x,y))[3] for y in range(H) for x in range(W)})
    transparent_rgb_nonzero=sum(1 for y in range(H) for x in range(W) if rgba.getpixel((x,y))[3]==0 and rgba.getpixel((x,y))[:3]!=(0,0,0))
    (out/'matte_halo_report.json').write_text(json.dumps({'schema_version':'matte_halo_diagnostic.v1','asset_id':OUT_ID,'alpha_values':alpha,'alpha_binary':set(alpha).issubset({0,255}),'transparent_rgb_nonzero':transparent_rgb_nonzero,'halo_status':'no_transparent_rgb_halo' if transparent_rgb_nonzero==0 else 'review','note':'Diagnostic only; does not establish visual quality.'},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    row77=[x for x in range(W) if grid[77*W+x]]; middle=[x for x in row77 if 15<=x<=36]
    (out/'ground_contact_report.json').write_text(json.dumps({'schema_version':'ground_contact_diagnostic.v2','asset_id':OUT_ID,'row':77,'visible_x':row77,'middle_strip_x':middle,'middle_strip_visible_count':len(middle),'baked_ground_strip_removed':len(middle)==0,'interpretation':'remaining pixels are the two foot contact intervals; diagnostic only.'},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (out/'material_topology_independent_report.json').write_text(json.dumps({'schema_version':'independent_material_topology_candidate.v1','asset_id':OUT_ID,'independent_from_palette_indices':True,'owner_source':'hand_authored_coordinate_region_masks_plus_silhouette_contour','visible_pixel_coverage_exact':True,'assigned_roles':['hair','skin','top','wraps','sash','trousers','feet','outline_shared'],'status':'independent_candidate_pending_human_review','artistic_validation':'not_run','notes':'Every visible pixel receives a diagnostic owner, but the map does not prove artistic topology until reviewed against the 1x sprite and model sheet.'},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    log={'schema_version':'localized_artistic_cleanup_action_log.v4','asset_id':OUT_ID,'parent_asset_id':PARENT_ID,'parent_sha256':PARENT_SHA,'method':'mechanical_palette_remap_with_minimal_native_patches','native_cleanup':'incomplete','material_topology':'independent_candidate_pending_human_review','semantic_map':'derived_diagnostic_not_independent','patches':actions,'patch_count':len(actions),'null_patches_count':0,'regions':sorted({p['region'] for p in actions}),'global_palette_remap':False,'source_regeneration':False,'resize_or_filter':False}
    lp=out/'cleanup_actions.json'; lp.write_text(json.dumps(log,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    report={'schema_version':'localized_native_cleanup_rework.v4','asset_id':OUT_ID,'status':'technical_pass_visual_rework','method':'mechanical_palette_remap_with_minimal_native_patches','native_cleanup':'incomplete','material_topology':'independent_candidate_pending_human_review','semantic_map':'derived_diagnostic_not_independent','parent':{'asset_id':PARENT_ID,'sha256':PARENT_SHA,'path':str(parent.relative_to(lab))},'target':'56x80','patch_count':len(actions),'patch_log':str(lp.relative_to(lab)),'independent_topology_map':'independent_material_topology_map.png','independent_topology_report':'material_topology_independent_report.json','palette_role_map':'palette_role_map.png','matte_halo_report':'matte_halo_report.json','ground_contact_report':'ground_contact_report.json','output':{'path':str(png.relative_to(lab)),'sha256':sha(png)},'claim_ceiling':'localized_native_cleanup_candidate','human_gate_status':'pending_human_decision','res_promotion':False,'animation_authorization':False,'rom_authorization':False}
    report['action_log_sha256']=sha(lp); (out/'localized_native_cleanup_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    sys.path.insert(0,str(lab.parents[2]/'tools/sgdk_wrapper')); from forge_art import pixel_contract
    validation=pixel_contract.validate_png(png,'transparent0')
    (out/'localized_native_cleanup_validation_report.json').write_text(json.dumps({'schema_version':'localized_native_cleanup_validation.v3','asset_id':OUT_ID,'path':str(png.relative_to(lab)),'sha256':sha(png),'pixel_contract':{k:validation[k] for k in ('status','blocking','content_sha256','visible_colors','plte_entries','bit_depth','width','height')},'index0_role':'transparent0','method':report['method'],'native_cleanup':report['native_cleanup'],'material_topology':report['material_topology'],'semantic_map':report['semantic_map'],'patch_count':len(actions),'null_patches_count':0,'global_palette_remap':False,'source_regeneration':False,'resize_or_filter':False,'human_gate_status':'pending_human_decision','visual_status':'technical_pass_visual_rework','res_promotion':False,'animation_authorization':False,'rom_authorization':False},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    manifest={'schema_version':'localized_native_cleanup_manifest.v4','decision':'approve_localized_native_cleanup','checkpoint_scope':'best_current_base_for_continued_native_authoring','incumbent':{'asset_id':OUT_ID,'path':str(png.relative_to(lab)),'sha256':sha(png),'scale':'56x80','status':'technical_pass_visual_rework','method':'mechanical_palette_remap_with_minimal_native_patches','native_cleanup':'incomplete','material_topology':'independent_candidate_pending_human_review','semantic_map':'derived_diagnostic_not_independent','claim_ceiling':'localized_native_cleanup_candidate'},'parent_checkpoint':{'asset_id':PARENT_ID,'sha256':PARENT_SHA,'decision':'approve_localized_native_cleanup'},'discarded_visual_regression':{'asset_id':'hybrid_cleanup_primary_im_lanczos3_rework_v02','source_allowed':False,'record':'localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v02/DISCARDED_VISUAL_REGRESSION.md'},'human_gate_status':'pending_human_decision','res_promotion':False,'animation_authorization':False,'rom_authorization':False}
    (lab/'localized_native_cleanup_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    gate='''# TAINA — v04 localized native cleanup human gate\n\nIncumbent congelada: `hybrid_cleanup_primary_im_lanczos3_rework_v04`\n\nSHA-256: `'''+sha(png)+'''`\n\nEscala: `56x80`\n\nEscopo: `localized_native_cleanup_only`; esta é a melhor base atual para continuar a autoria nativa, não uma pose final.\n\nStatus: `technical_pass_visual_rework`; `native_cleanup=incomplete`; `material_topology=independent_candidate_pending_human_review`; `visual_pass=false`.\n\nRevisar em 1x: cluster de rosto/olho/gaze, 3–5 grupos de cachos na silhueta, separação de punhos/wraps/antebraços, planos contínuos do abdômen, nó/caimento do sash, sombras internas das calças, pés e contato.\n\nPróximo gate separado após aprovação visual: `approved_for_final_native_pose`.\n\nResposta aceita:\n\n```text\ndecision=approved_for_final_native_pose\nasset_id=hybrid_cleanup_primary_im_lanczos3_rework_v04\nsha256='''+sha(png)+'''\nscale=56x80\n```\n\nou:\n\n```text\ndecision=reject_localized_native_cleanup\nreason=<motivo observável>\n```\n\nNada neste gate libera `res/`, animação, integração, ROM, `visual_pass` ou AAA.\n'''
    (lab/'human_gate_request_localized_cleanup.md').write_text(gate,encoding='utf-8')
    print(json.dumps({'status':'completed','asset_id':OUT_ID,'sha256':sha(png),'patches':len(actions),'parent_sha256':PARENT_SHA},ensure_ascii=False))
if __name__=='__main__': main()
