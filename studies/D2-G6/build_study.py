"""Build conceptual D2-G6 urban massings and orthographic review views.

The GLBs are schematic study geometry, not W0 survey data or construction models.
"""
from pathlib import Path
import math
import random
import json

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
RNG = random.Random(906)

COLORS = {
    "ground": (69, 82, 83, 255),
    "urban": (179, 174, 151, 255),
    "urban_light": (214, 202, 169, 255),
    "urban_dark": (109, 123, 119, 255),
    "water": (45, 180, 190, 255),
    "water_deep": (18, 75, 105, 255),
    "transit": (242, 177, 88, 255),
    "ecology": (97, 166, 121, 255),
    "ecology_light": (164, 197, 138, 255),
    "cliff": (94, 96, 91, 255),
    "void": (28, 34, 51, 255),
    "district": (119, 143, 159, 255),
    "light": (255, 221, 155, 255),
}


def box(name, center, size, color, angle=0.0):
    mesh = trimesh.creation.box(extents=size)
    mesh.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 0, 1]))
    mesh.apply_translation(center)
    mesh.visual.face_colors = np.tile(np.array(color, dtype=np.uint8), (len(mesh.faces), 1))
    mesh.metadata["name"] = name
    return mesh


def cylinder(name, center, radius, height, color, sections=12):
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    mesh.apply_translation(center)
    mesh.visual.face_colors = np.tile(np.array(color, dtype=np.uint8), (len(mesh.faces), 1))
    mesh.metadata["name"] = name
    return mesh


def ribbon(name, points, width, thickness, color, waterline=None):
    """Solid rectilinear sweep following a 3D polyline, with a parallel-transport frame."""
    p = np.asarray(points, dtype=float)
    verts = []
    for i, q in enumerate(p):
        tangent = p[min(i + 1, len(p) - 1)] - p[max(0, i - 1)]
        tangent /= max(np.linalg.norm(tangent), 1e-8)
        side = np.cross(tangent, np.array([0.0, 0.0, 1.0]))
        if np.linalg.norm(side) < 1e-6:
            side = np.array([1.0, 0.0, 0.0])
        side /= np.linalg.norm(side)
        up = np.cross(side, tangent)
        up /= np.linalg.norm(up)
        for su, sv in [(-1,-1),(1,-1),(1,1),(-1,1)]:
            verts.append(q + side * su * width * 0.5 + up * sv * thickness * 0.5)
    faces = []
    faces.extend([(0,3,2),(0,2,1)])
    for i in range(len(p)-1):
        a, b = 4*i, 4*(i+1)
        for j in range(4):
            k=(j+1)%4
            faces.extend([(a+j,a+k,b+k),(a+j,b+k,b+j)])
    a=4*(len(p)-1)
    faces.extend([(a,a+1,a+2),(a,a+2,a+3)])
    mesh=trimesh.Trimesh(vertices=np.array(verts),faces=np.array(faces),process=True)
    mesh.visual.face_colors=np.tile(np.array(color,dtype=np.uint8),(len(mesh.faces),1))
    mesh.metadata["name"]=name
    out=[mesh]
    if waterline:
        pts=[]
        for q in p:
            pts.append([q[0],q[1],q[2]+thickness*.52])
        out.append(ribbon(name+"_water",pts,waterline,.012,COLORS["water"]))
    return out


def poly_prism(name, outline, z0, z1, color):
    # Low-complexity extruded polygon with a center fan; suitable for conceptual terrain.
    pts=np.asarray(outline,dtype=float)
    n=len(pts)
    verts=np.vstack([np.c_[pts,np.full(n,z0)],np.c_[pts,np.full(n,z1)]])
    faces=[]
    for i in range(1,n-1):
        faces.append((n,n+i,n+i+1))
        faces.append((i+1,i,0))
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j),(i,n+j,n+i)])
    mesh=trimesh.Trimesh(vertices=verts,faces=np.array(faces),process=True)
    mesh.visual.face_colors=np.tile(np.array(color,dtype=np.uint8),(len(mesh.faces),1))
    mesh.metadata["name"]=name
    return mesh


