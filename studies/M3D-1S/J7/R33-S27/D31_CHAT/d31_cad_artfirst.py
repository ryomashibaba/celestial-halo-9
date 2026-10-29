#!/usr/bin/env python3
"""HALO-9 D31: independent design test of inhabited-rift macro grammar.
Hand-authored front elevation polygons (NOT an architectural adoption or a generated city).
CadQuery / OCC exact solids -> STEP and GLB -> 7 consistent VTK views.
The explicit art gate precedes any building ornament/detailing.
"""
from pathlib import Path
import os
import numpy as np, cadquery as cq, trimesh, vtk, json, hashlib
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
from PIL import Image,ImageOps,ImageDraw,ImageFont
R=Path(os.environ.get('D31_OUTPUT_DIR','/mnt/data/HALO9_D31_CHAT'));R.mkdir(parents=True,exist_ok=True)
# Interpret front elevation X,Z; extrude in Y. All dimensions metres. Research-only coordinates.
WEST=[(-1070,0),(-390,0),(-300,170),(-430,330),(-330,550),(-460,740),(-215,1050),(-345,1280),(-265,1470),(-430,1840),(-670,1980),(-845,1610),(-745,1370),(-900,1030),(-1020,730),(-1180,410)]
EAST=[(450,0),(1130,0),(1230,270),(1080,430),(1150,680),(960,920),(1090,1160),(930,1430),(1010,1730),(790,1980),(630,1750),(740,1540),(530,1180),(650,880),(420,640),(540,330)]
BRIDGE=[(-400,1080),(-340,970),(-175,1060),(110,1190),(460,1340),(700,1520),(680,1740),(510,1690),(230,1530),(-75,1430),(-470,1280),(-525,1170)]
FLOAT=[(-280,2040),(-100,2280),(220,2480),(405,2275),(320,2070),(85,1960),(-80,1890)]
# Physically intended civic windows, not symbolic facade decals. Opening through finite depth of wing.
WEST_VOID=[(-625,330),(-420,400),(-335,620),(-555,735),(-720,620)]
EAST_VOID=[(720,460),(970,540),(1010,740),(840,820),(660,650)]
# Contrasting independent morphology trial: ground-oriented and less bridge-dominant
BRIDGE_B=[(-445,1065),(-335,1000),(-10,1060),(310,1150),(585,1260),(665,1440),(540,1610),(400,1450),(10,1265),(-450,1250)]
FLOAT_B=[(-175,2100),(20,2440),(220,2590),(380,2290),(260,2105),(60,2010)]
COLOR={'WEST':(216,226,230),'EAST':(207,209,217),'SKY':(192,210,219),'FLOAT':(222,229,234),'GROUND':(86,99,108)}

def front(profile,depth,center_y):
    out=cq.Workplane('XZ').polyline(profile).close().extrude(depth).val()
    out=out.translate((0,center_y+depth/2,0)) # XZ normal is -Y
    assert out.isValid() and out.Volume()>0,(out.isValid(),out.Volume())
    return out

def make(which):
    west=front(WEST,560,0); east=front(EAST,630,90)
    # Subtract true through-void from native CAD solids (no voxel staircases)
    west=west.cut(front(WEST_VOID,650,0));east=east.cut(front(EAST_VOID,740,90))
    bridge=front(BRIDGE if which=='A' else BRIDGE_B,490,-10)
    floating=front(FLOAT if which=='A' else FLOAT_B,390,-90)
    # Ground civic meeting surface serves as scale/context only (not certified walkable full circulation)
    ground=cq.Workplane('XY').box(2650,1480,18).val().translate((0,0,-18))
    parts={'WEST':west,'EAST':east,'SKY':bridge,'FLOAT':floating,'GROUND':ground}
    for name,shape in parts.items():
        assert shape.isValid() and shape.Volume()>0,(which,name)
    # Export exact BREP in STEP as editable CAD geometry.
    cq.exporters.export(cq.Compound.makeCompound(list(parts.values())),str(R/f'D31_{which}_CAD_EXACT.step'),unit='M')
    scene=trimesh.Scene(); meshes={}
    for k,shape in parts.items():
        verts,facets=shape.tessellate(8,0.15)
        v=np.array([[p.x,p.y,p.z] for p in verts],float)
        f=np.array(facets,dtype=np.int64)
        mesh=trimesh.Trimesh(vertices=v,faces=f,process=False)
        mesh.visual.face_colors=(*COLOR[k],255)
        scene.add_geometry(mesh,geom_name=k,node_name=k)
        meshes[k]=mesh
    glb=trimesh.exchange.gltf.export_glb(scene)
    (R/f'D31_{which}_real3d.glb').write_bytes(glb)
    return parts,mesh_report(meshes,glb)

