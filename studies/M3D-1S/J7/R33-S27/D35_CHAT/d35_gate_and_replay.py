#!/usr/bin/env python3
"""D35 stage-critical automated fail-closed gate on SAVED real GLB; separate-process replay.
This gate reports not-ready. It is NOT automatic objective artistic quality assessment.
"""
import subprocess,tempfile,json,hashlib,sys,shutil
from pathlib import Path
import numpy as np
from PIL import Image
O=Path(__file__).parent

def hashpath(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run():
 files=['d35_civic_urban_section.py']
 with tempfile.TemporaryDirectory(prefix='halo9_d35_') as d:
  for name in files:shutil.copy2(O/name,Path(d)/name)
  proc=subprocess.run([sys.executable,str(Path(d)/files[0])],cwd=d,capture_output=True,text=True,timeout=60)
  if proc.returncode:raise RuntimeError(proc.stdout+'\n'+proc.stderr)
  replay={k:{'actual_sha256':hashpath(O/f'D35_{k}_URBAN_CANYON.glb'),'isolated_replay_sha256':hashpath(Path(d)/f'D35_{k}_URBAN_CANYON.glb')} for k in ['BASE','REVERSE_SKEW']}
  for k,v in replay.items():v['exact_match']=v['actual_sha256']==v['isolated_replay_sha256']
  assert all(v['exact_match'] for v in replay.values())
 qa={k:json.loads((O/f'D35_{k}_QA.json').read_text()) for k in ['BASE','REVERSE_SKEW']}
 dims={k:{'geometry_count':v['readback_geometry_count'],'triangle_count':v['readback_triangle_count'],'watertight_meshes':v['readback_individually_watertight'],'geometry_sha':v['glb_sha256'],'ramp_grades_percent':[round(x['linear_fit_grade_percent'],3) for x in v['sampled_ramps']],'ramp_max_percent':max(x['linear_fit_grade_percent'] for x in v['sampled_ramps'])} for k,v in qa.items()}
 # after camera repair: prove eye is ABOVE the actual civic floor surface, rather than hidden within it
 from d35_render import CAM
 eye=CAM['canyon_human'][0]
 assert eye[2]>3.0+1.0
 from itertools import product
 views=['south','west','east','north','aerial','canyon_human','side_human','elevated_civic']
 pixel_differences={}
 for v in views:
  a=np.asarray(Image.open(O/f'D35_BASE_{v}.png').convert('RGB'),dtype=np.int16)
  b=np.asarray(Image.open(O/f'D35_REVERSE_SKEW_{v}.png').convert('RGB'),dtype=np.int16)
  assert a.shape==b.shape
  pixel_differences[v]=round(100*np.mean(np.max(np.abs(a-b),axis=2)>18),3)
 tests={
 'positive_flat_ramp_regression':None,
 'negative_steep_ramp_regression':None,
 }
 # A separate synthetic numerical sanity test for the expected PCA longitudinal slope estimator.
 def calc(t,z):
  t=np.array(t,dtype=float);z=np.array(z,dtype=float);return abs(np.dot(t-t.mean(),z-z.mean())/np.dot(t-t.mean(),t-t.mean()))
 tests['positive_flat_ramp_regression']=bool(calc(np.linspace(0,100,101),np.linspace(0,4,101))<=.05)
 tests['negative_steep_ramp_regression']=bool(calc(np.linspace(0,100,101),np.linspace(0,55,101))>.05)
 assert all(tests.values())
 result={'study':'R33-S27-D35','main_policy':'CITY_MASTER_3D_FIRST','art_gate':{'BASE':'REJECT','REVERSE_SKEW':'REJECT','independent_professional_art_review':False,'rationale':['repeated open horizontal floor plates with no visually coherent inhabitable exterior','macroform merely changes curve of shelves and is not a civilisation','civic void remains an empty public canyon, not architectural destination']},'technical_gate':'FAIL','failure_reasons':['4 of 4 inspected grade ramps exceed selected 5% research threshold in both variants','upper crossing transfers and lift service are not verified','interior habitable apartments and vertical paths remain incomplete'], 'replay':replay,'dimensions_and_ramps':dims,'paired_camera_pixel_difference_percent_threshold18':pixel_differences,'paired_cameras_same_geometry_angles':True,'camera_fix':{'original_eye_z':2.0,'civic_floor_top_z':3.0,'revised_eye_z':eye[2],'revised_eye_above_floor':True},'test_sanity':tests,'canonical_M247C_modified':False,'minecraft_construction':'HOLD','city_master_complete':False,'formal_art_adoption':0,'chat_without_Work':True}
 p=O/'D35_GATE_AND_REPLAY.json';p.write_text(json.dumps(result,indent=2,ensure_ascii=False))
 print(json.dumps({'replay':{k:v['exact_match'] for k,v in replay.items()},'ramps_max_percent':{k:v['ramp_max_percent'] for k,v in dims.items()},'art':'REJECT','tech':'FAIL','pixel_diffs':pixel_differences,'camera_fixed':True},indent=2))
 return result
if __name__=='__main__':run()
