#!/usr/bin/env python3
"""D30: bounded oblique, curved civic-void subtraction from an ORIGINAL closed mesh GLB.

This is an isolated research proof: use the saved watertight source GLB as signed-distance
input; subtract parameterized curved tunnel, atrium and angled skylight; export actual GLB
triangles.  It is NOT a general mesh boolean, sculpting in Blender, or a city design.
"""
import io,json,hashlib
from pathlib import Path
import numpy as np
import trimesh
import vtk
from vtkmodules.util.numpy_support import numpy_to_vtk,vtk_to_numpy
from skimage import measure
from scipy import ndimage
TARGET='NEUTRAL_SCULPTED_MASS';ROUTE='PROTECTED_CIVIC_ROUTE';DECK='PROTECTED_ATRIUM_DECK'
NAMES={TARGET,ROUTE,DECK}
BOUNDS=np.array([[-560.,-480.,-190.],[560.,480.,650.]])
GRID_SPACING=8.0
MAX_BYTES=30_000_000

def sha(b):return hashlib.sha256(b).hexdigest()

def route_xy(y):
    y=np.asarray(y,dtype=float)
    return -83+0.28*(y+550)+17*np.sin((y+550)/230)

def route_z(y):
    return 112+0.026*(np.asarray(y,dtype=float)+550)

def route_mesh():
    ys=np.linspace(-550,100,91);centers=np.stack([route_xy(ys),ys,route_z(ys)],axis=1)
    tangent=np.gradient(centers[:,:2],axis=0); tangent/=np.linalg.norm(tangent,axis=1)[:,None]
    normals=np.stack([-tangent[:,1],tangent[:,0]],axis=1)
    verts=[]
    for i,p in enumerate(centers):
        for dz in (0.,-6.):
            for sign in (-1.,1.):verts.append([p[0]+sign*26*normals[i,0],p[1]+sign*26*normals[i,1],p[2]+dz])
    faces=[]
    # indices for top-left/right and bottom-left/right in each section
    for i in range(len(ys)-1):
        a=i*4;b=(i+1)*4
        for quad in [(a,a+1,b+1,b), (a+2,b+2,b+3,a+3), (a,b,b+2,a+2),(a+1,a+3,b+3,b+1)]:
            q=list(quad);faces.extend([(q[0],q[1],q[2]),(q[0],q[2],q[3])])
    for q in [(0,2,3,1),((len(ys)-1)*4,(len(ys)-1)*4+1,(len(ys)-1)*4+3,(len(ys)-1)*4+2)]:
        faces.extend([(q[0],q[1],q[2]),(q[0],q[2],q[3])])
    m=trimesh.Trimesh(vertices=np.array(verts),faces=faces,process=True)
    if m.volume<0:m.invert()
    m.visual.vertex_colors=np.tile(np.array([121,203,191,255],dtype=np.uint8),(len(m.vertices),1))
    return m

def deck_mesh():
    # Readable civic stop-floor, not a completed accessible facility
    m=trimesh.creation.box(extents=[280,165,9])
    m.apply_transform(trimesh.transformations.rotation_matrix(np.arctan(0.026),[1,0,0]))
    midy=87.5;m.apply_translation([100,midy,route_z(midy)-4.5])
    m.visual.vertex_colors=np.tile(np.array([234,214,174,255],dtype=np.uint8),(len(m.vertices),1))
    return m

def source_glb():
    m=trimesh.creation.icosphere(subdivisions=4,radius=1.0)
    u=np.asarray(m.vertices).copy(); unit=u.copy()
    # Test-only sculpted shell with non-planar exterior; never an art candidate.
    u[:,0]=unit[:,0]*430*(1+0.10*unit[:,2])+35*np.sin(2.2*unit[:,1])*unit[:,2]
    u[:,1]=unit[:,1]*325*(1-0.12*unit[:,0])+25*np.sin(2.6*unit[:,0])*unit[:,2]
    u[:,2]=unit[:,2]*310+210+26*np.sin(2.2*unit[:,0])*np.cos(1.7*unit[:,1])
    m.vertices=u
    if m.volume<0:m.invert()
    assert m.is_watertight and m.volume>0
    m.visual.vertex_colors=np.tile(np.array([173,188,207,255],dtype=np.uint8),(len(m.vertices),1))
    sc=trimesh.Scene()
    for name,g in [(TARGET,m),(ROUTE,route_mesh()),(DECK,deck_mesh())]:sc.add_geometry(g,geom_name=name,node_name=name)
    return trimesh.exchange.gltf.export_glb(sc)

