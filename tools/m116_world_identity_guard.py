#!/usr/bin/env python3
"""CELESTIAL HALO-9 read-only save identity preflight.

This is NOT a world writer or an authorization provider.
All construction invocations are unconditionally rejected in this phase.
A world display name is not a stable save identity; a level.dat hash is a
time-sensitive fingerprint, not a globally unique Minecraft world ID.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "survey" / "identity" / "M116_world_candidates.json"

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def inspect(world_dir, registry):
    result = {
        "operation": "READ_ONLY_INSPECT",
        "match": "UNIDENTIFIED",
        "record_id": None,
        "role": None,
        "identity_proven": False,
        "model_H_to_world_Y_verified": False,
        "construction_permitted": False,
        "world_file_writes": 0,
    }
    try:
        folder = Path(world_dir).expanduser().resolve(strict=True)
        if not folder.is_dir():
            raise ValueError("not a directory")
        level = folder / "level.dat"
        if not level.is_file():
            raise FileNotFoundError("missing level.dat")
        digest = sha256_file(level)
    except (OSError, ValueError) as exc:
        result["match"] = "UNREADABLE_OR_INVALID"
        result["reason"] = type(exc).__name__
        return result
    result["observed_save_folder"] = folder.name
    result["observed_level_dat_sha256"] = digest
    parts = tuple(part.casefold() for part in folder.parts)
    path_matches = [
        entry for entry in registry["known_saves"]
        if parts[-len(entry["save_folder_tail"]):] ==
        tuple(part.casefold() for part in entry["save_folder_tail"])
    ]
    for entry in path_matches:
        if digest == entry["level_dat_sha256"].casefold():
            result.update({
                "match": "FOLDER_AND_SNAPSHOT_MATCH_READ_ONLY",
                "record_id": entry["id"],
                "role": entry["role"],
                "screenshot_match": entry["screenshot_match"],
                "important": "Fingerprint comparison only: not proof of active world",
            })
            return result
    if path_matches:
        result.update({
            "match": "KNOWN_FOLDER_DIFFERENT_SNAPSHOT",
            "important": "Normal Minecraft play can change level.dat; re-review; no automatic target switch",
        })
    else:
        result["match"] = "UNREGISTERED_FOLDER"
    return result

def require_construction_permission(*_args, **_kwargs):
    """Fail closed: this repository has no authorized live-world writer."""
    return False

def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only Minecraft save identification")
    parser.add_argument("--world", required=True, help="Exact selected save folder")
    parser.add_argument("--mode", choices=("inspect", "construct"), default="inspect")
    args = parser.parse_args(argv)
    if args.mode == "construct":
        print(json.dumps({"status":"BLOCKED","reason":"NO_APPROVED_LIVE_WORLD_OR_CONSTRUCTION",
                          "world_files_changed":False}, indent=2))
        return 3
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    result = inspect(args.world, registry)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["match"] == "FOLDER_AND_SNAPSHOT_MATCH_READ_ONLY" else 2

if __name__ == "__main__":
    raise SystemExit(main())
