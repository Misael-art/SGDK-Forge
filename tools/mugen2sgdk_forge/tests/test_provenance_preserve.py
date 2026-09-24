"""Reconversao nao apaga decisao humana (followup_pr20_b54a82db.md): nota e restricao sobrevivem,
reconversao identica e idempotente, pixel novo exige nova aprovacao, simbolo removido fica no historico."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mugen2sgdk_forge import provenance as prov  # noqa: E402


def _proj(tmp: Path) -> Path:
    (tmp / "res" / "mugen" / "x").mkdir(parents=True)
    (tmp / "doc" / "mugen").mkdir(parents=True)
    (tmp / "res" / "mugen" / "x" / "a.png").write_bytes(b"pixels-v1")
    (tmp / "res" / "mugen" / "x" / "b.png").write_bytes(b"pixels-b")
    return tmp


def _entries(syms=("a", "b")):
    return [prov.entry(f"mg_x_{s}", "SPRITE", f"mugen/x/{s}.png", "gen", "pkg.zip", "0" * 64, f"derivado {s}")
            for s in syms]


def _manifest(p: Path) -> dict:
    return {e["res_symbol"]: e for e in json.loads((p / "doc/asset_provenance_manifest.json").read_text())["entries"]}


def _files(p: Path) -> dict:
    return {f: (p / f).read_bytes() for f in ("doc/asset_provenance_manifest.json", prov.ANNOTATIONS,
                                              "doc/mugen/x_audio_provenance.json") if (p / f).exists()}


def test_manual_edit_in_manifest_is_captured_not_lost(tmp_path):
    p = _proj(tmp_path)
    prov.write_visual(p, "mg_x_", _entries())
    m = json.loads((p / "doc/asset_provenance_manifest.json").read_text())
    for e in m["entries"]:
        if e["res_symbol"] == "mg_x_a":
            e["notes"] += "; aprovacao visual pendente"               # edicao a mao, como no Ken
    (p / "doc/asset_provenance_manifest.json").write_text(json.dumps(m))
    prov.write_visual(p, "mg_x_", _entries())                        # reconversao
    assert "aprovacao visual pendente" in _manifest(p)["mg_x_a"]["notes"]
    ann = prov.load_annotations(p)["symbols"]["mg_x_a"]
    assert "aprovacao visual pendente" in ann["human_notes"]


def test_human_note_and_restriction_survive_and_rerun_is_idempotent(tmp_path):
    p = _proj(tmp_path)
    prov.write_visual(p, "mg_x_", _entries())
    ann = prov.load_annotations(p)
    ann["symbols"]["mg_x_b"] = {"human_notes": ["revisado por direcao de arte"],
                                "restrictions": ["nao redistribuir fora do repositorio"]}
    (p / prov.ANNOTATIONS).write_text(json.dumps(ann))
    prov.write_visual(p, "mg_x_", _entries())
    prov.write_audio(p, "x", "pkg.zip", "0" * 64, [{"res_symbol": "mg_x_snd", "asset_path": "s.wav", "notes": "som"}])
    first = _files(p)
    n = _manifest(p)["mg_x_b"]["notes"]
    assert "revisado por direcao de arte" in n and "restricao: nao redistribuir fora do repositorio" in n
    prov.write_visual(p, "mg_x_", _entries())
    prov.write_audio(p, "x", "pkg.zip", "0" * 64, [{"res_symbol": "mg_x_snd", "asset_path": "s.wav", "notes": "som"}])
    assert _files(p) == first                                         # idempotente, byte a byte


def test_changed_pixels_do_not_inherit_approval(tmp_path):
    p = _proj(tmp_path)
    import hashlib
    h1 = hashlib.sha256(b"pixels-v1").hexdigest()
    prov.write_visual(p, "mg_x_", _entries())
    ann = prov.load_annotations(p)
    ann["symbols"]["mg_x_a"] = {"approvals": [{"status": "final", "asset_sha256": h1, "by": "humano"}]}
    (p / prov.ANNOTATIONS).write_text(json.dumps(ann))
    prov.write_visual(p, "mg_x_", _entries())
    assert _manifest(p)["mg_x_a"]["acceptance_status"] == "final"      # aprovado para ESTE hash
    (p / "res/mugen/x/a.png").write_bytes(b"pixels-v2")               # pixel mudou
    prov.write_visual(p, "mg_x_", _entries())
    assert _manifest(p)["mg_x_a"]["acceptance_status"] == "placeholder"
    sym = prov.load_annotations(p)["symbols"]["mg_x_a"]
    assert sym["approvals"][0]["asset_sha256"] == h1                  # aprovacao historica preservada
    assert any(h["event"] == "approval_stale" and h["approved_sha256"] == h1 for h in sym["history"])


def test_removed_symbol_is_recorded_and_bad_status_rejected(tmp_path):
    p = _proj(tmp_path)
    prov.write_visual(p, "mg_x_", _entries())
    prov.write_visual(p, "mg_x_", _entries(("a",)))                  # b sumiu na reconversao
    hist = prov.load_annotations(p)["symbols"]["mg_x_b"]["history"]
    assert any(h["event"] == "removed" and h["asset_path"] == "mugen/x/b.png" for h in hist)
    ann = prov.load_annotations(p)
    ann["symbols"]["mg_x_a"] = {"approvals": [{"status": "aprovadao", "asset_sha256": "x"}]}
    (p / prov.ANNOTATIONS).write_text(json.dumps(ann))
    with pytest.raises(ValueError):
        prov.write_visual(p, "mg_x_", _entries(("a",)))
