"""R1: direct edit of the R0 live geometry after visual rejection.
Principal edits: open inhabited atria, dislocated upper city, structural public hall,
H1 public courtyard, and ground/water section. Fixed review camera matrices retained.
"""
import bpy,math,pathlib
from mathutils import Vector
E=bpy.app.driver_namespace['E11']
globals().update({k:v for k,v in E.items() if not k.startswith('__')})
S=bpy.data.scenes['E11_INHABITED_SECTION_RESEARCH']
bpy.context.window.scene=S
def clip(poly,axis,threshold):
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ina=a[axis]>=threshold;inb=b[axis]>=threshold
        if ina: result.append(a)
        if ina!=inb:
            t=(threshold-a[axis])/(b[axis]-a[axis]);result.append(tuple(a[k]+t*(b[k]-a[k]) for k in range(3)))
    return result
changed=[]
for o in list(S.objects):
    if o.type!='MESH':continue
    name=o.name
    iswest=name.startswith('M247_WEST_ASCENDING_CITY');iseast=name.startswith('M247_EAST_TIDAL_BUTTRESS_CITY')
    if iswest or iseast:
        # Open the occupied volume to the NAVE, retaining real floors behind the recess.
        old=o.data;vs=[];fs=[];mi=[]
        for face in old.polygons:
            pts=[tuple(old.vertices[i].co) for i in face.vertices]
            z=sum(p[2] for p in pts)/len(pts)
            if (iswest and 174<z<365) or (iseast and 205<z<322):
                pts=clip(pts,1,(-25 if iswest else 10)+.14*(z-200))
            if iswest and 525<z<596: continue
            if len(pts)<3:continue
            k=len(vs);vs.extend(pts);fs.append(tuple(range(k,k+len(pts))));mi.append(face.material_index)
        new=bpy.data.meshes.new(name+'_R1_CARVED');new.from_pydata(vs,[],fs);new.update()
        for ma in old.materials:new.materials.append(ma)
        for f,i in zip(new.polygons,mi):f.material_index=i
        o.data=new
        for v in new.vertices:
            z=v.co.z
            if iswest and z>=596:
                t=(z-596)/414; x,y=v.co.x,v.co.y
                angle=.18*t
                v.co.x=-210+(x+210)*math.cos(angle)-(y-100)*math.sin(angle)+105+45*t
                v.co.y=100+(x+210)*math.sin(angle)+(y-100)*math.cos(angle)+45
                if z>900:v.co.z+=max(0,(v.co.y-140))*.44*((z-900)/110)
        changed.append(name)
# Curved exoskeletons move with the displaced upper body as well.
for o in S.objects:
    if o.type=='CURVE' and o.name.startswith('M247_WEST_ASCENDING_CITY'):
        for sp in o.data.splines:
            for p in sp.points:
                if p.co.z>=596:
                    t=(p.co.z-596)/414;x,y=p.co.x,p.co.y;angle=.18*t
                    p.co.x=-210+(x+210)*math.cos(angle)-(y-100)*math.sin(angle)+105+45*t
                    p.co.y=100+(x+210)*math.sin(angle)+(y-100)*math.cos(angle)+45
                    if p.co.z>900:p.co.z+=max(0,p.co.y-140)*.44*((p.co.z-900)/110)
        # The long spines intentionally bridge the upper-city displacement.
