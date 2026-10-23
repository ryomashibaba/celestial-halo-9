"""Explicit C2-G7 upload, small files only; creates blobs/tree, never moves a ref."""
from pathlib import Path
import json, subprocess, tempfile, base64, hashlib, concurrent.futures
R=Path(__file__).resolve().parent;W=R.parent.parent
REPO='ryomashibaba/celestial-halo-9'
HEAD='aaa0696f0239d05eda60c6bfeffe528363d8af3d'
BASE='7446cd1e4773da1c95eb8521b505ac9975e2dad7'
def api(endpoint,data=None):
 args=['gh','api','repos/'+REPO+'/'+endpoint]
 if data is not None:
  with tempfile.NamedTemporaryFile('w',encoding='utf-8',suffix='.json',dir=R,delete=False) as out:json.dump(data,out);p=Path(out.name)
  try:r=subprocess.run(args+['--method','POST','--input',str(p)],capture_output=True,text=True,encoding='utf-8')
  finally:p.unlink()
 else:r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
 if r.returncode:raise RuntimeError(r.stderr[:500])
 return json.loads(r.stdout)
assert api('git/ref/heads/art/c')['object']['sha']==HEAD,'Head changed: inspect before retry'
manifest=json.loads((R/'manifest.json').read_text(encoding='utf-8'))
assets={a['path']:a for a in manifest['assets']}
paths=list(assets)+['studies/C2-G7/manifest.json','latest.json']
receipt_path=R/'upload_receipt.local.json'
previous=json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
cache={x['path']:x for x in previous.get('files',[])}
def upload(path):
 assert path=='latest.json' or path.startswith('studies/C2-G7/')
 raw=(W/path).read_bytes();assert len(raw)<10_000_000,'Large file needs storage decision'
 h=hashlib.sha256(raw).hexdigest()
 if path in assets:assert h==assets[path]['sha256']
 if path in cache and cache[path]['sha256']==h:return cache[path]
 result=api('git/blobs',{'content':base64.b64encode(raw).decode(),'encoding':'base64'})
 expected=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert expected==result['sha']
 return {'path':path,'sha':result['sha'],'sha256':h,'bytes':len(raw)}
receipts=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for r in pool.map(upload,paths):
  receipts.append(r);receipt_path.write_text(json.dumps({'files':receipts},indent=2),encoding='utf-8');print('STORED',r['path'],flush=True)
tree=api('git/trees',{'base_tree':BASE,'tree':[{'path':r['path'],'mode':'100644','type':'blob','sha':r['sha']} for r in receipts]})
receipt={'branch':'art/c','parent_sha':HEAD,'base_tree':BASE,'tree_sha':tree['sha'],'files':receipts,'branch_moved':False}
receipt_path.write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps({'tree_sha':tree['sha'],'files':len(receipts),'bytes':sum(r['bytes'] for r in receipts),'parent_sha':HEAD}))
