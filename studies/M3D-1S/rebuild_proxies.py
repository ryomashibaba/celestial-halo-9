#!/usr/bin/env python3
"""Rebuild HALO-9 M3D-1S non-art 10km world scale proxies from scenarios.json.

Generated objects are only geometric volume comparison fixtures, NOT finished art.
Safe default: refuses to write into an existing output directory.
No Blender/Minecraft/Unreal access, no third-party libraries, no network calls.
"""
import argparse
import json
import math
from pathlib import Path


SEGMENTS = 28
N = 41


def loft_obj(scenario):
    """Build true OBJ vertices/faces for deliberately crude comparison envelopes."""
    lines = [
        "# HALO-9 M3D-1S scale-envelope proxy",
        "## RESEARCH ONLY / NOT architectural art / no interior geometry",
        "## Units metres, Z-up, local abstract W0 frame; not canonical world alignment",
        "# VARIANT " + scenario["key"],
    ]
    vertices = 0
    faces = 0
    points = []
    for component in scenario["components"]:
        lines.append("o " + component["name"])
        lines.append("g " + component["mat"])
        starts = []
        for ti, ring in enumerate(component["rings"]):
            z, cx, cy, rx, ry = ring
            starts.append(vertices + 1)
            for j in range(SEGMENTS):
                a = j * 2 * math.pi / SEGMENTS
                organic = 1 + .027 * math.sin(3 * a + ti * .36) + .018 * math.cos(5 * a - ti * .42)
                v = (cx + rx * organic * math.cos(a), cy + ry * organic * math.sin(a), z)
                points.append(v)
                vertices += 1
                lines.append("v " + " ".join(f"{q:.3f}" for q in v))
        bottom = starts[0]
        for j in range(1, SEGMENTS - 1):
            lines.append(f"f {bottom} {bottom + j + 1} {bottom + j}")
            faces += 1
        for ti in range(len(starts) - 1):
            b, e = starts[ti], starts[ti + 1]
            for j in range(SEGMENTS):
                k = (j + 1) % SEGMENTS
                lines.extend((f"f {b+j} {b+k} {e+k}", f"f {b+j} {e+k} {e+j}"))
                faces += 2
        top = starts[-1]
        for j in range(1, SEGMENTS - 1):
            lines.append(f"f {top} {top+j} {top+j+1}")
            faces += 1
    return "\n".join(lines) + "\n", vertices, faces, points


def common_context():
    lines = [
        "# 10km city common context / broad W0 attributes ONLY",
        "# NOT CANONICAL WORLD COORDINATES OR SURVEYED TERRAIN",
        "# North mountains; west escarpment; east water depression; SW intentional void.",
        "o COMMON_W0_ABSTRACT_TERRAIN",
    ]
    for j in range(N):
        y = -5000 + j * 10000 / (N - 1)
        for i in range(N):
            x = -5000 + i * 10000 / (N - 1)
            base = 38 + 65 * math.sin(x / 870) * math.cos(y / 930)
            north = ((180 + 900 * ((y - 2400) / 2600) ** 1.4)
                     * (.8 + .2 * math.cos(x / 800))) if y > 2400 else 0
            west = ((560 + 280 * math.sin(y / 700))
                    * min(1, (-3400-x) / 600)) if x < -3400 else 0
            sea = -190 if x > 3150 and abs(y) < 2200 else 0
            sw = (-450 * min(1, (-2100-x) / 800, (-1850-y) / 850)
                  if x < -2100 and y < -1850 else 0)
            z = base + north + west + sea + sw
            lines.append(f"v {x:.3f} {y:.3f} {z:.3f}")
    for j in range(N-1):
        for i in range(N-1):
            a = j * N + i + 1
            b, c, d = a + 1, a + N, a + N + 1
            lines.extend((f"f {a} {b} {d}", f"f {a} {d} {c}"))
    lines.append("# 1000m vertical scale marker (not a modeled city facility)")
    origin = N*N + 1
    for z in range(0, 5000, 1000):
        lines.append(f"v 4800 -4800 {z}")
    for i in range(4):
        lines.append(f"l {origin+i} {origin+i+1}")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="New output directory only")
    args = ap.parse_args()
    folder = Path(args.out)
    if folder.exists():
        raise SystemExit("Refusing to overwrite existing output directory")
    source_dir = Path(__file__).resolve().parent
    data = json.loads((source_dir / "scenarios.json").read_text(encoding="utf-8"))
    manifest = json.loads((source_dir / "measured_manifest.json").read_text(encoding="utf-8"))
    folder.mkdir(parents=True, exist_ok=False)
    summary = []
    for scenario in data["variants"]:
        obj, vcount, fcount, points = loft_obj(scenario)
        expected = next(x for x in manifest["variants"] if x["id"] == scenario["key"])
        assert vcount == expected["vertices"] and fcount == expected["faces"]
        dims = [
            max(v[k] for v in points) - min(v[k] for v in points)
            for k in range(3)
        ]
        for actual, documented in zip(dims,
            (expected["dimensions_m"]["width"],
             expected["dimensions_m"]["depth"],
             expected["dimensions_m"]["height"])):
            if abs(actual - documented) > .005:
                raise AssertionError(f"dimension mismatch: {scenario['key']}")
        (folder / (scenario["key"] + ".obj")).write_text(obj, encoding="utf-8")
        summary.append({"id": scenario["key"], "vertices": vcount,
                        "faces": fcount, "dimensions_m": dims})
    (folder / "COMMON_W0_NONCANONICAL_CONTEXT.obj").write_text(
        common_context(), encoding="utf-8")
    (folder / "rebuild_result.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OK — Generated only scale-envelope research OBJ files; no art acceptance.")


if __name__ == "__main__":
    main()
