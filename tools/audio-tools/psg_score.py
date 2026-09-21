#!/usr/bin/env python3
"""Compile an authored, frame-timed PSG score into VGM 1.50 for XGM2.

Offline authoring only; no claim of FM arrangement or perceptual approval.
Format reference: https://vgmrips.net/wiki/VGM_Specification
PSG register contract: sdk/sgdk-2.11/src/psg.c.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path


def integer(value, low, high, name):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f'{name}: expected integer {low}..{high}')
    return value


def compile_score(score):
    if score.get('schema_version') != '1.0.0':
        raise ValueError('unsupported schema_version')
    region = score.get('region')
    if region not in ('ntsc', 'pal'):
        raise ValueError('region must be ntsc or pal')
    rate, clock = (60, 3579545) if region == 'ntsc' else (50, 3546893)
    frames = integer(score.get('frames'), 1, rate * 600, 'frames')
    loop = integer(score.get('loop_frame', 0), 0, frames - 1, 'loop_frame')
    events = score.get('notes')
    if not isinstance(events, list) or not events:
        raise ValueError('notes must be nonempty')
    timeline = {}
    occupied = [set() for _ in range(3)]
    for event in events:
        channel = integer(event.get('channel'), 0, 2, 'channel')
        start = integer(event.get('frame'), 0, frames - 1, 'frame')
        duration = integer(event.get('duration'), 1, frames - start, 'duration')
        note = integer(event.get('midi'), 0, 127, 'midi')
        attenuation = integer(event.get('attenuation', 4), 0, 14, 'attenuation')
        period = round(clock / (32 * 440 * 2 ** ((note - 69) / 12)))
        if not 1 <= period <= 1023:
            raise ValueError('note outside PSG tone range; transpose explicitly')
        if start < loop < start + duration:
            raise ValueError('note crosses loop entry; retrigger explicitly')
        window = set(range(start, start + duration))
        if occupied[channel] & window:
            raise ValueError('overlapping notes on one PSG channel')
        occupied[channel].update(window)
        # Off before on permits adjacent notes without muting the new attack.
        timeline.setdefault(start + duration, []).append((0, channel, None, 15))
        timeline.setdefault(start, []).append((1, channel, period, attenuation))
    stream = bytearray()
    loop_offset = None

    def write(value):
        stream.extend((0x50, value))

    for frame in range(frames):
        if frame == 0 or frame == loop:
            if frame == loop:
                loop_offset = 0x40 + len(stream)
            # Deterministic entry, including noise channel left by prior BGM.
            for channel in range(4):
                write(0x90 | channel << 5 | 15)
        for _, channel, period, attenuation in sorted(timeline.get(frame, [])):
            if period is not None:
                write(0x80 | channel << 5 | (period & 15))
                write(period >> 4)
            write(0x90 | channel << 5 | attenuation)
        stream.append(0x62 if rate == 60 else 0x63)
    stream.append(0x66)
    header = bytearray(0x40)
    header[:4] = b'Vgm '
    for offset, value in ((4, len(header) + len(stream) - 4), (8, 0x150),
                          (0x0c, clock), (0x18, frames * (44100 // rate)),
                          (0x1c, loop_offset - 0x1c),
                          (0x20, (frames - loop) * (44100 // rate)),
                          (0x24, rate), (0x34, 0x0c)):
        struct.pack_into('<I', header, offset, value)
    struct.pack_into('<H', header, 0x28, 9)
    header[0x2a] = 16
    return bytes(header + stream)


def self_check():
    import copy
    score = {'schema_version': '1.0.0', 'region': 'ntsc', 'frames': 60,
             'loop_frame': 15, 'notes': [
                 {'channel': 0, 'frame': 15, 'duration': 15, 'midi': 69}]}
    for region, samples in [('ntsc', 44100), ('pal', 52920)]:
        score['region'] = region
        data = compile_score(score)
        assert struct.unpack_from('<I', data, 0x18)[0] == samples
        offset = struct.unpack_from('<I', data, 0x1c)[0] + 0x1c
        assert data[offset:offset+2] == bytes((0x50, 0x9f))
        assert data == compile_score(score)
    for patch in ({'channel': 3}, {'midi': 0}, {'duration': 0}, {'frame': True}):
        bad = copy.deepcopy(score)
        bad['notes'][0].update(patch)
        try:
            compile_score(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f'invalid score accepted: {patch}')
    for kind in ('overlap', 'loop_crossing'):
        bad = copy.deepcopy(score)
        if kind == 'overlap':
            bad['notes'].append(dict(bad['notes'][0]))
        else:
            bad['notes'][0].update(frame=10, duration=20)
        try:
            compile_score(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(kind)
    print('psg_score: passed NTSC/PAL, loop entry, determinism, range, overlap, crossing')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--score', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        self_check()
        return
    if not args.score or not args.out:
        parser.error('--score and --out required')
    if args.score.resolve() in {args.out.resolve(), args.out.with_suffix('.provenance.json').resolve()}:
        parser.error('output cannot overwrite source score')
    source = args.score.read_bytes()
    data = compile_score(json.loads(source))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    args.out.with_suffix('.provenance.json').write_text(json.dumps({
        'schema_version': '1.0.0', 'source_kind': 'authored_score',
        'acceptance_status': 'technical_candidate',
        'score_sha256': hashlib.sha256(source).hexdigest(),
        'vgm_sha256': hashlib.sha256(data).hexdigest(),
        'compiler_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope': 'three_psg_tone_channels; no_fm_no_pcm_no_runtime_proof'
    }, indent=2) + '\n')


if __name__ == '__main__':
    main()
