from pathlib import Path
import struct

from PIL import Image


def plte_entries(path: Path) -> int | None:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    i = 8
    while i + 8 <= len(data):
        length = struct.unpack(">I", data[i : i + 4])[0]
        ctype = data[i + 4 : i + 8]
        if ctype == b"PLTE":
            return length // 3
        i = i + 12 + length
    return None


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    paths = list((root / "res" / "sprites" / "hibrido").glob("*.png")) + list(
        (root / "data" / "processed" / "model_sheets").glob("*.png")
    )

    valid = {0x00, 0x22, 0x44, 0x66, 0x88, 0xAA, 0xCC, 0xEE}
    bad: list[tuple[str, str, object]] = []

    for p in paths:
        img = Image.open(p)
        if img.mode != "P":
            bad.append((p.name, "mode", img.mode))
            continue

        pal = img.getpalette()[:48]
        cols = [tuple(pal[i : i + 3]) for i in range(0, 48, 3)]
        if len(cols) != 16:
            bad.append((p.name, "palette_len", len(cols)))

        for r, g, b in cols:
            if r not in valid or g not in valid or b not in valid:
                bad.append((p.name, "rgb_not_9bit_grid", (r, g, b)))
                break

        w, h = img.size
        if (w % 8) or (h % 8):
            bad.append((p.name, "dimension_not_8px_aligned", (w, h)))

        n = plte_entries(p)
        if n is None:
            bad.append((p.name, "missing_plte", None))
        elif n > 16:
            bad.append((p.name, "plte_entries_gt_16", n))

    print("checked", len(paths), "bad", len(bad))
    for item in bad:
        print(item[0], item[1], item[2])

    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
