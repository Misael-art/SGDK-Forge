#!/usr/bin/env python3
"""Real keyboard playtest, fresh ROM snapshot, window video and health samples.

Does not edit emulator RAM or claim wins from input counts.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess as sp
import sys
import time
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'out/emulator_evidence'/('visual_ko_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
AUDIO_MODULE=None


def run(*args): return sp.check_output(args,stderr=sp.DEVNULL,text=True).strip()
def key(k,down): run('xdotool','keydown' if down else 'keyup',k)
def tap(k):
    key(k,True);time.sleep(.12);key(k,False);time.sleep(.12)


def main():
    global AUDIO_MODULE
    DEST.mkdir(parents=True)
    rom=DEST/'rom.bin';shutil.copy2(ROOT/'out/rom.bin',rom)
    sha=hashlib.sha256(rom.read_bytes()).hexdigest()
    before=set(run('xdotool','search','--name','BlastEm').splitlines()) if sp.run(['xdotool','search','--name','BlastEm'],stdout=sp.DEVNULL).returncode==0 else set()
    log=(DEST/'emulator.log').open('w')
    region='E' if '--pal' in sys.argv else 'U'
    p2='--p2' in sys.argv
    timeout_test=('--draw' in sys.argv or '--timeover' in sys.argv)
    with_audio='--audio' in sys.argv
    move,attack=('j','h') if p2 else ('Right','q')
    # XDG_CONFIG_HOME/XDG_DATA_HOME do flatpak: diretorio de scratch do
    # emulador, nao fonte.  Vive em out/ porque e artefato de execucao e
    # porque rascunho/ nao e versionado -- um clone nao teria o caminho.
    config=ROOT/'out/emulator_config'
    config.mkdir(parents=True, exist_ok=True)
    sink='hamoopig_qa_'+str(os.getpid())
    existing_audio_inputs=set()
    if with_audio:
        existing_audio_inputs={s['index'] for s in json.loads(run('pactl','-f','json','list','sink-inputs'))}
        AUDIO_MODULE=run('pactl','load-module','module-null-sink','sink_name='+sink,'rate=48000','channels=2')
    proc=sp.Popen(['flatpak','--user','run','--filesystem=/mnt/sdcard/Projects/Sgdk Forge',
                   '--env=SDL_AUDIODRIVER='+('pulseaudio' if with_audio else 'dummy'),'--env=PULSE_SINK='+sink,
                   '--env=SDL_JOYSTICK_HIDAPI=0','--command=sh','com.retrodev.blastem','-c',
                   'export XDG_CONFIG_HOME="$1" XDG_DATA_HOME="$2"; shift 2; exec /app/bin/blastem "$@"',
                   'hamoopig-qa',str(config/'blastem'),str(DEST/'userdata'),'-r',region,str(rom)],stdout=log,stderr=log,start_new_session=True)
    video=None;audio_capture=None;samples=[];special_samples=[]
    print('session='+str(DEST),flush=True)
    try:
        win=None
        for _ in range(200):
            result=sp.run(['xdotool','search','--name','BlastEm'],capture_output=True,text=True)
            found=set(result.stdout.splitlines())-before
            if found: win=next(iter(found));break
            time.sleep(.1)
        if not win: raise RuntimeError('window timeout')
        run('xdotool','windowactivate','--sync',win)
        time.sleep(4)
        def shot(name):
            path=DEST/(name+'.png')
            # XWayland can expose the window before its first framebuffer.
            # Retry only low-information captures; never synthesize pixels.
            for _ in range(8):
                run('import','-window',win,str(path))
                try:
                    im=Image.open(path).convert('RGB')
                    if len(set(im.get_flattened_data())) > 1: return path
                except Exception: pass
                time.sleep(.15)
            return path
        shot('00_select')
        if '--musgo' in sys.argv:
            # Confirm the displayed P1 name, not the number of injected taps.
            # This inspected prior screenshot is only an input-selection oracle,
            # never evidence for this ROM's gameplay.
            reference=Image.open(ROOT/'out/emulator_evidence/visual_ko_20260912T162335Z/00_musgo_selected.png').convert('RGB')
            def name_pixels(im):
                scale=im.width/320;top=(im.height-224*scale)/2
                return list(im.crop((int(72*scale),int(top+192*scale),int(112*scale),int(top+200*scale))).get_flattened_data())
            expected=name_pixels(reference)
            for attempt in range(8):
                selected=shot('00_musgo_selected')
                if name_pixels(Image.open(selected).convert('RGB'))==expected:break
                tap('Right');time.sleep(.5)
            else:raise RuntimeError('Musgo name did not match inspected selection reference')
        tap('a');tap('Return');time.sleep(2)
        for attempt in range(5):
            round_path=shot('01_round')
            im=Image.open(round_path).convert('RGB')
            band=im.crop((0,0,im.width,int(im.height*.2)))
            if sum(r>190 and g>190 and b<80 for r,g,b in band.get_flattened_data())>1000:break
            # Confirm both physical ports if a quick host tap was missed.
            tap('a');time.sleep(.5);tap('n');time.sleep(2)
        else:raise RuntimeError('Fight HUD did not appear; do not label zero yellow as KO')
        # Window framebuffer only; preserve native aspect/letterbox for audit.
        vlog=(DEST/'video.log').open('w')
        video=sp.Popen(['ffmpeg','-y','-f','x11grab','-window_id',win,'-framerate','60','-draw_mouse','0',
                        '-i',os.environ['DISPLAY'],'-an','-c:v','libx264','-preset','ultrafast','-crf','20',
                        str(DEST/'combat_window.mp4')],stdout=vlog,stderr=vlog)
        if with_audio:
            # Session policy/DSP can ignore PULSE_SINK. Move only the newly
            # created BlastEm stream and verify the actual sink assignment.
            new_inputs=[s for s in json.loads(run('pactl','-f','json','list','sink-inputs'))
                        if s['index'] not in existing_audio_inputs and
                        s.get('properties',{}).get('application.process.binary')=='blastem.bin']
            if len(new_inputs)!=1:raise RuntimeError('Cannot uniquely identify this emulator audio stream')
            run('pactl','move-sink-input',str(new_inputs[0]['index']),sink)
            alog=(DEST/'audio.log').open('w')
            audio_capture=sp.Popen(['ffmpeg','-y','-f','pulse','-i',sink+'.monitor','-c:a','pcm_s16le',
                                    str(DEST/'emulator_audio.wav')],stdout=alog,stderr=alog)
            owned_sinks=[s for s in json.loads(run('pactl','-f','json','list','sinks')) if s['name']==sink]
            ids={s['index'] for s in owned_sinks}
            owned_inputs=[]
            for _ in range(10):
                owned_inputs=[s for s in json.loads(run('pactl','-f','json','list','sink-inputs')) if s['sink'] in ids]
                if len(owned_inputs)==1:break
                time.sleep(.2)
            if len(owned_inputs)!=1:raise RuntimeError('Isolated monitor has no unique emulator stream')
            (DEST/'pulse_sink_inputs.json').write_text(json.dumps(owned_inputs,indent=2)+'\n')
            (DEST/'pulse_sinks.json').write_text(json.dumps(owned_sinks,indent=2)+'\n')
        time.sleep(5)
        if '--probe-short' in sys.argv:
            # Short regional probe: allow the ROM to warm up and export HPRB,
            # then close cleanly so BlastEm flushes SRAM without a long match.
            time.sleep(30)
            shot('probe_short')
            return
        def specials(label):
            # Match fsm.c: down, forward + punch. Musgo's 700 is a slam,
            # Ryo/Ken's 700 emits a projectile; screenshots require review.
            for player,down,forward,punch in ((1,'Down','Right','q'),(2,'k','j','h')):
                for attempt in range(3):
                    key(down,True);time.sleep(.10)
                    key(down,False);key(forward,True);time.sleep(.07)
                    key(punch,True);time.sleep(.08)
                    key(punch,False);key(forward,False)
                    # State 700 creates Ryo's fireball at animFrame 12;
                    # sample long enough to include that emission and Musgo's
                    # corresponding slam recovery.
                    for frame in range(24):
                        path=shot(f'{label}_p{player}_try{attempt}_{frame}')
                        special_samples.append({'phase':label,'player':player,'capture':path.name})
                        time.sleep(.075)
                    time.sleep(.8)
        if '--specials' in sys.argv:specials('before_reset')
        if '--timeover' in sys.argv:
            def defender_yellow(path):
                im=Image.open(path).convert('RGB');scale=im.width/320
                left,right=(8,136) if p2 else (184,312)
                roi=im.crop((int(left*scale),0,int(right*scale),int(40*scale)))
                return sum(r>190 and g>190 and b<80 for r,g,b in roi.get_flattened_data())
            baseline=defender_yellow(shot('timeover_before_damage'))
            for attempt in range(20):
                key(move,True);time.sleep(.5);tap(attack);time.sleep(.25);key(move,False)
                health=defender_yellow(shot('timeover_damage_setup'))
                if 0<health<baseline:break
            else:raise RuntimeError('Time-over setup did not produce observed nonlethal damage')
        zeros=0
        for hit in range(95 if timeout_test else 150):
            # Refresh movement after recovery; wait until the intro has ended.
            if timeout_test:time.sleep(1)
            else:
                key(move,True);time.sleep(.5)
                tap(attack);time.sleep(.25)
            if hit%5==0 or (timeout_test and hit>=48):
                path=shot(f'combat_{hit:03}')
                im=Image.open(path).convert('RGB');scale=im.width/320;top=(im.height-224*scale)/2
                left,right=(8,136) if p2 else (184,312)
                # PAL and NTSC have different vertical borders/scales. Restrict
                # x to a health strip and cover the complete upper HUD band.
                roi=im.crop((int(left*scale),0,int(right*scale),int(40*scale)))
                yellow=sum(r>190 and g>190 and b<80 for r,g,b in roi.get_flattened_data())
                samples.append({'step':hit,'defender':1 if p2 else 2,'yellow_pixels':yellow,'capture':path.name,
                                'window_title':run('xdotool','getwindowname',win)})
                print(json.dumps(samples[-1]),flush=True)
                if yellow==0:
                    zeros+=1;key(move,False)
                    time.sleep(2);shot(f'zero_{zeros}_settle')
                    time.sleep(5);shot(f'zero_{zeros}_result')
                    if zeros==1 and '--specials' in sys.argv:
                        # Observe restored health, then let ROUND/FIGHT expire.
                        for attempt in range(20):
                            restored=shot('special_reset_health')
                            im=Image.open(restored).convert('RGB');scale=im.width/320
                            roi=im.crop((int(left*scale),0,int(right*scale),int(40*scale)))
                            if sum(r>190 and g>190 and b<80 for r,g,b in roi.get_flattened_data())>1000:break
                            time.sleep(.5)
                        else:raise RuntimeError('No observed health reset before special test')
                        time.sleep(4);specials('after_reset')
                        break
                    if zeros>=2:break
        key(move,False)
        shot('after_combat')
        if timeout_test:
            shot('after_timeover_observation')
        elif '--musgo' in sys.argv and '--exit-select' not in sys.argv:
            tap('a');time.sleep(2);shot('rematch_round')
        else:
            tap('Return');time.sleep(2);shot('return_select_or_pause')
        (DEST/'manifest.json').write_text(json.dumps({'rom_sha256':sha,'rom_bytes':rom.stat().st_size,
            'scope':'real_keyboard_playtest','requested_p1':'musgo' if '--musgo' in sys.argv else 'ryo',
            'attacker':2 if p2 else 1,'region_requested':region,
            'scenario':'draw' if '--draw' in sys.argv else ('timeover' if timeout_test else 'ko'),
            'config_sha256':hashlib.sha256((config/'blastem/blastem.cfg').read_bytes()).hexdigest(),
            'audio':'isolated_monitor_captured_not_auditioned' if with_audio else 'not_captured_dummy_driver',
            'audio_monitor':sink+'.monitor' if with_audio else None,'samples':samples,'special_samples':special_samples,
            'title':run('xdotool','getwindowname',win),'video':'combat_window.mp4',
            'claims':'requires visual review; zero yellow is a candidate, not automatic KO proof'},indent=2)+'\n')
    finally:
        for k in ('Right','Down','k','a','q','Return','j','h','t'):
            try:key(k,False)
            except sp.CalledProcessError:pass
        if video:
            video.send_signal(signal.SIGINT);video.wait(timeout=10)
        if audio_capture:
            audio_capture.send_signal(signal.SIGINT);audio_capture.wait(timeout=10)
        # Only terminate this session's process group, never unrelated emulators.
        try:os.killpg(proc.pid,signal.SIGTERM)
        except ProcessLookupError:pass
        try:proc.wait(timeout=5)
        except sp.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()


if __name__=='__main__':
    try:main()
    finally:
        if AUDIO_MODULE:run('pactl','unload-module',AUDIO_MODULE)
