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


def convert(budget, output, refine=0, source=SOURCE, crop=None):
    output=output.resolve()
    source=Path(source).resolve()
    src=Image.open(source).convert('RGB')
    if crop is not None:
        src=src.crop(crop)
    src=src.resize((512,256),Image.Resampling.NEAREST)
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
    method='weighted farthest source-tile representatives, nearest replacement'
    if refine > 0 and selected:
        # Lloyd-style medoid refinement.  The representatives remain source
        # tiles, but the centroid step reduces the broad colour/texture error
        # that farthest-first alone leaves in large repeated regions.
        medoids=np.asarray(selected,dtype=np.int32)
        vector_norm=np.sum(vectors*vectors,axis=1)
        for _ in range(refine):
            medoid_vectors=vectors[medoids]
            distances=(vector_norm[:,None] + np.sum(medoid_vectors*medoid_vectors,axis=1)[None,:]
                       - 2.0*np.matmul(vectors,medoid_vectors.T))
            assignment=np.argmin(distances,axis=1).astype(np.int32)
            next_medoids=medoids.copy()
            used=set()
            for cluster in range(len(medoids)):
                members=np.flatnonzero(assignment==cluster)
                if len(members)==0:
                    continue
                weights=counts[members].astype(np.float32)
                centroid=np.average(vectors[members],axis=0,weights=weights)
                order=members[np.argsort(np.sum((vectors[members]-centroid)**2,axis=1))]
                for candidate in order:
                    candidate=int(candidate)
                    if candidate not in used:
                        next_medoids[cluster]=candidate
                        used.add(candidate)
                        break
            if np.array_equal(next_medoids,medoids):
                break
            medoids=next_medoids
        selected=medoids.tolist()
        nearest=np.full(len(unique),np.inf)
        assignment=np.zeros(len(unique),dtype=np.int32)
        for cluster,idx in enumerate(selected):
            distance=np.sum((vectors-vectors[idx])**2,axis=1)
            mask=distance<nearest
            nearest[mask]=distance[mask]
            assignment[mask]=idx
        method='weighted farthest initialization plus Lloyd medoid refinement, nearest replacement'
    mapped=unique[assignment[inverse]]
    image_pixels=mapped.reshape(32,64,8,8).transpose(0,2,1,3).reshape(256,512)
    out=Image.fromarray(image_pixels.astype(np.uint8)).convert('P')
    out.putpalette(pal.astype(np.uint8).reshape(-1).tolist())
    output.parent.mkdir(parents=True,exist_ok=True)
    out.save(output)
    try:
        source_ref=str(source.relative_to(ROOT))
    except ValueError:
        source_ref=str(source)
    result={'scope':'static_asset_budget','source':source_ref,
            'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'output':str(output.relative_to(ROOT)),'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
            'unique_source_tiles':len(unique),'tile_budget':budget,'unique_output_tiles':len(np.unique(mapped,axis=0)),
            'pixel_block_size':1,'transparent_index':0,'opaque_indices':[1,14],
            'mean_squared_rgb_error':float(np.average(nearest,weights=counts)/192),
            'method':method,'refine_iterations':refine,
            'crop_box':list(crop) if crop is not None else None,
            'claim_ceiling':'prototype_compare_flat','runtime_budget':'not_measured'}
    output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--budget',type=int,default=720)
    parser.add_argument('--output',type=Path,default=ROOT/'rascunho/showdown_tile_budget_720.png')
    parser.add_argument('--refine',type=int,default=0)
    parser.add_argument('--source',type=Path,default=SOURCE)
    parser.add_argument('--crop',type=int,nargs=4,metavar=('LEFT','TOP','RIGHT','BOTTOM'))
    args=parser.parse_args()
    if not 1<=args.budget<=2048: parser.error('budget must be 1..2048')
    if args.refine < 0 or args.refine > 8: parser.error('refine must be 0..8')
    convert(args.budget,args.output,args.refine,args.source,tuple(args.crop) if args.crop else None)
