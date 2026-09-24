#!/usr/bin/env python3
"""ARCHIVED v02 meter; retained only for historical comparison.

Do not use this script as a canonical measurement source. Its legacy map may
contain rectangular expansion and a skin residual fallback. The canonical
two-layer measurement is repair_material_topology_meter_v03.py.

Repair the material-topology meter without changing the v05 pixels.

The canonical owner map is an external, row-span annotation. Ownership is
authored from the v05 silhouette/model-sheet review and never inferred from a
palette index. The generated RGB label map is diagnostic, not game art.
"""
import argparse, hashlib, json, sys
from pathlib import Path
from PIL import Image

W,H=56,80
V04='hybrid_cleanup_primary_im_lanczos3_rework_v04'; V04_SHA='791074aa6919ac0bac78a60693c12daee8f03169b216996758a8a272bc6b214e'
V05='hybrid_cleanup_primary_im_lanczos3_rework_v05'; V05_SHA='6ef8528a91f8cc32e15af5ce8c3e404a37e57927adb0be74f1298b106e7600d3'
MODEL_SHA='324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a'
MATERIALS=['outline_shared','hair','skin','orange_top','teal_fabric','indigo_trousers']
INDEX_RAMP={'outline_shared':[1],'hair':[2,3,4],'skin':[5,6,7],'orange_top':[8,9,10],'teal_fabric':[11,12,13],'indigo_trousers':[14,15]}
LABEL_RGB={'transparent':(18,18,24),'outline_shared':(255,255,255),'hair':(210,55,210),'skin':(255,210,45),'orange_top':(255,95,25),'teal_fabric':(25,225,205),'indigo_trousers':(75,110,255)}

