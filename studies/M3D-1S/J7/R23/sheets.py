import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parent
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
def sheet(stage,names,output):
    names=[n for n in names if (R/stage/'renders'/(n+'.png')).exists()]
    w,h=720,505;out=Image.new('RGB',(w*2,h*((len(names)+1)//2)),(30,34,39));d=ImageDraw.Draw(out)
    for i,n in enumerate(names):
        p=R/stage/'renders'/(n+'.png')
        if not p.exists():continue
        im=Image.open(p).convert('RGB');im.thumbnail((720,480));x=i%2*w;y=i//2*h
        out.paste(im,(x,y+25));d.text((x+12,y+2),stage.upper()+' / '+n,font=font,fill='white')
    out.save(R/output,quality=92)
if __name__=='__main__':
    stage=sys.argv[1]
    sheet(stage,['front','oblique','side','rear','aerial','underside'],stage+'/SIX.jpg')
    sheet(stage,['ground_1p7','mid_1p7','high_1p7','rear_city'],stage+'/FLOORS.jpg')
    if stage=='final':
        out=Image.new('RGB',(2160,510),(30,34,39));d=ImageDraw.Draw(out)
        for i,stage in enumerate(['initial','revision','final']):
            im=Image.open(R/stage/'renders/oblique.png').convert('RGB');im.thumbnail((720,480));out.paste(im,(i*720,30));d.text((i*720+12,3),stage.upper()+' / identical camera',font=font,fill='white')
        out.save(R/'EVOLUTION.jpg',quality=93)
