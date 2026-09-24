"""Contrato do inventario E1. Fixtures sinteticas, criadas no teste (sem conteudo MUGEN de terceiros)."""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mugen2sgdk_forge import inventory  # noqa: E402

CHAR_DEF = """[Info]
name = "Fixture"
author = "mugen2sgdk_forge tests"
[Files]
cmd = f.cmd
cns = f.cns
sprite = f.sff
"""
STAGE_DEF = "[Info]\nname = Stage\n[BGdef]\nspr = s.sff\n"


def sff_header(v2: bool) -> bytes:
    ver = bytes([0, 0, 0, 2]) if v2 else bytes([0, 1, 0, 1])
    return b"ElecbyteSpr\0" + ver + b"\0" * 16


def make_acervo(root: Path) -> None:
    (root / "chars").mkdir(parents=True)
    (root / "stages").mkdir()
    (root / "fullgames").mkdir()
    with zipfile.ZipFile(root / "chars" / "fixture.zip", "w") as z:
        z.writestr("f.def", CHAR_DEF)
        z.writestr("f.sff", sff_header(v2=False))
        z.writestr("readme.txt", "license: CC0")
    with zipfile.ZipFile(root / "stages" / "st.zip", "w") as z:
        z.writestr("s.def", STAGE_DEF)
        z.writestr("s.sff", sff_header(v2=True))
    (root / "stages" / "broken.zip").write_bytes(b"not a zip")
    with zipfile.ZipFile(root / "fullgames" / "big.zip", "w") as z:
        z.writestr("x.def", CHAR_DEF)


def run(tmp_path: Path, name: str) -> dict:
    out = tmp_path / name
    assert inventory.main([str(tmp_path / "acervo"), "--out", str(out)]) == 0
    return json.loads(out.read_text(encoding="utf-8"))


def test_classifies_formats_and_defs(tmp_path):
    make_acervo(tmp_path / "acervo")
    doc = run(tmp_path, "a.json")
    s = doc["summary"]
    assert s["archives"] == 3  # fullgames ignorado por padrao
    assert s["archives_with_errors"] == 1
    assert s["def_kinds"] == {"character": 1, "stage": 1}
    assert s["sff_versions"] == {"1.0.1.0": 1, "2.0.0.0": 1}
    char = next(a for a in doc["archives"] if a["path"] == "chars/fixture.zip")
    assert char["defs"][0]["info"]["author"] == "mugen2sgdk_forge tests"
    assert char["license_candidates"] == ["readme.txt"]
    # candidato a licenca nunca confirma sozinho
    assert char["license_status"] == "unknown"


def test_deterministic_and_read_only(tmp_path):
    make_acervo(tmp_path / "acervo")
    before = {p: p.read_bytes() for p in (tmp_path / "acervo").rglob("*") if p.is_file()}
    a = (tmp_path / "a.json", run(tmp_path, "a.json"))
    b = (tmp_path / "b.json", run(tmp_path, "b.json"))
    assert hashlib.sha256(a[0].read_bytes()).hexdigest() == hashlib.sha256(b[0].read_bytes()).hexdigest()
    after = {p: p.read_bytes() for p in (tmp_path / "acervo").rglob("*") if p.is_file()}
    assert before == after
