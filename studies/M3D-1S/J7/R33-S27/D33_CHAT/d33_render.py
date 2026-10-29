#!/usr/bin/env python3
"""Render exactly loaded real GLBs to consistent offscreen VTK 6 viewpoints.
Colors are user-preview material choices and do not establish art acceptance.
"""
from pathlib import Path
import numpy as np, vtk, trimesh, json
from PIL import Image, ImageOps, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
VIEWS={
 '01_south':(50,-3100,1150), '02_east':(3200,400,1300),'03_north':(150,3300,1250),
 '04_west':(-3150,100,1300),'05_aerial':(2300,-2600,3200),'06_human':(120,-1200,1.7),
}
COLORS={'MAIN_SHEAR':(0.74,0.72,0.68),'HANGING_CROWN':(0.49,0.60,0.68),'LOWER_BUTTRESS':(0.42,0.48,0.56)}

def render(filename,outdir):
  outdir.mkdir(exist_ok=True)
  sc=trimesh.load(filename,force='scene',process=False)
  records=[]
  for view,pos in VIEWS.items():
    ren=vtk.vtkRenderer();ren.GradientBackgroundOn();ren.SetBackground(.96,.965,.977);ren.SetBackground2(.78,.82,.86)
    for name,geom in sc.geometry.items():
      g=geom.copy()
      pts=vtk.vtkPoints();pts.SetDataTypeToDouble()
      for p in g.vertices:pts.InsertNextPoint(*map(float,p))
      poly=vtk.vtkPolyData();poly.SetPoints(pts)
      cells=vtk.vtkCellArray()
      for a,b,c in g.faces:
        tri=vtk.vtkTriangle()
        for k,v in enumerate((a,b,c)):tri.GetPointIds().SetId(k,int(v))
        cells.InsertNextCell(tri)
      poly.SetPolys(cells)
      normal=vtk.vtkPolyDataNormals();normal.SetInputData(poly);normal.SplittingOff();normal.ConsistencyOn();normal.AutoOrientNormalsOn();normal.Update()
      mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normal.GetOutputPort())
      actor=vtk.vtkActor();actor.SetMapper(mapper)
      actor.GetProperty().SetColor(*COLORS.get(name,(.7,.7,.7)))
      actor.GetProperty().SetAmbient(.25);actor.GetProperty().SetDiffuse(.75);actor.GetProperty().SetSpecular(.25);actor.GetProperty().SetSpecularPower(24)
      ren.AddActor(actor)
    # Horizontal plane is renderer-only scale reference (not present in GLB).
    outline=vtk.vtkCubeSource();outline.SetBounds(-1000,1100,-1100,1100,-12,-10)
    groundm=vtk.vtkPolyDataMapper();groundm.SetInputConnection(outline.GetOutputPort());grounda=vtk.vtkActor();grounda.SetMapper(groundm)
    grounda.GetProperty().SetColor(.85,.88,.90);grounda.GetProperty().SetOpacity(.55);ren.AddActor(grounda)
    light=vtk.vtkLight();light.SetLightTypeToSceneLight();light.SetPosition(2500,-2500,4800);light.SetFocalPoint(0,0,700);light.SetIntensity(1.35);ren.AddLight(light)
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1050,700);win.AddRenderer(ren)
    camera=ren.GetActiveCamera();camera.SetFocalPoint(0,20,420 if 'human' in view else 730);camera.SetPosition(*pos)
    camera.SetViewUp(0,0,1)
    if 'human' in view: camera.ParallelProjectionOff();camera.SetViewAngle(65)  # actual 1.7m eye station
    else: camera.ParallelProjectionOn();camera.SetParallelScale(1200)
    ren.ResetCameraClippingRange();win.Render()
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.Update();write=vtk.vtkPNGWriter()
    target=outdir/(view+'.png');write.SetFileName(str(target));write.SetInputConnection(capture.GetOutputPort());write.Write()
    records.append(str(target))
    win.Finalize()
  return records

def montage(images,output,labels):
  W,H=520,360
  canvas=Image.new('RGB',(W*3,H*2),(247,248,250))
  dr=ImageDraw.Draw(canvas)
  for i,path in enumerate(images):
    im=Image.open(path).convert('RGB');im.thumbnail((W-8,H-45))
    x=(i%3)*W+(W-im.width)//2;y=(i//3)*H+32
    canvas.paste(im,(x,y));dr.text(((i%3)*W+12,(i//3)*H+8),labels[i],fill=(45,55,70))
  canvas.save(output,quality=89)

if __name__=='__main__':
  for tag in ('BASE','EDIT'):
    imgs=render(ROOT/f'D33_{tag}_ART_STUDY.glb',ROOT/f'D33_{tag}_VIEWS')
    montage(imgs,ROOT/f'D33_{tag}_6VIEW.jpg',[tag+' · '+x.replace('_',' ') for x in VIEWS])
    print(tag,len(imgs))
  a=Image.open(ROOT/'D33_BASE_6VIEW.jpg').convert('RGB');b=Image.open(ROOT/'D33_EDIT_6VIEW.jpg').convert('RGB')
  a.thumbnail((1080,900));b.thumbnail((1080,900));c=Image.new('RGB',(a.width+b.width,max(a.height,b.height)),(255,255,255));c.paste(a,(0,0));c.paste(b,(a.width,0));c.save(ROOT/'D33_BASE_EDIT_REAL_6VIEW_COMPARE.jpg',quality=90)
