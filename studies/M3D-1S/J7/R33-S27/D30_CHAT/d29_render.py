#!/usr/bin/env python3
import io, json
from pathlib import Path
import numpy as np
import trimesh
from PIL import Image,ImageDraw,ImageFont
import vtk
from vtkmodules.vtkRenderingCore import vtkActor,vtkRenderer,vtkRenderWindow,vtkPolyDataMapper,vtkWindowToImageFilter
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.util.numpy_support import vtk_to_numpy
from d28_visual_workbench import VIEWS,render,vtk_poly
ROOT=Path(__file__).resolve().parent

def inside_render(scene,position,target,view_up=(0,0,1),angle=70):
    ren=vtk.vtkRenderer();ren.SetBackground(.10,.14,.19)
    for name,g in scene.geometry.items():
        mapper=vtkPolyDataMapper();mapper.SetInputData(vtk_poly(g));actor=vtkActor();actor.SetMapper(mapper)
        colors=np.asarray(g.visual.vertex_colors);rgb=colors[0,:3]/255. if len(colors) else [.71,.79,.87]
        actor.GetProperty().SetColor(*rgb);actor.GetProperty().SetAmbient(.30);actor.GetProperty().SetDiffuse(.7)
        actor.GetProperty().SetSpecular(.15);ren.AddActor(actor)
    camera=ren.GetActiveCamera();camera.SetPosition(*position);camera.SetFocalPoint(*target);camera.SetViewUp(*view_up);camera.SetViewAngle(angle)
    rw=vtkRenderWindow();rw.SetOffScreenRendering(1);rw.SetMultiSamples(0);rw.SetSize(700,430);rw.AddRenderer(ren)
    ren.ResetCameraClippingRange();rw.Render()
    filt=vtkWindowToImageFilter();filt.SetInput(rw);filt.ReadFrontBufferOff();filt.SetInputBufferTypeToRGB();filt.Update()
    writer=vtkPNGWriter();writer.SetInputConnection(filt.GetOutputPort());writer.WriteToMemoryOn();writer.Write()
    data=vtk_to_numpy(writer.GetResult()).tobytes();rw.Finalize();return data

def sheet(entries,views,out,width=500,height=310):
    margin=16;heading=44;label=28;gap=8
    rows=len(views);cols=len(entries)
    W=margin*2+cols*width+(cols-1)*gap
    H=margin*2+heading+rows*(height+label)+(rows-1)*gap
    canvas=Image.new('RGB',(W,H),'#e9edf3');d=ImageDraw.Draw(canvas)
    for c,(title,code) in enumerate(entries):
        x=margin+c*(width+gap)
        d.text((x,margin+8),title,fill='#1c2c3b')
        for r,view in enumerate(views):
            y=margin+heading+r*(height+label+gap)
            p=ROOT/f'D29_{code}_{view}.png'
            im=Image.open(p).convert('RGB');im.thumbnail((width,height))
            canvas.paste(im,(x,y));d.text((x+7,y+height+5),view,fill='#293d4d')
    canvas.save(ROOT/out,quality=90)

def main():
    for code in ['BASE','ENTRY','ROOM','SKYLIGHT']:
        sc=trimesh.load(str(ROOT/f'D29_{code}.glb'),file_type='glb',force='scene',process=False)
        for view in VIEWS:
            (ROOT/f'D29_{code}_{view}.png').write_bytes(render(sc,view).png)
        (ROOT/f'D29_{code}_approach_human.png').write_bytes(inside_render(sc,[0,-305,110],[0,50,120]))
        (ROOT/f'D29_{code}_inside_human.png').write_bytes(inside_render(sc,[0,-90,125],[0,120,138]))
        (ROOT/f'D29_{code}_sky_human.png').write_bytes(inside_render(sc,[0,0,120],[0,0,330],(0,1,0),72))
    sheet([('BASE · sealed','BASE'),('ROOM · entry+civic room','ROOM'),('SKYLIGHT · roof cut','SKYLIGHT')],['front','oblique','aerial','approach_human','inside_human','sky_human'],'D29_6VIEW_PHASE_COMPARISON.jpg')
    sheet([('ROOM · roof closed','ROOM'),('SKYLIGHT · roof opened','SKYLIGHT')],['front','aerial','inside_human','sky_human'],'D29_ROOF_BEFORE_AFTER.jpg')
if __name__=='__main__':main()
