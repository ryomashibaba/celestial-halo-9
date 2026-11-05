"""HALO-9 R4-E6: completely new, non-adopted integrated inhabited-fault research artwork.
Blender 3.5+/4+/5+; no dependency on prior R0B scene. Isolated output only.

This is a deliberately architected study, not the certified 10km CITY MASTER.
Avoids an exterior shell imposed before public-space program: the two civic
flanks are articulated around a central inhabitable rift, with H1, W0 and
transit sharing the same research metre frame.
"""
import bpy
import math
import random
import json
import sys
import hashlib
from pathlib import Path
from mathutils import Vector

random.seed(2476)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[args.index('--output')+1]).resolve() if '--output' in args else Path('/tmp/halo9_r4_e6')
out.mkdir(parents=True,exist_ok=True)
(out/'renders').mkdir(exist_ok=True)
# Explicitly create a new data-block universe, never open or edit E2/E4/E5/R0B.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene['study']='HALO9_R4_E6_INHABITED_FAULT_SEPARATE_CANDIDATE'
scene['formal_art_adoption']=False
scene['minecraft_write']='FORBIDDEN'
scene['official_coordinates_verified']=False
scene['completed_targets']=0
scene['required_targets']=30
scene['source_R0B_geometry_imported']=False
scene.render.engine='CYCLES'
scene.cycles.samples=12
scene.cycles.use_denoising=False
scene.render.resolution_x=960
scene.render.resolution_y=640
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.render.threads_mode='FIXED'
scene.render.threads=2
scene.view_settings.view_transform='Standard'
try: scene.view_settings.look='Medium High Contrast'
except Exception: pass
scene.view_settings.exposure=0.2
scene.camera=None
world=bpy.data.worlds.new('Overcast bright monumental atmosphere')
world.use_nodes=True
bpy.context.scene.world=world
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.32,0.45,0.54,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.8

def coll(name):
    c=bpy.data.collections.new(name);scene.collection.children.link(c);return c
C={n:coll(n) for n in [
    'W0_BASIN_MACRO_NOT_CERTIFIED','M247_C_CIVIC_FAULT','NAVE_MULTILEVEL_CIVIC_ROOM',
    'H1_DENSE_INHABITED_SECTION','INTERDISTRICT_PUBLIC_TRANSIT','HUMAN_SCALE_PUBLIC_LIFE',
    'VIEW_CAMERAS','30_TARGET_REGISTRY_RESEARCH_ONLY']}

def mat(name,rgb,metallic=0,rough=0.55,emission=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*rgb,1)
    bs.inputs['Metallic'].default_value=metallic
    bs.inputs['Roughness'].default_value=rough
    if emission:
        bs.inputs['Emission Color'].default_value=(*rgb,1)
        bs.inputs['Emission Strength'].default_value=emission
    return m
MAT={
  'basalt':mat('01 Blue-black ceremonial basalt',(0.052,0.074,0.101),0.20),
  'spine':mat('02 Graphite metallic tectonic core',(0.11,0.16,0.19),0.65,0.40),
  'chalk':mat('03 Milled off-white civic stone',(0.68,0.77,0.77),0.22,0.57),
  'pearl':mat('04 Warm pearl inhabited ridges',(0.56,0.65,0.66),0.38,0.38),
  'titanium':mat('05 Neutral silver alloy',(0.37,0.51,0.55),0.73,0.33),
  'bronze':mat('06 Aged champagne bronze',(0.46,0.32,0.17),0.72,0.33),
  'glass':mat('07 Deep blue glazing',(0.055,0.18,0.26),0.42,0.14),
  'light':mat('08 Cyan civic luminance',(0.08,0.66,0.82),0.15,0.20,1.15),
  'water':mat('09 Artificial sea calm',(0.035,0.25,0.34),0.68,0.18),
  'vegetation':mat('10 Evergreen sky garden',(0.085,0.17,0.13),0.0,0.76),
  'terrain':mat('11 Weathered fractured granite',(0.23,0.26,0.29),0.05,0.9),
  'ground':mat('12 Civic warm pavement',(0.37,0.38,0.35),0.05,0.85),
}

def mesh(name,vs,fs,material,cname):
    data=bpy.data.meshes.new(name);data.from_pydata(vs,[],fs);data.update()
    ob=bpy.data.objects.new(name,data);C[cname].objects.link(ob)
    ob.data.materials.append(MAT[material])
    return ob

