#!/usr/bin/env python3
"""D32 research: two genuinely separate, hand-described spatial massing studies.

NOTE: Not canonical city, a building completion, or formal art adoption.
Study intention: reject code-friendly rock tower forms; begin with named inhabited
urban strata and public void, then compare real 3D cameras before detail work.
"""
import json, math, hashlib, argparse
from pathlib import Path
import numpy as np
import trimesh

OUT=Path(__file__).resolve().parent
COLORS={
 'civic':(198,202,193,255), 'civic_shadow':(140,153,157,255),
 'stratum':(105,135,145,255), 'stratum_bright':(160,179,170,255),
 'shell':(61,79,101,255), 'shell_light':(101,113,134,255),
 'fenestration':(210,194,142,255), 'transport':(148,157,170,255),
 'water':(29,98,135,255), 'terrain':(69,79,90,255),
 'plaza':(180,159,137,255), 'garden':(81,121,104,255)
}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def polyprism(points,z0,z1,color):
    """Extrude a convex manually controlled XY footprint to a solid volume."""
    points=np.asarray(points,dtype=float); n=len(points)
    v=np.vstack((np.column_stack([points,np.full(n,z0)]),np.column_stack([points,np.full(n,z1)])))
    faces=[]
    for i in range(1,n-1):
        faces.append([0,i+1,i]); faces.append([n,n+i,n+i+1])
    for i in range(n):
        j=(i+1)%n;faces.extend(([i,j,n+j],[i,n+j,n+i]))
    m=trimesh.Trimesh(vertices=v,faces=np.asarray(faces),process=False)
    m.fix_normals(); m.visual.face_colors=COLORS[color]
    assert m.is_watertight, 'nonwatertight prism'
    return m

def slab(x0,x1,y0,y1,z0,z1,color):
    return polyprism([[x0,y0],[x1,y0],[x1,y1],[x0,y1]],z0,z1,color)

def beam(a,b,width,height,color):
    a,b=np.array(a,dtype=float),np.array(b,dtype=float)
    mid=(a+b)*0.5; d=b-a
    m=trimesh.creation.box(extents=[width,height,float(np.linalg.norm(d))]);
    # Map local +Z onto direction in world frame.
    transform=trimesh.geometry.align_vectors([0,0,1],d)
    m.apply_transform(transform);m.apply_translation(mid);m.visual.face_colors=COLORS[color]
    return m

class Study:
    def __init__(self,name):self.name=name;self.scene=trimesh.Scene();self.program=[];self.count={}
    def add(self,name,geom,color=None,role='architecture',program=None):
        if name in self.scene.geometry:raise ValueError(name)
        if color:geom.visual.face_colors=COLORS[color]
        self.scene.add_geometry(geom,geom_name=name,node_name=name)
        self.count[role]=self.count.get(role,0)+1
        if program:self.program.append({'id':name,'program':program,'role':role,'bounds_m':np.asarray(geom.bounds).round(2).tolist()})
    def finish(self):
        output=OUT/f'D32_{self.name}_STUDY.glb';output.write_bytes(trimesh.exchange.gltf.export_glb(self.scene))
        read=trimesh.load(str(output),force='scene',process=False)
        assert len(read.geometry)==len(self.scene.geometry)
        assert all(g.is_watertight for g in read.geometry.values())
        return {'study':self.name,'file':output.name,'sha256':sha(output),'count':len(read.geometry),
            'triangles':int(sum(len(g.faces) for g in read.geometry.values())),
            'bounds_m':read.bounds.round(2).tolist(),'roles':self.count,
            'program':self.program,'GLB_readback':True,'each_mesh_watertight':True}

def civic_ground(s):
    s.add('ground_rim',slab(-950,950,-850,900,-60,-30,'terrain'),role='context')
    s.add('rift_basin_water',slab(-110,110,-610,720,-28,-25,'water'),role='context')
    s.add('rift_lower_walk_W',slab(-145,-106,-630,710,-15,-9,'civic'),role='public')
    s.add('rift_lower_walk_E',slab(106,145,-630,710,-15,-9,'civic'),role='public')
    # Open-air ground plaza and terminal. This is a *sampling ground route* only.
    s.add('south_arrival_plaza',slab(-190,190,-780,-650,-10,0,'plaza'),role='public',program='南側の公共入口広場')
    s.add('rift_spine_public_floor',slab(-85,85,-650,720,-9,-2,'civic'),role='public',program='連続する地上公共大路')
    s.add('north_arrival_plaza',slab(-220,220,720,820,-10,0,'plaza'),role='public')
    for y in (-560,-200,230,600):
      s.add(f'transverse_civic_threshold_{y}',slab(-155,155,y-9,y+9,-7,1,'civic_shadow'),role='public')

