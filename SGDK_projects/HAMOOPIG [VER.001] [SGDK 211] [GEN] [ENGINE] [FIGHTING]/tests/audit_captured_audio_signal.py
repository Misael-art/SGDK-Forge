#!/usr/bin/env python3
"""Signal-only PCM audit. No listening, music quality or frame-budget approval."""
import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import sys
import wave

def stats(values):
    if not values:raise ValueError('Empty PCM cannot pass')
    peak=max(abs(v) for v in values)
    rms=math.sqrt(sum(v*v for v in values)/len(values))
    return {'samples':len(values),'peak_pcm':peak,'rms_pcm':rms,
            'rms_dbfs':20*math.log10(rms/32768) if rms else None,
            'nonzero_samples':sum(v!=0 for v in values),
            'clipped_samples':sum(v in (-32768,32767) for v in values),
            'signal_present':peak>0}

def self_check():
    silent=stats([0]*100)
    assert silent['signal_present'] is False and silent['rms_pcm']==0
    signal=stats([16384,-16384]*50)
    assert signal['rms_pcm']==16384 and signal['clipped_samples']==0
    assert abs(signal['rms_dbfs']+6.020599913)<1e-6
    assert stats([32767,-32768])['clipped_samples']==2
    try:stats([])
    except ValueError:pass
    else:raise AssertionError('empty input passed')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--self-check',action='store_true')
    parser.add_argument('--wav',type=Path)
    args=parser.parse_args()
    self_check()
    if args.self_check:print('PASS: silence, known RMS, clipping and empty-input rejection')
    if not args.wav:return
    path=args.wav.resolve()
    with wave.open(str(path),'rb') as wav:
        assert wav.getsampwidth()==2 and wav.getcomptype()=='NONE'
        channels=wav.getnchannels();rate=wav.getframerate()
        pcm=array('h',wav.readframes(wav.getnframes()))
        if sys.byteorder!='little':pcm.byteswap()
    manifest=json.loads((path.parent/'manifest.json').read_text())
    inputs=json.loads((path.parent/'pulse_sink_inputs.json').read_text())
    sinks=json.loads((path.parent/'pulse_sinks.json').read_text())
    routed=(len(inputs)==1 and len(sinks)==1 and inputs[0]['sink']==sinks[0]['index']
            and inputs[0].get('properties',{}).get('application.process.binary')=='blastem.bin')
    result={'scope':'captured_audio_signal_only','self_check':'passed',
            'rom_sha256':manifest['rom_sha256'],'wav_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'sample_rate':rate,'channels':channels,'duration_seconds':len(pcm)/channels/rate,
            'isolated_emulator_route_verified':routed,**stats(pcm),
            'listening_review':'not_performed','performance_and_budget':'not_measured'}
    result['status']='signal_and_route_present' if result['signal_present'] and routed else 'not_validated'
    (path.parent/'audio_signal_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
    if result['status']!='signal_and_route_present':raise SystemExit(2)

if __name__=='__main__':main()
