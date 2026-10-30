"""D48-R1: three independent, truly editable macro-city research scenes.
All XYZ are declared ART-DIRECTION TEMP coordinates; not M204/W0/world.
No borrowed rejected E6 geometry, no world write, no automatic art PASS.
Blender 4.5 bpy wheel; run: python d48_r1_native_macro_studies.py OUTPUT_DIR
"""
import bpy
from mathutils import Vector
from pathlib import Path
import math, json, sys, hashlib, random

ROOT=Path(sys.argv[-1]).resolve()
ROOT.mkdir(parents=True,exist_ok=True)
PI=math.pi
VIEWS={
"01_NORTH_PANORAMA":((7600,-8300,6600),(0,0,1900),38),
"02_EAST_SEA":((8100,4400,3200),(0,0,1800),39),
"03_SOUTHWEST_VOID":((-8500,8500,4300),(0,0,1900),36),
"04_WEST_REAR":((-8600,-1300,3700),(0,0,2000),38),
"05_GROUND_APPROACH":((550,-2900,110),(0,0,1400),33),
"06_SKY_DISTRICT":((2900,-2000,3050),(350,600,2900),40),
}
ART={
"A":{"name":"STRATIFIED_CIVIC_CONTINUUM","col":(.70,.78,.75,1),"accent":(.89,.65,.37,1)},
"B":{"name":"INTERLACED_CIVIC_FLOWS","col":(.84,.81,.69,1),"accent":(.24,.73,.72,1)},
"C":{"name":"DISPLACED_INHABITED_LANDMASSES","col":(.67,.79,.83,1),"accent":(.85,.70,.46,1)},
}
def mat(name,rgb):
 m=bpy.data.materials.new(name)
 m.diffuse_color=rgb
 return m
def cuboid(name,xyz,size,material,group,role,asset_id=None,rot=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz)
 o=bpy.context.object
 o.name=name
 o.dimensions=size
 o.rotation_euler.z=rot
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(material)
 o["D48_role"]=role
 if asset_id: o["D48_asset_id"]=asset_id
 group.objects.link(o)
 for coll in list(o.users_collection):
  if coll!=group: coll.objects.unlink(o)
 bevel=o.modifiers.new("architectural_edge_lighting","BEVEL");bevel.width=min(size)*.055;bevel.segments=1
 o.modifiers.new("weighted_surface_normals","WEIGHTED_NORMAL")
 return o
def mesh(name,vs,fs,material,group,role,asset=None):
 m=bpy.data.meshes.new(name+"_editable_mesh")
 m.from_pydata(vs,[],fs)
 m.update()
 o=bpy.data.objects.new(name,m)
 group.objects.link(o)
 o.data.materials.append(material)
 o["D48_role"]=role
 if asset:o["D48_asset_id"]=asset
 return o
def loft_sections(name,rings,material,group,role,asset=None):
 # Explicit editable per-layer control cage, not a copied E6 primitive.
 n=len(rings[0]);assert n>=4 and all(len(r)==n for r in rings)
 vs=[p for ring in rings for p in ring]
 faces=[tuple(range(n-1,-1,-1))]
 for j in range(len(rings)-1):
  for k in range(n):
   q=(k+1)%n
   faces.append((j*n+k,j*n+q,(j+1)*n+q,(j+1)*n+k))
 faces.append(tuple((len(rings)-1)*n+k for k in range(n)))
 return mesh(name,vs,faces,material,group,role,asset)
def track(name,pts,width,material,group,role,asset=None):
 # Geometry is a real curve tube with 3D cubic smoothing.
 cu=bpy.data.curves.new(name+"_editable_spline","CURVE")
 cu.dimensions="3D";cu.resolution_u=12;cu.bevel_depth=width;cu.bevel_resolution=2
 sp=cu.splines.new("BEZIER");sp.bezier_points.add(len(pts)-1)
 for p,xyz in zip(sp.bezier_points,pts):
  p.co=xyz;p.handle_left_type="AUTO";p.handle_right_type="AUTO"
 ob=bpy.data.objects.new(name,cu);group.objects.link(ob);ob.data.materials.append(material)
 ob["D48_role"]=role
 if asset:ob["D48_asset_id"]=asset
 return ob
