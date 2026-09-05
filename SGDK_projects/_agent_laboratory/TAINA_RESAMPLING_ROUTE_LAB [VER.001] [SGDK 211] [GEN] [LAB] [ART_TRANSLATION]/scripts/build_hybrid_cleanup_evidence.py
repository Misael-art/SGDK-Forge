#!/usr/bin/env python3
"""Build the human comparison board and validation reports for the shootout."""
import argparse, hashlib, json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

NAMES=[
    "hybrid_cleanup_primary_im_lanczos3_v01",
    "hybrid_cleanup_challenger_im_mitchell_netravali_v01",
    "hybrid_cleanup_control_im_catmull_rom_v01",
]
LABELS=["PRIMARY / im_lanczos3","CHALLENGER / im_mitchell_netravali","CONTROL / im_catmull_rom"]
OBSERVATIONS={
    NAMES[0]: "mais contraste local; exige vigilancia de halos e microjaggies",
    NAMES[1]: "contorno mais calmo; perde parte da separacao fina em mao/sash",
    NAMES[2]: "controle intermediario; menos contraste e menor ruido de borda",
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load_font(size):
    try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",size)
    except OSError: return ImageFont.load_default()
def thumb(p, size, bg=(18,20,28)):
    im=Image.open(p).convert("RGBA"); im.thumbnail(size,Image.Resampling.NEAREST); out=Image.new("RGBA",size,bg+(255,)); out.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2)); return out
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--lab-root",type=Path,required=True); a=ap.parse_args(); lab=a.lab_root.resolve(); root=lab/"hybrid_cleanup_shootout"
    font,small=load_font(18),load_font(12)
    board=Image.new("RGBA",(1440,900),(10,12,18,255)); d=ImageDraw.Draw(board)
    d.text((24,18),"TAINA — HYBRID CLEANUP SHOOTOUT / HUMAN GATE",fill=(245,240,220),font=font)
    d.text((24,48),"Bases approved by exact route SHA; pixel survival allowed, blind promotion forbidden.",fill=(180,190,205),font=small)
    rows=[]
    for i,name in enumerate(NAMES):
        x=24+i*470; y=82; out=root/name; p=out/(name+".png")
        d.rectangle((x,y,x+440,y+570),outline=(72,82,104),width=1); d.text((x+10,y+10),LABELS[i],fill=(240,235,215),font=small)
        board.alpha_composite(thumb(out/"preview_nearest_8x.png",(410,430)),(x+15,y+38))
        d.text((x+10,y+480),OBSERVATIONS[name],fill=(195,205,215),font=small)
        d.text((x+10,y+506),"technical_candidate / human pending",fill=(225,180,110),font=small)
        rows.append({"asset_id":name,"path":str(p.relative_to(lab)),"sha256":sha(p),"route_id":json.loads((out/"hybrid_cleanup_report.json").read_text())["route_id"],"observation":OBSERVATIONS[name]})
    d.text((24,685),"DIRECT 1x REFERENCES / LIGHT-DARK-CHROMA AND REGION CROPS ARE IN EACH CANDIDATE FOLDER",fill=(245,240,220),font=small)
    for i,name in enumerate(NAMES):
        x=24+i*470; p=root/name/"background_light.png"; board.alpha_composite(thumb(p,(135,175),(238,238,230)),(x,710)); d.text((x+150,724),"light / 1x",fill=(215,220,230),font=small); d.text((x+150,748),"face + guard + sash + feet",fill=(180,190,205),font=small)
    board.convert("RGB").save(lab/"hybrid_cleanup_shootout_board.png")
    validation=[]
    sys.path.insert(0,str(lab.parents[2]/"tools/sgdk_wrapper"))
    try:
        from forge_art import pixel_contract
        for name in NAMES:
            p=root/name/(name+".png"); v=pixel_contract.validate_png(p,"transparent0"); validation.append({"asset_id":name,"path":str(p.relative_to(lab)),"sha256":sha(p),"status":v["status"],"blocking":v["blocking"],"content_sha256":v["content_sha256"],"visible_colors":v["visible_colors"],"dimensions":[v["width"],v["height"]],"plte_entries":v["plte_entries"],"bit_depth":v["bit_depth"],"index0_role":"transparent0"})
    except Exception as e:
        validation.append({"status":"validator_error","error":str(e)})
    (lab/"hybrid_cleanup_validation_report.json").write_text(json.dumps({"schema_version":"hybrid_cleanup_validation.v1","status":"technical_validation_only","candidates":validation,"human_gate_status":"pending_human_decision","promotion":{"res":False,"animation":False,"runtime":False,"rom":False,"aaa":False}},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (lab/"hybrid_cleanup_shootout_report.json").write_text(json.dumps({"schema_version":"hybrid_cleanup_shootout_report.v1","decision":"approve_hybrid_cleanup_shootout","scale":"56x80","bases":{"primary":{"route_id":"im_lanczos3","sha256":"933caee8829970d0f8877712396b19b57e5843ef73481aceb047cf338cde72be"},"challenger":{"route_id":"im_mitchell_netravali","sha256":"ee524888bd0be4e146a3236a9480565772b8fa8e752818bf2c9717bf702b17b5"},"control":{"route_id":"im_catmull_rom","sha256":"169426ebbf40eb01631154610cd73fff959afde8540dfa5943c3528225b20cd5"}},"observations":OBSERVATIONS,"no_numeric_score":True,"no_automatic_winner":True,"candidates":rows,"claim_ceiling":"hybrid_cleanup_candidate","human_gate_status":"pending_human_decision","res_promotion":False},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    md="# Hybrid cleanup shootout — human gate\n\nDecision received: `approve_hybrid_cleanup_shootout`; scale locked at `56x80`. Base pixels may survive, but blind pixel promotion is forbidden.\n\nNo numeric score or automatic winner is declared.\n\n| candidate | base route | candidate SHA-256 | observable tradeoff |\n|---|---|---|---|\n"+"\n".join(f"| {r['asset_id']} | {r['route_id']} | {r['sha256']} | {r['observation']} |" for r in rows)+"\n\nAll candidates are staging-only `technical_candidate` outputs. Review 1x, nearest 8x, light/dark/chroma and the face/guard/sash/feet crops before choosing.\n"
    (lab/"hybrid_cleanup_comparison.md").write_text(md,encoding="utf-8")
    (lab/"human_gate_request_hybrid_cleanup.md").write_text("# TAINA hybrid cleanup — decisão humana\n\n`decision=approve_hybrid_cleanup_shootout`\n\n`scale=56x80`\n\n## Gate\n\nEscolher uma candidata somente se rosto/olho, guarda diagonal, cabelo assimétrico, top/abdômen, wraps, sash, pernas e pés continuarem legíveis em 1×. Comparar perdas de contorno, halos e separação de materiais; não somar score.\n\nRespostas aceitas:\n\n```text\ndecision=approve_hybrid_cleanup_candidate\nasset_id=<id exato>\nsha256=<SHA exato>\nscale=56x80\n```\n\nou:\n\n```text\ndecision=reject_hybrid_cleanup_shootout\nreason=<motivo observável>\n```\n\nEsta decisão não libera `res/`, animação, runtime, ROM, `visual_pass` ou AAA.\n",encoding="utf-8")
    print(json.dumps({"status":"completed","board":"hybrid_cleanup_shootout_board.png","candidates":len(rows),"validation_status":validation[0]["status"] if validation else "none"},ensure_ascii=False))
if __name__=="__main__": main()
