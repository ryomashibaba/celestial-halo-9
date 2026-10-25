from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
R=Path(__file__).resolve().parents[1]
for idx in range(1,7):
 files=[next((R/'renders').glob(f'{state}_{idx:02d}_*.png')) for state in ['before','after']]
 canvas=Image.new('RGB',(1600,580),'#eeeeee');d=ImageDraw.Draw(canvas)
 for k,p in enumerate(files):
  im=Image.open(p).convert('RGB');im.thumbnail((800,545));canvas.paste(im,(800*k,35));d.text((800*k+12,10),p.stem,fill='black')
 canvas.save(R/'renders'/f'comparison_{idx:02d}.jpg',quality=94)
d=json.loads((R/'qa/ACTUAL_SECTION.json').read_text())
fig,axs=plt.subplots(2,1,figsize=(13,9),sharex=True,sharey=True)
for ax,state in zip(axs,['before','after']):
 for new,color in [(False,'#64748b'),(True,'#d8572a')]:
  lines=[s['yz'] for s in d[state] if s['object'].startswith('R25_')==new]
  ax.add_collection(LineCollection(lines,colors=color,linewidths=1.1))
 ax.set_xlim(550,1050);ax.set_ylim(500,850);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_ylabel('Native Z (m)');ax.set_title(state+' / actual triangle-plane intersections, X = -430 m')
axs[-1].set_xlabel('Native Y (m)');fig.suptitle('Finite section: existing geometry gray, new geometry orange. Not closed-solid proof.')
fig.tight_layout();fig.savefig(R/'renders/actual_section.png',dpi=130);plt.close(fig)
files={str(p.relative_to(R)).replace('\\','/'):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for folder in ['models','renders'] for p in sorted((R/folder).glob('*')) if p.is_file()}
(R/'qa/ARTIFACT_HASHES.json').write_text(json.dumps(files,indent=2),encoding='utf8')
