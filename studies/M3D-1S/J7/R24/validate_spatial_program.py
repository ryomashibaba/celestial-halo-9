"""R24 design-stage graph checks only. NOT geometry/visibility/walkability/art QA.
Run: python validate_spatial_program.py
No third-party dependencies; no writes.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict, deque
from pathlib import Path

p = Path(__file__).with_name("R24_SPATIAL_PROGRAM.json")
doc = json.loads(p.read_text(encoding="utf-8"))
assert doc["status"] == "UNBUILT_CONCEPT_GRAPH_ONLY"
assert doc["coordinates"] == "ISOLATED_RESEARCH_VIRTUAL_FRAME_UNAPPROVED_NOT_CITY_MASTER"
assert doc["restrictions"]["official_art_adoptions"] == 0
assert doc["restrictions"]["minecraft_build"] == "HOLD"
assert doc["validation_claims"]["walkable_or_transit_routes_exist_in_geometry"] is False
assert doc["validation_claims"]["visibility_not_yet_tested"] is True

nodes = doc["nodes"]
edges = doc["edges"]
idx = {n["id"]: n for n in nodes}
assert len(idx) == len(nodes)
assert set(n["district"] for n in nodes) == {d["id"] for d in doc["districts"]}
assert len(doc["districts"]) >= 3 and len(doc["public_voids"]) >= 2
for n in nodes:
    assert n["program"].strip() and len(n["xyz_m"]) == 3
    assert all(math.isfinite(v) for v in n["xyz_m"])

adj = defaultdict(list)
unique_pairs = set()
for e in edges:
    a, b = e["a"], e["b"]
    assert a in idx and b in idx and a != b
    k = frozenset((a, b))
    assert k not in unique_pairs
    unique_pairs.add(k)
    assert e["mode"] in {"pedestrian", "public_transfer", "vertical_transit"}
    assert e["alignment_geometry_verified"] is False
    direct = math.dist(idx[a]["xyz_m"], idx[b]["xyz_m"])
    assert abs(e["conceptual_straight_line_distance_m"] - direct) <= .51
    adj[a].append(b)
    adj[b].append(a)

seen = set()
q = deque([nodes[0]["id"]])
while q:
    u = q.popleft()
    if u in seen:
        continue
    seen.add(u)
    q.extend(v for v in adj[u] if v not in seen)
assert len(seen) == len(nodes)
cycle_rank = len(edges) - len(nodes) + 1
assert cycle_rank >= 2

def route_ok(route):
    assert len(route) >= 2
    assert all(node in idx for node in route)
    assert all(frozenset((a, b)) in unique_pairs for a, b in zip(route, route[1:]))

routes = doc["experience_routes"]
route_ok(routes["primary"]["nodes"])
route_ok(routes["branch_west"]["nodes"])
route_ok(routes["branch_east"]["nodes"])
assert routes["primary"]["nodes"][0] == "N00"
assert routes["primary"]["nodes"][-1] == "N10"
assert len({idx[n]["district"] for n in routes["primary"]["nodes"]}) >= 3
length = sum(
    round(math.dist(idx[a]["xyz_m"], idx[b]["xyz_m"]))
    for a, b in zip(routes["primary"]["nodes"], routes["primary"]["nodes"][1:])
)
assert routes["primary"]["estimated_unbuilt_straight_segment_sum_m"] == length
assert routes["primary"]["routing_distance_is_not_actual_road_length"] if (
    "routing_distance_is_not_actual_road_length" in routes["primary"]
) else doc["validation_claims"]["routing_distance_is_not_actual_road_length"]

for camera in doc["camera_test_hypotheses"]:
    assert camera["from"] in idx and camera["look_at"] in idx
    assert set(camera["desired_visible_worlds"]) <= {d["id"] for d in doc["districts"]}
    assert camera["desired_visible_anchor"] in idx

facts = doc["validation_claims"]
assert facts["node_count"] == len(nodes)
assert facts["edge_count"] == len(edges)
assert facts["connected_all_nodes"] is True
assert facts["connected_component_count"] == 1
assert facts["cycle_rank"] == cycle_rank
assert facts["district_count"] == len(doc["districts"])
assert facts["primary_route_graph_exists"] is True

print(json.dumps(
    {"R24_DESIGN_GRAPH": "PASS", "nodes": len(nodes), "edges": len(edges),
     "districts": len(doc["districts"]), "cycle_rank": cycle_rank,
     "estimated_unbuilt_straight_segment_sum_m": length,
     "NOT_TESTED": ["actual_mesh", "passable_routes", "visible_districts", "art"]},
    ensure_ascii=False
))
