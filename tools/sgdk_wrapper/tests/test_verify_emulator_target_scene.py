"""A requested capture state must be observed in the runtime metrics."""
import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "verify_emulator_target_scene.py"
SPEC = importlib.util.spec_from_file_location("verify_emulator_target_scene", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_match_from_vlab_is_released():
    assert MODULE.verify({"vlab": {"scene_id": 2}}, 2)["status"] == "passed"


def test_requested_menu_in_direct_fight_rom_is_blocked():
    result = MODULE.verify({"vlab": {"scene_id": 3}}, 2)
    assert result["status"] == "blocked"
    assert result["reason"] == "runtime_target_scene_mismatch"


def test_missing_id_never_passes():
    assert MODULE.verify({"vlab": {}}, 2)["status"] == "needs_review"
