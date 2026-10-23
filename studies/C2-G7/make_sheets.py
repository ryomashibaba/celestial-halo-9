"""Light review contacts; no image generation or edits to G6 source renders."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json
R=Path(__file__).resolve().parent;FONT='C:/Windows/Fonts/meiryo.ttc'
def f(s):return ImageFont.truetype(FONT,s)
def contact(prefix,name,title,labels):
 im=Image.new('RGB',(1920,610),'#10262e');d=ImageDraw.Draw(im)
 d.text((24,15),title,font=f(27),fill='#eef0e7')
 d.text((24,57),'C2-G7 / FINAL MODEL REVIEW / 抽象都市背景・正式施設配置ではない',font=f(18),fill='#b5c7c4')
 for i,(key,label) in enumerate(labels):
  with Image.open(R/(prefix+key+'.jpg')) as src:p=ImageOps.fit(src,(640,480))
  im.paste(p,(i*640,95));d.text((i*640+15,580),label,font=f(19),fill='#e4bf84')
 for quality in [86,80,74,68,60]:
  im.save(R/name,quality=quality,optimize=True,subsampling=0)
  if (R/name).stat().st_size<=600000:break
 assert (R/name).stat().st_size<=600000
 return {'file':name,'bytes':(R/name).stat().st_size,'pixels':list(im.size),'quality':quality}
if __name__=='__main__':
 result=contact('g6_','preview.jpg','G6 会流天蓋 A：最終 A.blend からの再出力', [('oblique','斜視：同一の最終形状'),('side','側面：街路の切込み'),('back','背面：大きな連続面')])
 if (R/'new_oblique.jpg').exists():result['new']=contact('new_','new_comparison.jpg','G7 N1 交室都宮：公共室の接合から変える低詳細形', [('oblique','斜視'),('side','側面'),('back','背面')])
 (R/'sheet_metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(result)
