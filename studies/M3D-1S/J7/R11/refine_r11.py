"""Main-form revision after four real baseline views, applied in live Blender.

Replaces equal-height stacked canopies with continuous skewed inhabited folds;
opens two entire strata into a connected 1km+ civic sky fissure. Original B is retained.
This is a research study, not an accepted central city master.
"""
import bpy
import math
import json
import importlib.util
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r11',ROOT/'build_r11.py')
r=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
r.MODEL=bpy.data.collections['01_EDITABLE_ARCHITECTURE']
for key,prefix in [('ivory','01 |'),('silver','02 |'),('dark','03 |'),('gold','04 |'),
                   ('glass','05 |'),('light','06 |'),('warm','07 |'),('garden','09 |')]:
    found=next((m for m in bpy.data.materials if m.name.startswith(prefix)),None)
    r.MATS[key]=found or r.material(prefix+' research supplementary',(.10,.21,.17))


def curved_rows(stations):
    # Catmull-Rom interpolation of authored, unequal stations. No random macro shape.
    result=[]
    for i in range(len(stations)-1):
        a=stations[max(0,i-1)];b=stations[i];c=stations[i+1];d=stations[min(i+2,len(stations)-1)]
        for k in range(8):
            t=k/8
            result.append([.5*((2*b[j])+(-a[j]+c[j])*t+
                                (2*a[j]-5*b[j]+4*c[j]-d[j])*t*t+
                                (-a[j]+3*b[j]-3*c[j]+d[j])*t*t*t) for j in range(len(b))])
    result.append(stations[-1])
    return result


def fold(name,stations):
    # x, y-centre, base z, half plan depth, top z. Actual 180-700m inhabited thickness.
    samples=curved_rows(stations)
    rows=[]
    for x,y,z,w,top in samples:
        rows.append([(x,y-w,z),(x,y+w*.8,z+100),(x,y+w,top-30),
                     (x,y-w*.72,top),(x,y-w*1.05,top-110)])
    ob=r.loft(name,rows,'ivory',7)
    ob['design_role']='PRIMARY_REVISED_INHABITED_CITY_FOLD'
    # Three differently sized deep open galleries actually follow the fold's section.
    # They are floor volumes, not a window bitmap or a line on an opaque wall.
    for level in range(3):
        gallery=[]
        for x,y,z,w,top in samples:
            zz=z+(top-z)*(.22+level*.22)
            gallery.append([(x,y-w-105,zz),(x,y-w*.77,zz+35),
                            (x,y-w*.77,zz+47),(x,y-w-105,zz+12)])
        r.loft(name+' / recessed promenade '+str(level),gallery,'dark',2)
        r.tube(name+' / gallery edge '+str(level),[(v[0][0],v[0][1]-1,v[0][2]+15) for v in gallery],3,'gold')
        for k in range(0,len(samples),3):
            x,y,z,w,top=samples[k]
            zz=z+(top-z)*(.22+level*.22)
            r.beam(name+' / city pier '+str(level)+'.'+str(k),
                   (x,y-w-75,zz),(x+13,y-w-18,zz+90),9,21,'ivory')
    return ob


