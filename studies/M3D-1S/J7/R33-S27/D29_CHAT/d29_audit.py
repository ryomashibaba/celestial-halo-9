#!/usr/bin/env python3
"""Independent GLB readback and spatial counterexample tests for D29 fixture."""
import io,json,hashlib,math,sys
from pathlib import Path
import numpy as np
import vtk
import trimesh
from d29_orthogonal_csg import sha,load_checked,TARGET,PUBLIC,carve_glb,fixture_glb
from d28_visual_workbench import vtk_poly
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.util.numpy_support import numpy_to_vtk

def read_glb(raw):
    return trimesh.load(io.BytesIO(raw),file_type='glb',force='scene',process=False)

def enclosed(mesh,pts):
    surface=vtk_poly(mesh)
    samples=vtkPolyData();vp=vtkPoints();vp.SetData(numpy_to_vtk(np.asarray(pts,dtype=np.float64),deep=True));samples.SetPoints(vp)
    sel=vtk.vtkSelectEnclosedPoints();sel.SetInputData(samples);sel.SetSurfaceData(surface);sel.SetTolerance(1e-6);sel.Update()
    return [bool(sel.IsInside(i)) for i in range(len(pts))]

def support_height(meshes,x,y,z=48):
    # Independent ray-mesh intersection, instead of consulting carve parameters.
    # Mesh faces intersected at z from upper foot sample to below the structure.
    closest=None
    for g in meshes:
        loc=vtk.vtkStaticCellLocator();loc.SetDataSet(vtk_poly(g));loc.BuildLocator()
        points=vtk.vtkPoints();ids=vtk.vtkIdList()
        loc.IntersectWithLine([x,y,z],[x,y,-30],1e-7,points,ids)
        for k in range(points.GetNumberOfPoints()):
            h=float(points.GetPoint(k)[2]); closest=h if closest is None else max(closest,h)
    return closest

def audit(base,entry,room,roof):
    models={k:read_glb(v) for k,v in [('BASE',base),('ENTRY',entry),('ROOM',room),('ROOF',roof)]}
    result={'study':'D29','glb':{},'sampled_route':{},'counterfactual':{},'safety_limits':[]}
    for name,scene in models.items():
        solid=scene.geometry[TARGET];route=scene.geometry[PUBLIC]
        result['glb'][name]={'sha256':sha({'BASE':base,'ENTRY':entry,'ROOM':room,'ROOF':roof}[name]),
         'faces':len(solid.faces),'vertices':len(solid.vertices),'watertight':bool(solid.is_watertight),
         'euler_number':int(solid.euler_number),'positive_volume':bool(solid.volume>0),
         'source_public_mesh_vertices_unchanged':bool(np.array_equal(route.vertices,models['BASE'].geometry[PUBLIC].vertices)),
         'source_public_mesh_faces_unchanged':bool(np.array_equal(route.faces,models['BASE'].geometry[PUBLIC].faces))}
        assert solid.is_watertight and solid.is_winding_consistent and solid.volume>0
        assert result['glb'][name]['source_public_mesh_vertices_unchanged']
    xs=(-45.,0.,45.);ys=np.linspace(-315.,70.,81)
    pts=np.array([[x,y,z] for y in ys for x in xs for z in (55.,85.,150.)])
    for key in ('BASE','ENTRY','ROOM','ROOF'):
        scene=models[key];s=scene.geometry[TARGET]
        inside=enclosed(s,pts)
        supported=[]
        for y in ys:
            for x in xs:
                h=support_height([s,scene.geometry[PUBLIC]],x,y,47)
                supported.append(h is not None and abs(h-40.)<.005)
        result['sampled_route'][key]={
            'stations':len(ys),'width_samples':len(xs),'height_samples':3,
            'floor_supported':sum(supported),'floor_total':len(supported),
            'human_volume_collisions':sum(inside),'human_volume_total':len(inside)}
    # Domain fact checks independently against actual GLB solids, not same cut parameters.
    room_point=[[0.,0.,150.]];sky_point=[[0.,0.,300.]]
    for key in ('BASE','ENTRY','ROOM','ROOF'):
        m=models[key].geometry[TARGET]
        result['counterfactual'][key]={'center_civic_point_inside_solid':enclosed(m,room_point)[0],
                                     'skylight_point_inside_solid':enclosed(m,sky_point)[0]}
    assert result['sampled_route']['ROOF']['floor_supported']==243
    assert result['sampled_route']['ROOF']['human_volume_collisions']==0
    assert result['counterfactual']['BASE']['center_civic_point_inside_solid']
    assert result['counterfactual']['ENTRY']['center_civic_point_inside_solid']
    assert not result['counterfactual']['ROOM']['center_civic_point_inside_solid']
    assert result['counterfactual']['ROOM']['skylight_point_inside_solid']
    assert not result['counterfactual']['ROOF']['skylight_point_inside_solid']
    result['safety_limits']=['finite point samples, not continuous swept human movement',
      'topological validity of two-mesh assembly only at individual mesh level',
      'no certified city, structural, fire, egress, habitation or access safety',
      'orthogonal box CSG is not general organic-form editing or art quality']
    return result

if __name__=='__main__':
    from d29_visual_workbench import D29Workspace
    import tempfile
    work=Path(tempfile.mkdtemp());src=work/'source.glb';src.write_bytes(fixture_glb());w=D29Workspace(work/'state',src)
    files=[w.edited]
    for box in ({'min':[-95,-270,40],'max':[95,-130,185]},
                {'min':[-210,-155,40],'max':[230,165,265]},
                {'min':[-60,-45,250],'max':[70,90,380]}):
        w.commit_cut({'revision':w.revision,'box':box});files.append(w.edited)
    print(json.dumps(audit(*files),indent=2))
