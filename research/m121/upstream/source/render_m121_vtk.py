#!/usr/bin/env python3
"""Offline VTK architectural perspectives from actual M121 mesh geometry.
No image generation service, no Minecraft IO and no model/preserve modifications.
"""
from __future__ import annotations
import sys,json,math
from collections import defaultdict
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import vtk
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m121_city_experience import build_experience,CATH_X,CATH_Z,FLOOR,CIVIC_X,CIVIC_Z
ROOT=Path(__file__).resolve().parents[1]
W,H=1600,930
MATS={
'obsidian':('#1b303a',1),'shadow':('#243946',1),'structure':('#25353a',1),'ivory':('#e8e0ce',1),
'pearl':('#e8eee9',1),'opal':('#a8d5d2',.82),'lagoon':('#27a9ba',.56),'glass':('#45a9b8',.58),
'cyan':('#58e6e9',1),'copper':('#d2a06b',1),'gold':('#f7ba68',1),'forest':('#416f61',1),
'garden':('#477d68',1),'court':('#81999e',1),'sandstone':('#b6a995',1)
}
BACKGROUND='#101c25'

def pos(xzy):return (xzy[0]-3703.5,xzy[2]+1840,xzy[1]+2184.5)
def dec(s):return tuple(int(s.lstrip('#')[i:i+2],16)/255 for i in (0,2,4))

def actor_for(meshes,opacity_scale=1.0):
    bymat=defaultdict(list)
    for item in meshes:
        for face in item['f']:
            if len(face)<3:continue
            for i in range(1,len(face)-1):
                bymat[item['material']].append([item['v'][face[0]],item['v'][face[i]],item['v'][face[i+1]]])
    actors=[]
    for mat,faces in bymat.items():
        points=vtk.vtkPoints();cells=vtk.vtkCellArray()
        for f in faces:
            ids=[]
            for p in f:ids.append(points.InsertNextPoint(*pos(p)))
            tri=vtk.vtkTriangle()
            for i,n in enumerate(ids):tri.GetPointIds().SetId(i,n)
            cells.InsertNextCell(tri)
        poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
        normals=vtk.vtkPolyDataNormals();normals.SetInputData(poly);normals.ConsistencyOff();normals.AutoOrientNormalsOff();normals.SplittingOff();normals.ComputePointNormalsOff();normals.ComputeCellNormalsOn();normals.Update()
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort());mapper.ScalarVisibilityOff()
        a=vtk.vtkActor();a.SetMapper(mapper)
        c,opacity=MATS.get(mat,('#bbc5c3',1))
        a.GetProperty().SetColor(*dec(c));a.GetProperty().SetOpacity(min(1,opacity*opacity_scale))
        a.GetProperty().SetAmbient(.46 if mat not in ('obsidian','shadow','structure') else .32)
        a.GetProperty().SetDiffuse(.53)
        a.GetProperty().SetSpecular(.35 if mat in ('opal','lagoon','glass','ivory') else .13)
        a.GetProperty().SetSpecularPower(28)
        actors.append(a)
    return actors

