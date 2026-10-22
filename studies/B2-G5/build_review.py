"""B2-G5 concept diagrams. No mesh, renderer, Work or world interaction.
Run: python studies/B2-G5/build_review.py
Requires Pillow; diagrams are schematic and use proposed dimensions only.
"""
from pathlib import Path
import json, hashlib, html, math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent.parent
BG='#101d29'; FG='#e9f0ef'; MUT='#9fb2be'; GOLD='#e4c589'; TEAL='#81cfc4'; INK='#344b5b'; BLUE='#235571'; RED='#cd8c83'
FONT='C:/Windows/Fonts/YuGothM.ttc'

class Board:
    def __init__(self,title,sub,w=1600,h=1100):
        self.w,self.h=w,h
        self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="{BG}"/>']
        self.im=Image.new('RGB',(w,h),BG); self.d=ImageDraw.Draw(self.im)
        self.text(44,32,title,32,FG); self.text(44,82,sub,17,MUT)
    def text(self,x,y,s,size=19,color=FG):
        self.parts.append(f'<text x="{x}" y="{y+size}" font-family="Yu Gothic, sans-serif" font-size="{size}" fill="{color}">{html.escape(str(s))}</text>')
        self.d.text((x,y),str(s),font=ImageFont.truetype(FONT,size),fill=color)
    def line(self,pts,color=MUT,width=2,dash=False):
        points=' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)
        self.parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="8 8"' if dash else '')+'/>')
        if not dash:self.d.line(pts,fill=color,width=width)
        else:
            for a,b in zip(pts,pts[1:]):
                d=math.dist(a,b); n=max(1,int(d/10))
                for k in range(0,n,2):
                    p=lambda t:(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
                    self.d.line([p(k/n),p(min(k+1,n)/n)],fill=color,width=width)
    def poly(self,pts,fill=INK,stroke=TEAL):
        self.parts.append('<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)+f'" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        self.d.polygon(pts,fill=fill,outline=stroke,width=2)
    def rect(self,x,y,w,h,fill=INK,stroke=MUT): self.poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],fill,stroke)
    def save(self,name,png=False):
        (ROOT/f'{name}.svg').write_text(''.join(self.parts)+'</svg>',encoding='utf-8')
        if png:self.im.save(ROOT/f'{name}.png')

def strip(b,points,width=36):
    # diagram of continuous public ground; not a structural envelope
    normals=[]
    for i,(x,y) in enumerate(points):
        a=points[max(0,i-1)]; c=points[min(len(points)-1,i+1)]
        dx,dy=c[0]-a[0],c[1]-a[1]; length=math.hypot(dx,dy)
        normals.append((-dy/length*width,dx/length*width))
    p=[(x+nx,y+ny) for (x,y),(nx,ny) in zip(points,normals)]
    p += [(x-nx,y-ny) for (x,y),(nx,ny) in reversed(list(zip(points,normals)))]
    b.poly(p,INK,TEAL); b.line(points,GOLD,3)

