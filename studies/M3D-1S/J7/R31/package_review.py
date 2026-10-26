"""Compose labelled comparisons from actual Blender images (Pillow), no geometry painting.
Offline invocation: python -B -X utf8 package_review.py. No old research is modified.
"""
import sys,json,hashlib,ast
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
BG='#14242b';FG='#e8e3d3';MUT='#afbdc3'
def font(n):return ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',n)
def sheet(file,title,subtitle,rows,w=640,h=400):
    cols=len(rows[0]);pad=16;top=106;rh=h+58
    out=Image.new('RGB',(cols*w+(cols+1)*pad,top+len(rows)*rh+pad),BG);d=ImageDraw.Draw(out)
    d.text((pad,12),title,font=font(26),fill=FG);d.text((pad,59),subtitle,font=font(16),fill=MUT)
    for j,row in enumerate(rows):
        for i,(path,label) in enumerate(row):
            im=Image.open(path).convert('RGB').resize((w,h),Image.Resampling.LANCZOS)
            x=pad+i*(w+pad);y=top+j*rh;out.paste(im,(x,y));d.text((x,y+h+8),label,font=font(16),fill=FG)
    out.save(R/'comparison'/file,quality=91,subsampling=0)
names=['01_CITY','02_CENTRAL','04_HUMAN','07_SKY_STREET','05_REAR','06_UNDERSIDE']
labels={'01_CITY':'全市遠景','02_CENTRAL':'中央斜視','03_PUBLIC':'1000m公共街路','04_HUMAN':'地上実床＋1.7m','07_SKY_STREET':'2190m街路＋1.7m','05_REAR':'背面','06_UNDERSIDE':'下面','08_FRONT':'正面'}
base=lambda n:R.parent/'R30/renders'/('B_clay_'+n+'.png')
final=lambda n:R/'renders/final'/('clay_'+n+'.png')
initial=lambda n:R/'process/initial'/('clay_'+n+'.png')
sheet('R30_INITIAL_FINAL.jpg','R30-B → R31-A 初回 → 修正後 — 実3D形状比較',
      '固定カメラ・同じ太陽／空／縮尺。初回960×600/16samples、R30・修正後1600×1000/48samples。',
      [[(base(n),'R30-B / '+labels[n]),(initial(n),'R31初回 / '+labels[n]),(final(n),'R31修正後 / '+labels[n])] for n in names])
sheet('R30_R31_NEUTRAL.jpg','R30-B → R31-A — 中性材質・全視点',
      '両方1600×1000/48samples、同カメラ・光・尺度。上部の骨格化と未解決の無地面も含めて審査。',
      [[(base(n),'R30-B / '+labels[n]),(final(n),'R31-A / '+labels[n])] for n in names+['03_PUBLIC']],w=800,h=500)
sheet('KEY.jpg','R30-B → R31-A《昇界織都》 — Gate A: HOLD',
      '上：中性形状、下：素材込み。大きく変わったことを美術的突破の証明にはしない。',
      [[(R.parent/'R30/renders'/('B_'+s+'_02_CENTRAL.png'),'R30-B / '+s),
        (R/'renders/final'/(s+'_02_CENTRAL.png'),'R31-A / '+s)] for s in ('clay','art')],w=800,h=500)
sheet('MATERIAL_HUMAN.jpg','R30-B → R31-A — 素材込み・同条件',
      '色を消した形状判定とは別評価。白銀・暗色・金属で断面差は読めるが、生活密度の不足は解消しない。',
      [[(R.parent/'R30/renders'/('B_art_'+n+'.png'),'R30-B / '+labels[n]),
        (R/'renders/final'/('art_'+n+'.png'),'R31-A / '+labels[n])] for n in ['02_CENTRAL','04_HUMAN','07_SKY_STREET']],w=800,h=500)
sheet('FRONT.jpg','R30-B → R31-A — 補足の共通正面',
      'R30原BLENDから同条件で追加描画。R30原本と既存画像への上書きなし。',
      [[(R/'renders/baseline/clay_08_FRONT.png','R30-B / 正面'),(final('08_FRONT'),'R31-A / 正面')]],w=800,h=500)
sheet('ITERATIONS.jpg','R31-A — 実画像を見た主形状の修正',
      '同じ中央斜視。初回→居住断面化→駅と東環境室→貫通公共室。工程数は美術改善の証明ではない。',
      [[(initial('02_CENTRAL'),'v1：細い骨格・反復した縦長地区'),(R/'renders/revision2/clay_02_CENTRAL.png','v2：主構造の居住断面化')],
       [(R/'renders/revision3/clay_02_CENTRAL.png','v3：駅・東環境室・地上接続'),(final('02_CENTRAL'),'v4：背面まで貫通する実公共室')]],w=800,h=500)
sheet('FAILED_EAST_PUBLIC.jpg','東乗換室の未成立 — 成功画像から除外',
      '左は近い壁、右は採光不足。別カメラ位置であり形状の前後比較ではない。床QA合格でも美術は不合格。',
      [[(R/'renders/revision3/clay_09_EAST_PUBLIC.png','試し撮り：巨大な近接壁が支配'),(final('09_EAST_PUBLIC'),'最終試し撮り：極端に暗い乗換室')]],w=800,h=500)
for p in R.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
images=[]
for p in sorted(R.rglob('*')):
    if p.suffix.lower() in ('.png','.jpg'):
        with Image.open(p) as im:im.verify()
        images.append(p.relative_to(R).as_posix())
out={'actual_final_renders':15,'final_primary_review_renders':13,'final_failed_east_room_shots':2,'fixed_six_before_initial_after':True,'R30_existing_renders_reused_without_duplicate':True,'R30_extra_front':1,'initial_preview_resolution':[960,600],'final_resolution':[1600,1000],'comparison_method':'Actual Cycles images resized only for labelled review sheets. No ImageGen, retouch, added geometry or background compositing.','images':images}
(R/'qa/REVIEW_PACKAGE.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('REVIEW_SHEETS_READY',len(images))
