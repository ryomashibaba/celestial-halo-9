"""Layout actual Blender render pixels only; no painted/generated architecture."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
dest=sys.argv[1];items=sys.argv[2:];cols=3 if len(items)>6 else 2
w=600;h=590;im=Image.new('RGB',(w*cols,h*((len(items)+cols-1)//cols)),(18,27,34));dr=ImageDraw.Draw(im)
for i,p in enumerate(items):
 src=R/p;pic=Image.open(src).convert('RGB');pic.thumbnail((w,h-34));x=(i%cols)*w+(w-pic.width)//2;y=(i//cols)*h+32
 im.paste(pic,(x,y));dr.text(((i%cols)*w+12,(i//cols)*h+10),p,fill='white')
out=R/dest;out.parent.mkdir(parents=True,exist_ok=True);im.save(out,quality=92)
print(str(out))
