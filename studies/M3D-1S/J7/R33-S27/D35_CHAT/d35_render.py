#!/usr/bin/env python3
"""Read independently saved D35 real GLB and generate identical camera renders."""
from pathlib import Path
import numpy as np,trimesh,vtk
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray
from PIL import Image,ImageDraw
OUT=Path(__file__).parent
CAM={
 'south':((80,-1550,780),(0,0,280),34),
 'west':((-1420,-400,720),(0,0,220),34),
 'east':((1450,440,760),(0,0,260),34),
 'north':((40,1450,810),(0,0,240),34),
 'aerial':((1030,-680,1430),(0,0,250),39),
 'canyon_human':((0,-390,4.7),(0,120,22),64),
 'side_human':((-190,-290,65),(-130,80,140),60),
 'elevated_civic':((-190,-80,120),(210,100,240),53),
}
def rgb(n):
 if 'URBAN_GROUND' in n:return(.13,.20,.23)
 if 'FLOOR' in n or 'ENTRY' in n or 'RAMP' in n:return(.66,.79,.77)
 if 'SERVICE_BACK' in n:return(.05,.15,.22)
 if 'GLAZING' in n:return(.13,.52,.64)
 if 'ROOF' in n:return(.48,.67,.72)
 if 'LIFT_SHAFT' in n or 'CROSS_CANYON' in n:return(.96,.70,.35)
 if 'BUTTRESS' in n:return(.33,.43,.51)
 if 'PIER' in n:return(.70,.77,.81)
 return(.45,.55,.60)
def render(variant):
 s=trimesh.load(OUT/f'D35_{variant}_URBAN_CANYON.glb',force='scene',process=False)
 r=vtk.vtkRenderer();r.SetBackground(.055,.073,.097)
 for n,m in s.geometry.items():
  p=vtk.vtkPoints();p.SetData(numpy_to_vtk(np.asarray(m.vertices,dtype=np.float64),deep=True))
  fa=np.asarray(m.faces,dtype=np.int64)
  ca=vtk.vtkCellArray();ca.SetCells(len(fa),numpy_to_vtkIdTypeArray(np.column_stack([np.full(len(fa),3),fa]).reshape(-1),deep=True))
  po=vtk.vtkPolyData();po.SetPoints(p);po.SetPolys(ca);ma=vtk.vtkPolyDataMapper();ma.SetInputData(po)
  ac=vtk.vtkActor();ac.SetMapper(ma);pr=ac.GetProperty();pr.SetColor(*rgb(n));pr.SetAmbient(.3);pr.SetDiffuse(.65);pr.SetSpecular(.13);r.AddActor(ac)
 for pos,power in [((-600,-800,1400),1.1),((600,600,900),.55)]:
  light=vtk.vtkLight();light.SetLightTypeToSceneLight();light.SetPosition(*pos);light.SetFocalPoint(0,0,200);light.SetIntensity(power);r.AddLight(light)
 rw=vtk.vtkRenderWindow();rw.AddRenderer(r);rw.SetOffScreenRendering(1);rw.SetSize(800,560)
 cards=[]
 for k,(eye,focus,angle) in CAM.items():
  c=r.GetActiveCamera();c.SetPosition(*eye);c.SetFocalPoint(*focus);c.SetViewUp(0,0,1);c.SetViewAngle(angle);r.ResetCameraClippingRange();rw.Render()
  f=vtk.vtkWindowToImageFilter();f.SetInput(rw);f.Update()
  w=vtk.vtkPNGWriter();w.SetInputConnection(f.GetOutputPort());out=OUT/f'D35_{variant}_{k}.png';w.SetFileName(str(out));w.Write()
  im=Image.open(out).convert('RGB');im.thumbnail((620,434));canvas=Image.new('RGB',(640,480),(14,22,32));canvas.paste(im,((640-im.width)//2,25));ImageDraw.Draw(canvas).text((14,5),variant+' / '+k,fill=(240,244,246));cards.append(canvas)
 board=Image.new('RGB',(640*4,480*2),(20,20,30))
 for i,item in enumerate(cards):board.paste(item,(i%4*640,i//4*480))
 out=OUT/f'D35_{variant}_8VIEW_REAL.jpg';board.save(out,quality=91)
 return [str(out),len(s.geometry)]
if __name__=='__main__':
 for v in ['BASE','REVERSE_SKEW']:print(v,render(v))
