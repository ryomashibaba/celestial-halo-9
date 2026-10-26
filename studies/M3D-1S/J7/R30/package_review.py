"""Build review sheets from actual Blender renders, prune only R30 temporary output.
Run with bundled Python -B -X utf8 (Pillow). No image synthesis or painted geometry.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,ast,sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
FONT='C:/Windows/Fonts/meiryo.ttc'
def font(n):return ImageFont.truetype(FONT,n)
BG='#14242b';FG='#e8e3d3';MUT='#aebec4'
labels={'01_CITY':'都市全域 / 共通カメラ','02_CENTRAL':'中央斜視 / 共通カメラ','03_PUBLIC':'代表公共空間 / 各案の実床・別位置','04_HUMAN':'実床上1.7m / 共通カメラ','05_REAR':'背面 / 共通カメラ','06_UNDERSIDE':'下面 / 共通カメラ','07_SKY_STREET':'高所街路 / 各案の実床・別位置'}
def sheet(path,title,subtitle,rows,cols=2,w=800,h=500):
    pad=16;top=116;rowh=h+70
    out=Image.new('RGB',(cols*w+(cols+1)*pad,top+len(rows)*rowh+pad),BG);d=ImageDraw.Draw(out)
    d.text((pad,14),title,font=font(28),fill=FG);d.text((pad,62),subtitle,font=font(17),fill=MUT)
    for j,row in enumerate(rows):
        for i,(p,label) in enumerate(row):
            im=Image.open(p).convert('RGB');im=im.resize((w,h),Image.Resampling.LANCZOS)
            x=pad+i*(w+pad);y=top+j*rowh;out.paste(im,(x,y));d.text((x,y+h+9),label,font=font(18),fill=FG)
    out.save(R/path,quality=91,subsampling=0)

names=['01_CITY','02_CENTRAL','03_PUBLIC','04_HUMAN','05_REAR','06_UNDERSIDE','07_SKY_STREET']
sheet('comparison/AB_NEUTRAL.jpg','R30-A 潮裂聖都  /  R30-B 懸海天都 — 中性形状比較','同一縮尺・光・1600×1000。03/07は空間の役割を比較。正式美術採択なし。',[[ (R/f'renders/{v}_clay_{n}.png',v+' — '+labels[n]) for v in ('A','B')] for n in names])
sheet('comparison/AB_ART.jpg','R30 — 材質込みの実3D比較','全画像は保存BLENDのCycles描画。AIによる後付け建築・背景合成なし。',[[ (R/f'renders/{v}_art_{n}.png',v+' — '+labels[n]) for v in ('A','B')] for n in ['02_CENTRAL','03_PUBLIC','04_HUMAN','07_SKY_STREET']])
sheet('comparison/AB_KEY.jpg','R30-A 潮裂聖都  /  R30-B 懸海天都','上：中性形状 / 下：材質込み。同じ実モデル・同じ中央カメラ。正式採択なし。',[[ (R/f'renders/{v}_{style}_02_CENTRAL.png',v+' — '+('形状' if style=='clay' else '材質込み')) for v in ('A','B')] for style in ('clay','art')])
sheet('comparison/ITERATION_SHAPE.jpg','初期形状 → 反復編集後（中性材質）','02・04は各案の前後で同一カメラ。後の単なる画角変更を形状改善に加算しない。',[[ (R/f'process/{v}_clay_{n}.png',v+' 初期'),(R/f'renders/{v}_clay_{n}.png',v+' 最終')] for v,n in [('A','02_CENTRAL'),('B','02_CENTRAL'),('A','04_HUMAN'),('B','04_HUMAN')]])
sheet('comparison/FAILED_EDITS.jpg','途中失敗の記録 — 最終成果と区別','上段：不正な上部欠落と閉塞。下段：最終の修正形状・空間。前後は異なる撮影条件を含む。',[
    [(R/'process/revision2/B_clay_02_CENTRAL.png','B v2失敗：上部が不正に消失'),(R/'process/revision2/B_art_07_SKY_STREET.png','B v2失敗：近い親構造が視線を塞ぐ')],
    [(R/'renders/B_clay_02_CENTRAL.png','B最終：上部を保持した開口'),(R/'renders/B_art_07_SKY_STREET.png','B最終：全親構造の実切削と街路再設計')]])
sheet('comparison/R29_A_B_REFERENCE.jpg','R29 → R30-A / R30-B — 同条件の中央斜視','R29も原BLENDからR30共通カメラ・中性材質・太陽で再描画。Aの美術的優越を保証しない。',[
    [(R/'comparison/R29_clay_02_CENTRAL.png','R29 基準'),(R/'renders/A_clay_02_CENTRAL.png','R30-A'),(R/'renders/B_clay_02_CENTRAL.png','R30-B')]],cols=3,w=600,h=375)

# Only this task's redundant previews/backups are pruned, never previous studies.
keep={'A_clay_02_CENTRAL.png','A_clay_04_HUMAN.png','B_clay_02_CENTRAL.png','B_clay_04_HUMAN.png'}
keep2={'B_clay_02_CENTRAL.png','B_art_07_SKY_STREET.png'}
for p in (R/'process').glob('*.png'):
    assert R.resolve() in p.resolve().parents
    if p.name not in keep:p.unlink()
for p in (R/'process/revision2').glob('*.png'):
    assert R.resolve() in p.resolve().parents
    if p.name not in keep2:p.unlink()
for name in ('R30_A.blend1','R30_B.blend1'):
    p=R/'model'/name
    if p.exists():p.unlink()
for category,predicate in [('RENDER_LOG.txt',lambda n:'render' in n or 'preview' in n),('BUILD_EDIT_EXPORT_LOG.txt',lambda n:'render' not in n and 'preview' not in n)]:
    logs=[p for p in sorted((R/'process').glob('*.log')) if predicate(p.name)]
    if logs:
        with (R/'process'/category).open('a',encoding='utf8') as out:
            for p in logs:out.write('\nFILE: '+p.name+'\n'+p.read_text(encoding='utf8',errors='replace'))
        for p in logs:p.unlink()

for p in R.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
images=[]
for p in sorted((R/'renders').glob('*.png')):
    with Image.open(p) as im:
        im.verify()
    images.append(p.relative_to(R).as_posix())
assert len(images)==22,len(images)
record=dict(final_render_count=22,neutral=14,material=8,matched_original_reference=1,full_sheets=6,initial_previews_retained=4,failed_previews_retained=2,source='Actual saved BLEND, Cycles/OPTIX; 1600x1000, 48 samples, same sun/sky/exposure. No ImageGen.',images=images)
(R/'qa/REVIEW_PACKAGE.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
files=[]
for p in sorted(R.rglob('*')):
    if p.is_file() and p.name!='MANIFEST_SHA256.json':
        raw=p.read_bytes();files.append(dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
(R/'MANIFEST_SHA256.json').write_text(json.dumps(dict(scope='R30 only; manifest excludes itself',files=files),ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(files=len(files)+1,bytes=sum(f['bytes'] for f in files),max_file_bytes=max(f['bytes'] for f in files),render_count=len(images)),indent=2))