for m in [stone,lightstone]:
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.39,.44,.43,1) if m==stone else (.48,.40,.29,1)
warmnode=next(n for n in warm.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
warmnode.inputs['Emission Strength'].default_value=.08
for o in C['LIGHTS'].objects:
    if o.data.type=='AREA':o.data.energy*=.085

# Diagonal inhabited transfer mass is modelled as a deep, open public cross-section.
# It is a different sculpted volume, not a large cosmetic roof over R0.
slab('R1_SKY_TRANSFER_CITY_LOWER',[(-325,100),(-180,40),(20,135),(275,245),(335,350),(150,405),(-80,300),(-300,230)],410,22,stone,'M247_C')
slab('R1_SKY_TRANSFER_CITY_UPPER',[(-260,145),(-155,90),(55,180),(290,280),(300,370),(140,395),(-85,290),(-250,245)],478,18,stone,'M247_C')
for i,(a,b) in enumerate([
 ((-310,150,410),(-190,170,478)),((-120,155,410),(-60,220,478)),((70,225,410),(145,300,478)),((275,290,410),(260,335,478))]):
    beam('R1_SKY_PUBLIC_BRANCH_'+str(i),a,b,13,22,stone,'M247_C')
for name,poly,z in [
 ('WEST_OPEN_LIBRARY',[(-455,-15),(-310,-20),(-190,50),(-225,195),(-405,205)],184),
 ('WEST_MID_CONSERVATORY',[(-430,15),(-280,10),(-170,90),(-215,220),(-390,230)],304),
 ('EAST_OPEN_CIVIC_ROOM',[(230,25),(405,20),(505,100),(440,225),(275,180)],224)]:
    slab('R1_'+name+'_GARDEN',poly,z,6,green,'M247_C')
    for i in [0,2,4]:
        x,y=poly[i];beam('R1_'+name+'_PIER_'+str(i),(x,y,z),(x+14,y+25,z+51),7,12,stone,'M247_C')

# NAVE: a civic forum with walk-in colonnades, broad stepped auditorium and water room.
slab('R1_NAVE_PUBLIC_STOA_FLOOR',[(-140,-155),(-80,-210),(70,-190),(140,-90),(115,25),(-10,70),(-125,5)],91,10,lightstone)
for j in range(17):
    y=-225+j*3.5;w=45+j*1.9
    slab('R1_NAVE_FORUM_STAIR_'+str(j),[(-w,y),(w,y),(w+1.9,y+3.5),(-w-1.9,y+3.5)],72+(j+1)*1.12,1.8,lightstone)
# Four branching portal piers frame a room rather than closing a shell around it.
for i,(x,y) in enumerate([(-115,-85),(95,-75),(-75,30),(70,35)]):
    beam('R1_NAVE_STOA_TRUNK_'+str(i),(x,y,91),(x*.72,y+14,138),7,10,stone,'NAVE')
    beam('R1_NAVE_STOA_BRANCH_A_'+str(i),(x*.72,y+14,138),(x*1.05,y-25,174),5,9,stone,'NAVE')
    beam('R1_NAVE_STOA_BRANCH_B_'+str(i),(x*.72,y+14,138),(x*.45,y+35,181),5,9,stone,'NAVE')
# Sculpted five-station canopy vault with thickness; open perimeter and open clerestory.
for side in [-1,1]:
    rows=[]
    for y,w,z in [(-150,105,170),(-90,140,181),(-20,150,191),(50,112,184),(100,50,163)]:
        rows.append([(side*w,y,z-18),(side*w*.55,y,z+6),(side*18,y,z+18),(side*18,y,z+13),(side*w*.55,y,z),(side*w,y,z-25)])
    volume('R1_NAVE_SCULPTED_VAULT_'+str(side),rows,stone,'NAVE',1)
# Ring of inhabited two-storey public rooms behind the stoa.
for name,poly in [
 ('WEST_READING_ROOM',[(-148,-55),(-115,-80),(-65,-25),(-65,35),(-125,45),(-160,10)]),
 ('EAST_CITY_MODEL_ROOM',[(95,-60),(140,-30),(150,20),(110,60),(65,35),(65,-15)])]:
    slab('R1_'+name+'_MEZZANINE',poly,110,3,stone)
    slab('R1_'+name+'_ROOF',poly,129,4,stone)
    for i in [0,2,4]:
        x,y=poly[i];beam('R1_'+name+'_COLUMN_'+str(i),(x,y,91),(x,y,129),2.2,3,stone,'NAVE')
    # Actual opaque rear wall, facing the central room through an open front.
    a,b=poly[0],poly[1];beam('R1_'+name+'_REAR_WALL',(a[0],a[1],109),(b[0],b[1],109),2,36,dark,'NAVE')
# Water and foreground use a meaningful two-level threshold.
slab('R1_NAVE_REFLECTING_POOL',[(-76,-332),(-20,-346),(15,-315),(6,-265),(-43,-250),(-80,-279)],72.25,1.3,water)
slab('R1_NAVE_POOL_BORDER',[(-86,-337),(-18,-355),(24,-319),(15,-258),(-44,-240),(-90,-277)],72.0,1.5,copper)

# Public landscaping, furniture and scale figures are auxiliary, never main city mass.
def tree(name,x,y,z,h,group):
    beam(name+'_TRUNK',(x,y,z),(x+1,y,z+h*.63),h*.055,h*.07,copper,group)
    for dx,dy,sz in [(-.2,.08,.46),(.19,.08,.43),(0,-.13,.5)]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(x+dx*h,y+dy*h,z+h*.72))
        o=bpy.context.object;o.name=name+'_CROWN';o.scale=(h*sz,h*sz*.7,h*.3)
        for c in list(o.users_collection):c.objects.unlink(o)
        C[group].objects.link(o);o.data.materials.append(green)
