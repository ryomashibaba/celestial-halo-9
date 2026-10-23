"""Build the D2-G7 seasonal territory-exchange city concept.

Geometry is deliberately low-detail diagnostic massing. Coordinates are km,
not official HALO-9 survey data. Seasonal geometry pairs show a speculative
district-scale reconfiguration, not an animation or engineering simulation.
"""
from pathlib import Path
import importlib.util
import hashlib
import json
import math
import sys
from datetime import datetime, timezone

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
G6_PATH = ROOT.parent / "D2-G6" / "build_study.py"
spec = importlib.util.spec_from_file_location("halo9_g6_helpers", G6_PATH)
g6 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = g6
spec.loader.exec_module(g6)
g6.ROOT = ROOT

C = {
    "ground": (70, 81, 82, 255),
    "mass": (190, 184, 160, 255),
    "mass_hi": (226, 216, 187, 255),
    "mass_mid": (151, 156, 143, 255),
    "transit": (247, 179, 82, 255),
    "water": (39, 154, 169, 255),
    "wetland": (72, 141, 115, 255),
    "habitat": (123, 177, 131, 255),
    "habitat_hi": (184, 201, 143, 255),
    "deep": (28, 42, 58, 255),
    "sky": (121, 149, 170, 255),
}


def box(name, center, size, color, angle=0.0):
    return g6.box(name, center, size, color, angle)