def shapeA():
    """Urban escarpment: inhabited stepped sections define a civic canyon."""
    s=Study('A_FAULT_URBAN_ESCARPMENT');civic_ground(s)
    # Opposing deep inhabited cliffs, not columns. Hand-adjusted floor level offsets.
    layers=[(25,165,1.00),(173,310,.94),(322,475,.82),(490,650,.72),(666,820,.62)]
    for flank,sign in [('WEST',-1),('EAST',1)]:
        for k,(z0,z1,f) in enumerate(layers):
            # Increasing top terraces have successive staggered city frontage.
            inner=180+(33*k if sign<0 else 56*k)
            outer=790-(33*k if sign<0 else 24*k)
            xx0,xx1=(-outer,-inner) if sign<0 else (inner,outer)
            dy=((-90*k+55) if sign<0 else (76*k-90))
            shape=[[xx0,-580+dy], [xx1,-630+dy], [xx1+sign*30,480+dy], [xx0,645+dy]]
            # Convex polygon for inhabitable district block: continuous, thick roof/floor.
            s.add(f'{flank}_inhabited_stratum_{k}',polyprism(shape,z0,z1,'stratum_bright' if k%2 else 'stratum'),role='inhabited',program=f'{flank}複合都市居住層{k+1}; 連続した街区質量（内部未設計）')
            # Exposed deep terraced civic band at the inner face, never floating thin strip alone.
            tx0,tx1=(xx1-14,xx1+60) if sign<0 else (xx0-60,xx0+14)
            s.add(f'{flank}_public_terrace_{k}',slab(tx0,tx1,-400+dy,390+dy,z1+7,z1+22,'plaza' if k%2 else 'garden'),role='public',program=f'{flank}段丘広場{k+1}（垂直アクセス未設計）')
            # Fenestration pattern: strong horizontal scale cues, not a substitute for form.
            ystart=-530+dy
            for j in range(9):
                y=ystart+j*109
                if y>450+dy:break
                z=z0+25+(j%3)*12
                if sign<0:
                    x=xx1+sign*2
                    m=slab(x-3,x+3,y,y+40,z,z+27,'fenestration')
                else:
                    x=xx0+sign*2
                    m=slab(x-3,x+3,y,y+40,z,z+27,'fenestration')
                s.add(f'{flank}_bay_{k}_{j}',m,role='facade')
    # Large offset hanging inhabited fold: slanted topography supporting high civic park.
    s.add('west_oblique_escapement',polyprism([[-865,-280],[-705,-550],[-540,410],[-660,690]],735,975,'shell'),role='macroform')
    s.add('east_diagonal_urban_rampart',polyprism([[550,-570],[805,-380],[660,820],[480,550]],745,1065,'shell_light'),role='macroform')
    # mid-height civic crossing is not certified accessible from the ground spine.
    s.add('midspan_civic_footbridge',slab(-380,390,190,245,325,346,'transport'),role='transport',program='中層公共連絡橋（アクセス未設計）')
    # Ramp spine deliberately not faked as accessible; vertical links absent.
    return s

def shapeB():
    """Hanging city strata: staggered full-depth horizontal flying platforms around an oblique rift."""
    s=Study('B_SUSPENDED_INHABITED_FAN');civic_ground(s)
    for i,(sign,z,shift) in enumerate([(-1,95,-300),(1,240,-175),(-1,400,45),(1,560,220),(-1,730,-50),(1,915,250)]):
        z=float(z)
        # Conspicuous asymmetric full-depth urban bars fanning away from an empty gulf.
        if sign<0:
            footprint=[[-820,shift-315],[-155,shift-225],[-205,shift+440],[-750,shift+320]]
        else:
            footprint=[[170,shift-300],[800,shift-390],[865,shift+290],[240,shift+430]]
        s.add(f'fan_city_{i:02d}',polyprism(footprint,z,z+139,'stratum' if i%2 else 'stratum_bright'),role='inhabited',program=f'高高度居住街区{i+1}（内部・構造未設計）')
        # Vertical cut is a real *open external space* rather than painted tunnel.
        if sign<0: tt=(-330,-140)
        else:tt=(160,365)
        s.add(f'fan_civic_through_deck_{i:02d}',slab(*tt,shift-90,shift+215,z+140,z+164,'garden' if i%2 else 'plaza'),role='public',program=f'高層の外部公共広場{i+1}（経路未接続）')
        for j in range(7):
            xx=(-760+j*75) if sign<0 else (210+j*82)
            yy=shift+260
            s.add(f'fan_facade_light_{i}_{j}',slab(xx,xx+27,yy,yy+7,z+38,z+84,'fenestration'),role='facade')
    # Off-axis monumental spine has two immense, opposed tapering architectural sails.
    s.add('west_flying_shear',polyprism([[-930,-660],[-740,-700],[-260,780],[-530,795]],710,1190,'shell'),role='macroform')
    s.add('east_drifted_edge',polyprism([[660,-610],[880,-390],[455,755],[310,530]],765,1105,'shell_light'),role='macroform')
    s.add('lower_public_bridge',slab(-370,340,-230,-185,200,224,'transport'),role='transport',program='中層横断通路（アクセス未認証）')
    return s

def run():
    outcomes=[]
    for proc in (shapeA,shapeB):outcomes.append(proc().finish())
    (OUT/'D32_GEOMETRY_EVIDENCE.json').write_text(json.dumps(outcomes,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps([{k:v for k,v in d.items() if k!='program'} for d in outcomes],ensure_ascii=False,indent=2))
if __name__=='__main__':run()
