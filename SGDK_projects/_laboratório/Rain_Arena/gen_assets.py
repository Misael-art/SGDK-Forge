import os
from PIL import Image, ImageDraw
import random

random.seed(7)

MD_VALUES = (0x00, 0x22, 0x44, 0x66, 0x88, 0xAA, 0xCC, 0xEE)
MAGENTA = (0xFF, 0x00, 0xFF)


def snap_channel(value):
    return min(MD_VALUES, key=lambda candidate: abs(candidate - value))


def snap_color(color):
    return tuple(snap_channel(channel) for channel in color)


def save_md_background(image, output_path, colors=15):
    indexed = image.convert('P', palette=Image.ADAPTIVE, colors=colors)
    palette = indexed.getpalette()
    used_indices = sorted(set(indexed.tobytes()))

    for index in used_indices[:16]:
        r, g, b = palette[index * 3:index * 3 + 3]
        sr, sg, sb = snap_color((r, g, b))
        palette[index * 3:index * 3 + 3] = [sr, sg, sb]

    indexed.putpalette(palette)
    indexed.save(output_path)


def save_md_sprite(image, output_path, visible_colors):
    indexed = Image.new('P', image.size, 0)
    palette = [0] * 768
    palette[0:3] = list(MAGENTA)

    color_to_index = {}
    for offset, color in enumerate(visible_colors, start=1):
        snapped = snap_color(color)
        color_to_index[color] = offset
        palette[offset * 3:offset * 3 + 3] = list(snapped)

    pixels = []
    source_pixels = image.load()
    width, height = image.size
    for y in range(height):
        for x in range(width):
            pixel = source_pixels[x, y]
            if pixel == MAGENTA:
                pixels.append(0)
            else:
                pixels.append(color_to_index[pixel])

    indexed.putpalette(palette)
    indexed.putdata(pixels)
    indexed.info['transparency'] = 0
    indexed.save(output_path, transparency=0)

res_dir = 'res'
if not os.path.exists(res_dir):
    os.makedirs(res_dir)

# BASE PALETTE (Unified Dark Cyan/Blue + White Flash)
# We limit the colors to enforce SGDK 15-color hardware limits natively.

sky = Image.new('RGB', (320, 224), color=(10, 15, 30))
d = ImageDraw.Draw(sky)

for y in range(0, 160, 4):
    cloud_brightness = max(0, 40 - (y // 4))
    fill_col = (cloud_brightness, cloud_brightness + 10, cloud_brightness + 30)
    for x in range(0, 320, 2):
        if random.randint(0, 3) > 0:
            d.point((x + (y % 2), y), fill=fill_col)
            d.point((x + (y % 2) + 1, y), fill=fill_col)

save_md_background(sky, os.path.join(res_dir, 'sky.png'))

temple = Image.new('RGB', (320, 224), color=snap_color((10, 15, 30)))
d = ImageDraw.Draw(temple)

for y in range(180, 224):
    col = (20 + (y-180), 30 + (y-180), 50 + (y-180))
    d.line([(0, y), (320, y)], fill=col)

pillar_color = (20, 25, 30)
highlight_color = (40, 55, 65)

def draw_pillar(x_start, width):
    d.rectangle([x_start, 50, x_start+width, 180], fill=pillar_color)
    d.line([(x_start, 50), (x_start, 180)], fill=highlight_color, width=2)
    for py in range(50, 180, 2):
        for px in range(x_start+2, x_start+width, 2):
            if random.randint(0, 5) > 3:
                d.point((px + (py % 2), py), fill=highlight_color)

draw_pillar(40, 60)
draw_pillar(220, 60)

d.rectangle([20, 30, 300, 50], fill=(15, 20, 25))
d.line([(20, 30), (300, 30)], fill=highlight_color, width=1)

save_md_background(temple, os.path.join(res_dir, 'temple.png'))

rain = Image.new('RGB', (64, 16), color=MAGENTA)
d = ImageDraw.Draw(rain)
rain_col = (180, 210, 230)

d.line([8, 0, 12, 6], fill=rain_col, width=1)
d.line([22, 10, 25, 14], fill=rain_col, width=1)
d.line([36, 14, 40, 10], fill=rain_col, width=1)
d.line([40, 14, 44, 10], fill=rain_col, width=1)
d.point((38, 12), fill=rain_col)
d.point((42, 12), fill=rain_col)
d.point((50, 8), fill=rain_col)
d.point((58, 8), fill=rain_col)

save_md_sprite(rain, os.path.join(res_dir, 'rain_sprite.png'), [rain_col])

print("Visual Cohesion Assets Generated: Wet Stone Dither, Parallax Base, Splash Frames (16x16).")
