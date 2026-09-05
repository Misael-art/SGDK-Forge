#!/usr/bin/env python3
import argparse, hashlib, json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

INC="hybrid_cleanup_primary_im_lanczos3_v01"
REWORK="hybrid_cleanup_primary_im_lanczos3_rework_v01"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def font(size):
    try: return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size)
    except OSError: return ImageFont.load_default()
def thumb(p,size,bg=(16,18,26)):
    im=Image.open(p).convert('RGBA'); im.thumbnail(size,Image.Resampling.NEAREST); out=Image.new('RGBA',size,bg+(255,)); out.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2)); return out
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--lab-root',type=Path,required=True); a=ap.parse_args(); lab=a.lab_root.resolve(); base=lab/'hybrid_cleanup_shootout'/INC/(INC+'.png'); out=lab/'localized_native_cleanup'/REWORK; re=out/(REWORK+'.png')
    board=Image.new('RGBA',(1080,760),(10,12,18,255)); d=ImageDraw.Draw(board); d.text((24,18),'TAINA — LOCALIZED NATIVE CLEANUP / HUMAN GATE',fill=(245,240,220),font=font(18)); d.text((24,48),'Selected incumbent with localized grid edits; no resize, no res promotion.',fill=(180,190,205),font=font(12))
    for i,(label,p,note) in enumerate([('INCUMBENT / selected',base,'before: baked ground-shadow strip'),('REWORK / localized',re,'after: strip removed; orphan edge pixel removed')]):
        x=24+i*520; d.rectangle((x,82,x+480,650),outline=(72,82,104),width=1); d.text((x+12,94),label,fill=(240,235,215),font=font(13)); board.alpha_composite(thumb(out/'preview_nearest_8x.png' if p==re else lab/'hybrid_cleanup_shootout'/INC/'preview_nearest_8x.png',(440,500)),(x+20,126)); d.text((x+12,600),note,fill=(205,210,220),font=font(12)); d.text((x+12,625),'56x80 / technical candidate / human pending',fill=(225,180,110),font=font(12))
    board.convert('RGB').save(lab/'localized_native_cleanup_comparison_board.png')
    sys.path.insert(0,str(lab.parents[2]/'tools/sgdk_wrapper'))
    from forge_art import pixel_contract
    v=pixel_contract.validate_png(re,'transparent0')
    report={"schema_version":"localized_native_cleanup_validation.v1","asset_id":REWORK,"path":str(re.relative_to(lab)),"sha256":sha(re),"pixel_contract":{"status":v['status'],"blocking":v['blocking'],"content_sha256":v['content_sha256'],"visible_colors":v['visible_colors'],"plte_entries":v['plte_entries'],"bit_depth":v['bit_depth'],"dimensions":[v['width'],v['height']],"index0_role":"transparent0"},"human_gate_status":"pending_human_decision","visual_status":"not_yet_human_passed","res_promotion":False,"animation_authorization":False,"rom_authorization":False,"notes":["localized cleanup only","ground shadow between feet removed","orphan sash-edge pixel removed","no automatic winner"]}
    (out/'localized_native_cleanup_validation_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (lab/'human_gate_request_localized_cleanup.md').write_text('# TAINA — localized cleanup human gate\n\nSelecionado: `hybrid_cleanup_primary_im_lanczos3_v01`\n\nRework: `hybrid_cleanup_primary_im_lanczos3_rework_v01`\n\nRework SHA-256: `'+sha(re)+'`\n\nEscala: `56x80`\n\nEscopo aprovado: `localized_native_cleanup_only`\n\nVerificar em 1×: rosto/olho, guarda diagonal, cabelo assimétrico, separação top/pele, wraps, sash, pernas, pés e ausência de sombra de chão assada.\n\nResposta aceita:\n\n```text\ndecision=approve_localized_native_cleanup\nasset_id=hybrid_cleanup_primary_im_lanczos3_rework_v01\nsha256='+sha(re)+'\nscale=56x80\n```\n\nou:\n\n```text\ndecision=reject_localized_native_cleanup\nreason=<motivo observável>\n```\n\nNada neste gate libera `res/`, animação, runtime, ROM, `visual_pass` ou AAA.\n',encoding='utf-8')
    print(json.dumps({"status":"completed","board":"localized_native_cleanup_comparison_board.png","rework_sha256":sha(re),"pixel_status":v['status']},ensure_ascii=False))
if __name__=='__main__': main()