def flower_ridge(name,xy,size,z,mat0,grp,phase,n=9,theta=.0,thickness=180):
 # Sculpted (irregular) coastal/mountain civic landmass with finite depth.
 x0,y0=xy;vs=[];rings=[]
 for scale,zz in [(1.0,z-thickness),(.86,z+thickness*.20),(.56,z+thickness)]:
  ring=[]
  for k in range(n):
   a=2*PI*k/n+theta
   rr=size*(1+.15*math.sin(k*2.4+phase)+.07*math.cos(k*5+phase))
   ring.append((x0+rr*scale*math.cos(a),y0+rr*.72*scale*math.sin(a),zz+44*math.sin(3*a+phase)))
  rings.append(ring)
 return loft_sections(name,rings,mat0,grp,"INHABITED_THICK_CIVIC_GROUND")
def ground_sculpt(mat0,grp,mode):
 # Three-dimensional 12km basin, distinct from the skyline structures.
 N=29;vs=[];faces=[]
 for j in range(N):
  y=-6000+12000*j/(N-1)
  for i in range(N):
   x=-6000+12000*i/(N-1)
   north=1250*max(0,(-y-2200)/3800)**1.25
   west=880*max(0,(-x-2800)/3200)
   ridges=170*math.sin((x+1600)/650)*math.sin((y-200)/1100)
   void=-450 if x< -1500 and y>1900 else 0
   east=-300 if x>3600 else 0
   z=-100+north+west+ridges+void+east
   vs.append((x,y,z))
 for j in range(N-1):
  for i in range(N-1):
   k=j*N+i;faces.append((k,k+1,k+1+N,k+N))
 mesh("W0_fractured_topography_EDITABLE",vs,faces,mat0,grp,"BASIN_SCULPTED_TOPOGRAPHY","W0")
def central_lobes(style,grp,mats):
 # Two non-mirrored sculptural inhabited landmass shells with generous gap.
 # Cross-sections individually vary in length, depth, slope, rotation; cavities remain external/open.
 for side in (-1,1):
  rings=[]
  for j,z in enumerate([200,700,1250,1850,2500,3150,3800,4200]):
   skew=(.22*side+(.18 if style=="B" else -.08))*z
   cx=side*(610+140*math.sin(j*.63+side)+(.035 if style=="C" else 0)*z)
   cy=110*math.sin(j*.62+side)+skew
   radius_x=(700-38*j)*(1+.13*math.sin(j*.9+side))
   radius_y=(560-30*j)*(1+.18*math.cos(.7*j+side))
   # Intentional 12-point irregular volumetric shape, not rectangular plates.
   ring=[]
   for k in range(12):
    a=2*PI*k/12+.21*j+side*.18
    wav=1+.12*math.sin(3*a+side+j*.32)+.05*math.sin(5*a-j)
    xx=cx+radius_x*wav*math.cos(a)
    yy=cy+radius_y*wav*math.sin(a)
    # large open fissure between the two principal shells
    if side==-1:xx=min(xx,-180-85*math.sin(j*.33))
    else:xx=max(xx,180+100*math.cos(j*.31))
    ring.append((xx,yy,z+70*math.sin(a*2+j*.5)))
   rings.append(ring)
  loft_sections("M247-C_"+("WEST" if side<0 else "EAST")+"_SCULPTABLE_SHELL",rings,mats["shell"] if side==-1 else mats["ivory"],grp,"M247-C_DOUBLE_SHELL_ART_STUDY","M247-C")
 # A different, 3D angled ascending spine anchored inside upper shell, not a vertical tower.
 points=[(-280,-70,800),(-250,220,1600),(-45,300,2750),(200,700,3700),(470,780,5050)]
 for k in range(len(points)-1):
  st=points[k];en=points[k+1]
  mid=tuple((st[i]+en[i])/2 for i in range(3))
  d=Vector(en)-Vector(st)
  ob=cuboid("M247-C_OBLIQUE_SPINE_"+str(k),mid,(310,370,d.length),mats["dark"],grp,"ASCENDING_SPINE","M247-C")
  ob.rotation_mode="QUATERNION";ob.rotation_quaternion=Vector((0,0,1)).rotation_difference(d)
 # Traversable dimensions not certified, but urban physical presence shown.
 for z in [680,1510,2390,3160]:
  track("M247-C_INHABITED_CIVIC_TRANSFER_"+str(z),
        [(-1150,-170,z),( -500,250,z+190),(260,370,z+320),(1200,640,z+480)],
        56,mats["glow"],grp,"THICK_3D_PUBLIC_TRANSFER_PROXY","M247-C")
