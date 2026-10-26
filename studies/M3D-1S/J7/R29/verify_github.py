"""Download fixed-commit R29 files over authenticated HTTPS; receipt outside repo.
Token stays in memory and is never printed or written. Compare actual git bytes.
"""
import sys,json,hashlib,subprocess,urllib.request,concurrent.futures
from pathlib import Path
sys.dont_write_bytecode=True
commit=sys.argv[1];receipt=Path(sys.argv[2])
assert len(commit)==40 and all(c in '0123456789abcdef' for c in commit)
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',commit,'--','studies/M3D-1S/J7/R29/'],text=True,encoding='utf8').splitlines()
token=subprocess.check_output(['gh','auth','token'],text=True).strip()
def check(path):
    expected=subprocess.check_output(['git','show',commit+':'+path])
    req=urllib.request.Request('https://raw.githubusercontent.com/ryomashibaba/celestial-halo-9/'+commit+'/'+path,headers={'Authorization':'Bearer '+token,'Accept-Encoding':'identity','User-Agent':'HALO9-R29-readback'})
    with urllib.request.urlopen(req,timeout=180) as r:actual=r.read()
    return {'path':path,'bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest(),'expected_sha256':hashlib.sha256(expected).hexdigest(),'match':actual==expected}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(check,paths))
out={'artifact_commit':commit,'all_match':all(r['match'] for r in rows),'file_count':len(rows),'total_bytes':sum(r['bytes'] for r in rows),'method':'Authenticated actual HTTPS download against git show bytes at fixed commit','files':rows}
receipt.write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k!='files'}));assert out['all_match']