def mesh_report(meshes,glb):
    return {'sha256':hashlib.sha256(glb).hexdigest(),'meshes':len(meshes),'triangles':int(sum(len(m.faces) for m in meshes.values())),'watertight_per_geometry':{k:bool(m.is_watertight) for k,m in meshes.items()},'bounds_m':[np.min(np.stack([m.bounds[0] for m in meshes.values()]),axis=0).tolist(),np.max(np.stack([m.bounds[1] for m in meshes.values()]),axis=0).tolist()]}

def render(which):
    s=trimesh.load(R/f'D31_{which}_real3d.glb',force='scene',process=False)
    center=np.array([0,0,1100.]);
    # Camera placements are fixed across independent A and B for fair comparison.
    cameras={
      'front':([0,-5800,1580],[0,0,1220]),
      'west_oblique':([-3900,-4300,1840],[0,0,1150]),
      'east_oblique':([3800,-4300,1750],[0,0,1250]),
      'rear':([0,5800,1690],[0,0,1220]),
      'aerial':([1200,-2800,4350],[0,0,1150]),
      'side':([-4600,400,1550],[0,0,1100]),
      'human_canyon':([0,-720,20],[0,0,1300])
    }
    for name,(pos,focal) in cameras.items():
        window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(750,480);window.SetMultiSamples(0)
        ren=vtk.vtkRenderer();ren.SetBackground(0.078,0.095,0.122);window.AddRenderer(ren)
        for gname,m in s.geometry.items():
            pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(np.asarray(m.vertices,dtype=np.float32),deep=True))
            arr=np.hstack([np.full((len(m.faces),1),3,dtype=np.int64),m.faces.astype(np.int64)]).ravel()
            cells=vtk.vtkCellArray();cells.SetCells(len(m.faces),numpy_to_vtkIdTypeArray(arr,deep=True))
            pd=vtk.vtkPolyData();pd.SetPoints(pts);pd.SetPolys(cells)
            mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(pd)
            actor=vtk.vtkActor();actor.SetMapper(mapper)
            cc=COLOR[gname];actor.GetProperty().SetColor(*(x/255 for x in cc));actor.GetProperty().SetInterpolationToPhong();actor.GetProperty().SetAmbient(0.26);actor.GetProperty().SetDiffuse(0.70);actor.GetProperty().SetSpecular(0.07)
            ren.AddActor(actor)
        ren.AutomaticLightCreationOn()
        camera=ren.GetActiveCamera();camera.SetPosition(*pos);camera.SetFocalPoint(*focal);camera.SetViewUp(0,0,1);camera.SetClippingRange(0.1,20000)
        if name!='human_canyon':camera.ParallelProjectionOn();camera.SetParallelScale(1800 if name not in ('aerial','side') else 2200)
        else:camera.ParallelProjectionOff();camera.SetViewAngle(60)
        window.Render()
        w=vtk.vtkWindowToImageFilter();w.SetInput(window);w.ReadFrontBufferOff();w.Update()
        writer=vtk.vtkPNGWriter();writer.SetInputConnection(w.GetOutputPort());writer.SetFileName(str(R/f'D31_{which}_{name}.png'));writer.Write()
        window.Finalize()
    card_w=500;card_h=320
    cv=Image.new('RGB',(4*card_w,2*(card_h+25)+45),(248,249,250));dr=ImageDraw.Draw(cv)
    dr.text((15,12),f'D31 {which} / exact CAD BREP test / same GLB',fill=(20,25,29))
    for i,name in enumerate(cameras):
        a=Image.open(R/f'D31_{which}_{name}.png').convert('RGB').resize((card_w-10,card_h))
        x=(i%4)*card_w+5;y=45+(i//4)*(card_h+25)
        cv.paste(a,(x,y));dr.text((x+5,y+card_h+2),name,fill=(30,38,45))
    cv.save(R/f'D31_{which}_7views.jpg',quality=92)
if __name__=='__main__':
    res={}
    for w in ('A','B'):
        p,stats=make(w);res[w]=stats;print(w,stats,flush=True)
        render(w)
    (R/'D31_INITIAL_QA.json').write_text(json.dumps(res,indent=2),encoding='utf-8')
