"""Final offline package checks and byte manifest. Invoke after final edits."""
import sys,json,hashlib,ast,struct
from pathlib import Path
from PIL import Image
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
for p in R.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
for p in R.rglob('*'):
    if p.suffix.lower() in ('.jpg','.png'):
        with Image.open(p) as im:im.verify()
glb=(R/'model/R31_A.glb').read_bytes();magic,ver,size=struct.unpack('<4sII',glb[:12])
assert magic==b'glTF' and ver==2 and size==len(glb)
assert (R/'model/R31_A.blend').read_bytes().startswith((b'BLENDER',b'\x28\xb5\x2f\xfd'))
qa=json.loads((R/'qa/SAVED_MODELS.json').read_text(encoding='utf8'))
assert all(qa['glb_match'].values()) and all(qa['original_7_cameras_unchanged'].values())
assert all(x['limited_floor_pass'] for x in qa['human_cameras'])
assert json.loads((R/'qa/SOURCE_INTEGRITY.json').read_text(encoding='utf8'))['all_unchanged']
files=[]
for p in sorted(R.rglob('*')):
    if p.is_file() and p.name!='MANIFEST_SHA256.json':
        assert p.suffix not in ('.pyc','.log','.blend1')
        raw=p.read_bytes();files.append({'path':p.relative_to(R).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
(R/'MANIFEST_SHA256.json').write_text(json.dumps({'files':files,'total_bytes_excluding_manifest':sum(x['bytes'] for x in files)},ensure_ascii=False,indent=2),encoding='utf8')
print('PACKAGE_VALID',len(files)+1,'files',sum(x['bytes'] for x in files),'bytes excluding manifest')
