"""Byte-for-byte HTTPS download verification of this new study at a fixed commit.
Existing gh credential is retained in memory, only sent to GitHub HTTPS, never logged.
Run from repo. Output receipt is outside repo to avoid recursive commits.
"""
import sys,json,hashlib,subprocess,urllib.request,concurrent.futures
from pathlib import Path
sys.dont_write_bytecode=True
commit=sys.argv[1];receipt=Path(sys.argv[2])
assert len(commit)==40 and all(c in '0123456789abcdef' for c in commit)
prefix='studies/M3D-1S/J7/R27B/'
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',commit,'--',prefix],text=True,encoding='utf8').splitlines()
token=subprocess.check_output(['gh','auth','token'],text=True).strip()
def check(path):
    expected=subprocess.check_output(['git','show',commit+':'+path])
    request=urllib.request.Request('https://raw.githubusercontent.com/ryomashibaba/celestial-halo-9/'+commit+'/'+path,
        headers={'Authorization':'Bearer '+token,'Accept-Encoding':'identity','User-Agent':'HALO9-R27B-readback'})
    with urllib.request.urlopen(request,timeout=90) as response:actual=response.read()
    return {'path':path,'bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest(),
            'expected_sha256':hashlib.sha256(expected).hexdigest(),'match':actual==expected}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: rows=list(pool.map(check,paths))
out={'artifact_commit':commit,'all_match':all(x['match'] for x in rows),'file_count':len(rows),
     'total_bytes':sum(x['bytes'] for x in rows),'method':'Actual authenticated HTTPS download at fixed commit vs git show bytes',
     'files':rows}
receipt.write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k!='files'}));assert out['all_match']
