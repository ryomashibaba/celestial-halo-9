"""Verify staged R32 bytes vs working artifacts and manifest. Offline -B -X utf8."""
import sys,json,subprocess,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;repo=R.parents[3];prefix='studies/M3D-1S/J7/R32/'
def git(*args):return subprocess.check_output(['git',*args],cwd=repo)
rows=git('diff','--cached','--name-status').decode().splitlines()
paths=[]
for row in rows:
    status,path=row.split('\t');assert status=='A' and path.startswith(prefix),row
    paths.append(path);assert git('show',':'+path)==(repo/path).read_bytes(),path
manifest=json.loads((R/'MANIFEST_SHA256.json').read_text(encoding='utf8'))
for row in manifest['files']:
    b=(R/row['path']).read_bytes()
    assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],row['path']
assert len(paths)==len(manifest['files'])+1
print(json.dumps({'staged_R32_additions_only':True,'staged_and_working_bytes_identical':len(paths),'manifest_verified':len(manifest['files']),'total_staged_bytes':sum((repo/p).stat().st_size for p in paths)}))
