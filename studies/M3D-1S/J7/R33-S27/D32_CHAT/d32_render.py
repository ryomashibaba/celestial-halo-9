#!/usr/bin/env python3
"""Offscreen VTK GLB readback and standardized 8 camera views; research proof only."""
import os
os.environ.setdefault('LIBGL_ALWAYS_SOFTWARE','1')
from pathlib import Path
import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
import trimesh
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
VIEWS={
 '01_south_distant':((100,-2800,990),(0,0,590),37),
 '02_west_threequarter':((-2300,-1800,1150),(0,0,510),37),
 '03_east_threequarter':((2250,-1400,1190),(0,0,510),37),
 '04_north_reversal':((80,2650,1050),(0,0,560),37),
 '05_west_profile':((-2850,80,980),(0,0,550),36),
 '06_aerial':((1350,-1250,2650),(0,0,360),40),
 '07_human_approach':((30,-940,60),(0,60,420),64),
 '08_civic_spine_human':((0,-390,28),(0,400,355),70)
}

def actor_from_geom(g):
    v=np.asarray(g.vertices,dtype=float)
    f=np.asarray(g.faces,dtype=np.int64)
    points=vtk.vtkPoints();points.SetData(numpy_to_vtk(v,deep=True))
    polys=vtk.vtkCellArray();longfaces=np.column_stack((np.full(len(f),3),f)).astype(np.int64)
    polys.SetCells(len(f),numpy_to_vtkIdTypeArray(longfaces.ravel(),deep=True))
    pdata=vtk.vtkPolyData();pdata.SetPoints(points);pdata.SetPolys(polys)
    norms=vtk.vtkPolyDataNormals();norms.SetInputData(pdata);norms.ComputeCellNormalsOn();norms.ComputePointNormalsOff();norms.AutoOrientNormalsOff();norms.ConsistencyOn();norms.Update()
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(norms.GetOutputPort())
    a=vtk.vtkActor();a.SetMapper(mapper)
    try: c=np.asarray(g.visual.face_colors)[0,:3]/255
    except: c=np.array([.55,.64,.7])
    a.GetProperty().SetColor(*map(float,c));a.GetProperty().SetAmbient(.36);a.GetProperty().SetDiffuse(.54);a.GetProperty().SetSpecular(.12)
    return a

def render(filename,variant):
    scene=trimesh.load(str(filename),force='scene',process=False)
    ren=vtk.vtkRenderer();ren.SetBackground(.035,.054,.080);ren.SetBackground2(.12,.18,.25);ren.GradientBackgroundOn()
    for geometry in scene.geometry.values():ren.AddActor(actor_from_geom(geometry))
    light=vtk.vtkLight();light.SetPosition(-900,-900,1800);light.SetFocalPoint(0,0,400);light.SetIntensity(1.2);light.SetLightTypeToSceneLight();ren.AddLight(light)
    light2=vtk.vtkLight();light2.SetPosition(1700,900,1600);light2.SetFocalPoint(0,0,400);light2.SetIntensity(.5);light2.SetLightTypeToSceneLight();ren.AddLight(light2)
    rw=vtk.vtkRenderWindow();rw.SetSize(720,480);rw.SetOffScreenRendering(1);rw.SetMultiSamples(0);rw.AddRenderer(ren)
    pns=[]
    for name,(pos,focal,angle) in VIEWS.items():
        cam=ren.GetActiveCamera();cam.ParallelProjectionOff();cam.SetPosition(*pos);cam.SetFocalPoint(*focal);cam.SetViewUp(0,0,1);cam.SetViewAngle(angle);ren.ResetCameraClippingRange()
        rw.Render();w2=vtk.vtkWindowToImageFilter();w2.SetInput(rw);w2.SetInputBufferTypeToRGB();w2.ReadFrontBufferOff();w2.Update();wr=vtk.vtkPNGWriter();path=ROOT/f'D32_{variant}_{name}.png';wr.SetFileName(str(path));wr.SetInputConnection(w2.GetOutputPort());wr.Write();pns.append(path)
    rw.Finalize();return pns

def sheet(a,b,title,outname):
    W,H=720,480
    img=Image.new('RGB',(2*W+28,8*(H+32)+70),'#111923');d=ImageDraw.Draw(img)
    d.text((20,13),title,fill='#f4f1e7')
    d.text((32,41),'A / URBAN ESCARPMENT',fill='#c6d8e1');d.text((W+42,41),'B / SUSPENDED FAN',fill='#c6d8e1')
    for i,((name,_),p,q) in enumerate(zip(VIEWS.items(),a,b)):
        y=70+i*(H+32)
        img.paste(Image.open(p).convert('RGB'),(8,y));img.paste(Image.open(q).convert('RGB'),(W+20,y))
        d.text((14,y+H+5),name,fill='#d8d2c5');d.text((W+28,y+H+5),name,fill='#d8d2c5')
    img.save(ROOT/outname,quality=88)

if __name__=='__main__':
    x=render(ROOT/'D32_A_FAULT_URBAN_ESCARPMENT_STUDY.glb','A')
    y=render(ROOT/'D32_B_SUSPENDED_INHABITED_FAN_STUDY.glb','B')
    sheet(x,y,'D32 / ACTUAL SAVED GLB RENDER / ART-FIRST 8-VIEW GATE','D32_8VIEW_A_B_COMPARE.jpg')
    print('Wrote',len(x)+len(y),'real saved GLB images')
