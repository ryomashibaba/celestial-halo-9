"""Upload explicit small C2-G5 assets as blobs/tree only. Never move a branch."""
from pathlib import Path
import json, subprocess, tempfile, base64, hashlib, concurrent.futures
R=Path(__file__).resolve().parent;W=R.parent.parent
REPO='ryomashibaba/celestial-halo-9'
HEAD='bd87de4f1bbf2aa54727b616714cdcb1a92a1c74'
BASE='22d0a68171ec8c4e15c34e216443264e1f797f34'
def api(endpoint,data=None):
 args=['gh','api','repos/'+REPO+'/'+endpoint]
 if data is not None:
  with tempfile.NamedTemporaryFile('w',encoding='utf-8',suffix='.json',dir=R,delete=False) as out:json.dump(data,out);p=Path(out.name)
  try:r=subprocess.run(args+['--method','POST','--input',str(p)],capture_output=True,text=True,encoding='utf-8')
  finally:p.unlink()
 else:r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
 if r.returncode:raise RuntimeError(r.stderr[:500])
 return json.loads(r.stdout)
assert api('git/ref/heads/art/c')['object']['sha']==HEAD,'Head moved: inspect before retry'
manifest=json.loads((R/'manifest.json').read_text(encoding='utf-8'))
paths=[a['path'] for a in manifest['assets']]+['studies/C2-G5/manifest.json','latest.json']
def upload(path):
 assert path=='latest.json' or path.startswith('studies/C2-G5/')
 raw=(W/path).read_bytes();assert len(raw)<2_000_000,'Storage review required'
 result=api('git/blobs',{'content':base64.b64encode(raw).decode(),'encoding':'base64'})
 expected=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
 assert expected==result['sha'],'Blob content mismatch'
 return {'path':path,'sha':result['sha'],'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:receipts=list(pool.map(upload,paths))
tree=api('git/trees',{'base_tree':BASE,'tree':[{'path':r['path'],'mode':'100644','type':'blob','sha':r['sha']} for r in receipts]})
receipt={'branch':'art/c','parent_sha':HEAD,'base_tree':BASE,'tree_sha':tree['sha'],'files':receipts,'branch_moved':False}
(R/'upload_receipt.local.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({'tree_sha':tree['sha'],'files':len(receipts),'bytes':sum(r['bytes'] for r in receipts),'parent_sha':HEAD}))
