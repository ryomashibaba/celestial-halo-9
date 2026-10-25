"""Compare manifest hashes with exact staged Git blobs in one batch."""
import sys,json,subprocess,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;repo=R.parents[3];prefix=R.relative_to(repo).as_posix()+'/'
m=json.loads((R/'MANIFEST_SHA256.json').read_text(encoding='utf8'))
paths=[prefix+x['path'] for x in m['files']]
raw=subprocess.check_output(['git','cat-file','--batch'],input=''.join(':'+p+'\n' for p in paths).encode(),cwd=repo)
offset=0;bad=[]
for row in m['files']:
    end=raw.index(b'\n',offset);header=raw[offset:end].split();assert header[1]==b'blob',header
    size=int(header[2]);offset=end+1;blob=raw[offset:offset+size];offset+=size+1
    if size!=row['bytes'] or hashlib.sha256(blob).hexdigest()!=row['sha256']:bad.append(row['path'])
assert not bad,bad
names=subprocess.check_output(['git','diff','--cached','--name-only'],text=True,cwd=repo).splitlines()
assert len(names)==len(m['files'])+1 and all(n.startswith(prefix) for n in names),names
print('STAGED_MANIFEST_PASS',len(m['files']),'/',len(m['files']),'all bytes match')
print('SCOPE_PASS',len(names),'R28 additions only')