def prism(name,poly,z0,z1,material,cname):
    n=len(poly);vs=[(x,y,z0) for x,y in poly]+[(x,y,z1) for x,y in poly]
    fs=[tuple(reversed(tuple(range(n)))),tuple(range(n,2*n))]
    for k in range(n):fs.append((k,(k+1)%n,(k+1)%n+n,k+n))
    return mesh(name,vs,fs,material,cname)

def loft(name,basepoly,sections,material,cname):
    """Art-directed, asymmetric vertical fabric, not repeated ring/tube sections."""
    count=len(basepoly);vs=[]
    for z,xoff,yoff,sx,sy,angle in sections:
        co=math.cos(angle);si=math.sin(angle)
        for x,y in basepoly:
            xx=x*sx;yy=y*sy
            vs.append((xx*co-yy*si+xoff,xx*si+yy*co+yoff,z))
    fs=[tuple(reversed(tuple(range(count)))),tuple(range((len(sections)-1)*count,len(sections)*count))]
    for j in range(len(sections)-1):
        for k in range(count):
            a=j*count+k;b=j*count+(k+1)%count
            fs.append((a,b,b+count,a+count))
    return mesh(name,vs,fs,material,cname)

def block(name,x,y,z,sx,sy,sz,material,cname,ang=0):
    ob=prism(name,[(-sx/2,-sy/2),(sx/2,-sy/2),(sx/2,sy/2),(-sx/2,sy/2)],-sz/2,sz/2,material,cname)
    ob.location=(x,y,z);ob.rotation_euler[2]=ang;return ob

def route(name,points,width=18,thick=5,material='pearl',cname='INTERDISTRICT_PUBLIC_TRANSIT'):
    """Wayfinding ribbon with true extruded walkable footprint, not thin line."""
    vs=[]
    for i,p in enumerate(points):
        tangent=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])
        tangent.z=0
        tangent.normalize() if tangent.length>0 else None
        nx,ny=-tangent.y,tangent.x
        for dz in [0,-thick]:
            for s in [-1,1]:vs.append((p[0]+nx*width/2*s,p[1]+ny*width/2*s,p[2]+dz))
    fs=[]
    for i in range(len(points)-1):
        a=i*4;b=(i+1)*4
        fs += [(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),(a,b,a+2,a+2) if False else (a,b,b+2,a+2),(a+1,a+3,b+3,b+1)]
    fs +=[(0,2,3,1),tuple(reversed(tuple(range((len(points)-1)*4,len(points)*4))))]
    return mesh(name,vs,fs,material,cname)

def stair(name,a,b,width=16,steps=16,material='chalk'):
    pts=[]
    for j in range(steps+1):
        t=j/steps
        pts.append((a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t))
    return route(name,pts,width,3,material,'INTERDISTRICT_PUBLIC_TRANSIT')

# W0: sculptural fractured 10 km-wide context. Research coordinates only.
verts=[]; faces=[]; N=60
for j in range(N+1):
    y=-5000+j*10000/N
    for i in range(N+1):
        x=-5000+i*10000/N
        north=1400*math.exp(-((y-3750)/1580)**2)*(0.6+0.4*math.cos(x/1700)**2)
        west=740/(1+math.exp((x+3300)/170))
        sw=-570*math.exp(-((x+2700)/1200)**2-((y+2950)/1400)**2)
        basin=-210*math.exp(-((x-1100)/1900)**2-((y+300)/2500)**2)
        fractures=42*math.sin(x/310+y/400)+26*math.cos(x/160-y/420)
        z=40+north+west+sw+basin+fractures
        verts.append((x,y,z))
for j in range(N):
    for i in range(N):
        a=j*(N+1)+i;faces.append((a,a+1,a+N+2,a+N+1))
mesh('W0_rough_terrain_unapproved_research_frame',verts,faces,'terrain','W0_BASIN_MACRO_NOT_CERTIFIED')
block('EAST_ARTIFICIAL_SEA_broad_void',2820,0,-112,4300,8200,8,'water','W0_BASIN_MACRO_NOT_CERTIFIED')