def warped_civic_slab(name, outline, z0, z1, phase, color):
    """Thick, faceted public ground with a ridged top instead of a flat box-like lid."""
    p=np.asarray(outline,dtype=float); n=len(p)
    heights=np.asarray([z1+.22*math.sin(i*1.31+phase)+.08*math.cos(i*.77-phase) for i in range(n)])
    center=np.mean(p,axis=0)
    center_z=float(np.mean(heights)+.10)
    verts=np.vstack([np.c_[p,np.full(n,z0)],np.c_[p,heights],[[center[0],center[1],center_z]]])
    faces=[]; c=2*n
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j),(i,n+j,n+i)])
        faces.append((c,n+i,n+j))
    for i in range(1,n-1): faces.append((0,i+1,i))
    mesh=trimesh.Trimesh(vertices=verts,faces=np.asarray(faces),process=True)
    mesh.visual.face_colors=np.tile(np.asarray(color,dtype=np.uint8),(len(mesh.faces),1))
    mesh.metadata["name"]=name
    return mesh


def cluster(name, cx, cy, base, radius, count, palette, height_factor=1.0):
    out=[]
    for i in range(count):
        a=RNG.random()*math.tau
        r=radius*math.sqrt(RNG.random())
        x=cx+math.cos(a)*r
        y=cy+math.sin(a)*r
        sx=RNG.uniform(.09,.23)
        sy=RNG.uniform(.08,.19)
        sz=RNG.uniform(.10,.38)*height_factor
        z=base+sz*.5
        c=palette[RNG.randrange(len(palette))]
        out.append(box(f"{name}_{i:03d}",(x,y,z),(sx,sy,sz),c,angle=RNG.random()*.35))
        if i%5==0 and sz>.22:
            out.append(box(f"{name}_crown_{i:03d}",(x,y,z+sz*.53),(sx*.67,sy*.67,.035),COLORS["light"]))
    return out


def context(variant):
    out=[box("10km_study_terrain",(0,0,-.12),(10,10,.24),COLORS["ground"])]
    # W0-like orientation in a research-only diagram: north +Y, sea east +X.
    for i,(x,y,r,h) in enumerate([(-4.35,4.12,.82,1.20),(-3.05,4.38,.74,1.55),(-1.72,4.18,.92,1.28),(-.10,4.43,.88,1.72),(1.48,4.16,.88,1.30),(3.05,4.40,.78,1.52),(4.22,4.03,.64,1.10)]):
        peak=trimesh.creation.cone(radius=r,height=h,sections=5)
        peak.apply_translation((x,y,h*.5))
        peak.visual.face_colors=np.tile(np.array(COLORS["cliff"],dtype=np.uint8),(len(peak.faces),1))
        peak.metadata["name"]=f"north_mountain_peak_{i+1}"
        out.append(peak)
    out.append(box("west_cliff_face",(-4.82,0,.44),(.35,7.45,1.12),COLORS["cliff"],angle=-.10))
    out.append(box("east_artificial_inland_sea",(4.28,.05,-.025),(1.34,6.7,.055),COLORS["water_deep"]))
    out.append(box("southwest_great_void",(-3.65,-3.6,-.18),(2.3,2.0,.08),COLORS["void"]))
    # District blocks around the central study anchor; they are schematic density, not exact locations.
    for idx,(x,y) in enumerate([(-3.25,2.5),(-1.1,3.0),(1.8,2.9),(3.0,1.6),(-3.0,-.3),(-2.0,-2.2),(.2,-3.1),(2.3,-2.9),(3.35,-.8)]):
        out.extend(cluster(f"urban_context_{idx}",x,y,.02,.62,18,[COLORS["urban_dark"],COLORS["urban"]],.65))
    return out


def transit_lines(out, paths, zoffset=.12):
    for i,p in enumerate(paths):
        pts=[(x,y,z+zoffset) for x,y,z in p]
        out.extend(ribbon(f"public_transit_{i}",pts,.045,.025,COLORS["transit"]))


