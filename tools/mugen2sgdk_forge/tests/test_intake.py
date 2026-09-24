"""Indice de intake: gerado das fontes; o lint pega deriva, owner fantasma e promocao sem canon."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mugen2sgdk_forge import intake  # noqa: E402


def _repo(tmp: Path, lessons: list[dict], adjudication: list[dict]) -> Path:
    (tmp / "doc/curation/2026_01_01").mkdir(parents=True)
    (tmp / "tools/sgdk_wrapper/.agent/skills/code/real-skill").mkdir(parents=True)
    (tmp / "tools/sgdk_wrapper/.agent/skills/code/real-skill/SKILL.md").write_text("x")
    (tmp / "doc/curation/lessons_x_mugen.json").write_text(json.dumps({"lessons": lessons}))
    (tmp / "doc/curation/2026_01_01/lesson_adjudication.json").write_text(json.dumps({"lessons": adjudication}))
    subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
    return tmp


def _les(i, owner="real-skill"):
    return {"id": i, "lesson": "l", "proposed_owner": owner, "canonized_in": "", "enforcement_state": "candidate"}


class IntakeIndex(unittest.TestCase):
    def test_clean_then_drift(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _repo(Path(t), [_les("a")], [{"id": "a", "verdict": "qualificar", "next_action": "G03",
                                                 "promotion": "pending_human_review", "canonized_in": []}])
            self.assertTrue(intake.check(repo))  # indice ainda nao gerado
            intake.write(repo)
            self.assertEqual(intake.check(repo), [])
            row = json.loads((repo / intake.INDEX_JSON).read_text())["lessons"][0]
            self.assertEqual((row["status"], row["owner_path"], row["source_commit"]),
                             ("qualificar", "tools/sgdk_wrapper/.agent/skills/code/real-skill/SKILL.md", "uncommitted"))
            # status mudou na fonte e ninguem regenerou: deriva
            adj = repo / "doc/curation/2026_01_01/lesson_adjudication.json"
            adj.write_text(adj.read_text().replace("qualificar", "rejeitar"))
            self.assertTrue(any("desatualizado" in p for p in intake.check(repo)))

    def test_ghost_owner_and_promotion_without_canon(self):
        with tempfile.TemporaryDirectory() as t:
            repo = _repo(Path(t), [_les("a", owner="nao-existe"), _les("b")],
                         [{"id": "b", "verdict": "confirmar", "promotion": "promoted", "canonized_in": []}])
            intake.write(repo)
            probs = intake.check(repo)
            self.assertTrue(any("'nao-existe' nao existe" in p for p in probs))
            self.assertTrue(any("b: promocao 'promoted' sem canonized_in" in p for p in probs))


if __name__ == "__main__":
    unittest.main()
