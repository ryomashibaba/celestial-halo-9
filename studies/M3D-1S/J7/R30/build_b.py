"""R30-B SUSPENDED SEA / 懸海天都. Independently authored horizontal civilisation.
Starts empty; R29 supplies common terrain and context assets only, never central geometry.
"""
import sys,math
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
from geometry import box,beam,path,solid,surface,deck,ribbon,tree,people,arcade,catmull
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['build']

def continent(name,keys,material='ivory'):
    # Unique B grammar: a lateral body with unequal upper/lower inhabited lobes.
    # X, centre Y, bottom Z, top Z, half depth. Its silhouette is not A's vertical walls.
    rows=[]
    for x,y,zb,zt,w in catmull(keys,10):
        h=zt-zb
        rows.append([(x,y-w*.40,zb),(x,y-w*.86,zb+h*.19),(x,y-w,zb+h*.53),(x,y-w*.82,zt-h*.14),(x,y-w*.35,zt),(x,y+w*.44,zt-h*.04),(x,y+w*.90,zt-h*.24),(x,y+w,zb+h*.32),(x,y+w*.47,zb+h*.05)])
    solid(name,rows,material)

def pendant(name,x,y,z,w,depth,drop,shift):
    rows=[]
    for t in range(31):
        q=t/30;zz=z-drop*q;cx=x+shift*q*q;cy=y+q*130
        rx=w*(1-.64*q);ry=depth*(1-.47*q)
        rows.append([(cx+rx*math.copysign(abs(math.cos(a))**.6,math.cos(a)),cy+ry*math.copysign(abs(math.sin(a))**.6,math.sin(a)),zz) for a in [i*math.tau/16 for i in range(16)]])
    solid(name,rows,'porcelain')

