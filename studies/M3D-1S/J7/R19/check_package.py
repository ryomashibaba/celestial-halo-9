"""Offline evidence checks. Run python -B -X utf8 .../check_package.py."""
from pathlib import Path
import sys,json,hashlib,struct
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check():
 cases=['initial/R19_INITIAL','revision_1/R19_REVISION_1','revision_2/R19_LIVING_HORIZON','final/R19_LIVING_HORIZON','sections/XZ_Y200/XZ_Y200','sections/YZ_X0/YZ_X0']
 checks=[]
 for stem in cases:
  bl=R/(stem+'.blend');gl=R/(stem+'.glb')
  raw=bl.read_bytes();gb=gl.read_bytes();magic,version,length=struct.unpack('<4sII',gb[:12])
  checks.append(dict(id=stem,blend_nonempty=len(raw)>1000,glb_header_valid=magic==b'glTF' and version==2 and length==len(gb)))
 for directory in ['initial','final']:
  for name in ['01_FRONT','02_OBLIQUE','03_SIDE','04_REAR','05_AERIAL','06_UNDERSIDE']:
   p=R/directory/(name+'.png');b=p.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n' and len(b)>10000
 qa=json.loads((R/'qa/BLEND_GLB_READBACK.json').read_text(encoding='utf8'));assert qa['basic_persistence_pass']
 for v in checks:assert v['blend_nonempty'] and v['glb_header_valid']
 images=[]
 for folder in ['initial','revision_1','revision_2','final','sections','context']:
  images.extend((R/folder).rglob('*.png'))
 for p in images:assert p.stat().st_size>10000
 out={'offline_pass':True,'model_pairs':checks,'real_blender_pngs':len(images),'persistence_pass':qa['basic_persistence_pass'],'does_not_certify':'Art, walking, traffic operation, connected enclosed void volume, structural or occupancy safety, W0 anchoring.'}
 (R/'qa/OFFLINE_PACKAGE_CHECK.json').write_text(json.dumps(out,indent=2),encoding='utf8')
 manifest={str(p.relative_to(R)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':digest(p)} for p in R.rglob('*') if p.is_file() and p.suffix in ('.blend','.glb','.png','.jpg')}
 (R/'qa/ASSET_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':check()
