#!/usr/bin/env python3
"""Reduce resident tile count by reusing nearest source tiles, at native pixels.

Uses only complete tiles from the source: no 4x4 downsample/upscale.
This is a lossy prototype translation, not a native-art promotion.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'rascunho/showdown_native_crop_preview.png'


def convert(budget, output):
    output=output.resolve()
    src=Image.open(SOURCE).convert('RGB').resize((512,256),Image.Resampling.NEAREST)
    q=src.quantize(colors=14,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    raw=q.getpalette()
    pal=np.array(raw+[0]*(768-len(raw)),dtype=np.float32).reshape(256,3)
    pal=np.clip(np.round(pal/34)*34,0,238)
    # VDP color zero is transparent even on BG_B. Reserve it: otherwise
    # the lightest ground color becomes the global (HUD-black) backdrop.
    pal[1:15] = pal[:14].copy()
    pal[0] = 0
    pixels=np.asarray(q,dtype=np.uint8)+1
    tiles=pixels.reshape(32,8,64,8).transpose(0,2,1,3).reshape(-1,64)
    unique,inverse,counts=np.unique(tiles,axis=0,return_inverse=True,return_counts=True)
    vectors=pal[unique].reshape(len(unique),-1)
    # Farthest-first representatives weighted by occurrence count. Each
    # representative remains a verbatim 8x8 tile of the quantized source.
    nearest=np.full(len(unique),np.inf)
    assignment=np.zeros(len(unique),dtype=np.int32)
    selected=[]
    idx=int(counts.argmax())
    for _ in range(min(budget,len(unique))):
        selected.append(idx)
        distance=np.sum((vectors-vectors[idx])**2,axis=1)
        mask=distance<nearest
        nearest[mask]=distance[mask]
        assignment[mask]=idx
        idx=int(np.argmax(nearest*np.sqrt(counts)))
    mapped=unique[assignment[inverse]]
    image_pixels=mapped.reshape(32,64,8,8).transpose(0,2,1,3).reshape(256,512)
    out=Image.fromarray(image_pixels.astype(np.uint8)).convert('P')
    out.putpalette(pal.astype(np.uint8).reshape(-1).tolist())
    output.parent.mkdir(parents=True,exist_ok=True)
    out.save(output)
    result={'scope':'static_asset_budget','source':str(SOURCE.relative_to(ROOT)),
            'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'output':str(output.relative_to(ROOT)),'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
            'unique_source_tiles':len(unique),'tile_budget':budget,'unique_output_tiles':len(np.unique(mapped,axis=0)),
            'pixel_block_size':1,'transparent_index':0,'opaque_indices':[1,14],
            'mean_squared_rgb_error':float(np.average(nearest,weights=counts)/192),
            'method':'weighted farthest source-tile representatives, nearest replacement',
            'claim_ceiling':'prototype_compare_flat','runtime_budget':'not_measured'}
    output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--budget',type=int,default=720)
    parser.add_argument('--output',type=Path,default=ROOT/'rascunho/showdown_tile_budget_720.png')
    args=parser.parse_args()
    if not 1<=args.budget<=2048: parser.error('budget must be 1..2048')
    convert(args.budget,args.output)