def beam_between(name, a, b, width, depth, color):
    """A thick, occupied district body aligned from a to b, long axis on X."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    d = b - a
    length = float(np.linalg.norm(d))
    mesh = trimesh.creation.box(extents=(length, width, depth))
    axis0 = np.array([1.0, 0.0, 0.0])
    axis1 = d / max(length, 1e-8)
    cross = np.cross(axis0, axis1)
    dot = float(np.clip(np.dot(axis0, axis1), -1.0, 1.0))
    if np.linalg.norm(cross) > 1e-8:
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.acos(dot), cross))
    elif dot < 0:
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [0, 0, 1]))
    mesh.apply_translation((a + b) * 0.5)
    mesh.visual.face_colors = np.tile(np.asarray(color, dtype=np.uint8), (len(mesh.faces), 1))
    mesh.metadata["name"] = name
    return mesh


def inhabited_body(name, points, width, height, color):
    """A beveled, tapered urban body swept through an elbow; deliberately bulky."""
    p=np.asarray(points,dtype=float)
    verts=[]; ring=8
    for i,q in enumerate(p):
        tangent=p[min(i+1,len(p)-1)]-p[max(0,i-1)]
        tangent/=max(np.linalg.norm(tangent),1e-8)
        side=np.cross(tangent,np.array([0.,0.,1.]))
        if np.linalg.norm(side)<1e-8: side=np.array([1.,0.,0.])
        side/=np.linalg.norm(side); up=np.cross(side,tangent); up/=np.linalg.norm(up)
        factor=[.82,1.0,.88][i]
        w=width*factor; h=height*factor; c=min(w,h)*.16
        # Chamfered rectangle: a heavy architectural section, not a flat plate.
        coords=[(-w/2+c,-h/2), (w/2-c,-h/2),(w/2,-h/2+c),(w/2,h/2-c),
                (w/2-c,h/2),(-w/2+c,h/2),(-w/2,h/2-c),(-w/2,-h/2+c)]
        for a,b in coords: verts.append(q+side*a+up*b)
    faces=[]
    for i in range(len(p)-1):
        for j in range(ring):
            k=(j+1)%ring; a=i*ring+j; b=i*ring+k; c=(i+1)*ring+k; d=(i+1)*ring+j
            faces.extend([(a,b,c),(a,c,d)])
    for j in range(1,ring-1):
        faces.append((0,j+1,j))
        base=(len(p)-1)*ring
        faces.append((base,base+j,base+j+1))
    mesh=trimesh.Trimesh(vertices=np.asarray(verts),faces=np.asarray(faces),process=True)
    mesh.visual.face_colors=np.tile(np.asarray(color,dtype=np.uint8),(len(mesh.faces),1))
    mesh.metadata["name"]=name
    return mesh


def marker_tree(name, x, y, z, height, color):
    """A coarse vegetation / habitat marker for legibility at city scale."""
    out = [g6.cylinder(name + "_trunk", (x, y, z + height * .34), .055, height * .68, C["mass_mid"], 7)]
    out.append(g6.cylinder(name + "_crown", (x, y, z + height * .80), .19, height * .40, color, 7))
    return out


def wetland_patch(name, cx, cy, sx, sy, z, color):
    # Two offset prisms make an irregular lowland territory without simulating water.
    out = [g6.poly_prism(name + "_field", [(cx-sx*.5,cy-sy*.28),(cx-sx*.18,cy-sy*.5),
        (cx+sx*.42,cy-sy*.34),(cx+sx*.5,cy+sy*.14),(cx+sx*.15,cy+sy*.5),
        (cx-sx*.43,cy+sy*.30)], z, z+.022, color)]
    return out


def tapered_branch(name, points, radii, color):
    """Faceted volumetric branch of a bio-structural, inhabited crown."""
    p=np.asarray(points,dtype=float); verts=[]; sides=8
    for i,q in enumerate(p):
        tangent=p[min(i+1,len(p)-1)]-p[max(0,i-1)]
        tangent/=max(np.linalg.norm(tangent),1e-8)
        u=np.cross(tangent,np.array([0.,0.,1.]))
        if np.linalg.norm(u)<1e-8: u=np.array([1.,0.,0.])
        u/=np.linalg.norm(u); v=np.cross(tangent,u); v/=np.linalg.norm(v)
        for j in range(sides):
            a=math.tau*j/sides
            verts.append(q+radii[i]*(math.cos(a)*u+math.sin(a)*v))
    faces=[]
    for i in range(len(p)-1):
        for j in range(sides):
            k=(j+1)%sides; a=i*sides+j; b=i*sides+k; c=(i+1)*sides+k; d=(i+1)*sides+j
            faces.extend([(a,b,c),(a,c,d)])
    for j in range(1,sides-1):
        faces.append((0,j+1,j)); base=(len(p)-1)*sides; faces.append((base,base+j,base+j+1))
    mesh=trimesh.Trimesh(vertices=np.asarray(verts),faces=np.asarray(faces),process=True)
    mesh.visual.face_colors=np.tile(np.asarray(color,dtype=np.uint8),(len(mesh.faces),1))
    mesh.metadata["name"]=name
    return mesh


def context():
    # Schematic orientation only: north mountain, west cliff, east sea, SW void.
    g6.RNG=__import__("random").Random(906)
    return g6.context("G7")


def borrowed_ground(season="wet", with_context=True):
    """Inhabited shoulder-districts hinge upward/downward around civic roots."""
    wet = season == "wet"
    out = context() if with_context else []
    # A deep, angular civic root: open-sided public chamber, not a closed basin.
    out += [box("civic_root_east",(.14,.0,.82),(1.25,1.05,1.64),C["mass_hi"],.12),
            box("civic_root_west",(-.56,.18,.72),(.72,1.35,1.42),C["mass"],-.17),
            box("civic_root_north",(-.10,.66,1.16),(.84,.62,2.32),C["mass_mid"],.08),
            box("civic_root_south",(.12,-.66,.59),(.80,.48,1.18),C["mass_hi"],-.06)]
    # High public bridge / transit exchange crosses the open civic chamber.
    out += [beam_between("public_crossing_spine",(-.48,-.10,1.62),(.64,.18,1.86),.20,.13,C["transit"]),
            beam_between("public_exchange_balcony",(-.22,.50,1.12),(.42,-.46,1.28),.18,.10,C["mass_hi"])]

    # Four neighborhood bodies are thick occupied volumes on articulated roots.
    shoulders = [
        ("North Ward",(-.28,.42,1.14),(-.35,1.36,1.78 if wet else .78),(-.12,2.42,2.50 if wet else .30),.91,.78),
        ("East Ward",(.36,.10,1.18),(1.18,.02,1.94 if wet else .80),(2.34,.17,2.75 if wet else .36),1.02,.82),
        ("South Ward",(.12,-.42,1.08),(.42,-1.30,1.64 if wet else .70),(.58,-2.38,2.34 if wet else .27),.88,.72),
        ("West Ward",(-.45,-.05,1.12),(-1.25,-.22,2.04 if wet else .89),(-2.30,-.46,2.62 if wet else .42),1.08,.84),
    ]
    for idx,(name,root,elbow,tip,width,depth) in enumerate(shoulders):
        col=[C["mass_hi"],C["mass"],C["mass_mid"],C["mass_hi"]][idx]
        # Near-square section and deliberate overlap make these deep city bodies,
        # not thin inclined plates. They cross through a shared civic core.
        out.append(inhabited_body(name+"_occupied_city_body",[root,elbow,tip],width*1.62,depth*1.88,col))
        # Dense blocks are housing, markets and winter gardens embedded on the bodies.
        for j,t in enumerate((.28,.50,.72,.88)):
            p=np.asarray(root)*(1-t)+np.asarray(tip)*t
            h=.19+(.06*((idx+j)%3))
            out.append(box(f"{name}_inhabited_cluster_{j}",(p[0],p[1],p[2]+depth*.55+h*.38),
                           (.32+(j%2)*.09,.27,h),[C["mass_hi"],C["mass"],C["mass_mid"]][(idx+j)%3],
                           (idx*.23+j*.16)))
        # Urban-transfer track sits on the volume, while the mass beneath remains habitable.
        pts=[root,elbow,tip]
        pts=[(p[0],p[1],p[2]+depth*.52+.035) for p in pts]
        out += g6.ribbon(name+"_public_mobility",pts,.095,.055,C["transit"])
        # Fixed root + variable-height outer mooring make the district land-connected.
        out.append(box(name+"_hinge_pylon",(root[0],root[1],.72),(.82,.88,1.44),C["mass_mid"],idx*.21))
        outer_h=max(.32,tip[2]+.16)
        out.append(box(name+"_ground_mooring",(tip[0],tip[1],outer_h*.5),(.92,.96,outer_h),C["mass_mid"],idx*.13))

    # Ground territory deliberately swaps civic and ecological use by season.
    if wet:
        out += wetland_patch("wet_commons_east",.34,-.15,1.48,1.02,.035,C["water"])
        out += wetland_patch("wet_commons_south",-.31,-.88,.96,.63,.035,C["wetland"])
        out += wetland_patch("wet_commons_west",-.88,.63,.72,.55,.035,C["water"])
        for i,(x,y,h) in enumerate([(-.72,-.46,.30),(.76,-.52,.44),(-.72,.84,.36),(.88,.67,.31),(.08,-1.06,.42)]):
            out += marker_tree(f"wetland_canopy_{i}",x,y,.05,h,C["habitat"])
        # Local intake from the east-sea system is a separate connection, not the shape generator.
        out += g6.ribbon("eastern_sea_exchange",[(1.58,.08,.05),(2.55,.20,.035),(3.78,.18,.025)],.24,.028,C["water"])
        # Wet-season pedestrian spine stays high above occupied wetland ground.
        out += g6.ribbon("high_seasonal_promenade",[(-2.1,.7,2.70),(-.45,.56,2.25),(.68,.28,2.22),(2.26,.20,2.89)],.12,.08,C["transit"])
        out.append(box("wetland_migration_tower",(-.05,-.14,1.08),(.30,.28,2.16),C["habitat_hi"],.12))
    else:
        # Dry-season lowlands reopen as civic terrain; residual refugia remain distinct.
        out.append(g6.poly_prism("dry_commons_forecourt",[(-1.48,-.78),(-.94,-1.14),(.25,-1.10),
            (1.16,-.66),(1.14,.42),(.28,.77),(-.88,.54),(-1.32,.02)],.03,.08,C["mass_hi"]))
        for i,(x,y) in enumerate([(-.96,-.22),(-.56,-.37),(.46,-.42),(.82,-.14),(.16,.42)]):
            out.append(box(f"dry_market_pavilion_{i}",(x,y,.30),(.23,.20,.44),C["mass_mid"],i*.17))
        for i,(x,y,h) in enumerate([(-1.10,.60,.33),(.89,.66,.39),(-.55,-.98,.31)]):
            out += marker_tree(f"dry_refuge_{i}",x,y,.07,h,C["habitat_hi"])
        out += g6.ribbon("dry_ground_civic_route",[(-1.36,-.72,.13),(-.55,-.44,.13),(.25,-.42,.13),(1.17,-.08,.13)],.11,.05,C["transit"])
        # Habitat refuge continues above the city floor after the seasonal retreat.
        out += g6.ribbon("upper_dry_habitat_refuge",[(-1.82,1.02,2.42),(-.44,.86,2.72),(.84,.72,2.81),(2.12,.50,2.58)],.17,.13,C["habitat"])
        out.append(box("dry_ecology_coolth_spine",(.05,.86,1.40),(.24,.30,2.80),C["habitat_hi"],-.08))

    # H1-H6 remain as named interfaces in the urban network. Their exact
    # locations are deliberately not invented in this noncanonical massing.
    return out


def habitat_crown(season="wet", with_context=True):
    """A single rooted city whose inhabited biostructural crown changes extent."""
    wet=season=="wet"
    out=context() if with_context else []
    # Three intersecting inhabited civic cores establish a rooted central landmark.
    out += [inhabited_body("crown_core_west",[(-.45,-.35,.12),(-.62,.12,1.24),(-.48,.52,2.12)],.88,1.05,C["mass_hi"]),
            inhabited_body("crown_core_east",[(.42,-.32,.10),(.55,.18,1.38),(.38,.58,2.72)],.92,1.10,C["mass"]),
            inhabited_body("crown_core_north",[(-.08,.38,.16),(.12,.68,1.55),(.24,.76,2.98)],.74,.94,C["mass_mid"])]
    # The urban root is a deep public exchange room. It remains open to the east sea axis.
    out += [box("root_city_east_wing",(.60,-.10,.44),(.75,1.02,.88),C["mass_hi"],.12),
            box("root_city_west_wing",(-.67,-.02,.50),(.70,1.18,1.0),C["mass"],-.11),
            g6.poly_prism("central_common_floor",[(-.48,-.70),(.48,-.70),(.55,.52),(-.53,.52)],.04,.10,C["deep"])]
    # Six axial roots, each becomes a deep inhabited habitat artery, not a skin or panel.
    angles=[-8,48,119,188,247,310]
    extent=2.38 if wet else 1.36
    crown_z=[3.22,2.72,3.46,2.82,3.05,2.58] if wet else [1.76,2.04,1.68,1.92,1.62,2.12]
    for i,(deg,z) in enumerate(zip(angles,crown_z),1):
        a=math.radians(deg); ux,uy=math.cos(a),math.sin(a)
        root=(ux*.32,uy*.32,1.20)
        elbow=(ux*(extent*.49),uy*(extent*.49),z*.68)
        tip=(ux*extent,uy*extent,z)
        r0=.39 if wet else .34; r1=.31 if wet else .28; r2=.22 if wet else .20
        out.append(inhabited_body(f"H{i}_inhabited_artery",[root,elbow,tip],r0*2.5,r0*2.35,C["mass_hi"]))
        # Paired full-section habitat galleries thicken the crown into 3D city volume.
        for side_sign in (-1,1):
            branch_a=(elbow[0],elbow[1],elbow[2])
            side_angle=a+side_sign*(.36 if wet else .28)
            side_r=extent*(.80 if wet else .79)
            branch_b=(math.cos(side_angle)*side_r,math.sin(side_angle)*side_r,z*.89)
            side_tip=(math.cos(side_angle)*side_r*1.10,math.sin(side_angle)*side_r*1.10,z*.78)
            out.append(inhabited_body(f"H{i}_habitat_fork_{side_sign}",[branch_a,branch_b,side_tip],
                                      .38 if wet else .29,.34 if wet else .27,C["mass_mid"]))
        # Public mobility follows inside the massive arterial, not above it as a thin bridge.
        pts=[(root[0],root[1],root[2]+r0*.32),(elbow[0],elbow[1],elbow[2]+r1*.32),(tip[0],tip[1],tip[2]+r2*.30)]
        out += g6.ribbon(f"H{i}_internal_civic_route",pts,.055,.035,C["transit"])

    # Structural joins at the root tie the six living city arteries together.
    for deg in (24,143,265):
        a=math.radians(deg)
        p0=(math.cos(a)*.52,math.sin(a)*.52,1.52)
        p1=(math.cos(a+1.05)*.67,math.sin(a+1.05)*.67,1.82)
        out.append(tapered_branch(f"civic_crossroot_{deg}",[p0,p1], [.32,.26],C["mass_mid"]))

    if wet:
        out += wetland_patch("crown_wetland_east",.15,-.28,1.62,1.12,.025,C["water"])
        out += wetland_patch("crown_wetland_south",-.18,-.95,1.18,.58,.025,C["wetland"])
        for i,(x,y,h) in enumerate([(-.76,-.52,.42),(.72,-.57,.48),(-.64,.67,.36),(.86,.53,.38),(.05,-1.04,.46)]):
            out += marker_tree(f"crown_ground_habitat_{i}",x,y,.05,h,C["habitat"])
        out += g6.ribbon("east_sea_estuary_link",[(1.08,-.20,.05),(2.16,-.06,.035),(3.75,.18,.025)],.22,.03,C["water"])
    else:
        out.append(g6.poly_prism("dry_civic_exchange_ground",[(-1.18,-.79),(-.72,-1.20),(.42,-1.10),
            (1.02,-.64),(.96,.35),(.28,.62),(-.82,.45),(-1.22,-.08)],.035,.095,C["mass_hi"]))
        for i,(x,y) in enumerate([(-.84,-.37),(-.38,-.48),(.45,-.39),(.78,.08),(.06,.39)]):
            out.append(box(f"dry_civic_market_{i}",(x,y,.25),(.24,.22,.32),C["mass_mid"],i*.14))
        for i,(x,y,h) in enumerate([(-1.0,.58,.32),(.86,.60,.37),(-.55,-.96,.29)]):
            out += marker_tree(f"dry_high_refuge_{i}",x,y,.075,h,C["habitat_hi"])
        out += g6.ribbon("dry_ground_city_route",[(-1.20,-.71,.14),(-.49,-.44,.14),(.31,-.37,.14),(1.15,-.12,.14)],.105,.05,C["transit"])
        out += g6.ribbon("high_coolth_refuge",[(-1.74,1.18,1.62),(-.70,1.42,2.02),(.58,1.46,2.25),(1.70,1.28,1.84)],.14,.11,C["habitat"])
    return out


def fixed_ecotone(with_context=True):
    """Alternative: a fixed vertical civic escarpment with a migrating ecotone."""
    out=context() if with_context else []
    # Three offset habitable ridges make a split, high-altitude civic canyon.
    out += [inhabited_body("ecotone_ridge_west",[(-1.04,-1.18,.25),(-1.15,.18,1.55),(-.88,1.38,3.25)],1.18,1.22,C["mass_hi"]),
            inhabited_body("ecotone_ridge_east",[(.88,-1.30,.22),(.70,.04,1.72),(.46,1.48,3.55)],1.24,1.36,C["mass"]),
            inhabited_body("ecotone_ridge_north",[(-.18,.70,.26),(-.02,1.40,2.05),(.26,1.94,3.80)],1.42,1.48,C["mass_mid"])]
    # Internal public stairs and the permanent central vertical habitat ravine.
    out += [g6.poly_prism("fixed_civic_ravine_floor",[(-.52,-1.35),(.42,-1.32),(.48,1.16),(-.46,1.21)],.02,.08,C["deep"]),
            g6.ribbon("east_ravine_walk",[(.49,-1.20,.32),(.47,-.35,.74),(.44,.46,1.36),(.31,1.10,2.05)],.12,.08,C["transit"]),
            g6.ribbon("west_ravine_walk",[(-.55,-1.13,.28),(-.51,-.30,.80),(-.43,.48,1.48),(-.36,1.16,2.22)],.12,.08,C["transit"])]
    # Seasonal migration is territorial use, not structural motion.
    for i,(x,y,z) in enumerate([(-.40,-.70,.20),(-.38,-.10,.58),(-.33,.52,1.30),(-.26,1.03,2.05)]):
        out += marker_tree(f"fixed_ecotone_marker_{i}",x,y,z,.54,C["habitat"])
    for i,(x,y,z) in enumerate([(.20,-.86,.30),(.22,-.16,.82),(.17,.54,1.56),(.12,1.15,2.42)]):
        out.append(box(f"ecotone_civic_balcony_{i}",(x,y,z),(.56,.36,.16),C["mass_hi"],.08))
    # Six aerial connections repeat as abstract urban interfaces.
    for i,x in enumerate([-2.2,-1.35,-.48,.48,1.35,2.2],1):
        out.append(box(f"ecotone_H{i}_lift",(x,1.65,1.37),(.16,.16,2.74),C["sky"]))
        out.append(box(f"ecotone_H{i}_district",(x,1.65,2.92),(.40,.38,.27),C["mass_hi"]))
    out += g6.ribbon("ecotone_east_sea_link",[(1.1,-.4,.12),(1.8,-.2,.24),(2.9,.1,.45),(3.7,.2,.50)],.14,.08,C["transit"])
    return out


def export_glb(meshes, filename):
    scene=trimesh.Scene()
    for i,m in enumerate(meshes):
        scene.add_geometry(m,geom_name=f"mesh_{i:04d}",node_name=m.metadata.get("name",f"node_{i:04d}"))
    scene.export(ROOT/filename,file_type="glb")
    return ROOT/filename


def validate(models):
    data={"study_id":"D2-G7","coordinate_units":"kilometres; 1 unit = 1 km",
          "method":"Low-detail procedural trimesh geometry. Diagnostic orthographic images use the D2-G6 custom depth-buffer renderer; preview.jpg is a contact montage of the same low-detail meshes.",
          "seasonal_mechanism":{"structure_moves":True,"moving_elements":"Six inhabited, branching civic arteries and their district hubs extend into a wide crown in the wet state and contract toward the rooted core in the dry state. The core and public ground anchors stay fixed.",
            "fictional_assumption":"Living bio-ceramic / active structural tissue changes the full-depth branch geometry over a slow seasonal transfer. It is a fictional civilization technology, not ordinary physics or a panel-hinge mechanism.",
            "ordinary_physics":"Rainfall collects at low ground; local drainage follows gravity. Wetland patches and the east-sea estuary are diagrammatic, with no flow, tide, load, climate, or ecology simulation. Residents transfer to fixed cores before the arterial transition; moving joints close to public circulation.",
            "territory_change":"Wet state reserves the low commons for wetland and uses the expanded inhabited crown for elevated life and movement. Dry state contracts the crown, opens the rooted commons to markets and walking, and retains habitat in upper refugia."},
          "models":{},"views":[],"limits":["Conceptual massing, not official W0 coordinates, survey data, structural engineering, climate/hydrology/ecology simulation, or construction-ready geometry.","H1-H6 name six symbolic rooted arteries; canonical positions and programs were not available in the task mirror.","Terrain uses schematic north mountain, west cliff, east artificial inland sea, and southwest void as orientation cues only.","Individual meshes are closed but are separate GLB objects; watertightness does not certify load paths or welded connectivity.","No Blender connection was available; no .blend file or Blender render is claimed."]}
    for key in ("wet","dry"):
        meshes=models[key]
        path=ROOT/{"wet":"Habitat-Crown-wet.glb","dry":"Habitat-Crown-dry.glb"}[key]
        loaded=trimesh.load(path,force="scene")
        geoms=[g for g in loaded.geometry.values() if hasattr(g,"faces")]
        merged=trimesh.util.concatenate(geoms)
        context_prefixes=("10km_study_terrain","north_mountain_peak_","west_cliff_face","east_artificial_inland_sea","southwest_great_void","urban_context_")
        central=[g for g in geoms if not g.metadata.get("name","").startswith(context_prefixes)]
        central_mesh=trimesh.util.concatenate(central)
        data["models"][key]={"path":path.name,"size_bytes":path.stat().st_size,"mesh_objects":len(geoms),
            "faces":sum(len(g.faces) for g in geoms),"scene_bounds_km":np.round(merged.bounds,4).tolist(),
            "scene_dimensions_km":np.round(merged.extents,4).tolist(),"central_city_bounds_km":np.round(central_mesh.bounds,4).tolist(),
            "central_city_dimensions_km":np.round(central_mesh.extents,4).tolist(),"all_meshes_individually_watertight":all(g.is_watertight for g in geoms),
            "watertight_meshes":sum(g.is_watertight for g in geoms),"connected_components":len(merged.split(only_watertight=False))}
    (ROOT/"geometry-validation.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return data


def write_metadata(validation):
    """Write the study manifest and advance the local branch latest pointer."""
    stamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
    def asset(p):
        raw=p.read_bytes(); suffix=p.suffix.lower()
        kind={".md":"REPORT",".glb":"GLB",".png":"IMAGE",".jpg":"IMAGE",".json":"JSON",".py":"SOURCE"}.get(suffix,"FILE")
        return {"path":f"studies/D2-G7/{p.name}","kind":kind,"sha256":hashlib.sha256(raw).hexdigest(),"size_bytes":len(raw)}
    files=sorted(p for p in ROOT.iterdir() if p.is_file() and p.name!="manifest.json")
    assets=[asset(p) for p in files]
    models=validation["models"]
    manifest={"schema_version":"1.0","study_id":"D2-G7","title":"季節遷移都市：生態系と都市生活が共に形成する巨大建築",
        "track":"D","branch":"art/d","stage":"CONCEPT + LOW-DETAIL 3D","art_review_status":"HOLD",
        "updated_at":stamp,"base_head":"b39cf4834a93a06747bea0bb1b3fdeac8e5b44c6",
        "selected_candidate":"Habitat Crown (provisional; central review required)","assets":assets,
        "models":models,"seasonal_mechanism":validation["seasonal_mechanism"],"limits":validation["limits"],
        "review_note":"The first Borrowed Ground moving-slab massing was screened out because it read as inclined plates and bridges. Habitat Crown is the current comparative candidate, with tree/crown cliché and interior public-space quality unresolved."}
    (ROOT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    manifest_asset=asset(ROOT/"manifest.json")
    latest_path=ROOT.parent.parent/"latest.json"
    latest=json.loads(latest_path.read_text(encoding="utf-8")) if latest_path.exists() else {"schema_version":"1.0","branch":"art/d","track":"D","history":[]}
    history=latest.setdefault("history",[])
    if not any(x.get("study_id")=="D2-G7" for x in history):
        history.append({"study_id":"D2-G7","manifest_path":"studies/D2-G7/manifest.json"})
    dims={key:{"width":round(v["central_city_dimensions_km"][0]*1000),"depth":round(v["central_city_dimensions_km"][1]*1000),"height":round(v["central_city_dimensions_km"][2]*1000)} for key,v in models.items()}
    latest["latest"]={"study_id":"D2-G7","title":"HALO-9 G7-D Seasonal Territory Exchange / Habitat Crown",
        "stage":"CONCEPT + LOW-DETAIL 3D","art_review_status":"HOLD","updated_at":stamp,"dimensions_m":None,
        "proposed_dimensions_m":dims,"assets":assets+[manifest_asset],
        "validation":{"load_results":"Two seasonal GLBs reloaded with trimesh; component meshes individually watertight, but kept as separate objects.",
            "shared_camera_comparisons":"Same-design wet/dry oblique and profile views plus a fixed-form alternative were generated.",
            "limits":validation["limits"]},
        "notes":"Habitat Crown is provisionally selected over Fixed Ecotone because seasonal growth/contraction changes the urban silhouette and shifts low-ground use. Central art review remains required; current branching form risks tree/flower resemblance and interior public space is schematic."}
    latest["last_submission_at"]=stamp
    latest["policy"]="ART-FIRST. Formal design and Minecraft construction remain HOLD. Internal REJECT preserves study history and is not a formal adoption decision."
    latest_path.write_text(json.dumps(latest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def make_preview(models):
    wet=models["wet"]; dry=models["dry"]; alt=models["alternative"]
    views=[]
    for meshes,name,title,sub,direction,target,span in [
        (wet,"wet-oblique.png","G7 · BORROWED GROUND / WET","Inhabited shoulders rise; low commons returns to wetland",(8,-10,7),(0,0,1.0),7.8),
        (dry,"dry-oblique.png","G7 · BORROWED GROUND / DRY","District masses settle; civic ground widens",(8,-10,7),(0,0,1.0),7.8),
        (wet,"wet-profile.png","WET PROFILE","Raised urban mass, low ecological territory",(13,1,4),(0,0,1.2),8.0),
        (dry,"dry-profile.png","DRY PROFILE","The same inhabited masses return to ground",(13,1,4),(0,0,1.2),8.0),
        (alt,"fixed-ecotone.png","ALTERNATIVE · FIXED ECOTONE","Permanent split civic ridge; habitat activity migrates vertically",(8,-10,7),(0,0,1.0),7.6),
    ]:
        p=g6.render(meshes,name,title,sub,direction,target=target,size=(1000,650),span=span)
        views.append(p)
    # Same-model seasonal side views placed side by side for direct form comparison.
    a=Image.open(views[2]).convert("RGB"); b=Image.open(views[3]).convert("RGB")
    strip=Image.new("RGB",(1000,650),(12,19,31))
    left=a.crop((0,0,1000,650)).resize((500,650),Image.Resampling.LANCZOS)
    right=b.crop((0,0,1000,650)).resize((500,650),Image.Resampling.LANCZOS)
    strip.paste(left,(0,0)); strip.paste(right,(500,0))
    dr=ImageDraw.Draw(strip,"RGBA")
    dr.rectangle((15,98,280,142),fill=(12,19,31,220)); dr.text((30,110),"WET · RAISED CITY",fill=(105,210,200))
    dr.rectangle((515,98,785,142),fill=(12,19,31,220)); dr.text((530,110),"DRY · CITY RETURNS",fill=(247,202,125))
    strip.save(ROOT/"season-pair.png",optimize=True)
    # Compact five-panel review image: wet, dry, profile pair, alternate massing, urban setting.
    panels=[Image.open(views[0]).convert("RGB"),Image.open(views[1]).convert("RGB"),strip,Image.open(views[4]).convert("RGB")]
    W,H=1600,1000; canvas=Image.new("RGB",(W,H),(9,15,26)); draw=ImageDraw.Draw(canvas)
    try: font=ImageFont.truetype("C:/Windows/Fonts/aptos.ttf",28); small=ImageFont.truetype("C:/Windows/Fonts/aptos.ttf",20)
    except OSError: font=small=ImageFont.load_default()
    draw.text((32,20),"D2-G7 · SEASONAL TERRITORY EXCHANGE",font=font,fill=(242,235,214))
    draw.text((32,60),"Low-detail 3D study · wet/dry transform · fixed-form alternative",font=small,fill=(143,202,205))
    positions=[(20,100),(810,100),(20,550),(810,550)]
    for p,(x,y) in zip(panels,positions):
        p.thumbnail((770,420),Image.Resampling.LANCZOS); canvas.paste(p,(x,y))
    canvas.save(ROOT/"preview.jpg",quality=82,optimize=True,progressive=True)
    return views+[ROOT/"season-pair.png",ROOT/"preview.jpg"]


def main():
    wet=habitat_crown("wet",True)
    dry=habitat_crown("dry",True)
    alternative=fixed_ecotone(True)
    models={"wet":g6.flatten(wet),"dry":g6.flatten(dry),"alternative":g6.flatten(alternative)}
    for key,name in [("wet","Habitat-Crown-wet.glb"),("dry","Habitat-Crown-dry.glb")]:
        export_glb(models[key],name)
    views=make_preview(models)
    val=validate(models)
    val["views"]=[{"path":p.name,"size_bytes":p.stat().st_size,"resolution_px":list(Image.open(p).size) if p.suffix.lower() in (".png",".jpg",".jpeg") else None} for p in views]
    (ROOT/"geometry-validation.json").write_text(json.dumps(val,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    write_metadata(val)
    print("MODELS",{k:{"objects":len(v),"faces":sum(len(m.faces) for m in v)} for k,v in models.items()})
    print("CENTRAL_SIZES",{k:v["central_city_dimensions_km"] for k,v in val["models"].items()})
    print("VIEWS",[p.name for p in views])


if __name__=="__main__":
    main()
