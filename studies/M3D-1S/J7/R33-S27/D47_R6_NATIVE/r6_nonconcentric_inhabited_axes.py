"""D47-R6: two nonconcentric THREE-AXIS civic-city spatial G0 candidates in REAL Blender.
Art-first falsification. NO full 10 km city, no canonical coordinates, no Minecraft.
A: THREE_DISPLACED_URBAN_GORGES, three different oriented inhabited cliffs.
B: TIDAL_CONFLUENCE_CITY, different city-axis direction, high reversal world.
All 3D is native editable Blender mesh. Voids are physical gaps between genuinely
independent occupied urban bank geometry; no fake software generated pictures.
Early art G0 first, do NOT append decorations to an ART-REJECTED macro.
"""
import bpy, math,sys,json,hashlib
from mathutils import Vector
from pathlib import Path
P=Path(sys.argv[-1]);P.mkdir(parents=True,exist_ok=True)
def mat(name,rgb):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);return m
ivory=mat("01 Civic bone",(.72,.73,.66))
slate=mat("02 shaded cliff",(.22,.30,.34))
blue=mat("03 public bridge blue",(.27,.48,.53))
copper=mat("04 inhabited cultural copper",(.54,.38,.29))
ground=mat("05 public terrain",(.38,.45,.43))
shade=mat("06 open urban rim",(.46,.51,.53))
sun=mat("07 upper city",(.82,.71,.49))
def reset():
    bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        if c.name!="Collection" and c.users==0:bpy.data.collections.remove(c)
def grp(n):
    c=bpy.data.collections.get(n)
    if c is None:
        c=bpy.data.collections.new(n)
        bpy.context.scene.collection.children.link(c)
    return c
def obj(n,vs,fs,m,col,role):
    mesh=bpy.data.meshes.new(n+"_ACTUAL_EDITABLE_MESH")
    mesh.from_pydata(vs,[],fs);mesh.update()
    o=bpy.data.objects.new(n,mesh);grp(col).objects.link(o);mesh.materials.append(m)
    o["functional_role"]=role
    return o
def bridge_volume(n,A,B,matl,col,role):
    # Corners A and B are each a closed (ordered) 3D transverse section.
    assert len(A)==len(B) and len(A)>=3
    k=len(A);vs=list(A)+list(B)
    fs=[tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]
    for j in range(k):fs.append((j,(j+1)%k,(j+1)%k+k,j+k))
    return obj(n,vs,fs,matl,col,role)
def box(n,c,size,m,col,role):
    x,y,z=c;dx,dy,dz=size
    v=[(x+u*dx/2,y+v*dy/2,z+w*dz/2) for w in [-1,1] for v in [-1,1] for u in [-1,1]]
    f=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(1,5,7,3),(3,7,6,2),(2,6,4,0)]
    return obj(n,v,f,m,col,role)
def add_strip(n,rows,matl,col,role):
    # A single real continuous winding surface, no screenshot-only panel.
    k=len(rows[0]);assert k==2
    vs=[p for row in rows for p in row]
    fs=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(rows)-1)]
    return obj(n,vs,fs,matl,col,role)
def local(point,side,offset,up):
    # point=(x,y,z); side a true horizontal perpendicular to this axis.
    return (point[0]+side[0]*offset,point[1]+side[1]*offset,point[2]+up)
def frames(st):
    # Ensures distinct true axes rather than radial arrays; lateral changes with path.
    r=[]
    for i,p in enumerate(st):
        a=st[max(0,i-1)];b=st[min(len(st)-1,i+1)]
        dx=b[0]-a[0];dy=b[1]-a[1]
        mag=math.hypot(dx,dy)
        assert mag>0
        r.append((p,(-dy/mag,dx/mag)))
    return r
