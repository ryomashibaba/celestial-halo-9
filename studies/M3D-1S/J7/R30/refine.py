"""Observation-led R30 mesh edits. Always load saved R30, never an earlier original.
Revision 1 evidence is retained as six preview images; final BLEND is revision 2.
blender -b --python refine.py -- A|B
"""
import bpy, bmesh, sys,math
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import box,beam,path,surface,solid,deck,ribbon,tree,people,arcade,catmull
from mathutils import Vector
V=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.open_mainfile(filepath=str(g.R/f'model/R30_{V}.blend'))
g.materials()

def erase(name):
    o=bpy.data.objects.get(name)
    if o:g.CHANGES.append({'removed':name,'vertices':len(o.data.vertices)});g.remove(o)

def civic_cliff(name,x,y,z,w,d,h,turn=0):
    """A small metropolitan subvolume with clear public void, not a filled icon.
    Different cross-sections at every level; broad front stair street, two room flanks.
    """
    for side in (-1,1):
        rows=[]
        for k in range(9):
            t=k/8;zz=z+h*t
            xx=x+side*w*(.31-.13*t)+w*.10*math.sin(math.pi*t)
            ry=d*(.48-.16*t);rx=w*(.19-.07*t)
            rows.append([(xx-rx,y-ry,zz),(xx+rx,y-ry,zz),(xx+rx,y+ry,zz),(xx-rx,y+ry,zz)])
        solid(name+' inhabited flank '+str(side),rows,'recess')
        # Nonuniform civic landings; not every private floor needs a stripe.
        for t in (.0,.17,.39,.64,.88):
            zz=z+h*t;xx=x+side*w*(.31-.13*t)+w*.1*math.sin(math.pi*t)
            ww=w*(.43-.1*t);dd=d*(1.04-.25*t)
            deck(name+' inhabited terrace',[(xx-ww/2,y-dd/2),(xx+ww/2,y-dd/2),(xx+ww/2+18,y+dd/2),(xx-ww/2+18,y+dd/2)],zz,3,'porcelain')
            for q in (-1,1):
                beam(name+' facade supports',(xx+q*ww*.43,y-dd*.48,zz),(xx+q*ww*.35+12,y-dd*.42,zz+h*.14),2,3,'bronze')
        path(name+' continuous raked spine',[(x+side*w*.5,y+d*.48,z),(x+side*w*.37,y+d*.4,z+h*.6),(x+side*w*.23,y+d*.3,z+h)],7,11,'ivory',True)
    # A light open overhead blade, with a genuine skylit slot between the two wings.
    for side in (-1,1):
        rows=[]
        for i in range(17):
            t=i/16;xx=x-w*.5+w*t;zz=z+h*(.88+.20*math.sin(math.pi*t))
            rows.append([(xx,y+side*d*.10,zz),(xx,y+side*d*.56,zz-15)])
        surface(name+' roof halves '+str(side),rows,3,'ivory')
    deck(name+' public street floor',[(x-w/2,y-d/2),(x+w/2,y-d/2),(x+w/2,y+d/2),(x-w/2,y+d/2)],z,6,'ground')

