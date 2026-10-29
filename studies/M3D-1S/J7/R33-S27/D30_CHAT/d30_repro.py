#!/usr/bin/env python3
"""Run another interpreter in temporary cwd against just code, source GLB and recipes."""
import tempfile,shutil,subprocess,sys,json,hashlib,io
from pathlib import Path
import numpy as np
import trimesh
P=Path(__file__).resolve().parent
from d30_freeform_csg import carve,sha,TARGET,GRID_SPACING,load

def rejects(fn):
    try:fn()
    except (ValueError,KeyError,TypeError):return True
    return False

def main():
    base=(P/'D30_BASE.glb').read_bytes();results={}
    with tempfile.TemporaryDirectory(prefix='d30-isolated-') as t:
        t=Path(t);shutil.copy(P/'d30_freeform_csg.py',t/'d30_freeform_csg.py');(t/'source.glb').write_bytes(base)
        for phase in ('TUNNEL','ROOM','SKYLIGHT'):
            fn=f'D30_PLAN_{phase}.json';shutil.copy(P/fn,t/fn)
            out=t/f'{phase}.glb'
            run=subprocess.run([sys.executable,str(t/'d30_freeform_csg.py'),str(t/'source.glb'),str(t/fn),str(out)],cwd=t,
                capture_output=True,text=True,timeout=60,check=True)
            expected=(P/f'D30_{phase}.glb').read_bytes()
            results[phase]={'isolated_glb_sha256_match':sha(out.read_bytes())==sha(expected),
                'saved_sha256':sha(expected),'saved_bytes':len(expected),
                'isolated_process':True}
            assert results[phase]['isolated_glb_sha256_match'],(phase,run.stdout)
        assert base==(t/'source.glb').read_bytes()
    plan=json.loads((P/'D30_PLAN_SKYLIGHT.json').read_text('utf-8'))
    bads={
        'baseline_sha_mismatch':lambda:carve(base,dict(plan,baseline_sha256='0'*64)),
        'protected_target':lambda:carve(base,dict(plan,target_geometry='PROTECTED_CIVIC_ROUTE')),
        'wrong_operation_order':lambda:carve(base,dict(plan,operations=['skylight','atrium'])),
        'atrium_without_tunnel':lambda:carve(base,dict(plan,operations=['atrium'])),
        'grid_mismatch':lambda:carve(base,dict(plan,grid_m=4.0)),
        'unknown_key':lambda:carve(base,dict(plan,untrusted=True)),
    }
    negatives={key:rejects(fn) for key,fn in bads.items()}
    assert all(negatives.values()),negatives
    report={'study':'D30','reproduction':results,'negative_controls':negatives,
            'source_glb_sha256':sha(base),'source_unchanged':sha((P/'D30_BASE.glb').read_bytes())==sha(base)}
    (P/'D30_REPRO.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
