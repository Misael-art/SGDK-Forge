import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "SGDK_projects" / "SMOKE_TEST [VER.001] [SGDK 211] [GEN] [LAB]"
SCENE = PROJECT / "src" / "scenes" / "scene_branding.c"
RES = PROJECT / "res" / "resources.res"


class BrandingV3RuntimeContractTest(unittest.TestCase):
    def test_timeline_and_resources_match_approved_storyboard(self):
        scene = SCENE.read_text(encoding="utf-8")
        resources = RES.read_text(encoding="utf-8")

        self.assertRegex(scene, r"#define BRAND_ENGINE_END 150")
        self.assertRegex(scene, r"#define BRAND_AUTHOR_END 300")
        self.assertRegex(scene, r"#define BRAND_PROJECT_END 480")

        for resource in (
            "img_brand_engine_bg_v3",
            "img_brand_author_bg_v3",
            "img_brand_project_bg_v3",
            "img_brand_engine_logo_v4",
            "img_brand_author_signature_v4",
            "img_brand_project_logo_v4",
            "img_brand_presents_v4",
            "spr_brand_monogram_v3",
            "spr_brand_shield_v3",
            "spr_brand_debris_v3",
        ):
            self.assertIn(resource, resources)
            self.assertIn(resource, scene)

        self.assertIn("PSG_setNoise(PSG_NOISE_TYPE_WHITE, PSG_NOISE_FREQ_CLOCK2)", scene)
        self.assertNotIn("img_brand_fx_tiles", scene)
        self.assertNotRegex(scene, r"PSG_setFrequency\s*\(\s*3\s*,")
        self.assertLess(
            scene.index("sBrandMonogram = SPR_addSprite"),
            scene.index("brandGlowEnter(160, 76)"),
        )


if __name__ == "__main__":
    unittest.main()
