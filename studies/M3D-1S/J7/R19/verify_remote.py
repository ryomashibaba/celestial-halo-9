"""Download committed R19 delivery bytes through GitHub HTTPS, compare SHA256.
Uses existing gh auth; never prints or stores credentials. No GitHub writes.
Run from repo: python -B -X utf8 studies/M3D-1S/J7/R19/verify_remote.py COMMIT.
"""
import sys,json,hashlib,subprocess,concurrent.futures,urllib.request,urllib.error
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;sha=sys.argv[1]
assert len(sha)==40 and all(c in '0123456789abcdef' for c in sha)
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',sha,'--','studies/M3D-1S/J7/R19/','studies/M3D-1S/latest.json'],text=True,encoding='utf8').splitlines()
# Existing account credential is used only in-memory for the same GitHub repo.
# Never print, persist, interpolate into a shell, or transmit it outside GitHub.
credential=subprocess.check_output(['gh','auth','token'],text=True).strip()
def verify(path):
 expected=subprocess.check_output(['git','show',sha+':'+path])
 url='https://raw.githubusercontent.com/ryomashibaba/celestial-halo-9/'+sha+'/'+path
 request=urllib.request.Request(url,headers={'Authorization':'Bearer '+credential,'Accept-Encoding':'identity','User-Agent':'HALO9-R19-byte-readback'})
 with urllib.request.urlopen(request,timeout=60) as response:actual=response.read()
 eh=hashlib.sha256(expected).hexdigest();ah=hashlib.sha256(actual).hexdigest()
 return {'path':path,'bytes':len(actual),'expected_bytes':len(expected),'sha256':ah,'expected_sha256':eh,'match':expected==actual}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(verify,paths))
out={'artifact_commit':sha,'source':'Independent GitHub HTTPS contents downloads, full exact bytes against local artifact commit','checked_files':len(results),'checked_bytes':sum(r['bytes'] for r in results),'all_match':all(r['match'] for r in results),'files':results}
(R/'qa/GITHUB_READBACK.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in out.items() if k!='files'}));assert out['all_match']
