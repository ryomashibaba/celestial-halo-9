"""Contact sheets only: labels and scaling of genuine renders, no content synthesis."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
R=Path(__file__).parent
try:
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
except OSError:
    font=ImageFont.load_default(size=22);small=ImageFont.load_default(size=16)
names=['E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL']
def sheet(versions,name,width=640):
    height=int(width*.75);out=Image.new('RGB',(width*3,(height+40)*len(versions)),(235,235,231));d=ImageDraw.Draw(out)
    for j,ver in enumerate(versions):
        for i,cam in enumerate(names):
            im=Image.open(R/ver/(cam+'.png')).convert('RGB');im.resize((width,height),Image.Resampling.LANCZOS)
            im.thumbnail((width,height),Image.Resampling.LANCZOS)
            out.paste(im,(i*width,j*(height+40)+40))
            d.text((i*width+12,j*(height+40)+8),ver+' | '+cam.replace('E11_',''),font=small,fill=(20,25,27))
    out.save(R/name,quality=92)
sheet(['R0','R1','R2'],'E11_FIXED_CAMERA_R0_R1_R2_ART_REJECT.jpg')
sheet(['R2'],'E11_FINAL_TRUE_THREE_VIEW_ART_REJECT.jpg',800)
source=R.parent/'D48_R4_E10'/'e10_evidence'/'E10_REAL_NATIVE_THREE_VIEW_ART_UNREVIEWED.jpg'
old=Image.open(source).convert('RGB');old.thumbnail((2400,565),Image.Resampling.LANCZOS)
new=Image.open(R/'E11_FINAL_TRUE_THREE_VIEW_ART_REJECT.jpg').convert('RGB')
out=Image.new('RGB',(2400,old.height+new.height+70),(235,235,231));d=ImageDraw.Draw(out)
d.text((12,7),'E10 frozen reference - ART REJECT (different cameras / composition)',font=font,fill=(20,25,27))
out.paste(old,(0,35));d.text((12,old.height+42),'E11 R2 genuine Blender - ART REJECT - no formal adoption',font=font,fill=(20,25,27))
out.paste(new,(0,old.height+70));out.save(R/'E10_E11_CONTEXT_NOT_SAME_CAMERA.jpg',quality=92)
# Public log excerpt: no private machine path, include real success/failure markers only.
lines=[]
for log in ['render_R0.log','render_R1.log','render_R2.log','verify_raw.log']:
    p=R/log
    if p.exists():
        content=p.read_text(encoding='utf-8',errors='replace')
        content=content.replace(str(R),'<E11_RESEARCH>').replace(str(R).replace('\\','/'),'<E11_RESEARCH>')
        lines.append('=== '+log+' ===\n'+content)
(R/'EXECUTION_LOG_SANITIZED.txt').write_text('\n\n'.join(lines),encoding='utf-8')
print('GENUINE_RENDER_CONTACT_SHEETS_SAVED')
