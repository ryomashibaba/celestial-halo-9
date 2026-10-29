"""D47-R3: inhabited sectional architecture, NOT a canonical city or art acceptance.

Unlike R1 (named empty slabs) or R2 (one Boolean-sculpted boulder), space is authored
as occupied public rooms with genuinely open portals, usable floors and connections.
The prototype is deliberately local (~0.8 km) to expose design-method defects early.
No GUI / Work, no official W0/M247-C geometry, no Minecraft writes.
Run: python d47_r3_habitable_section.py /absolute/output/directory
"""
import bpy, math, sys, json
from pathlib import Path
from mathutils import Vector
from math import pi, sin, cos
P = Path(sys.argv[-1]); P.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def group(name):
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c

def material(name,col):
    m=bpy.data.materials.new(name); m.diffuse_color=(*col,1); return m

ivory=material('01 public architecture bone',(.79,.76,.66))
shell=material('02 shaded city wall',(.18,.25,.30))
copper=material('03 civic library warm',(.58,.36,.24))
blue=material('04 transit blue',(.22,.47,.55))
glass=material('05 clerestory glass',(.36,.67,.73))
ground=material('06 urban walking stone',(.58,.60,.55))
gold=material('07 community amphitheater',(.73,.62,.35))
terrain=material('08 contextual land not approved',(.19,.26,.28))
lake=material('09 contextual sea not approved',(.06,.23,.31))

def geom(name,v,f,mat,layer,role):
    me=bpy.data.meshes.new(name+'_editable')
    me.from_pydata(v,[],f); me.update()
    o=bpy.data.objects.new(name,me);group(layer).objects.link(o)
    me.materials.append(mat)
    o['role']=role
    o['scope']='provisional R3 architectural section only'
    return o

def prism(name,poly,lo,hi,mat,layer,role):
    n=len(poly)
    v=[(x,y,lo) for x,y in poly]+[(x,y,hi) for x,y in poly]
    f=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]
    for i in range(n):
        j=(i+1)%n
        f.append((i,j,n+j,n+i))
    return geom(name,v,f,mat,layer,role)

def block(name,x0,x1,y0,y1,z0,z1,mat,layer,role):
    assert x1>x0 and y1>y0 and z1>z0
    return prism(name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],
                 z0,z1,mat,layer,role)

def horizontal_wall(name,x0,x1,y,z0,z1,th,m,lay,role):
    return block(name,x0,x1,y-th/2,y+th/2,z0,z1,m,lay,role)

def vertical_wall(name,x,y0,y1,z0,z1,th,m,lay,role):
    return block(name,x-th/2,x+th/2,y0,y1,z0,z1,m,lay,role)