def plans():
    b=Board('B2-G5 / 都市が大地になる','01 — 10km研究平面｜W0への座標登録前・既存施設の位置は未描画')
    for j,name in enumerate(['G5-01  昇街褶都','G5-02  天架織都']):
        ox=60+j*800; oy=180; s=620
        b.text(ox,130,name,26,GOLD); b.rect(ox,oy,s,s,BG,INK)
        def p(x,y):return (ox+(x+5)*62,oy+(5-y)*62)
        for x in range(-4,5,2): b.line([p(x,-5),p(x,5)],INK,1)
        for y in range(-4,5,2): b.line([p(-5,y),p(5,y)],INK,1)
        b.poly([p(-5,3.6),p(-3,4.5),p(-1,3.5),p(1,4.5),p(3,3.7),p(5,4.4),p(5,5),p(-5,5)],'#283c44',MUT)
        b.line([p(-4.4,-1),p(-4.2,1),p(-4.6,3.6)],MUT,6)
        b.poly([p(3,-2),p(4.4,-2.5),p(5,-1),p(5,2.7),p(3.2,1.7)],BLUE,TEAL)
        b.poly([p(-5,-5),p(-2,-5),p(-2.4,-2.2),p(-4.2,-1.7),p(-5,-2.5)],BG,RED)
        b.text(ox+140,oy+13,'北：山岳・高原（依頼条件）',16,MUT)
        b.text(ox+8,oy+270,'西の断崖',15,MUT); b.text(ox+488,oy+310,'東の内海',15,TEAL)
        b.text(ox+15,oy+535,'南西：負空間',17,RED)
        if j==0:
            for k in range(3):
                xs=-1.4+k*1.15
                a=[p(xs-.2,-2.1),p(xs+.2,-.8),p(xs-.2,.4),p(xs+.3,2.1)]
                strip(b,a,17)
            for y in [-.8,.4,1.3]:b.line([p(-1.7,y),p(1.8,y)],GOLD,8)
            b.text(ox+242,oy+255,'P2',18,GOLD);b.text(ox+300,oy+204,'P4',18,GOLD)
        else:
            a=[p(-2.3,-1.4),p(1.7,1.3)];c=[p(-1.2,1.8),p(2.3,-1.5)]
            strip(b,a,28);strip(b,c,28)
            for k,(x,y) in enumerate([(-1.9,-1.1),(-.7,-.3),(1.4,1.1),(-.9,1.5),(.4,.3),(1.9,-1.2)]):
                q=p(x,y);b.rect(q[0]-12,q[1]-12,24,24,BG,GOLD)
                b.text(q[0]+14,q[1]-12,f'S{k+1}',12,GOLD)
        for x,y in [(0,3),(3,0),(-3,0)]:
            b.line([p(x,y),p(x*.55,y*.55)],GOLD,2,True)
        b.text(ox+635,oy+20,'N ↑',19,FG)
        b.line([(ox+400,oy+650),(ox+586,oy+650)],FG,3);b.text(ox+400,oy+657,'0           3km',16,MUT)
        b.text(ox,oy+712,'中央：提案地盤　金線：中央側共有動線',18,TEAL)
        b.text(ox,oy+745,'点線：方向のみ／既定都市軸とは未照合',18,MUT)
    b.text(44,1020,'比較座標：X/Y −5〜+5km｜中央寸法は計画値｜H/SB/HERO4の確定位置・回廊・保護範囲は未確認',18,RED)
    b.save('city_plans',True)

def sections():
    b=Board('B2-G5 / 地盤・公共建築・生活の断面','02 — 計画断面｜南→北を展開した模式図。水平延長と形状は略図、Zのみ計画高さを示す')
    b.text(50,130,'G5-01  昇街褶都｜屋根が次の街路になる',25,GOLD)
    x0=120; y0=500; sx=.105; sz=.105
    pts=[(0,0),(2100,420),(4700,980),(7500,1650),(10600,2400)]
    q=[(x0+x*sx,y0-z*sz) for x,z in pts]
    b.line([(85,y0),(1450,y0)],MUT,2)
    for i,(x,y) in enumerate(q):
        b.rect(x-35,y,140,29,INK,TEAL)
        b.text(x-23,y-34,f'P{i} / {pts[i][1]}m',17,GOLD)
        for k in range(3):b.rect(x+k*22,y-18,14,18,'#7caba7',TEAL)
    for a,c in zip(q,q[1:]):strip(b,[(a[0]+85,a[1]+14),(c[0]-35,c[1]+14)],10)
    b.text(100,540,'地下 −180m：公共駅と物流を区分　　斜行交通：20〜24%（方式未検証）　　上昇経路水平延長10.6km',17,MUT)
    b.rect(620,398,200,57,BG,GOLD);b.text(632,414,'P2 千光市庭',20,GOLD)
    b.text(55,570,'P2：700×320m・有効高さ150m / 上面は街区地盤。住居は外縁・中庭縁、奥行12〜24mを計画目標にする。',18,FG)
    b.text(50,640,'G5-02  天架織都｜都市が大地を支え、大地が都市を生む',25,GOLD)
    y=975; zz=.095
    b.line([(85,y),(1450,y)],MUT,2)
    for i,x in enumerate([230,590,1040]):
        b.rect(x,y-1450*zz,110,1450*zz,INK,TEAL)
        b.rect(x+34,y-1450*zz,42,1450*zz,BG,GOLD)
        for z in [300,700,1100]:b.line([(x,y-z*zz),(x+110,y-z*zz)],GOLD,3)
        b.text(x,y+8,'中庭縦都市',16,MUT)
    b.rect(160,y-1450*zz,1160,21,INK,TEAL)
    b.rect(470,y-2200*zz,790,25,INK,TEAL)
    for x in [520,810,1090]:
        b.poly([(x,y-1450*zz),(x+85,y-2200*zz),(x+140,y-2200*zz),(x+55,y-1450*zz)],INK,TEAL)
    b.text(1340,y-1450*zz,'1,450m',17,GOLD);b.text(1300,y-2200*zz,'2,200m',17,GOLD)
    b.text(60,1020,'交差部：空の共同庁 800×500m・高さ180m｜支持体の中庭＋横断切欠き｜巨大スパン・日射・風・避難は未検証',18,RED)
    b.save('sections',True)

