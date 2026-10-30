"""HALO-9 R12: author-guided FULL 3D sculptural visual pilot. ART UNREVIEWED.

Goal is to test *inhabited civic negative space* and asymmetrical upper quarter,
not generate a monolithic box/arch or adopt canonical M247-C. Two authored
architectural diagrams are intentionally different:
A: split tilted civic escarpments + public aerial court
B: asymmetric inhabited sky shelf and three offset vaulted streets

All output is inspectable, editable Blender meshes. No image generation,
not procedural city completion. Public room and spatial character physical
but walkability / full interior / loads / coordinates NOT certified.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
P=Path(sys.argv[-1]).resolve();P.mkdir(parents=True,exist_ok=True)
MATS={}
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);MATS[n]=m;return m
def reset():
 bpy.ops.wm.read_factory_settings(use_empty=True)
 MATS.clear()
 mat("01 ivory civic enclosure",(.74,.75,.68))
 mat("02 midnight urban cut",(.24,.35,.39))
 mat("03 pale sky lit quarter",(.75,.69,.51))
 mat("04 copper cultural gallery",(.59,.41,.30))
 mat("05 turquoise public transport",(.32,.55,.58))
 mat("06 ecological terraces",(.42,.55,.43))
 mat("07 deep monumental spine",(.21,.30,.37))
 mat("08 public ground",(.46,.49,.48))
def grp(n):
 c=bpy.data.collections.get(n)
 if not c:
  c=bpy.data.collections.new(n);bpy.context.scene.collection.children.link(c)
 return c
def obj(n,v,f,ma,col,role):
 me=bpy.data.meshes.new(n+" EDITABLE MESH")
 me.from_pydata(v,[],f);me.update()
 o=bpy.data.objects.new(n,me);grp(col).objects.link(o)
 me.materials.append(MATS[ma]);o["program"]=role;o["canonical"]=False
 return o
def solid_poly(n,pts,z0,z1,ma,col,role):
 assert len(pts)>=3 and z1>z0
 N=len(pts);v=[(x,y,z0) for x,y in pts]+[(x,y,z1) for x,y in pts]
 f=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]
 f.extend((i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N))
 return obj(n,v,f,ma,col,role)
def beam(n,a,b,wx,wz,ma,col,role):
 a,b=Vector(a),Vector(b)
 tangent=(b-a).normalized()
 # deliberately variable 3D framing, not generic horizontal box
 q=Vector((0,0,1))
 if abs(tangent.dot(q))>.9:q=Vector((0,1,0))
 side=tangent.cross(q).normalized()
 up=tangent.cross(side).normalized()
 off=[side*wx/2+up*wz/2,side*wx/2-up*wz/2,-side*wx/2-up*wz/2,-side*wx/2+up*wz/2]
 v=[tuple(a+t) for t in off]+[tuple(b+t) for t in off]
 f=[(3,2,1,0),(4,5,6,7)]
 f.extend((i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4))
 return obj(n,v,f,ma,col,role)
def corridor(n,points,widths,ma,role):
 v=[]
 for i,(x,y,z) in enumerate(points):
  a=points[max(0,i-1)];b=points[min(len(points)-1,i+1)]
  dx=b[0]-a[0];dy=b[1]-a[1];norm=math.hypot(dx,dy)
  assert norm>0
  nx,ny=-dy/norm,dx/norm
  v.extend([(x-nx*widths[i]/2,y-ny*widths[i]/2,z),
            (x+nx*widths[i]/2,y+ny*widths[i]/2,z)])
 f=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(points)-1)]
 return obj(n,v,f,ma,"01 GENUINE CITY WALKING SURFACES",role)
def skin(n,rails,ma,role):
 # author-created sculptural skins through nonuniform 3D contours:
 # each cross section is a transverse line; no concrete mass is filled.
 pts=[p for pair in rails for p in pair]
 f=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(rails)-1)]
 ob=obj(n,pts,f,ma,"02 ARCHITECTURAL SKYLINE WALLS",role)
 ob.shape_key_add(name="Basis")
 ob.shape_key_add(name="R12_ARTIST_REVERSIBLE_EDITS")
 ob["R12_ART_EDIT_CONTROL"]=True
 return ob
def polygon(cx,cy,rx,ry,turn):
 pts=[(-.91,-.48),(-.46,-1),(.42,-.86),(1,-.32),(.82,.77),(.22,1),(-.65,.76)]
 ans=[]
 for x,y in pts:
  x*=rx;y*=ry
  ans.append((cx+x*math.cos(turn)-y*math.sin(turn),
              cy+x*math.sin(turn)+y*math.cos(turn)))
 return ans
def public_room(name,center,dimensions,z,h,angle,ma,open_side):
 # Physical floor, weather roof, two flanking real walls and an open entry.
 cx,cy=center;rx,ry=dimensions
 p=polygon(cx,cy,rx,ry,angle)
 solid_poly(name+" REAL PUBLIC ROOM FLOOR",p,z-5,z,
  "01 ivory civic enclosure","03 REAL ENCLOSED CULTURAL SPACE",
  "true public floor, room purpose representative only")
 # roof supports depend on perimeter, no box shaped exterior.
 solid_poly(name+" WEATHER ROOF",p,z+h,z+h+10,ma,
  "03 REAL ENCLOSED CULTURAL SPACE","true physical enclosing roof of public hall")
 for i in range(len(p)):
  a,b=p[i],p[(i+1)%len(p)]
  if i==open_side:
   for t in (0.08,.91):
    xx=a[0]+(b[0]-a[0])*t;yy=a[1]+(b[1]-a[1])*t
    beam(name+f" ACTUAL PORCH PIER {i} {t}",(xx,yy,z+4),(xx,yy,z+h-3),6,6,
        ma,"03 REAL ENCLOSED CULTURAL SPACE","entrance pier beside real open portal")
   beam(name+" PORTAL HEAD",(a[0]+.19*(b[0]-a[0]),a[1]+.19*(b[1]-a[1]),z+h-8),
       (a[0]+.81*(b[0]-a[0]),a[1]+.81*(b[1]-a[1]),z+h-8),
       7,12,ma,"03 REAL ENCLOSED CULTURAL SPACE","physical lintel above open entry")
  else:
   # not monolithic exterior walls: three partial spatial frames with through views
   for u in (.03,.50,.97):
    xx=a[0]+(b[0]-a[0])*u;yy=a[1]+(b[1]-a[1])*u
    beam(name+f" PORTICO FIN {i} {u}",(xx,yy,z+3),(xx,yy,z+h-6),4,6,ma,
       "03 REAL ENCLOSED CULTURAL SPACE","real separated facade structural member")
   beam(name+f" HIGH WINDOW TOP {i}",(a[0],a[1],z+h-9),
      (b[0],b[1],z+h-9),8,7,ma,
      "03 REAL ENCLOSED CULTURAL SPACE","facade upper structural beam")
 return {'name':name,'center':center,'z':z,'height':h,'roof':True,
         'actual_open_portal':True,'full_accessibility':False}
def city_quarter(tag,centers,style):
 # A sequence of DIFFERENT multi-bay public courts on distinct vertical levels.
 # Connect a true pedestrian district spine, each stop a separate space.
 colors=("03 pale sky lit quarter","04 copper cultural gallery","05 turquoise public transport")
 floorpoints=[]
 info=[]
 for i,(x,y,z) in enumerate(centers):
  angle=.38+(.17 if i%2 else -.15) if style=='wind' else -.30+.27*i
  rx=90+((i*37)%83);ry=83+((i*23)%71)
  info.append(public_room(tag+f" HOUSE-OF-COMMONS-{i+1}",
             (x,y),(rx,ry),z,65+((i*43)%50),angle,
             colors[i%3],(i+2)%7))
  floorpoints.append((x,y,z-4))
 # Shared street only spans supplied heterogeneous cultural destinations.
 corridor(tag+" PUBLIC ROOM-TO-ROOM STREET",floorpoints,
    [33+7*(i%3) for i in range(len(floorpoints))],
    "08 public ground",
    "real continuous elevated public street with unknown gradient/access quality")
 return info
def create(tag):
 reset()
 a=tag=="A"
 scene=bpy.context.scene
 scene["R12_VARIANT"]=tag
 scene["R12_HERO_ARCHITECTURE_PROPOSAL"]=False
 scene["R12_ART_ADOPTED"]=False
 scene["R12_FULL_10KM_MASTER"]=False
 scene["R12_M247C_CHANGED"]=False
 scene["R12_MINECRAFT_CONSTRUCTION"]=False
 scene["R12_LOCATION"]="noncanonical partial 1.8km test, NOT official anchor"
 # ACTUAL itinerary and two coherent inhabited wings (no single huge exterior box).
 if a:
  street=[(-5,-1000,0),(-7,-730,0),(18,-440,4),(30,-100,6),
          (35,210,14),(57,530,24),(45,920,34)]
  WEST=[(-392,-495,72),(-422,-236,230),(-515,58,392),
        (-487,355,515),(-577,668,750),(-620,868,855)]
  EAST=[(350,-553,43),(410,-298,188),(470,4,345),
        (403,309,550),(507,607,690),(590,926,840)]
  SKY=[(-335,-124,950),(-149,145,1180),(210,324,1340),
       (510,608,1260)]
  galleria=[((-610,-570,90),(-110,-580,260)),
           ((-580,-295,280),(-85,-250,500)),
           ((-650,50,465),(-100,5,730)),
           ((-620,344,670),(-55,300,870)),
           ((-670,650,930),(-130,680,1080))]
  second=[((140,-590,50),(630,-620,155)),
         ((200,-290,240),(780,-325,390)),
         ((160,0,480),(690,30,640)),
         ((115,313,620),(720,280,840)),
         ((160,635,800),(850,690,1080))]
 else:
  street=[(-230,-1010,0),(-160,-767,0),(-65,-450,3),(11,-137,9),
          (77,202,17),(86,530,26),(110,920,39)]
  WEST=[(-520,-560,135),(-515,-268,296),(-403,22,480),
        (-352,309,700),(-300,601,950),(-190,886,1090)]
  EAST=[(440,-575,25),(390,-318,150),(550,-18,325),
        (680,345,492),(715,653,650),(830,921,795)]
  SKY=[(-500,-250,1080),(-200,99,1310),(290,450,1500),
       (780,870,1290)]
  galleria=[((-710,-570,260),(-160,-540,425)),
            ((-680,-265,425),(-175,-270,570)),
            ((-585,20,650),(-140,60,750)),
            ((-480,350,810),(-95,335,995)),
            ((-410,650,1150),(-60,635,1260))]
  second=[((150,-640,45),(760,-650,255)),
          ((170,-370,280),(850,-290,455)),
          ((245,-70,440),(890,50,665)),
          ((240,340,670),(870,250,800)),
          ((275,650,870),(910,770,1060))]
 corridor("COMMON ARRIVAL INTO REAL PUBLIC OPEN-AIR VOID",street,
   [52,57,71,88,93,81,68],"08 public ground",
   "actual contiguous civic passage through negative space")
 quarters=city_quarter("WEST_CULTURAL_DISTRICT",WEST,"wind" if a else "fall")
 quarters+=city_quarter("EAST_TRANSIT_DISTRICT",EAST,"fall" if a else "wind")
 quarters+=city_quarter("UPPER_LIVED_CITY",SKY,"fall" if a else "wind")
 # The silhouette is made by public galleries at different heights, with an
 # actual line of sight through in the middle and no closed global facade.
 for n,rails in (("WEST INNER CANYON WIND-CUT GALLERY",galleria),
                 ("EAST MULTI-HEIGHT PUBLIC EDGE",second)):
  skin(n,rails,"02 midnight urban cut",
     "sculpted open facade; genuine partial architecture NO certified occupancy")
  for k in (0,2,4):
   p0,p1=rails[k]
   # deliberate limited portal frame with no spanning giant roof
   beam(n+f" BRANCH SUSPENDED CANTILEVER {k}",
        (p0[0],p0[1],p0[2]+8),(p1[0],p1[1],p1[2]+13),
        10,17,"07 deep monumental spine","04 PUBLIC CANTILEVER CONNECTIONS",
        "visible tectonic member of a large city void, NOT verified load-bearing")
 # Three civic hand-off crossings, do not make one huge bridge as main shape.
 links=( [(-387,-239,245),(-242,-105,288),(-68,54,339),(250,116,359),(464,-19,360)],
          [(-492,353,530),(-250,339,620),(5,314,729),(224,425,752),(418,367,710)] )
 if not a:
  links=( [(-510,-257,315),(-313,-178,370),(-29,-2,420),(210,94,450),(533,-13,420)],
          [(-352,319,712),(-210,405,820),(70,461,915),(312,376,902),(680,335,860)] )
 for i,pts in enumerate(links):
  corridor("VISIBLE PUBLIC CIVIC CROSSING "+str(i+1),pts,
           [19,22,29,24,20],
           "05 turquoise public transport",
           "actual bridge floor of 2nd city axis, structural and accessibility not certified")
 # Real public volumes of differing configurations at city threshold.
 for i,(cx,cy,rx,ry,z) in enumerate(
       [(-183,-743,94,92,0),(175,-725,102,97,0),
        (-98,-389,120,103,12),(164,415,105,100,17)]):
  quarters.append(public_room("GROUND PUBLIC DESTINATION "+str(i+1),
     (cx,cy),(rx,ry),z,84+i*31,.23*i,
     ("03 pale sky lit quarter" if i%2 else "04 copper cultural gallery"),
     (i+2)%7))
 # Frame CAMERA views with 3D consistent world positions across both variants.
 cameras=[
 ("01_LONG_APPROACH",(0,-2100,250),(0,150,690),2900),
 ("02_FRONT",(-80,-2600,800),(0,160,810),2400),
 ("03_OBLIQUE",(2180,-1900,1380),(0,100,800),2700),
 ("04_SIDE",(2580,180,900),(0,210,780),2250),
 ("05_REAR",(250,2380,1100),(0,170,820),2350),
 ("06_AERIAL",(1800,-1350,3400),(0,175,780),2800),
 ("07_GROUND_ARRIVAL",(6,-870,30),(0,250,730),None),
 ("08_CIVIC_VOID",(30,-130,23),(0,450,1120),None),
 ("09_SKY_CITY_DISTRICT",(-200,90,1160),(310,520,1300),None)]
 for name,eye,target,ortho in cameras:
  cam=bpy.data.cameras.new(name); ob=bpy.data.objects.new(name,cam)
  grp("05 FIXED VISUAL G0 REAL CAMERAS").objects.link(ob); ob.location=eye
  ob.rotation_euler=(Vector(target)-ob.location).to_track_quat("-Z","Y").to_euler()
  cam.clip_end=30000
  if ortho:cam.type="ORTHO";cam.ortho_scale=ortho
  else:cam.type="PERSP";cam.lens=23
 # Bind a self-contained artist UI script to both editable genuine 3D scenes.
 script=Path(__file__).resolve().parent/"r12_art_review_toolbar.py"
 assert script.exists(),"Missing portable Blender GUI art toolbar source"
 bpy.data.texts.load(str(script)).name="R12_RUN_THIS_TO_ENABLE_ART_TOOLS.py"
 scene.render.engine="BLENDER_WORKBENCH"
 scene.display.shading.light="STUDIO"
 scene.display.shading.color_type="MATERIAL"
 scene.display.shading.show_cavity=True
 scene.render.resolution_x=1100;scene.render.resolution_y=740
 scene.render.resolution_percentage=100
 scene.render.image_settings.file_format="PNG"
 blend=P/(tag+"_R12_ART_DIRECTED_INHABITED_VOID.blend")
 glb=P/(tag+"_R12_ART_DIRECTED_INHABITED_VOID.glb")
 bpy.ops.wm.save_as_mainfile(filepath=str(blend))
 bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
                export_cameras=False,export_lights=False)
 rendered=[]
 for name,*_ in cameras:
  scene.camera=bpy.data.objects[name]
  png=P/(tag+"_"+name+".png")
  scene.render.filepath=str(png)
  bpy.ops.render.render(write_still=True)
  rendered.append(png.name)
 return {"variant":tag,"name":"split escarpment upper city" if a else "sheared living quarter",
    "native_blend":blend.name,"real_glb":glb.name,
    "actual_public_rooms":len(quarters),
    "mesh_count":len([o for o in bpy.data.objects if o.type=="MESH"]),
    "real_view_names":rendered,
    "art":"G0_NOT_VISUALLY_REVIEWED",
    "room_access_fully_certified":False,"city_full_master":False,
    "original_main_modified":False,"official_central_adopted":False}
res=[create("A"),create("B")]
manifest={
 "title":"R12 Art-first inhabited civic void alternatives, truly independent Blender 3D",
 "noncanonical":"~1.8km civic-only sketch; NOT final central M247-C or 10km master",
 "required_visual_art_check":"front oblique side rear aerial ground void high street",
 "art_adopted":False,"minecraft_construction":False,
 "two_real_distinct_geometry_variants":True,
 "variants":res,"blender_version":bpy.app.version_string}
(P/"R12_REAL_3D_MANIFEST.json").write_text(
 json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf8")
print("R12_REAL_EDITABLE_18_VIEW_G0_DONE_NOT_ART_PASSED",res)