# -----------------------------------------------------------------------------
# CENTRAL: paired, severely sheared lithic civic shoulders. The unfilled rift is
# the architectural centerpiece. Individual facets articulate occupied terraces
# around it; there is no closed generic outer shell and no transplanted R0B mesh.
# -----------------------------------------------------------------------------
profiles=[
 ('WEST_A',(-670,30),[(150,-670,40,1.0,1.0,-.17),(460,-625,75,.98,.94,.01),(870,-645,40,.86,.83,-.12),(1240,-470,100,.72,.68,.17),(1730,-300,120,.46,.54,.41)]),
 ('WEST_B',(-430,330),[(80,-440,400,1,.95,.09),(470,-475,360,.8,1.08,-.11),(980,-435,480,.78,.76,.13),(1390,-350,360,.45,.7,.3)]),
 ('EAST_A',(645,-40),[(130,670,-120,1,1,.16),(510,630,-160,.87,.98,.08),(970,515,-50,.79,.75,-.07),(1420,420,120,.72,.62,-.32),(1820,350,165,.40,.32,-.51)]),
 ('EAST_B',(370,370),[(140,390,450,1,.95,-.1),(490,470,400,.92,.9,.14),(1000,415,490,.74,.7,.36),(1450,320,500,.46,.6,.48)]),
]
nonagon=[(-185,-110),(-85,-175),(110,-160),(205,-60),(170,130),(30,190),(-105,155),(-205,25)]
for label,center,sects in profiles:
    loft(f'M247_{label}_rift_wall_not_outer_shell',nonagon,sects,'basalt','M247_C_CIVIC_FAULT')
    # Inhabited overhangs are thick occupation wedges; separated above central void.
    for tier,z in enumerate((390,715,1050)):
        if z>sects[-1][0]-150:continue
        x=center[0]+(-30 if label.startswith('WEST') else 35)+math.sin(tier*1.4)*65
        y=center[1]+(-10 if tier%2 else -110)
        p=[(-125,-68),(-50,-113),(100,-82),(157,-8),(96,82),(-80,120),(-150,16)]
        sec=[(z-58,x,y,1.18,1.15,.18*tier),(z+20,x+14,y+12,.94,.9,.10*tier)]
        loft(f'{label}_occupied_fault_ledge_{tier}',p,sec,'pearl','M247_C_CIVIC_FAULT')
        # Not a flat residential row: vertical basins/courtyard apertures remain legible.
        for n in range(4):
            px=x+55*math.cos(n*1.8+tier)
            py=y+42*math.sin(n*1.9+tier)
            psmall=[(-19,-10),(4,-22),(24,-6),(16,21),(-12,26),(-25,6)]
            h=35+15*((n+tier)%3)
            loft(f'{label}_ledge_tier{tier}_inhabited_volume{n}',psmall,[(z+22,px,py,1.0,1.0,.2*n),(z+22+h,px+6,py+2,.69,.85,.1*n)],'chalk','M247_C_CIVIC_FAULT')

# Beta: asymmetric tilted broken civic ascent, not a lone black blade.
# Three separated inhabited solid segments across the rift skyline.
beta=[
 [(1050,-130,150,1.0,.85,-.20),(1500,-15,200,.86,.82,-.05),(2150,150,245,.64,.65,.18),(2500,250,285,.35,.40,.32)],
 [(720,360,310,.78,.85,.12),(1230,265,310,.85,.74,-.10),(1690,130,360,.55,.58,-.26)],
]
beta_poly=[(-190,-100),(-70,-165),(130,-100),(205,20),(100,120),(-105,105)]
for n,sects in enumerate(beta):loft(f'BETA_INHABITED_RIFT_ASCENT_{n}',beta_poly,sects,'spine','M247_C_CIVIC_FAULT')

