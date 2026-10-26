"""Download every R32 fixed-commit artifact; exact byte compare with local Git.
python -B -X utf8 verify_github.py COMMIT RECEIPT_OUTSIDE_REPO
The existing gh credential stays in memory and is never printed.
"""
import sys,json,hashlib,subprocess,urllib.request,concurrent.futures
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;repo=R.parents[3]
commit=sys.argv[1];receipt=Path(sys.argv[2]).resolve()
assert len(commit)==40 and all(c in '0123456789abcdef' for c in commit)
assert repo.resolve() not in receipt.parents
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',commit,'--','studies/M3D-1S/J7/R32/'],cwd=repo,text=True,encoding='utf8').splitlines()
token=subprocess.check_output(['gh','auth','token'],text=True).strip()
def check(path):
    expected=subprocess.check_output(['git','show',commit+':'+path],cwd=repo)
    req=urllib.request.Request('https://raw.githubusercontent.com/ryomashibaba/celestial-halo-9/'+commit+'/'+path,headers={'Authorization':'Bearer '+token,'Accept-Encoding':'identity','User-Agent':'HALO9-R32-readback'})
    with urllib.request.urlopen(req,timeout=180) as response:actual=response.read()
    return {'path':path,'bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest(),'expected_sha256':hashlib.sha256(expected).hexdigest(),'match':actual==expected}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(check,paths))
out={'artifact_commit':commit,'all_match':all(r['match'] for r in rows),'file_count':len(rows),'total_bytes':sum(r['bytes'] for r in rows),
     'method':'Actual authenticated HTTPS download of all fixed-commit R32 files, including BLEND, GLB and every image; byte equality to git show.','files':rows}
receipt.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k!='files'}));assert out['all_match']
