"""R30-A TIDAL RIFT / 潮裂聖都. R29 research-copy radical rebuild.
blender -b -t 6 --python build_a.py -- build|render|export [clay|art] [preview]
"""
import sys, math
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import box,beam,path,solid,surface,deck,ribbon,tree,people,arcade,catmull
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['build']

def escarpment(name,keys,material='ivory'):
    # Authored section coordinates: Y, base X, crest X, base Z, roof Z, thickness.
    rows=[]
    for y,xb,xt,zb,zt,w in catmull(keys,7):
        rows.append([(xb-w*.47,y,zb),(xb+w*.50,y,zb),(xb*.85+xt*.15+w*.48,y,zb+(zt-zb)*.22),(xt+w*.28,y,zt-30),(xt+w*.15,y,zt),(xt-w*.2,y,zt-5),(xt-w*.46,y,zt-100),(xb-w*.55,y,zb+(zt-zb)*.2)])
    solid(name,rows,material)

def rebuild():
    g.start('A');g.GROUP='A_WEST_LIVING_ESCARPMENT'
    escarpment('A west tidal wall',[(-1700,-1350,-1240,80,390,460),(-900,-1250,-1130,80,1050,600),(0,-1220,-820,70,2050,700),(950,-1140,-450,70,2990,730),(1900,-1050,-450,100,3070,670),(2800,-820,-620,170,2040,620),(3100,-600,-520,280,740,360)])
    # Secondary knuckle has a distinct low forward address and a concave sky court.
    escarpment('A estuary shoulder',[(-1350,1160,1270,80,320,470),(-600,1100,1080,80,760,600),(200,1030,1370,80,1620,620),(1000,930,1160,100,2300,700),(1900,720,1120,120,2530,680),(2570,650,850,210,1840,520)],'porcelain')
    g.GROUP='A_NORTH_FOLDED_SPINE'
    # The former needle is replaced by unequal folded inhabited blades, not enlarged rings.
    escarpment('A north spine',[ (900,-460,-280,110,1770,570),(1550,-310,110,100,3580,670),(2130,-250,160,110,4200,660),(2540,-170,320,150,3370,600),(2960,-50,180,260,2100,430)],'ivory')
    escarpment('A split crown counterleaf',[(1920,400,600,180,2410,350),(2310,410,840,180,3550,430),(2700,420,1030,240,3920,320),(2990,440,1050,350,2750,260)],'porcelain')
    g.flush()
    # Large diagonal mouths produce inhabited contours; the floor datums are independent.
    g.cut_portal('A 600m west sea mouth',[(-900,104),(-330,104),(230,740),(140,1020),(-240,1010),(-650,570)],'X',-2100,-200,['A west tidal wall'])
    g.cut_portal('A west upper city rift',[(300,1430),(1050,1430),(1470,1740),(1350,2090),(900,2150),(470,1880)],'X',-2200,100,['A west tidal wall'])
    g.cut_portal('A east civic fjord',[(-550,104),(250,104),(1000,940),(1030,1270),(650,1400),(100,1030)],'X',500,2200,['A estuary shoulder'])
    g.cut_portal('A sky passage through spine',[(1320,1250),(2220,1250),(2500,1700),(2150,2040),(1640,1860)],'X',-1400,1500,['A north spine','A split crown counterleaf'])
    g.GROUP='A_PRIMARY_CIVIC_GROUNDS'
    # A branched waterfront street, rather than one rectangular empty hall floor.
    deck('A_REAL_LOW_FLOOR',[(-620,-1880),(650,-1880),(980,-1200),(610,-750),(680,-200),(420,800),(-120,1530),(-850,940),(-900,-150),(-750,-940)],105,20,'ground')
    deck('A seaward terrace',[(350,-1200),(1510,-1550),(1860,-910),(1100,40),(580,180)],105,24,'porcelain')
    # An actual narrow canal, not the whole ceremonial apron.
    deck('A canal inlet',[(-90,-1885),(100,-1885),(170,-900),(100,50),(-70,830),(-160,350),(-60,-550)],105.15,1,'water')
    ribbon('A west processional street',catmull([(-530,-1840,105),(-430,-980,105),(-440,-250,105),(-570,520,105),(-600,1140,105)],9),95,4,'porcelain')
    # Terraces are strongly unequal. They are real interior street grounds inside the cuts.
    deck('A_WEST_780_FLOOR',[(-1510,-260),(-500,-260),(-350,60),(-630,710),(-1420,930)],780,14,'ground')
    deck('A_WEST_1430_FLOOR',[(-1430,280),(-450,330),(-250,990),(-510,1260),(-1500,1090)],1430,18,'ground')
    deck('A_EAST_805_FLOOR',[(760,-100),(1610,-100),(1630,600),(920,1050),(710,760)],805,18,'ground')
    deck('A_NORTH_1250_FLOOR',[(-650,1320),(870,1320),(950,2100),(400,2250),(-660,2000)],1250,20,'porcelain')
    # Raised destinations interrupt the canyon at different distances, without roofing it all.
    for label,pts,w in [('A high city causeway',[(-870,790,1430),(-400,940,1430),(240,1160,1250),(880,1610,1250)],65),('A estuary aerial arrival',[(1200,400,805),(1570,40,805),(1960,-540,804.5)],46),('A west garden arrival',[(-1210,540,780),(-1800,620,690),(-2240,670,674.5)],38)]:
        ribbon(label,catmull(pts,12),w,9,'porcelain',True)
        curve=catmull([(x,y,z-18) for x,y,z in pts],12)
        path(label+' underside keel',curve,12,30,'bronze')
    # Ground connections and 1:20 urban ascent.
    ribbon('A low-to-sea walk',catmull([(-430,-1700,105),(330,-1540,105),(1020,-1280,105),(1500,-1020,105)],10),40,4,'porcelain',True)
    ribbon('A garden slope',catmull([(-500,-1220,105),(-880,-650,140),(-1100,-120,170),(-1340,140,190)],9),30,7,'porcelain',True)
    g.GROUP='A_INHABITED_PUBLIC_ROOMS'
    # Three different interior orders: a lower open winter court, a tall bridge chamber,
    # and the top-lit sky commons which actually changes the shoulder silhouette.
    arcade('A winter exchange',-660,-620,105,180,270,92,1)
    arcade('A river craft chambers',740,-970,105,230,330,130,2)
    arcade('A west high commons',-920,760,1430,200,370,145,0)
    arcade('A estuary arrival court',1290,230,805,240,330,100,1)
    # A large room inside the west mouth; tall side volumes and a high tilted shell.
    deck('A_PUBLIC_ROOM_FLOOR',[(-1460,-720),(-640,-720),(-640,-300),(-1460,-300)],105,5,'porcelain')
    for i,(x,y,z,w,d,h) in enumerate([(-1330,-480,105,160,440,280),(-740,-540,105,150,300,170),(-1110,650,780,190,320,135)]):
        arcade('A embedded public house '+str(i),x,y,z,w,d,h,i%3)
    # Five strongly separated vertical circulation stacks with public landing mouths.
    for x,y,low,high in [(-620,420,105,1430),(840,1030,105,1250),(1520,570,105,805),(-1340,1050,780,1430)]:
        for dx in (-12,12):beam('A public lift ribs',(x+dx,y,low),(x+dx+high*.035,y+45,high),3,5,'bronze')
        for z in (low,high):
            box('A lift arrival chamber',(x+(z-low)*.035,y+45*(z-low)/max(1,high-low),z+8),(45,40,16),'recess')
            box('A lift public apron',(x+(z-low)*.035,y+45*(z-low)/max(1,high-low)-25,z-1),(65,60,2),'porcelain')
    g.GROUP='A_MAJOR_FACADE_ORDER'
    # Broad vertical folds and a few deeply recessed district bands replace 100+ storey stripes.
    for j in range(10):
        t=j/9;y=-1020+3400*t;h=700+2250*math.sin(math.pi*t)**.7
        xb=-1320+250*t;xt=-1150+650*math.sin(math.pi*t)
        path('A west rising buttress',[(xb-250,y,110),(xb-200,y+90,h*.32),(xt-260,y+50,h*.78),(xt-170,y,h)],18,30,'ivory',True)
        path('A west bronze reveals',[(xb-267,y+12,120),(xb-218,y+102,h*.32),(xt-277,y+62,h*.78),(xt-187,y+12,h)],3,8,'bronze',True)
    for j in range(6):
        y=-550+j*490;h=900+1500*math.sin((j+1)*math.pi/7)
        path('A east sweeping ribs',[(1530,y,120),(1630,y+120,h*.5),(1440,y+120,h)],18,28,'porcelain',True)
    # Crown fluting is sparse and asymmetric, not floors repeated to the top.
    for j in range(7):
        yy=1400+j*200
        path('A crown raked folds',[(-650,yy,1800),(-190,yy+160,2850),(190,yy+220,3780-j*65)],14,22,'ivory',True)
    # Habitation is represented by deep actual room bars at the great openings,
    # with multiple local scales; this is not full private/public interior completion.
    for j in range(9):
        yy=320+j*96;zz=1430
        arcade('A upper canyon neighbourhood '+str(j),-1180,yy,zz,86+(j%3)*14,68+(j%2)*18,55+(j%4)*16,j%3)
    for j in range(7):
        yy=-630+j*100;xx=-400+35*math.sin(j)
        arcade('A water street address '+str(j),xx,yy,105,80+(j%3)*15,75,36+(j%4)*15,(j+1)%3)
    # A selectively retained open sky arc ties two unequal crowns, never a closed roof.
    path('A crown arc',catmull([(-660,1740,2690),(-670,1280,3110),(0,1000,3500),(930,1730,3700)],16),22,28,'bronze')
    g.GROUP='A_LIVED_THRESHOLD'
    # Deliberately limited human evidence: close buildings, raised edges, a planted rill,
    # an intermediate 200m room and the 3km distant crest are all in the same geometry.
    arcade('A foreground crossing house',-210,-1480,105,80,140,44,1)
    arcade('A sea stair house',420,-1400,105,105,160,68,0)
    for x,y in [(-300,-1570),(320,-1530),(-390,-1200),(-390,-1010),(550,-1090),(700,-1060),(-900,-650),(-1170,690),(1320,80)]:tree(x,y,1430 if y==690 else 805 if x==1320 else 105,19)
    people([(100+i*4,-1480+i*15,105) for i in range(12)]+[(-450,-710+i*40,105) for i in range(12)]+[(-1100,480+i*30,1430) for i in range(8)])
    railpts=[(210,-1700,105),(190,-1370,105),(230,-1110,105)]
    g.rail('A canal bank handrail',railpts)
    for y in range(-1650,-1200,35):box('A waterfront seats',(260,y,105.45),(6,1.2,.9),'bronze')
    g.flush();g.setup_lighting();cameras();g.save('A',1)

def cameras():
    for a in [('01_CITY',(11000,-15000,11000),(0,800,1500),43,None),('02_CENTRAL',(5300,-7000,3500),(0,800,1800),38,None),('03_PUBLIC',(-1010,-670,106.7),(-720,730,440),24,'A_PUBLIC_ROOM_FLOOR'),('04_HUMAN',(100,-1650,106.7),(-120,1400,700),25,'A_REAL_LOW_FLOOR'),('05_REAR',(5300,6200,3500),(0,1100,1700),40,None),('06_UNDERSIDE',(3500,3300,650),(0,1000,1600),29,None),('07_SKY_STREET',(-910,500,1431.7),(950,1150,1400),27,'A_WEST_1430_FLOOR')]:g.camera(*a)

if __name__=='__main__':
    if ARGS[0]=='build':rebuild()
    elif ARGS[0]=='export':g.export('A')
    elif ARGS[0]=='render':g.render('A','art' if 'art' in ARGS else 'clay','preview' in ARGS,names=[n for n in ARGS if n[:2].isdigit()] or None)