def render(scene_name,camera,focal,angle,select,full=False):
    model=build_experience()
    old=model['meshes'][:model['m121_meshes_start_index']]
    new=model['meshes'][model['m121_meshes_start_index']:]
    r=vtk.vtkRenderer();r.SetBackground(*dec(BACKGROUND));r.GradientBackgroundOn();r.SetBackground2(*dec('#1f3742'))
    lights=[((600,550,-700),1.25,'#ffeed0'),((-500,240,540),.85,'#68c4cc'),((0,700,0),.30,'#d4e8f1')]
    for xyz,inten,color in lights:
        l=vtk.vtkLight();l.SetPosition(*xyz);l.SetFocalPoint(0,0,0)
        l.SetColor(*dec(color));l.SetIntensity(inten);l.SetPositional(False);r.AddLight(l)
    if full:
        for act in actor_for(old,opacity_scale=.44):r.AddActor(act)
    for act in actor_for([s for s in new if s['site'] in select],1):r.AddActor(act)
    cam=r.GetActiveCamera();cam.SetPosition(*pos(camera));cam.SetFocalPoint(*pos(focal));cam.SetViewUp(0,1,0);cam.SetViewAngle(angle)
    r.ResetCameraClippingRange()
    ren=vtk.vtkRenderWindow();ren.SetOffScreenRendering(True);ren.AddRenderer(r);ren.SetSize(W,H);ren.SetMultiSamples(8);ren.SetAlphaBitPlanes(1)
    ren.Render()
    to_img=vtk.vtkWindowToImageFilter();to_img.SetInput(ren);to_img.SetInputBufferTypeToRGB();to_img.ReadFrontBufferOff();to_img.Update()
    wr=vtk.vtkPNGWriter();wr.SetInputConnection(to_img.GetOutputPort());wr.SetFileName(str(ROOT/'images'/scene_name));wr.Write()
    del ren, r
    return ROOT/'images'/scene_name

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def overlay(p,title,eyebrow,notes):
    img=Image.open(p).convert('RGB');d=ImageDraw.Draw(img,'RGBA')
    d.rectangle((0,0,W,154),fill=(6,19,29,210))
    d.rectangle((0,H-81,W,H),fill=(6,19,29,225))
    d.rectangle((48,56,55,126),fill=(47,204,209,255))
    big=ImageFont.truetype(FONT,42);small=ImageFont.truetype(FONT,19);mid=ImageFont.truetype(FONT,24)
    d.text((79,26),eyebrow,fill=(91,213,215),font=small)
    d.text((79,59),title,fill=(243,238,226),font=big)
    d.text((58,H-59),notes,fill=(221,222,217),font=mid)
    d.text((W-310,31),'M121 / MODEL-ONLY',fill=(211,172,104),font=small)
    img.save(p,optimize=True)

if __name__=='__main__':
    (ROOT/'images').mkdir(exist_ok=True)
    scenes=[
      ('M121_01_SB08_PEDESTRIAN_NAVE.png',
       (CATH_X,CATH_Z-56,FLOOR+2.8),(CATH_X,CATH_Z+20,FLOOR+39),77,
       {'SB08'},False,'01 / AURORA TWIN VAULT','THE NAVE, FROM HUMAN EYE HEIGHT',
       '150m proposed open vault  /  1.8m people  /  3 gallery levels  /  unbuilt'),
      ('M121_02_CIVIC_PUBLIC_GROUND.png',
       (CIVIC_X,CIVIC_Z-49,-1737.7),(CIVIC_X,CIVIC_Z+19,-1698),78,
       {'CIVIC_CORE'},False,'02 / CELESTIAL FORUM','THE PUBLIC CITY AS AN ARCHITECTURAL ROOM',
       '137m proposed main vault  /  2 suspended galleries  /  full-height opening'),
      ('M121_03_SB08_HERO_SECTION.png',
       (CATH_X-260,CATH_Z-128,FLOOR+128),(CATH_X,CATH_Z,FLOOR+64),58,
       {'SB08'},False,'03 / HERO4 MATERIAL STUDY','THE TWIN VAULTS IN SECTION',
       'Open central sky slot  /  tall stained-glass aisles  /  heavy dark buttress'),
      ('M121_04_CITY_SILHOUETTE.png',
       (4890,-3250,-1118),(3703.5,-2184.5,-1698),48,
       {'SB08','CIVIC_CORE','PUBLIC_EXPERIENCE_SPINE'},True,
       '04 / MEGACITY RESEARCH','ONE CITY MODEL, NOT A DIFFERENT CONCEPT PAINTING',
       'M120 inherited city shown dimmed  /  M121 public realm shapes added  /  HOLD')
    ]
    for filename,camera,focal,ang,select,full,eyebrow,title,note in scenes:
        p=render(filename,camera,focal,ang,select,full)
        overlay(p,title,eyebrow,note)
        print(p,p.stat().st_size,flush=True)
