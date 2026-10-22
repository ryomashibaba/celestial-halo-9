"""Deterministic 2D concept diagrams. No 3D, game IO or canonical coordinates."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, json, csv, hashlib
R=Path(__file__).resolve().parent
W,H=2400,2140
BG='#0d2029'; PANEL='#142f39'; INK='#e9eee5'; MUTED='#a0b9b9'; GOLD='#e5b467'; TEAL='#3e8e99'; GREEN='#78a28d'; DARK='#244752'
font='C:/Windows/Fonts/meiryo.ttc'
def f(s):return ImageFont.truetype(font,s)
def start(title,sub):
 global im,d
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 d.text((70,45),'CELESTIAL HALO-9   /   C2-G5   /   CONCEPT',font=f(24),fill=GOLD)
 d.text((70,95),title,font=f(56),fill=INK)
 d.text((70,182),sub,font=f(27),fill=MUTED)
def text(x,y,s,size=25,color=INK):d.text((x,y),s,font=f(size),fill=color)
def panel(x,y,w,h,label):
 d.rounded_rectangle((x,y,x+w,y+h),radius=12,fill=PANEL)
 text(x+22,y+16,label,29)
def line(pts,col=GOLD,width=5):d.line(pts,fill=col,width=width)
def poly(pts,col=INK):d.polygon(pts,fill=col)
def dashed(a,b,col=MUTED):
 dx,dy=b[0]-a[0],b[1]-a[1];n=max(1,int(math.hypot(dx,dy)/20))
 for i in range(0,n,2):line([(a[0]+dx*i/n,a[1]+dy*i/n),(a[0]+dx*min(i+1,n)/n,a[1]+dy*min(i+1,n)/n)],col,3)
def path(pts):
 for a,b in zip(pts,pts[1:]):dashed(a,b)
def blocks(x,y,w,h,n=9):
 for i in range(n):
  xx=x+i*w/n;hh=h*(.45+(.37*i%1)*.5)
  d.rectangle((xx,y-hh,xx+w/n*.7,y),fill=GREEN)
def mass(kind,x,y,s=1,variant=None):
 # All points use a diagram-local frame, NOT surveyed coordinates.
 def pp(points):return [(x+a*s,y+b*s) for a,b in points]
 if kind=='A':
  shapes=[([(0,0),(0,-85),(70,-115),(155,-115),(175,-20),(175,0)],'05'),
          ([(125,0),(125,-170),(205,-195),(232,-355),(310,-380),(340,-325),(340,0)],'12'),
          ([(350,0),(350,-260),(405,-288),(455,-220),(455,0)],'08'),
          ([(435,0),(435,-115),(505,-135),(590,-82),(615,0)],'09')]
 else:
  shapes=[([(40,0),(20,-110),(65,-180),(175,-165),(200,-70),(170,0)],'05'),
          ([(160,0),(150,-270),(235,-320),(300,-230),(290,0)],'12'),
          ([(265,-65),(245,-180),(330,-260),(420,-240),(470,-140),(430,-60)],'08'),
          ([(405,0),(380,-95),(460,-150),(550,-140),(595,-65),(570,0)],'09')]
 for pts,key in shapes:
  if key==variant:continue
  poly(pp(pts),INK)
  # Public room and smaller living grain remain distinct in section.
  bx=min(a for a,b in pts);ex=max(a for a,b in pts);by=min(b for a,b in pts)
  room=[(bx+(ex-bx)*.23,-32),(bx+(ex-bx)*.23,by*.63),(ex-(ex-bx)*.22,by*.7),(ex-(ex-bx)*.22,-32)]
  poly(pp(room),TEAL)
  for q in range(3):
   yy=by*.85+q*13
   line(pp([(bx+(ex-bx)*.25,yy),(ex-(ex-bx)*.24,yy)]),GREEN,max(1,int(4*s)))
 line(pp([(-35,3),(650,3)]),GOLD,max(2,int(4*s)))
 if variant:
  text(x,y+15,'− SB'+variant+' の関係',22,GOLD)
def plan(kind):
 panel(60,270,1100,660,'01  10km都市の関係図  /  方位・既存配置は未確定')
 cx,cy=600,593
 # Coarse city field rather than a new physical ring.
 for j in range(8):
  for i in range(15):
   xx=130+i*62;yy=390+j*52
   if ((xx-cx)/220)**2+((yy-cy)/140)**2<1:continue
   d.rectangle((xx,yy,xx+34,yy+21),fill=DARK)
 path([(420,500),(530,465),(750,510),(805,675),(660,742),(440,680),(420,500)])
 text(450,717,'W0等の負空間：占有照合待ち',21,MUTED)
 axes=[[(145,800),(340,700),(510,635)],[(1025,780),(845,670),(720,600)],[(760,360),(720,450),(665,525)]]
 for k,pts in enumerate(axes):
  line(pts,GOLD,8);text(pts[0][0]-20,pts[0][1]-35,'αβγ'[k],29,GOLD)
 if kind=='A':
  for pts in [[(500,570),(575,520),(650,540),(640,620),(570,650),(500,620)],[(630,530),(710,515),(760,555),(730,630),(665,620)]]:poly(pts,INK)
  line([(520,610),(610,590),(680,555)],TEAL,22)
 else:
  for a,b in [(560,530),(675,555),(600,630),(745,640)]:d.rounded_rectangle((a-45,b-32,a+45,b+32),18,fill=INK)
  line([(560,530),(600,630),(675,555),(745,640)],TEAL,18)
  path([(280,450),(900,450),(980,700),(300,790)])
 text(110,839,'α・β・γは仮の接近方向。V1〜V3の番号ではない。',23)
 text(110,876,'H1〜H6・SB01〜16は、実座標未確認のため配置しない。',23,MUTED)
def section(kind):
 panel(1200,270,1140,660,'02  中央主役の断面仮説  /  形状は2D包絡')
 mass(kind,1415,795,1.12)
 text(1260,830,'地上：到着・市場  →  中高度：大公共室  →  高所：生活と公共庭',23)
 text(1260,871,('A  約2.8 × 2.1 × 高さ2.2km' if kind=='A' else 'B  約3.2 × 2.5 × 高さ1.9km')+'  /  提案値・実測ではない',23,GOLD)
def views(kind):
 for k,(x,y,title) in enumerate([(60,970,'03  遠景 約10km'),(1220,970,'04  都市軸からの接近'),(60,1455,'05  中央公共空間'),(1220,1455,'06  高高度からの関係')]):
  panel(x,y,1120,445,title)
  if k==0:
   blocks(x+55,y+350,995,45,35);mass(kind,x+340,y+345,.65)
   for xx,yy in [(155,215),(850,195),(960,260)]:
    d.rectangle((x+xx,y+yy,x+xx+75,y+yy+20),fill=GREEN)
    dashed((x+xx+35,y+yy+20),(x+xx+35,y+325))
   text(x+28,y+391,'都市の生活密度・空白・中央質量を同時に読む',23)
  elif k==1:
   poly([(x+100,y+355),(x+455,y+260),(x+580,y+260),(x+980,y+355)],DARK)
   line([(x+150,y+355),(x+480,y+265)],GOLD,4);line([(x+950,y+355),(x+565,y+265)],GOLD,4)
   mass(kind,x+360,y+315,.55)
   blocks(x+70,y+335,200,92,6);blocks(x+800,y+335,220,85,5)
   text(x+28,y+391,'側方の施設 → 前庭の空白 → 主役。実視線は未検証',23)
  elif k==2:
   poly([(x+55,y+80),(x+285,y+85),(x+320,y+340),(x+55,y+350)],INK)
   poly([(x+820,y+105),(x+1070,y+70),(x+1070,y+350),(x+785,y+340)],INK)
   line([(x+320,y+340),(x+785,y+340)],GOLD,5)
   blocks(x+320,y+325,465,28,15)
   for xx in [420,530,645,710]:
    d.ellipse((x+xx,y+319,x+xx+5,y+324),fill=GOLD);line([(x+xx+2,y+324),(x+xx+2,y+338)],GOLD,2)
   if kind=='B':
    poly([(x+320,y+110),(x+465,y+75),(x+510,y+165),(x+355,y+210)],TEAL)
    text(x+525,y+175,'室の間に開く谷',27,TEAL)
   else:text(x+350,y+175,'上空へ開く余白',30,TEAL)
   text(x+28,y+391,'大公共室の入口と日常街路が同じ前庭に面する',23)
  else:
   roofsets=([[(170,280),(400,150),(530,200),(310,330)],[(570,250),(790,130),(960,210),(740,340)]] if kind=='A' else [[(100,270),(270,160),(390,210),(240,315)],[(390,170),(540,95),(650,160),(510,245)],[(670,210),(830,130),(970,210),(815,290)],[(420,330),(590,230),(720,300),(570,370)]])
   for pts in roofsets:poly([(x+a,y+b) for a,b in pts],INK)
   for a,b in [(220,270),(340,220),(650,235),(780,190)]:blocks(x+a,y+b,100,25,6)
   path([(x+470,y+130),(x+570,y+180),(x+540,y+330),(x+420,y+350)])
   text(x+458,y+290,'負空間',26,TEAL)
   text(x+28,y+391,'公共の肩・生活街区・地上への切込みを読む',23)
def make(kind):
 start('A  天衢会都 ／ 会流宮' if kind=='A' else 'B  六庭共議都 ／ 交響公館',
       '接近の流れが、厚い公共街区と光の裂隙を生む' if kind=='A' else '分散した公共活動の交換が、異なる高さの室と庭を生む')
 plan(kind);section(kind);views(kind)
 text(70,1940,'白：公共街区包絡   青緑：公共室   緑：生活街区   金：公共の移動・広場   破線：未照合領域',24)
 text(70,1990,'全図は関係を説明する2Dスケッチ。透視・構造・交通・実座標は未検証。HERO4本体は移設しない。',24,MUTED)
 text(70,2040,'CONCEPT審査待ち  /  正式M247-C維持  /  施工HOLD  /  GLB・BLENDなし',24,GOLD)
 im.save(R/(kind+'_CONCEPT.png'))
def causal():
 start('施設との関係を除くと、主役の外形も変わる','中央側の新設空間の差分。正式施設の撤去・移築・需要計算を示す図ではない。')
 labels=[('05','大集会の前室が消え、低い肩が縮む'),('08','二大公共室が消え、中ほどの量を失う'),('09','閾との関係を失い、前庭の後退を再設計'),('12','静かな高所の目的地が消え、高い肩が縮む')]
 for j,kind in enumerate(['A','B']):
  xx=80+j*1170;text(xx,270,kind+'  全関係あり',32,GOLD);mass(kind,xx+180,710,.9)
  for i,(key,caption) in enumerate(labels):
   yy=790+i*280;panel(xx,yy,1100,255,'SB'+key+'との関係を除く')
   mass(kind,xx+30,yy+205,.34,key)
   text(xx+365,yy+105,caption,24)
 text(80,1990,'A：前庭と肩が変わる。B：室の隣接と接合が変わる。活動の違いを装飾だけに押し込めない。',25)
 text(80,2040,'概念上の除去テスト  /  容量・構造に基づく自動生成ではない  /  CONCEPT・美術HOLD',23,GOLD)
 im.save(R/'CAUSALITY.png')
if __name__=='__main__':
 for k in ['A','B']:make(k)
 causal()
 print('Generated three deterministic 2D concept sheets')
