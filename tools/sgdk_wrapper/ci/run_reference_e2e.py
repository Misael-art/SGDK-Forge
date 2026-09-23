#!/usr/bin/env python3
"""Linux build -> BlastEm -> observed FREF contracts. Not a game quality gate."""
import argparse
import hashlib
import json
import os
import platform
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WRAPPER = ROOT / 'tools/sgdk_wrapper'
REFERENCE = 'SGDK_projects/FORGE_REFERENCE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, default=ROOT / REFERENCE)
    args = parser.parse_args()
    project = args.project_root.resolve()
    if not project.is_dir():
        parser.error('required reference project missing')
    logs = project / 'out/logs'
    logs.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    evidence = project / 'out' / ('blastem_env_e2e_' + run_id)
    report_path = logs / 'reference_e2e_report.json'
    report = {'schema_version': '1.0.0', 'scope': 'technical_fixture_contracts',
              'run_id': run_id, 'status': 'running', 'ready_for_aaa': False,
              'steps': [], 'unproven': ['game_quality', 'audio_quality', 'sustained_performance']}

    def save():
        data = json.dumps(report, indent=2) + '\n'
        (logs / f'reference_e2e_{run_id}_report.json').write_text(data)
        report_path.write_text(data)

    def run(name, command, timeout=180):
        log = logs / f'e2e_{run_id}_{name}.log'
        step = {'name': name, 'command': [str(v) for v in command], 'log': str(log)}
        report['steps'].append(step)
        save()
        print(f'[e2e] {name}', flush=True)
        try:
            with log.open('w') as output:
                process = subprocess.Popen(step['command'], cwd=ROOT, stdout=output,
                                           stderr=subprocess.STDOUT, start_new_session=True)
                started = activity = time.monotonic()
                previous_size = 0
                while process.poll() is None:
                    try:
                        process.wait(timeout=20)
                    except subprocess.TimeoutExpired:
                        size = log.stat().st_size
                        if size != previous_size:
                            activity = time.monotonic()
                            previous_size = size
                        print(f'[e2e] {name}: running; log_bytes={size}', flush=True)
                        if time.monotonic() - started > timeout or time.monotonic() - activity > 120:
                            os.killpg(process.pid, signal.SIGTERM)
                            try:
                                process.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                os.killpg(process.pid, signal.SIGKILL)
                                process.wait()
                            raise RuntimeError(f'{name}: timeout or 120 seconds without log progress')
            step['exit_code'] = process.returncode
            step['status'] = 'passed' if process.returncode == 0 else 'failed'
        except (OSError, RuntimeError) as exc:
            step.update(status='failed', error=str(exc))
        save()
        if step['status'] != 'passed':
            raise RuntimeError(f'{name} failed; see {log}')

    try:
        if platform.system() != 'Linux':
            raise RuntimeError('this runner validates Linux only; use the Windows wrapper on Windows')
        for name, tail in [
            ('adopt_project_methodology', ['-Lifecycle', 'existing']),
            ('validate_project_context', []), ('validate_project_hygiene', []),
            ('validate_project_methodology', []), ('audit_project_learning', ['-Mode', 'Audit'])]:
            run(name, ['pwsh', '-NoProfile', '-File', WRAPPER / (name + '.ps1'),
                       '-ProjectRoot', project, *tail])
        run('preflight', ['pwsh', '-NoProfile', '-File', WRAPPER / 'preflight_host.ps1', '-RepoRoot', ROOT])
        run('fixture_regressions', [sys.executable, WRAPPER / 'ci/test_canonical_fixture_contracts.py'])
        run('build', ['bash', WRAPPER / 'build_sgdk_wine_bridge.sh', '--project-root', project], 1800)
        rom = project / 'out/rom.bin'
        digest = hashlib.sha256(rom.read_bytes()).hexdigest()
        report['rom_sha256'] = digest
        run('capture_route', [sys.executable, WRAPPER / 'select_blastem_capture_route.py',
                             '--repo-root', ROOT, '--project-root', project,
                             '--target-scene', '0', '--output-base', evidence,
                             '--output', logs / 'blastem_capture_route_report.json'])
        run('capture', ['bash', WRAPPER / 'capture_blastem_evidence_linux.sh',
                        '--project-root', project, '--output-base', evidence,
                        '--warmup-seconds', '12'], 180)
        manifests = list(evidence.glob('*/evidence_manifest.json'))
        if len(manifests) != 1:
            raise RuntimeError('expected exactly one fresh capture manifest')
        session = manifests[0].parent
        run('observed_contracts', [sys.executable, WRAPPER / 'canonical_fixture_gate.py',
                                  '--fref-sram', session / 'save.sram', '--rom-path', rom,
                                  '--evidence-manifest', manifests[0],
                                  '--output', session / 'fref_final_gate_report.json'])
        if hashlib.sha256(rom.read_bytes()).hexdigest() != digest:
            raise RuntimeError('ROM changed during capture')
        report.update(status='passed', evidence_manifest=str(manifests[0]))
    except (RuntimeError, OSError, ValueError) as exc:
        report.update(status='blocked', error=str(exc))
    save()
    print(json.dumps({'status': report['status'], 'report': str(report_path)}))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