def person(name,x,y,z,group):
    # 1.75m scale marker with torso, head and legs, modelled and stored in BLEND.
    beam(name+'_BODY',(x,y,z+.65),(x,y,z+1.4),.36,.24,dark,group)
    for dx in [-.12,.12]:beam(name+'_LEG',(x+dx,y,z),(x+dx,y,z+.7),.12,.12,dark,group)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.15,location=(x,y,z+1.62))
    o=bpy.context.object;o.name=name+'_HEAD'
    for c in list(o.users_collection):c.objects.unlink(o)
    C[group].objects.link(o);o.data.materials.append(lightstone)
for i,(x,y) in enumerate([(-95,-315),(-100,-265),(60,-305),(105,-245),(-150,-195),(145,-150),(-135,-60),(115,-20)]):
    slab('R1_NAVE_PLANTER_'+str(i),[(x-5,y-5),(x+5,y-5),(x+5,y+5),(x-5,y+5)],74,2,lightstone)
    tree('R1_NAVE_TREE_'+str(i),x,y,74,12,'DETAIL')
for i,(x,y) in enumerate([(14,-333),(22,-326),(28,-300),(-15,-283),(40,-290),(60,-270),(-57,-298),(-100,-230),(90,-210),(-9,-179),(10,-159),(-35,-138),(35,-125),(-25,-94),(45,-55),(12,0)]):
    person('R1_NAVE_PERSON_'+str(i),x,y,72 if y<-225 else 91,'DETAIL')
for i,(x,y) in enumerate([(708,280),(820,285),(770,345),(815,390),(710,390),(765,190),(800,310),(735,335)]):
    slab('R1_H1_GARDEN_'+str(i),[(x-6,y-7),(x+6,y-7),(x+6,y+7),(x-6,y+7)],439,2,lightstone,'H1')
    tree('R1_H1_TREE_'+str(i),x,y,439,11,'H1')
for i,(x,y) in enumerate([(758,292),(765,300),(755,310),(790,325),(735,305),(720,330),(800,350),(775,370),(750,385),(825,385)]):person('R1_H1_PERSON_'+str(i),x,y,437,'H1')
for i,(x,y,z,group) in enumerate([(-72,-330,72,'NAVE'),(64,-305,72,'NAVE'),(-105,-290,72,'NAVE'),(735,285,437,'H1'),(815,335,437,'H1'),(750,370,437,'H1')]):
    beam('R1_PUBLIC_SEAT_'+str(i),(x-3,y,z+.5),(x+3,y,z+.5),1.2,.6,lightstone,group)
    line('R1_PUBLIC_LIGHT_'+str(i),[(x+4,y,z),(x+4,y,z+5),(x+2,y,z+5)],.12,copper,group)

# Façade vertical depth breaks the previous unrelieved horizontal stripes.
for profiles,name in [(west,'W'),(east,'E')]:
    for i in [1,3,5,7]:
        # Lower carved faces remain open; fins follow only the solid back and side faces.
        if i not in [3,5]:continue
        pts=[(p[i][0],p[i][1],z) for z,p in profiles if z<525]
        if len(pts)>1:line('R1_CITY_REAR_FIN_'+name+str(i),pts,5,stone,'M247_C')
S['REVISION']='R1_AFTER_DIRECT_VISUAL_REJECTION'
S['PRINCIPAL_MESHES_EDITED']=len(changed)
S['ART_STATUS']='AWAITING_R1_IMAGES'
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'E11_INHABITED_SECTION_WORKING.blend'))
(ROOT/'R1_change_record.json').write_text(__import__('json').dumps({'principal_meshes_directly_edited':len(changed),'camera_matrices_changed':False,'method':'MCP direct geometry clipping/displacement and authored public-section additions','formal_art':0,'completion':0,'world':'HOLD'},indent=2),encoding='utf-8')
print('E11_R1_SAVED',len(S.objects),'PRINCIPAL_EDITED',len(changed))
