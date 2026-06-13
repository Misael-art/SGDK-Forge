import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from mugen_sff.def_stage import parse_stage_def


class TestStageDef(unittest.TestCase):
    def test_showdown_layers_and_action(self) -> None:
        stage_def = ROOT / "rascunho" / "inputs" / "showdown.def"
        stage = parse_stage_def(stage_def)
        self.assertEqual(len(stage.bgs), 4)
        self.assertIn(2, stage.actions)
        self.assertEqual(len(stage.actions[2]), 4)
        self.assertEqual(stage.actions[2][0].group, 2)
        self.assertEqual(stage.actions[2][0].index, 0)
        self.assertEqual(stage.zoffset, 215)
        self.assertEqual(stage.camera_startx, 0)
        self.assertEqual(stage.camera_starty, 0)
        self.assertEqual(stage.camera_boundleft, -224)
        self.assertEqual(stage.camera_boundright, 224)
        self.assertEqual(stage.camera_boundhigh, -240)
        self.assertEqual(stage.camera_boundlow, 0)
        self.assertEqual(stage.verticalfollow, 0.5)
        self.assertEqual(stage.bgs[1].start_x, 0)
        self.assertEqual(stage.bgs[1].start_y, 240)
        self.assertEqual(stage.bgs[1].delta_x, 0.71)
        self.assertEqual(stage.bgs[1].delta_y, 0.635)
        self.assertEqual(stage.bgs[1].tile_x, 0)
        self.assertEqual(stage.bgs[1].tile_y, 0)
        self.assertEqual(stage.bgs[3].mask, 1)


if __name__ == "__main__":
    unittest.main()