def scheme(b,x,y,w,h,variant,view):
    # Six conceptual glyphs, not projections of a validated shared model.
    def p(a,c):return(x+a*w,y+c*h)
    b.line([p(0,.92),p(1,.92)],INK,2)
    if view==4:
        if variant==0:
            for j in range(3):strip(b,[p(.15+j*.22,.8),p(.22+j*.22,.46),p(.15+j*.22,.13)],w*.045)
            for k in [.3,.6]:b.line([p(.1,k),p(.82,k)],GOLD,4)
        else:
            strip(b,[p(.12,.77),p(.86,.18)],w*.06);strip(b,[p(.17,.15),p(.87,.8)],w*.06)
    elif view==5:
        if variant==0:
            b.poly([p(.02,.1),p(.98,.1),p(.84,.3),p(.12,.3)],INK,TEAL)
            for j in range(6):b.rect(x+j*w*.16,y+h*.64,w*.13,h*.25,INK,GOLD)
            b.line([p(.04,.9),p(.5,.54),p(.96,.9)],TEAL,3)
            b.rect(x+w*.43,y+h*.35,w*.14,h*.18,BG,GOLD)
        else:
            b.poly([p(.06,.1),p(.32,.24),p(.32,.87),p(.06,.9)],INK,TEAL)
            b.poly([p(.94,.1),p(.68,.24),p(.68,.87),p(.94,.9)],INK,TEAL)
            for k in [.35,.55,.75]:b.line([p(.32,k),p(.68,k)],GOLD,3)
            b.line([p(.32,.1),p(.5,.04),p(.68,.1)],TEAL,3)
        # human scale symbol / diagram only
        b.line([p(.5,.85),p(.5,.92)],FG,2);b.line([p(.48,.86),p(.52,.86)],FG,2)
    elif variant==0:
        if view==2:
            strip(b,[p(.04,.88),p(.23,.74),p(.43,.55),p(.65,.33),p(.88,.1)],w*.045)
            for a,c in [(.23,.74),(.43,.55),(.65,.33),(.88,.1)]:b.line([p(a-.06,c),p(a+.1,c)],GOLD,6)
        else:
            for j in range(3):
                off=j*.23
                a=[p(.04+off,.88),p(.17+off,.64),p(.12+off,.39),p(.22+off,.1+(.06 if j==1 else 0))]
                strip(b,a,w*.045)
                for k in [.38,.63]:
                    b.line([p(.08+off,k),p(.25+off,k)],GOLD,4)
                    for n in range(3):
                        ax=x+(.09+off+n*.035)*w; cy=y+k*h
                        b.rect(ax,cy-h*.05,w*.025,h*.045,'#7caba7',TEAL)
            if view==1:b.line([p(.13,.72),p(.87,.45)],GOLD,4)
            if view==3:
                for j in range(3):b.rect(x+(.14+j*.23)*w,y+.75*h,.06*w,.14*h,BG,GOLD)
    elif view in [0,2,3]:
        # Elevation studies intentionally differ from the oblique glyph.
        columns=[.14,.43,.75] if view!=2 else [.24,.66]
        for a in columns:
            b.rect(x+a*w,y+.24*h,.12*w,.65*h,INK,TEAL)
            b.rect(x+(a+.045)*w,y+.31*h,.03*w,.58*h,BG,GOLD)
        for left,right,c in [(.06,.93,.48),(.2,.88,.18)]:
            b.rect(x+left*w,y+c*h,(right-left)*w,.09*h,INK,TEAL)
            for j in range(5):
                a=left+.03+j*(right-left-.08)/5
                b.rect(x+a*w,y+(c-.055)*h,.045*w,.05*h,'#7caba7',TEAL)
        if view==3:
            for a in columns:
                b.line([p(a,.68),p(a+.12,.68)],GOLD,4)
                b.rect(x+(a+.02)*w,y+.73*h,.08*w,.13*h,BG,GOLD)
    else:
        for j in range(3):
            ax=x+(.15+j*.28)*w
            b.rect(ax,y+h*.25,w*.12,h*.64,INK,TEAL)
            b.rect(ax+w*.045,y+h*.3,w*.03,h*.59,BG,GOLD)
        b.poly([p(.05,.26),p(.69,.06),p(.96,.18),p(.31,.4)],INK,TEAL)
        b.poly([p(.12,.5),p(.76,.32),p(.95,.45),p(.32,.64)],INK,TEAL)
        if view==2:b.line([p(.12,.5),p(.95,.45)],GOLD,4)
        for j in range(7):b.rect(x+(.27+j*.075)*w,y+(.23-j*.018)*h,w*.045,h*.07,'#7caba7',TEAL)