def a():
    g.GROUP='A_REV2_INHABITED_EXCAVATIONS'
    # Through-cuts substantially alter front, back and the crest itself.
    west=['A west tidal wall']
    for label,poly in [
      ('A rear low civic breach',[(1540,390),(2300,390),(2530,690),(2370,1120),(1900,1040),(1540,790)]),
      ('A west high sloping light street',[(-250,1840),(320,1900),(760,2520),(660,2740),(300,2690),(-80,2250)]),
      ('A west north upper chamber',[(1600,1680),(2340,1680),(2540,2030),(2190,2590),(1800,2440),(1570,2090)])]:g.cut_portal(label,poly,'X',-2100,500,west)
    for label,poly in [
      ('A spine low north transit',[(2170,350),(2850,350),(2950,680),(2770,1070),(2430,990),(2200,700)]),
      ('A spine upper through court',[(1590,2460),(2290,2460),(2440,2880),(2220,3340),(1890,3220),(1650,2850)]),
      ('A spine crown split',[(2100,3470),(2230,3470),(2500,4270),(2170,4380),(2020,3930)])]:g.cut_portal(label,poly,'X',-1400,1200,['A north spine'])
    g.cut_portal('A countercrown inhabited light gap',[(2220,2620),(2790,2620),(2820,2990),(2620,3300),(2360,3250)],'X',-200,1700,['A split crown counterleaf'])
    g.cut_portal('A east rear public chamber',[(1420,550),(2170,550),(2440,1010),(2270,1350),(1820,1370),(1480,990)],'X',100,2100,['A estuary shoulder'])
    g.cut_portal('A east upper light street',[(800,1710),(1660,1710),(1880,2000),(1640,2210),(1160,2110)],'X',200,2000,['A estuary shoulder'])
    # New chamber floors are limited to the openings, not full rectangular plinths.
    for name,poly,z in [('A_REAR_390_FLOOR',[(-1520,1570),(-610,1570),(-440,2150),(-990,2470),(-1530,2230)],390),('A_SPINE_2460_FLOOR',[(-620,1630),(550,1650),(710,2180),(10,2370),(-640,2160)],2460),('A_EAST_1710_FLOOR',[(830,870),(1610,870),(1610,1550),(1080,1730),(780,1420)],1710)]:deck(name,poly,z,14,'ground')
    for name,x,y,z,w,d,h in [('A rear winter quarter',-1030,2080,390,420,440,300),('A crown public suspension',-100,1910,2460,510,480,360),('A east upper living cleft',1230,1270,1710,400,500,270),('A west canyon convergence',-930,740,1430,350,510,330)]:civic_cliff(name,x,y,z,w,d,h)
    # Carve back the giant blind cliff directly behind the human sightline.
    g.cut_portal('A low longitudinal civil passage',[(-430,105),(550,105),(730,630),(300,900),(-170,680)],'X',-600,650,['A north spine'])
    # Two intermediate-distance thresholds break the empty 2km basin without closing it.
    civic_cliff('A basin inhabited crossing',-530,180,105,280,300,250)
    civic_cliff('A sea threshold district',810,-430,105,340,380,310)
    ribbon('A rear-to-west public link',catmull([(-980,2010,390),(-1320,1280,570),(-1330,660,780)],13),42,8,'porcelain',True)
    for x,y,z in [(-980,1800,390),(-400,1780,2460),(1300,1080,1710),(-400,400,105)]:tree(x,y,z,24)
    people([(-1200,1800+i*30,390) for i in range(10)])
    # The old supports protruded above the roof: remove those unrelated construction lines.
    erase('A east sweeping ribs');erase('A crown raked folds')
    g.CHANGES.append({'visual_reason':'Revision 1 was an almost solid cliff with huge blank surfaces. Revision 2 cuts nine more large public/sky passages, splits crest, adds four metropolitan rooms, removes disconnected external ribs. Still an unfinished challenger.'})

