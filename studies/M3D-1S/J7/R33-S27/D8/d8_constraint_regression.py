"""R33-S27-D8: independent GLB-level constraint-regression smoke test.
After extracting R33_S27_D8_CHAT_RESEARCH.zip:
  pip install numpy trimesh
  python d8_constraint_regression.py path/to/R33_S27_D8_CHAT/models
This does not prove urban quality, walkability or Blender direct vertex editing.
"""
from pathlib import Path
import sys, json, numpy as np, trimesh

DIR=Path(sys.argv[1])
STAGES=("BASE","PUBLIC_FORUM_EDIT","HABITAT_EDIT","EXTERIOR_TARGET_EDIT")
G={k:trimesh.load(DIR/f"D8_{k}.glb",force="scene").geometry for k in STAGES}
def geometry_motion(stage,key):
    a=np.asarray(G["BASE"][key].vertices)
    b=np.asarray(G[stage][key].vertices)
    if a.shape!=b.shape:raise RuntimeError("Topology changed; per-vertex comparison invalid")
    motion=np.linalg.norm(b-a,axis=1)
    return float(motion.max())
def xs_at(stage,key,y):
    m=G[stage][key]
    v=np.asarray(m.vertices)
    ys=np.unique(np.round(v[:,1],6))
    mins=[];maxs=[]
    for yy in ys:
        row=v[np.abs(v[:,1]-yy)<1e-5,0]
        mins.append(row.min());maxs.append(row.max())
    return float(np.interp(y,ys,mins)),float(np.interp(y,ys,maxs))
q={}
for k,g in G.items():
    q[k]={"mesh_count":len(g),"watertight":sum(m.is_watertight for m in g.values()),
          "winding_consistent":sum(m.is_winding_consistent for m in g.values()),
          "positive_volume":sum(m.volume>0 for m in g.values())}
    assert q[k]["mesh_count"]==64 and all(q[k][n]==64 for n in ("watertight","winding_consistent","positive_volume"))
q["public_edit"]={
  "west_wall_motion_m":geometry_motion("PUBLIC_FORUM_EDIT","L_lower_outer_urban_fabric"),
  "west_floor_motion_m":geometry_motion("PUBLIC_FORUM_EDIT","L_lower_public_floor"),
  "east_wall_motion_m":geometry_motion("PUBLIC_FORUM_EDIT","R_lower_outer_urban_fabric"),
  "east_floor_motion_m":geometry_motion("PUBLIC_FORUM_EDIT","R_lower_public_floor")}
q["habitat_edit"]={
  "west_upper_wall_m":geometry_motion("HABITAT_EDIT","L_upper_outer_urban_fabric"),
  "west_upper_floor_m":geometry_motion("HABITAT_EDIT","L_upper_public_floor")}
_,bx=xs_at("BASE","R_lower_outer_urban_fabric",110)
_,ax=xs_at("EXTERIOR_TARGET_EDIT","R_lower_outer_urban_fabric",110)
bi,bo=xs_at("BASE","R_lower_public_floor",110)
ai,ao=xs_at("EXTERIOR_TARGET_EDIT","R_lower_public_floor",110)
q["inverse_facade_edit"]={"outer_move_m":ax-bx,"public_room_width_move_m":(ao-ai)-(bo-bi)}
assert abs((ax-bx)-22)<.5
assert abs((ax-bx)-((ao-ai)-(bo-bi)))<.02
assert all(v>2 for v in q["public_edit"].values())
assert all(v>2 for v in q["habitat_edit"].values())
print(json.dumps(q,ensure_ascii=False,indent=2))
print("GEOMETRY CONSTRAINT REGRESSION: LIMITED PASS. ART UNVERIFIED.")