def build_a1():
    out=context("A1")
    paths=[
        [(-2.6,-1.5,.30),(-1.8,-.95,.55),(-.9,-.55,.92),(-.15,0,1.18),(.75,.48,1.42),(1.65,.92,1.10),(2.6,1.55,.55)],
        [(-2.5,1.55,.77),(-1.55,1.0,1.0),(-.65,.50,1.12),(.10,-.05,.94),(1.0,-.60,.72),(1.85,-1.18,.43),(2.55,-1.60,.26)],
        [(-2.35,.05,.18),(-1.30,.18,.43),(-.35,.12,.69),(.58,.16,.82),(1.48,.18,.54),(2.35,.03,.34)],
    ]
    for i,p in enumerate(paths):
        out.extend(ribbon(f"inhabited_hydraulic_spine_{i+1}",p,[.70,.62,.54][i],[.32,.29,.24][i],COLORS["urban_light"],waterline=.075 if i<2 else None))
        for j in range(1,len(p)-1):
            x,y,z=p[j]
            out.extend(cluster(f"inhabited_quarter_{i}_{j}",x,y,z+.19,.37,12,[COLORS["urban"],COLORS["urban_light"],COLORS["urban_dark"]],1.0 if z>1 else .72))
    transit_lines(out,paths,zoffset=.19)
    # Major public room: broad civic hall whose open roof makes the inhabited sectional edges legible.
    out.extend([
        box("confluence_hall_floor",(0,0,.72),(1.22,1.08,.12),COLORS["urban_dark"]),
        box("hall_north_gallery",(0,.49,1.16),(1.12,.12,.78),COLORS["urban_light"]),
        box("hall_south_gallery",(0,-.49,1.16),(1.12,.12,.78),COLORS["urban_light"]),
        box("hall_west_gallery",(-.54,0,1.14),(.12,.84,.72),COLORS["urban"]),
        box("hall_east_gallery",(.54,0,1.11),(.12,.84,.66),COLORS["urban"]),
        box("hall_translucent_canopy",(0,0,1.72),(.74,.14,.055),COLORS["light"],angle=.25),
    ])
    # Three exposed return channels and two low-lift pumping stacks make direction readable.
    for i,(x,y,z) in enumerate([(-.92,-.26,.48),(.95,.21,.57),(.28,-.96,.38)]):
        out.append(ribbon(f"gravity_return_channel_{i}",[(x-0.34,y,z),(x,y-.05,z-.08),(x+.36,y-.10,z-.17)],.075,.018,COLORS["water"]))
    for x,y in [(-1.75,-1.25),(1.8,1.2)]:
        out.append(cylinder("speculative_pumped_riser",(x,y,.72),.10,.88,COLORS["water"],16))
        out.append(cylinder("riser_control_collar",(x,y,1.18),.15,.08,COLORS["transit"],16))
    # H1-H6 are generic symbolic markers only; no claim to canonical position.
    for i,(x,y,z) in enumerate([(-2.1,-.8,.8),(-1.2,1.25,1.5),(-.15,-.2,1.9),(.8,.88,2.05),(1.9,-.75,1.25),(2.15,1.38,.95)]):
        out.append(cylinder(f"H{i+1}_continuous_lift_spine",(x,y,z*.48),.065,z*.96,COLORS["urban_dark"],10))
        out.append(cylinder(f"H{i+1}_schematic_sky_district",(x,y,z),.22,.28,COLORS["district"],12))
        out.extend(cluster(f"H{i+1}_inhabited_volume",x,y,z+.17,.21,7,[COLORS["urban_light"],COLORS["district"]],.6))
    return out


