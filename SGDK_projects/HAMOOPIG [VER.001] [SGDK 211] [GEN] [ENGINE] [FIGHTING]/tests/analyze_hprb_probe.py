#!/usr/bin/env python3
"""Decode HAMOOPIG's diagnostic HPRB SRAM block.

The probe samples the DMA queue before VBlank and the active SGDK sprite list;
it is evidence for the captured ROM only, not a synthetic performance claim.
"""
import argparse, hashlib, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('sram',type=Path); ap.add_argument('--rom',type=Path)
    ap.add_argument('--out',type=Path); a=ap.parse_args()
    b=a.sram.read_bytes(); off=0x500
    if b[off:off+4]!=b'HPRB': raise SystemExit('HPRB signature missing')
    schema=int.from_bytes(b[off+4:off+6],'big'); size=int.from_bytes(b[off+6:off+8],'big')
    pre_sprite_dma = sprite_dma_delta = None
    if schema==1 and size==24:
        vals=[int.from_bytes(b[off+8+i*2:off+10+i*2],'big') for i in range(8)]
        frame=(vals[0]<<16)|vals[1]; peak_dma_frame=None; peak_scanline_frame=None
        dma,active,vdp,scanline,samples,scene=vals[2:]
    elif schema in (2,3,4,5) and size in (32,36,46,50):
        words = 12 if size == 32 else (14 if size == 36 else (19 if size == 46 else 21))
        vals=[int.from_bytes(b[off+8+i*2:off+10+i*2],'big') for i in range(words)]
        frame=(vals[0]<<16)|vals[1]; peak_dma_frame=(vals[2]<<16)|vals[3]
        peak_scanline_frame=(vals[4]<<16)|vals[5]
        dma,active,vdp,scanline,samples,scene=vals[6:12]
        pre_sprite_dma = vals[12] if len(vals) > 12 else None
        sprite_dma_delta = vals[13] if len(vals) > 13 else None
        stage_dma = vals[14:19] if len(vals) >= 19 else None
        peak_pre_at_max = vals[19] if len(vals) >= 21 else None
        peak_sprite_at_max = vals[20] if len(vals) >= 21 else None
    else: raise SystemExit('unsupported HPRB schema')
    # SGDK 2.11 H40 VBlank envelope from dma.h: NTSC ~7.6 KiB, PAL ~17 KiB.
    region='PAL' if (scene & 0x8000) else 'NTSC'
    dma_limit=17*1024 if region=='PAL' else int(7.6*1024)
    result={'schema':schema,'frame':frame,'peak_dma_frame':peak_dma_frame,
            'peak_scanline_frame':peak_scanline_frame,'max_dma_bytes':dma,
            'max_active_sprites':active,'max_vdp_sprites':vdp,
            'max_sprites_per_scanline':scanline,'samples':samples,
            'max_pre_sprite_dma_bytes':pre_sprite_dma,
            'max_sprite_dma_delta_bytes':sprite_dma_delta,
            'max_stage_dma_delta_bytes':stage_dma,
            'stage_names':['clock','health_hud','message_hud','animation','fsm'],
            'peak_pre_sprite_dma_at_max_bytes':peak_pre_at_max,
            'peak_sprite_dma_delta_at_max_bytes':peak_sprite_at_max,
            'last_scene':scene & 0x7FFF,'region_inference':region,
            'limits':{'dma_bytes':dma_limit,'vdp_sprite_links':80,'sprites_per_scanline':20},
            'dma_status':'over_budget' if dma>dma_limit else 'within_nominal',
            'sprite_status':'within_nominal' if vdp<=80 and scanline<=20 else 'over_budget',
            'decision':'cabe com recuo' if dma>dma_limit else 'cabe',
            'evidence_scope':'HPRB SRAM snapshot from BlastEm; same ROM hash required'}
    if a.rom: result['rom_sha256']=hashlib.sha256(a.rom.read_bytes()).hexdigest()
    out=a.out or a.sram.with_name('hprb_probe_report.json'); out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
