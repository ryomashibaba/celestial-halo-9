"""Offline artifact hashes. python -B -X utf8."""
import sys,json,hashlib,struct,ast
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
for p in R.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
data=(R/'model/R32_A.glb').read_bytes()
magic,version,size=struct.unpack('<4sII',data[:12]);assert magic==b'glTF' and version==2 and size==len(data)
rows=[]
for p in sorted(R.rglob('*')):
    if p.is_file() and p.name!='MANIFEST_SHA256.json':
        assert '__pycache__' not in p.parts
        b=p.read_bytes();rows.append({'path':p.relative_to(R).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(R/'MANIFEST_SHA256.json').write_text(json.dumps({'scope':'R32 only, manifest itself excluded','files':rows,'total_bytes_excluding_manifest':sum(r['bytes'] for r in rows)},ensure_ascii=False,indent=2),encoding='utf8',newline='\n')
print('MANIFEST_READY',len(rows),sum(r['bytes'] for r in rows))
