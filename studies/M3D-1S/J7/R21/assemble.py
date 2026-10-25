"""Contact sheets from unchanged actual Blender renders and real cut edges."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parent
O=R/'sheets';O.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',18)
small=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',14)
def sheet(name,rows,header):
    w,h=640,360;hh=36
    out=Image.new('RGB',(w*2,(h+hh)*len(rows)+60),'#1c252b');d=ImageDraw.Draw(out)
    d.text((15,12),header,font=font,fill='white')
    for row,(label,a,b) in enumerate(rows):
        for col,(path,who) in enumerate([(a,'R19'),(b,'C55-A')]):
            x=col*w;y=60+row*(h+hh)
            d.text((x+10,y+5),who+' | '+label,font=small,fill='white')
            if path and path.exists():
                im=Image.open(path).convert('RGB');im.thumbnail((w,h));out.paste(im,(x+(w-im.width)//2,y+hh+(h-im.height)//2))
            else:d.text((x+20,y+100),'NO EQUIVALENT IMAGE',font=small,fill='#c3c9ce')
    out.save(O/name,quality=92)
for regime in ['fixed16km','fit']:
    views=['front','oblique','side','rear','aerial','underside']
    sheet(regime+'_SIX.jpg',[(v,R/'renders/R19'/f'{regime}_{v}.png',R/'renders/C55A'/f'{regime}_{v}.png') for v in views],
          'CLAY / no decals / 50 deg H / '+('same centre distance 16 km' if regime=='fixed16km' else 'individual fit distances; NO scale change'))
sheet('FLOORS.jpg',[(v,R/'renders/R19'/f'floor_{v}.png',R/'renders/C55A'/f'floor_{v}.png') for v in ['low','mid','high','axis_entry','axis_middle','axis_arrival']],
      'ACTUAL FLOOR + 1.7 m / clay / 50 deg H / local support, continuous walking UNVERIFIED')
sheet('MATERIALS.jpg',[(v,R/'renders/R19'/f'material_{v}.png',R/'renders/C55A'/f'material_{v}.png') for v in ['open_oblique','rear','underside','floor_axis_middle','floor_high']],
      'ORIGINAL PBR / same light / emission OFF / C55-A decal geometry ON')
sheet('OPEN_OBLIQUE.jpg',[('open oblique CLAY',R/'renders/R19/fit_open_oblique.png',R/'renders/C55A/fit_open_oblique.png'),
      ('supported low / both pitch 15 deg',R/'renders/R19/floor_low_axis15.png',R/'renders/C55A/floor_low_axis15.png')],
      'R21 ACTUAL BLENDER COMPARISON / original dimensions / 50 deg H')
sheet('SECTIONS.jpg',[(label,R.parent/'R19/sections'/old/(old+'.png'),R/'renders/C55A'/('section_'+new+'.png'))
      for label,old,new in [('longitudinal','XZ_Y200','longitudinal_X860'),('cross','YZ_X0','cross_Yminus600')]],
      'REAL MESH CUTS / R19 prior evidence reused (different studio) / C55-A new cuts, UNCAPPED')
for path in (R/'qa').glob('C55A_CUT_*.json'):
    j=json.loads(path.read_text(encoding='utf8'));axis=j['plane_axis'];horizontal=1-axis
    seg=j['cut_segments'];points=[p for e in seg for p in e['points_m']]
    xmin=min(p[horizontal] for p in points);xmax=max(p[horizontal] for p in points);zmin=min(p[2] for p in points);zmax=max(p[2] for p in points)
    W,H=1800,1100;scale=min((W-80)/(xmax-xmin),(H-120)/(zmax-zmin))
    im=Image.new('RGB',(W,H),'#f5f5f2');dr=ImageDraw.Draw(im)
    dr.text((30,15),path.stem+' | actual triangle/plane intersection; no inferred solid fill',font=font,fill='black')
    for e in seg:
        color='#cf591b' if ('hall' in e['object'] or 'gallery' in e['object'] or 'vault' in e['object']) else '#236a9b' if 'wall' in e['object'] else '#707070'
        coords=[(40+(p[horizontal]-xmin)*scale,H-40-(p[2]-zmin)*scale) for p in e['points_m']]
        dr.line(coords,fill=color,width=2)
    dr.text((35,H-28),'Blue: massif surfaces   Orange: great hall surfaces   Grey: other geometry',font=small,fill='black')
    im.save(O/(path.stem.replace('_CUT_','_SECTION_')+'_CONTOUR.png'))
print('CONTACT_SHEETS',len(list(O.iterdir())))
