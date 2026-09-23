#!/usr/bin/env python3
"""Content identity for the SDK consumed by the Wine bridge (no mtime cache)."""
import argparse
import hashlib
import json
from pathlib import Path


def inventory(root, bridge):
    root = Path(root).resolve(strict=True)
    files = []
    for path in sorted(root.rglob('*')):
        if path.is_file():
            files.append({'path': path.relative_to(root).as_posix(),
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    if not files or not (root / 'makefile.gen').is_file():
        raise ValueError('SDK missing makefile.gen or empty')
    payload = {'files': files, 'library_parameters': {'LTO': 0, 'target': 'release'},
               'bridge_sha256': hashlib.sha256(Path(bridge).read_bytes()).hexdigest()}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return {'schema': 'sdk_content_identity.v1', 'sdk_root': str(root),
            'sha256': digest, **payload}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk-root', required=True, type=Path)
    parser.add_argument('--bridge', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    report = inventory(args.sdk_root, args.bridge)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix('.tmp')
    temporary.write_text(json.dumps(report, indent=2) + '\n')
    temporary.replace(args.output)
    print(report['sha256'])


if __name__ == '__main__':
    main()
