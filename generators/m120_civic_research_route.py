#!/usr/bin/env python3
"""M120 research-only geometric centerline. Never reads/writes Minecraft saves.
This is only the small GitHub-mirrored route definition. Full sculptural M120
3D generator and rendering source are stored in the user's integrated ZIP.
"""
from __future__ import annotations
import json, math
def research_route():
    angle=math.acos((3574.-3703.5)/575)
    end=(3703.5+575*math.cos(angle),-2184.5+319*math.sin(angle),
         -1650+21*math.sin(2.5*angle)+7)
    nodes=[
      ("SB13_PROXY_APPROACH",(4068.,-2348.,-1787.)),
      ("SB13_LIFT_BASE",(4056.,-2348.,-1787.)),
      ("SB13_LIFT_TOP",(4056.,-2348.,-1695.)),
      ("SB09_OUTER_GATE",(3830.,-2348.,-1695.)),
      ("SB10_TRANSIT",(3830.,-2246.,-1695.)),
      ("CENTRAL_CIVIC",(3703.5,-2184.5,-1695.)),
      ("SB07_FORUM",(3574.,-2124.,-1695.)),
      ("SB07_UPPER_LIFT",(3574.,-2124.,end[2])),
      ("SB08_TWIN_VAULTS",(3574.,-2022.,end[2])),
      ("INNER_ORBIT",(end[0],end[1],end[2]))
    ]
    parts=[]
    for i,(a,b) in enumerate(zip(nodes,nodes[1:])):
        p=a[1];q=b[1]
        lift=abs(p[0]-q[0])<1e-5 and abs(p[1]-q[1])<1e-5
        parts.append({"id":"S%02d"%i,"start":p,"end":q,
                      "type":"UNBUILT_LIFT" if lift else "UNBUILT_WALKWAY",
                      "length_m":round(math.dist(p,q),2),
                      "collision_certified":False,"protected_entrance_attached":False,
                      "operational":False})
    return {"phase":"M120","model":"CONTINUOUS_MATH_CENTERLINE_ONLY",
            "station_count":len(nodes),"segment_count":len(parts),"nodes":nodes,"segments":parts,
            "world_write_operations":0,"pedestrian_traversable":False,
            "real_portal_xyz_registered":False,"absolute_Y_to_old_relative_H_registered":False,
            "world_to_modify":None}
if __name__=="__main__":
    d=research_route();print(json.dumps(d,ensure_ascii=False,indent=2))