def build_a2():
    out=context("A2")
    # Four asymmetric occupied shoulders; a large open public room cuts through their shared center.
    shoulders=[
        ([(-2.7,-1.7),(-1.25,-1.2),(-.63,-.50),(-1.05,.10),(-2.55,.25)],.15,.78),
        ([(-2.4,1.65),(-1.55,1.15),(-.65,.48),(-.30,1.05),(-.82,2.1),(-2.2,2.35)],.48,1.32),
        ([(.45,-.40),(1.18,-1.08),(2.8,-1.65),(2.75,-.38),(1.65,.18)],.42,1.45),
        ([(.22,.47),(1.02,.96),(1.62,1.88),(.62,2.35),(-.08,1.35)],.86,2.05),
    ]
    for i,(poly,z0,z1) in enumerate(shoulders):
        out.append(warped_civic_slab(f"occupied_civic_shoulder_{i+1}",poly,z0,z1,i*.85,COLORS["urban_light"] if i%2==0 else COLORS["urban"]))
        cx=sum(x for x,y in poly)/len(poly); cy=sum(y for x,y in poly)/len(poly)
        out.extend(cluster(f"shoulder_district_{i+1}",cx,cy,z1+.04,.65,24,[COLORS["urban"],COLORS["urban_light"],COLORS["district"]],1.2))
    # Blue-green lowland channels traverse the built shoulders and gravity-drop into return wetlands.
    channel_paths=[
        [(-2.8,-.35,.19),(-1.55,-.18,.31),(-.72,.02,.48),(0,.05,.58),(.96,.02,.41),(2.7,.35,.25)],
        [(-.48,2.1,.25),(-.28,1.25,.47),(.05,.45,.61),(.26,-.54,.45),(.53,-1.55,.23)],
        [(1.18,2.3,.2),(1.10,1.42,.36),(.74,.52,.52),(.26,-.28,.39),(-.30,-1.38,.19)],
    ]
    for i,p in enumerate(channel_paths):
        out.extend(ribbon(f"urban_waterway_{i+1}",p,.095,.022,COLORS["water"]))
    transit_lines(out,channel_paths,zoffset=.11)
    # East-sea intake, pumped lift, high-level distribution and independent gravity return.
    out.extend(ribbon("lowland_sea_intake",[(3.60,.62,.025),(3.05,.56,.035),(2.55,.50,.08),(2.08,.42,.12)],.15,.035,COLORS["water"]))
    out.append(cylinder("speculative_lift_main",(1.98,.40,.77),.12,1.52,COLORS["water"],16))
    out.append(box("high_level_distribution_header",(1.18,.42,1.50),(.92,.26,.18),COLORS["water"]))
    out.extend(ribbon("high_level_distribution_to_central",[(1.45,.42,1.50),(.82,.34,1.40),(.26,.24,1.16)],.11,.025,COLORS["water"]))
    out.extend(ribbon("gravity_return_to_east_sea",[(.25,-.94,.10),(.92,-.86,.085),(1.62,-.76,.07),(2.30,-.67,.05),(3.61,-.61,.025)],.16,.035,COLORS["water"]))
    # Flow arrows point from the sea intake toward the lift and from the city back to the sea.
    out.append(poly_prism("intake_flow_arrow",[(2.45,.37),(2.26,.48),(2.26,.26)],.11,.15,COLORS["light"]))
    out.append(poly_prism("return_flow_arrow",[(2.42,-.67),(2.22,-.56),(2.22,-.78)],.07,.11,COLORS["light"]))
    # Massive civic room is open and inhabited at its rims, not a decorative water bowl.
    out.extend([
        box("civic_exchange_floor",(0,0,.35),(1.12,1.02,.12),COLORS["urban_dark"]),
        box("exchange_north_inhabited_gallery",(0,.60,.87),(1.2,.18,1.04),COLORS["urban_light"]),
        box("exchange_south_inhabited_gallery",(0,-.60,.82),(1.2,.18,.94),COLORS["urban"]),
        box("exchange_east_inhabited_gallery",(.68,0,.78),(.18,.92,.86),COLORS["urban_light"]),
        box("exchange_west_inhabited_gallery",(-.68,0,.76),(.18,.92,.82),COLORS["urban"]),
        box("exchange_public_bridge",(0,0,1.34),(.84,.11,.09),COLORS["transit"],angle=.28),
    ])
    # Upper residential shelves and real mass at altitude.
    for i,(x,y,z) in enumerate([(-1.5,1.75,2.15),(.82,1.65,2.38),(2.15,-.95,1.95),(-1.7,-.9,1.78)]):
        out.append(box(f"high_city_shelf_{i}",(x,y,z),(.78,.52,.36),COLORS["district"],angle=(i-1)*.12))
        out.extend(cluster(f"high_residence_{i}",x,y,z+.2,.34,13,[COLORS["urban_light"],COLORS["district"]],1.0))
    for i,(x,y,z) in enumerate([(-2.0,-.65,1.35),(-1.45,1.7,2.05),(-.35,.15,2.35),(.8,1.55,2.45),(1.75,-.8,2.05),(2.45,1.2,1.65)]):
        out.append(cylinder(f"H{i+1}_continuous_lift_spine",(x,y,z*.48),.06,z*.96,COLORS["urban_dark"],10))
        out.append(cylinder(f"H{i+1}_schematic_sky_district",(x,y,z),.20,.26,COLORS["district"],12))
        out.extend(cluster(f"H{i+1}_inhabited_volume",x,y,z+.15,.21,6,[COLORS["urban_light"],COLORS["district"]],.65))
    return out


