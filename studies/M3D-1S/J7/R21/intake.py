"""Inspect the user ZIP as data; never execute its bundled scripts."""
import hashlib, json, struct, zipfile, subprocess
from pathlib import Path
R = Path(__file__).resolve().parent
R.mkdir(exist_ok=True)
zpath = Path(r'C:\Users\ryoma\Downloads\C55A_independent_research_payload.zip')
sha = lambda b: hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(zpath) as z:
    assert z.testzip() is None
    checks = []
    for line in z.read('MANIFEST_SHA256.txt').decode().splitlines():
        digest, name = line.split(maxsplit=1)
        name = name.removeprefix('./')
        checks.append(dict(path=name, sha256=sha(z.read(name)), match=sha(z.read(name)) == digest))
    assert all(x['match'] for x in checks)
    for name in z.namelist():
        if name.endswith('/') or name.startswith('renders/') or name == 'push_to_github.sh':
            continue
        dest = R / 'source' / name
        assert dest.resolve().is_relative_to((R / 'source').resolve())
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(z.read(name))
b = (R / 'source/model/C55A_SevenfoldHaloRift.glb').read_bytes()
assert sha(b) == '4e0d8092c2bbe59ad6553d81e1a44594e7ff0dac3cfbc1ce1a9fb60144b76ae0'
j = json.loads(b[20:20+struct.unpack_from('<I', b, 12)[0]])
tri = sum(j['accessors'][p['indices']]['count']//3 for m in j['meshes'] for p in m['primitives'])
out = dict(zip_original_path=str(zpath), zip_sha256=sha(zpath.read_bytes()), zip_crc_pass=True,
           recorded_filename_differs=True, identity_by_glb_hash=True, manifest_checks=checks,
           glb_sha256=sha(b), glb_triangles=tri, meshes=len(j['meshes']), nodes=len(j['nodes']), materials=len(j['materials']),
           source_scripts_executed=False, git_start_head='5d83a66de5ac4208f0da24c4208aa1deb0ba84c1',
           r20_verified_head='8ed17bcb0078e5fcd276e5db72954791d2ae1338',
           r19_original_sha256=sha((R.parent/'R19/final/R19_LIVING_HORIZON.blend').read_bytes()))
(R/'SOURCE_VERIFICATION.json').write_text(json.dumps(out, indent=2), encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k!='manifest_checks'}, indent=2))