def apply_revision():
    removed=[];edited=[]
    # Remove the periodic structural solution and two whole occupied levels.
    for ob in list(r.MODEL.objects):
        name=ob.name
        kill=name.startswith(('B02','B20','B21','B30'))
        if name.startswith(('B01','B03','B04','B05')):
            tail=name.split()[-1]
            j=int(tail.split('.')[0])
            if j in [1,3]:
                kill=True
        if name.startswith('B10') and name.split()[-1] in ['2','3']:
            kill=True
        if kill:
            removed.append(name)
            bpy.data.objects.remove(ob,do_unlink=True)
    # Rework every retained district in world coordinates: unequal shear and twist.
    changes={0:(-4,-5,0,0),2:(-11,7,-240,-80),4:(-21,-8,-350,170),5:(-29,10,-460,200)}
    for ob in list(r.MODEL.objects):
        if not ob.name.startswith(('B01','B03','B04','B05')):continue
        j=int(ob.name.split()[-1].split('.')[0])
        ay,az,dx,dy=changes[j]
        z0=r.FAULTS[j][0]
        center=Vector((850,0,z0))
        rot=Matrix.Rotation(math.radians(az),4,'Z')@Matrix.Rotation(math.radians(ay),4,'Y')
        # Mesh coordinates from procedural boxes and beams have different transforms.
        mw=ob.matrix_world.copy()
        for v in ob.data.vertices:
            p=mw@v.co
            q=(rot@(p-center))+center+Vector((dx,dy,0))
            v.co=mw.inverted()@q
        edited.append(ob.name)
    # A continuous deep, bending city blade replaces six ordinary long roof slabs.
    fold('R01 | ascending inhabited western fold',[
        [-3100,680,80,150,350],[-2530,700,240,470,900],[-1780,900,730,700,1540],
        [-900,1080,1510,620,2210],[100,1120,2090,470,2810],
        [1170,1020,2610,300,3320],[2310,770,3070,120,3640],[2900,520,3420,28,3710]])
    fold('R02 | front continent fractures upward',[
        [-3000,-1110,80,100,310],[-2300,-1200,110,440,530],
        [-1350,-1260,170,590,760],[-320,-1190,240,540,1090],
        [670,-910,570,390,1610],[1480,-570,1210,250,2320],
        [2140,-140,2080,140,2920],[2600,250,2910,45,3450]])
    fold('R03 | back return living cliff',[
        [-1930,1390,110,120,490],[-1100,1540,300,370,1050],
        [-140,1550,900,440,1680],[930,1450,1470,390,2270],
        [1900,1220,2110,250,2840],[2660,900,2870,75,3380]])
    # 600m-deep overhead connection closes one end of the civic room while the other
    # end is sky-open: this is not a pair of isolated pillars.
    r.loft('R04 | civic vault inhabited cross-continent',[
        [(620,-820,1950),(1290,-600,2090),(1550,-530,2600),(840,-820,2570)],
        [(830,100,2250),(1530,200,2320),(1730,280,2850),(1020,70,2800)],
        [(1060,1000,2540),(1820,1060,2630),(2040,1100,3140),(1220,900,3080)]
    ],'ivory',9)
    # Native diagonal circulation penetrates the thickness of the return fold.
    for i,yy in enumerate([-700,350,1200]):
        pts=[(-2370,yy,125),(-1490,yy+120,620),(-500,yy+170,1310),
             (600,yy+100,2140),(1710,yy-80,2930),(2510,yy-260,3500)]
        r.tube('R10 | deep-city transit '+str(i),pts,12,'dark')
        r.tube('R11 | restrained guide light '+str(i),[(x,y,z+15) for x,y,z in pts],2,'light')
    # Nonperiodic roof light wells cut through the actual primary city folds.
    # Individual boolean mesh apertures admit light and expose the inhabited thickness.
    targets=[bpy.data.objects['R01 | ascending inhabited western fold'],
             bpy.data.objects['R02 | front continent fractures upward'],
             bpy.data.objects['R03 | back return living cliff']]
    cuts=[(-1730,880,1300,360,1300),(-230,1100,2350,420,1500),
          (-1450,-1200,600,290,1250),(300,-1040,1150,300,1500),
          (100,1500,1400,280,1450)]
    for i,(x,y,z,w,h) in enumerate(cuts):
        cutter=r.box('TEMP volumetric city lightwell',(x,y,z),(w,500,h),'dark')
        cutter.rotation_euler[1]=math.radians(-27)
        for target in targets:
            bpy.context.view_layer.objects.active=target
            mod=target.modifiers.new('true open lightwell '+str(i),'BOOLEAN')
            mod.operation='DIFFERENCE'
            mod.object=cutter
            bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
    # Add open, occupied substructure on a few large city cuts (not thousands of houses).
    for j,(x,y,z,w,d,h) in enumerate([(-2200,-1180,260,340,440,170),
            (-1620,-1150,520,420,460,220),(-920,-1060,780,350,430,200),
            (-210,760,1920,400,430,240),(520,900,2470,330,380,220),
            (1580,1080,2630,340,290,250)]):
        for lev in range(10):
            r.box('R20 | embedded city terrace %d.%d'%(j,lev),
                  (x+lev*7,y+lev*8,z+lev*h/10),(w-lev*9,d,7),'silver')
        for k in range(9):
            r.beam('R21 | city light court %d.%d'%(j,k),
                   (x-w/2+k*w/8,y-d/2,z),(x-w/2+k*w/8+60,y-d/2+75,z+h),
                   8,14,'gold' if k%3==0 else 'ivory')
    # A real human-scale viewing court inside the fault, connected to lower district.
    r.box('R30 | interior civic bridge',(-1100,-300,620),(580,380,22),'ivory')
    for y in [-480,-120]:
        r.tube('R31 | public bridge guard',[(-1380,y,632),(-820,y,632)],.07,'gold')
    scene=bpy.context.scene
    scene.name='R11_B_REVISED_NONCANONICAL_METERS'
    scene['revision']='Removed periodic canopies and complete levels 1/3; tilted city strata; new continuous inhabited folds and actual lightwell openings'
    scene.render.resolution_x=1440;scene.render.resolution_y=1100
    scene.cycles.samples=40
    bpy.context.view_layer.update()
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.clip_end=100000
                area.spaces.active.region_3d.view_distance=9500
                area.spaces.active.region_3d.view_location=(0,0,1700)
    folder=ROOT/'refined'
    r.save_exports(folder,'B_REFINED')
    record={'removed_objects':len(removed),'removed_names':removed,'edited_native_meshes':len(edited),
            'edited_names':edited,'edit_context':'LIVE_BLENDER_MCP',
            'based_on_visuals':['concept_B/01_FRONT.png','concept_B/02_OBLIQUE.png',
                              'concept_B/03_SIDE.png','concept_B/04_REAR.png'],
            'art_acceptance':'NOT_GRANTED','canonical_changes':False}
    (ROOT/'qa'/'main_form_revision.json').write_text(json.dumps(record,indent=2),encoding='utf8')
    print('LIVE R11 MAIN-FORM REVISION SAVED',len(removed),len(edited),flush=True)


if __name__=='__main__':
    apply_revision()
