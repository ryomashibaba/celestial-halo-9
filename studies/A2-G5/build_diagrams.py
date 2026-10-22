"""G5 conceptual diagrams only. No 3D geometry or registered masterplan."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import html, json, math

ROOT=Path(__file__).resolve().parent
BG='#101c29'; PANEL='#182a39'; INK='#e8edf0'; MUTED='#a9bdca'
GOLD='#edc67d'; TEAL='#79c8c3'; BLUE='#608ca9'; MASS='#607e91'; DARK='#091520'
FONT='C:/Windows/Fonts/YuGothM.ttc'
if not Path(FONT).exists(): FONT='C:/Windows/Fonts/meiryo.ttc'

class Board:
    def __init__(self,w,h):
        self.w=w; self.h=h; self.im=Image.new('RGB',(w,h),BG); self.d=ImageDraw.Draw(self.im)
        self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',f'<rect width="{w}" height="{h}" fill="{BG}"/>']
    def rect(self,box,fill=PANEL,outline=None,width=2):
        self.d.rectangle(box,fill=fill,outline=outline,width=width)
        x,y,X,Y=box; self.svg.append(f'<rect x="{x}" y="{y}" width="{X-x}" height="{Y-y}" fill="{fill or "none"}" stroke="{outline or "none"}" stroke-width="{width}"/>')
    def line(self,pts,fill=TEAL,width=3,dash=False):
        if dash:
            for p,q in zip(pts,pts[1:]):
                n=max(1,int(math.dist(p,q)/9))
                for i in range(0,n,2):
                    self.d.line([(p[0]+(q[0]-p[0])*i/n,p[1]+(q[1]-p[1])*i/n),(p[0]+(q[0]-p[0])*min(i+1,n)/n,p[1]+(q[1]-p[1])*min(i+1,n)/n)],fill=fill,width=width)
        else:self.d.line(pts,fill=fill,width=width)
        points=' '.join(f'{x},{y}' for x,y in pts)
        self.svg.append(f'<polyline points="{points}" fill="none" stroke="{fill}" stroke-width="{width}"'+(' stroke-dasharray="9 9"' if dash else '')+'/>')
    def poly(self,pts,fill=MASS,outline=BLUE):
        self.d.polygon(pts,fill=fill); self.d.line(pts+[pts[0]],fill=outline,width=2)
        self.svg.append(f'<polygon points="'+ ' '.join(f'{x},{y}' for x,y in pts)+f'" fill="{fill}" stroke="{outline}" stroke-width="2"/>')
    def text(self,x,y,s,size=24,fill=INK):
        f=ImageFont.truetype(FONT,size); self.d.text((x,y),s,font=f,fill=fill)
        self.svg.append(f'<text x="{x}" y="{y+size}" font-family="Yu Gothic,Meiryo,sans-serif" font-size="{size}" fill="{fill}">{html.escape(s)}</text>')
    def save(self,name):
        self.im.save(ROOT/(name+'.png')); (ROOT/(name+'.svg')).write_text('\n'.join(self.svg+['</svg>']),encoding='utf-8')

def title(b,num,name,subtitle):
    b.text(55,35,f'CELESTIAL HALO-9   /   A2-G5   /   CONCEPT {num}',23,GOLD)
    b.text(55,78,name,48)
    b.text(58,144,subtitle,25,MUTED)

def detail(b,kind):
    b.text(1190,760,'03 / 生活断面の成立単位',26,GOLD)
    b.text(1190,810,'下向き重力・水平な住戸床',22,MUTED)
    b.rect((1200,875,1685,923),MASS)
    b.line([(1200,875),(1685,875)],TEAL,5)
    for x in [1240,1410,1570]:
        b.rect((x,842,x+65,875),BLUE)
    b.text(1200,935,'住戸 → 前庭 → 8〜20m街路',22)
    b.text(1200,980,'学校・食・ケアを各高度へ',22)
    if kind==1:
        b.rect((1240,1040,1670,1145),MASS)
        b.rect((1270,1062,1640,1120),DARK)
        b.line([(1240,1040),(1670,1040)],TEAL,5)
        b.line([(1240,1145),(1670,1145)],GOLD,5)
        b.text(1200,1165,'上の街の床＝公共施設の屋根',21)
        b.text(1200,1205,'下の街の公共庭に側面が開く',21)
        b.text(1200,1255,'共有岸：300〜700m級の複合体',21,MUTED)
    else:
        b.line([(1230,1150),(1375,1090),(1500,1090),(1660,1015)],TEAL,6)
        b.line([(1375,1090),(1430,1020),(1510,1020)],GOLD,5)
        b.rect((1270,1025,1290,1150),GOLD)
        b.rect((1560,1015,1580,1130),GOLD)
        b.text(1200,1185,'短い坂＋水平街路＋公共昇降',21)
        b.text(1200,1230,'5%で30m上昇 ≈ 水平600m',21,MUTED)
        b.text(1200,1270,'巨大な一本坂は日常圏を壊す',21,MUTED)
    b.text(1200,1340,'数値は設計目標。実測・法規値ではない',18,MUTED)

def board(kind):
    b=Board(1800,1580)
    if kind==1:title(b,'I','交庭聖都 / SHARED CIVIC SHORES','共有する公共境界 → 二つの生活地盤 → 奥行きのある連体都市')
    else:title(b,'II','群街昇都 / BRANCHING URBAN GROUNDS','街路と住所の分岐 → 複数の生活地盤 → 都市が立ち上がる輪郭')
    b.rect((45,210,960,690)); b.rect((985,210,1755,690)); b.rect((45,720,1145,1430)); b.rect((1170,720,1755,1430))
    b.text(70,228,'01 / 約10km都市の関係配置・平面構想',26,GOLD)
    b.text(70,270,'非地理登録：既存H・SBを移動しない',22,MUTED)
    # Central proposal plan: no compass or registered boundary.
    if kind==1:
        polys=[[(240,345),(330,330),(570,565),(505,615)],[(200,530),(240,450),(710,400),(740,485)],[(585,330),(675,350),(620,610),(535,580)]]
    else:
        polys=[[(340,615),(260,575),(260,365),(335,345)],[(340,615),(350,460),(500,330),(565,375),(435,535)],[(340,615),(440,540),(680,465),(715,540),(475,635)]]
    for p in polys:b.poly(p)
    labels=['L','M','U'] if kind==1 else ['R','B','T']
    for (x,y),t in zip([(325,410),(465,485),(610,550)],labels):
        b.rect((x-22,y-18,x+22,y+24),DARK,TEAL);b.text(x-10,y-15,t,24,TEAL)
    b.line([(110,600),(110,325),(830,325),(830,600)],MUTED,2,True)
    b.text(80,635,'W0・V1〜V3・三軸：既存方針を保持／経路は照合待ち',21,MUTED)
    b.text(1010,228,'02 / 地区・施設と中央の接続原理',26,GOLD)
    for i in range(6):
        y=300+i*46;b.rect((1015,y,1095,y+34),DARK,BLUE);b.text(1030,y+1,f'H{i+1}',21)
        b.line([(1095,y+17),(1130,y+17)],TEAL,2)
    b.line([(1130,317),(1130,547)],TEAL,4)
    b.text(1015,588,'Hの表示順は地理・高度を意味しない',20,MUTED)
    nodes=[(1250,340,'L 到着庭'),(1440,440,'M 共同庭'),(1250,540,'U 高所庭')]
    if kind==2:nodes=[(1250,540,'R 地上根'),(1440,340,'B 街路扇'),(1510,540,'T 横断庭')]
    pts=[(x,y) for x,y,t in nodes]
    b.line([pts[0],pts[1],pts[2],pts[0]],GOLD,4)
    for i,pt in enumerate(pts):
        b.line([(1130,340+i*90),(1170,340+i*90),pt],TEAL,2,True)
    for x,y,t in nodes:
        b.rect((x-30,y-18,x+120,y+30),DARK,TEAL);b.text(x-20,y-11,t,22)
    b.rect((1490,610,1725,655),DARK,BLUE); b.text(1500,615,'SB01〜16 / HERO4',21)
    b.line([pts[2],(1600,610)],MUTED,2,True)
    b.text(1160,286,'地区横断系統＋中央利用系統',21,TEAL)
    b.text(1190,645,'SPINE接続：端点未確定',19,MUTED)
    # Section uses proposed elevations only; horizontal schematic.
    b.text(70,745,'S-I / 中央主要断面' if kind==1 else 'S-II / 中央主要断面',27,GOLD)
    b.text(70,790,'構想高度km／横方向は模式図／遠景シルエット案ではない',20,MUTED)
    base=1325; scale=75
    for z in range(7):
        yy=base-z*scale;b.line([(125,yy),(1090,yy)],BLUE,1,True);b.text(75,yy-16,str(z),20,MUTED)
    def transform(poly):return [(int(140+x*150),int(base-z*scale)) for x,z in poly]
    if kind==1:
        masses=[[(0,0),(1.0,0),(1.5,1.8),(3.1,2.0),(3.0,2.5),(1.1,2.4),(.5,1.2)],[(4.4,0),(5.8,0),(5.3,2.4),(4.5,4.0),(2.6,3.9),(2.6,3.3),(4.0,3.2)],[(.5,1.3),(1.4,1.5),(1.8,3.6),(3.0,5.3),(5.0,5.3),(5.0,5.8),(2.6,5.8),(1.1,4.2)]]
        for p in masses:b.poly(transform(p))
        for p in [[(1.1,2.4),(3.0,2.5)],[(2.6,3.9),(4.5,4.0)],[(3,5.3),(5,5.3)]]:b.line(transform(p),TEAL,5)
        for x,z,t in [(1.6,2.0,'市場・公共庭'),(3.0,3.5,'学習・文化'),(3.0,5.5,'高所居住都市')]:
            X,Y=transform([(x,z)])[0];b.text(X,Y-28,t,21,GOLD)
        b.line(transform([(1,0),(1,2.1),(2.3,2.1),(2.3,3.5),(3.8,3.5),(3.8,5.3)]),GOLD,5)
        b.text(200,1065,'二つの街が公共境界を共有',22)
        b.text(240,1210,'大きな空をずれた高度で外へ開く',22)
        b.text(160,1360,'中央包絡の構想：4.8 × 4.2 × 高さ5.8km',24)
    else:
        masses=[[(.2,0),(1.3,0),(1.9,2.0),(1.4,3.6),(.7,3.8),(.5,2.2)],[(1,0),(2.0,0),(3.4,3.0),(4.3,4.4),(4.3,4.8),(3.4,4.8),(2.3,3.0)],[(1.7,0),(3.0,0),(4.7,1.7),(5.8,2.1),(5.8,2.6),(4.5,2.6),(2.7,1.1)]]
        for p in masses:b.poly(transform(p))
        for p in [[(.7,3.8),(1.4,3.6)],[(3.4,4.8),(4.3,4.8)],[(4.5,2.6),(5.8,2.6)]]:b.line(transform(p),TEAL,5)
        for x,z in [(1,0),(3,1.8),(4.7,2.6)]:b.line(transform([(x,z),(x,z+1.2)]),GOLD,6)
        b.line(transform([(.6,.5),(1.5,.9),(2.7,2.1),(3.8,3.3),(4.1,4.4)]),GOLD,5)
        b.line(transform([(1.2,2),(4.4,2),(5.3,2.4)]),TEAL,4,True)
        b.text(220,910,'複数の高所生活地盤',22,GOLD)
        b.text(500,1100,'谷は街路と採光のために残す',22)
        b.text(200,1220,'地上の街から分岐／各枝で日常が完結',22)
        b.text(160,1360,'中央包絡の構想：5.6 × 4.6 × 高さ4.8km',24)
    detail(b,kind)
    b.text(55,1460,'凡例：青灰＝居住・公共・設備を含む都市断面　水緑＝生活地盤／横断　金＝公共移動・共有部',22,MUTED)
    b.text(55,1502,'座標未確認・接続端点未確定。W0や既存建築の形状再現図ではない。ART NOT_REVIEWED / 施工HOLD',21,GOLD)
    b.save('concept-I' if kind==1 else 'concept-II')

def comparison():
    b=Board(1800,1110);title(b,'I / II','都市の生成原理を比較する','暫定選抜：案I 交庭聖都 ／ 両案とも未合格・中央監督のG5審査待ち')
    for x,name,sub in [(55,'I / 交庭聖都','共有境界が先 → 都市が連体する'),(925,'II / 群街昇都','街路が先 → 生活地盤が分岐する')]:
        b.rect((x,220,x+820,580));b.text(x+25,240,name,32,GOLD);b.text(x+25,300,sub,25)
    # Comparison drawn independently to keep SVG/PNG in exact agreement.
    b.poly([(150,535),(220,535),(260,420),(475,425),(475,390),(210,390)])
    b.poly([(570,535),(640,535),(590,350),(380,350),(380,385),(530,390)])
    b.poly([(215,430),(270,430),(345,315),(580,315),(580,345),(380,350)])
    b.poly([(1030,535),(1110,535),(1190,360),(1150,345),(1080,430)])
    b.poly([(1090,535),(1170,535),(1420,345),(1420,310),(1360,310),(1220,420)])
    b.poly([(1160,535),(1250,535),(1570,440),(1570,400),(1470,400)])
    rows=[('形成単位','上下近隣が共有する公共岸','地上街路から分岐する生活地盤'),('都市性','自立した近隣＋共同利用の厚い結節','住所と沿道が連続／移動負荷が課題'),('主役性','大空地と高所主質量が同時に生まれる','都市の広がりは強い／中央が薄まり得る'),('失敗の条件','巨大な棒組み・橋・門にしか見えない','巨大な棚・階段・団地にしか見えない'),('未解決','共有岸の実断面／全方向の輪郭','徒歩距離／側面の壁化／中央の唯一性')]
    y=625
    for label,a,c in rows:
        b.line([(55,y+65),(1745,y+65)],BLUE,1)
        b.text(65,y,label,24,GOLD);b.text(330,y,a,23);b.text(1040,y,c,23);y+=77
    b.text(55,1030,'精密3Dなし。比較は構想に対する自己批評であり、第三者審査・正式採択ではない。',23,MUTED)
    b.save('comparison')

if __name__=='__main__':
    board(1);board(2);comparison()
    print('Created 3 PNG + 3 SVG concept diagrams; no 3D model.')
