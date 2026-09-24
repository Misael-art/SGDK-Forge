import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def thumb(p, size, background=(22,24,32)):
    im=Image.open(p).convert("RGBA"); im.thumbnail(size,Image.Resampling.NEAREST); out=Image.new("RGBA",size,background+(255,)); out.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2)); return out
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--lab-root",type=Path,required=True); args=ap.parse_args(); lab=args.lab_root.resolve()
    try: font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",14); small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",11)
    except OSError: font=small=ImageFont.load_default()
    matrix=json.loads((lab/"route_matrix.json").read_text()); routes=[r for r in matrix["routes"] if r["status"]=="passed"]
    board=Image.new("RGBA",(1280,960),(12,14,22,255)); d=ImageDraw.Draw(board); d.text((20,14),"TAÍNA RESAMPLING ROUTE LAB — STAGE 1 RAW GEOMETRY",fill=(245,240,220),font=font); d.text((20,40),"All cells are mechanical probes; no route is a native candidate.",fill=(180,190,205),font=small)
    for i,r in enumerate(routes):
        x=20+(i%10)*124; y=70+(i//10)*430; d.rectangle((x,y,x+112,y+400),outline=(72,82,104),width=1); d.text((x+5,y+5),r["route_id"],fill=(240,235,215),font=small); p=lab/r["output"]["path"]; board.alpha_composite(thumb(p,(100,145)),(x+6,y+28)); p8=lab/r["output"]["path"].replace("raw_rgba_56x80.png","preview_nearest_8x.png"); board.alpha_composite(thumb(p8,(100,210)),(x+6,y+184)); d.text((x+5,y+380),f"partial={r['metrics'].get('partial_alpha_pixels',0)}",fill=(180,190,205),font=small)
    board.convert("RGB").save(lab/"route_exploration_board.png")
    final=Image.new("RGBA",(1440,920),(12,14,22,255)); d=ImageDraw.Draw(final); d.text((20,14),"TAÍNA — CURATED ROUTE REVIEW / HUMAN GATE",fill=(245,240,220),font=font); d.text((20,40),"identity source, directional source, rejected v04, palette probes and two guide candidates",fill=(180,190,205),font=small)
    cards=[("MODEL SHEET / identity",lab/"inputs/model_sheet_v02.png"),("56×80 source / direction",lab/"inputs/approved_direction_56x80.png"),("v04 / rejected negative",lab/"inputs/v04_negative_evidence.png")]
    for i,(label,p) in enumerate(cards):
        x=20+i*470; d.rectangle((x,70,x+440,360),outline=(72,82,104),width=1); d.text((x+8,78),label,fill=(240,235,215),font=small); final.alpha_composite(thumb(p,(420,250)),(x+10,100))
    d.text((20,390),"FOUR PALETTE SURVIVORS",fill=(245,240,220),font=font)
    pal=["im_nearest","im_box_area","pil_lanczos","cv_area"]
    for i,rid in enumerate(pal):
        x=20+i*205; p=lab/"palette_probe_reports"/rid/"technical_palette_probe_56x80.png"; d.rectangle((x,420,x+185,660),outline=(72,82,104),width=1); d.text((x+6,426),rid,fill=(240,235,215),font=small); final.alpha_composite(thumb(p,(165,210)),(x+10,450))
    d.text((20,690),"TWO NATIVE REWORK GUIDES — NOT v05 / NOT final",fill=(245,240,220),font=font)
    for i,rid in enumerate(["native_guide_candidate_route_a_v01","native_guide_candidate_route_b_v01"]):
        x=20+i*260; p=lab/"rework_candidates"/rid/(rid+".png"); d.rectangle((x,720,x+235,900),outline=(72,82,104),width=1); d.text((x+6,726),rid,fill=(240,235,215),font=small); final.alpha_composite(thumb(p,(210,145)),(x+12,750))
    final.convert("RGB").save(lab/"human_gate_request_board.png")
    rows=[]
    for r in matrix["routes"]: rows.append(f"| {r['route_id']} | {r['tool']} | {r['algorithm']} | {r['status']} | {r['output']['sha256'] or 'none'} |")
    md="# Route comparison matrix\n\nStage 1 is geometry-only and has claim ceiling `mechanical_geometry_probe`. No automatic winner is declared.\n\n| route | tool | algorithm | status | raw SHA-256 |\n|---|---|---|---|---|\n"+"\n".join(rows)+"\n\nGIMP batch attempts timed out without a deterministic export and are `skipped`; they do not block the matrix.\n"
    (lab/"route_comparison_matrix.md").write_text(md,encoding="utf-8")
    repeat=json.loads((lab/"route_matrix_repeat.json").read_text()); pairs=[]; identical=True
    for a,b in zip(matrix["routes"],repeat["routes"]):
        same=a["output"]["sha256"]==b["output"]["sha256"]; identical &= same; pairs.append({"route_id":a["route_id"],"first_sha256":a["output"]["sha256"],"repeat_sha256":b["output"]["sha256"],"identical":same})
    (lab/"reproducibility_report.json").write_text(json.dumps({"schema_version":"route_reproducibility.v1","same_canonical_input":True,"all_output_hashes_identical":identical,"routes":pairs,"status":"passed" if identical else "failed"},indent=2)+"\n",encoding="utf-8")
    (lab/"learning_ledger.json").write_text(json.dumps({"schema_version":"resampling_lab_learning_ledger.v1","observations":["nearest preserves hard silhouette but exposes source detail collapse","area/box suppresses ringing while softening small facial and hand clusters","bicubic/lanczos family can retain local contrast but introduces partial-alpha edge behavior requiring matte review","no filter can establish identity when the source pose and native topology are not explicitly reauthored"],"negative_learning":["v04 native redraw was rejected for block mass and signature loss","GIMP route without deterministic export bridge cannot be called executed"],"promotion_proposal":"none_until_reusable_non_taina_harness_and_human_approval","status":"lab_evidence_only"},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (lab/"memory_bank.md").write_text("# TAINA resampling route lab memory\n\n- Identity is bound to the copied model sheet SHA; the 56x80 source is directional only.\n- Stage 1 executed 20 deterministic ImageMagick/Pillow/OpenCV geometry routes and skipped 5 GIMP routes after batch timeout/no export.\n- Stage 2 selected four probes for the same manual semantic palette; none is a native candidate.\n- Stage 3 contains two native-grid guide candidates only; they are not v05, not final and not eligible for res/.\n- Human rejection is recorded exactly as `rejected_requires_route_lab` for v04, SHA-256 `0f0c758bd50fd41b028ad44f04a3c48e48faf1859f2b4e9769ca68621733800e`, in `contracts/v04_route_lab_rejection.json`; normal TAÍNA production is paused until this lab gate.\n",encoding="utf-8")
    print(json.dumps({"raw_board":str((lab/"route_exploration_board.png").relative_to(lab)),"human_board":str((lab/"human_gate_request_board.png").relative_to(lab)),"reproducible":identical}))
if __name__=="__main__": main()