def inside_room(name, bounds, height, portal, kind, tint):
    """Functional closed-sided room with genuine empty portal to a public route."""
    x0,x1,y0,y1,z0=bounds
    assert z0>=0 and height>=50
    lay='02 INHABITED PUBLIC ENCLOSURES'
    t=9.5
    block(name+'_ACTUAL_FLOOR',x0,x1,y0,y1,z0-8,z0,tint,lay,
          kind+' physically usable interior floor')
    block(name+'_WEATHER_ROOF',x0,x1,y0,y1,z0+height,z0+height+14,ivory,lay,
          kind+' weather roof actually above enclosed room')
    # Three solid walls plus exactly one open portal with real side piers and lintel.
    if portal=='EAST':
        horizontal_wall(name+'_SOUTH',x0,x1,y0,z0,z0+height,t,shell,lay,kind+' enclosed south wall')
        horizontal_wall(name+'_NORTH',x0,x1,y1,z0,z0+height,t,shell,lay,kind+' enclosed north wall')
        vertical_wall(name+'_WEST',x0,y0,y1,z0,z0+height,t,ivory,lay,kind+' outer west wall')
        yc=(y0+y1)/2
        vertical_wall(name+'_PORTAL_SOUTH_PIER',x1,y0,yc-41,z0,z0+height,t,ivory,lay,'physical east opening pier')
        vertical_wall(name+'_PORTAL_NORTH_PIER',x1,yc+41,y1,z0,z0+height,t,ivory,lay,'physical east opening pier')
        vertical_wall(name+'_PORTAL_LINTEL',x1,yc-41,yc+41,z0+55,z0+height,t,ivory,lay,'opening lintel with 55m open height')
        portal_probe=(x1,yc,z0+18)
    elif portal=='WEST':
        horizontal_wall(name+'_SOUTH',x0,x1,y0,z0,z0+height,t,shell,lay,kind+' enclosed south wall')
        horizontal_wall(name+'_NORTH',x0,x1,y1,z0,z0+height,t,shell,lay,kind+' enclosed north wall')
        vertical_wall(name+'_EAST',x1,y0,y1,z0,z0+height,t,ivory,lay,kind+' outer east wall')
        yc=(y0+y1)/2
        vertical_wall(name+'_PORTAL_SOUTH_PIER',x0,y0,yc-41,z0,z0+height,t,ivory,lay,'physical west opening pier')
        vertical_wall(name+'_PORTAL_NORTH_PIER',x0,yc+41,y1,z0,z0+height,t,ivory,lay,'physical west opening pier')
        vertical_wall(name+'_PORTAL_LINTEL',x0,yc-41,yc+41,z0+55,z0+height,t,ivory,lay,'opening lintel with 55m open height')
        portal_probe=(x0,yc,z0+18)
    elif portal=='SOUTH':
        vertical_wall(name+'_EAST',x1,y0,y1,z0,z0+height,t,ivory,lay,kind+' east wall')
        vertical_wall(name+'_WEST',x0,y0,y1,z0,z0+height,t,ivory,lay,kind+' west wall')
        horizontal_wall(name+'_NORTH',x0,x1,y1,z0,z0+height,t,shell,lay,kind+' north wall')
        xc=(x0+x1)/2
        horizontal_wall(name+'_PORTAL_WEST_PIER',x0,xc-44,y0,z0,z0+height,t,ivory,lay,'physical south portal pier')
        horizontal_wall(name+'_PORTAL_EAST_PIER',xc+44,x1,y0,z0,z0+height,t,ivory,lay,'physical south portal pier')
        horizontal_wall(name+'_PORTAL_LINTEL',xc-44,xc+44,y0,z0+59,z0+height,t,ivory,lay,'opening lintel with 59m open height')
        portal_probe=(xc,y0,z0+18)
    else: raise ValueError(portal)
    return {'id':name,'role':kind,'opening_axis':portal,'probe_m':portal_probe,
            'clear_opening_height_m':55 if portal!='SOUTH' else 59,
            'open_width_m':82 if portal!='SOUTH' else 88,
            'base_z_m':z0,'roof_z_m':z0+height}

def face_roof(name,profiles,mat,role):
    """Non-primitive authored folded habitable upper façade/roof connection."""
    n=len(profiles[0])
    assert len(profiles)>1 and all(len(p)==n for p in profiles)
    vs=[pt for row in profiles for pt in row]
    fs=[]
    for j in range(len(profiles)-1):
        for i in range(n-1):
            a=j*n+i;fs.append((a,a+1,a+n+1,a+n))
    return geom(name,vs,fs,mat,'05 ARCHITECTURAL URBAN SECTION',role)

# The civic path and large central chamber are real ground, not artist-only markers.
block('SOUTH_PUBLIC_ENTRY_STREET',-59,59,-465,-160,-10,0,ground,
      '01 SHARED CIVIC TOPOLOGY','ground-level public approach from W0 concept')
block('MAIN_RIFT_CIVIC_CONCOURSE',-148,148,-160,167,-10,0,ground,
      '01 SHARED CIVIC TOPOLOGY','central public chamber with interdependent adjacent enclosed rooms')
block('NORTH_TRANSITION_PUBLIC_STREET',-62,62,167,448,-10,0,ground,
      '01 SHARED CIVIC TOPOLOGY','public north continuation, no official world tie')

rooms=[]
rooms.append(inside_room('WEST_ARCHIVE_AND_LIBRARY',
    (-377,-166,-126,200,0),127,'EAST','public library with archive room',copper))
rooms.append(inside_room('EAST_STATION_INTERCHANGE',
    (164,399,-202,178,0),114,'WEST','transit interchange and concourse',blue))
rooms.append(inside_room('NORTH_CIVIC_FORUM',
    (-142,151,170,391,0),166,'SOUTH','public civic assembly and museum',gold))
# All three real portals lead toward the shared ground via actual corridor floor meshes.
block('WEST_ACTUAL_PORTAL_THRESHOLD',-176,-127,-16,98,-8,0,ground,
      '01 SHARED CIVIC TOPOLOGY','public floor crossing the real west portal threshold')
block('EAST_ACTUAL_PORTAL_THRESHOLD',125,178,-66,55,-8,0,ground,
      '01 SHARED CIVIC TOPOLOGY','public floor crossing the real east portal threshold')
block('NORTH_ACTUAL_PORTAL_THRESHOLD',-68,69,143,191,-8,0,ground,
      '01 SHARED CIVIC TOPOLOGY','public floor crossing the real north portal threshold')