def rebuild():
    g.start('B');g.GROUP='B_SUSPENDED_CONTINENT'
    continent('B inhabited horizon',[(-2850,700,120,490,230),(-2400,620,270,1300,430),(-1730,550,960,2350,700),(-700,770,1720,2900,830),(300,1130,2180,3250,850),(1250,1550,2540,3570,670),(2070,1970,3200,4050,430),(2530,2360,3850,4310,150)],'ivory')
    # The lower lee world threads BELOW the horizon, rather than another floor on top.
    continent('B lower lee inhabited reach',[(-2520,1120,110,480,270),(-1700,1270,220,1220,650),(-580,1600,720,1740,760),(450,2020,1210,2080,600),(1300,2510,1640,2270,360),(1870,2800,1990,2350,120)],'porcelain')
    g.GROUP='B_HANGING_CITY_BUTTRESSES'
    pendant('B west suspended city',-1470,580,1870,370,380,1360,-420)
    pendant('B central suspended city',-150,1270,2340,440,500,1430,310)
    pendant('B eastern suspended city',1270,1680,3030,320,390,1540,280)
    g.flush()
    # Long inhabited lateral chambers cut through the solid body. Different shapes/heights
    # are deliberately specified for each; no A wings, circle or public-hall inheritance.
    g.cut_portal('B west public sky cavern',[(-2200,1000),(-1370,1000),(-800,1700),(-1050,2040),(-1670,2010),(-2090,1580)],'Y',-900,2200,['B inhabited horizon','B west suspended city'])
    g.cut_portal('B horizon civic aperture',[(-850,2190),(800,2190),(1330,2630),(980,2960),(0,2900),(-620,2600)],'Y',-900,2800,['B inhabited horizon'])
    g.cut_portal('B central pendulum room',[(-430,930),(470,930),(620,1370),(270,1710),(-210,1610),(-470,1260)],'Y',300,2500,['B central suspended city','B lower lee inhabited reach'])
    g.cut_portal('B eastern folded chamber',[(1040,1680),(1670,1680),(1730,2070),(1430,2450),(1190,2300)],'Y',500,3000,['B eastern suspended city','B lower lee inhabited reach'])
    g.GROUP='B_CIVIL_GROUNDS_AND_WATER'
    deck('B_REAL_LOW_FLOOR',[(-2100,-1650),(300,-1880),(1450,-1280),(1490,-500),(680,50),(-180,610),(-1080,700),(-1990,80)],105,20,'ground')
    # A broad negative water space cuts into the urban basin; walks branch around it.
    deck('B tidal public water',[(-1000,-850),(-100,-1160),(970,-810),(1090,-380),(200,240),(-910,180)],106,1,'water')
    ribbon('B inhabited shore street',catmull([(-1450,-1510,105),(-1350,-800,105),(-1360,100,105),(-890,700,105),(-300,900,105)],12),90,6,'porcelain',True)
    ribbon('B east tidal route',catmull([(80,-1710,105),(650,-1330,105),(1250,-870,105),(1370,-220,105),(900,400,105)],10),100,7,'porcelain',True)
    ribbon('B basin diagonal bridge',catmull([(-1230,-480,105),(-800,-330,110),(0,-100,130),(780,240,105)],14),42,7,'ivory',True)
    # Four actual public worlds live inside the sculpted apertures.
    deck('B_WEST_1000_FLOOR',[(-2210,170),(-1130,-60),(-970,750),(-1460,1060),(-2220,700)],1000,16,'ground')
    deck('B_CENTRAL_930_FLOOR',[(-480,650),(610,650),(640,1660),(160,1870),(-480,1450)],930,18,'ground')
    deck('B_HORIZON_2190_FLOOR',[(-860,250),(1120,610),(1040,1680),(0,1870),(-850,1270)],2190,24,'ground')
    deck('B_EAST_1680_FLOOR',[(1020,1450),(1780,1450),(1780,2230),(1060,2360)],1680,16,'ground')
    # Suspended avenues are not isolated shelves: both ends enter actual civic voids.
    ribbon('B west-to-central avenue',catmull([(-1280,610,1000),(-730,650,980),(-170,790,930),(380,1100,930)],15),62,12,'porcelain',True)
    ribbon('B central-to-east avenue',catmull([(430,1420,930),(700,1540,1180),(1070,1710,1500),(1400,1830,1680)],12),54,12,'porcelain',True)
    # Vertical transport is architectural equipment only; no operation certification.
    for x,y,z0,z1 in [(-1500,620,105,1000),(310,1500,930,2190),(1600,1880,1680,2900)]:
        for dx in (-20,20):path('B lift gantries',[(x+dx,y,z0),(x+dx+90,y+30,z1)],4,8,'bronze')
        for zz in [z0,z1]:
            box('B elevator public portal',(x+(90 if zz==z1 else 0),y+(30 if zz==z1 else 0),zz+10),(58,55,20),'recess')
            box('B elevator apron',(x+(90 if zz==z1 else 0),y-25+(30 if zz==z1 else 0),zz-2),(90,100,4),'porcelain')
    # Connections to the same provisional surrounding sky studies, with a different network.
    for name,pts,w in [('B harbor connector',[(1620,1830,1680),(2120,1200,1300),(2400,200,1000),(2160,-580,804.5)],46),('B northern observatory connector',[(700,1600,2190),(640,2100,2070),(610,2850,1894.5)],40),('B west garden connector',[(-2200,610,1000),(-2550,650,780),(-2700,700,674.5)],38)]:ribbon(name,catmull(pts,14),w,10,'ivory',True)
    g.GROUP='B_PUBLIC_INTERIORS'
    # Ground-level tidal forum is a city plaza below a 1km suspended neighbourhood.
    arcade('B shore civic threshold',-1510,-480,105,240,350,170,1)
    arcade('B undertide exchange',-550,700,105,320,240,190,0)
    arcade('B horizon convergence house',270,1110,2190,340,450,260,1)
    arcade('B low cloud court',30,1410,930,250,320,165,2)
    arcade('B hanging eastern atrium',1420,1960,1680,240,350,180,0)
    for i in range(7):
        x=-2000+i*130;y=450+80*math.sin(i*.8)
        arcade('B western sky address '+str(i),x,y,1000,95+(i%3)*23,140,74+(i%4)*30,i%3)
    # A long 2190m city street with variable side rooms; the overhead mass remains open.
    for i,(x,y,w,d,h) in enumerate([(-710,1090,150,240,120),(-420,1380,210,170,220),(30,1510,240,260,160),(520,1440,180,310,260),(900,1110,160,200,180)]):
        arcade('B horizon public neighbourhood '+str(i),x,y,2190,w,d,h,(i+1)%3)
    g.GROUP='B_OUTER_ARCHITECTURAL_ORDER'
    # A few immense structural strakes follow the longitudinal bodily flow. They break
    # at the mouths rather than filling them with copied horizontal floor stripes.
    for j in range(6):
        q=j/5;yoff=-480+j*180
        path('B high horizon longitudinal keel',catmull([(-2570,650+yoff*.28,550),(-1780,580+yoff*.6,2250),(-700,770+yoff*.9,2860),(350,1140+yoff,3220),(1350,1620+yoff*.7,3590),(2390,2250+yoff*.2,4200)],12),12+j%2*3,18,'porcelain')
    for x,y,z,w,h in [(-1830,230,1220,330,800),(-1070,520,2230,440,550),(620,900,2890,440,380),(1680,1660,3540,320,350)]:
        # Deep open slots along the crest are physical gaps between louvres.
        for j in range(11):
            xx=x-w/2+j*w/10
            path('B crest buttress',( (xx,y,z),(xx+90,y+40,z+h*.8),(xx+120,y+70,z+h)),8,18,'ivory')
    # Unequal underside ribs communicate depth, and deliberately remain visible in rear QA.
    for j in range(8):
        x=-1350+j*400;yy=700+(x+1300)*.29;zz=1250+(x+1300)*.42
        path('B underside articulated spine',catmull([(x,yy-360,zz+200),(x+150,yy-100,zz-60),(x+200,yy+330,zz-100),(x+100,yy+640,zz+200)],8),18,32,'bronze')
    g.GROUP='B_LIVED_THRESHOLD'
    # Foreground architecture has its own solid rooms and entrances, no image billboards.
    arcade('B foreground water house',-150,-1510,105,110,170,66,2)
    arcade('B forecourt transit house',500,-1390,105,140,230,108,1)
    for x,y,z in [(-320,-1510,105),(350,-1550,105),(-1330,-700,105),(-1390,-330,105),(1000,-920,105),(-1650,250,1000),(-1400,360,1000),(-250,500,2190),(500,800,2190)]:tree(x,y,z,22)
    people([(120+i*4,-1660+i*17,105) for i in range(14)]+[(-1700+i*25,390,1000) for i in range(10)]+[(-170+i*30,800,2190) for i in range(10)])
    for y in range(-1630,-1300,35):box('B shore seats',(310,y,105.45),(7,1.3,.9),'bronze')
    g.flush();g.setup_lighting();cameras();g.save('B',1)

def cameras():
    for a in [('01_CITY',(11000,-15000,11000),(0,800,1500),43,None),('02_CENTRAL',(5300,-7000,3500),(0,800,1800),38,None),('03_PUBLIC',(-1760,210,1001.7),(-720,770,1500),24,'B_WEST_1000_FLOOR'),('04_HUMAN',(100,-1650,106.7),(-120,1400,700),25,'B_REAL_LOW_FLOOR'),('05_REAR',(5300,6200,3500),(0,1100,1700),40,None),('06_UNDERSIDE',(3500,3300,650),(0,1000,1600),29,None),('07_SKY_STREET',(-380,700,2191.7),(1050,1260,2500),27,'B_HORIZON_2190_FLOOR')]:g.camera(*a)

if __name__=='__main__':
    if ARGS[0]=='build':rebuild()
    elif ARGS[0]=='export':g.export('B')
    elif ARGS[0]=='render':g.render('B','art' if 'art' in ARGS else 'clay','preview' in ARGS,names=[n for n in ARGS if n[:2].isdigit()] or None)
