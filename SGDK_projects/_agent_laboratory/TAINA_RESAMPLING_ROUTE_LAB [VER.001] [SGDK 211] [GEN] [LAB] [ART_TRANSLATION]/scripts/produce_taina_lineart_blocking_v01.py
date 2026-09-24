#!/usr/bin/env python3
"""Author two independent native lineart-blocking candidates for TAINA.

The candidate pixels are explicit grid clusters authored from the approved
model sheet. Lanczos3 and Mitchell are guide metadata only; their pixels are
never copied. This script writes only a new laboratory stage.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

W, H = 56, 80
LAB_NAME = "TAINA_RESAMPLING_ROUTE_LAB [VER.001] [SGDK 211] [GEN] [LAB] [ART_TRANSLATION]"
MODEL = "inputs/model_sheet_v02.png"
MODEL_SHA = "324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a"
UNDERLAYS = {
    "A_underlay_im_lanczos3": ("hybrid_cleanup_shootout/hybrid_cleanup_primary_im_lanczos3_v01/hybrid_cleanup_primary_im_lanczos3_v01.png", "3e60cd9efb233d0ce715c543e9cacdaacbe044b253c088dd06ada52f131b4cf1"),
    "B_underlay_im_mitchell_netravali": ("hybrid_cleanup_shootout/hybrid_cleanup_challenger_im_mitchell_netravali_v01/hybrid_cleanup_challenger_im_mitchell_netravali_v01.png", "8e8eb7cbb6d0aaa8906f88f7a12c4352f431d41cd823f57e958c41c3d19bcd61"),
}
PALETTE = [(0, 0, 0), (32, 32, 32), (224, 128, 64), (128, 128, 128)]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_spans(mask: set[tuple[int, int]], spans: list[tuple[int, int, int]]) -> None:
    for y, x1, x2 in spans:
        mask.update((x, y) for x in range(x1, x2 + 1))


def variant_mask(variant: str) -> set[tuple[int, int]]:
    rows_a = [
        (0,21,22),(1,18,25),(2,16,27),(3,15,29),(4,14,30),(5,14,31),(6,15,31),(7,13,32),(8,15,33),(9,14,33),(10,14,32),(11,15,33),(12,16,32),(13,17,32),(14,18,31),(15,20,30),(16,21,29),(17,22,29),
        (18,20,35),(19,18,36),(20,17,37),(21,16,38),(22,15,39),(23,15,40),(24,14,40),(25,14,40),(26,14,40),(27,15,41),(28,15,40),(29,16,39),(30,17,39),(31,18,38),(32,19,37),(33,20,36),(34,20,36),(35,19,37),(36,19,38),(37,18,39),(38,18,40),(39,17,41),(40,17,41),
        (41,15,26),(41,29,40),(42,15,26),(42,29,41),(43,14,26),(43,30,42),(44,14,27),(44,30,42),(45,14,27),(45,30,43),(46,13,27),(46,30,43),(47,13,28),(47,30,43),(48,13,28),(48,30,42),(49,12,26),(49,29,43),(50,12,25),(50,29,43),(51,12,25),(51,30,43),(52,12,25),(52,29,44),(53,11,24),(53,30,44),(54,11,24),(54,31,43),(55,11,24),(55,31,43),(56,10,23),(56,31,43),(57,10,23),(57,31,44),(58,10,23),(58,32,44),(59,9,22),(59,32,44),(60,9,22),(60,32,44),(61,9,21),(61,33,43),(62,8,21),(62,33,43),(63,8,21),(63,33,43),(64,8,20),(64,33,43),(65,8,20),(65,34,42),(66,8,20),(66,34,42),(67,8,19),(67,35,42),(68,9,18),(68,35,42),
        (69,8,18),(69,37,47),(70,8,18),(70,37,47),(71,8,17),(71,38,47),(72,7,17),(72,38,47),(73,7,17),(73,38,47),(74,7,17),(74,38,47),(75,7,18),(75,37,47),(76,7,18),(76,37,47),(77,8,18),(77,37,47),(78,8,18),(78,39,45),(79,9,16),(79,39,45)
    ]
    mask: set[tuple[int, int]] = set(); add_spans(mask, rows_a)
    if variant == "B":
        # Independent silhouette blocking: extra outer curls, a more open
        # right guard, and a different foot spread. These are authored cells,
        # not pixels sampled from either underlay.
        for p in [(12,5),(12,6),(11,7),(11,8),(12,9),(13,10),(33,6),(34,7),(35,8),(35,9),(36,10),(36,11),(42,22),(43,23),(43,24),(44,25),(45,26),(45,27),(46,28),(6,73),(6,74),(6,75),(48,74),(48,75),(48,76)]: mask.add(p)
        for p in [(13,2),(14,2),(14,3),(15,3),(15,4),(16,4),(17,5),(18,5),(19,6),(20,6),(21,7),(22,7),(23,8),(24,8),(25,9),(26,9)]: mask.add(p)
        for p in [(10,69),(10,70),(10,71),(11,72),(46,69),(46,70),(47,71),(47,72)]: mask.add(p)
    return mask


def boundary(mask: set[tuple[int, int]]) -> set[tuple[int, int]]:
    return {(x, y) for x, y in mask if any((x + dx, y + dy) not in mask for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)))}


def set_cells(grid: dict[tuple[int, int], int], coords: list[tuple[int, int]], color: int, mask: set[tuple[int, int]]) -> None:
    for x, y in coords:
        if (x, y) in mask:
            grid[(x, y)] = color


def span(grid: dict[tuple[int, int], int], y: int, x1: int, x2: int, color: int, mask: set[tuple[int, int]]) -> None:
    set_cells(grid, [(x, y) for x in range(x1, x2 + 1)], color, mask)


def variant_mask_v03(variant: str) -> set[tuple[int, int]]:
    """Explicit component blocking with a raised diagonal guard.

    This is authored geometry, not a resize or a palette-derived mask. The
    negative spaces are intentional: they are the visual evidence that the
    forearms are separate from the ribcage at 1x.
    """
    mask: set[tuple[int, int]] = set()
    add_spans(mask, [
        (0,20,29),(1,18,32),(2,16,34),(3,15,35),(4,14,35),(5,13,34),
        (6,13,34),(7,14,35),(8,15,35),(9,17,35),(10,19,35),(11,21,35),
        (12,22,35),(13,23,35),(14,24,34),(15,24,33),(16,25,32),
        (17,26,31),(18,27,31),(19,27,31),(20,27,32),(21,26,35),
        (22,24,37),(23,23,37),(24,22,36),(25,22,35),(26,22,35),
        (27,23,35),(28,23,35),(29,24,35),(30,24,34),(31,24,34),
        (32,24,34),(33,24,34),(34,23,35),(35,23,35),(36,22,36),
        (37,21,35),(38,21,34),(39,20,34),(40,19,35),(41,17,38),
        (42,16,39),(43,15,40),(44,14,41),(45,14,42),(46,14,42),
        (47,14,42),(48,14,42),(49,13,42),(50,13,42),(51,13,41),
        (52,12,41),(53,12,40),(54,13,40),(55,14,39),(56,15,38),
        (57,16,37),(58,17,36),(59,18,35),(60,19,35),(61,20,34),
        (62,20,34),(63,20,34),(64,19,35),(65,19,35),(66,18,36),
        (67,18,36),(68,17,37),
        # left trouser and planted foot
        (69,9,24),(70,8,24),(71,8,23),(72,7,23),(73,7,22),(74,7,22),
        (75,7,21),(76,8,21),(77,8,20),(78,9,20),(79,10,18),
        # right trouser and planted foot
        (69,31,47),(70,31,47),(71,32,47),(72,32,47),(73,33,48),(74,33,48),
        (75,34,48),(76,34,48),(77,35,47),(78,36,46),(79,38,45),
    ])
    # Raised left fist, wrap and forearm.
    add_spans(mask, [
        (17,18,22),(18,17,22),(19,17,21),(20,18,22),(21,17,21),
        (22,16,20),(23,16,20),(24,17,21),(25,18,22),(26,19,23),
        (27,20,24),(28,21,25),(29,21,25),(30,20,24),(31,20,24),
    ])
    # Raised right fist, wrap and forearm, mirrored with a deliberate offset.
    add_spans(mask, [
        (17,37,41),(18,38,42),(19,38,42),(20,37,41),(21,37,41),
        (22,38,42),(23,39,43),(24,39,43),(25,38,42),(26,37,41),
        (27,36,40),(28,35,39),(29,34,38),(30,34,37),(31,34,36),
    ])
    if variant == "B":
        # B keeps the same gesture but changes the fist notch, curl rhythm,
        # sash tail and foot spread enough to be a genuine challenger.
        mask.update((x,y) for x,y in [(16,17),(16,18),(17,16),(18,16),(42,17),(43,18),(44,19),(45,20),(46,21)])
        mask.difference_update((x,y) for x,y in [(20,19),(39,19),(37,28),(38,28),(13,74),(14,74),(43,76),(44,76)])
    return mask


def lineart_grid(variant: str) -> tuple[list[int], dict[str, list[list[int]]]]:
    mask = variant_mask_v03(variant)
    outline = boundary(mask)
    grid = {p: 3 for p in mask}
    # Hair mass and front lock are dark structural blocks. The warm pixels
    # below are explicit curl groups, not palette-derived shading.
    hair_spans = [(0,21,22),(1,18,25),(2,16,26),(3,15,23),(4,14,22),(5,14,22),(6,15,23),(7,13,22),(8,15,23),(9,14,23),(10,14,22),(11,15,22),(12,16,21),(13,17,21),(14,18,21)]
    add_spans(set(), [])
    for y, x1, x2 in hair_spans: span(grid, y, x1, x2, 1, mask)
    for y, x1, x2 in [(7,30,32),(8,30,33),(9,31,33),(10,31,34),(11,31,34),(12,31,33),(13,30,32),(14,30,31),(15,29,30)]: span(grid, y, x1, x2, 1, mask)
    if variant == "B":
        for y, x1, x2 in [(5,12,14),(6,12,15),(7,11,15),(8,11,14),(9,12,15),(10,13,16)]: span(grid, y, x1, x2, 1, mask)

    # Face cluster: brow, eye/gaze, nose and jaw. B turns the gaze one cell
    # upward/right while retaining a readable contiguous eye cluster.
    if variant == "A":
        for y,x1,x2 in [(10,26,29),(12,27,29),(13,30,30),(14,30,30),(16,27,31)]: span(grid,y,x1,x2,1,mask)
        set_cells(grid, [(26,11),(27,11),(28,11),(29,12),(30,12)], 2, mask)
        set_cells(grid, [(27,10),(28,10),(29,10),(28,11),(29,11),(27,15),(28,15),(29,15)], 1, mask)
    else:
        for y,x1,x2 in [(10,25,28),(12,26,28),(13,29,30),(14,30,30),(16,27,31)]: span(grid,y,x1,x2,1,mask)
        set_cells(grid, [(25,11),(26,11),(27,12),(28,12),(29,13)], 2, mask)
        set_cells(grid, [(26,10),(27,10),(28,10),(27,11),(28,11),(26,15),(27,15),(28,15)], 1, mask)

    # Neck, shoulder, top hem and exposed abdomen planes.
    for y,x1,x2 in [(18,24,28),(19,21,31),(20,20,33),(21,20,34),(30,21,35),(31,20,36),(32,21,35),(33,23,33),(34,24,32),(35,25,31),(36,25,31),(37,26,30),(38,26,30)]: span(grid,y,x1,x2,2 if y >= 33 else 1,mask)
    span(grid, 31, 22, 34, 1, mask); span(grid, 32, 23, 33, 2, mask)
    for p in [(26,34),(27,34),(28,34),(29,34),(26,35),(29,35),(26,36),(29,36),(27,38),(28,38)]: set_cells(grid,[p],2,mask)

    # Four readable curl groups on the silhouette and internal texture groups.
    curl_groups = [[(15,5),(16,5),(16,6),(17,6)],[(14,8),(15,8),(15,9),(16,9)],[(18,2),(19,2),(19,3),(20,3)],[(21,1),(22,1),(22,2),(23,2)],[(23,6),(24,6),(24,7),(25,7)]]
    for group in curl_groups: set_cells(grid, group, 2, mask)
    if variant == "B":
        for group in [[(12,6),(13,6),(13,7),(14,7)],[(32,7),(33,7),(33,8),(34,8)]]: set_cells(grid, group, 2, mask)

    # Guard: wrap, fist and forearm are separate clusters on each side.
    left = [(18,20),(19,20),(20,21),(19,22),(20,22),(21,23),(20,24),(21,24),(22,25),(21,26),(22,27),(23,28),(22,29)]
    right = [(34,20),(35,20),(36,21),(35,22),(36,22),(37,23),(36,24),(37,24),(38,25),(37,26),(38,27),(39,28),(38,29)]
    set_cells(grid,left,1,mask); set_cells(grid,right,1,mask)
    for p in [(19,21),(20,23),(21,25),(22,26),(35,21),(36,23),(37,25),(38,26)]: set_cells(grid,[p],2,mask)
    if variant == "B":
        set_cells(grid, [(40,23),(41,24),(40,25),(41,26),(42,27)], 1, mask)
        set_cells(grid, [(17,24),(18,25),(19,26)], 2, mask)

    # Sash knot and falling tail.
    for y,x1,x2 in [(35,20,37),(36,21,38),(37,22,39),(38,23,40),(39,24,41),(40,25,41),(41,26,40),(42,27,39),(43,28,38),(44,29,37),(45,30,36),(46,31,35),(47,32,35)]: span(grid,y,x1,x2,1 if y in (35,36,40,41) else 2,mask)
    for p in [(31,36),(32,36),(33,36),(32,37),(33,37),(34,37),(33,38),(34,38)]: set_cells(grid,[p],1,mask)
    if variant == "B":
        for y,x1,x2 in [(40,38,42),(41,39,43),(42,40,44),(43,40,44),(44,39,43),(45,38,42),(46,37,41)]: span(grid,y,x1,x2,2,mask)

    # Trousers: waist, center separation and two continuous fold planes.
    span(grid, 42, 16, 40, 1, mask)
    for y in range(43, 67):
        if y % 2 == 1: span(grid, y, 25, 28, 1, mask)
    for y,x1,x2 in [(44,17,19),(48,16,20),(52,15,20),(56,13,19),(60,11,18),(64,10,16),(47,35,38),(51,36,40),(55,37,41),(59,38,42),(63,39,42),(67,40,41)]: span(grid,y,x1,x2,2,mask)
    if variant == "B":
        for y,x1,x2 in [(45,18,21),(50,16,21),(55,14,20),(60,12,19),(65,10,17),(46,34,38),(52,36,40),(58,38,42),(64,39,42)]: span(grid,y,x1,x2,1,mask)

    # Ankles and planted feet.
    for y,x1,x2 in [(68,10,18),(68,35,42),(69,9,17),(69,37,46),(70,9,17),(70,37,46),(71,8,16),(71,38,46),(72,8,16),(72,38,46),(73,8,17),(73,38,46),(74,8,17),(74,38,46),(75,8,18),(75,37,46),(76,8,18),(76,37,46),(77,9,18),(77,37,46),(78,10,18),(78,39,45),(79,10,16),(79,39,45)]: span(grid,y,x1,x2,2,mask)
    span(grid, 68, 10, 18, 1, mask); span(grid, 68, 35, 42, 1, mask)
    for y,x1,x2 in [(72,10,15),(74,40,45),(76,11,17),(77,39,45)]: span(grid,y,x1,x2,1,mask)

    for p in outline: grid[p] = 1
    if variant == "B":
        for p in [(27,12),(28,12),(29,13),(35,24),(40,25),(43,27),(33,37),(38,43),(17,65),(40,64)]: set_cells(grid,[p],2,mask)
    data = [grid.get((x,y), 0) for y in range(H) for x in range(W)]
    feature_regions = {
        "face": [[24, 8, 33, 17]], "hair": [[11, 0, 35, 15]], "guard": [[14, 18, 45, 31]], "hem": [[19, 29, 37, 33]], "sash": [[20, 35, 44, 47]], "feet": [[7, 67, 48, 79]]
    }
    return data, feature_regions


def save_indexed(data: list[int], path: Path) -> None:
    im = Image.new("P", (W, H), 0); im.putpalette([v for rgb in PALETTE for v in rgb] + [0] * (768 - 4 * 3)); im.putdata(data); im.save(path, "PNG", bits=4, transparency=0)


def diagnostic_assets(png: Path, out: Path, model: Path) -> dict:
    with Image.open(png) as source: rgba = source.convert("RGBA")
    for n in (2,3,8): rgba.resize((W*n,H*n), Image.Resampling.NEAREST).save(out/f"preview_nearest_{n}x.png")
    silhouette = Image.new("RGBA", (W,H), (0,0,0,255)); silhouette.putalpha(rgba.getchannel("A")); silhouette.save(out/"silhouette_black.png")
    for name, color in (("background_light",(224,224,208,255)),("background_dark",(18,24,34,255)),("background_chroma",(255,0,255,255))):
        bg=Image.new("RGBA",(W,H),color); bg.alpha_composite(rgba); bg.resize((W*8,H*8),Image.Resampling.NEAREST).convert("RGB").save(out/f"{name}.png")
    comp=Image.new("RGBA",(320,224),(18,24,34,255)); comp.alpha_composite(rgba,(132,72)); comp.convert("RGB").save(out/"composition_320x224.png")
    crops={"face":(22,7,35,19),"hair":(10,0,36,17),"guard":(12,17,47,33),"hem":(18,28,39,35),"sash":(18,33,46,49),"feet":(6,66,50,80)}
    for name, box in crops.items(): rgba.crop(box).resize(((box[2]-box[0])*8,(box[3]-box[1])*8),Image.Resampling.NEAREST).save(out/f"crop_{name}.png")
    # Diagnostic contour map: only authored structural ink (indices 1/2),
    # never the complete silhouette. This keeps the evidence about internal
    # drawing separate from the silhouette evidence.
    indexed = Image.open(png).convert("P")
    contour=Image.new("RGBA",(W,H),(0,0,0,0)); contour.putdata([(0,0,0,255) if p in (1,2) else (0,0,0,0) for p in indexed.getdata()]); contour.save(out/"internal_contour_map.png")
    # A diagnostic board may use text and a reference thumbnail; it is not an
    # art source and is not imported by resources.
    ref=Image.open(model).resize((384,256),Image.Resampling.NEAREST).convert("RGB")
    board=Image.new("RGB",(1200,700),(24,24,30)); board.paste(ref,(20,20)); board.paste(rgba.resize((448,640),Image.Resampling.NEAREST).convert("RGB"),(390,30)); ImageDraw.Draw(board).text((20,285),"model sheet v02",fill=(255,255,255)); ImageDraw.Draw(board).text((390,675),"lineart candidate",fill=(255,255,255)); board.save(out/"overlay_model_sheet_diagnostic.png")
    return {"preview_nearest": [f"preview_nearest_{n}x.png" for n in (2,3,8)], "silhouette":"silhouette_black.png", "backgrounds":[f"background_{n}.png" for n in ("light","dark","chroma")], "composition":"composition_320x224.png", "crops":[f"crop_{n}.png" for n in crops], "contour":"internal_contour_map.png", "overlay":"overlay_model_sheet_diagnostic.png"}


def main() -> None:
    lab=Path(__file__).resolve().parent.parent; model=lab/MODEL
    out=lab/"native_lineart_blocking_v03"; out.mkdir(exist_ok=True)
    underlay_meta={}
    for label,(rel,expected) in UNDERLAYS.items():
        p=lab/rel
        if sha(p)!=expected: raise SystemExit(f"underlay SHA mismatch: {label}")
        underlay_meta[label]={"path":rel,"sha256":expected,"role":"guide_only_not_pixel_source"}
    if sha(model)!=MODEL_SHA: raise SystemExit("model sheet SHA mismatch")
    candidates={}
    for variant in ("A_underlay_im_lanczos3","B_underlay_im_mitchell_netravali"):
        code="A" if variant.startswith("A") else "B"; folder=out/code; folder.mkdir(exist_ok=True)
        data, regions=lineart_grid(code); asset_id=f"taina_56x80_native_lineart_blocking_{code.lower()}_v03"; png=folder/f"{asset_id}.png"; save_indexed(data,png); diagnostic_assets(png,folder,model)
        identity_report={"asset_id":asset_id,"scale":"56x80","authority":{"file":MODEL,"sha256":MODEL_SHA},"observed_checks":{"athletic_silhouette_1x":"candidate_evidence_required","eye_and_gaze":"candidate_evidence_required","hair_face_separation":"candidate_evidence_required","asymmetric_curly_hair_front_lock":"candidate_evidence_required","two_separate_arms":"candidate_evidence_required","diagonal_guard":"candidate_evidence_required","legible_fists":"candidate_evidence_required","top_hem":"candidate_evidence_required","exposed_abdomen":"candidate_evidence_required","wraps":"candidate_evidence_required","sash_knot_and_fall":"candidate_evidence_required","wide_trousers_leg_separation":"candidate_evidence_required","planted_feet":"candidate_evidence_required","pivot_and_ground_line":"candidate_evidence_required"},"review_rule":"human_visual_readability_is_not replaced by technical counters","status":"pending_human_visual_review"}
        (folder/f"{asset_id}_identity_report.json").write_text(json.dumps(identity_report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        report={"schema_version":"taina_native_lineart_validation.v1","asset_id":asset_id,"sha256":sha(png),"scale":"56x80","variant":code,"method":"agent_authored_native_lineart_blocking","acceptance_status":"visual_lab_control","source_kind":"procedural_composed_from_authored","source_file_unchanged":True,"output_pixels_reassigned":sum(1 for x in data if x != 0),"identity_authority":{"file":MODEL,"sha256":MODEL_SHA},"underlay_guide":underlay_meta[variant],"forbidden_sources":["material_palette_reseed_v01","hybrid_cleanup_primary_im_lanczos3_rework_v05","material_owner_shade_annotation_v01"],"features_required":["athletic_silhouette_1x","eye_and_gaze","hair_face_separation","asymmetric_curly_hair_front_lock","two_separate_arms","diagonal_guard","legible_fists","top_hem","exposed_abdomen","wraps","sash_knot_and_fall","wide_trousers_leg_separation","planted_feet","pivot_and_ground_line"],"feature_regions":regions,"identity_report":f"{asset_id}_identity_report.json","pixel_evidence":diagnostic_assets(png,folder,model),"pixel_contract":{"width":W,"height":H,"mode":"P","bit_depth":4,"index0_transparent":True,"visible_colors":len(set(x for x in data if x != 0)),"grid":"8x8"},"human_visual_gate":"pending_human_decision","visual_status":"structural_lineart_candidate_not_yet_human_passed","promotable":False,"allowed_as_pixel_source":False,"res_promotion":False,"animation_authorization":False,"rom_authorization":False,"ready_for_aaa":False}
        (folder/f"{asset_id}_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); candidates[code]={"asset_id":asset_id,"path":str(png),"sha256":sha(png),"report":f"{code}/{asset_id}_report.json","identity_report":f"{code}/{asset_id}_identity_report.json"}
    a=Image.open(out/"A"/f"{candidates['A']['asset_id']}.png").convert("P"); b=Image.open(out/"B"/f"{candidates['B']['asset_id']}.png").convert("P"); ap=list(a.getdata()); bp=list(b.getdata()); diff=[i for i,(x,y) in enumerate(zip(ap,bp)) if x!=y]; visible=sum(1 for x in ap if x or False)
    region_boxes={"face":(22,7,35,19),"hair":(10,0,36,17),"guard":(12,17,47,33),"hem":(18,28,39,35),"sash":(18,33,46,49),"feet":(6,66,50,80)}; affected={n:sum(1 for i in diff if box[0]<=i%W<box[2] and box[1]<=i//W<box[3]) for n,box in region_boxes.items()}; affected={k:v for k,v in affected.items() if v}
    manifest={"schema_version":"taina_native_lineart_blocking_manifest.v1","stage":"native_lineart_blocking_v03","iteration_reason":"v01 and v02 retained a block-mass torso; v03 redraws the authored structural mask with two raised fists, diagonal forearms and explicit ribcage negative space","identity_authority":{"file":MODEL,"sha256":MODEL_SHA},"underlays":underlay_meta,"candidates":candidates,"source_file_unchanged":True,"forbidden_pixel_sources":["BASIC","ELITE","v02_regressiva","G2","RGB_diagnostic_maps","v05"],"comparison":{"pixels_different":len(diff),"visible_pixel_denominator":visible,"difference_ratio":len(diff)/visible if visible else 0,"near_duplicate":(len(diff)/visible if visible else 0)<0.02,"affected_regions":affected,"meaningful_visual_alternatives":len(affected)>=3,"intended_gain":"recover internal drawing, identity, gaze, guard separation and volume before color"},"not_attempted":["material_color_blocking","shadow_or_highlight_authoring","palette_reseed","animation","res_promotion","sgdk_integration","rom_or_emulator_validation"],"human_gate_status":"pending_human_decision","decision_required":"select_one_structurally_valid_lineart_candidate","res_promotion":False,"animation_authorization":False,"rom_authorization":False,"visual_pass":False,"ready_for_aaa":False}
    (out/"native_lineart_blocking_manifest_v01.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    board=Image.new("RGB",(960,420),(18,24,34)); draw=ImageDraw.Draw(board)
    for i,(code,title) in enumerate((("A","A — im_lanczos3"),("B","B — im_mitchell_netravali"))):
        p=out/code/f"{candidates[code]['asset_id']}.png"; im=Image.open(p).convert("RGBA"); board.paste(im.resize((280,400),Image.Resampling.NEAREST).convert("RGB"),(80+i*440,10)); draw.text((80+i*440,400),title,fill=(255,255,255))
    board.save(out/"native_lineart_shootout_board.png")
    print(json.dumps({"status":"lineart_blocking_candidates_written","manifest":str(out/"native_lineart_blocking_manifest_v01.json"),"candidates":candidates,"comparison":manifest["comparison"]},ensure_ascii=False))


if __name__=="__main__": main()
