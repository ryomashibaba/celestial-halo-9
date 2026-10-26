"""Offline release checks; optional --staged compares exact Git index bytes."""
import sys,json,hashlib,ast,subprocess,struct
from pathlib import Path
from PIL import Image
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;REPO=R.parents[3];PREFIX=R.relative_to(REPO).as_posix()+'/'
def git(*a):return subprocess.check_output(['git',*a],cwd=REPO)
for p in R.glob('*.py'):ast.parse(p.read_text(encoding='utf8'),filename=str(p))
manifest=json.loads((R/'MANIFEST_SHA256.json').read_text(encoding='utf8'))
for row in manifest['files']:
    raw=(R/row['path']).read_bytes()
    assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],row['path']
for p in (R/'renders').glob('*.png'):
    with Image.open(p) as im:assert im.size==(1600,1000),p
for name in ['02_CENTRAL_CHOIR','03_FORUM_HUMAN','06_REAR_NORTH','08_WHOLE_CITY']:
    assert (R/'comparison'/('R28_'+name+'.png')).read_bytes()==(R.parent/'R28/renders'/(name+'.png')).read_bytes()
raw=(R/'model/R29_TIDAL_COMMONS.glb').read_bytes();magic,version,size=struct.unpack('<4sII',raw[:12])
assert magic==b'glTF' and version==2 and size==len(raw)
staged=[]
if '--staged' in sys.argv:
    staged=git('diff','--cached','--name-only').decode().splitlines()
    assert staged and all(p.startswith(PREFIX) for p in staged),staged
    for p in staged:assert git('show',':'+p)==(REPO/p).read_bytes(),p
assert not git('diff','--name-only').strip(),'Unexpected unstaged tracked edits'
assert not any(p.name=='__pycache__' for p in R.rglob('*'))
assert all(p.stat().st_size<100_000_000 for p in R.rglob('*') if p.is_file())
print(json.dumps({'manifest_files_matched':len(manifest['files']),'python_syntax_files':len(list(R.glob('*.py'))),'final_renders':len(list((R/'renders').glob('*.png'))),'R28_copied_render_bytes_matched':4,'glb_header_and_length_pass':True,'staged_exact_bytes_matched':len(staged),'scope':'Only R29 staged; no unstaged tracked changes; all original R28 bytes checked separately'},ensure_ascii=False))
