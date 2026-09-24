#!/usr/bin/env python3
"""Translate generated KO/victory poses into the existing Musgo palette."""
import hashlib
import json
from pathlib import Path
from PIL import Image
from convert_musgo import load_keyed, tight_crop, remap

ROOT = Path(__file__).resolve().parents[3]
SRC = Path(__file__).with_name('ko_victory_source_v1.png')
OUT = ROOT/'res/sprite/musgo'


def main():
    source = load_keyed(SRC)
    w,h = source.size
    # The generated sheet has unequal whitespace; these cuts fall in the
    # inspected magenta gaps, including the wider horizontal landed pose.
    cuts = [0, round(w*.25), round(w*.50), round(w*.795), w]
    poses = [tight_crop(source.crop((cuts[i],0,cuts[i+1],h))) for i in range(4)]
    pal = Image.open(OUT/'palettes/pal1.png').getpalette()
    colors = [tuple(pal[i*3:i*3+3]) for i in range(16)]
    # Shared physical scale: fallen body wider, raised-arm victory taller.
    scale = 120 / poses[3].height
    report = {'source':'data/source_art/musgo/ko_victory_source_v1.png',
              'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
              'status':'source_candidate','tool':'built-in image_gen',
              'conversion':'chroma key, nearest resize, existing PAL2/PAL3 indices', 'outputs':{}}
    for filename,indices,cw,ch in [('fall_v1.png',[0,1],120,120),
                                    ('defeat_v1.png',[2],128,64),
                                    ('victory_v1.png',[3],88,128)]:
        strip = Image.new('P',(cw*len(indices),ch),0)
        strip.putpalette(pal)
        for fi,idx in enumerate(indices):
            pose=poses[idx]
            size=(round(pose.width*scale),round(pose.height*scale))
            assert size[0]<=cw and size[1]<=ch, (filename,size)
            frame=pose.resize(size,Image.Resampling.NEAREST)
            q=remap(frame,colors,pal)
            strip.paste(q,(fi*cw+(cw-size[0])//2,ch-size[1]))
        path=OUT/filename
        strip.save(path)
        report['outputs'][filename]={'cell':[cw,ch],'frames':len(indices),'pivot':[cw//2,ch],
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    (ROOT/'rascunho/musgo_ko_victory_report.json').write_text(json.dumps(report,indent=2)+'\n')
    path = ROOT/'doc/asset_provenance_manifest.json'
    manifest = json.loads(path.read_text())
    entries = next(v for v in manifest.values() if isinstance(v,list) and v and isinstance(v[0],dict) and 'res_symbol' in v[0])
    for filename,symbol in [('fall_v1.png','spr_musgo_fall_v1'),('defeat_v1.png','spr_musgo_defeat_v1'),('victory_v1.png','spr_musgo_victory_v1')]:
        entry = next((e for e in entries if e.get('res_symbol')==symbol),None)
        if entry is None:
            entry = {'res_symbol':symbol}
            entries.append(entry)
        entry.update(res_kind='SPRITE',asset_path='sprite/musgo/'+filename,
                     source_kind='procedural_composed_from_authored',acceptance_status='placeholder',
                     generated_by='convert_ko_victory.py; built-in image_gen source, nearest resize and palette mapping',
                     authored_source=report['source'],authored_source_hash=report['source_sha256'])
    path.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__': main()
