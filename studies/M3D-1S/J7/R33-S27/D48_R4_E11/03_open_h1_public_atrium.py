"""Direct R2 public-section intervention. Keep the same human and aerial cameras."""
import bpy,math
from mathutils import Vector
E=bpy.app.driver_namespace['E11'];globals().update({k:v for k,v in E.items() if not k.startswith('__')})
import ast
# Reuse only the auxiliary tree helper; do not re-execute R1 geometry edits.
source=(ROOT/'02_recompose_same_mesh.py').read_text(encoding='utf-8')
node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='tree')
exec(compile(ast.Module(body=[node],type_ignores=[]),'E11_auxiliary_tree','exec'),globals())
S=bpy.data.scenes['E11_INHABITED_SECTION_RESEARCH'];bpy.context.window.scene=S
def half(poly,axis,value,sign=1):
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ia=(a[axis]-value)*sign>=0;ib=(b[axis]-value)*sign>=0
        if ia:out.append(a)
        if ia!=ib:
            t=(value-a[axis])/(b[axis]-a[axis]);out.append(tuple(a[k]+t*(b[k]-a[k]) for k in range(3)))
    return out
for o in list(S.objects):
    if o.type!='MESH':continue
    if o.name.startswith('H1_NORTH_SCHOOL_CRESCENT'):
        vs=[];fs=[];mi=[];old=o.data
        for f in old.polygons:
            poly=[tuple(old.vertices[i].co) for i in f.vertices];z=sum(p[2] for p in poly)/len(poly)
            pieces=[half(poly,0,718,-1),half(poly,0,835,1)] if 439<z<481 else [poly]
            for pts in pieces:
                if len(pts)<3:continue
                k=len(vs);vs.extend(pts);fs.append(tuple(range(k,len(vs))));mi.append(f.material_index)
        m=bpy.data.meshes.new(o.name+'_R2_PUBLIC_PORTAL');m.from_pydata(vs,[],fs);m.update()
        for ma in old.materials:m.materials.append(ma)
        for p,i in zip(m.polygons,mi):p.material_index=i
        o.data=m
    # North crown now folds over the public rift; main volume is edited, not camera-swapped.
    if o.name.startswith('M247_DISPLACED_NORTH_CROWN'):
        if o.type=='MESH':
            for v in o.data.vertices:
                if v.co.z>650:
                    t=(v.co.z-650)/630;v.co.x-=190*t;v.co.y+=70*t
                    if v.co.z>1150:v.co.z+=(v.co.y-510)*.85*((v.co.z-1150)/130)
for o in list(S.objects):
    if o.type=='CURVE' and o.name.startswith('M247_DISPLACED_NORTH_CROWN'):
        for sp in o.data.splines:
            for p in sp.points:
                if p.co.z>650:
                    t=(p.co.z-650)/630;p.co.x-=190*t;p.co.y+=70*t
                    if p.co.z>1150:p.co.z+=(p.co.y-510)*.85*((p.co.z-1150)/130)

# H1 school / library public hall is entered from the existing camera courtyard.
for i,(x,y) in enumerate([(716,413),(836,416),(720,502),(835,505)]):
    beam('R2_H1_PUBLIC_HALL_PIER_'+str(i),(x,y,437),(775+(x-775)*.53,y+8,478),4,6,stone,'H1')
    beam('R2_H1_PUBLIC_HALL_FORK_'+str(i),(775+(x-775)*.53,y+8,478),(x,y+10,487),3,4,stone,'H1')
slab('R2_H1_PUBLIC_HALL_GALLERY',[(710,400),(740,393),(750,430),(745,513),(708,523),(690,470)],461,3,lightstone,'H1')
slab('R2_H1_PUBLIC_HALL_EAST_GALLERY',[(825,400),(855,408),(875,475),(850,527),(817,512),(813,440)],461,3,lightstone,'H1')
for j in range(24):
    y=345+j*2.4
    slab('R2_H1_GALLERY_STAIR_'+str(j),[(692,y),(708,y),(708,y+2.4),(692,y+2.4)],437+(j+1),2,lightstone,'H1',.2)
# Storefronts have actual deep entrance returns beneath a roof; roofs differ from housing.
for i,(x,y) in enumerate([(700,365),(842,365),(725,470),(835,470)]):
    beam('R2_H1_DOOR_JAMB_L_'+str(i),(x-4,y,437),(x-4,y,445),1,2,copper,'H1')
    beam('R2_H1_DOOR_JAMB_R_'+str(i),(x+4,y,437),(x+4,y,445),1,2,copper,'H1')
    beam('R2_H1_DOOR_LINTEL_'+str(i),(x-4,y,445),(x+4,y,445),1,2,copper,'H1')
    line('R2_H1_PUBLIC_SIGN_'+str(i),[(x-3,y-1,446),(x+3,y-1,446)],.2,glow,'H1')
# A deep urban shore section: coves, flood terraces and the occupied W0 approach.
shore=[(-720,-650),(-575,-740),(-380,-730),(-180,-640),(-280,-560),(-450,-520),(-620,-550)]
slab('R2_W0_INHABITED_WEST_QUAY',shore,30,25,terrain,'W0')
slab('R2_W0_UPPER_URBAN_LAND',[(-750,-520),(-620,-550),(-450,-520),(-280,-560),(-225,-440),(-420,-355),(-680,-370)],62,32,terrain,'W0')
slab('R2_W0_BASALT_WATERSHED',[(-970,-270),(-840,-370),(-660,-320),(-545,-210),(-555,100),(-690,255),(-860,210),(-990,15)],86,80,terrain,'W0')
beam('R2_W0_TIDAL_ARCHIVE_BRIDGE',(-520,-555,35),(-225,-520,70),17,6,stone,'TRANSIT')
for i,(x,y) in enumerate([(-560,-660),(-480,-640),(-410,-620),(-600,-420),(-530,-420)]):
    tree('R2_W0_PUBLIC_TREE_'+str(i),x,y,32 if y<-500 else 64,16,'W0')
# Finely cut structural ribs frame the main rift as a diagonal sequence rather than flat walls.
for i,(a,b,c) in enumerate([
 ((-320,-210,72),(-230,-50,230),(-150,120,410)),
 ((320,-210,72),(250,-40,250),(180,130,478)),
 ((-360,120,185),(-150,230,410),(-65,300,680))]):
    beam('R2_RIFT_CARVED_PORTAL_BASE_'+str(i),a,b,12,22,stone,'M247_C')
    beam('R2_RIFT_CARVED_PORTAL_CROWN_'+str(i),b,c,9,18,stone,'M247_C')
S['REVISION']='R2_PUBLIC_ATRIA_AND_FOLDED_CROWN'
S['ART_STATUS']='AWAITING_R2_IMAGES'
# Keep an explicit 30-item obligation ledger without pretending marker geometry is detail.
targets=['M247_C','W0']+['H'+str(i) for i in range(1,7)]+['SB'+str(i).zfill(2) for i in range(1,17)]+['V'+str(i) for i in range(1,4)]+['METRO_AXIS_'+str(i) for i in range(1,4)]
text=bpy.data.texts.new('E11_30_TARGET_OBLIGATIONS_NOT_COMPLETION.json')
text.write(__import__('json').dumps({t:{'complete':False,'formal_art_accepted':False,'stage':'research_partial' if t in ['M247_C','W0','H1'] else 'not_authored_in_E11'} for t in targets},indent=2))
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'E11_INHABITED_SECTION_WORKING.blend'))
print('E11_R2_SAVED',len(S.objects),'TARGETS_UNFINISHED',len(targets))
