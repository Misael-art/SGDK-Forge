import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen

CHAR_INDEX = {"o": 1, "h": 2, "m": 3, "k": 4, "d": 5, "s": 6, "l": 7,
              "r": 8, "t": 9, "u": 10, "q": 11, "w": 12, "v": 13, "n": 14, "i": 15}


def api(base, route, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(base + route, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def actions_from_plan(plan, spec):
    colors = {entry["index"]: entry["hex"] for entry in spec["palette"]}
    width, height = spec["canvas"]["width"], spec["canvas"]["height"]
    actions = []
    occupied = set()
    overwrites = 0
    for stroke in plan["strokes"]:
        x0, y = stroke["x"], stroke["y"]
        pixels = stroke["pixels"]
        if not isinstance(x0, int) or not isinstance(y, int) or y < 0 or y >= height:
            raise ValueError("stroke outside canvas")
        for offset, symbol in enumerate(pixels):
            x = x0 + offset
            if x < 0 or x >= width:
                raise ValueError(f"stroke outside canvas at {x},{y}")
            if symbol == ".":
                continue
            if symbol not in CHAR_INDEX:
                raise ValueError(f"unknown authoring symbol {symbol!r}")
            key = (x, y)
            if key in occupied:
                overwrites += 1
            occupied.add(key)
            actions.append({"kind": "pencil", "x": x, "y": y, "color": colors[CHAR_INDEX[symbol]]})
    return actions, overwrites


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:8765")
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--restore-log", type=Path)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    if plan.get("asset_id"):
        spec["asset_id"] = plan["asset_id"]
    print(api(args.base, "/api/session", {"spec": spec}))
    if args.restore_log:
        print(api(args.base, "/api/restore", {"action_log": json.loads(args.restore_log.read_text(encoding="utf-8"))}))
    actions, overwrites = actions_from_plan(plan, spec)
    print({"plan_actions": len(actions), "intentional_layer_overwrites": overwrites})
    print(api(args.base, "/api/apply", {"actions": actions}))
    print(api(args.base, "/api/validate", {}))
    print(api(args.base, "/api/export", {"name": args.name, "target_dir": spec["export_dir"]}))


if __name__ == "__main__":
    main()
