#!/usr/bin/env python3
"""Reassemble byte-identical C55-E source GLBs from 2 MiB raw GitHub blob chunks.

Usage:
  python models/RESTORE_ORIGINAL_GLB.py --verify-only
  python models/RESTORE_ORIGINAL_GLB.py --output-dir ./restored-models

Fails closed if any part is missing, malformed or the final SHA-256 is wrong.
Requires only the Python standard library. Never overwrites originals.
"""
from __future__ import annotations
import argparse
import hashlib
import os
import pathlib
import struct
import sys
import tempfile

PART_SIZE = 2 * 1024 * 1024
MODELS = {
    "EA": {
        "filename": "C55E_EA_terra_turn_open_lattice_v2.glb",
        "total_parts": 17,
        "bytes": 35478456,
        "sha256": "42c2cbd1c51389e55d57b6c2f998a8ecce5219454382a99c16f3c9672024f6d9",
    },
    "EB": {
        "filename": "C55E_EB_yori_well_v3.glb",
        "total_parts": 26,
        "bytes": 53010436,
        "sha256": "01ea7a7f5865c569ac41d1e1946cfa366125872f83a058d4759ab341d57b58e2",
    },
}
PARTS = pathlib.Path(__file__).resolve().parent / "parts"

def restore(label, outdir, verify_only):
    spec = MODELS[label]
    missing = [f"{label}_{i:03d}.bin" for i in range(spec["total_parts"])
               if not (PARTS / f"{label}_{i:03d}.bin").is_file()]
    if missing:
        raise RuntimeError(f"{label}: {len(missing)} required binary chunks missing: " + ", ".join(missing))
    h = hashlib.sha256()
    n = 0
    first = b""
    out = None
    temp_path = None
    try:
        if not verify_only:
            outdir.mkdir(parents=True, exist_ok=True)
            dst = outdir / spec["filename"]
            if dst.exists():
                raise FileExistsError(f"Refusing to overwrite existing file: {dst}")
            fd, t = tempfile.mkstemp(prefix=f"verify_{label}_",suffix=".tmp",dir=outdir)
            temp_path = pathlib.Path(t)
            out = os.fdopen(fd, "wb")
        for i in range(spec["total_parts"]):
            chunk = (PARTS / f"{label}_{i:03d}.bin").read_bytes()
            correct = min(PART_SIZE, spec["bytes"] - i * PART_SIZE)
            if len(chunk) != correct:
                raise ValueError(f"{label} chunk {i:03d} size {len(chunk)} != {correct}")
            if i == 0:
                first = chunk[:12]
            n += len(chunk)
            h.update(chunk)
            if out:
                out.write(chunk)
        actual = h.hexdigest()
        if n != spec["bytes"] or actual != spec["sha256"]:
            raise ValueError(f"{label}: byte/SHA mismatch {n} / {actual}; expected {spec['bytes']} / {spec['sha256']}")
        if len(first) != 12 or first[:4] != b"glTF" or struct.unpack("<I",first[4:8])[0] != 2 or struct.unpack("<I",first[8:12])[0] != n:
            raise ValueError(f"{label}: invalid GLB magic/version/declared length")
        if out:
            out.close()
            out = None
            temp_path.replace(dst)
        print(f"PASS: {label} {n} bytes SHA256={actual}" + (f" -> {dst}" if not verify_only else ""))
    finally:
        if out:
            out.close()
        if temp_path and temp_path.exists():
            temp_path.unlink()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", type=pathlib.Path, default=pathlib.Path("./restored-models"))
    p.add_argument("--verify-only", action="store_true")
    p.add_argument("--model", choices=("EA","EB","all"), default="all")
    args = p.parse_args()
    labels = MODELS if args.model == "all" else [args.model]
    status = 0
    for label in labels:
        try:
            restore(label, args.output_dir, args.verify_only)
        except (OSError, ValueError, RuntimeError) as e:
            print(f"NOT RESTORED: {e}", file=sys.stderr)
            status = 1
    return status

if __name__ == "__main__":
    sys.exit(main())
