#!/usr/bin/env python3
"""Render the saved real GLB; no illustrative images or fake camera planes."""
from pathlib import Path
import vtk, numpy as np, trimesh
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
from PIL import Image,ImageOps,ImageDraw,ImageFont
OUT=Path(__file__).parent
CAM={
 '01_south':((30,-750,240),(-20,0,12)),
 '02_west':((-800,-300,200),(-80,0,15)),
 '03_east':((800,200,230),(-60,0,20)),
 '04_north':((60,720,230),(0,0,15)),
 '05_aerial':((480,50,800),(-20,0,10)),
 '06_route_human':((-282,-75,1.7),(-115,-85,10)),
 '07_mid_gallery_human':((-80,-145,9.7),(-65,-98,11)),
 '08_top_gallery_human':((190,145,17.7),(185,96,18)),
 '09_mid_crossing_human':((-80,0,9.7),(-30,50,12)),
}
COL={'routes':(0.1,.69,.79),'rooms':(.83,.88,.91),'walls':(.31,.42,.5),'roof':(.92,.7,.35),'structure':(.44,.54,.63),'glass':(.3,.72,.81),'ground':(.19,.25,.30),'highlight':(1,.80,.41)}
def color(name):
 if name=='SITE_STUDY_GROUND':return COL['ground']
 if name.startswith(('RAMP_','GROUND_ENTRY','MID_CROSSING','TOP_PROMENADE','ROOM_G')) and ('_ACCESS' in name or name in ['RAMP_WEST','RAMP_EAST','GROUND_ENTRY','MID_CROSSING','TOP_PROMENADE']):return COL['routes']
 if name.endswith('interior_floor'):return COL['rooms']
 if name.endswith('ceiling_slab'):return COL['roof']
 if name.startswith('CIVIC_VOID_OPEN'):return COL['highlight']
 if name.startswith('civic_void_pylon') or name.startswith('column_'):return COL['structure']
 if 'window' in name:return COL['glass']
 if 'partition' in name:return COL['structure']
 return COL['walls']
def run(glb_path=None,prefix='D34'):
 scene=trimesh.load(glb_path or OUT/'D34_CIVIC_THREE_LEVEL_REAL.glb',force='scene',process=False)
 ren=vtk.vtkRenderer();ren.SetBackground(.062,.082,.108)
 for name,mesh in scene.geometry.items():
  pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(np.asarray(mesh.vertices,dtype=np.float64),deep=True))
  polys=vtk.vtkCellArray();faces=np.asarray(mesh.faces,dtype=np.int64)
  padded=np.hstack([np.full((len(faces),1),3,dtype=np.int64),faces]).reshape(-1)
  polys.SetCells(len(faces),numpy_to_vtkIdTypeArray(padded,deep=True))
  poly=vtk.vtkPolyData();poly.SetPoints(pts);poly.SetPolys(polys)
  mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(poly)
  actor=vtk.vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetColor(*color(name));actor.GetProperty().SetAmbient(.28);actor.GetProperty().SetDiffuse(.62);actor.GetProperty().SetSpecular(.08)
  ren.AddActor(actor)
 lights=[((-450,-370,800),1.0),((400,450,500),.48)]
 for p,i in lights:
  l=vtk.vtkLight();l.SetLightTypeToSceneLight();l.SetPosition(*p);l.SetFocalPoint(0,0,0);l.SetIntensity(i);ren.AddLight(l)
 win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.AddRenderer(ren);win.SetSize(1024,680)
 imgs=[]
 for key,(eye,target) in CAM.items():
  cam=ren.GetActiveCamera();cam.SetPosition(*eye);cam.SetFocalPoint(*target);cam.SetViewUp(0,0,1);cam.SetClippingRange(.05,5000);cam.SetViewAngle(54 if 'human' in key else 33);ren.ResetCameraClippingRange();win.Render()
  w=vtk.vtkWindowToImageFilter();w.SetInput(win);w.Update();writer=vtk.vtkPNGWriter();writer.SetInputConnection(w.GetOutputPort());out=OUT/f'{prefix}_{key}.png';writer.SetFileName(str(out));writer.Write();imgs.append(out)
 # 3x3 contact, labels overlay
 cards=[]
 for imf in imgs:
  im=Image.open(imf).convert('RGB');im.thumbnail((620,410));cn=Image.new('RGB',(640,446),(20,28,40));cn.paste(im,((640-im.width)//2,25));ImageDraw.Draw(cn).text((16,5),imf.stem,fill=(235,241,246));cards.append(cn)
 board=Image.new('RGB',(640*3,446*3),(14,18,23))
 for i,im in enumerate(cards):board.paste(im,((i%3)*640,(i//3)*446))
 board.save(OUT/f'{prefix}_9VIEW_REAL_CONTACT.jpg',quality=91)
 print({'views':len(imgs),'contact':str(OUT/f'{prefix}_9VIEW_REAL_CONTACT.jpg')})
if __name__=='__main__':run()
