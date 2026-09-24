#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def font(size):
    try: return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size)
    except OSError: return ImageFont.load_default()

def thumb(path,size,bg):
    im=Image.open(path).convert('RGBA'); im.thumbnail(size,Image.Resampling.NEAREST)
    out=Image.new('RGBA',size,bg+(255,)); out.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2)); return out

def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('--lab-root',type=Path,required=True); args=ap.parse_args(); lab=args.lab_root.resolve()
    parent=lab/'localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v03'; current=lab/'localized_native_cleanup/hybrid_cleanup_primary_im_lanczos3_rework_v04'
    board=Image.new('RGBA',(1640,760),(10,12,18,255)); d=ImageDraw.Draw(board)
    d.text((24,18),'TAINA — PRIMARY CHECKPOINT → STRICT LOCALIZED v04',fill=(245,240,220),font=font(18))
    d.text((24,48),'v03 congelada como melhor base atual; v04 sem resize/filtro/remapeamento global; decisão humana pendente.',fill=(180,190,205),font=font(12))
    entries=[('v03 / CHECKPOINT INCUMBENT',parent/'preview_nearest_8x.png','33 patches efetivos; checkpoint intermediário'),('v04 / LOCALIZED REWORK',current/'preview_nearest_8x.png','patches adicionais em rosto, cabelo, guarda, abdômen, sash e calças'),('v04 / SILHOUETTE',current/'silhouette_binary.png','teste de massa externa e contato')]
    for i,(label,path,note) in enumerate(entries):
        x=24+i*536; d.rectangle((x,82,x+512,700),outline=(72,82,104),width=1); d.text((x+14,96),label,fill=(240,235,215),font=font(13)); board.alpha_composite(thumb(path,(480,560),(235,235,235) if i==0 else (24,26,32)),(x+16,124)); d.text((x+14,644),note,fill=(205,210,220),font=font(11)); d.text((x+14,668),'56x80 • technical pass • visual rework • human pending',fill=(225,180,110),font=font(11))
    board.convert('RGB').save(lab/'localized_native_cleanup_v04_comparison_board.png')

if __name__=='__main__': main()