# NAVE PUBLIC SPACE: civic ground and three asymmetrical, usable banks in a
# several-hundred-metre-wide canyon (not an empty planar box beneath roof beams).
prism('NAVE_CIVIC_GROUND_COURT',[(-290,-480),(240,-475),(345,-250),(220,70),(-330,110)],146,164,'ground','NAVE_MULTILEVEL_CIVIC_ROOM')
# A clear spatial program per tier, alternating along canyon flanks.
platforms=[
 ('SOUTH_LIBRARY', [(-335,-330),(-110,-345),(-80,-210),(-330,-185)],242,'pearl'),
 ('WEST_ASSEMBLY', [(-350,-120),(-170,-95),(-160,88),(-340,100)],358,'chalk'),
 ('EAST_EXHIBITION',[(130,-295),(370,-245),(325,-70),(120,-90)],315,'pearl'),
 ('NORTH_BATH_OF_LIGHT',[(-115,50),(90,42),(155,215),(-100,240)],474,'pearl'),
]
for name,foot,z,mm in platforms:
    prism('NAVE_'+name+'_PUBLIC_FLOOR',foot,z-30,z+2,mm,'NAVE_MULTILEVEL_CIVIC_ROOM')
    # Articulated public stalls facing the open atrium, interrupted for pedestrian flow.
    xs=[p[0] for p in foot];ys=[p[1] for p in foot]
    cx=sum(xs)/len(xs);cy=sum(ys)/len(ys)
    for k in range(3):
        dx=(k-1)*43
        p=[(-24,-12),(15,-22),(30,-3),(22,22),(-23,16)]
        loft(f'NAVE_{name}_INHABITED_ATRIUM_{k}',p,[(z+2,cx+dx,cy,1,.85,-.1),(z+57,cx+dx+12,cy+7,.76,.86,.1)],'glass','NAVE_MULTILEVEL_CIVIC_ROOM')
        block(f'NAVE_{name}_LIGHT_CUT_{k}',cx+dx,cy-23,z+27,18,3,45,'light','NAVE_MULTILEVEL_CIVIC_ROOM')
# Three distinct elevated public crossings with different curvature/elevation.
route('NAVE_STREET_TO_LIBRARY',[(-90,-470,164),(-115,-408,188),(-155,-340,242)],21,7,'chalk')
route('NAVE_LIBRARY_TO_ASSEMBLY',[(-170,-285,244),(-200,-220,290),(-230,-130,358)],23,8,'pearl')
route('NAVE_TO_EAST_GALLERY',[(-200,-70,360),(-120,-55,356),(-5,-85,342),(125,-140,315)],26,9,'titanium')
route('NAVE_NORTH_LIGHT_CROSSING',[(-175,83,358),(-65,122,407),(40,130,475)],19,7,'chalk')
# Slender irregular pleated clerestory fins emphasize daylight, secondary not dominant.
for i in range(8):
    y=-360+i*76
    a=-330+23*math.sin(i)
    p=[(-16,-10),(22,-12),(32,4),(10,15),(-27,9)]
    loft(f'NAVE_ATRIUM_DAYLIGHT_FIN_{i}',p,[(210,a,y,1,1,0),(660+i*21,a+15,y+8,.50,.72,.18)],'titanium','NAVE_MULTILEVEL_CIVIC_ROOM')

# H1: a true thick inhabited city section at high altitude. Streets wind between
# buildings with staggered atria and several urban levels, not aligned small houses.
h1foot=[(-1365,-580),(-900,-680),(-605,-350),(-635,115),(-1120,245),(-1450,-40)]
prism('H1_CARVED_MAIN_OCCUPIED_STRATUM',h1foot,666,814,'spine','H1_DENSE_INHABITED_SECTION')
# Three multi-layer elevated inhabited districts with connective urban streets.
for index,(poly,z,matkey) in enumerate([
 ([(-1420,-560),(-1160,-640),(-895,-480),(-940,-185),(-1230,-115)],818,'chalk'),
 ([(-1290,-90),(-950,-155),(-720,150),(-890,360),(-1220,270)],885,'pearl'),
 ([(-1075,-650),(-730,-520),(-565,-260),(-690,-120),(-1060,-245)],978,'pearl')]):
    prism(f'H1_PUBLIC_WARD_{index}_STRUCTURAL_DEPTH',poly,z-42,z+4,matkey,'H1_DENSE_INHABITED_SECTION')
