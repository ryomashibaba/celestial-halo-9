#!/usr/bin/env python3
"""Render fixed 6 cameras from SAVED D37 GLB, not conceptual illustrations."""
import numpy as np, trimesh, vtk
from pathlib import Path
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray
from PIL import Image,ImageDraw
R=Path(__file__).parent
SOURCES={'BASE':R/'D37_NEUTRAL_FIXTURE.glb','EDIT':R/'D37_REFERENCE_EDIT.glb'}
CAM={'south':([0,-2800,1000],[0,0,550]),'north':([0,2800,1000],[0,0,550]),'east':([2700,0,1000],[0,0,550]),'west':([-2700,0,1000],[0,0,550]),'aerial':([1600,-1700,2400],[0,0,500]),'oblique':([2200,-2100,1250],[0,0,620])}

def render(label,path):
    s=trimesh.load(str(path),force='scene',process=False)
    rend=vtk.vtkRenderer();rend.SetBackground(.055,.07,.095)
    for name,m in s.geometry.items():
        pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(np.asarray(m.vertices,dtype=float),deep=True))
        faces=np.asarray(m.faces,dtype=np.int64)
        cells=vtk.vtkCellArray();cells.SetCells(len(faces),numpy_to_vtkIdTypeArray(np.column_stack([np.full(len(faces),3),faces]).reshape(-1),deep=True))
        poly=vtk.vtkPolyData();poly.SetPoints(pts);poly.SetPolys(cells)
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(poly)
        actor=vtk.vtkActor();actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*((.48,.72,.75) if 'TARGET' in name else ((.84,.70,.46) if 'MARKER' in name else (.25,.38,.42))))
        actor.GetProperty().SetAmbient(.27);actor.GetProperty().SetDiffuse(.72)
        rend.AddActor(actor)
    for pos,intensity in [([-1000,-1400,2200],1.25),([1000,600,1900],.65)]:
        light=vtk.vtkLight();light.SetPosition(*pos);light.SetFocalPoint(0,0,650);light.SetIntensity(intensity);rend.AddLight(light)
    win=vtk.vtkRenderWindow();win.AddRenderer(rend);win.SetOffScreenRendering(1);win.SetSize(800,540)
    result={}
    for name,(eye,focus) in CAM.items():
        c=rend.GetActiveCamera();c.SetPosition(*eye);c.SetFocalPoint(*focus);c.SetViewUp(0,0,1);c.SetViewAngle(30)
        rend.ResetCameraClippingRange();win.Render();cap=vtk.vtkWindowToImageFilter();cap.SetInput(win);cap.Update()
        w=vtk.vtkPNGWriter();w.SetInputConnection(cap.GetOutputPort());output=R/f'D37_{label}_{name}.png';w.SetFileName(str(output));w.Write();result[name]=output
    win.Finalize();return result

def contact(images,label):
    board=Image.new('RGB',(1500,900),'#10161d')
    for i,(name,path) in enumerate(images.items()):
        im=Image.open(path).convert('RGB');im.thumbnail((740,415));x=(i%2)*750+(750-im.width)//2;y=(i//2)*300
        im=im.resize((730,270))
        board.paste(im,(x,y+22));ImageDraw.Draw(board).text((x+8,y+5),f'{label} - {name}',fill=(235,242,245))
    out=R/f'D37_{label}_6VIEW.jpg';board.save(out,quality=90);return out

if __name__=='__main__':
    for label,src in SOURCES.items():
        f=render(label,src);print(label,contact(f,label))
    # Same 3 views side-by-side, not claiming art success.
    board=Image.new('RGB',(1600,1155),'#121820')
    for i,name in enumerate(('south','oblique','aerial')):
        for j,label in enumerate(('BASE','EDIT')):
            p=R/f'D37_{label}_{name}.png';im=Image.open(p).convert('RGB').resize((790,365));x=j*800;y=i*385
            board.paste(im,(x,y+20));ImageDraw.Draw(board).text((x+12,y+4),f'{label}  /  {name}',fill='white')
    board.save(R/'D37_BASE_EDIT_3VIEW_COMPARE.jpg',quality=91)
