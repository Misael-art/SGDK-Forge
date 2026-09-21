#!/usr/bin/env python3
"""Prepare real artifact paths for the canonical identity finalizer.

No gameplay approvals: visual findings belong to the reviewed closeout.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('sessions',nargs='+')
    args=parser.parse_args()
    sha=digest(ROOT/'out/rom.bin')
    evidence=[]
    for name in args.sessions:
        session=ROOT/'out/emulator_evidence'/name
        manifest=json.loads((session/'manifest.json').read_text())
        assert manifest['rom_sha256']==sha==digest(session/'rom.bin'), 'ROM mismatch'
        assert manifest['samples'], 'No observations recorded'
        files=sorted(p for p in session.iterdir() if p.suffix in ('.png','.mp4','.wav','.json'))
        files+=sorted(session.glob('userdata/**/save.sram'))
        assert any(p.suffix=='.png' for p in files) and any(p.suffix=='.mp4' for p in files)
        evidence.extend(str(p.relative_to(ROOT)) for p in files)
    target=ROOT/'out/logs/continuation_session_20260913.json'
    target.write_text(json.dumps({'schema_version':'1.0.0','session_id':'continuation_20260913',
        'scope':'artifact_identity_only','rom_sha256':sha,'evidence_files':evidence,
        'evidence_stale':False,'claims':'See reviewed closeout; no automatic gameplay approval',
        'missing_canonical_axes':['vlab','vdp_dump','runtime_metrics','worst_frame_budget']},indent=2)+'\n')
    print(target)

if __name__=='__main__':main()