def load(raw):
    if len(raw)>MAX_BYTES:raise ValueError('oversized GLB')
    s=trimesh.load(io.BytesIO(raw),file_type='glb',force='scene',process=False)
    if set(s.geometry)!=NAMES or len(s.graph.nodes_geometry)!=len(NAMES):raise ValueError('unsupported mesh set or instancing')
    for node in s.graph.nodes_geometry:
        t,name=s.graph.get(node)
        if not np.allclose(t,np.eye(4)):raise ValueError('scene transform unsupported')
    if any(not x.is_watertight or x.volume<=0 for x in s.geometry.values()):raise ValueError('requires positive watertight individual solids')
    return s

def vtk_poly(m):
    points=vtk.vtkPoints();points.SetData(numpy_to_vtk(np.asarray(m.vertices,dtype=np.float64),deep=True))
    p=vtk.vtkPolyData();p.SetPoints(points)
    a=np.asarray(m.faces,dtype=np.int64)
    cells=vtk.vtkCellArray();cells.SetCells(len(a),numpy_to_vtk(np.c_[np.full(len(a),3,dtype=np.int64),a].ravel(),deep=True,array_type=vtk.VTK_ID_TYPE));p.SetPolys(cells)
    return p

def source_distance(mesh,axes):
    """Voxel approximation to the signed distance from a saved, watertight triangle mesh.

    Unlike exact geometric Boolean, this uses an 8m discretization, and will
    create a new triangle mesh. Accuracy/structure is NOT certified.
    """
    x,y,z=axes; step=GRID_SPACING
    img=vtk.vtkImageData();img.SetDimensions(len(x),len(y),len(z))
    img.SetSpacing(step,step,step)
    img.SetOrigin(float(x[0]),float(y[0]),float(z[0]))
    img.AllocateScalars(vtk.VTK_UNSIGNED_CHAR,1)
    vtk_to_numpy(img.GetPointData().GetScalars()).fill(1)
    stencil=vtk.vtkPolyDataToImageStencil();stencil.SetInputData(vtk_poly(mesh))
    stencil.SetOutputOrigin(*img.GetOrigin());stencil.SetOutputSpacing(*img.GetSpacing())
    stencil.SetOutputWholeExtent(img.GetExtent());stencil.Update()
    cut=vtk.vtkImageStencil();cut.SetInputData(img);cut.SetStencilConnection(stencil.GetOutputPort())
    cut.SetBackgroundValue(0);cut.Update()
    inside=vtk_to_numpy(cut.GetOutput().GetPointData().GetScalars())
    inside=inside.reshape((len(z),len(y),len(x))).transpose(2,1,0).astype(bool)
    outer=ndimage.distance_transform_edt(~inside,sampling=step)-ndimage.distance_transform_edt(inside,sampling=step)
    return outer.astype(np.float32)

def ellipsoid(X,Y,Z,center,radii):
    return np.sqrt(((X-center[0])/radii[0])**2+((Y-center[1])/radii[1])**2+((Z-center[2])/radii[2])**2)-1

def tunnel_field(X,Y,Z,seed=0):
    ys=np.linspace(-650,120,41)
    xs=route_xy(ys); zs=route_z(ys)+92
    # Closely spaced capsules following a non-linear, oblique route.
    dist=np.full(np.broadcast_shapes(X.shape,Y.shape,Z.shape),1e4,dtype=np.float32)
    for x,y,z in zip(xs,ys,zs):
        d=((X-x)/95)**2+((Y-y)/102)**2+((Z-z)/125)**2-1
        np.minimum(dist,d,out=dist)
    return dist

def skylight_field(X,Y,Z):
    # Slants through the roof, continues past the upper shell boundary.
    xc=110+0.23*(Z-230); yc=95+0.13*(Z-230)
    radius=64+0.03*np.maximum(Z-230,0)
    radial=((X-xc)/radius)**2+((Y-yc)/radius)**2-1
    return np.maximum(radial,np.maximum((230-Z)/35,(Z-625)/35))