def views():
    b=Board('B2-G5 / 六つの距離から読む都市','03 — 手描き相当の構想模式画｜各図は設計意図を説明する独立図。共通GLB・共通カメラによるレンダーではない',1600,1200)
    names=['正面／南','斜視／南東','側面／東','背面／北','俯瞰','内部']
    for v in range(2):
        b.text(40+v*800,126,['G5-01 昇街褶都','G5-02 天架織都'][v],25,GOLD)
        for k,n in enumerate(names):
            x=40+v*800+(k%2)*370;y=190+(k//2)*315
            b.text(x,y,n,20,TEAL);scheme(b,x+12,y+45,315,215,v,k)
    b.text(40,1150,'淡色＝生活地区・公共地盤 / 金＝共有動線・切欠き / 暗色＝構造・設備帯 / 全て提案、未測量・未解析',17,MUT)
    b.save('six_views',True)

def comparison():
    b=Board('CELESTIAL HALO-9 / B2-G5','CONCEPT REVIEW 01｜都市そのものが人工地形になる｜精密3D・正式採用・施工は保留',1600,1000)
    for v in range(2):
        x=50+v*800
        b.text(x,140,['G5-01 昇街褶都','G5-02 天架織都'][v],31,GOLD)
        b.text(x,192,['公共建築の屋根 → 次の街路 → 次の公共建築','高空の共有地盤 → 内部都市を持つ支持体'][v],21,TEAL)
        scheme(b,x+30,260,620,385,v,1)
        lines=[['地面から育つ / 内部と外側を何度も往復','中央包絡：3.8 × 4.2 × 2.8km（計画）','暫定有望：生活の連鎖が主質量を決める','リスク：山の輪郭・長大な移動・深い影'],['空の地盤から組織 / 縦都市と横都市が交差','中央包絡：4.6 × 3.6 × 2.6km（計画）','独立対案：都市が地盤を支え、地盤が都市を生む','リスク：巨大床・柱への還元・スパンと地上の影']][v]
        for i,s in enumerate(lines):b.text(x,700+i*47,s,20,FG if i!=3 else RED)
    b.text(50,937,'構想模式図：実3D・完成予想の証明画像ではない。W0確定配置との整合と中央監督の選抜は未実施。',18,MUT)
    b.save('comparison',True)

def public_spaces():
    b=Board('B2-G5 / 公共空間の下に建築、上に次の都市','04 — 部分断面模式図｜寸法は計画値。荷重・設備・環境・避難容量は未検証',1600,1000)
    for v in range(2):
        ox=55+v*800; oy=340
        b.text(ox,135,['G5-01  P2《千光市庭》','G5-02《空の共同庁》'][v],27,GOLD)
        b.text(ox,184,['Z980m / 700×320m / 有効高さ150m','交差地盤 / 800×500m / 有効高さ180m'][v],18,TEAL)
        b.rect(ox+15,oy,675,35,INK,TEAL)
        for j in range(5):
            xx=ox+45+j*128
            b.rect(xx,oy-68,70,68,'#537b7d',TEAL)
            b.rect(xx+12,oy-58,45,40,BG,GOLD)
        b.text(ox+25,oy-108,'屋根上：学校・住居・市場・通学街路',19,FG)
        b.line([(ox+35,oy-2),(ox+655,oy-2)],GOLD,4)
        b.rect(ox+15,oy+270,675,32,INK,TEAL)
        for xx in [ox+15,ox+645]:
            b.rect(xx,oy+35,45,235,INK,TEAL)
            b.rect(xx+10,oy+75,25,125,BG,GOLD)
        for j in range(5):
            xx=ox+90+j*107
            b.rect(xx,oy+175,75,95,INK,GOLD)
            b.line([(xx,oy+215),(xx+75,oy+215)],TEAL,2)
        b.line([(ox-5,oy+265),(ox+15,oy+265)],GOLD,4)
        b.line([(ox+690,oy+265),(ox+710,oy+265)],GOLD,4)
        b.text(ox+90,oy+90,['市場・図書館・共同食堂','図書館・議場・市場'][v],20,GOLD)
        b.text(ox+100,oy+130,'大空間の縁が街路と生活の入口になる',16,FG)
        b.text(ox+10,oy+320,'← 外部街路　内部公共街路を通過　外部出口 →',18,TEAL)
        b.text(ox+15,oy+375,['地上からP1を経て入り、P3へ上がる','支持体の中庭街路から入り、上部地盤へ'][v],19,FG)
        b.text(ox+15,oy+420,'主公共空間と背後の居住入口を分離',18,MUT)
        b.text(ox+15,oy+460,'住居は浅い外縁・中庭縁。設備は構造帯へ',18,MUT)
    b.text(50,925,'大空洞の中に施設を点置せず、公共空間の縁・上・下を街の住所にする。柱・支点の図は構造解ではありません。',18,RED)
    b.save('public_spaces',True)

def write(name,obj): (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def records():
    a=['P1＋独立縦交通','P2東側街路','P2西側街路','P3横断生活街路','P4南側公共街路','P3/P4間の乗換口','地上東口→P0','地上北口→P1','地上西口→P0','P1公共街路','P1横断街路','P2東側街路','P2市場縁','P2北側出口','P3東側街路','P3横断街路','P3北側街路','P4水平生活街路','P4西側街路','P0地上回廊','P2/P3乗換口','地下公共駅→分散出口','主眺望回廊→P2']
    c=['下部地盤東端','下部地盤北端','支持体地域駅→下部地盤','上部地盤東端','上部地盤北端','上下交差公共街区','地上東口→縦都市','地上北口→下部地盤','地上西口→縦都市','下部地盤公共街路','下部地盤交差節','下部地盤東端','下部地盤地域庭','支持体Z700m地域街路','上部地盤東端','上部地盤交差節','上部地盤北端','上部地盤地域街路','上部地盤西端','地上独立回廊','上下地盤間乗換口','地下公共駅→縦都市','眺望から帯を退かせ交差部へ']
    ids=[f'H{i}' for i in range(1,7)]+[f'SB{i:02}' for i in range(1,17)]+['HERO4']
    rows=[{'id':i,'existing_coordinate_m':None,'existing_altitude_m':None,'existing_function':None,'relocation':False,'G5-01_proposed_receiver':aa,'G5-02_proposed_receiver':cc,'status':'ENDPOINT_UNVERIFIED','shared_route':True,'clearance_check':'NOT_PERFORMED'} for i,aa,cc in zip(ids,a,c)]
    write('connections.json',{'study_id':'B2-G5','coordinate_status':'CONCEPT_LOCAL_UNREGISTERED','not_existing_layout':True,'endpoints':rows})
    write('integration_guards.json',{'study_id':'B2-G5','authority':'User clarification 2026-10-23 JST','existing_elements':[{'id':i,'coordinate_status':'UNVERIFIED','function_status':'UNVERIFIED','relocation':False,'connection_endpoint':'UNDETERMINED'} for i in ['V1','V2','V3','EXISTING_MAJOR_AXIS_1','EXISTING_MAJOR_AXIS_2','EXISTING_MAJOR_AXIS_3','EXISTING_VIEW_CORRIDORS']],'coordinate_systems':{'M207_W0':'U/H/V','M204_CENTRAL':'X/H/Z','G5':'UNREGISTERED_RESEARCH_LOCAL_X_Y_Z','verified_common_anchors':0,'transforms_created':False,'inferred_registration':'PROHIBITED'},'M117':'OLD_REVIEW_WORLD_ONLY_NOT_CURRENT_FORMAL_CITY','G5-01_axis_rule':'Retain each existing axis; adapt transverse public openings, retain ground passage and optional vertical transfer','G5-02_axis_rule':'Keep inhabited supports off existing axes; adapt gaps and open ground passages','V_rule':'Preserve existence/basic policy; no invented use or exact position','view_corridor_rule':'Adjust proposed massing to existing protected views once identified'})
    refs=[('B1','Machu Picchu','https://whc.unesco.org/en/list/274','Description; Outstanding Universal Value / Brief Synthesis'),('B2','Matera / Sassi','https://whc.unesco.org/en/list/670','Brief synthesis; Authenticity'),('B3','Göreme / Cappadocia','https://whc.unesco.org/en/list/357','Description; Brief synthesis'),('B4','Heydar Aliyev Centre','https://www.zha.com/projects/architecture/heydar-aliyev-centre?disclaimer=true','A continuous, fluid relationship; structural systems')]
    write('references.json',{'accessed_date_jst':'2026-10-23','method':'Live web read of official pages; no copyrighted images copied','references':[dict(id=i,title=t,url=u,read_sections=s,interpretation_is_research=True) for i,t,u,s in refs],'lineage':{'report':'studies/B2-G4/REPORT_ja.md','sha256':digest(BASE/'studies/B2-G4/REPORT_ja.md'),'art_status':'REJECT_PRESERVED','github_parent':'149985d50de532de1711b529e018aa1a32625678'},'W0':{'source':'user brief only','synced_sources_files_found':0,'canonical_layout':'NOT_FOUND','read_only_repository_checks':['art/b recursive tree','main recursive tree','integration/m149-source-reality-gate-20261015 recursive tree'],'legacy_coordinates_substituted':False}})
    write('history.json',{'study_id':'B2-G5','branch':'art/b','events':[{'date_jst':'2026-10-23','event':'G5_CONCEPT_RESEARCH_REQUESTED','note':'Current user brief authorizes concept research after G4 STOP; prior rejections remain.'},{'event':'TWO_INDEPENDENT_FORMATION_PRINCIPLES_DOCUMENTED','concepts':['G5-01','G5-02']},{'event':'INTERNAL_CONCEPT_COMPARISON','provisional_preference':'G5-01','formal_selection':None,'art_review_status':'NOT_REVIEWED','next_gate':'CENTRAL_SUPERVISOR_SELECTION'}],'holds':['DETAILED_3D','MINECRAFT_CONSTRUCTION','UNAPPROVED_WORK_USE'],'canonical_layout_alignment':'PENDING_SOURCE'})
    rows_html=''.join(f'<tr><td>{r["id"]}</td><td>{r["G5-01_proposed_receiver"]}</td><td>{r["G5-02_proposed_receiver"]}</td><td>端点未確認</td></tr>' for r in rows)
    page='''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>B2-G5 構想審査</title><style>body{margin:0;background:#101d29;color:#e9f0ef;font:17px/1.8 'Yu Gothic',sans-serif}main{max-width:1500px;margin:auto;padding:28px}h1,h2{color:#e4c589}a{color:#81cfc4}img{width:100%;height:auto;display:block;margin:20px 0}table{width:100%;border-collapse:collapse}td,th{padding:10px;border-bottom:1px solid #344b5b;text-align:left}aside{border-left:4px solid #cd8c83;padding:12px 24px}nav a{margin-right:20px}@media print{body{background:white;color:black}img{break-inside:avoid}}</style><main><h1>B2-G5｜都市が大地になる</h1><p>2026-10-23 / art/b / G5構想審査・revision 01</p><nav><a href="#plans">10km平面</a><a href="#section">断面</a><a href="#views">六景観</a><a href="#connections">接続</a><a href="REPORT_ja.md">研究報告全文</a></nav><aside>暫定有望案：G5-01《昇街褶都》。正式選抜は中央監督待ち。全図は構想模式図で、実3Dレンダーではありません。W0確定配置資料が未確認のため、全23対象の接続・衝突・高度整合は保留。精密3D、施工、未承認のWork利用はHOLD。</aside><img src="comparison.png" alt="昇街褶都と天架織都の独立原理比較"><h2 id="plans">10km都市の地形と中央</h2><img src="city_plans.svg" alt="二案の10km研究平面。北山岳、西断崖、東内海、南西負空間と中央提案"><h2 id="section">公共建築が生活地盤になる断面</h2><img src="sections.svg" alt="昇街褶都の高度別公共空間と天架織都の縦横都市断面"><h2 id="views">六景観の設計意図</h2><p>独立した模式画です。共通モデルからの投影やカメラ比較ではありません。各方向の審査要件は研究報告に記載しています。</p><img src="six_views.svg" alt="両案の正面・斜視・側面・背面・俯瞰・内部の計12模式画"><h2 id="connections">既定配置を保持する接続予約</h2><p>方角・用途をIDから推定せず、中央側受入口だけを仮設定。既存施設を移す計画ではありません。共有幹線と乗換口を用い、23本の専用橋を要求しません。</p><table><thead><tr><th>対象</th><th>昇街褶都</th><th>天架織都</th><th>状態</th></tr></thead><tbody>'''+rows_html+'''</tbody></table><h2>審査の結論と限界</h2><p>昇街褶都は公共建築の屋根と次の街路を反復し、接近するほど生活都市が現れる原理に優位があります。天架織都は高空地盤と内部都市を持つ支持体から別の文明像をつくります。山塊、厚い壁、巨大床への退行は両案の審査リスクです。構造、採光、風、避難、交通容量は未検証です。</p><p><a href="REPORT_ja.md">4先例・二案・断面・六景観・美術比較の全文</a> / <a href="references.json">一次資料と継承記録</a> / <a href="connections.json">接続台帳</a> / <a href="verification.json">実施済み検証</a> / <a href="manifest.json">成果物索引</a></p></main></html>'''
    (ROOT/'review.html').write_text(page,encoding='utf-8')
    page=page.replace('<h2 id="views">','<h2>巨大公共空間の生活断面</h2><img src="public_spaces.svg" alt="千光市庭と空の共同庁の公共内部・屋根上の生活・二方向の出口"><p>V1〜V3・三大都市軸・景観回廊は維持条件。M207 U/H/VとM204 X/H/Zの共通アンカーは0件、推測による座標統合は行いません。</p><h2 id="views">')
    (ROOT/'review.html').write_text(page,encoding='utf-8')
    assert len(rows)==23 and len(set(ids))==23
    slopes=[420/2100,560/2600,670/2800,750/3100]
    verification={'study_id':'B2-G5','stage':'CONCEPT','checks':{'unique_connection_ids':len(set(ids)),'H_count':6,'SB_count':16,'HERO4_count':1,'independent_principles':['ROOF_STREET_PUBLIC_BUILDING_RECURSION','ELEVATED_COMMON_GROUND_AND_INHABITED_SUPPORTS'],'primary_references':4,'svg_xml':'PASS','html_local_links':'PASS','comparison_png':'PASS'},'calculations':{'G5-01_transport_slopes_percent':[round(100*s,2) for s in slopes],'horizontal_transport_length_m':10600,'walking_2400m_rise_at_5percent_horizontal_m':48000},'not_verified':['W0_COORDINATE_ALIGNMENT','EXISTING_ENDPOINT_ALTITUDES_FUNCTIONS','COLLISION_CLEARANCE','STRUCTURE','DAYLIGHT','WIND','EGRESS','TRANSPORT_CAPACITY','3D_SILHOUETTE','INHABITABILITY'],'model_files_created':[],'measured_dimensions_m':None,'images':'DETERMINISTIC_CONCEPT_DIAGRAMS_NOT_3D_RENDERS','art_review_status':'NOT_REVIEWED','provisional_preference':'G5-01','formal_selection':None}
    verification['visual_inspection']={'method':'Assistant inspected exported PNG boards using view_image; corrected strip widths, label spacing and elevation distinctions','boards':['comparison.png','city_plans.png','sections.png','six_views.png','public_spaces.png'],'scope':'Diagram readability only; no browser or 3D rendering QA'}
    verification['coordinate_guard']={'verified_common_anchors':0,'M207_M204_transform_created':False,'legacy_M117_coordinates_used':False,'V1_V3_and_axes':'PRESERVE_UNREGISTERED'}
    import xml.etree.ElementTree as ET
    for p in ROOT.glob('*.svg'): ET.parse(p)
    import re
    for target in re.findall(r'(?:href|src)="([^"]+)"',page):
        if not target.startswith('#') and target not in ['verification.json','manifest.json']:assert (ROOT/target).is_file(),target
    with Image.open(ROOT/'comparison.png') as im:assert im.size==(1600,1000)
    write('verification.json',verification)
    files=[p for p in sorted(ROOT.iterdir()) if p.is_file() and p.name not in ['manifest.json','delivery_receipt.json']]
    assets=[{'path':p.relative_to(BASE).as_posix(),'kind':{'py':'CODE','md':'REPORT','json':'JSON','svg':'SVG','png':'PNG','html':'HTML'}[p.suffix[1:]],'sha256':digest(p),'size_bytes':p.stat().st_size} for p in files]
    manifest={'study_id':'B2-G5','branch':'art/b','revision':1,'stage':'CONCEPT','art_review_status':'NOT_REVIEWED','provisional_preference':'G5-01','formal_selection':None,'assets':assets,'holds':['DETAILED_3D','MINECRAFT_CONSTRUCTION','UNAPPROVED_WORK_USE'],'W0_alignment':'PENDING_CANONICAL_SOURCE'}
    write('manifest.json',manifest)
    index=json.loads((BASE/'latest.json').read_text(encoding='utf-8-sig'))
    index['latest']={'study_id':'B2-G5','title':'都市が大地になる — 昇街褶都／天架織都・G5構想審査','stage':'CONCEPT','art_review_status':'NOT_REVIEWED','review_authority':'Central supervisor selection pending; internal preference only','updated_at':'2026-10-22T21:10:55Z','dimensions_m':None,'proposed_dimensions_m':None,'concept_dimensions_m':{'G5-01':{'width':3800,'depth':4200,'height':2800},'G5-02':{'width':4600,'depth':3600,'height':2600}},'selected_concept':None,'provisional_preference':'G5-01','assets':assets+[{'path':'studies/B2-G5/manifest.json','kind':'JSON','sha256':digest(ROOT/'manifest.json'),'size_bytes':(ROOT/'manifest.json').stat().st_size}],'validation':{'report':'studies/B2-G5/verification.json','concept_art_review':'INTERNAL_COMPARISON_ONLY','formal_selection':'PENDING','W0_alignment':'PENDING_SOURCE','structural_feasibility':'NOT_TESTED','models_created':False},'notes':'Two independent concept principles; 4 primary references, 23 unresolved endpoints. G4 REJECT preserved. Detailed 3D, construction and unapproved Work use HOLD.'}
    # Preserve the existing reject history. Idempotent only for this revision's event.
    if not any(e.get('study_id')=='B2-G5' for e in index['history']):index['history'].append({'study_id':'B2-G5','manifest':'studies/B2-G5/manifest.json','event':'concept_submission','art_review_status':'NOT_REVIEWED','updated_at':'2026-10-22T21:10:55Z'})
    for event in index['history']:
        if event.get('study_id')=='B2-G5' and event.get('event')=='concept_submission':event['updated_at']='2026-10-22T21:10:55Z'
    index['last_submission_at']='2026-10-22T21:10:55Z'
    index['policy']='Concept preference is not formal adoption. Preserve all REJECT history. M247-C protected; Minecraft and detailed 3D HOLD; Work use requires prior approval.'
    (BASE/'latest.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'assets':len(assets)+1,'size_bytes':sum(a['size_bytes'] for a in assets),'ids':len(ids),'checks':'PASS'},ensure_ascii=False))

if __name__=='__main__':
    plans();sections();views();comparison();public_spaces();records()