def sky_cities(style,grp,mats,rng):
 poses=[(-2850,-1350,2300),(2250,-1350,2700),(-2300,1600,3550),(2900,1300,3200),(-650,3250,3950),(1200,-3200,4100)]
 for idx,(x,y,z) in enumerate(poses,1):
  asset="H"+str(idx)
  off=idx*.74
  # thick inhabited ground is sculptural 3D, not a paper shelf
  flower_ridge("D48_"+asset+"_INHABITED_URBAN_MASS",(x,y),520+idx*32,z,mats["ground"],grp,off,theta=off,thickness=160+idx*17)
  # Varied parcels and legible buildings, left as WIP rather than "detailed full city".
  for k in range(14):
   phi=k*2.399+idx
   r=165+70*(k%3)
   bx=x+r*math.cos(phi);by=y+r*.7*math.sin(phi)
   h=125+48*((k+idx)%4)
   cuboid(asset+"_urban_parcel_"+str(k),(bx,by,z+140+h/2),(60+15*(k%2),80,h),mats["civic"] if k%4 else mats["glass"],grp,"SKY_DISTRICT_GENERAL_FACADE_WIP",asset,rot=phi/3)
  track(asset+"_local_public_street",
        [(x-280,y-80,z+160),(x-130,y-70,z+195),(x+80,y+80,z+205),(x+280,y+140,z+175)],
        19,mats["glow"],grp,"DISTRICT_LOCAL_PUBLIC_STREET_PROXY",asset)
 # This is only VISUAL physical connection, NOT functional certified access
 for idx,(x,y,z) in enumerate(poses,1):
  track("H"+str(idx)+"_central_city_transfer_VISUAL_PROXY",
        [(x,y,z+50),(.72*x,.72*y,z+120),(.41*x,.40*y,2300+180*(idx%3)),(430 if x>0 else -410,300,2100)],
        25,mats["civic"],grp,"MOBILITY_ENVELOPE_UNVERIFIED","H"+str(idx))