def build_b1(season="wet"):
    out=context("B1")
    # Three folded, inhabited habitat ridges with ecological succession bands.
    folds=[
        [(-2.45,-1.45,.18),(-2.05,-.80,.72),(-1.52,-.15,1.42),(-1.15,.55,1.95),(-.70,1.2,1.62),(-.35,1.75,.86)],
        [(-.18,-2.1,.15),(.20,-1.35,.56),(.72,-.55,1.16),(1.30,.10,1.82),(1.64,.86,2.25),(2.0,1.55,1.54)],
        [(2.25,-1.65,.18),(1.78,-.98,.70),(1.05,-.35,1.28),(.30,.25,1.72),(-.48,.98,2.12),(-1.25,1.75,1.72)],
    ]
    for i,p0 in enumerate(folds):
        # The wet monsoon fans habitat outward; the dry-season fold pulls back and exposes migration commons.
        opening=(.38 if season=="wet" else -.27)
        p=[(x+opening*math.sin(j/(len(p0)-1)*math.pi)*(1 if i!=1 else -1),y,z+(0.12 if season=="wet" and j in (2,3,4) else 0)) for j,(x,y,z) in enumerate(p0)]
        out.extend(ribbon(f"inhabited_ecological_fold_{i+1}",p,.76,.46,COLORS["urban_light"]))
        # Living succession edge on the outer flank, below the summit and adjacent to housing.
        eco=[(x+.18,y,z+.18) for x,y,z in p]
        out.extend(ribbon(f"seasonal_habitat_band_{i+1}",eco,.36 if season=="wet" else .20,.055,COLORS["ecology_light"] if season=="wet" else COLORS["ecology"]))
        for j in range(1,len(p)-1):
            x,y,z=p[j]
            out.extend(cluster(f"fold_residential_neighborhood_{i}_{j}",x-.12,y,z-.05,.38,10,[COLORS["urban"],COLORS["urban_light"],COLORS["district"]],.92))
    # Seasonal commons: wetlands shift at ground level; dry season opens migration terraces.
    if season=="wet":
        out.append(box("seasonal_floodplain_wet",(.05,-.15,.04),(2.65,1.75,.045),COLORS["water"]))
        eco_color=COLORS["ecology"]
    else:
        out.append(box("seasonal_commons_dry",(.05,-.15,.025),(1.45,1.05,.035),COLORS["ecology_light"]))
        out.append(box("dry_migration_walk",(.05,-.15,.07),(2.35,.075,.045),COLORS["transit"]))
        eco_color=COLORS["transit"]
    # Species paths and public pedestrian crossings remain separate and visible.
    for i,p in enumerate([
        [(-2.8,.05,.11),(-1.65,.15,.17),(-.55,.0,.21),(.55,.12,.18),(1.8,.35,.15),(2.75,.8,.10)],
        [(-1.8,-1.9,.08),(-1.25,-.95,.13),(-.65,-.05,.16),(.05,.8,.18),(.92,1.7,.12)],
    ]):
        out.extend(ribbon(f"seasonal_species_corridor_{i}",p,.055,.018,eco_color))
    transit_lines(out,[[(-2.6,-1.85,.28),(-1.4,-1.2,.35),(-.25,-.72,.43),(.85,-.15,.48),(2.4,.65,.38)]],zoffset=.07)
    # Six schematic sky-district markers, again intentionally unplaced as canon.
    for i,(x,y,z) in enumerate([(-1.8,-.5,1.1),(-1.35,.9,2.1),(-.3,1.55,1.5),(.72,-.72,1.5),(1.45,.55,2.35),(2.05,1.25,1.55)]):
        out.append(cylinder(f"H{i+1}_continuous_lift_spine",(x,y,z*.48),.06,z*.96,COLORS["urban_dark"],10))
        out.append(cylinder(f"H{i+1}_schematic_sky_district",(x,y,z),.20,.25,COLORS["district"],12))
        out.extend(cluster(f"H{i+1}_inhabited_volume",x,y,z+.14,.2,6,[COLORS["urban_light"],COLORS["district"]],.65))
    return out


def export_scene(meshes, filename):
    scene=trimesh.Scene()
    for i,m in enumerate(meshes):
        name=m.metadata.get("name",f"part_{i:04d}")
        scene.add_geometry(m,geom_name=name,node_name=name)
    path=ROOT/filename
    scene.export(path,file_type="glb")
    return path


def flatten(meshes):
    result=[]
    for item in meshes:
        if hasattr(item,"faces") and hasattr(item,"vertices"):
            result.append(item)
        elif isinstance(item,(list,tuple)):
            result.extend(flatten(item))
        elif isinstance(item,trimesh.Scene):
            result.extend(geom for geom in item.geometry.values() if hasattr(geom,"faces"))
        else:
            raise TypeError(f"Unsupported scene item: {type(item).__name__}")
    return result