def b():
    g.GROUP='B_REV2_OPENED_METROPOLITAN_BODY'
    # Cut apart the largest abstract upper blade. These are full-depth public worlds,
    # with sky breaks at the rising east end, not applied facade windows.
    for label,poly in [
      ('B upper west inhabited split',[(-1800,2120),(-1010,2180),(-650,2490),(-900,2720),(-1420,2590)]),
      ('B roof long public fault',[(-600,2690),(470,2820),(980,3110),(720,3220),(50,3080),(-500,2940)]),
      ('B upper eastern city sky mouth',[(1030,3150),(1910,3350),(2220,3680),(1920,3920),(1530,3750),(1190,3450)]),
      ('B bifurcated apical head',[(2030,3920),(2300,3790),(2610,4140),(2670,4570),(2240,4520)])]:
        # Faults excavate the seaward inhabited face, preserving a deep landward
        # city spine. Rev2 first attempt erroneously lost the upper mass.
        hi=1100 if 'long public' in label else 1850 if 'eastern city' in label else 4000
        g.cut_portal(label,poly,'Y',-2000,hi,['B inhabited horizon'])
    # Remove the flat aprons that read as shelves and replace them with streets
    # along inhabited rims and substantial underside sections.
    for name in ['B_HORIZON_2190_FLOOR','B_CENTRAL_930_FLOOR','B_EAST_1680_FLOOR','B_WEST_1000_FLOOR','B underside articulated spine','B high horizon longitudinal keel','B crest buttress']:erase(name)
    deck('B_WEST_1000_FLOOR',[(-2190,100),(-1820,0),(-1370,120),(-1170,460),(-1400,830),(-2030,1000),(-2250,600)],1000,20,'ground')
    deck('B_CENTRAL_930_FLOOR',[(-460,670),(-180,650),(520,1000),(620,1500),(280,1690),(-350,1390)],930,20,'ground')
    # An open forked high street outlines a real void where the broad platform was.
    ribbon('B_HORIZON_2190_FLOOR',catmull([(-790,330,2190),(-450,340,2190),(0,540,2190),(600,740,2190),(1100,1120,2190),(840,1610,2190),(40,1640,2190),(-500,1280,2190),(-790,330,2190)],10),120,20,'ground',True)
    deck('B_EAST_1680_FLOOR',[(1080,1610),(1440,1460),(1750,1620),(1730,2110),(1440,2300),(1110,2090)],1680,16,'ground')
    # Deep inhabited city keels integrate the grounds into the body; no little village
    # pasted onto an unchanged giant shelf.
    civic_cliff('B western metropolitan gorge',-1800,590,1000,520,570,520)
    civic_cliff('B hanging convergence district',-20,1240,930,470,530,450)
    civic_cliff('B eastern metropolitan lantern',1430,1930,1680,430,550,500)
    civic_cliff('B horizon inner city',100,1220,2190,570,630,610)
    # Make an entirely new 3020m urban room in the upper mass, with a real forked
    # floor and two unequal flanking public buildings.
    ribbon('B_UPPER_3020_FLOOR',catmull([(810,1000,3020),(1110,1160,3020),(1510,1430,3020),(1870,1760,3020)],12),220,26,'ground',True)
    civic_cliff('B upper eastern living terminus',1430,1640,3020,470,430,350)
    # The major western threshold is an intermediate-size public hall in the same
    # undercity as the grand suspended world: large but not the whole composition.
    civic_cliff('B landward civil confluence',-1170,100,105,540,600,450)
    civic_cliff('B waterward civil confluence',1030,350,105,460,540,390)
    # Replace the huge plain near-ground slab by multiple lobed quays with water cuts.
    g.flush()
    g.cut_portal('B tidal basin floor excavation',[(-1040,-90),(130,-90),(1080,-90),(1080,107),(800,107),(200,107),(-300,107),(-1040,107)],'Y',-900,-300,['B_REAL_LOW_FLOOR'])
    # The cut above is below/at the floor surface: retain only explicit public streets.
    g.GROUP='B_REV2_TIDAL_GROUNDS'
    deck('B_HUMAN_THRESHOLD_FLOOR',[(-500,-1830),(430,-1830),(670,-1380),(180,-1200),(-400,-1350)],105,12,'porcelain')
    ribbon('B public tide crossing',catmull([(100,-1530,105),(-330,-1250,105),(-820,-1040,105),(-1270,-780,105),(-1220,-140,105)],12),60,7,'porcelain',True)
    # Explicit underside keels converge with real buttress endpoints, unlike the
    # first version's visually free-floating loops.
    for pts,w in [([(-2300,700,400),(-1700,810,570),(-900,1120,950),(70,1420,950)],30),([(-1300,550,1200),(-700,750,1500),(100,1100,2080),(1100,1610,2660)],24),([(900,1840,1740),(1150,1930,1590),(1450,1980,1620)],28)]:
        path('B connected lower structural sweep',pts,w,w*1.5,'bronze',True)
    # Widely spaced longitudinal skin seams; no equal horizontal floor stack.
    for yoff in (-480,-230,130,410):
        path('B sculpted outer seam',catmull([(-2600,650+yoff*.3,640),(-1800,570+yoff*.7,2220),(-600,800+yoff,2850),(700,1330+yoff*.8,3270),(1700,1850+yoff*.6,3810)],13),6,10,'bronze')
    for x,y,z in [(-1530,180,1000),(-130,780,2190),(370,1100,2190),(1170,1350,3020),(1530,1630,3020),(-1050,-160,105)]:tree(x,y,z,28)
    # A real moving-scale foreground porch: slab underside does not fill the frame.
    arcade('B human waterside portico',-250,-1580,105,70,95,32,0)
    people([(50+i*7,-1620+i*12,105) for i in range(18)]+[(920+i*20,1140,3020) for i in range(8)])
    g.CHANGES.append({'visual_reason':'Revision 1 was a suspended weapon-like mass with empty shelf aprons. Revision 2 breaks upper blade into skyline faults, creates upper public world, replaces three aprons, integrates four deep city-room districts and a tidal ground sequence. B selected for further development, not formal adoption.'})

if V=='A':a()
elif V=='B':b()
else:raise ValueError(V)
g.flush()
# Record actual floor support before altering any camera. Matched cameras are held fixed.
sc=bpy.context.scene;bpy.context.view_layer.update()
for o in sc.objects:
    if o.type=='MESH' and o.name.startswith(('A west tidal wall','A estuary shoulder','A north spine','A split crown','B inhabited horizon','B lower lee','B west suspended','B central suspended','B eastern suspended')):
        # Flat section-to-section creases distracted from architectural order in v1.
        for p in o.data.polygons:p.use_smooth=True
        # weighted normals are avoided: GLB exports the very same edited geometry.
g.save(V,2)
