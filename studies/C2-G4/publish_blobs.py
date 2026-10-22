"""Upload an explicit manifest using authenticated gh; create only blobs + a tree.
This script NEVER moves any branch. Branch commit/update is a separate leased action.
Network is needed; no credentials are read or printed by this script.
"""
from pathlib import Path
import json,subprocess,base64,hashlib,concurrent.futures,tempfile,time
R=Path(__file__).resolve().parent;W=R.parent.parent
REPO='ryomashibaba/celestial-halo-9';BASE='4da0fa34d75b78f5227926506e2321f574c6d5cb';HEAD='36599732dc82d1496851a30d70d38bcd0cf7f44b'
def api(path,data=None):
    args=['gh','api','repos/'+REPO+'/'+path]
    if data is not None:
        with tempfile.NamedTemporaryFile('w',suffix='.json',encoding='utf-8',delete=False,dir=R) as f:
            json.dump(data,f);fn=Path(f.name)
        try:
            p=subprocess.run(args+['--method','POST','--input',str(fn)],capture_output=True,text=True,encoding='utf-8')
        finally:fn.unlink()
    else:p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
    if p.returncode:raise RuntimeError(p.stderr[:500])
    return json.loads(p.stdout)
assert api('git/ref/heads/art/c')['object']['sha']==HEAD,'Branch moved: inspect before proceeding'
manifest=json.loads((R/'manifest.json').read_text(encoding='utf-8'))
paths=list(manifest['files'])+['studies/C2-G4/manifest.json','latest.json']
receiptpath=R/'blob_receipt.json';done=json.loads(receiptpath.read_text()) if receiptpath.exists() else {}
def upload(path):
    p=W/path;raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest()
    if path in done and done[path]['sha256']==h:return path,done[path]
    assert path=='latest.json' or path.startswith('studies/C2-G4/')
    assert len(raw)<10_000_000,'Large file requires a storage decision'
    if path in manifest['files']:assert h==manifest['files'][path]['sha256']
    res=api('git/blobs',dict(content=base64.b64encode(raw).decode('ascii'),encoding='base64'))
    return path,dict(sha=res['sha'],sha256=h,bytes=len(raw))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    for fut in concurrent.futures.as_completed([ex.submit(upload,p) for p in paths]):
        path,v=fut.result();done[path]=v;receiptpath.write_text(json.dumps(done,indent=2),encoding='utf-8');print('STORED',path,flush=True)
tree=api('git/trees',dict(base_tree=BASE,tree=[dict(path=p,mode='100644',type='blob',sha=done[p]['sha']) for p in paths]))
(R/'upload_tree_receipt.json').write_text(json.dumps(dict(tree_sha=tree['sha'],parent_sha=HEAD,branch='art/c',files=len(paths)),indent=2))
print('TREE',tree['sha'],'FILES',len(paths),flush=True)
