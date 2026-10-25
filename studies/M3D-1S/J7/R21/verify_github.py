"""Exact GitHub HTTPS byte readback of the committed R21 package. No writes.
Existing gh credentials remain in memory and are only sent to GitHub HTTPS.
"""
import sys, json, hashlib, subprocess, urllib.request, concurrent.futures, time
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;commit=sys.argv[1]
assert len(commit)==40 and all(c in '0123456789abcdef' for c in commit)
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',commit,'--','studies/M3D-1S/J7/R21/'],text=True,encoding='utf8').splitlines()
credential=subprocess.check_output(['gh','auth','token'],text=True).strip()
def check(path):
    expected=subprocess.check_output(['git','show',commit+':'+path])
    req=urllib.request.Request('https://raw.githubusercontent.com/ryomashibaba/celestial-halo-9/'+commit+'/'+path,
          headers={'Authorization':'Bearer '+credential,'Accept-Encoding':'identity','User-Agent':'HALO9-R21-readback'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=90) as response:actual=response.read()
            break
        except Exception:
            if attempt==2:raise
            time.sleep(1+attempt)
    return dict(path=path,bytes=len(actual),sha256=hashlib.sha256(actual).hexdigest(),
                expected_sha256=hashlib.sha256(expected).hexdigest(),match=actual==expected)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(check,paths))
out=dict(artifact_commit=commit,checked_files=len(results),checked_bytes=sum(v['bytes'] for v in results),all_match=all(v['match'] for v in results),files=results)
(R/'qa/GITHUB_READBACK.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k!='files'}));assert out['all_match']
