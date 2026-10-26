"""Compose actual Blender images only. python -B -X utf8; no image generation."""
import sys,json,ast,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
def font(n):return ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',n)
def sheet(file,title,subtitle,rows,w=640,h=400):
    pad=16;top=108;rh=h+58;cols=len(rows[0])
    im=Image.new('RGB',(cols*w+(cols+1)*pad,top+len(rows)*rh+pad),'#14242b');draw=ImageDraw.Draw(im)
    draw.text((pad,12),title,font=font(25),fill='#e8e3d3');draw.text((pad,60),subtitle,font=font(15),fill='#bdc8cb')
    for j,row in enumerate(rows):
        for i,(p,label) in enumerate(row):
            src=Image.open(p).convert('RGB').resize((w,h),Image.Resampling.LANCZOS)
            x=pad+i*(w+pad);y=top+j*rh;im.paste(src,(x,y));draw.text((x,y+h+9),label,font=font(15),fill='#e8e3d3')
    im.save(R/'comparison'/file,quality=92,subsampling=0)
names=['01_CITY','02_CENTRAL','08_FRONT','04_HUMAN','07_SKY_STREET','05_REAR','06_UNDERSIDE']
labels=['全市遠景','中央斜視','正面','地上実床＋1.7m','旧2190m視点：R32は壁内・無効','背面','下面']
def source(v,s,n):
    if v==30 and n=='08_FRONT':return R.parent/'R31/renders/baseline/clay_08_FRONT.png'
    return R.parent/f'R{v}'/('renders' if v==30 else 'renders/final')/(('B_' if v==30 else '')+s+'_'+n+'.png')
sheet('KEY.jpg','R30-B → R31-A → R32-A《天層共都》：Gate A REJECT',
      '上：中性、下：素材。三つの都市地形を実造形。巨大レールは脱したが、反復街区・無地壁へ収束。',
      [[(source(v,s,'02_CENTRAL'),f'R{v} / '+s) for v in (30,31,32)] for s in ('clay','art')])
sheet('FIXED_SEVEN.jpg','R30-B → R31-A → R32-A：固定7視点の実3D比較',
      '1600×1000 / Cycles48samples / 同カメラ・太陽・空・露出・尺度。黒い旧高所視点も省略しない。',
      [[(source(v,'clay',n),f'R{v} / '+label) for v in (30,31,32)] for n,label in zip(names,labels)])
sheet('MATERIAL_HUMAN.jpg','地上・旧高所街路：素材を含む実画像',
      '地上は同じ実床。旧高所視点のR32は質量内のため、居住空間や採光の成功証拠として扱えない。',
      [[(source(v,'art',n),f'R{v} / '+label) for v in (30,31,32)] for n,label in [('04_HUMAN','地上'),('07_SKY_STREET','旧高所視点')]])
sheet('EXPLORATORY_FORUM.jpg','R32：実床上の探索視点（旧カメラ比較と分離）',
      '同一の新視点：床上1.7m。空は見えるが、単調な積層街区と広い空床。Stage4の詳細公共室は未制作。',
      [[(source(32,s,'09_EXPLORATORY_FORUM'),'R32 / 新しい2190m公共床 / '+s) for s in ('clay','art')]],w=800,h=500)
sheet('MACRO_REVISION.jpg','R32：初回 → 一度の大形状修正 → REJECTで停止',
      'カメラ・光・尺度は固定。初回960×600/16samples、最終1600×1000/48samples。微修正の継続なし。',
      [[(R/'process/initial'/('clay_'+n+'.png'),'初回：分散する小街区と縦塔'),(source(32,'clay',n),'修正後：厚い都市地盤・反復壁が残る')] for n in ('02_CENTRAL','05_REAR')],w=800,h=500)
# Prune previews whose geometry is fully represented in final renders. Exact R32
# paths only; neither old studies nor any source data are deleted.
revised=R/'process/revised'
if revised.exists():
    for n in ('02_CENTRAL','05_REAR','06_UNDERSIDE','07_SKY_STREET','08_FRONT'):
        (revised/('clay_'+n+'.png')).unlink(missing_ok=True)
    (revised/'conditions_clay.json').unlink(missing_ok=True);revised.rmdir()
for n in ('06_UNDERSIDE','08_FRONT'):(R/'process/initial'/('clay_'+n+'.png')).unlink(missing_ok=True)
for p in R.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
images=[]
for p in sorted(R.rglob('*')):
    if p.suffix.lower() in ('.png','.jpg'):
        with Image.open(p) as im:im.verify()
        images.append(p.relative_to(R).as_posix())
(R/'qa/REVIEW_PACKAGE.json').write_text(json.dumps({'final_renders':16,'fixed_camera_renders':14,'invalid_old_sky_camera_renders_included':2,'exploratory_renders':2,'initial_failure_previews':3,'review_sheets':5,'images':images,
    'method':'Only resizing and labels on actual Cycles renders. No ImageGen, retouch, synthetic geometry or background compositing. No duplicate baseline images copied into R32.'},ensure_ascii=False,indent=2),encoding='utf8')
print('IMAGE_PACKAGE_VERIFIED',len(images))