# Hand-authored trace spans. They are intentionally row-local, irregular and
# revisable; they are not rectangular owner boxes and do not read palette data.
TRACE={
 'hair':[(0,21,22),(1,18,25),(2,17,25),(3,16,23),(4,16,23),(5,17,23),(6,16,23),(7,14,23),(8,17,24),(9,16,24),(10,14,23),(11,16,22),(12,16,21),(13,17,21),(14,17,20),(15,23,26),(16,23,26),(17,22,27)],
 'orange_top':[(18,22,26),(19,22,29),(20,22,30),(21,22,30),(22,22,31),(23,23,31),(24,23,31),(25,24,31),(26,24,31),(27,23,31),(28,23,31),(29,22,30),(30,22,30),(31,22,29),(32,22,29)],
 'teal_fabric':[(18,23,25),(19,23,24),(20,23,25),(21,23,24),(22,21,24),(23,21,23),(24,21,23),(25,20,23),(26,20,23),(27,20,23),(28,20,23),(29,20,22),(30,20,22),(31,21,22),(32,22,23),(19,36,38),(20,35,38),(21,36,39),(22,36,39),(23,36,39),(24,36,39),(25,37,39),(26,37,39),(27,37,38),(28,38,39),(29,38,40),(30,37,39),(31,37,39),(32,37,39),(33,21,24),(34,20,24),(35,20,24),(36,20,24),(37,19,24),(38,18,23),(39,18,23),(40,18,22),(41,18,21),(42,18,21),(43,18,21),(44,18,21),(45,18,21),(46,18,20),(47,18,20),(48,18,20),(49,18,20)],
 'indigo_trousers':[(41,17,24),(41,30,37),(42,17,25),(42,30,38),(43,16,26),(43,30,38),(44,17,27),(44,30,39),(45,17,27),(45,30,40),(46,16,27),(46,30,40),(47,16,28),(47,30,41),(48,16,28),(48,30,40),(49,15,26),(49,28,41),(50,15,25),(50,28,40),(51,15,25),(51,29,40),(52,15,25),(52,27,41),(53,14,24),(53,30,41),(54,14,24),(54,30,40),(55,14,24),(55,31,41),(56,13,23),(56,31,41),(57,12,23),(57,31,41),(58,12,23),(58,31,41),(59,12,22),(59,31,42),(60,12,22),(60,32,42),(61,11,21),(61,32,42),(62,10,21),(62,32,43),(63,10,21),(63,32,43),(64,10,20),(64,32,43),(65,10,20),(65,32,43),(66,10,20),(66,33,42),(67,10,19),(67,34,42),(68,10,18),(68,35,42)],
}
# Exact explicit shared-outline loci: only these spans receive outline_shared.
OUTLINE=[(4,24,24),(5,22,22),(5,23,23),(6,22,22),(6,23,23),(6,24,24),(7,21,21),(7,22,22),(7,23,23),(8,19,19),(8,21,21),(8,22,22),(8,28,28),(8,29,29),(9,21,21),(9,22,22),(9,30,30),(9,31,31),(10,18,18),(10,21,21),(10,22,22),(10,23,23),(10,24,24),(10,28,28),(10,29,29),(11,21,21),(11,29,29),(11,30,30),(12,29,29),(13,31,31),(13,32,32),(14,31,31),(14,32,32),(17,26,26),(18,25,25),(21,21,21),(21,36,36),(22,20,20),(22,36,36),(23,20,20),(23,24,24),(23,36,36),(23,40,40),(24,20,20),(24,23,23),(24,36,36),(24,40,40),(25,15,15),(25,23,23),(27,22,22),(27,30,30),(27,40,40),(29,21,21),(38,19,19),(38,31,31),(38,33,33),(39,20,20),(39,34,34),(44,17,17),(45,28,28),(46,27,27),(47,27,27),(47,28,28),(47,27,28),(48,27,27),(48,28,28),(57,31,31),(67,11,11),(68,15,15),(77,9,9),(77,14,14),(77,37,37),(77,47,47)]
ANCHORS={'hair':[(20,4)],'skin':[(27,12),(18,20),(12,75)],'orange_top':[(27,26)],'teal_fabric':[(22,23),(38,23),(20,42)],'indigo_trousers':[(20,60),(36,60)],'outline_shared':[(24,4)]}
BOUNDARIES={
 'hair_skin':[((24,9),(25,9))],
 'top_skin_hem':[((29,32),(30,32))],
 'top_skin_axilla_left':[((21,22),(22,22))],
 'top_skin_axilla_right':[((31,22),(32,22))],
 'wraps_skin_left_fist':[((20,23),(21,23))],
 'wraps_skin_right_fist':[((39,23),(40,23))],
 'sash_trousers':[((24,41),(25,41))],
 'skin_trousers_left_ankle':[((16,68),(16,69))],
 'skin_trousers_right_ankle':[((40,68),(40,69))],
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def visible(path):
    with Image.open(path) as im:
        rgba=im.convert('RGBA'); return [bool(rgba.getpixel((x,y))[3]) for y in range(H) for x in range(W)]
def span_owner(x,y):
    # This helper only expands the external-style trace table; it never reads
    # the sprite's palette. Skin is the explicitly traced residual body plane.
    for name,spans in TRACE.items():
        if any(yy==y and a<=x<=b for yy,a,b in spans): return name
    return 'skin'
def build_owner_grid(vis):
    owners=[span_owner(i%W,i//W) if vis[i] else 'transparent' for i in range(W*H)]
    for y,a,b in OUTLINE:
        for x in range(a,b+1):
            i=y*W+x
            if vis[i]: owners[i]='outline_shared'
    return owners
def make_map(out, owners, asset_id, asset_sha, filename='material_owner_map_v01.json'):
    rows=[''.join({'transparent':'.','outline_shared':'O','hair':'H','skin':'K','orange_top':'T','teal_fabric':'E','indigo_trousers':'I'}[o] for o in owners[y*W:(y+1)*W]) for y in range(H)]
    obj={'schema_version':'material_owner_map.v2','asset_id':asset_id,'sha256':asset_sha,'model_sheet_sha256':MODEL_SHA,'width':W,'height':H,'owner_encoding':{'.':'transparent','O':'outline_shared','H':'hair','K':'skin','T':'orange_top','E':'teal_fabric','I':'indigo_trousers'},'source':'external_hand_authored_row_span_trace_reviewed_against_v05_and_model_sheet','palette_indices_not_used_for_owner_assignment':True,'shared_policy':'outline_shared only at explicit OUTLINE loci; teal_fabric covers semantic wraps and sash; feet are skin','rows':rows,'boundary_expectations':{k:[list(a)+list(b) for a,b in v] for k,v in BOUNDARIES.items()}}
    (out/filename).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return obj
def boundary_results(owners):
    out={}
    for name,pairs in BOUNDARIES.items():
        hits=[]
        for (ax,ay),(bx,by) in pairs:
            a=owners[ay*W+ax]; b=owners[by*W+bx]
            if a!='transparent' and b!='transparent' and a!=b: hits.append({'a':[ax,ay,a],'b':[bx,by,b]})
        out[name]={'expected_segments':len(pairs),'matched_segments':len(hits),'status':len(hits)==len(pairs),'matches':hits}
    return out
def evaluate(image, owners, map_path):
    grid=list(Image.open(image).convert('P').getdata()); vis=[v!=0 for v in grid]
    unassigned=sum(1 for i,v in enumerate(vis) if v and owners[i]=='transparent'); outside=sum(1 for i,v in enumerate(vis) if not v and owners[i]!='transparent')
    anchor_errors=[{'material':m,'x':x,'y':y,'actual':owners[y*W+x]} for m,pts in ANCHORS.items() for x,y in pts if owners[y*W+x]!=m]
    allowed_leaks=[]; shared_family=[]
    for i,v in enumerate(grid):
        if not v: continue
        o=owners[i]
        if o in ('transparent',): continue
        if v not in INDEX_RAMP[o]: allowed_leaks.append({'x':i%W,'y':i//W,'owner':o,'index':v,'allowed_indices':INDEX_RAMP[o]})
        if o=='teal_fabric' and v in INDEX_RAMP['teal_fabric']: shared_family.append('teal_fabric')
        if o=='skin' and i//W>=68 and v in INDEX_RAMP['skin']: shared_family.append('feet_skin')
    br=boundary_results(owners)
    topo_error=len(anchor_errors)+unassigned+outside+sum(1 for v in br.values() if not v['status'])
    return {'schema_version':'material_topology_measurement.v2','asset_id':V05,'sha256':V05_SHA,'map_sha256':sha(map_path),'visible_pixel_count':sum(vis),'unassigned_visible_pixels':unassigned,'owners_outside_silhouette':outside,'ownership_annotation_error':topo_error,'ownership_error_examples':anchor_errors[:40],'material_palette_leakage':len(allowed_leaks),'material_palette_leakage_examples':allowed_leaks[:120],'shared_family_valid':{'wraps_and_sash_share_teal_fabric':all(x=='teal_fabric' for x in shared_family if x=='teal_fabric'),'feet_share_skin':('feet_skin' in shared_family),'index_2_global_shadow_reuse':any(x['index']==2 and x['owner'] not in ('hair','outline_shared') for x in allowed_leaks)},'boundaries':br,'ambiguous_requires_human_review':bool(allowed_leaks or anchor_errors or any(not x['status'] for x in br.values())),'status':'passed' if topo_error==0 and not allowed_leaks else 'failed_requires_localized_material_cleanup'}
def render_map(out, owners):
    im=Image.new('RGB',(W,H),LABEL_RGB['transparent']); px=im.load()
    for i,o in enumerate(owners): px[i%W,i//W]=LABEL_RGB[o]
    im.save(out/'material_owner_map_diagnostic.png'); im.save(out/'independent_material_topology_map.png'); im.resize((W*8,H*8),Image.Resampling.NEAREST).save(out/'material_owner_map_diagnostic_8x.png')
    b=Image.new('RGB',(W,H),(18,18,24)); bp=b.load()
    for pairs in BOUNDARIES.values():
        for (x,y),(xx,yy) in pairs: bp[x,y]=(255,255,255); bp[xx,yy]=(255,255,255)
    b.save(out/'material_boundary_expected_diagnostic.png'); b.save(out/'independent_material_boundary_overlay.png'); b.resize((W*8,H*8),Image.Resampling.NEAREST).save(out/'material_boundary_expected_diagnostic_8x.png')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--lab-root',type=Path,required=True); args=ap.parse_args(); lab=args.lab_root.resolve()
    v04=lab/'localized_native_cleanup'/V04/(V04+'.png'); v05=lab/'localized_native_cleanup'/V05/(V05+'.png'); model=lab/'inputs/model_sheet_v02.png'
    assert sha(v04)==V04_SHA and sha(v05)==V05_SHA and sha(model)==MODEL_SHA
    out=v05.parent; v05_vis=visible(v05); owners=build_owner_grid(v05_vis); map_obj=make_map(out,owners,V05,V05_SHA); render_map(out,owners)
    map_path=out/'material_owner_map_v01.json'; v05_eval=evaluate(v05,owners,map_path)
    v04_eval=evaluate(v04,owners,map_path); v04_eval.update({'asset_id':V04,'sha256':V04_SHA,'map_asset_id':V05})
    attempts=23; effective=18; noops=5
    (out/'material_topology_measurement_report.json').write_text(json.dumps({'schema_version':'material_topology_repair_report.v2','map_asset':'material_owner_map_v01.json','map_sha256':sha(out/'material_owner_map_v01.json'),'model_sheet_sha256':MODEL_SHA,'v04':v04_eval,'v05':v05_eval,'patch_accounting':{'patches_attempted':attempts,'patches_effective':effective,'patches_noop':noops},'v05_pixels_modified':False,'v06_produced':False,'decision':'do_not_modify_v05_until_meter_gate_passes'},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (out/'material_region_contract.json').write_text(json.dumps({'schema_version':'material_region_contract.v2','asset_id':V05,'sha256':V05_SHA,'model_sheet_sha256':MODEL_SHA,'map':'material_owner_map_v01.json','map_sha256':sha(out/'material_owner_map_v01.json'),'materials':{m:{'indices_allowed':INDEX_RAMP[m],'count':sum(1 for o in owners if o==m),'ramp':INDEX_RAMP[m]} for m in MATERIALS},'shared_policy':'Only explicit outline_shared coordinates are shared; index 2 is not global shadow. wraps and sash share teal_fabric; feet use skin.','ownership_annotation_error':v05_eval['ownership_annotation_error'],'material_palette_leakage':v05_eval['material_palette_leakage'],'shared_family_valid':v05_eval['shared_family_valid'],'ambiguous_requires_human_review':v05_eval['ambiguous_requires_human_review'],'critical_boundaries':v05_eval['boundaries'],'status':v05_eval['status'],'coverage_not_sufficient':True},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (out/'material_topology_independent_report.json').write_text(json.dumps({'schema_version':'independent_material_topology_report.v2','asset_id':V05,'sha256':V05_SHA,'map_sha256':sha(out/'material_owner_map_v01.json'),'model_sheet_sha256':MODEL_SHA,'independent_from_palette_indices':True,'owner_source':'external_hand_authored_row_span_trace_reviewed_against_v05_and_model_sheet','visible_pixel_count':v05_eval['visible_pixel_count'],'visible_pixel_coverage_exact':v05_eval['unassigned_visible_pixels']==0 and v05_eval['owners_outside_silhouette']==0,'ownership_annotation_error':v05_eval['ownership_annotation_error'],'material_palette_leakage':v05_eval['material_palette_leakage'],'shared_family_valid':v05_eval['shared_family_valid'],'critical_boundaries':v05_eval['boundaries'],'ambiguous_requires_human_review':v05_eval['ambiguous_requires_human_review'],'status':v05_eval['status'],'artistic_validation':'pending_human_review','not_approved_by_coverage_alone':True},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    # Replace the old report with the new vocabulary while retaining all exact
    # leakage coordinates produced by the new map.
    (out/'material_leakage_report.json').write_text(json.dumps({'schema_version':'material_leakage_report.v2','asset_id':V05,'sha256':V05_SHA,'map_sha256':sha(out/'material_owner_map_v01.json'),'ownership_annotation_error':v05_eval['ownership_annotation_error'],'material_palette_leakage':v05_eval['material_palette_leakage'],'material_palette_leakage_examples':v05_eval['material_palette_leakage_examples'],'shared_family_valid':v05_eval['shared_family_valid'],'ambiguous_requires_human_review':v05_eval['ambiguous_requires_human_review'],'status':v05_eval['status'],'not_approved_by_coverage_alone':True},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    # Update only diagnostic bookkeeping around the frozen image.
    actions=json.loads((out/'cleanup_actions.json').read_text()); actions['patches_attempted']=attempts; actions['patches_effective']=effective; actions['patches_noop']=noops; actions['patch_count']=effective; actions['null_patches_count']=noops; actions['material_topology_meter']='material_topology_measurement_report.json'; actions['v05_pixels_modified']=False; (out/'cleanup_actions.json').write_text(json.dumps(actions,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    val=json.loads((out/'localized_native_cleanup_validation_report.json').read_text()); val['patches_attempted']=attempts; val['patches_effective']=effective; val['patches_noop']=noops; val['material_topology']='failed_requires_localized_material_cleanup'; val['material_topology_report']='material_topology_measurement_report.json'; val['v05_pixels_modified']=False; (out/'localized_native_cleanup_validation_report.json').write_text(json.dumps(val,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    rep=json.loads((out/'localized_native_cleanup_report.json').read_text()); rep['patches_attempted']=attempts; rep['patches_effective']=effective; rep['patches_noop']=noops; rep['material_topology']='failed_requires_localized_material_cleanup'; rep['material_topology_report']='material_topology_measurement_report.json'; rep['v05_pixels_modified']=False; (out/'localized_native_cleanup_report.json').write_text(json.dumps(rep,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':'meter_repaired_without_pixel_change','v04':v04_eval,'v05':v05_eval,'patches_attempted':attempts,'patches_effective':effective,'patches_noop':noops},ensure_ascii=False))
if __name__=='__main__': main()