def facilities(style,grp,mats):
 for i in range(1,17):
  ang=2*PI*(i/16)+.18
  rr=3850+((i*37)%4)*185
  x=rr*math.cos(ang)
  y=rr*math.sin(ang)*.80
  asset=f"SB{i:02d}"
  h=430+70*(i%5)
  if i==5:
   # Sail citadel: independent raked open crest forms
   for s in (-1,1):
    sections=[]
    for zz,rx,ry in [(100,220,310),(330,270,240),(730,110,130),(1140,45,60)]:
     cx=x+190*s+zz*.26*s;cy=y+zz*.13
     sections.append([(cx+rx*math.cos(t*PI/3),cy+ry*math.sin(t*PI/3),zz) for t in range(6)])
    loft_sections(asset+"_RADIANT_SAIL_"+str(s),sections,mats["ivory"],grp,"HERO4_SAIL_ART_STUDY",asset)
  elif i==8:
   for s in (-1,1):
    track(asset+"_TWIN_AURORA_VAULT_"+str(s),
          [(x+s*270,y-380,100),(x+s*370,y-130,750),(x+s*190,y+240,920),(x+s*180,y+400,120)],
          98,mats["shell"],grp,"HERO4_TWIN_VAULT_ART_STUDY",asset)
  elif i==9:
   for s in (-1,1):
    cuboid(asset+"_GATE_TOWER_"+str(s),(x+s*280,y,430),(160,230,850),mats["dark"],grp,"HERO4_GATE_FRAME_WIP",asset)
   track(asset+"_UPPER_GATE_WIP",[(x-270,y,875),(x,y,1040),(x+270,y,875)],80,mats["ivory"],grp,"HERO4_GATE_ART_STUDY_NOT_PROTECTED_ORIGINAL",asset)
  elif i==12:
   for j in range(4):
    flower_ridge(asset+"_SANCTUARY_CASCADE_"+str(j),(x+90*j,y-55*j),340-j*52,160+145*j,mats["stone"],grp,i+j,thickness=115)
  else:
   # 12 individually scaled WIP civic masses: not full megastructure interiors
   flower_ridge(asset+"_PUBLIC_MEGASTRUCTURE_PROXY",(x,y),210+(i%4)*36,100,mats["stone"] if i%3 else mats["civic"],grp,i*.75,thickness=h*.32)
   cuboid(asset+"_VERTICAL_LIFE_CORE",(x+65,y-40,h*.50+140),(145,125,h),mats["glass"],grp,"SB_PUBLIC_INTERIOR_WIP",asset,rot=ang/2)
def urban_ground(style,grp,mats):
 # Decorative metropolitan tissue remains deliberately WIP, not detailed city.
 for gx in range(-3500,3501,700):
  for gy in range(-2400,2401,650):
   if gx*gx+gy*gy<1600**2 or gx< -1800 and gy>1600:continue
   if gx>3000:continue
   z=90+40*math.sin(gx/550+gy/780)
   cuboid("W0_CITY_FABRIC_"+str(gx)+"_"+str(gy),
          (gx,gy,z+190),(220,170,360+110*math.sin((gx+gy)/930)),
          mats["civic"] if (gx+gy)%3 else mats["ivory"],grp,"GROUND_CITY_BLOCK_OUT_WIP","W0")
 # sea edge positive x. Literal broad blue water is W0 research geography.
 cuboid("W0_EAST_ARTIFICIAL_SEA",(5040,-100,25),(1820,9600,20),mats["sea"],grp,"EAST_INLAND_SEA_PROXY","W0")