def project_points(v, target, direction, width, height, scale):
    direction=np.asarray(direction,dtype=float); direction/=np.linalg.norm(direction)
    up0=np.array([0.,0.,1.])
    if abs(float(np.dot(direction,up0)))>.96: up0=np.array([0.,1.,0.])
    forward=-direction
    right=np.cross(forward,up0); right/=np.linalg.norm(right)
    up=np.cross(right,forward); up/=np.linalg.norm(up)
    rel=v-np.asarray(target)
    sx=rel@right; sy=rel@up; depth=rel@direction
    px=width*.5+sx*scale
    py=height*.53-sy*scale
    return np.c_[px,py,depth], right, up, direction


def render(meshes, filename, title, subtitle, direction, target=(0,0,.7), size=(1400,900), span=12.8, section=False):
    W,H=size
    if span <= 8.0:
        context_names={"10km_study_terrain","north_mountain_range","west_cliff_face","southwest_great_void"}
        meshes=[m for m in meshes if m.metadata.get("name","") not in context_names and not m.metadata.get("name","").startswith(("urban_context_","north_mountain_peak_"))]
    image=Image.new("RGB",size,(14,23,39))
    px=image.load()
    for y in range(H):
        t=y/max(1,H-1)
        c=(int(18+13*t),int(29+20*t),int(50+30*t))
        for x in range(W): px[x,y]=c
    draw=ImageDraw.Draw(image,"RGBA")
    try:
        font=ImageFont.truetype("C:/Windows/Fonts/aptos.ttf",28)
        small=ImageFont.truetype("C:/Windows/Fonts/aptos.ttf",16)
    except OSError:
        font=ImageFont.load_default(); small=font
    scale=min((W-90)/span,(H-150)/(span*.68))
    allv=np.vstack([m.vertices for m in meshes])
    allp, right, up, direction=project_points(allv,target,direction,W,H,scale)
    zbuf=np.full((H,W),-np.inf,dtype=np.float32)
    rgb=np.zeros((H,W,3),dtype=np.uint8)
    for y in range(H):
        t=y/max(1,H-1)
        rgb[y,:,0]=int(18+13*t); rgb[y,:,1]=int(29+20*t); rgb[y,:,2]=int(50+30*t)
    # Camera-side clipping for an explanatory section image.
    for m in meshes:
        verts=m.vertices
        p,_,_,_=project_points(verts,target,direction,W,H,scale)
        f=m.faces
        fc=np.asarray(m.visual.face_colors) if hasattr(m.visual,"face_colors") else np.tile([180,180,180,255],(len(f),1))
        if len(fc)!=len(f): fc=np.tile(fc[0],(len(f),1))
        for j,face in enumerate(f):
            tri=p[face]
            centroid=verts[face].mean(axis=0)
            # Cut away the near-side half of the central complex to reveal its interior.
            if section and centroid[1] < -.30 and np.max(np.abs(centroid[:2]))<2.9:
                continue
            if np.max(tri[:,0])<0 or np.min(tri[:,0])>W or np.max(tri[:,1])<60 or np.min(tri[:,1])>H-60:
                continue
            normal=m.face_normals[j]
            light=np.array([-.4,-.55,.72]); light/=np.linalg.norm(light)
            lam=.46+.54*max(0.,float(np.dot(normal,light)))
            base=fc[j,:3].astype(float)
            col=tuple(np.clip(base*lam,0,255).astype(int))
            xy=tri[:,:2]
            x0=max(0,int(np.floor(xy[:,0].min()))); x1=min(W-1,int(np.ceil(xy[:,0].max())))
            y0=max(45,int(np.floor(xy[:,1].min()))); y1=min(H-45,int(np.ceil(xy[:,1].max())))
            if x1<x0 or y1<y0: continue
            den=(xy[1,1]-xy[2,1])*(xy[0,0]-xy[2,0])+(xy[2,0]-xy[1,0])*(xy[0,1]-xy[2,1])
            if abs(den)<1e-8: continue
            gx,gy=np.meshgrid(np.arange(x0,x1+1,dtype=np.float32)+.5,np.arange(y0,y1+1,dtype=np.float32)+.5)
            w0=((xy[1,1]-xy[2,1])*(gx-xy[2,0])+(xy[2,0]-xy[1,0])*(gy-xy[2,1]))/den
            w1=((xy[2,1]-xy[0,1])*(gx-xy[2,0])+(xy[0,0]-xy[2,0])*(gy-xy[2,1]))/den
            w2=1.0-w0-w1
            inside=(w0>=-1e-5)&(w1>=-1e-5)&(w2>=-1e-5)
            dep=w0*tri[0,2]+w1*tri[1,2]+w2*tri[2,2]
            sub=zbuf[y0:y1+1,x0:x1+1]
            visible=inside&(dep>sub)
            if np.any(visible):
                sub[visible]=dep[visible]
                rgb[y0:y1+1,x0:x1+1][visible]=col
    image=Image.fromarray(rgb,"RGB")
    draw=ImageDraw.Draw(image,"RGBA")
    # Broad metropolitan context axis annotations.
    draw.rounded_rectangle((28,22,W-28,84),radius=12,fill=(8,14,25,205),outline=(95,131,152,120),width=1)
    draw.text((48,31),title,font=font,fill=(244,238,220,255))
    draw.text((50,65),subtitle,font=small,fill=(144,207,211,255))
    # Legend and orientation panel.
    draw.rounded_rectangle((W-265,H-157,W-28,H-28),radius=10,fill=(8,14,25,205),outline=(95,131,152,120),width=1)
    legend=[("Urban mass",COLORS["urban_light"]),("Water / habitat",COLORS["water"]),("Public transit",COLORS["transit"])]
    for i,(label,c) in enumerate(legend):
        y=H-139+i*31
        draw.rounded_rectangle((W-246,y,W-229,y+14),radius=3,fill=c)
        draw.text((W-218,y-2),label,font=small,fill=(224,228,225,255))
    # Tiny N arrow.
    draw.line((56,H-80,56,H-132),fill=(232,223,196,220),width=3)
    draw.polygon([(56,H-140),(48,H-122),(64,H-122)],fill=(232,223,196,220))
    draw.text((48,H-109),"N",font=small,fill=(232,223,196,220))
    path=ROOT/filename
    image.save(path,optimize=True)
    return path