# Distinct interiors: different occupation and spatial use, physically INSIDE room bounds.
for i,(y,x) in enumerate([(-85,-337),(8,-337),(94,-337),(162,-337)]):
    block('WEST_REAL_OPEN_READ_SHELVING_%02d'%i,x,x+45,y,y+13,0,39,copper,
          '03 ACTUAL INTERIOR USE','physical archive shelving, not a texture')
# Station: tracks are actually separated by passenger platform.
for i,(x,ma) in enumerate([(219,blue),(334,blue)]):
    block('EAST_PASSENGER_PLATFORM_%d'%i,x,x+37,-147,135,0,7,ma,
          '03 ACTUAL INTERIOR USE','physical raised station island platform')
for i,x in enumerate([262,308]):
    block('EAST_TRACK_WELL_%d'%i,x,x+5,-153,146,-4,1,shell,
          '03 ACTUAL INTERIOR USE','rail alignment indicator, not certified service')
# Forum: stepped in-situ seating around an actual accessible central open stage.
for i,rad in enumerate([0,1,2,3]):
    x0=-117+i*15; x1=115-i*15
    y0=309+i*11; y1=342+i*8
    block('FORUM_OCCUPIED_TIER_%d'%i,x0,x1,y0,y1,i*8,i*8+7,gold,
          '03 ACTUAL INTERIOR USE','physical stepped auditorium seating')

# An upper inhabited research volume sits across all three roofs, bearing on the rooms.
# It must be a volumetric occupied element, not a free floating blank roof slab.
block('UPPER_CROSS_CIVIC_BASE',-316,305,163,260,180,192,ivory,
      '05 ARCHITECTURAL URBAN SECTION',
      'actual deep inhabited lateral city crossing with adjacent room supports')
block('UPPER_CROSS_LIBRARY_WALL',-314,305,163,176,192,274,shell,
      '05 ARCHITECTURAL URBAN SECTION','enclosed side of inhabited urban crossing')
block('UPPER_CROSS_FORUM_WALL',-314,305,246,259,192,274,ivory,
      '05 ARCHITECTURAL URBAN SECTION','enclosed second side, life spaces inside')
block('UPPER_CROSS_CITY_ROOF',-330,327,151,268,273,290,ivory,
      '05 ARCHITECTURAL URBAN SECTION','physical roof of enclosed upper urban crossing')
# Facade openings of genuinely occupied bridge: alternate entire-wall openings 20-28m.
for j,(x0,x1) in enumerate([(-271,-236),(-188,-143),(-91,-45),
                           (2,53),(105,144),(195,251)]):
    block('UPPER_CROSS_GLAZED_INHABITED_WINDOW_%02d'%j,
          x0,x1,174.5,179.5,215,252,glass,
          '05 ARCHITECTURAL URBAN SECTION',
          'aperture indication in inhabited crossing; glazing facade')
# Far side transversely folded canopy forms continuation of the upper inhabited volume.
face_roof('ASYMMETRIC_INTERLOCKED_PUBLIC_CROWN',[
 [(-344,166,291),(-230,174,324),(-80,183,356),(65,183,327),(240,178,301),(362,175,267)],
 [(-342,260,300),(-230,259,352),(-80,268,375),(65,273,338),(240,270,311),(358,269,290)],
 [(-291,356,247),(-220,348,280),(-45,351,308),(55,350,295),(208,342,267),(274,336,242)]
],ivory,'roof geometry is related to occupied upper city, not standalone outer sculpture')

# Raised occupied room with real upper-world thickness, asymmetrically offset and supported.
block('HIGH_OCCUPIED_CULTURAL_VOLUME',-341,-140,231,448,295,411,copper,
      '05 ARCHITECTURAL URBAN SECTION','solid occupied cultural/civic upper city study shell, rooms unverified')
block('HIGH_OCCUPIED_CULTURAL_ROOF',-347,-135,226,454,412,432,ivory,
      '05 ARCHITECTURAL URBAN SECTION','upper cultural volume roof')
# A substantial station skylight canopy connects upper city to east hall roof.
face_roof('TRANSIT_PUBLIC_LIGHT_BUTTRESS',[
 [(178,-215,117),(271,-220,178),(356,-219,201),(416,-217,145)],
 [(170,5,134),(264,20,211),(373,25,234),(424,5,172)],
 [(155,178,125),(253,185,198),(354,200,219),(409,179,153)]
],glass,'station lighting canopy tied to actual enclosed station')