def massing_variant(style,grp,mats):
 # A/B/C differ in the spatial syntax of central and district relationships.
 if style=="A":
  for j in range(6):
   z=400+j*360
   x=-1900+j*140;y=-500+j*80
   # Layered public geography: each layer a thick fractured sculpted city body
   flower_ridge("A_STRATIFIED_CIVIC_BASIN_"+str(j),(x,y),620+j*60,z,mats["stone"],grp,.4*j,thickness=140)
  for j in range(4):
   track("A_VERTICAL_CIVIC_CUT_"+str(j),[(-2300+j*430,-1000,300),(-1500+j*380,0,1200),(-520+j*250,700,2600)],48,mats["glow"],grp,"ART_CIVIC_SECTION_ROUTE_PROXY")
 elif style=="B":
  for j,s in enumerate((-1,1)):
   # 3D inhabitable transit tidal armatures are curved and merge into the central city.
   for k in range(3):
    z=280+k*510
    track("B_CIVIC_TIDAL_CONFLUENCE_"+str(j)+"_"+str(k),
          [(s*4600,-2900+k*850,180),(s*3400,-1900+k*660,z+350),
           (s*2000,-1200+k*600,z+680),(s*650,-100+k*420,z+1250),
           (s*230,400+k*120,z+1770)],70-8*k,
           mats["glow"] if k==1 else mats["stone"],grp,"INHABITED_AXIS_ART_FORM_NOT_FUNCTION_PROOF")
  for x,y in [(-2400,-2100),(2150,1750),(720,-3550)]:
   flower_ridge("B_PUBLIC_TRANSFER_BASIN_"+str(x),(x,y),380,320,mats["stone"],grp,x*.01,thickness=130)
 elif style=="C":
  for j,(x,y,z) in enumerate([(-1780,-350,2250),(1450,850,2850),(400,-1050,3500)]):
   flower_ridge("C_DISPLACED_REAL_CIVIC_MASS_"+str(j),(x,y),620+j*80,z,mats["stone"],grp,j*1.3,thickness=390)
   for q in range(8):
    phi=q*2.4
    cuboid("C_LIVING_STREET_FRAGMENT_"+str(j)+"_"+str(q),
           (x+240*math.cos(phi),y+160*math.sin(phi),z+420+80),
           (70,60,160),mats["civic"],grp,"INHABITED_DISPLACED_MASS_WIP")
   track("C_INTERNAL_REAL_PUBLIC_LINK_"+str(j),
         [(x-350,y,z+400),(x+150,y+60,z+440),(x+400,y+60,z+405)],27,mats["glow"],grp,"PUBLIC_LINK_PROXY")
def setup_camera(n,origin,target,lens,coll):
 cam=bpy.data.cameras.new(n+"_REAL_ORIGINAL_CAMERA")
 ob=bpy.data.objects.new(n,cam);coll.objects.link(ob)
 ob.location=origin
 ob.rotation_euler=(Vector(target)-ob.location).to_track_quat("-Z","Y").to_euler()
 cam.type="PERSP";cam.lens=lens
 return ob