def make_atlas():
    variants={
        "A1":flatten(build_a1()),
        "A2":flatten(build_a2()),
        "B1":flatten(build_b1("wet")),
    }
    glbs={}
    for key,meshes in variants.items():
        glbs[key]=export_scene(meshes,{"A1":"A1-Civic-Weave.glb","A2":"A2-Confluence-Chambers.glb","B1":"B1-Monsoon-Folds.glb"}[key])
    views=[]
    # Panel renders all come from the same exported-equivalent mesh collection.
    for key,meshes in variants.items():
        title={"A1":"A1 · CIVIC WEAVE","A2":"A2 · CONFLUENCE CHAMBERS","B1":"B1 · MONSOON FOLDS"}[key]
        views.append(render(meshes,f"{key}-overview.png",title,"10 km study context · north mountain / west cliff / east inland sea / southwest void",(9,-12,9),target=(0,0,.7),span=12.5))
    views.append(render(variants["A2"],"A2-10km-city-plan.png","A2 · 10 KM CITY PLAN","Study context only · north mountain / west cliff / east artificial inland sea / southwest great void",(0,-.18,1),target=(0,0,.15),span=12.2))
    # A2 is the selected configuration for the complete six-view art screen.
    a2=variants["A2"]
    for name,title,sub,direction,target,span,section in [
        ("A2-east-sea-approach.png","A2 · EAST SEA APPROACH","Artificial inland sea, lowland intake and inhabited central exchange",(1,.2,.3),(0,0,.8),11.8,False),
        ("A2-central-oblique.png","A2 · CENTRAL OBLIQUE","Four occupied shoulders open a deep civic exchange chamber",(8,-10,7),(0,0,.9),7.0,False),
        ("A2-side-profile.png","A2 · SIDE PROFILE","Side silhouette with high residential shelves",(14,1,3),(0,0,.8),7.1,False),
        ("A2-rear-profile.png","A2 · REAR PROFILE","Back view: channels and public routes remain connected",(-8,11,6),(0,0,.9),7.3,False),
        ("A2-high-city.png","A2 · HIGH ALTITUDE CITY","Connected inhabited shelves and six symbolic sky-district lifts",(6,-8,13),(0,0,1.35),7.0,False),
        ("A2-public-interior-section.png","A2 · PUBLIC ROOM / SECTION","Cutaway reveals galleries, exchange floor and upper inhabited shoulders",(0,-12,2.5),(0,0,1.0),7.0,True),
    ]:
        views.append(render(a2,name,title,sub,direction,target=target,span=span,section=section,size=(1400,900)))
    # B seasonal comparison changes habitat fold geometry and the amount of exposed commons.
    views.append(render(build_b1("dry"),"B1-dry-season.png","B1 · DRY SEASON","Migration terrace opens; quiet breeding ground contracts",(8,-10,7),target=(0,0,.8),span=7.3))
    # Contact sheet for the review panel.
    thumbs=[]
    for p in views:
        im=Image.open(p).convert("RGB")
        im.thumbnail((510,328),Image.Resampling.LANCZOS)
        thumbs.append((p.name,im.copy()))
    cols=3; rows=math.ceil(len(thumbs)/cols)
    sheet=Image.new("RGB",(cols*520,rows*360),(12,18,31))
    sd=ImageDraw.Draw(sheet)
    try: f=ImageFont.truetype("C:/Windows/Fonts/aptos.ttf",19)
    except OSError: f=ImageFont.load_default()
    for i,(label,im) in enumerate(thumbs):
        x=(i%cols)*520+5; y=(i//cols)*360+5
        sheet.paste(im,(x,y))
        sd.text((x+7,y+331),label,font=f,fill=(228,227,211))
    sheet.save(ROOT/"D2-G6-view-atlas.png",optimize=True)
    validation={
        "study_id":"D2-G6",
        "method":"Procedural multi-object meshes generated with trimesh; orthographic diagnostic views rasterized from the same mesh collections using a custom PIL depth-buffer renderer.",
        "coordinate_units":"kilometres; 1 model coordinate unit equals 1 km",
        "models":{},
        "view_files":[{"path":p.name,"size_bytes":p.stat().st_size,"resolution_px":[1400,900] if p.name!="D2-G6-view-atlas.png" else [1560,1440]} for p in views]+[{"path":"D2-G6-view-atlas.png","size_bytes":(ROOT/"D2-G6-view-atlas.png").stat().st_size,"resolution_px":[1560,1440]}],
        "checks":["All three GLBs reloaded through trimesh", "Scene and central-city envelopes measured from exported meshes", "Per-object watertightness and face counts recorded", "All A2 views share the same central geometry", "B wet and dry comparison views derive from the same seasonal-fold design family"],
        "limits":["Concept art geometry only; not a Blender scene, survey model, structural model, W0 coordinate reconstruction, or construction-ready asset", "Watertight individual objects do not imply a single connected building structure", "Custom orthographic renders are flat-shaded diagnostics, not photorealistic Blender renders", "Hydrology, climate, ecology, circulation capacity, safety, and constructability are not simulated", "H1-H6 markers are schematic interfaces, not canonical coordinates"],
    }
    for key,meshes in variants.items():
        glb=ROOT/{"A1":"A1-Civic-Weave.glb","A2":"A2-Confluence-Chambers.glb","B1":"B1-Monsoon-Folds.glb"}[key]
        loaded=trimesh.load(glb,force="scene")
        geoms=[g for g in loaded.geometry.values() if hasattr(g,"faces")]
        combined=trimesh.util.concatenate(geoms)
        central=[m for m in meshes if not m.metadata.get("name","").startswith(("10km_study_terrain","north_mountain_peak_","west_cliff_face","east_artificial_inland_sea","southwest_great_void","urban_context_"))]
        central_mesh=trimesh.util.concatenate(central)
        validation["models"][key]={
            "path":glb.name,"size_bytes":glb.stat().st_size,
            "mesh_objects":len(geoms),"faces":int(sum(len(g.faces) for g in geoms)),
            "scene_bounds_km":np.round(combined.bounds,5).tolist(),"scene_dimensions_km":np.round(combined.extents,5).tolist(),
            "central_city_bounds_km":np.round(central_mesh.bounds,5).tolist(),"central_city_dimensions_km":np.round(central_mesh.extents,5).tolist(),
            "all_objects_individually_watertight":bool(all(g.is_watertight for g in geoms)),
            "watertight_object_count":int(sum(g.is_watertight for g in geoms)),
            "connected_components_after_concatenation":int(len(combined.split(only_watertight=False))),
            "vertex_count":int(sum(len(g.vertices) for g in geoms)),
        }
    (ROOT/"geometry-validation.json").write_text(json.dumps(validation,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return variants,views


if __name__=="__main__":
    variants,views=make_atlas()
    print("MODELS",{k:{"objects":len(v),"faces":sum(len(m.faces) for m in v)} for k,v in variants.items()})
    print("VIEWS",[p.name for p in views])
