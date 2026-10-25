"""Third spatial sketch after A/B actual image rejection: excavated city lands.
Each district is sculpted around several differently sized open public caverns.
"""
import bpy,bmesh,math,json,sys
sys.dont_write_bytecode=True
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
import build_r13 as H
ROOT=Path(__file__).parent

def loft(name,levels,mat):
    n=len(levels[0][1]);verts=[(x,y,z) for z,poly in levels for x,y in poly]
    faces=[tuple(reversed(range(n))),tuple(range((len(levels)-1)*n,len(levels)*n))]
    for k in range(len(levels)-1):
        for i in range(n):faces.append((k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i))
    return H.mesh(name,verts,faces,mat)

def carve(ob,cutter):
    # Exact booleans must receive outward, triangulated solids. Long warped
    # loft quads and coincident cave edges otherwise produced invalid faces.
    def clean(obj):
        obj.data.validate(verbose=False)
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001)
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.00001)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bmesh.ops.triangulate(bm,faces=list(bm.faces))
        bm.to_mesh(obj.data);bm.free();obj.data.update()
    clean(ob);clean(cutter)
    low=[min(v.co[i] for v in ob.data.vertices) for i in range(3)]
    high=[max(v.co[i] for v in ob.data.vertices) for i in range(3)]
    bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('True carved public volume','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    ob.modifiers.move(ob.modifiers.find(mod.name),0)
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
    clean(ob)
    for v in ob.data.vertices:
        if any(v.co[i]<low[i]-.02 or v.co[i]>high[i]+.02 for i in range(3)):
            raise RuntimeError('DIFFERENCE enlarged source bounds: '+ob.name)

def portal(name,center,rx,ry,height,axis='Y',skew=0):
    # Six-sided inhabited urban canyon, not an image's dark patch.
    x,y,z=center
    profile=[(-rx,0),(rx,0),(rx*.95,height*.62),(rx*.45,height),(-rx*.58,height*.95),(-rx,height*.52)]
    v=[]
    for d in (-ry,ry):
        for u,h in profile:
            if axis=='Y':v.append((x+u+skew*h,y+d,z+h))
            else:v.append((x+d,y+u+skew*h,z+h))
    n=6;faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    if axis=='Y':faces=[tuple(reversed(f)) for f in faces]
    return H.mesh(name,v,faces,None)

PLAN=[(-.8,-1),(.2,-1),(1,-.4),(.82,.65),(.25,1),(-.8,.73),(-1,.1),(-.92,-.65)]
def land(name,center,size,levels,spaces):
    x,y,z=center;rx,ry=size
    polys=[]
    for dz,sx,sy,dx,dy in levels:
        polys.append((z+dz,[(x+a*rx*sx+dx,y+b*ry*sy+dy) for a,b in PLAN]))
    ob=loft(name+'__inhabited_land',polys,H.PEARL);ob['district']=name
    # The public chambers generate the outer silhouette/porosity.
    for j,(cx,cy,cz,r,d,h,axis,skew) in enumerate(spaces):
        cut=portal('temporary_civic_void',(x+cx,y+cy,z+cz),r,d,h,axis,skew);carve(ob,cut)
        H.DISTRICTS.append(dict(label=name+f'_space_{j}',role='CIVIC_CAVERN',origin_m=[x+cx,y+cy,z+cz],nominal_width_m=2*r,nominal_depth_m=2*d,nominal_height_m=h,axis=axis))
    bevel=ob.modifiers.new('Ceramic erosion of inhabited edges','BEVEL');bevel.width=9;bevel.segments=2
    return ob

def build_C():
    H.setup()
    land('C01_WEST_DEEP',(-1650,220,0),(1100,1120),
         [(0,1,1,0,0),(900,1.07,.95,100,0),(2150,.87,.94,90,130),(3400,.72,.78,320,170),(4550,.45,.62,500,230)],
         [(0,0,180,570,1800,870,'Y',.05),(160,0,1430,470,1800,950,'Y',-.1),(350,60,2760,370,1800,1050,'Y',.1),
          (100,40,860,440,1600,620,'X',.13),(240,0,2170,360,1600,550,'X',-.1)])
    land('C02_EAST_TIDELAND',(1550,390,0),(1130,1230),
         [(0,1,1,0,0),(700,1.12,1.05,-150,30),(1650,.92,.95,-200,100),(2600,.88,.75,-420,200),(3510,.56,.65,-650,180)],
         [(0,0,200,600,1900,1050,'Y',-.10),(-220,0,1660,480,1900,1090,'Y',-.15),
          (0,0,1000,470,1700,680,'X',0)])
    land('C03_REAR_ARCHIVE',(-100,1630,0),(1400,940),
         [(0,.95,1,0,0),(1000,1.04,1,0,0),(2200,.88,.87,0,-50),(3200,.78,.86,-40,-50),(4240,.72,.61,-160,-20)],
         [(0,0,220,810,1600,1300,'Y',.08),(0,0,1910,640,1700,1100,'Y',-.05),
          (0,0,1060,420,1900,800,'X',0)])
    land('C04_CONFLUENCE_SKY',(-130,650,3050),(1700,920),
         [(0,1,.9,0,0),(500,.9,1,0,40),(1100,.75,.8,-120,30),(1510,.5,.58,-260,150)],
         [(0,0,160,850,1800,850,'Y',-.2),(0,0,320,390,2300,660,'X',.0)])
    # Two low inhabited lands shape the approach rather than an applied podium.
    land('C05_INNER_SEED',(-1100,-950,0),(1100,750),
         [(0,1,1,0,0),(480,.92,.94,30,0),(990,.7,.72,130,60)],
         [(0,0,140,490,1400,590,'Y',0)])
    land('C06_TIDAL_APPROACH',(1250,-920,0),(1050,750),
         [(0,1,1,0,0),(420,1,.92,-80,40),(790,.7,.72,-50,70)],
         [(0,0,100,470,1400,490,'Y',-.1)])
    # Real waters and broad land surfaces inside, not surface house decorations.
    for name,poly,z in [
        ('Lower confluence water',[(-760,-1300),(640,-1150),(900,1000),(-650,1000)],45),
        ('Upper tidal world',[(-2050,-300),(-1200,-300),(-1100,950),(-1900,1050)],1470),
        ('East inner sea',[(1000,-100),(1800,-100),(1900,1200),(1100,1200)],1690)]:
        H.prism(name,poly,z,z+10,H.WATER)
    # Deliberate public landscape ledges opening into caverns, 150-700m, not equal floors.
    for name,poly,z0,z1,mat in [
        ('West suspended cultivation',[(-1980,-680),(-1350,-640),(-1270,-100),(-1730,100)],1550,1630,H.GREEN),
        ('East collective ground',[(920,-340),(1550,-450),(1850,40),(1180,330)],1810,1900,H.STONE),
        ('High confluence common',[(-470,350),(360,450),(580,1150),(-350,1250)],3250,3340,H.BRONZE),
        ('Rear deep cultivation',[(-750,1150),(400,1080),(680,1760),(-700,1930)],2260,2335,H.GREEN)]:
        H.prism(name,poly,z0,z1,mat,8)

if __name__=='__main__':
    build_C();H.save(ROOT/'exploration_C','R13_C');H.render(ROOT/'exploration_C')
