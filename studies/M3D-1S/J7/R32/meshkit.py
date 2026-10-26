"""R32 copy of low-level editable mesh vocabulary; no old generators run.
All coordinates are relative study metres. Output paths limited to R32.
"""
import bpy, bmesh, math, random, json, sys
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
for p in ('model','renders','process','comparison','qa'): (R/p).mkdir(exist_ok=True)
BATCH={}; GROUP='R32'; MATS={}; CHANGES=[]

def record(path,data):
    (R/path).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')

def mat(name,rgb,metal=0,rough=.5,emission=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    p.inputs['Emission Color'].default_value=(*rgb,1);p.inputs['Emission Strength'].default_value=emission
    MATS[name]=m

def materials():
    for a in [('ivory',(.68,.72,.71),.24,.4),('porcelain',(.82,.80,.70),.1,.5),('basalt',(.035,.065,.083),.38,.48),('recess',(.08,.15,.17),.5,.32),('bronze',(.32,.22,.11),.64,.36),('ground',(.28,.32,.31),.1,.7),('garden',(.11,.20,.16),0,.85),('light',(.38,.78,.86),.15,.25,2),('human',(.21,.105,.06),.05,.7),('clay',(.52,.55,.55),.06,.75)]:mat(*a)

def add(name,vs,fs,material='ivory'):
    v,f=BATCH.setdefault((GROUP,name,material),([],[]));off=len(v)
    v.extend(tuple(p) for p in vs);f.extend(tuple(off+i for i in face) for face in fs)

def box(name,c,d,material='ivory',angle=0):
    x,y,z=c;a,b,h=[v/2 for v in d];co,si=math.cos(angle),math.sin(angle)
    vs=[(x+u*co-v*si,y+u*si+v*co,z+w) for w in [-h,h] for u,v in [(-a,-b),(a,-b),(a,b),(-a,b)]]
    add(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material)

def beam(name,a,b,w,d,material='ivory'):
    a,b=Vector(a),Vector(b);t=(b-a).normalized();u=t.cross(Vector((0,0,1)))
    if u.length<.01:u=Vector((1,0,0))
    u.normalize();v=t.cross(u)*d/2;u*=w/2
    vs=[p+s*u+q*v for p in (a,b) for s,q in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    add(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material)

def catmull(points,sub=10):
    pts=[Vector(p) for p in points];out=[]
    for i in range(len(pts)-1):
        a,b,c,d=pts[max(i-1,0)],pts[i],pts[i+1],pts[min(i+2,len(pts)-1)]
        for j in range(sub):
            t=j/sub
            out.append(tuple(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)))
    out.append(tuple(pts[-1]));return out

def path(name,points,w,d,material='ivory',smooth=False):
    if smooth:points=catmull(points,8)
    for a,b in zip(points,points[1:]):beam(name,a,b,w,d,material)

def solid(name,sections,material='ivory',smooth=True):
    n,m=len(sections),len(sections[0]);vs=[p for row in sections for p in row];fs=[]
    for i in range(n-1):
        for j in range(m):fs.append((i*m+j,i*m+(j+1)%m,(i+1)*m+(j+1)%m,(i+1)*m+j))
    fs += [tuple(reversed(range(m))),tuple((n-1)*m+j for j in range(m))]
    add(name,vs,fs,material)

def surface(name,rows,thick=8,material='ivory'):
    n,m=len(rows),len(rows[0]);vs=[p for row in rows for p in row];off=len(vs)
    vs += [(x,y,z-thick) for x,y,z in vs];fs=[]
    for i in range(n-1):
        for j in range(m-1):
            a=i*m+j;b=a+m;fs.extend([(a,a+1,b+1,b),(a+off,b+off,b+1+off,a+1+off)])
        for j in (0,m-1):
            a=i*m+j;b=a+m;fs.append((a,b,b+off,a+off))
    for i in (0,n-1):
        for j in range(m-1):
            a=i*m+j;fs.append((a,a+off,a+1+off,a+1))
    add(name,vs,fs,material)

def deck(name,outline,z,depth=8,material='ground'):
    n=len(outline);vs=[(x,y,z-depth) for x,y in outline]+[(x,y,z) for x,y in outline]
    fs=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    add(name,vs,fs,material)

def ribbon(name,points,width=25,thick=4,material='porcelain',rails=False):
    rows=[]
    for i,p in enumerate(points):
        a=Vector(points[max(0,i-1)]);b=Vector(points[min(len(points)-1,i+1)])
        u=Vector((-(b-a).y,(b-a).x,0)).normalized()*width/2;p=Vector(p)
        rows.append([tuple(p-u),tuple(p+u)])
    surface(name,rows,thick,material)
    if rails:
        for k in (0,1):rail(name+' guard', [row[k] for row in rows])

def rail(name,pts):
    path(name,[(x,y,z+1.1) for x,y,z in pts],.18,.22,'bronze')
    for a,b in zip(pts,pts[1:]):
        a,b=Vector(a),Vector(b);steps=max(1,int((b-a).length/6))
        for i in range(steps):
            p=a.lerp(b,i/steps);box(name+' posts',p+Vector((0,0,.55)),(.14,.14,1.1),'bronze')

def tree(x,y,z,s=15):
    beam('tree stems',(x,y,z),(x,y,z+s*.65),s*.04,s*.04,'bronze')
    for k in range(3):
        rr=s*(.32-.06*k);zz=z+s*(.56+k*.15);n=9
        vs=[(x+rr*math.cos(i*math.tau/n),y+rr*math.sin(i*math.tau/n),zz) for i in range(n)]+[(x,y,zz+s*.21),(x,y,zz-s*.15)]
        add('canopy foliage',vs,[(i,(i+1)%n,n) for i in range(n)]+[(i,n+1,(i+1)%n) for i in range(n)],'garden')

def people(pts):
    for x,y,z in pts:
        box('human scale witnesses',(x,y,z+.99),(.4,.25,1.22),'human')
        box('human scale heads',(x,y,z+1.66),(.25,.24,.28),'human')
        for dx in (-.12,.12):box('human scale legs',(x+dx,y,z+.33),(.12,.14,.66),'human')

def arcade(name,x,y,z,w,d,h,style=0):
    # A deliberately open building: separate rooms at the sides and a real public aisle.
    box(name+' street floor',(x,y,z-1),(w,d,2),'porcelain')
    for side in (-1,1):
        box(name+' occupied flank',(x+side*w*.36,y,z+h*.42),(w*.23,d,h*.84),'recess')
        for k in range(1,4):box(name+' gallery',(x+side*w*.29,y,z+k*h*.21),(w*.36,d+4,1.3),'ivory')
    if style==0:
        rows=[]
        for j in range(13):
            yy=y-d/2+d*j/12
            rows.append([(x+(i/20-.5)*w*1.12,yy,z+h*.66+h*.35*(1-(2*i/20-1)**2)) for i in range(21)])
        surface(name+' lenticular roof',rows,2,'ivory')
    elif style==1:
        surface(name+' folded roof',[[(x-w*.6,y-d*.55,z+h),(x,y-d*.55,z+h*1.35),(x+w*.6,y-d*.55,z+h*.72)],[(x-w*.6,y+d*.55,z+h*.8),(x,y+d*.55,z+h),(x+w*.6,y+d*.55,z+h*.6)]],3,'porcelain')
    else:
        box(name+' planted roof',(x,y,z+h),(w+8,d+8,3),'garden')
        for yy in (y-d*.3,y+d*.3):tree(x,yy,z+h+1.5,12)
    for xx in (x-w*.48,x+w*.48):
        for j in range(6):
            yy=y-d/2+j*d/5
            beam(name+' portal piers',(xx,yy,z),(xx+(.12*w if xx<x else -.12*w),yy,z+h),1.8,2.4,'bronze')

def flush():
    result=[]
    for (group,name,material),(vs,fs) in BATCH.items():
        me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
        ob=bpy.data.objects.new(name,me);co=bpy.data.collections.get(group)
        if co is None:co=bpy.data.collections.new(group);bpy.context.scene.collection.children.link(co)
        co.objects.link(ob);me.materials.append(MATS.get(material) or bpy.data.materials[material])
        ob['study_group']=group;ob['provenance']='R32 relative metre study, not canonical'
        result.append(ob)
    BATCH.clear();return result

def remove(o):bpy.data.objects.remove(o,do_unlink=True)

def camera(name,pos,target,lens=36,support=None):
    ob=bpy.data.objects.new(name,bpy.data.cameras.new(name))
    bpy.context.scene.collection.objects.link(ob)
    ob.location=pos
    ob.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler()
    ob.data.lens=lens;ob.data.clip_start=.1;ob.data.clip_end=120000
    ob['target_m']=list(target);ob['support_floor']=support or ''
    return ob

def setup_gpu_only():
    try:
        cp=bpy.context.preferences.addons['cycles'].preferences;cp.compute_device_type='OPTIX';cp.get_devices()
        for d in cp.devices:d.use=d.type=='OPTIX'
        bpy.context.scene.cycles.device='GPU'
    except Exception:bpy.context.scene.cycles.device='CPU'
