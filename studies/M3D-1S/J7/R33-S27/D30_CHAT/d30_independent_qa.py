#!/usr/bin/env python3
"""Readback QA on saved GLBs. Finite samples only; NOT full accessible-route proof."""
import io,json,hashlib,sys
from pathlib import Path
import numpy as np
import vtk
import trimesh
from vtkmodules.util.numpy_support import numpy_to_vtk
ROOT=Path(__file__).resolve().parent
TARGET='NEUTRAL_SCULPTED_MASS';ROUTE='PROTECTED_CIVIC_ROUTE';DECK='PROTECTED_ATRIUM_DECK'

def vtk_poly(m):
    p=vtk.vtkPolyData();pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(np.asarray(m.vertices,dtype=np.float64),deep=True));p.SetPoints(pts)
    a=np.asarray(m.faces,dtype=np.int64);c=vtk.vtkCellArray()
    c.SetCells(len(a),numpy_to_vtk(np.c_[np.full(len(a),3,dtype=np.int64),a].ravel(),deep=True,array_type=vtk.VTK_ID_TYPE));p.SetPolys(c)
    return p

def inside(mesh,positions):
    data=vtk.vtkPolyData();points=vtk.vtkPoints();points.SetData(numpy_to_vtk(np.asarray(positions,dtype=np.float64),deep=True));data.SetPoints(points)
    pick=vtk.vtkSelectEnclosedPoints();pick.SetInputData(data);pick.SetSurfaceData(vtk_poly(mesh));pick.SetTolerance(1e-6);pick.Update()
    return np.array([bool(pick.IsInside(i)) for i in range(len(positions))],dtype=bool)

def supported(route,positions):
    loc=vtk.vtkStaticCellLocator();loc.SetDataSet(vtk_poly(route));loc.BuildLocator()
    result=[]
    for x,y,z in positions:
        out=vtk.vtkPoints();ids=vtk.vtkIdList()
        loc.IntersectWithLine((float(x),float(y),float(z+16)),(float(x),float(y),float(z-12)),1e-5,out,ids)
        heights=[out.GetPoint(i)[2] for i in range(out.GetNumberOfPoints())]
        result.append(any(abs(t-float(z))<1.0 for t in heights))
    return np.array(result,dtype=bool)

def audit():
    models={p:trimesh.load(str(ROOT/f'D30_{p}.glb'),force='scene',process=False) for p in ('BASE','TUNNEL','ROOM','SKYLIGHT')}
    ref=models['BASE'];report={'model_integrity':{},'route_spatial':{},'counterfactual':{},'negative_controls':{},'limits':[]}
    base_public={k:(np.asarray(ref.geometry[k].vertices).copy(),np.asarray(ref.geometry[k].faces).copy()) for k in (ROUTE,DECK)}
    ys=np.linspace(-400,75,61)
    # path sample locations are independently specified in the auditor, not read from a cut-plan file.
    floor=[];heads=[]
    for y in ys:
        x=-83+0.28*(y+550)+17*np.sin((y+550)/230)
        z=112+0.026*(y+550)
        for across in (-20,0,20):
            # tangent normal approximated for lateral cross section
            dx=0.28+(17/230)*np.cos((y+550)/230)
            norm=np.array([-1.,dx])/np.sqrt(1+dx**2)
            px=x+across*norm[0];py=y+across*norm[1]
            floor.append([px,py,z])
            for elevation in (7,55,110):heads.append([px,py,z+elevation])
    floor=np.array(floor);heads=np.array(heads)
    for name,scene in models.items():
        assert set(scene.geometry)==set(ref.geometry)
        solid=scene.geometry[TARGET]
        untouched={k:bool(np.array_equal(scene.geometry[k].vertices,base_public[k][0]) and np.array_equal(scene.geometry[k].faces,base_public[k][1])) for k in base_public}
        if not all(untouched.values()):raise AssertionError('protected route/deck changed')
        report['model_integrity'][name]={
            'mesh_count':len(scene.geometry),'target_triangles':len(solid.faces),
            'watertight':bool(solid.is_watertight),'winding_consistent':bool(solid.is_winding_consistent),
            'positive_volume':bool(solid.volume>0), 'euler_number':int(solid.euler_number),
            'protected_meshes_unchanged':untouched,
            'glb_sha256':hashlib.sha256((ROOT/f'D30_{name}.glb').read_bytes()).hexdigest()}
        assert solid.is_watertight and solid.is_winding_consistent and solid.volume>0
        support=supported(scene.geometry[ROUTE],floor)
        hit=inside(solid,heads)
        report['route_spatial'][name]={ 'support_success':int(support.sum()),'support_total':len(support),
            'volume_collision_samples':int(hit.sum()),'collision_total':len(hit)}
        # Counterfactual stage checks with the *actual reimported* geometry
        probes=[[105,85,215],[135,113,405],[-80,-330,190]]
        report['counterfactual'][name]={'probes':[bool(z) for z in inside(solid,probes)]}
    # Removal of public route must be detected by ray support sampling on empty geometry.
    with_floor=supported(ref.geometry[ROUTE],floor)
    without_floor=supported(ref.geometry[DECK],floor)
    report['negative_controls']['missing_route_support_failures'] = int((~without_floor).sum())
    report['negative_controls']['valid_route_support_success'] = int(with_floor.sum())
    # Place a real solid obstruction into the saved tunnel and test actual mesh inclusion.
    obstacle=trimesh.creation.box(extents=[58.,75.,70.]); obstacle.apply_translation([30.,-225.,190.])
    blocked=inside(obstacle,heads)
    report['negative_controls']['obstruction_collision_samples'] = int(blocked.sum())
    assert blocked.sum()>0 and with_floor.all() and (~without_floor).sum()>0
    # GLB signature differs whenever an actual vertex / topology cut was made
    sigs=[report['model_integrity'][k]['glb_sha256'] for k in models]
    assert len(set(sigs))==4
    assert report['route_spatial']['SKYLIGHT']['volume_collision_samples']==0
    assert report['route_spatial']['SKYLIGHT']['support_success']==len(floor)
    assert report['route_spatial']['BASE']['volume_collision_samples']>0
    assert report['counterfactual']['ROOM']['probes'][1] and not report['counterfactual']['SKYLIGHT']['probes'][1]
    report['limits']=['point samples only: no continuous or whole body clearance guarantee',
                      'support check validates triangles underneath points, not structural support',
                      'voxel signed-distance approximates source with a finite 8m lattice, not exact CSG',
                      'no inhabited city, engineered building, structural/egress or formal architectural approval',
                      'no Blender GUI, MCP, Work, Minecraft operation']
    return report
if __name__=='__main__':
    data=audit();(ROOT/'D30_QA.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:data[k] for k in ('route_spatial','counterfactual')},indent=2))