def bank_section(p,s,edge,outer,height,sign,lean=0):
    # Nonrectangular inhabited urban cliff. Center void has NO enclosure.
    # "L" and terraced face is a bounded true solid, not a billboard.
    lo=sign*edge; hi=sign*outer
    mid=sign*(edge+(outer-edge)*.53)
    lip=sign*(edge+(outer-edge)*.16)
    pts=[
        (lo,-64),(hi,-64),(hi+sign*95,height*.29),
        (hi+sign*35,height*.66),
        (mid+sign*lean,height*1.0),
        (mid-sign*38,height*.74),
        (lip+sign*58,height*.51),
        (lip,height*.28)
    ]
    return [local(p,s,x,z) for x,z in pts]
def add_arm(tag,st,width,heights,style,variant):
    fr=frames(st)
    assert len(fr)==len(width)==len(heights)
    base=f"URBAN_AXIS_{tag}_"
    axis_col=f"01 CITY {tag} INHABITED CLIFFS"
    # 3 physical nested, distinct inhabited districts on each side, NEVER one ring.
    for sign,side_name in [(-1,"WEST_BANK"),(1,"EAST_BANK")]:
        for i in range(len(fr)-1):
            p0,s0=fr[i];p1,s1=fr[i+1]
            w0=width[i];w1=width[i+1]
            h0=heights[i]*(.9 if sign<0 else 1.12)
            h1=heights[i+1]*(.9 if sign<0 else 1.12)
            edge0=w0*.42;edge1=w1*.42
            outer0=w0*(1.05 if sign<0 else 1.13)
            outer1=w1*(1.05 if sign<0 else 1.13)
            A=bank_section(p0,s0,edge0,outer0,h0,sign,lean=55 if style=="riven" else -45)
            B=bank_section(p1,s1,edge1,outer1,h1,sign,lean=5 if style=="riven" else 85)
            m=ivory if (i+int(sign>0))%2 else slate
            bridge_volume(base+side_name+f"_S{i:02d}_INHABITED_LANDMASS",
                    A,B,m,axis_col,
                    "large composite occupied cliff volume with faceted public-facing section; rooms within mass NOT validated")
        # Physical parallel open terraces, with upper inhabited city at distinct elevations.
        for level in range(3):
            floor=[]
            for i,(p,s) in enumerate(fr):
                u=width[i]*(.52+.17*level)*sign
                z=heights[i]*(.19+.17*level)
                floor.append([local(p,s,u-45,z),local(p,s,u+45,z+14*sign)])
            add_strip(base+side_name+f"_L{level}_TERRACE",
                      floor, sun if level==2 else copper,
                      "02 REAL PUBLIC WALKWAY SURFACES",
                      "actual outdoor inhabited terrace; end connections and accessibility not certified")
        # City legibility: physically framed occupied facade on cliff inner lip,
        # not black painted windows on a closed wall.
        for i in range(len(fr)-1):
            if i%2:continue
            a,s=fr[i];b,t=fr[i+1]
            for k in range(2):
                za=heights[i]*(.27+.24*k)
                zb=heights[i+1]*(.27+.24*k)
                edgea=sign*width[i]*.48;edgeb=sign*width[i+1]*.48
                sec0=[local(a,s,edgea-21,za-22),local(a,s,edgea+21,za-22),
                      local(a,s,edgea+21,za+22),local(a,s,edgea-21,za+22)]
                sec1=[local(b,t,edgeb-21,zb-22),local(b,t,edgeb+21,zb-22),
                      local(b,t,edgeb+21,zb+22),local(b,t,edgeb-21,zb+22)]
                bridge_volume(base+side_name+f"_COURT_FACADE_K{k}_S{i}",
                  sec0,sec1,shade,"03 FACADE SECTION CITY",
                  "actual architectural band covering portions of mass; not proved as inhabitable interior")
    # Below & over axes civic public movement surface: central, truly open axial street.
    street=[]
    for i,(p,s) in enumerate(fr):
        r=width[i]*.28
        street.append([local(p,s,-r,-35),local(p,s,r,-35)])
    add_strip(base+"CENTER_OPEN_AIR_PUBLIC_STREET",street,ground,
             "04 CONNECTED AXIAL PUBLIC GROUND",
             "physical open civic ground strip; full path/collision/level engineering unverified")
    # Major open atrium interruptions. They are intentionally not a dome or arch.
    # Two inhabited crossing decks leave broad public air between segments.
    for i in [2,4] if len(fr)>5 else [2]:
        p,s=fr[i]
        if i+1>=len(fr):continue
        if style=="faulted" and i==4:continue
        edge=width[i]*.56
        zz=heights[i]*(.75 if i==2 else 1.13)
        sections=[]
        for j in [i-1,i,i+1]:
            if not (0<=j<len(fr)):continue
            q,ss=fr[j]
            wj=width[j]*(.55 if j!=i else .85)
            z=heights[j]*(.75 if i==2 else 1.13)
            sections.append([local(q,ss,-wj,z),local(q,ss,wj,z+64)])
        if len(sections)>1:
            add_strip(base+f"CROSSCIVIC_BRIDGE_{i}",sections,blue,
              "05 PUBLIC CROSS CITY BRIDGES",
              "elevated bridge deck with no certified vertical access")