# Real occupied envelopes are irregular vertically stepped massing: civic school,
# housing, market, health/communal services, with pedestrian gaps between.
bldgs=[
 ('H1_LEARNING_CITADEL',-1210,-400,827,105,120,260),
 ('H1_MARKET_CONSERVATORY',-1020,-480,830,145,125,165),
 ('H1_HOSPITAL_PORCH',-800,-305,832,96,118,220),
 ('H1_CIVIC_ARCHIVE',-1170,68,899,130,107,260),
 ('H1_COMMUNAL_BATH',-996,182,904,103,85,155),
 ('H1_HOUSING_NORTH',-815,145,910,100,100,235),
 ('H1_HOUSING_UPPER',-810,-380,992,90,145,265),
 ('H1_RESIDENTIAL_GARDEN',-1000,-445,995,115,100,160),
]
poly=[(-.5,-.31),(-.12,-.55),(.45,-.43),(.54,.15),(.13,.55),(-.37,.49),(-.54,.13)]
for j,(name,x,y,z,w,d,h) in enumerate(bldgs):
    ps=[(a*w,b*d) for a,b in poly]
    sect=[(z,x,y,1.0,1.0,-.13+j*.05),(z+h*.32,x+12,y+4,.95,.89,.02+j*.06),
          (z+h*.7,x-12,y+9,.83,.75,.12+j*.05),(z+h,x+18,y-3,.68,.64,.16+j*.06)]
    loft(name+'_SCULPTED_ENVELOPE',ps,sect,'chalk' if j%3==0 else 'pearl','H1_DENSE_INHABITED_SECTION')
    # Public terrace hung between structural occupied levels (not fake windows).
    loft(name+'_PUBLIC_WEDGE',ps,[(z+h*.33,x+11,y,.88,.82,.05),(z+h*.33+14,x+11,y,.84,.81,.08)],'bronze','H1_DENSE_INHABITED_SECTION')
    for k in range(3):
        az=z+h*(.17+k*.19)
        block(name+f'_GLAZED_CRACK_{k}',x-0.15*w,y-0.29*d,az,w*.18,2,h*.08,'glass','H1_DENSE_INHABITED_SECTION',.12)
# Winding street systems connect three distinct heights, not a wide empty stage.
route('H1_MAIN_PUBLIC_STREET',[(-1380,-280,819),(-1260,-320,819),(-1100,-295,820),(-930,-250,820),(-770,-160,820)],30,12,'chalk','H1_DENSE_INHABITED_SECTION')
route('H1_UPPER_COMMONS_STREET',[(-1260,105,891),(-1100,95,891),(-910,130,893),(-740,200,891)],24,8,'chalk','H1_DENSE_INHABITED_SECTION')
route('H1_TERRACE_GARDEN_STREET',[(-1055,-580,982),(-910,-510,982),(-760,-460,982),(-650,-300,982)],22,8,'chalk','H1_DENSE_INHABITED_SECTION')
stair('H1_LEVEL_CHANGE_SOUTH',(-1330,-280,820),(-1235,-10,890),22,20)
stair('H1_LEVEL_CHANGE_NORTH',(-960,100,890),(-880,-270,984),20,24)
for n,(x,y,z) in enumerate([(-1330,-180,826),(-1110,-170,827),(-1000,285,894),(-710,-400,985)]):
    # The gardens are recognizable as thick planter islands, not tree-icon rows.
    p=[(-33,-11),(-16,-32),(28,-26),(44,4),(17,26),(-26,32)]
    loft(f'H1_COURTYARD_BIOME_{n}',p,[(z,x,y,1.0,1.0,.2),(z+17,x,y,.86,.80,.2)],'vegetation','H1_DENSE_INHABITED_SECTION')

# Transit: highly legible spatial section with visibly multiple connections.
route('TRANSIT_PRIMARY_CIVIC_TO_H1',[(-310,90,470),(-460,92,520),(-610,10,620),(-790,-78,705),(-1050,-180,818)],40,15,'titanium')
route('TRANSIT_SEA_FACING_CONNECTION',[(275,-70,317),(410,-190,381),(565,-260,450),(775,-360,530)],27,10,'chalk')
route('TRANSIT_SECOND_H1_SERVICE_SECTION',[(-390,270,475),(-540,300,555),(-720,255,698),(-925,230,885)],26,8,'pearl')
for name,point,z in [('NAVE_CIVIC_STOP',(-308,89),470),('H1_RIDGE_STOP',(-1045,-180),819),('SEA_PROMENADE_STOP',(770,-355),530)]:
    x,y=point
    prism(name+'_TERMINAL',[ (x-50,y-40),(x+40,y-45),(x+65,y+10),(x+5,y+45),(x-55,y+24)],z-8,z+5,'bronze','INTERDISTRICT_PUBLIC_TRANSIT')

