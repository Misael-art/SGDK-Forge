#!/usr/bin/env python3
"""Generate the provisional provenance register for the imported legacy art.

The source package does not carry producer records or source-art hashes.  The
register therefore keeps every imported visual asset at ``placeholder`` until
the author supplies a stronger lineage record; it never promotes these assets
to a final AAA claim.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

VISUAL_KINDS = {"IMAGE", "SPRITE", "TILESET", "TILEMAP", "MAP", "BITMAP", "PALETTE"}
ENTRY_RE = re.compile(
    r'^\s*(?P<kind>[A-Z][A-Z0-9_]*)\s+(?P<symbol>[A-Za-z_][A-Za-z0-9_]*)\s+'
    r'(?:(?:"(?P<quoted>[^"]+)")|(?P<plain>\S+))'
)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: generate_provenance_manifest.py PROJECT_ROOT")
    root = Path(sys.argv[1]).resolve()
    entries = []
    for res_file in sorted((root / "res").rglob("*.res")):
        for raw in res_file.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.split("//", 1)[0].strip()
            match = ENTRY_RE.match(line)
            if not match or match.group("kind") not in VISUAL_KINDS:
                continue
            entries.append({
                "res_symbol": match.group("symbol"),
                "res_kind": match.group("kind"),
                "asset_path": match.group("quoted") or match.group("plain"),
                "source_kind": "hand_authored_pixel",
                "acceptance_status": "placeholder",
                "generated_by": "legacy_asset_import_from_user_source",
                "notes": (
                    "Imported from the user-provided legacy BLAZE_ENGINE source. "
                    "Producer lineage is not independently verified; placeholder "
                    "status deliberately blocks final AAA visual promotion."
                ),
            })

    manifest = {
        "schema_version": "1.0.0",
        "project_name": root.name,
        "declared_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "validator_fixture": False,
        "entries": entries,
    }
    output = root / "doc" / "asset_provenance_manifest.json"
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "entries": len(entries)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