# Explicit elevators: multi-storey shafts with wall skins and a real enclosed car.
# Doors and mechanical function need independent engineering; never call them certified.
for idx,x,y in [(0,-210,130),(1,220,123)]:
    lay='04 VERTICAL CIRCULATION PROVISIONAL'
    block('LIFT_SHAFT_WEST_%d'%idx,x-17,x-12,y-21,y+21,0,302,shell,lay,
          'vertical transport structure, mechanism unverified')
    block('LIFT_SHAFT_EAST_%d'%idx,x+12,x+17,y-21,y+21,0,302,shell,lay,
          'vertical transport structure, mechanism unverified')
    block('LIFT_SHAFT_REAR_%d'%idx,x-17,x+17,y+17,y+22,0,302,shell,lay,
          'vertical transport structure, mechanism unverified')
    block('LIFT_CAR_FLOOR_%d'%idx,x-10,x+10,y-14,y+14,4,8,blue,lay,
          'actual car floor present, accessibility unverified')

# Foreground and approximate water/terrain expressly NOT city development.
block('W0_CONTEXT_GROUND_NOT_CANONICAL',-790,795,-740,-475,-31,-18,terrain,
      '06 PROVISIONAL CONTEXT ONLY','rough placement scaffold, not finished W0')
block('W0_CONTEXT_EAST_SEA_NOT_CANONICAL',575,830,-740,615,-30,-22,lake,
      '06 PROVISIONAL CONTEXT ONLY','research-only inland sea indicative direction')

# One camera at near-human scale and three architecture views, avoiding empty distant renders.
def camera(name,loc,target,scale=None):
    ca=bpy.data.cameras.new(name); ob=bpy.data.objects.new(name,ca)
    group('07 FIXED REVIEW CAMERAS').objects.link(ob)
    ob.location=loc
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    ca.clip_end=20000
    if scale:
        ca.type='ORTHO';ca.ortho_scale=scale
    else:
        ca.type='PERSP';ca.lens=22
    return ob

views=[
 ('01_arrival',(12,-520,12),(3,10,88),None),
 ('02_shared_public_room',(3,-85,27),(-25,195,150),None),
 ('03_west_inhabited_room',(-223,19,23),(-300,75,54),None),
 ('04_east_transit_room',(220,-49,29),(337,34,62),None),
 ('05_threequarter_city',(1050,-1130,690),(0,10,200),1150),
 ('06_rear_urban_section',(-950,970,830),(0,75,200),1050)
]
for q in views: camera(*q)
scene=bpy.context.scene
scene['research_phase']='D47-R3 functional spaces before outer form'
scene['formal_policy']='CITY_MASTER_3D_FIRST_LOCKED'
scene['canonical_coordinates']=False
scene['art_adopted']=False
scene['M247_C_protected']=True
scene['official_minecraft_construction']=False
scene['completed_10km_city_master']=False
scene['all_rooms_stair_lift_verified']=False
scene['blender_gui_direct_edit_proven']=False
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_cavity=True
scene.render.resolution_x=1120
scene.render.resolution_y=730
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
# Must save before camera renders for stable reproducible original.
bpy.ops.wm.save_as_mainfile(filepath=str(P/'D47_R3_G0_EDITABLE.blend'))
bpy.ops.export_scene.gltf(filepath=str(P/'D47_R3_G0.glb'),export_format='GLB',
                          export_cameras=False,export_lights=False)
for name,*_ in views:
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=str(P/(name+'.png'))
    bpy.ops.render.render(write_still=True)
manifest={
 'scope':'~0.8 km functional civic section, noncanonical; not a 10 km city',
 'technical_state':'G0_GENERATED_NOT_YET_INDEPENDENTLY_VERIFIED',
 'art':'UNREVIEWED',
 'rooms':rooms,
 'doors_created_as_real_geometric_gaps':len(rooms),
 'shared_reachable_ground':'physical same-level ground plan; formal walk QA NOT PROVED',
 'upper_city_lift_function':'NOT VERIFIED',
 'all_streets_and_platforms_accessible':'NOT VERIFIED',
 'actual_meshes':len([o for o in bpy.data.objects if o.type=='MESH']),
 'render_names':[n+'.png' for n,*_ in views],
 'blender_version':bpy.app.version_string,
 'official_coordinates':False,'formal_art_adopted':False,
 '10km_master_complete':False,'H1_H6_complete':False,'SB01_SB16_complete':False,
 'minecraft_construction_authorized':False,'gui_direct_edit_proven':False
}
(P/'D47_R3_G0_MANIFEST.json').write_text(
    json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('D47_R3_G0_CREATED_ART_UNREVIEWED',json.dumps(manifest,ensure_ascii=False))