# Ground arrival is surrounded by imposing service/public architecture to be
# read from eye height, not a monolithic lid blocking all views.
route('GROUND_ARRIVAL_MAIN',[(-225,-910,146),(-210,-660,147),(-100,-470,165)],39,13,'chalk')
for i,(x,y) in enumerate([(-390,-780),(-90,-810),(245,-695)]):
    p=[(-75,-28),(-40,-80),(60,-72),(90,20),(10,96),(-80,55)]
    loft(f'GROUND_CIVIC_PORTAL_DISTINCT_WING_{i}',p,[(135,x,y,1.0,1.0,.1*i),(300+i*35,x-10,y+27,.72,.7,.2*i)],'basalt','NAVE_MULTILEVEL_CIVIC_ROOM')
    block(f'GROUND_PORTAL_GLAZED_PUBLIC_HALL_{i}',x,y-30,168,58,18,55,'glass','NAVE_MULTILEVEL_CIVIC_ROOM')

# Camera and light rig; fixed named views. 1.65m above research walking surfaces.
def camera(name,loc,look,ortho=None,lens=27):
    data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data)
    C['VIEW_CAMERAS'].objects.link(ob)
    ob.location=loc;direction=Vector(look)-ob.location
    ob.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    data.lens=lens
    data.clip_end=26000
    if ortho:data.type='ORTHO';data.ortho_scale=ortho
    return ob
camera('human_public_interior',(-100,-440,165.65),(-30,130,415),lens=25)
camera('human_sky_district',(-1325,-300,825.65),(-805,-95,1050),lens=26)
camera('urban_aerial',(-3200,-3650,2600),(0,100,820),ortho=5000)
camera('human_street',(-205,-840,148.65),(-100,-10,700),lens=26)
camera('central_front',(40,-3100,1200),(0,0,1120),ortho=3500)
camera('central_rear',(450,2600,1750),(0,20,1050),ortho=3700)
camera('east_seafront',(3000,-1150,1100),(-100,-50,1250),ortho=4800)

sun_data=bpy.data.lights.new('Soft atmospheric sun','SUN')
sun=bpy.data.objects.new('Soft atmospheric sun',sun_data);C['VIEW_CAMERAS'].objects.link(sun)
sun.rotation_euler=(math.radians(30),math.radians(-18),math.radians(-35));sun_data.energy=2.1
sun_data.angle=math.radians(13)

# Documentary metadata. No claimed path/occupancy certifications.
for n in ['M247-C','W0','H1','H2','H3','H4','H5','H6']+[f'SB{i:02d}' for i in range(1,17)]+['V1','V2','V3']+[f'METRO_AXIS_{i}' for i in range(1,4)]:
    ob=bpy.data.objects.new('REGISTRY_ONLY_'+n,None)
    C['30_TARGET_REGISTRY_RESEARCH_ONLY'].objects.link(ob)
    ob['status']='PARTIAL_RESEARCH' if n in ['M247-C','W0','H1'] else 'NOT_PRODUCED'
    ob['not_an_artwork_completion']=True
assert len(C['30_TARGET_REGISTRY_RESEARCH_ONLY'].objects)==30

blend=out/'E6_INHABITED_FAULT_CITY_WORKING.blend'
# Use uncompressed standard file; verify via independent process later.
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=False)
print('HALO9_E6_NATIVE_BLEND_SAVED',str(blend),flush=True)
for name in ['human_public_interior','human_sky_district','urban_aerial']:
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=str(out/'renders'/f'{name}.png')
    bpy.ops.render.render(write_still=True)
    print('HALO9_E6_NATIVE_RENDER_SAVED',name,flush=True)
# Restore a primary camera and save, meaning final scene opens with an authored view.
scene.camera=bpy.data.objects['urban_aerial']
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=False)
report={
    'schema':'halo9-r4-e6-research-native-v1',
    'technical':'NATIVE_AUTHOR_COMPLETED_REOPEN_PENDING',
    'art':'PENDING_DIRECT_NATIVE_IMAGE_JURY_NO_ADOPTION',
    'completed_targets':0,'official_coordinates_verified':False,
    'minecraft':'HOLD','formal_art_adoption':False,
    'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),
    'images':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((out/'renders').glob('*.png'))},
    'mesh_count':len([o for o in bpy.data.objects if o.type=='MESH']),
    'no_R0B_source_or_geometry_imported':True,
    'units':'non-certified research metres',
}
(out/'AUTHOR_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('HALO9_E6_AUTHOR_REPORT',json.dumps(report),flush=True)