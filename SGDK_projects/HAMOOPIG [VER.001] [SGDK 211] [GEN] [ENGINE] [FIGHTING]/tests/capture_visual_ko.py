#!/usr/bin/env python3
"""Real keyboard playtest, fresh ROM snapshot, window video and health samples.

Does not edit emulator RAM or claim wins from input counts.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import struct
import subprocess as sp
import sys
import time
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
# Include microseconds and PID so rapid matrix retries never collide on the
# one-second directory name after a timeout or an emulator startup failure.
DEST=ROOT/'out/emulator_evidence'/('visual_ko_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'-'+str(os.getpid()))
AUDIO_MODULE=None
FIGHTER_IDS={'ryo': 1, 'ken': 2, 'musgo': 3}


def arg_value(name, default=None):
    prefix=name+'='
    for value in sys.argv:
        if value.startswith(prefix): return value[len(prefix):]
    return default


def fighter_arg(name, default):
    value=arg_value(name, default)
    value=value.lower()
    if value not in FIGHTER_IDS:
        raise ValueError(f'{name} must be one of {", ".join(FIGHTER_IDS)}')
    return value


def prepare_blastem_config(config_file):
    """Materialize packaged defaults and inject only the P2 QA bindings."""
    try:
        result=sp.run(
            ['flatpak','--user','run','--command=sh','com.retrodev.blastem','-c',
             'cat /app/etc/default.cfg'], capture_output=True, timeout=5.0)
    except sp.TimeoutExpired:
        result=None
    if result is not None and result.returncode == 0:
        base=result.stdout.decode('utf-8')
    else:
        # The checked-in host package is the same default consumed by the
        # Flatpak image.  Use it when a rapid matrix run briefly cannot exec
        # the container, so a transient Flatpak lookup does not invalidate a
        # ROM-bound case.
        # Linux workspaces keep the checked-in emulator directory as
        # ``Blastem`` (the Windows executable itself is BlastEm.exe).  Use the
        # canonical case so the fallback works when the Flatpak briefly cannot
        # be queried.
        packaged_default=ROOT.parents[1]/'tools'/'emuladores'/'Blastem'/'default.cfg'
        if not packaged_default.is_file():
            raise RuntimeError('BlastEm packaged default.cfg unavailable')
        base=packaged_default.read_text(encoding='utf-8')
    extra=(ROOT/'tests/blastem_qa.cfg').read_text(encoding='utf-8')
    match=re.search(r'keys\s*\{(.*?)\n\s*\}\s*pads\s*\{', base, re.S)
    extra_match=re.search(r'keys\s*\{(.*?)\}', extra, re.S)
    if not match or not extra_match:
        raise RuntimeError('BlastEm keyboard binding contract changed')
    injected=match.group(1)+extra_match.group(1)
    base=base[:match.start(1)]+injected+base[match.end(1):]
    config_file.write_text(base, encoding='utf-8')


def run(*args): return sp.check_output(args,stderr=sp.DEVNULL,text=True).strip()
def key(k,down): run('xdotool','keydown' if down else 'keyup',k)
def tap(k):
    key(k,True);time.sleep(.12);key(k,False);time.sleep(.12)


def main():
    global AUDIO_MODULE
    DEST.mkdir(parents=True)
    phase_clock={}
    def mark_phase(name):
        phase_clock[name]={'monotonic_ns':time.monotonic_ns(),
                           'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    mark_phase('process_start')
    rom_source=Path(arg_value('--rom', str(ROOT/'out/rom.bin'))).expanduser().resolve()
    if not rom_source.is_file():
        raise FileNotFoundError(f'ROM source not found: {rom_source}')
    rom=DEST/'rom.bin';shutil.copy(rom_source,rom)
    sha=hashlib.sha256(rom.read_bytes()).hexdigest()
    mark_phase('rom_snapshot_complete')
    before=set(run('xdotool','search','--name','BlastEm').splitlines()) if sp.run(['xdotool','search','--name','BlastEm'],stdout=sp.DEVNULL).returncode==0 else set()
    log=(DEST/'emulator.log').open('w')
    region='E' if '--pal' in sys.argv else 'U'
    p2='--p2' in sys.argv or arg_value('--attacker','p1') == 'p2'
    requested_p1=fighter_arg('--p1', 'musgo' if '--musgo' in sys.argv else 'ryo')
    requested_p2=fighter_arg('--p2fighter', 'musgo')
    timeout_test=('--draw' in sys.argv or '--timeover' in sys.argv)
    with_audio='--audio' in sys.argv
    # Use the same punch family on both ports.  P2's A kick was too short to
    # close the authored spacing reliably on BGB2, so the real keyboard route
    # now mirrors P1's X punch through the QA binding (Y on the host).
    move,attack=('j','y') if p2 else ('Right','q')
    # XDG_CONFIG_HOME/XDG_DATA_HOME do flatpak: diretorio de scratch do
    # emulador, nao fonte.  Vive em out/ porque e artefato de execucao e
    # porque rascunho/ nao e versionado -- um clone nao teria o caminho.
    config=ROOT/'out/emulator_config'
    config.mkdir(parents=True, exist_ok=True)
    config_dir=config/'blastem'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_text_path=config_dir/'blastem.cfg'
    prepare_blastem_config(config_text_path)
    # BlastEm releases differ in whether XDG_CONFIG_HOME is treated as the
    # parent or as the already-resolved application directory.  Keep the same
    # generated profile in both documented layouts; the manifest records the
    # canonical path used for the session.
    for alternate in (config_dir/'.config'/'blastem'/'blastem.cfg',
                      config/'.config'/'blastem'/'blastem.cfg'):
        alternate.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(config_text_path, alternate)
    sink='hamoopig_qa_'+str(os.getpid())
    existing_audio_inputs=set()
    if with_audio:
        existing_audio_inputs={s['index'] for s in json.loads(run('pactl','-f','json','list','sink-inputs'))}
        AUDIO_MODULE=run('pactl','load-module','module-null-sink','sink_name='+sink,'rate=48000','channels=2')
    mark_phase('emulator_launch_start')
    proc=sp.Popen(['flatpak','--user','run','--filesystem=/mnt/sdcard/Projects/Sgdk Forge',
                   '--env=SDL_AUDIODRIVER='+('pulseaudio' if with_audio else 'dummy'),'--env=PULSE_SINK='+sink,
                   '--env=SDL_JOYSTICK_HIDAPI=0','--command=sh','com.retrodev.blastem','-c',
                   'export XDG_CONFIG_HOME="$1" XDG_DATA_HOME="$2"; shift 2; exec /app/bin/blastem "$@"',
                   'hamoopig-qa',str(config/'blastem'),str(DEST/'userdata'),'-r',region,str(rom)],stdout=log,stderr=log,start_new_session=True)
    mark_phase('emulator_launch_end')
    video=None;transition_video=None;transition_log=None;audio_capture=None;samples=[];special_samples=[]
    capture_timeline=[]
    capture_clock={'video_enabled':'--no-video' not in sys.argv,
                   'video_started_monotonic_ns':None,
                   'video_started_utc':None,
                   'audio_started_monotonic_ns':None,
                   'audio_started_utc':None,
                   'video_stopped_monotonic_ns':None,
                   'audio_stopped_monotonic_ns':None}
    def stop_owned_process(child, label):
        if not child or child.poll() is not None:
            return
        try:
            child.send_signal(signal.SIGINT)
            child.wait(timeout=10)
        except sp.TimeoutExpired:
            (DEST/'finalization_warnings.log').open('a').write(label+' did not exit after SIGINT; SIGKILL used\n')
            child.kill()
            try: child.wait(timeout=5)
            except sp.TimeoutExpired: pass
    print('session='+str(DEST),flush=True)
    try:
        win=None
        for _ in range(200):
            result=sp.run(['xdotool','search','--name','BlastEm'],capture_output=True,text=True)
            found=set(result.stdout.splitlines())-before
            if found: win=next(iter(found));break
            time.sleep(.1)
        if not win: raise RuntimeError('window timeout')
        mark_phase('window_ready')
        run('xdotool','windowactivate','--sync',win)
        if '--transition' in sys.argv:
            transition_log=(DEST/'transition_video.log').open('w')
            transition_video=sp.Popen(['ffmpeg','-y','-f','x11grab','-window_id',win,
                                       '-framerate','60','-draw_mouse','0','-i',os.environ['DISPLAY'],
                                       '-an','-c:v','libx264','-preset','ultrafast','-crf','20',
                                       str(DEST/'opening_title_transition.mp4')],
                                      stdout=transition_log,stderr=transition_log)
        # A abertura agora é uma cena própria e o título só aceita START
        # depois do fade-in. Esperar a composição completa evita enviar a
        # confirmação durante a carga protegida e cair no seletor por acaso.
        time.sleep(7)
        def shot(name):
            path=DEST/(name+'.png')
            # XWayland can expose the window before its first framebuffer.
            # Retry only low-information captures; never synthesize pixels.
            for _ in range(8):
                # ImageMagick import can block forever when BlastEm exits or
                # XWayland keeps a stale window id.  A bounded capture keeps a
                # failed probe recoverable and prevents a semantic route from
                # hanging without producing an honest bundle.
                try:
                    sp.run(['import','-window',win,str(path)],
                           stdout=sp.DEVNULL, stderr=sp.DEVNULL, timeout=2.0,
                           check=False)
                except sp.TimeoutExpired:
                    continue
                try:
                    im=Image.open(path).convert('RGB')
                    if len(set(im.get_flattened_data())) > 1:
                        capture_timeline.append({'capture':path.name,
                                                 'monotonic_ns':time.monotonic_ns(),
                                                 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                                 'scene':debug_snapshot()})
                        return path
                except Exception: pass
                time.sleep(.15)
            return path
        def debug_snapshot():
            path=DEST/'userdata/blastem/rom/save.sram'
            try:
                raw=path.read_bytes()
                if raw[0x600:0x604] != b'HDBG': return None
                schema,total=__import__('struct').unpack_from('>HH', raw, 0x604)
                if schema == 2 and total == 56 and len(raw) >= 0x600 + total:
                    words=__import__('struct').unpack_from('>24H', raw, 0x608)
                elif schema == 1 and total == 32 and len(raw) >= 0x600 + total:
                    words=__import__('struct').unpack_from('>12H', raw, 0x608) + (None,) * 12
                else:
                    return None
                return {
                    'scene': words[0], 'clock_l': words[1], 'clock_r': words[2],
                    'clock_tick': words[3], 'p1_energy': words[4], 'p2_energy': words[5],
                    'p1_state': words[6], 'p2_state': words[7], 'result_timer': words[8],
                    'pause_ko': words[9], 'frames': words[10] | (words[11] << 16),
                    'hdbg_schema': schema,
                    'p1_anim_frame': words[12], 'p1_anim_frame_total': words[13],
                    'p1_frame_time': words[14], 'p1_frame_time_total': words[15],
                    'p1_fireball_active': words[16], 'p1_fireball_x': words[17],
                    'p1_fireball_y': words[18], 'p1_attack_button': words[19],
                    'p1_down_input': words[20], 'p1_right_input': words[21],
                    'p1_x_input': words[22], 'presentation_frame': words[23]
                }
            except (OSError, IndexError, ValueError, struct.error):
                return None
        def cadence_snapshot():
            """Decode HCAD so every full capture carries logic/presentation evidence."""
            path=DEST/'userdata/blastem/rom/save.sram'
            try:
                # BlastEm flushes SRAM on a short timer. Give the final probe
                # write one bounded interval before decoding; otherwise a
                # valid HCAD block can be present on disk while the manifest
                # still records null.
                raw=None
                offset=-1
                schema=0
                total=0
                words=None
                for _ in range(10):
                    raw=path.read_bytes()
                    offset=0x640
                    if raw[offset:offset+4] != b'HCAD':
                        offset=raw.find(b'HCAD')
                    if offset >= 0:
                        schema,total=struct.unpack_from('>HH',raw,offset+4)
                        if schema == 1 and total == 40 and len(raw) >= offset + 40:
                            words=struct.unpack_from('>16H',raw,offset+8)
                            break
                    time.sleep(.20)
                if offset < 0 or words is None: return None
                names=('video_frames','logic_ticks','zero_tick_frames','one_tick_frames',
                       'two_tick_frames','max_ticks_per_frame','presentation_commits',
                       'presentation_without_logic','fight_video_frames','fight_logic_ticks',
                       'fight_presentation_commits','fight_zero_tick_frames','last_logic_ticks',
                       'last_scene','region_hz','timing_profile')
                report=dict(zip(names,words)); report['schema']=schema
                report['cadence_invariant']=(
                    report['video_frames']==report['presentation_commits'] and
                    report['logic_ticks']==report['one_tick_frames']+2*report['two_tick_frames'])
                report['fight_cadence_invariant']=(
                    report['fight_video_frames']==report['fight_presentation_commits'] and
                    report['fight_logic_ticks']<=report['logic_ticks'])
                return report
            except (OSError, IndexError, ValueError, struct.error):
                return None
        def media_marker_snapshot():
            """Read HANC only after clean exit; it is runtime context, not sync."""
            path=DEST/'userdata/blastem/rom/save.sram'
            try:
                for _ in range(12):
                    raw=path.read_bytes(); offset=raw.find(b'HANC')
                    if offset >= 0 and len(raw) >= offset + 24:
                        schema,total=struct.unpack_from('>HH',raw,offset+4)
                        if schema == 1 and total == 24:
                            words=struct.unpack_from('>8H',raw,offset+8)
                            marker_id=words[0]
                            gameplay_event=bool(marker_id & 0x8000)
                            return {'schema':schema,'bytes':total,'marker_id':marker_id,
                                    'marker_sequence':marker_id & 0x7FFF,
                                    'marker_kind':'gameplay_fball_activation' if gameplay_event else 'periodic_capture_marker',
                                    'gameplay_event_marker':gameplay_event,
                                    'runtime_presentation_frame':(words[1]<<16)|words[2],
                                    'marker_period_frames':words[3],
                                    'visible_hold_frames':words[4],
                                    'psg_channel':words[5],'psg_frequency_hz':words[6],
                                    'scene':words[7], 'source':'save.sram:HANC'}
                    time.sleep(.20)
                return None
            except (OSError, IndexError, ValueError, struct.error):
                return None
        def wait_for_scene(scene_id, timeout=6.0):
            """Wait for the runtime-owned scene before taking a labelled shot."""
            deadline=time.monotonic()+timeout
            while time.monotonic() < deadline:
                probe=debug_snapshot()
                if probe and probe['scene'] == scene_id:
                    return True
                time.sleep(.10)
            return False
        shot('00_title')
        # Preserve the semantic setup path (`if '--semantics' in sys.argv:`)
        # for both the full P04 route and
        # the isolated special probe; the latter must not enter the long
        # guard/throw choreography below.
        if '--semantics' in sys.argv or '--specials-only' in sys.argv or '--guard-only' in sys.argv:
            # The semantic route needs an accepted special without first
            # defeating the victim.  Toggle RULES -> FREE through the actual
            # front-end so the manifest represents a user-visible setting,
            # then return to START; no config or SRAM injection is used.
            tap('Down'); tap('a'); time.sleep(.7)
            # OPTIONS opens on item 0 (SFX); SPECIAL RULES is item 9.
            for _ in range(9): tap('Down')
            tap('a'); time.sleep(.35)
            tap('s'); time.sleep(.5)
            tap('Up'); tap('Return'); time.sleep(2.0)
        if '--h240' in sys.argv:
            if region != 'E':
                raise RuntimeError('--h240 requires --pal; NTSC cannot enable 240-line mode')
            # Enter OPTIONS, open DEBUG, toggle H240, then return to the main
            # title before confirming START.  BlastEm maps A/B/C to A/S/D;
            # Q/W/E are the X/Y/Z buttons.
            def slowtap(button):
                key(button, True); time.sleep(.25); key(button, False); time.sleep(.35)
            slowtap('Down'); slowtap('a'); time.sleep(.7); shot('h240_options')
            for _ in range(10): slowtap('Down')
            slowtap('a'); time.sleep(.7); shot('h240_debug')
            # The debug defaults expose TEXT in the fight overlay. Disable it
            # for a clean H240 round, then move to the H240 item.
            for _ in range(2): slowtap('Down')
            slowtap('a'); time.sleep(.4)
            for _ in range(5): slowtap('Down')
            slowtap('a'); time.sleep(.7); shot('h240_toggled')
            slowtap('s'); slowtap('s'); time.sleep(.7); shot('h240_back')
            slowtap('Up'); time.sleep(.4)
        # The packaged BlastEm profile binds P1 START to the X11 key name
        # ``enter``; the project QA profile maps the same physical edge to
        # the runtime A/START path.  A literal Return key can be accepted by
        # xdotool while remaining invisible to BlastEm, which previously
        # mislabeled the title framebuffer as ``00_select``.
        tap('a')
        if not wait_for_scene(2):
            # SRAM is diagnostic evidence, not a control channel.  If the
            # probe is temporarily unavailable, leave enough time for the
            # normal scene commit before the framebuffer is labelled.
            time.sleep(2.0)
        shot('00_select')
        if '--selection-confirmation' in sys.argv:
            # Capture the visible P1 confirmation, then exercise the real B
            # return path before P2 is confirmed. This is a state-flow proof,
            # not a gameplay capture and must never enter SCENE_FIGHT.
            tap('a')
            time.sleep(.5)
            confirmed=shot('01_p1_confirmed')
            both=None
            if '--confirm-both' in sys.argv:
                # P2's X is tapped with a short edge and captured before the
                # 20-frame commit grace period can enter SCENE_FIGHT.
                time.sleep(.35)
                # blastem_qa.cfg maps host X to the real P2 A button; host Y
                # is P2 X and is intentionally kept separate from this probe.
                key('x', True); time.sleep(.12); key('x', False)
                time.sleep(.06)
                both=shot('02_both_confirmed')
            if both:
                # Once both slots are locked the runtime owns the transition;
                # B is no longer a valid "back" assertion. Preserve the
                # resulting framebuffer under a truthful name.
                time.sleep(1.0)
                returned=shot('03_post_confirmation')
            else:
                tap('s')
                time.sleep(2)
                returned=shot('02_desconfirmed_title')
            config_file=config/'blastem/blastem.cfg'
            config_sha=hashlib.sha256(config_file.read_bytes()).hexdigest() if config_file.exists() else None
            (DEST/'manifest.json').write_text(json.dumps({
                'rom_sha256': sha,
                'rom_source': str(rom_source),
                'rom_source_kind': 'diagnostic_override' if '--rom' in sys.argv else 'release_out_rom',
                'rom_bytes': rom.stat().st_size,
                'scope': 'real_keyboard_selection_confirmation_flow',
                'requested_p1': requested_p1,
                'requested_p2': requested_p2,
                'region_requested': region,
                'stage': 'SHOWDOWN' if '--showdown' in sys.argv else 'BGB2',
                'config_sha256': config_sha,
                'confirmation_capture': confirmed.name,
                'both_confirmation_capture': both.name if both else None,
                'post_confirmation_capture': returned.name,
                'claims': 'visible P1 confirmation and B return-to-title flow only; dual-lock route records gameplay transition only'
            }, indent=2)+'\n')
            return
        if '--showdown' in sys.argv:
            # Explicit alternate route: C is the P1-owned stage toggle.
            tap('d')
            time.sleep(1.5)
            shot('00_showdown_selected')
        elif '--stage2' in sys.argv:
            # A fresh runtime starts with BGB2 selected. C is a toggle, so do
            # not press it here or this evidence would switch back to SHOWDOWN.
            time.sleep(1.5)
            shot('00_stage2_selected')
        # Select both slots explicitly. P1 starts at Ryo; P2 starts at Musgo.
        # select.c cycles Ryo -> Ken -> Musgo -> Ryo.
        p1_steps=(FIGHTER_IDS[requested_p1] - FIGHTER_IDS['ryo']) % 3
        p2_steps=(FIGHTER_IDS[requested_p2] - FIGHTER_IDS['musgo']) % 3
        if '--select-only' in sys.argv:
            # Do not confirm A/X in a selection-only capture: those inputs
            # intentionally commit SCENE_FIGHT after the 20-frame grace window.
            # Move the cursors, let their preview/text redraw, then capture the
            # actual selection framebuffer without entering gameplay.
            for _ in range(p1_steps): tap('Right')
            for _ in range(p2_steps): tap('l')
            time.sleep(.4)
            selected=shot('selected_final')
            config_file=config/'blastem/blastem.cfg'
            config_sha=hashlib.sha256(config_file.read_bytes()).hexdigest() if config_file.exists() else None
            (DEST/'manifest.json').write_text(json.dumps({
                'rom_sha256': sha,
                'rom_bytes': rom.stat().st_size,
                'scope': 'real_keyboard_playtest_selection_only',
                'requested_p1': requested_p1,
                'requested_p2': requested_p2,
                'region_requested': region,
                'stage': 'SHOWDOWN' if '--showdown' in sys.argv else 'BGB2',
                'config_sha256': config_sha,
                'capture': selected.name,
                'claims': 'selection framebuffer only; no gameplay claim'
            }, indent=2)+'\n')
            return
        for _ in range(p1_steps): tap('Right')
        time.sleep(.50)
        tap('a')
        time.sleep(.50)
        for _ in range(p2_steps): tap('l')
        # Use the declared P2 A binding instead of relying on a packaged
        # default: host X is P2 A in tests/blastem_qa.cfg.
        tap('x')
        # Some Linux/XWayland sessions deliver the P2 edge late even though
        # the physical key was released.  Use P2 START as the fallback rather
        # than P1 START: if the scene commits between the two host events,
        # P1 START arms the fight pause/debug panel.  f2 remains the real P2
        # input and confirms the current P2 cursor without writing game state.
        tap('f2')
        time.sleep(2.5)
        # If the P2 START edge was not delivered, use P1 START only while the
        # runtime still reports SELECT.  Once SCENE_FIGHT is live, never send
        # P1 START: it is the fight pause/debug owner.
        probe_after_confirm = None
        for _ in range(10):
            candidate_probe = debug_snapshot()
            if candidate_probe and candidate_probe.get('scene') == 10:
                probe_after_confirm = candidate_probe
                break
            time.sleep(.20)
        if (not probe_after_confirm or probe_after_confirm['scene'] != 10) and '--specials-only' not in sys.argv and '--throw-only' not in sys.argv and '--guard-only' not in sys.argv:
            # Never use P1 START as a confirmation fallback here: once the
            # fight scene has committed, that edge is the pause owner and
            # contaminates the visual capture with PAUSE/DEBUG. Retry only
            # the P2 confirmation while HDBG still reports SELECT.
            for _ in range(3):
                probe_retry = debug_snapshot()
                if probe_retry and probe_retry['scene'] == 10:
                    probe_after_confirm = probe_retry
                    break
                tap('x'); time.sleep(.35); tap('f2'); time.sleep(.75)
        probe_short_readiness = {
            'status': 'observed' if probe_after_confirm and probe_after_confirm.get('scene') == 10 else 'not_observed_before_capture',
            'hdbg_scene': probe_after_confirm.get('scene') if probe_after_confirm else None,
            'claim_limit': 'post-session HCAD is authoritative for overhead comparability'
        }
        if '--probe-short' in sys.argv:
            # Overhead sessions measure the existing capture route and must
            # not fail because a transient XWayland framebuffer omitted the
            # yellow HUD.  HDBG scene=10 is the runtime readiness contract;
            # visual HUD presence remains mandatory for visual-review routes.
            # SRAM can lag the live emulator until its periodic flush, so the
            # persisted HCAD/fight window below is the final comparability gate.
            pass
        else:
            for attempt in range(5):
                round_path=shot('01_round')
                im=Image.open(round_path).convert('RGB')
                band=im.crop((0,0,im.width,int(im.height*.2)))
                # Compact 16x8 segments contain 64 visible pixels each; two full
                # bars therefore provide roughly 1024 bright pixels before
                # scaling/letterboxing.  Allow a lower bound for partially hidden
                # bars while still rejecting the title/select scenes.
                if sum(r>220 and g>220 and b<230 for r,g,b in band.get_flattened_data())>400:break
                # Confirm both physical ports if a quick host tap was missed.
                time.sleep(1.0)
                tap('a');time.sleep(.5);tap('x');time.sleep(2)
            else:raise RuntimeError('Fight HUD did not appear; do not label zero yellow as KO')
        if '--draw' in sys.argv:
            # A stale START edge can arm the fight free-step panel while the
            # two confirmation ports commit.  B is the documented emergency
            # exit from that panel; harmless during normal gameplay.
            tap('s')
            time.sleep(.5)
        if '--throw-only' in sys.argv:
            # Isolated close-range route: P2 approaches on the real keyboard
            # while P1 emits Y edges.  No position/state/SRAM injection is
            # allowed; this separates throw reachability from the longer
            # guard/projectile choreography below.
            # The yellow HUD is allocated during ROUND; movement is still
            # locked until the intro finishes, so wait for the fight owner to
            # enable input before measuring approach distance.
            time.sleep(5.0)
            # P1 starts on the left.  Walk P1 toward the idle P2 with the
            # canonical P1 direction key, then emit isolated Y edges only
            # after the fighters are in the close-range band.  Keeping Y out
            # of the approach avoids normal attacks consuming the state slot
            # that the throw branch requires.
            # P1's Y is W.  Move P2 left from the right boundary: the mass-box
            # resolver then translates the pair toward the stage interior
            # instead of pinning P1 at x=240/P2=336.  Emit only P1 Y edges at
            # point blank so the route has one input owner for the command.
            key('j', True)
            time.sleep(3.70)
            key('j', False)
            time.sleep(.35)
            # Keep P1's forward edge held while Y is sampled; this satisfies
            # the relative-direction rule even after P2's facing correction.
            key('Right', True)
            for _ in range(12):
                key('w', True); time.sleep(.05); key('w', False); time.sleep(.12)
                shot(f'throw_only_contact_{_}')
            key('Right', False)
            time.sleep(1.0)
            shot('throw_only_result')
            config_file=config/'blastem/blastem.cfg'
            config_sha=hashlib.sha256(config_file.read_bytes()).hexdigest() if config_file.exists() else None
            (DEST/'manifest.json').write_text(json.dumps({
                'rom_sha256': sha, 'rom_bytes': rom.stat().st_size,
                'rom_source': str(rom_source),
                'rom_source_kind': 'diagnostic_override' if '--rom' in sys.argv else 'release_out_rom',
                'scope': 'real_keyboard_throw_only_probe',
                'requested_p1': requested_p1, 'requested_p2': requested_p2,
                'attacker': 1, 'region_requested': region,
                'scenario': 'p2_approach_p1_y_edges',
                'stage': 'SHOWDOWN' if '--showdown' in sys.argv else 'BGB2',
                'config_sha256': config_sha,
                'claims': 'HPRB/HSEM event telemetry only; no gameplay or visual approval'
            }, indent=2)+'\n')
            return
        if '--guard-only' in sys.argv:
            # Isolated guard route: P2 holds the real back direction only
            # across the projectile's expected contact window.  No position,
            # state, meter, SRAM, or event data is injected by the harness.
            time.sleep(4.0)
            key('Down', True); time.sleep(.10); key('Down', False)
            key('Right', True); time.sleep(.10); key('Right', False)
            tap('q')
            # Do not let the back direction move P2 away before the projectile
            # exists.  Enter guard after emission while the defender remains
            # at the natural starting spacing.
            time.sleep(.35)
            key('l', True)
            for frame in range(24):
                shot(f'guard_only_{frame:02}')
                time.sleep(.075)
            key('l', False)
            time.sleep(.5)
            shot('guard_only_result')
            config_file=config/'blastem/blastem.cfg'
            config_sha=hashlib.sha256(config_file.read_bytes()).hexdigest() if config_file.exists() else None
            (DEST/'manifest.json').write_text(json.dumps({
                'rom_sha256': sha, 'rom_bytes': rom.stat().st_size,
                'rom_source': str(rom_source),
                'rom_source_kind': 'diagnostic_override' if '--rom' in sys.argv else 'release_out_rom',
                'scope': 'real_keyboard_guard_only_probe',
                'requested_p1': requested_p1, 'requested_p2': requested_p2,
                'attacker': 1, 'defender': 2, 'region_requested': region,
                'scenario': 'p1_projectile_p2_back_guard',
                'stage': 'SHOWDOWN' if '--showdown' in sys.argv else 'BGB2',
                'config_sha256': config_sha,
                'claims': 'HPRB/HSEM guard telemetry and visual frames only; requires review'
            }, indent=2)+'\n')
            return
        if '--semantics' in sys.argv:
            # Bounded P04 semantic route.  It uses only real controller input
            # and leaves HPRB as the authority for event classes; the route is
            # intentionally not a visual/gameplay approval.
            def qcf(button):
                key('Down', True); time.sleep(.10); key('Down', False)
                key('Right', True); time.sleep(.10); key('Right', False)
                tap(button)
            # RULES=FREE makes the authored Ryo fireball available at round
            # start.  Launch it from the natural 160 px spacing, then let P2
            # enter guard while the projectile is active (the fball branch
            # accepts a longer-distance guard than a body hit).
            qcf('q'); time.sleep(.35)
            key('l', True); time.sleep(1.35); key('l', False); time.sleep(.45)
            # Bring P2 back toward P1 before testing throw.  The preceding
            # guard intentionally holds RIGHT for the projectile; without
            # this return leg P2 is at the stage boundary and a throw attempt
            # would be a range failure rather than a throw/FSM result.
            # Initial world positions are about 160 px apart.  Walking P1
            # into P2 invokes the mass-box resolver and pushes both fighters,
            # preserving the distance.  Move P2 toward P1 instead, then stop
            # before overlap; this leaves the authored P1 hitbox in range.
            # Return P2 from the projectile guard edge, then make a bounded
            # approach with P1.  The runtime accepts the authored 0..100 px
            # body spacing; the short sweeps below are a fallback for small
            # region/input cadence differences.  The
            # direction is held only for a short sweep; it is never written
            # into runtime state.
            # Keep the approach and Y edges concurrent.  Waiting for P2 to
            # stop first lets the mass-box resolver separate the pair again;
            # overlapping the two real inputs guarantees a point-blank edge
            # without writing positions or states from the harness.
            key('j', True)
            for _ in range(40):
                key('w', True); time.sleep(.05); key('w', False); time.sleep(.05)
            key('j', False); time.sleep(.30)
            key('Right', True); time.sleep(.52); tap('w'); time.sleep(.08)
            tap('w'); time.sleep(.08); key('Right', False); time.sleep(.30)
            def throw_sweep(direction, count):
                key(direction, True)
                for _ in range(count):
                    key('w', True); time.sleep(.04); key('w', False); time.sleep(.04)
                    # Keep intermediate frames for the isolated throw route;
                    # the final frame alone can show only the post-contact
                    # spacing and would not be sufficient visual evidence of
                    # the authored grab pose.
                    if '--throw-only' in sys.argv and _ % 4 == 0:
                        shot(f'throw_only_{direction.lower()}_{_}')
                key(direction, False); time.sleep(.30)
            throw_sweep('Right', 36)
            throw_sweep('Left', 36)
            # Start the attack edge before pressing P2's back direction.  If
            # RIGHT is held while the opponent is idle, the legacy FSM walks
            # away; the guard branch is only selected after it sees an active
            # enemy attack.  Keeping both edges in the same short window makes
            # the contact deterministic without moving P2 out of range.
            key('q', True); time.sleep(.06); key('l', True); time.sleep(.25)
            key('q', False); time.sleep(1.0)
            key('l', False); time.sleep(.45)
            # Build a full meter reserve from confirmed body hits before asking
            # the real FSM to accept the projectile command.  Waiting for each
            # attack lifecycle avoids the persistent-hit gate suppressing all
            # but the first contact.
            for _ in range(12): tap('q'); time.sleep(.62)
            # QCF + X (``q``) is the authored special input; A (``a``) is a
            # different attackButton and cannot satisfy the special FSM.  A
            # second attempt documents the accept/deny edge after the first
            # free special has been consumed.
            qcf('q')
            # Keep the real projectile on screen long enough for visual
            # review; the semantic probe is still the authority for whether
            # the FSM accepted it.
            for frame in range(12):
                shot(f'semantics_projectile_{frame:02}')
                time.sleep(.08)
            time.sleep(1.2)
            # Throw uses Y (``w``) and the facing/forward edge.  Keep the
            # direction held across the button press so KEY_PRESSED and the
            # proximity test are sampled in the same logic tick.
            key('Right', True); time.sleep(.12); tap('w'); time.sleep(.25); key('Right', False); time.sleep(.9)
            key('q', True); key('x', True); time.sleep(.12)
            key('q', False); key('x', False); time.sleep(2.5)
            shot('semantics_probe')
            config_file=config/'blastem/blastem.cfg'
            config_sha=hashlib.sha256(config_file.read_bytes()).hexdigest() if config_file.exists() else None
            (DEST/'manifest.json').write_text(json.dumps({
                'rom_sha256': sha, 'rom_bytes': rom.stat().st_size,
                'rom_source': str(rom_source),
                'rom_source_kind': 'diagnostic_override' if '--rom' in sys.argv else 'release_out_rom',
                'scope': 'real_keyboard_combat_semantics_probe',
                'requested_p1': requested_p1, 'requested_p2': requested_p2,
                'attacker': 1, 'region_requested': region,
                'scenario': 'guard_projectile_throw_simultaneous',
                'stage': 'SHOWDOWN' if '--showdown' in sys.argv else 'BGB2',
                'config_sha256': config_sha,
                'semantic_input_script': 'close; P2 guard+P1 punches x3; P1 QCF projectile; P1 forward+Y throw; P1 Q/P2 X simultaneous',
                'claims': 'HPRB event-class telemetry only; requires full gameplay and visual review'
            }, indent=2)+'\n')
            return
        # Window framebuffer only; preserve native aspect/letterbox for audit.
        vlog=(DEST/'video.log').open('w')
        mark_phase('capture_start')
        if '--no-video' not in sys.argv:
            capture_clock['video_started_monotonic_ns']=time.monotonic_ns()
            capture_clock['video_started_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
            video=sp.Popen(['ffmpeg','-y','-f','x11grab','-window_id',win,'-framerate','60','-draw_mouse','0',
                            '-i',os.environ['DISPLAY'],'-an','-fps_mode','passthrough',
                            '-c:v','libx264','-preset','ultrafast','-crf','20',
                            str(DEST/'combat_window.mp4')],stdout=vlog,stderr=vlog)
        if with_audio:
            # Session policy/DSP can ignore PULSE_SINK. Move only the newly
            # created BlastEm stream and verify the actual sink assignment.
            new_inputs=[]
            for _ in range(20):
                new_inputs=[s for s in json.loads(run('pactl','-f','json','list','sink-inputs'))
                            if s['index'] not in existing_audio_inputs and
                            (s.get('properties',{}).get('application.process.binary')=='blastem.bin' or
                             s.get('properties',{}).get('pipewire.access.portal.app_id')=='com.retrodev.blastem')]
                if len(new_inputs)==1: break
                time.sleep(.2)
            if len(new_inputs)!=1:raise RuntimeError('Cannot uniquely identify this emulator audio stream')
            selected_audio_input_index=new_inputs[0]['index']
            run('pactl','move-sink-input',str(selected_audio_input_index),sink)
            alog=(DEST/'audio.log').open('w')
            capture_clock['audio_started_monotonic_ns']=time.monotonic_ns()
            capture_clock['audio_started_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
            audio_capture=sp.Popen(['ffmpeg','-y','-f','pulse','-i',sink+'.monitor','-c:a','pcm_s16le',
                                    str(DEST/'emulator_audio.wav')],stdout=alog,stderr=alog)
            owned_sinks=[s for s in json.loads(run('pactl','-f','json','list','sinks')) if s['name']==sink]
            ids={s['index'] for s in owned_sinks}
            owned_inputs=[]
            for _ in range(10):
                all_owned_inputs=[s for s in json.loads(run('pactl','-f','json','list','sink-inputs')) if s['sink'] in ids]
                # PipeWire can expose a short-lived duplicate stream while
                # the move settles. The BlastEm input index selected above is
                # the identity proof; do not reject a uniquely identified
                # stream merely because a transient sibling is present.
                owned_inputs=[s for s in all_owned_inputs if s['index']==selected_audio_input_index]
                if len(owned_inputs)==1:break
                time.sleep(.2)
            if len(owned_inputs)!=1:
                (DEST/'pulse_sink_inputs_debug.json').write_text(json.dumps({
                    'selected_audio_input_index': selected_audio_input_index,
                    'sink_ids': sorted(ids),
                    'observed_inputs': all_owned_inputs,
                }, indent=2)+'\n')
                raise RuntimeError('Isolated monitor has no uniquely identified emulator stream')
            (DEST/'pulse_sink_inputs.json').write_text(json.dumps(owned_inputs,indent=2)+'\n')
            (DEST/'pulse_sinks.json').write_text(json.dumps(owned_sinks,indent=2)+'\n')
        time.sleep(5)
        if '--probe-short' in sys.argv:
            if '--probe-combat' in sys.argv:
                # Pequena sequência determinística para que o probe observe
                # o caminho real FSM -> colisão -> CombatEvent. Isto não é um
                # KO completo: o runner continua classificando o caso como
                # pending_visual_review e gameplay incompleto.
                for _ in range(3):
                    key('Right', True); time.sleep(.35); key('Right', False)
                    tap('q'); time.sleep(.35)
                for _ in range(2):
                    key('j', True); time.sleep(.25); key('j', False)
                    tap('x'); time.sleep(.30)
            # Short regional probe: allow the ROM to warm up and export HPRB,
            # then close cleanly so BlastEm flushes SRAM without a long match.
            probe_wait=max(1, int(arg_value('--probe-wait', '30')))
            time.sleep(probe_wait)
            shot('probe_short')
            mark_phase('capture_end')
            config_file=config/'blastem/blastem.cfg'
            config_sha=hashlib.sha256(config_file.read_bytes()).hexdigest() if config_file.exists() else None
            (DEST/'manifest.json').write_text(json.dumps({
                'rom_sha256': sha,
                'rom_bytes': rom.stat().st_size,
                'scope': 'real_keyboard_playtest_probe_short',
                'requested_p1': requested_p1,
                'requested_p2': requested_p2,
                'attacker': 1,
                'region_requested': region,
                'scenario': 'probe_short',
                'combat_probe': '--probe-combat' in sys.argv,
                'combat_probe_inputs': 'P1:Right+Q x3; P2:J+X x2' if '--probe-combat' in sys.argv else None,
                'stage': 'SHOWDOWN' if '--showdown' in sys.argv else 'BGB2',
                'h240_requested': '--h240' in sys.argv,
                'config_sha256': config_sha,
                'audio': 'isolated_monitor_captured_not_auditioned' if with_audio else 'not_captured_dummy_driver',
                'audio_wav': 'emulator_audio.wav' if with_audio else None,
                'video': 'combat_window.mp4' if video is not None else None,
                'video_capture_enabled': video is not None,
                'capture_clock': capture_clock,
                'capture_timeline': capture_timeline,
                'phase_clock': phase_clock,
                'runtime_readiness_precheck': probe_short_readiness,
                'title': run('xdotool','getwindowname',win),
                'claims': 'requires visual review; HPRB is a runtime probe, not gameplay coverage'
            }, indent=2)+'\n')
            return
        def specials(label):
            # Match fsm.c: down, forward + punch. Musgo's 700 is a slam,
            # Ryo/Ken's 700 emits a projectile; screenshots require review.
            for player,down,forward,punch in ((1,'Down','Right','q'),(2,'k','j','h')):
                for attempt in range(3):
                    # Let the previous attack lifecycle close so the real
                    # directional buffer starts from neutral.
                    time.sleep(.35)
                    # joyDirTimer is a 12-frame command window. Keep the
                    # complete down -> forward -> punch chord below that
                    # budget; the generic tap() interval is intentionally
                    # not used here because it spends ~14 frames per edge.
                    key(down,True);time.sleep(.080)
                    key(down,False);time.sleep(.040)
                    key(forward,True);time.sleep(.080)
                    key(forward,False);time.sleep(.040)
                    key(punch,True);time.sleep(.080);key(punch,False)
                    # State 700 creates Ryo's fireball at animFrame 12;
                    # sample long enough to include that emission and Musgo's
                    # corresponding slam recovery.
                    for frame in range(24):
                        path=shot(f'{label}_p{player}_try{attempt}_{frame}')
                        special_samples.append({'phase':label,'player':player,'capture':path.name})
                        time.sleep(.075)
                    time.sleep(.8)
        if '--specials-only' in sys.argv:
            # Isolated real-keyboard special probe.  Keep this route separate
            # from KO/throw choreography so a failed QCF cannot be hidden by
            # a later attack, and leave HPRB/HSEM as the runtime authority.
            time.sleep(4.0)
            specials('special_only')
            mark_phase('capture_end')
            config_file=config/'blastem/blastem.cfg'
            config_sha=hashlib.sha256(config_file.read_bytes()).hexdigest() if config_file.exists() else None
            cadence_probe=cadence_snapshot()
            (DEST/'manifest.json').write_text(json.dumps({
                'rom_sha256':sha,'rom_bytes':rom.stat().st_size,
                'scope':'real_keyboard_special_only_probe',
                'requested_p1':requested_p1,'requested_p2':requested_p2,
                'region_requested':region,
                'stage':'SHOWDOWN' if '--showdown' in sys.argv else 'BGB2',
                'config_sha256':config_sha,
                'config_path_present':config_file.exists(),
                'audio':'isolated_monitor_captured_not_auditioned' if with_audio else 'not_captured_dummy_driver',
                'audio_wav':'emulator_audio.wav' if with_audio else None,
                'video':'combat_window.mp4' if video else None,
                'video_capture_enabled':video is not None,
                'runtime_trace':'HDBG_schema_2_live_special_frames+HSTR_schema_1_ring',
                'capture_clock':capture_clock,
                'capture_timeline':capture_timeline,
                'phase_clock':phase_clock,
                'special_samples':special_samples,
                'cadence_probe':cadence_probe,
                'title':run('xdotool','getwindowname',win),
                'claims':'HPRB/HSEM special telemetry and visual frames only; requires review'
            }, indent=2)+'\n')
            return
        if '--specials' in sys.argv:specials('before_reset')
        if '--timeover' in sys.argv:
            def defender_yellow(path):
                im=Image.open(path).convert('RGB');scale=im.width/320
                left,right=(8,136) if p2 else (184,312)
                # The compact HUD has two independent yellow rows: life at
                # the top and special below it.  The old 40px native crop
                # included both rows, so a full special meter made a KO look
                # like a full life bar.  Keep the detector on the life row
                # only. The capture has a top letterbox, so the life strip lands
                # at native y=24..26; include rows through 31 while excluding
                # the special row at y=27.
                roi=im.crop((int(left*scale),0,int(right*scale),int(32*scale)))
                return sum(r>190 and g>190 and b<80 for r,g,b in roi.get_flattened_data())
            baseline=defender_yellow(shot('timeover_before_damage'))
            for attempt in range(20):
                key(move,True);time.sleep(.5);tap(attack);time.sleep(.25);key(move,False)
                health=defender_yellow(shot('timeover_damage_setup'))
                if 0<health<baseline:break
            else:raise RuntimeError('Time-over setup did not produce observed nonlethal damage')
        zeros=0
        terminal_probe=None
        terminal_capture=None
        after_match_capture=None
        rematch_capture=None
        ko_rounds=0
        waiting_round_reset=False
        # The visible clock is the authority for time-over.  Region/audio
        # startup and screenshot overhead can consume different wall-clock
        # amounts, so 95 one-second sleeps are not a safe upper bound for a
        # 99-second round. Keep the route bounded, but wide enough to reach
        # zero before a final screenshot is considered.
        timeout_iterations = 180
        # A long-lived opponent can enter a one-segment recovery cadence after
        # repeated contact. Give the real input route enough time to produce a
        # visible zero; terminal_capture remains the only KO acceptance gate.
        # A full match is two authored rounds.  The old 360-iteration bound
        # could finish immediately after round one and label the still-live
        # fight as a rematch, even though AFTER_MATCH had never been observed.
        # Keep the bound finite, but large enough for two real keyboard rounds.
        match_iterations = 900 if ('--aggressive' in sys.argv and not timeout_test) else 180
        for hit in range(timeout_iterations if timeout_test else match_iterations):
            if waiting_round_reset:
                key(move,False)
                probe=debug_snapshot()
                if probe and probe['scene'] == 11:
                    terminal_probe=probe
                    after_match_capture=shot('after_match_result')
                    break
                # Round reset is scene-owned.  Wait for the next fight's full
                # health before sending another physical attack edge.  SRAM is
                # normally flushed only on clean exit, so the visual route is
                # the live authority and HDBG becomes post-session evidence.
                if probe and probe['scene'] == 10 and probe['p1_energy'] == 96 and probe['p2_energy'] == 96:
                    waiting_round_reset=False
                else:
                    time.sleep(2.5)
                    reset_path=shot(f'round_{ko_rounds}_reset_probe')
                    reset_im=Image.open(reset_path).convert('RGB');reset_scale=reset_im.width/320
                    reset_roi=reset_im.crop((int(left*reset_scale),0,int(right*reset_scale),int(32*reset_scale)))
                    reset_yellow=sum(r>190 and g>190 and b<80 for r,g,b in reset_roi.get_flattened_data())
                    if reset_yellow >= 900:
                        waiting_round_reset=False
                    continue
            # Refresh movement after recovery; wait until the intro has ended.
            if timeout_test:time.sleep(1)
            else:
                key(move,True);time.sleep(.42 if '--aggressive' in sys.argv else .5)
                tap(attack);time.sleep(.25)
                # Sixteen confirmed contacts leave a safe margin for the
                # event gate while filling the real 0..32 meter for the
                # attacking player. Capture the signature special before the
                # KO route consumes the round, rather than pretending a reset
                # round still owns the previous meter.
                if '--specials' in sys.argv and hit == 16:
                    specials('charged_midround')
            if hit%5==0 or (timeout_test and hit>=48):
                path=shot(f'combat_{hit:03}')
                im=Image.open(path).convert('RGB');scale=im.width/320;top=(im.height-224*scale)/2
                left,right=(8,136) if p2 else (184,312)
                # PAL and NTSC have different vertical borders/scales. Restrict
                # x to a health strip and cover the complete upper HUD band.
                roi=im.crop((int(left*scale),0,int(right*scale),int(32*scale)))
                yellow=sum(r>190 and g>190 and b<80 for r,g,b in roi.get_flattened_data())
                samples.append({'step':hit,'defender':1 if p2 else 2,'yellow_pixels':yellow,'capture':path.name,
                                'window_title':run('xdotool','getwindowname',win)})
                print(json.dumps(samples[-1]),flush=True)
                if timeout_test:
                    terminal_probe=debug_snapshot()
                    if terminal_probe and terminal_probe['scene'] == 10:
                        terminal_pair=(terminal_probe['p1_state'], terminal_probe['p2_state'])
                        terminal_pair_seen=(terminal_pair == (615, 615) or
                                            terminal_pair in ((611, 612), (612, 611),
                                                              (611, 100), (100, 611),
                                                              (612, 100), (100, 612)))
                        if terminal_pair_seen:
                            terminal_capture=shot('draw_result' if terminal_pair == (615, 615) else 'timeover_result')
                            break
                # The authored frame keeps warm pixels in its empty caps.  A
                # low internal fill is therefore only a visual candidate; the
                # terminal claim requires the same ROM's SRAM HDBG to report
                # zero health plus an authored KO/victory state.
                zero_candidate=(yellow <= 180)
                if zero_candidate:
                    zeros+=1
                    key(move,False)
                    # The internal fill excludes the persistent caps: 164
                    # warm pixels is the authored empty-frame signature, while
                    # a one-segment fill is already ~324.  This is a visual
                    # candidate only; the final HDBG dump is decoded after the
                    # emulator exits and must agree with the candidate.
                    terminal_capture=shot(f'ko_result_round_{ko_rounds + 1}')
                    ko_rounds+=1
                    if ko_rounds >= 2:
                        # Two round wins must own the result screen before A
                        # can be treated as a rematch input.  The interval is
                        # bounded and intentionally visual; no SRAM control is
                        # used here.
                        time.sleep(12.0)
                        after_match_capture=shot('after_match_result')
                        break
                    waiting_round_reset=True
                    if terminal_capture and '--specials' in sys.argv and ko_rounds == 1:
                        # Preserve the existing isolated special route: after
                        # the first real KO it must prove the round reset before
                        # asking for another special, never treat the reset as
                        # a health refill in the same frame.
                        for attempt in range(20):
                            restored=shot('special_reset_health')
                            im=Image.open(restored).convert('RGB');scale=im.width/320
                            roi=im.crop((int(left*scale),0,int(right*scale),int(32*scale)))
                            if sum(r>190 and g>190 and b<80 for r,g,b in roi.get_flattened_data())>1000:break
                            time.sleep(.5)
                        else: raise RuntimeError('No observed health reset before special test')
                        time.sleep(4);specials('after_reset')
                        break
        key(move,False)
        shot('after_combat')
        # If the second round ended just before the periodic HDBG export, give
        # the runtime a bounded observation window to expose AFTER_MATCH.
        if not after_match_capture and ko_rounds >= 2:
            for _ in range(24):
                terminal_probe=debug_snapshot()
                if terminal_probe and terminal_probe['scene'] == 11:
                    after_match_capture=shot('after_match_result')
                    break
                time.sleep(.25)
        if timeout_test:
            shot('after_timeover_observation')
        elif after_match_capture:
            # A is the actual AFTER_MATCH rematch owner.  Capture only after
            # the visible round surface returns; SRAM may still contain the
            # pre-exit HDBG block and is not a live scene-control channel.
            tap('a')
            time.sleep(2.0)
            rematch_capture=shot('rematch_round')
        elif '--musgo' in sys.argv and '--exit-select' not in sys.argv:
            tap('a');time.sleep(2);shot('rematch_round')
        else:
            tap('Return');time.sleep(2);shot('return_select_or_pause')
        config_file=config/'blastem/blastem.cfg'
        config_sha=hashlib.sha256(config_file.read_bytes()).hexdigest() if config_file.exists() else None
        cadence_probe=cadence_snapshot()
        mark_phase('capture_end')
        (DEST/'manifest.json').write_text(json.dumps({'rom_sha256':sha,'rom_bytes':rom.stat().st_size,
            'scope':'real_keyboard_playtest','requested_p1':requested_p1,'requested_p2':requested_p2,
            'attacker':2 if p2 else 1,'region_requested':region,
                'scenario':'draw' if '--draw' in sys.argv else ('timeover' if timeout_test else 'ko'),
                'stage':'SHOWDOWN' if '--showdown' in sys.argv else 'BGB2',
            'h240_requested': '--h240' in sys.argv,
            'config_sha256':config_sha,
            'config_path_present':config_file.exists(),
            'audio':'isolated_monitor_captured_not_auditioned' if with_audio else 'not_captured_dummy_driver',
            'audio_monitor':sink+'.monitor' if with_audio else None,'samples':samples,'special_samples':special_samples,
            'title':run('xdotool','getwindowname',win),'video':'combat_window.mp4' if video else None,
            'video_capture_enabled':video is not None,
            'capture_clock':capture_clock,
            'capture_timeline':capture_timeline,
            'phase_clock':phase_clock,
            'terminal_probe':terminal_probe,
            'terminal_capture':terminal_capture.name if terminal_capture else None,
            'after_match_capture':after_match_capture.name if after_match_capture else None,
            'rematch_capture':rematch_capture.name if rematch_capture else None,
            'cadence_probe':cadence_probe,
            'ko_rounds_confirmed':ko_rounds,
            'claims':'requires visual review; zero yellow is a candidate, not automatic KO proof'},indent=2)+'\n')
    finally:
        mark_phase('finalization_start')
        for k in ('Right','Down','k','a','q','Return','j','h','t','l','x','g','f2','i'):
            try:key(k,False)
            except sp.CalledProcessError:pass
        if video:
                capture_clock['video_stopped_monotonic_ns']=time.monotonic_ns()
                stop_owned_process(video, 'video')
        if transition_video:
            stop_owned_process(transition_video, 'transition_video')
        if transition_log:
            transition_log.close()
        if audio_capture:
            capture_clock['audio_stopped_monotonic_ns']=time.monotonic_ns()
            stop_owned_process(audio_capture, 'audio')
        # Let BlastEm exit through its own UI path first. SRAM-backed
        # HPRB/HSEM/VLAB snapshots are written by the emulator on clean exit;
        # killing the process immediately after a semantics route can leave a
        # valid framebuffer but no save.sram artifact.
        try:
            if win:
                key('esc', True); time.sleep(.12); key('esc', False)
                time.sleep(.80)
        except Exception:
            pass
        # Only terminate this session's process group, never unrelated emulators.
        try:os.killpg(proc.pid,signal.SIGTERM)
        except ProcessLookupError:pass
        try:proc.wait(timeout=5)
        except sp.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
        mark_phase('finalization_end')
        (DEST/'capture_clock.json').write_text(json.dumps(capture_clock, indent=2)+'\n')
        (DEST/'phase_clock.json').write_text(json.dumps(phase_clock, indent=2)+'\n')
        manifest_path=DEST/'manifest.json'
        if manifest_path.is_file():
            try:
                # BlastEm may return after scheduling its final SRAM write;
                # wait once before the bounded HANC retry so the manifest
                # cannot race the terminal save flush.
                time.sleep(1.0)
                capture_manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
                capture_manifest['runtime_media_marker']=media_marker_snapshot()
                capture_manifest['runtime_media_marker_claim_limit'] = (
                    'runtime marker context only; video PTS/audio sample binding requires '
                    'analyze_media_marker.py and bind_runtime_media_anchor.py')
                manifest_path.write_text(json.dumps(capture_manifest, indent=2)+'\n', encoding='utf-8')
            except (OSError, ValueError, TypeError):
                (DEST/'finalization_warnings.log').open('a').write('manifest runtime marker update failed\n')


if __name__=='__main__':
    try:main()
    finally:
        if AUDIO_MODULE:run('pactl','unload-module',AUDIO_MODULE)
