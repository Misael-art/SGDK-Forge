import unittest
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[3]


class ChaseV009RuntimeContractTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (PROJECT / relative_path).read_text(encoding="utf-8")

    def test_resources_promote_v009_assets(self):
        resources = self.read("res/resources.res")
        for symbol in (
            "spr_chase_hero_run_v009",
            "spr_chase_hero_ghost_v009",
            "spr_chase_pursuer_head_v009",
            "spr_chase_pursuer_claw_v009",
            "spr_chase_energy_star_v009",
            "spr_chase_pulse_impact_v009",
            "spr_chase_cloud_v009",
            "ts_chase_letterbox_v009",
        ):
            self.assertIn(symbol, resources)

    def test_scene_owns_safe_v009_composition(self):
        scene = self.read("src/scenes/scene_chase.c")
        self.assertIn("CHASE_ROAD_enter", scene)
        self.assertIn("VDP_setHilightShadow", scene)
        self.assertNotIn("sBgBScroll -=", scene)

    def test_pursuer_is_modular_in_runtime(self):
        pursuer = self.read("src/gameplay/chase_pursuer.c")
        for symbol in (
            "spr_chase_pursuer_torso_v011",
            "spr_chase_pursuer_head_v009",
            "spr_chase_pursuer_claw_v009",
        ):
            self.assertIn(symbol, pursuer)

    def test_player_owns_afterimages(self):
        player = self.read("src/gameplay/chase_player.c")
        self.assertIn("spr_chase_hero_ghost_v009", player)

    def test_letterbox_uses_auditable_resident_tile_fill(self):
        road = self.read("src/gameplay/chase_road.c")
        self.assertIn("VDP_fillTileMap(VDP_BG_A", road)
        self.assertNotIn("VDP_fillTileMapRect(", road)


if __name__ == "__main__":
    unittest.main()
