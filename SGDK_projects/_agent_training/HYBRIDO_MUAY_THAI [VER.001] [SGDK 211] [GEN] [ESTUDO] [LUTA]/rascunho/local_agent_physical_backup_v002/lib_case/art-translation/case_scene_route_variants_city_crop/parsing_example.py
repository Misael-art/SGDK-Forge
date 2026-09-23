"""
Pedagogical example for route exploration on a fixed scene crop.

This is not a production converter.
It exists to teach the agent that alternative routes are a controlled comparison
exercise, not a free-for-all redraw.
"""

CASE = {
    "slug": "case_scene_route_variants_city_crop",
    "source_taxonomy": "palette_separated_panorama",
    "fixed_contract": {
        "scene_geometry": "locked",
        "shared_canvas_contract": "locked",
        "translation_target": "scene_slice",
        "palette_ceiling": "15 visible colors + transparency when needed",
    },
    "routes": [
        {
            "id": "route_a_high_key_haze",
            "kind": "production_candidate",
            "varies": ["sky_story", "global_temperature", "ambient_haze"],
            "keeps": ["geometry", "crop", "focal_corner", "street_mass_distribution"],
            "status": "survivor_candidate",
        },
        {
            "id": "route_b_high_key_duplicate",
            "kind": "duplicate_alias",
            "same_as": "route_a_high_key_haze",
            "status": "collapse",
        },
        {
            "id": "route_c_cool_evening",
            "kind": "production_candidate",
            "varies": ["sky_story", "thermal_separation", "bg_b_weight"],
            "keeps": ["geometry", "crop", "focal_corner", "street_mass_distribution"],
            "status": "survivor_candidate",
        },
        {
            "id": "route_d_grid_alignment",
            "kind": "diagnostic_board",
            "varies": ["overlay_grid"],
            "keeps": ["all_scene_content"],
            "status": "debug_only",
        },
    ],
    "expected_outputs": [
        "route_exploration_board",
        "route_comparison_matrix",
        "route_decision_record",
        "locked_visual_direction",
    ],
}


def summarize_case():
    survivors = [
        route["id"]
        for route in CASE["routes"]
        if route["status"] == "survivor_candidate"
    ]
    return {
        "slug": CASE["slug"],
        "survivors": survivors,
        "duplicates_removed": [
            route["id"] for route in CASE["routes"] if route["status"] == "collapse"
        ],
        "debug_boards": [
            route["id"] for route in CASE["routes"] if route["status"] == "debug_only"
        ],
    }


if __name__ == "__main__":
    import json

    print(json.dumps(summarize_case(), indent=2))