def main(style):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 scene=bpy.context.scene
 scene.name="D48_R1_"+ART[style]["name"]+"_RESEARCH_NOT_ADOPTED"
 scene["D48_OFFICIAL_WORLD_COORDINATES_VERIFIED"]=False
 scene["D48_WORLD_WRITE"]=False
 scene["D48_ART_ADOPTED"]=False
 scene["D48_CITY_MASTER_COMPLETE"]=False
 scene["D48_MODEL_RELATIVE_H_TO_MINECRAFT_Y"]="UNKNOWN"
 scene["D48_FORMAL_SITE_COORDINATES"]="NULL_RESEARCH_LAYOUT_ONLY"
 groups={}
 for n in ["00_W0_ART_TERRAIN","01_CENTRAL_M247C","02_SKY_DISTRICT_H1_TO_H6","03_SPECIAL_SITES_SB01_TO_SB16","04_ART_CIVIC_FLOWS","05_URBAN_GROUND_WIP","99_CAMERAS"]:
  c=bpy.data.collections.new(n);scene.collection.children.link(c);groups[n]=c
 m={
 "shell":mat("D48_IRIDESCENT_CERAMIC",ART[style]["col"]),
 "ivory":mat("D48_WARM_IVORY",(.9,.87,.8,1)),
 "accent":mat("D48_COPPER_ACCENT",ART[style]["accent"]),
 "dark":mat("D48_DEEP_SHADOW",(.12,.19,.23,1)),
 "civic":mat("D48_PEARL_CIVIC",(.57,.66,.66,1)),
 "ground":mat("D48_INHABITED_STONE",(.39,.50,.49,1)),
 "glass":mat("D48_GLASS_PROXY",(.26,.53,.61,1)),
 "glow":mat("D48_CIVIC_LIGHT_PATH",ART[style]["accent"]),
 "sea":mat("D48_INLAND_SEA",(.18,.37,.48,1)),
 "stone":mat("D48_FRACTURED_STONE",(.48,.49,.44,1)),
 }
 ground_sculpt(m["ground"],groups["00_W0_ART_TERRAIN"],style)
 central_lobes(style,groups["01_CENTRAL_M247C"],m)
 sky_cities(style,groups["02_SKY_DISTRICT_H1_TO_H6"],m,random.Random(48))
 facilities(style,groups["03_SPECIAL_SITES_SB01_TO_SB16"],m)
 massing_variant(style,groups["04_ART_CIVIC_FLOWS"],m)
 urban_ground(style,groups["05_URBAN_GROUND_WIP"],m)
 for k,((origin,target,lens)) in VIEWS.items():
  setup_camera(k,origin,target,lens,groups["99_CAMERAS"])
 scene.render.engine="BLENDER_WORKBENCH"
 scene.display.shading.light="STUDIO"
 scene.display.shading.color_type="MATERIAL"
 scene.display.shading.show_shadows=True
 scene.display.shading.show_cavity=True
 scene.display.shading.cavity_type="BOTH"
 scene.display.shading.curvature_ridge_factor=1.2
 scene.display.shading.curvature_valley_factor=1.1
 scene.display.shading.background_type="WORLD"
 scene.world=bpy.data.worlds.new("D48_COOL_CITY_ATMOSPHERE")
 scene.world.color=(.18,.23,.28)
 scene.render.resolution_x=1200;scene.render.resolution_y=740
 scene.render.resolution_percentage=100
 scene.render.image_settings.file_format="PNG"
 scene.camera=bpy.data.objects["01_NORTH_PANORAMA"]
 scene.view_settings.view_transform="Standard"
 out=ROOT/style
 out.mkdir(parents=True,exist_ok=True)
 blend=out/("D48_R1_"+style+"_MACRO_CITY_EDITABLE.blend")
 glb=out/("D48_R1_"+style+"_MACRO_CITY_GEOMETRY.glb")
 bpy.ops.wm.save_as_mainfile(filepath=str(blend))
 bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",export_cameras=False,export_lights=False,export_apply=True)
 images=[]
 for name in VIEWS:
  scene.camera=bpy.data.objects[name]
  scene.render.filepath=str(out/(name+".png"))
  bpy.ops.render.render(write_still=True)
  images.append(name+".png")
 objects=[ob for ob in bpy.data.objects if ob.type in {"MESH","CURVE"}]
 ids={ob.get("D48_asset_id") for ob in objects if ob.get("D48_asset_id")}
 expected={"M247-C","W0"}|{f"H{i}" for i in range(1,7)}|{f"SB{i:02d}" for i in range(1,17)}
 assert expected.issubset(ids),sorted(expected-ids)
 info={"schema":"D48_R1_TRUE_BLENDER_RESEARCH","alternative":style,
       "art_direction":ART[style]["name"],"source_tech":"AWAIT_INDEPENDENT_REOPEN",
       "art":"UNREVIEWED","function":"UNCERTIFIED","formal_adoption":False,
       "official_coordinates":"UNVERIFIED_TEMP_ART_LAYOUT",
       "minecraft_write":False,"city_master_complete":False,
       "blender_editable":True,"camera_names":list(VIEWS),
       "registered_real_object_ids":sorted(ids),
       "real_object_count":len(objects),"blender_objects":len(bpy.data.objects),
       "mesh_count":len([ob for ob in objects if ob.type=="MESH"]),
       "curve_count":len([ob for ob in objects if ob.type=="CURVE"]),
       "files":{"blend":blend.name,"glb":glb.name,"images":images},
       "sha256":{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [blend,glb]+[out/p for p in images]}}
 (out/"D48_R1_MANIFEST.json").write_text(json.dumps(info,indent=2,ensure_ascii=False))
 print("D48_R1_NATIVE_MACRO_"+style+"_CREATED",len(objects),flush=True)
for key in ("A","B","C"):
 main(key)
print("D48_R1_ALL_THREE_REAL_BLENDER_SCENES_CREATED",flush=True)
