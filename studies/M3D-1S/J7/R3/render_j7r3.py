"""VTK off-screen renders from actual saved GLB, with fixed camera metadata and no photoreal claims."""
import json, math, os
import numpy as np
import trimesh, vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
from collections import defaultdict
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).parent
GLB=OUT/'J7R3_FRACTURED_INHABITED_CIVIC_SKY_NONCANONICAL.glb'
scene=trimesh.load(GLB,force='scene',process=False)
print('import',len(scene.geometry),scene.bounds)
# GLB glTF coordinate convention is y up; scene geometry converted by trimesh back to z up consistently
# verified by bounds relative to source
if not (3900<scene.bounds[1,2]<5000):
 print('WARNING unexpected Z up bounds',scene.bounds)
parts=defaultdict(list)
for name,geom in scene.dump(concatenate=False)[0].items() if False else []:pass
# scene.dump() returns transformed Trimesh list; material colors survive per-vertex
for m in scene.dump(concatenate=False):
 if not isinstance(m,trimesh.Trimesh):continue
 if m.visual.kind=='vertex':rgba=np.median(m.visual.vertex_colors,axis=0).astype(int)
 else:rgba=np.array([180,190,205,255]);
 col=tuple(int(x) for x in rgba[:3]); parts[col].append(m)
print('palette groups',len(parts))
renderer=vtk.vtkRenderer(); renderer.SetBackground(0.055,0.075,0.105);renderer.SetBackground2(0.20,0.26,0.30);renderer.GradientBackgroundOn()
win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1350,850);win.SetMultiSamples(4);win.AddRenderer(renderer)
allactors={}
for rgb,meshs in parts.items():
 V=[];F=[];offset=0
 for m in meshs:
  v=np.asarray(m.vertices,dtype=np.float32);f=np.asarray(m.faces,dtype=np.int64)
  V.append(v);F.append(f+offset);offset+=len(v)
 vs=np.concatenate(V);fs=np.concatenate(F)
 pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(vs,deep=True));cells=vtk.vtkCellArray()
 ids=np.hstack([np.full((len(fs),1),3,dtype=np.int64),fs]).reshape(-1)
 cells.SetCells(len(fs),numpy_to_vtkIdTypeArray(ids,deep=True));poly=vtk.vtkPolyData();poly.SetPoints(pts);poly.SetPolys(cells)
 normals=vtk.vtkPolyDataNormals();normals.SetInputData(poly);normals.ConsistencyOn();normals.AutoOrientNormalsOff();normals.SplittingOff();normals.Update()
 mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
 actor=vtk.vtkActor();actor.SetMapper(mapper)
 actor.GetProperty().SetColor(*[x/255 for x in rgb]);actor.GetProperty().SetAmbient(.18);actor.GetProperty().SetDiffuse(.70);actor.GetProperty().SetSpecular(.18);actor.GetProperty().SetSpecularPower(28)
 renderer.AddActor(actor)
 allactors[rgb]=actor
cam=renderer.GetActiveCamera();cam.ParallelProjectionOn()
cam.SetClippingRange(.1,40000)
views=[
('01_FRONT',[0,-10000,4600],[0,0,1900],11200),
('02_OBLIQUE',[7500,-8500,6400],[0,0,1900],11200),
('03_SIDE',[11000,0,4900],[0,0,1900],11200),
('04_REAR',[0,10300,4800],[0,0,1900],11200),
('05_AERIAL',[6500,-6500,13500],[0,0,1900],11200),
('06_GROUND',[0,-11000,560],[0,0,1900],11200),
('07_REVERSE_DIAGONAL',[-7500,7000,6600],[0,0,1900],11200),
('08_CIVIC_COURT',[2400,-2600,2900],[-30,20,1650],3300),
]
view_results=[]
for name,pos,focal,scale in views:
 cam.SetPosition(*pos);cam.SetFocalPoint(*focal);cam.SetViewUp(0,0,1);cam.SetParallelScale(scale/2)
 renderer.ResetCameraClippingRange();win.Render()
 filt=vtk.vtkWindowToImageFilter();filt.SetInput(win);filt.SetInputBufferTypeToRGB();filt.ReadFrontBufferOff();filt.Update()
 writer=vtk.vtkPNGWriter();file=str(OUT/(name+'.png'));writer.SetFileName(file);writer.SetInputConnection(filt.GetOutputPort());writer.Write()
 # add clear exact status label on actual render
 img=Image.open(file).convert('RGB');d=ImageDraw.Draw(img,'RGBA')
 d.rectangle([0,0,1350,78],fill=(6,15,24,210));d.text((25,15),'CELESTIAL HALO-9  |  J7-R3  |  '+name,fill=(235,242,248,255),font=ImageFont.load_default(size=23))
 tag='SAME 10km CITY FRAME  |  NONCANONICAL' if name!='08_CIVIC_COURT' else 'LOCAL VIEW (NOT SCALE-COMPARABLE)'
 d.text((25,49),tag+'  |  REAL GLB RENDER  |  ART HOLD',fill=(142,208,216,255),font=ImageFont.load_default(size=16))
 img.save(file)
 view_results.append({'file':name+'.png','camera_m':pos,'target_m':focal,'orthographic_vertical_extent_m':scale,'classification':'FIXED_CITY_FRAME' if name!='08_CIVIC_COURT' else 'LOCAL_NOT_SCALE_COMPARABLE'})
 print('view',name,Path(file).stat().st_size)
# contact sheet for human side-by-side judging
imgs=[Image.open(OUT/(v['file'])).convert('RGB') for v in view_results]
small=[]
for im in imgs:
 w=665;h=420
 small.append(im.resize((w,h),Image.Resampling.LANCZOS))
sheet=Image.new('RGB',(1330,1680),(11,22,32))
for i,img in enumerate(small):sheet.paste(img,((i%2)*665,(i//2)*420))
sheet.save(OUT/'J7R3_EIGHT_VIEW_CONTACT_SHEET.png')
(OUT/'J7R3_VIEW_META.json').write_text(json.dumps({'schema':'halo9.j7r1.vtk_camera_verification.v1','source_glb':GLB.name,'render_software':'VTK 9.6 offscreen, not Blender GUI','actual_rendered':True,'source_after_glb_import':'trimesh.Scene.load','views':view_results,'art_acceptance':'PENDING','limitations':['camera sizes identical for 7 city views; local interior camera not directly comparable','rendered GLB itself, not AI generated images; no GI or final materials','urban internal mobility, full building design, landscape surveyed coordinates remain unverified']},indent=2))