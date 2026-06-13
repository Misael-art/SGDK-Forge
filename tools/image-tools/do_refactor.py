import sys
from pathlib import Path

script_path = Path("f:/Projects/MegaDrive_DEV/tools/image-tools/generate_metal_slug_translation_case.py")
content = script_path.read_text("utf-8")

# 1. Add import for sgdk_semantic_parser near top
if "import sgdk_semantic_parser" not in content:
    content = content.replace("import numpy as np\n", "import numpy as np\nimport sgdk_semantic_parser\n")

# 2. Replace build_layer_*_source
def replace_func(func_name, new_impl):
    global content
    lines = content.splitlines()
    start_idx = -1
    for i, line in enumerate(lines):
        if line.startswith(f"def {func_name}("):
            start_idx = i
            break
    if start_idx == -1: return
    end_idx = start_idx + 1
    while end_idx < len(lines) and (lines[end_idx].startswith(" ") or lines[end_idx] == ""):
        end_idx += 1
    lines[start_idx:end_idx] = new_impl.splitlines()
    content = "\n".join(lines) + "\n"

# Rewrite build_layer_*_source to use A, B, C boxes explicitly
replace_func("build_layer_a_source", """def build_layer_a_source(source: Image.Image) -> Image.Image:
    return sgdk_semantic_parser.extract_region(source, A_BOX).resize(TARGET_SIZE, Image.Resampling.LANCZOS)
""")

replace_func("build_layer_b_source", """def build_layer_b_source(source: Image.Image) -> Image.Image:
    # Scale to canvas keeping it anchored appropriately or just squashing to target size
    return sgdk_semantic_parser.extract_region(source, B_BOX).resize(TARGET_SIZE, Image.Resampling.LANCZOS)
""")

replace_func("build_layer_c_source", """def build_layer_c_source(source: Image.Image) -> Image.Image:
    img = sgdk_semantic_parser.extract_region(source, C_BOX)
    # We want to put C at the bottom of TARGET_SIZE, just like in original scale
    # But since TARGET_SIZE is generic, we just resize directly as before, but from C_BOX
    img = img.resize((TARGET_SIZE[0], int(TARGET_SIZE[1] * (img.height / TARGET_SIZE[1]))), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", TARGET_SIZE, (0, 0, 0, 0))
    canvas.alpha_composite(img, (0, TARGET_SIZE[1] - img.height))
    return canvas
""")

# Delete fake heuristic functions (we just make them empty shells if they are still called, or rewrite basics)
replace_func("build_architecture_alpha", """def build_architecture_alpha(image: Image.Image) -> Image.Image:
    return sgdk_semantic_parser.mask_from_isolated_region(image)
""")

replace_func("build_debris_alpha", """def build_debris_alpha(image: Image.Image) -> Image.Image:
    return sgdk_semantic_parser.mask_from_isolated_region(image)
""")

# Rewrite basic_layer_a_rgba
replace_func("basic_layer_a_rgba", """def basic_layer_a_rgba(source: Image.Image) -> Image.Image:
    sky = build_layer_a_source(source)
    sky = ImageEnhance.Color(sky).enhance(0.9)
    sky = ImageEnhance.Contrast(sky).enhance(0.9)
    return sky
""")

# Rewrite basic_layer_b_rgba
replace_func("basic_layer_b_rgba", """def basic_layer_b_rgba(source: Image.Image) -> Image.Image:
    city = build_layer_b_source(source)
    city_mask = sgdk_semantic_parser.mask_from_isolated_region(city)
    city = apply_alpha_mask(city, city_mask)
    return city
""")

# Rewrite basic_layer_c_rgba
replace_func("basic_layer_c_rgba", """def basic_layer_c_rgba(source: Image.Image) -> Image.Image:
    fg = build_layer_c_source(source)
    mask = sgdk_semantic_parser.mask_from_isolated_region(fg)
    bg = apply_alpha_mask(fg, mask)
    return bg
""")

# Rewrite elite_layer_a_rgba
replace_func("elite_layer_a_rgba", """def elite_layer_a_rgba(source: Image.Image) -> Image.Image:
    sky = build_layer_a_source(source)
    sky = ImageEnhance.Color(sky).enhance(1.04)
    sky = ImageEnhance.Contrast(sky).enhance(1.1)
    sky = ImageEnhance.Brightness(sky).enhance(0.98)
    
    warm_horizon = vertical_gradient_mask(TARGET_SIZE, start=0.0, end=0.22, power=2.2)
    sky = apply_overlay(sky, (238, 136, 34), warm_horizon)
    return sky
""")

# Rewrite elite_layer_b_rgba
replace_func("elite_layer_b_rgba", """def elite_layer_b_rgba(source: Image.Image) -> Image.Image:
    city = build_layer_b_source(source)
    city_mask = sgdk_semantic_parser.mask_from_isolated_region(city)
    city = apply_alpha_mask(city, city_mask)
    city = ImageEnhance.Color(city).enhance(0.8)
    city = ImageEnhance.Contrast(city).enhance(1.24)
    city = ImageEnhance.Brightness(city).enhance(0.9)
    return city
""")

# Rewrite elite_layer_c_rgba
replace_func("elite_layer_c_rgba", """def elite_layer_c_rgba(source: Image.Image) -> Image.Image:
    fg = build_layer_c_source(source)
    mask = sgdk_semantic_parser.mask_from_isolated_region(fg)
    fg = apply_alpha_mask(fg, mask)
    fg = ImageEnhance.Color(fg).enhance(0.78)
    fg = ImageEnhance.Contrast(fg).enhance(1.2)
    return fg
""")

script_path.write_text(content, "utf-8")
print("Refactoring complete.")
