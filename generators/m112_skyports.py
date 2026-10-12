#!/usr/bin/env python3
"""M112: proposed vertical skyports. Pure Python, zero Minecraft access."""
from __future__ import annotations
from generators.m111_grand_skybridges import option_b,endpoints,prism_box,beam
VARIANTS=("SKYPORT_MONOLITHS","OPEN_LANTERN_LIFTS")
def study(variant):
    if variant not in VARIANTS:raise ValueError(variant)
    data,opt=option_b();sites={s["id"]:s for s in data["sites"]}
    meshes=[];portals=[]
    for a in endpoints(data,opt):
        fid=a["fid"];x,z,h=a["a"];rect=sites[fid]["parcel"]
        sign=-1 if fid in ("SB05","SB09") else 1
        edge=rect[1] if sign<0 else rect[3]
        entry_z=edge+2*sign;tag="M112_"+variant+"_"+fid
        start=(x,entry_z,8);end=(x,z,8)
        meshes.append(beam(start,end,10,2,1.2,"spine",tag+"_LOW_DECK"))
        meshes.append(beam(start,end,7,0,2,"shell",tag+"_GUIDE"))
        if variant=="SKYPORT_MONOLITHS":
            for props in [
             (x-5,z-5,6,x+5,z+5,h+6,"structure","DARK_CORE"),
             (x-4,z-6,8,x+4,z+6,h+3,"glass","GLAZING"),
             (x-11,z-7,h-3,x+11,z+7,h+8,"shell","CROWN"),
             (x-12,z-2,h+7,x+12,z+2,h+12,"cyan","LIGHT")]:
                *b,mat,name=props;meshes.append(prism_box(*b,mat,tag+"_"+name))
        else:
            for d in (-1,1):
                meshes.append(prism_box(x+d*6-1.2,z-5,6,x+d*6+1.2,z+5,h+6,
                    "spine",tag+"_RIB_"+str(d)))
            for props in [
             (x-4,z-4,6,x+4,z+4,h+6,"glass","ATRIUM"),
             (x-12,z-8,h-2,x+12,z+8,h+5,"shell","CANOPY"),
             (x-13,z-2,h+4,x+13,z+2,h+8,"gold","CREST")]:
                *b,mat,name=props;meshes.append(prism_box(*b,mat,tag+"_"+name))
        floors=[v for v in (7+18*i for i in range(int((h-8)/18)+1)) if v<h-4]
        for i,v in enumerate(floors):
            meshes.append(prism_box(x-5,z-5,v,x+5,z+5,v+1.2,"shell",tag+"_UNBUILT_FLOOR_"+str(i)))
        meshes.append(prism_box(x-9,z-7,h-1.5,x+9,z+7,h+2.5,"shell",tag+"_UPPER_CONNECTOR"))
        portals.append(dict(fid=fid,low_approach_m=round(abs(z-entry_z),3),gap_to_parcel_m=2,
          low_relative_H=8,high_relative_H=round(h,3),rise_relative_H=round(h-8,3),
          existing_door_connected=False,functional_lift=False,absolute_y_verified=False))
    return dict(phase="M112",variant=variant,status="RESEARCH_NONCONSTRUCTION",
      comparison_baseline="M101_UNCHANGED",model_H_not_actual_Y=True,
      construction_approved=False,world_writes=0,meshes=meshes,interfaces=portals)
if __name__=="__main__":
    for v in VARIANTS:
        result=study(v);print(v,len(result["meshes"]),result["interfaces"])
