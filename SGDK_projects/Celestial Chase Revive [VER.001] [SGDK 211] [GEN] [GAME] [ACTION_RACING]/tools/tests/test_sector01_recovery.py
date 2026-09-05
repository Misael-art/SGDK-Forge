from pathlib import Path
import json
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]


class Sector01RecoveryTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def generated_animation_frame_count(self, resource_name, animation_index):
        symbols = self.read("out/symbol.txt")
        pattern = re.compile(
            rf"\b{re.escape(resource_name)}_animation{animation_index}_frame(\d+)$"
        )
        frame_indexes = []
        for line in symbols.splitlines():
            match = pattern.search(line)
            if match:
                frame_indexes.append(int(match.group(1)))
        self.assertTrue(
            frame_indexes,
            f"No generated frames found for {resource_name} animation {animation_index}",
        )
        return max(frame_indexes) + 1

    def test_road_tiles_use_declared_user_vram_base(self):
        source = self.read("src/race/road_renderer.c")
        self.assertIn("#define TILE_USER_BASE TILE_USER_INDEX", source)
        self.assertIn("VDP_loadTileSet(img_road_tiles.tileset, TILE_USER_BASE", source)
        self.assertIn(
            "TILE_ATTR_FULL(PAL2, FALSE, FALSE, FALSE, base + tile)", source
        )
        self.assertIn(
            "TILE_ATTR_FULL(PAL2, FALSE, FALSE, FALSE, base + TILE_ROAD_DARK)",
            source,
        )
        self.assertNotIn("VDP_drawImageEx(BG_B, (Image*)&img_road_tiles", source)

    def test_title_images_do_not_share_tile_zero(self):
        source = self.read("src/scenes/title_scene.c")
        self.assertIn("TITLE_BG_TILE_BASE", source)
        self.assertIn("TITLE_LOGO_TILE_BASE", source)
        self.assertNotIn("TILE_ATTR(PAL1, FALSE, FALSE, FALSE)", source)

    def test_sprite_definition_failure_is_not_ignored(self):
        source = self.read("src/scenes/race_scene.c")
        self.assertIn("set_sprite_definition_checked", source)
        self.assertNotIn("SPR_setDefinition(sp, def);", source)
        self.assertNotIn(
            "if ((sp == NULL) || !e->active)\n        {\n            SPR_setVisibility(sp, HIDDEN);",
            source,
        )

    def test_resource_cooldown_ticks_each_frame(self):
        header = self.read("src/race/race_resources.h")
        source = self.read("src/race/race_resources.c")
        scene = self.read("src/scenes/race_scene.c")
        self.assertIn("void Resources_update(void);", header)
        self.assertIn("void Resources_update(void)", source)
        self.assertIn("Resources_update();", scene)

    def test_trigger_events_are_spawned_and_pressure_gate_is_applied(self):
        entities = self.read("src/race/race_entities.c")
        scene = self.read("src/scenes/race_scene.c")
        resources = self.read("src/race/race_resources.c")
        self.assertNotIn("else\n    {\n        return;\n    }", entities)
        self.assertIn("case EV_PRESSURE_GATE", scene)
        self.assertIn("void Resources_addPressure(u8 amount)", resources)

    def test_hud_owns_window_plane(self):
        hud = self.read("src/race/race_hud.c")
        scene = self.read("src/scenes/race_scene.c")
        self.assertIn("VDP_setWindowOnTop(3);", hud)
        self.assertIn("VDP_setTextPlane(WINDOW);", hud)
        self.assertIn("VDP_setTextPriority(TRUE);", hud)
        self.assertIn("#define HUD_BG_TILE_ATTR", hud)
        self.assertIn(
            "VDP_fillTileMapRect(WINDOW, HUD_BG_TILE_ATTR, 0, 0, 40, 3);",
            hud,
        )
        self.assertNotIn("VDP_clearTextArea", hud)
        self.assertIn("VDP_setTextPlane(WINDOW);", scene)
        self.assertIn(
            "SPR_addSprite(&spr_lio_all, 148, 140, "
            "TILE_ATTR(PAL1, FALSE, FALSE, FALSE))",
            scene,
        )
        self.assertIn(
            "SPR_addSprite(&spr_low_stone, 0, 0, "
            "TILE_ATTR(PAL3, FALSE, FALSE, FALSE))",
            scene,
        )
        self.assertIn(
            "SPR_addSprite(&spr_lumen_orb, 0, 0, "
            "TILE_ATTR(PAL3, FALSE, FALSE, FALSE))",
            scene,
        )
        self.assertGreaterEqual(
            scene.count("if (py < TRACK_PLAYFIELD_TOP)"),
            2,
        )
        self.assertIn("VDP_setTextPriority(FALSE);", scene)

    def test_jump_offset_is_not_cast_to_unsigned_or_applied_twice(self):
        scene = self.read("src/scenes/race_scene.c")
        self.assertNotIn("u8 phase = Player_getVisualYOffset();", scene)
        self.assertIn("SPR_setPosition(player_sprite, px, py);", scene)

    def test_lumen_orb_frame_selection_matches_rescomp_definition(self):
        scene = self.read("src/scenes/race_scene.c")
        generated_frames = self.generated_animation_frame_count("spr_lumen_orb", 0)

        self.assertEqual(3, generated_frames)
        self.assertIn("get_definition_frame_count", scene)
        self.assertIn("def->animations[0]->numFrame", scene)
        self.assertNotIn("case EV_LUMEN_ORB: return 4;", scene)
        self.assertNotIn("(e->kind == EV_BEACON_KEY) ? 3 : 4", scene)

    def test_metrics_preserve_success_failure_without_pressure_overflow(self):
        header = self.read("src/race/race_metrics.h")
        metrics = self.read("src/race/race_metrics.c")
        race = self.read("src/scenes/race_scene.c")

        self.assertIn("static u32 pressure_sum", metrics)
        self.assertIn("bool sector_cleared;", header)
        self.assertIn("bool cleared", header)
        self.assertIn("sector_cleared = cleared;", metrics)
        self.assertIn(
            "Metrics_raceComplete(final_int, final_lum, max_pressure_value, "
            "pulse_used_count, race_state == RSTATE_CLEAR);",
            race,
        )

    def test_result_scene_distinguishes_success_and_failure(self):
        result = self.read("src/scenes/result_scene.c")

        self.assertIn("result_data.sector_cleared", result)
        self.assertIn('"SECTOR 01 COMPLETE"', result)
        self.assertIn('"SECTOR 01 FAILED"', result)

    def test_compiled_scene_contracts_cover_runtime_scene_enum(self):
        contract = json.loads(
            (ROOT / "doc/scene-contracts.json").read_text(encoding="utf-8-sig")
        )
        scenes = {entry["scene_id"]: entry for entry in contract["scenes"]}
        expected = {
            "branding_sigil": 0,
            "title_menu": 1,
            "opening_catalyst_cutscene": 2,
            "sector_01_farol_quebrado": 3,
            "ending_result": 4,
            "credits_roll": 5,
        }

        for scene_id, app_scene_id in expected.items():
            self.assertIn(scene_id, scenes)
            self.assertEqual(
                app_scene_id, scenes[scene_id].get("expected_app_scene_id")
            )
            self.assertEqual("sram_bootstrap", scenes[scene_id].get("boot_mode"))

    def test_qa_bootstrap_is_validated_and_normal_boot_is_preserved(self):
        header = self.read("inc/system/qa_bootstrap.h")
        source = self.read("src/system/qa_bootstrap.c")
        main = self.read("src/main.c")

        self.assertIn("PROJECT_QA_BOOTSTRAP_SRAM_OFFSET 0x120u", header)
        self.assertIn("QA_BOOTSTRAP_CHECKSUM_SEED 0xA55Au", source)
        self.assertIn("'S'", source)
        self.assertIn("'B'", source)
        self.assertIn("'I'", source)
        self.assertIn("scene_id < APP_SCENE_COUNT", source)
        self.assertIn("QA_bootstrapResolve(APP_SCENE_BRANDING)", main)
        self.assertIn("SM_init(initial_scene);", main)

    def test_runtime_probe_exports_canonical_mdrt_and_vlab(self):
        header = self.read("inc/system/runtime_probe.h")
        source = self.read("src/system/runtime_probe.c")
        main = self.read("src/main.c")

        self.assertIn("#define MD_RUNTIME_PROBE_MAX_SAMPLES 1800u", header)
        self.assertIn("#define MD_RUNTIME_PROBE_SRAM_OFFSET 0x200u", header)
        self.assertIn("#define MD_RUNTIME_PROBE_VLAB_OFFSET 0x000u", header)
        self.assertIn("'M'", source)
        self.assertIn("'D'", source)
        self.assertIn("'R'", source)
        self.assertIn("'T'", source)
        self.assertIn("'V'", source)
        self.assertIn("'L'", source)
        self.assertIn("'A'", source)
        self.assertIn("'B'", source)
        self.assertIn("SYS_getCPULoad()", source)
        self.assertIn("SPR_getUsedVDPSprite()", source)
        self.assertIn("measure_max_scanline_sprites", source)
        self.assertIn("MDRuntimeProbe_init();", main)
        self.assertIn("MDRuntimeProbe_tick();", main)

    def test_success_route_uses_targeted_sdl_input_without_rebuilding(self):
        route = self.read("tools/run_sector01_blastem_route.ps1")

        self.assertIn("PostMessage", route)
        self.assertIn("WM_KEYDOWN", route)
        self.assertIn("WM_KEYUP", route)
        self.assertIn("SBIS", route)
        self.assertIn("race_start.png", route)
        self.assertIn("race_mid.png", route)
        self.assertIn("beacon_approach.png", route)
        self.assertIn("result_complete.png", route)
        self.assertIn("title_return.png", route)
        self.assertIn("visual_vdp_dump.bin", route)
        self.assertNotIn("build.bat", route.lower())


if __name__ == "__main__":
    unittest.main()
