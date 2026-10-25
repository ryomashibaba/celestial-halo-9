"""Re-download all R17 delivery files at fixed commit and compare actual bytes.
Run python -B -X utf8 .../verify_remote.py SHA from repository root.
Uses existing gh authentication only if the public raw endpoint denies access.
Never emits credentials. No repository mutation.
"""
import sys,json,hashlib,urllib.request,urllib.error,subprocess,concurrent.futures
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;sha=sys.argv[1]
assert len(sha)==40 and all(c in '0123456789abcdef' for c in sha)
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',sha,'--','studies/M3D-1S/J7/R17/','studies/M3D-1S/latest.json'],text=True,encoding='utf8').splitlines()
def verify(path):
 expected=subprocess.check_output(['git','show',sha+':'+path]);url='https://raw.githubusercontent.com/ryomashibaba/celestial-halo-9/'+sha+'/'+path
 request=urllib.request.Request(url,headers={'User-Agent':'HALO9-R17-art-research-readback'})
 try:
  with urllib.request.urlopen(request,timeout=60) as response:actual=response.read()
 except urllib.error.HTTPError as e:
  if e.code not in (401,404):raise
  actual=subprocess.check_output(['gh','api','repos/ryomashibaba/celestial-halo-9/contents/'+path+'?ref='+sha,'-H','Accept: application/vnd.github.raw+json'])
 eh=hashlib.sha256(expected).hexdigest();ah=hashlib.sha256(actual).hexdigest()
 return {'path':path,'bytes':len(actual),'expected_bytes':len(expected),'sha256':ah,'expected_sha256':eh,'match':len(expected)==len(actual) and eh==ah}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(verify,paths))
out={'source':'Independent HTTPS downloads of ALL R17 deliverables and latest pointer at fixed artifact commit; bytes checked against local commit.', 'artifact_commit':sha,'checked_files':len(results),'checked_bytes':sum(r['bytes'] for r in results),'all_match':all(r['match'] for r in results),'files':results}
(R/'qa/GITHUB_READBACK.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k!='files'}));assert out['all_match']
