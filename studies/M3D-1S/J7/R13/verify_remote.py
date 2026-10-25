"""Re-download every delivered model/image/specification by immutable commit SHA."""
import sys
sys.dont_write_bytecode=True
import json,hashlib,urllib.request,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).parent
sha=sys.argv[1]
assert len(sha)==40 and all(c in '0123456789abcdef' for c in sha)
manifest=json.loads((ROOT/'qa/MODEL_IMAGE_MANIFEST.json').read_text(encoding='utf8'))
prefix='https://raw.githubusercontent.com/ryomashibaba/celestial-halo-9/'+sha+'/studies/M3D-1S/J7/R13/'
def verify(record):
    req=urllib.request.Request(prefix+record['path'],headers={'User-Agent':'HALO9-R13-artifact-readback'})
    with urllib.request.urlopen(req,timeout=45) as response:data=response.read()
    digest=hashlib.sha256(data).hexdigest()
    return dict(path=record['path'],bytes=len(data),sha256=digest,
                match=len(data)==record['bytes'] and digest==record['sha256'])
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(verify,manifest))
out=dict(source='Independent HTTPS raw file byte downloads, not local Git objects',commit=sha,
         checked_files=len(records),checked_bytes=sum(r['bytes'] for r in records),
         all_match=all(r['match'] for r in records),files=records)
(ROOT/'qa/GITHUB_READBACK.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k!='files'}))
assert out['all_match']