def create(variant):
    reset()
    if variant=="A":
        axes={
          "W0_TO_NORTH":([(-2500,-1600,70),(-1930,-1200,410),(-1190,-600,850),
                          (-370,60,1380),(510,530,1920),(1410,730,2470),(2400,1090,2820)],
                          [380,450,505,550,460,380,300],[440,560,665,770,620,570,435],"riven"),
          "WEST_TO_SEA":([(-2150,1550,150),(-1550,1070,620),(-870,410,1040),
                          (50,-190,1570),(870,-790,2050),(1580,-1430,2590),(2260,-2060,3070)],
                          [480,445,505,435,560,500,330],[460,550,700,750,660,600,430],"faulted"),
          "REVERSED_HIGH":([(-900,-2700,3070),(-690,-1950,3420),(-400,-1040,3630),
                          (-200,-100,3720),(280,920,3490),(710,1750,3190),(1050,2640,2840)],
                          [390,540,590,600,455,390,270],[570,690,770,750,670,575,450],"riven")
        }
    else:
        axes={
          "DESCENDING_CIVIC":([(-2650,900,90),(-1940,580,300),(-1250,210,700),
                                (-350,-220,1340),(650,-660,2070),(1500,-1090,2720),(2340,-1220,3020)],
                                [340,450,460,680,530,460,320],[420,535,720,910,670,550,410],"faulted"),
          "INCLINED_GALLERY":([(-2000,-1940,110),(-1580,-1090,590),(-1080,-240,1000),
                                (-370,420,1430),(610,1060,2090),(1510,1580,2460),(2150,2110,2600)],
                                [360,390,455,485,660,495,340],[350,515,580,610,810,570,440],"riven"),
          "UPPER_REVERSE_WARD":([(-2150,-420,3500),(-1390,-740,3760),(-570,-900,4030),
                                (230,-540,3970),(940,-130,3500),(1530,500,2990),(2000,1180,2650)],
                                [420,475,620,590,530,405,285],[600,725,820,790,620,540,390],"faulted")
        }
    for name,(stations,width,height,style) in axes.items():
        add_arm(name,stations,width,height,style,variant)
    # Real public ground arrival in the noncanonical study, no faked completed W0.
    box("NONCANONICAL_GROUND_CITY_APPROACH",(0,-2800,-105),
        (3900,750,80),ground,"06 CONTEXT ONLY","provisional terrain concept, NOT complete W0")
    box("NONCANONICAL_EAST_STUDY_WATER",(3300,-100,-130),
        (1400,5700,28),blue,"06 CONTEXT ONLY","temporary directional locator, NOT W0 coast")
    # Cites central open civic axes and 3 critical open-air void corridors.
    voids={"G0_GROUND_CONFLUENCE":(0,-2250,230),
           "G1_MID_CIVIC_AIR":(0,0,1550),
           "G2_REVERSED_SKY_AIR":(0,200,2980)}
    def camera(n,loc,target,ortho):
        d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d)
        grp("07 FIXED G0 CAMERA SYSTEM").objects.link(o);o.location=loc
        o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
        d.clip_end=25000
        if ortho:d.type="ORTHO";d.ortho_scale=ortho
        else:d.type="PERSP";d.lens=24
    cameras=[
        ("01_FRONT",(0,-9000,2900),(0,0,2150),9400),
        ("02_OBLIQUE",(8000,-6500,5400),(0,0,2200),9500),
        ("03_SIDE",(9000,800,3400),(0,0,2300),9000),
        ("04_REAR",(-500,9000,3200),(0,0,2300),10000),
        ("05_AERIAL",(4800,-4100,11300),(0,0,2000),11000),
        ("06_GROUND_UP",(200,-1400,45),(0,200,3100),None),
        ("07_CIVIC_VOID",(150,-250,1470),(150,750,3050),None)
    ]
    for n,eye,target,orto in cameras:camera(n,eye,target,orto)
    scene=bpy.context.scene
    scene["research"]="D47-R6 NONCONCENTRIC TRIPLE URBAN AXIS G0"
    scene["variant"]=variant
    scene["art_approved"]=False
    scene["official_coords_verified"]=False
    scene["M247_C_protected"]=True
    scene["city_10km_master_complete"]=False
    scene["minecraft_write"]=False
    scene["inhabited_room_clearance_verified"]=False
    scene["all_axis_transfers_certified"]=False
    scene["macro_public_void_probes"]=str(voids)
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.light="STUDIO"
    scene.display.shading.color_type="MATERIAL"
    scene.display.shading.show_cavity=True
    scene.render.resolution_x=1050
    scene.render.resolution_y=710
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    native=P/(variant+"_G0_NATIVE_EDITABLE.blend")
    glb=P/(variant+"_G0_GLTF.glb")
    bpy.ops.wm.save_as_mainfile(filepath=str(native))
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
                export_cameras=False,export_lights=False)
    for name,*_ in cameras:
        scene.camera=bpy.data.objects[name]
        scene.render.filepath=str(P/(variant+"_"+name+".png"))
        bpy.ops.render.render(write_still=True)
    return {
     "variant":variant,
     "meaning":"R6 nonconcentric 3 axis inhabitable cliff and separate ground worlds in genuine 3D",
     "axis_names":list(axes),
     "axis_first_last_stations":{k:[v[0][0],v[0][-1]] for k,v in axes.items()},
     "scene_meshes":len([o for o in bpy.data.objects if o.type=="MESH"]),
     "render_names":[variant+"_"+n+".png" for n,*_ in cameras],
     "native_blend":native.name,"native_glb":glb.name,
     "void_probe_hypotheses_not_verified":voids,
     "art":"NOT REVIEWED",
     "all_internal_rooms_and_vertical_routes":False,
     "urban_residential_appearance_proven":False,
     "m204_w0_anchor_calibrated":False,
     "full_city_master":False,
     "minecraft_construction":False
    }
results=[]
for variant in ("A","B"):
    print("R6_BUILD",variant,flush=True)
    results.append(create(variant))
p={"state":"G0_REAL_BLENDER_RENDERED_ART_UNREVIEWED",
   "blender_version":bpy.app.version_string,
   "not_claude_eb_spiral_copy":True,
   "city_scope":"local 3-axis macro research only NOT formal master",
   "variants":results,
   "gui_or_mcp_used":False,
   "art_adopted":False,
   "main_modified":False,
   "minecraft_construction":False}
(P/"R6_G0_MANIFEST.json").write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding="utf8")
print("D47_R6_G0_TWO_REAL_VARIANTS_DONE_UNREVIEWED",json.dumps(
    {r["variant"]:r["scene_meshes"] for r in results}))