def carve(raw,plan):
    if set(plan)!={'baseline_sha256','target_geometry','operations','grid_m'}:raise ValueError('unexpected plan shape')
    if plan['baseline_sha256']!=sha(raw):raise ValueError('baseline SHA mismatch')
    if plan['target_geometry']!=TARGET:raise ValueError('protected/unrecognized target')
    ops=plan['operations']
    if not isinstance(ops,list) or ops not in [['tunnel'],['tunnel','atrium'],['tunnel','atrium','skylight']]:raise ValueError('invalid order / unsupported operation')
    if plan['grid_m']!=GRID_SPACING:raise ValueError('unvalidated voxel spacing')
    s=load(raw)
    source_bounds=np.asarray(s.geometry[TARGET].bounds)
    if np.any(source_bounds[0]<BOUNDS[0]+2*GRID_SPACING) or np.any(source_bounds[1]>BOUNDS[1]-2*GRID_SPACING):
        raise ValueError('source does not fit safely inside study raster bounds')
    if len(s.geometry[TARGET].faces)>200_000:
        raise ValueError('target too dense for validated limited study')
    x=np.arange(BOUNDS[0,0],BOUNDS[1,0]+0.1,GRID_SPACING)
    y=np.arange(BOUNDS[0,1],BOUNDS[1,1]+0.1,GRID_SPACING)
    z=np.arange(BOUNDS[0,2],BOUNDS[1,2]+0.1,GRID_SPACING)
    axes=(x,y,z)
    outer=source_distance(s.geometry[TARGET],axes)
    # Broadcasting arrays avoids fully materializing X,Y,Z 3D coordinates.
    X=x[:,None,None].astype(np.float32);Y=y[None,:,None].astype(np.float32);Z=z[None,None,:].astype(np.float32)
    void=tunnel_field(X,Y,Z)
    if 'atrium' in ops:
        void=np.minimum(void,ellipsoid(X,Y,Z,[100,85,204],[180,165,157]))
    if 'skylight' in ops:
        void=np.minimum(void,skylight_field(X,Y,Z))
    # Inside outside material is negative. Subtract void where void field < 0.
    signed=np.maximum(outer,-void*72.0)
    vertices,faces,_,_=measure.marching_cubes(signed,level=0,spacing=(GRID_SPACING,)*3,
                                              allow_degenerate=False)
    vertices+=BOUNDS[0]
    m=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
    m.remove_unreferenced_vertices()
    if m.volume<0:m.invert()
    if not m.is_watertight or not m.is_winding_consistent or m.volume<=0:raise ValueError('nonmanifold or inverted CSG mesh')
    m.visual.vertex_colors=np.tile(np.array([183,201,218,255],dtype=np.uint8),(len(m.vertices),1))
    original={n:(np.asarray(s.geometry[n].vertices).copy(),np.asarray(s.geometry[n].faces).copy()) for n in (ROUTE,DECK)}
    s.geometry[TARGET]=m
    for n,(verts0,faces0) in original.items():
        if not np.array_equal(s.geometry[n].vertices,verts0) or not np.array_equal(s.geometry[n].faces,faces0):raise ValueError('protected geometry moved')
    result=trimesh.exchange.gltf.export_glb(s)
    again=load(result)
    for n,(verts0,faces0) in original.items():
        if not np.allclose(again.geometry[n].vertices,verts0,atol=1e-5) or not np.array_equal(again.geometry[n].faces,faces0):
            raise ValueError('protected geometry export corrupted')
    return result

def main():
    import sys
    if len(sys.argv)!=4:raise SystemExit('python d30_freeform_csg.py source.glb plan.json output.glb')
    src,plan,dst=map(Path,sys.argv[1:]);
    if src.resolve()==dst.resolve() or dst.exists():raise ValueError('refuse source/output overwrite')
    result=carve(src.read_bytes(),json.loads(plan.read_text('utf-8')))
    dst.write_bytes(result)
    print(json.dumps({'output':str(dst),'sha256':sha(result),'bytes':len(result)}))
if __name__=='__main__':main()
