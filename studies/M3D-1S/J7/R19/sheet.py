"""Compose unchanged render pixels for review; no architecture synthesis."""
from pathlib import Path
from PIL import Image, ImageDraw
import sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
dest=sys.argv[1];items=sys.argv[2:];cols=3 if len(items)>4 else 2
w=640;h=580;im=Image.new('RGB',(w*cols,h*((len(items)+cols-1)//cols)),(17,25,30));d=ImageDraw.Draw(im)
for i,p in enumerate(items):
 src=Image.open(R/p).convert('RGB');src.thumbnail((w,h-30));x=(i%cols)*w+(w-src.width)//2;y=(i//cols)*h+30
 im.paste(src,(x,y));d.text(((i%cols)*w+12,(i//cols)*h+9),p,fill='white')
(R/dest).parent.mkdir(parents=True,exist_ok=True);im.save(R/dest,quality=93)
print(R/dest)
