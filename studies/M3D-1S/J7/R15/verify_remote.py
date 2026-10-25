"""Re-download each delivered model/image through HTTPS at a fixed commit.
Uses gh's existing authentication internally only if the private repo requires it.
"""
import sys,json,hashlib,urllib.request,concurrent.futures,subprocess
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;sha=sys.argv[1]
assert len(sha)==40 and all(c in '0123456789abcdef' for c in sha)
manifest=json.loads((R/'qa/MODEL_IMAGE_MANIFEST.json').read_text('utf8'))
prefix='https://raw.githubusercontent.com/ryomashibaba/celestial-halo-9/'+sha+'/studies/M3D-1S/J7/R15/'
def verify(rec):
 request=urllib.request.Request(prefix+rec['path'],headers={'User-Agent':'HALO9-R15-research-readback'})
 try:
  with urllib.request.urlopen(request,timeout=50) as resp:data=resp.read()
 except urllib.error.HTTPError as e:
  if e.code not in (401,404):raise
  # gh API retrieves binary bytes with Accept raw; no credential is printed or saved.
  data=subprocess.check_output(['gh','api','repos/ryomashibaba/celestial-halo-9/contents/studies/M3D-1S/J7/R15/'+rec['path']+'?ref='+sha,'-H','Accept: application/vnd.github.raw+json'])
 h=hashlib.sha256(data).hexdigest()
 return dict(path=rec['path'],bytes=len(data),sha256=h,match=len(data)==rec['bytes'] and h==rec['sha256'])
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(verify,manifest))
out=dict(source='Independent HTTPS file byte downloads at fixed commit; not local Git objects',commit=sha,checked_files=len(results),checked_bytes=sum(x['bytes'] for x in results),all_match=all(x['match'] for x in results),files=results)
(R/'qa/GITHUB_READBACK.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k!='files'}));assert out['all_match']
