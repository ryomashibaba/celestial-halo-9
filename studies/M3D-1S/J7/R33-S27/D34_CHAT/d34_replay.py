#!/usr/bin/env python3
"""Verify that an isolated second process can rebuild identical real GLB from source."""
from pathlib import Path
import tempfile,subprocess,sys,hashlib,json,shutil
root=Path(__file__).parent
with tempfile.TemporaryDirectory(prefix='halo9-d34-replay-') as d:
  d=Path(d);shutil.copy2(root/'d34_civic_section.py',d/'d34_civic_section.py')
  r=subprocess.run([sys.executable,str(d/'d34_civic_section.py')],cwd=d,capture_output=True,text=True,timeout=60,check=True)
  orig=(root/'D34_CIVIC_THREE_LEVEL_REAL.glb').read_bytes();rebuilt=(d/'D34_CIVIC_THREE_LEVEL_REAL.glb').read_bytes()
  assert hashlib.sha256(orig).hexdigest()==hashlib.sha256(rebuilt).hexdigest(), 'GLB differs'
  obj={'independent_subprocess_source_only_glb_sha256_match':True,'actual_glb_sha256':hashlib.sha256(orig).hexdigest(),'source_sha256':hashlib.sha256((root/'d34_civic_section.py').read_bytes()).hexdigest(), 'source_recreated_mesh_count':json.loads(r.stdout)['meshes']}
  (root/'D34_REPRO_QA.json').write_text(json.dumps(obj,indent=2))
  print(obj)
