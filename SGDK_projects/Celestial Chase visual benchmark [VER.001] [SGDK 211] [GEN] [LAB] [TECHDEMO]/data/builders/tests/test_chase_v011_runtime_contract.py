import unittest
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[3]


class ChaseV011RuntimeContractTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (PROJECT / relative_path).read_text(encoding="utf-8")

    def test_obstacles_use_one_shared_depth_state(self):
        obstacles = self.read("src/gameplay/chase_obstacles.c")
        for token in (
            "obstacleZ",
            "CHASE_OBSTACLE_DEPTH_Y",
            "CHASE_OBSTACLE_LANE_SPREAD",
            "CHASE_OBSTACLE_SCALE_FRAME",
            "CHASE_OBSTACLE_CONTACT_Z_MIN",
            "CHASE_OBSTACLE_CONTACT_Z_MAX",
        ):
            self.assertIn(token, obstacles)
        self.assertNotIn("slot->y +=", obstacles)
        self.assertNotIn("slot->y >=", obstacles)

    def test_scale_upload_is_bounded(self):
        obstacles = self.read("src/gameplay/chase_obstacles.c")
        scene = self.read("src/scenes/scene_chase.c")
        self.assertIn("scaleUploadConsumed", obstacles)
        self.assertIn("allowScaleUpload", obstacles)
        self.assertIn("CHASE_OBSTACLES_update(&sRules, (sMotionFrame & 3u) == 2u)", scene)

    def test_scene_passes_chase_mode_to_rules_reset(self):
        scene = self.read("src/scenes/scene_chase.c")
        self.assertIn("CHASE_RULES_reset(&sRules, gApp.targetFps, gApp.chaseMode)", scene)

    def test_resources_promote_v011_depth_assets(self):
        resources = self.read("res/resources.res")
        for symbol in (
            "img_chase_bg_b_v011",
            "img_chase_bg_a_v011",
            "spr_chase_obstacle_boulder_v011",
            "spr_chase_obstacle_brand_v011",
            "spr_chase_pursuer_torso_v011",
            "spr_chase_contact_shadow_v011",
            "ts_chase_hud_font_v011",
        ):
            self.assertIn(symbol, resources)

    def test_extended_backgrounds_use_centered_base_scroll(self):
        road = self.read("src/gameplay/chase_road.c")
        scene = self.read("src/scenes/scene_chase.c")
        self.assertIn("#define CHASE_ROAD_BASE_HSCROLL -96", road)
        self.assertIn("CHASE_ROAD_BASE_HSCROLL + bend - streak + shakeX", road)
        self.assertIn("img_chase_bg_b_v011", scene)
        self.assertIn("img_chase_bg_a_v011", scene)
        self.assertIn("VDP_fillTileMap(VDP_BG_A, tile, firstRow, planeWidth)", road)

    def test_pursuer_rig_clamps_head_inside_collar_overlap(self):
        pursuer = self.read("src/gameplay/chase_pursuer.c")
        for token in (
            "CHASE_PURSUER_HEAD_Y_OFFSET -18",
            "CHASE_PURSUER_HEAD_SWING_SHIFT 2",
            "CHASE_PURSUER_BOB_SHIFT 2",
            "spr_chase_pursuer_torso_v011",
        ):
            self.assertIn(token, pursuer)

    def test_contact_shadows_are_owned_by_runtime_actors(self):
        obstacles = self.read("src/gameplay/chase_obstacles.c")
        player = self.read("src/gameplay/chase_player.c")
        pursuer = self.read("src/gameplay/chase_pursuer.c")
        self.assertIn("slot->shadow", obstacles)
        self.assertIn("sPlayerShadow", player)
        self.assertIn("sClawShadowNear", pursuer)
        self.assertIn("sClawShadowFar", pursuer)

    def test_runtime_probe_measures_hardware_sprite_spans(self):
        probe = self.read("src/system/runtime_probe.c")
        self.assertIn("measure_max_scanline_sprites", probe)
        self.assertIn("FrameVDPSprite", probe)
        self.assertIn("firstSprite", probe)
        self.assertIn("PROBE_SCANLINE_SAMPLE_GROUPS 4", probe)
        self.assertIn("PROBE_SCANLINE_GROUP_LENGTH", probe)
        self.assertNotIn("s_scanlinePressure", probe)
        self.assertNotIn("SPR_getUsedVDPSprite", probe)
        self.assertNotIn("usedVdpSprites > 20", probe)

    def test_scene_regression_uses_sram_capture_hold(self):
        probe = self.read("src/system/runtime_probe.c")
        app = self.read("src/core/app.c")
        manifest = self.read("doc/scene-regression.json")
        self.assertIn("PROBE_SCENE_BOOTSTRAP_HOLD_VERSION 2", probe)
        self.assertIn("MDRuntimeProbe_shouldHoldScene", app)
        self.assertIn('"capture_hold_frame": 120', manifest)

    def test_hud_loads_custom_font_and_restores_default(self):
        hud = self.read("src/gameplay/chase_hud.c")
        self.assertIn("VDP_loadFont(&ts_chase_hud_font_v011, CPU)", hud)
        self.assertIn("VDP_loadFont(&font_default, CPU)", hud)


if __name__ == "__main__":
    unittest.main()
