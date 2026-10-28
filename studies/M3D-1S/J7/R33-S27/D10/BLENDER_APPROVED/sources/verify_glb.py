"""Independent GLB byte parser: no Blender or exporter library.
Uses scene graph matrices, remaps split exported corners to saved source vertices.
Requires NumPy only. Does NOT prove art, collision-free interiors or accessibility.
"""
import json,struct,sys,math
from pathlib import Path
import numpy as np
OUT=Path(sys.argv[1]).resolve()
TYPES={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
DT={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}
def parse(path):
    raw=path.read_bytes();magic,version,size=struct.unpack_from('<4sII',raw)
    assert magic==b'glTF' and version==2 and size==len(raw)
    off=12;doc=None;binary=None
    while off<len(raw):
        length,kind=struct.unpack_from('<II',raw,off);off+=8
        chunk=raw[off:off+length];off+=length
        if kind==0x4e4f534a:doc=json.loads(chunk)
        elif kind==0x004e4942:binary=chunk
    assert doc and binary is not None
    def array(index):
        a=doc['accessors'][index];assert 'sparse' not in a
        v=doc['bufferViews'][a['bufferView']];assert v.get('buffer',0)==0
        dtype=np.dtype(DT[a['componentType']]);n=TYPES[a['type']]
        start=v.get('byteOffset',0)+a.get('byteOffset',0)
        stride=v.get('byteStride',n*dtype.itemsize)
        return np.ndarray((a['count'],n),dtype=dtype,buffer=binary,offset=start,strides=(stride,dtype.itemsize)).copy()
    def transform(node):
        if 'matrix' in node:return np.asarray(node['matrix']).reshape((4,4),order='F')
        x,y,z,w=node.get('rotation',[0,0,0,1]);m=np.eye(4)
        m[:3,:3]=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                    [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                    [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
        m[:3,:3]=m[:3,:3]@np.diag(node.get('scale',[1,1,1]));m[:3,3]=node.get('translation',[0,0,0])
        return m
    result={}
    def visit(index,parent):
        node=doc['nodes'][index];matrix=parent@transform(node)
        if 'mesh' in node:
            vv=[];ff=[]
            for p in doc['meshes'][node['mesh']]['primitives']:
                assert p.get('mode',4)==4
                v=array(p['attributes']['POSITION']).astype(float)
                v=(matrix@np.c_[v,np.ones(len(v))].T).T[:,:3]
                v=v[:,[0,2,1]]*np.array([1,-1,1]) # glTF Y-up -> Blender Z-up
                idx=array(p['indices']).ravel().astype(int) if 'indices' in p else np.arange(len(v))
                assert len(idx)%3==0 and idx.min()>=0 and idx.max()<len(v)
                ff.extend((idx.reshape((-1,3))+len(vv)).tolist());vv.extend(v.tolist())
            result[node['name']]={'v':np.asarray(vv),'f':np.asarray(ff)}
        for c in node.get('children',[]):visit(c,matrix)
    for index in doc['scenes'][doc.get('scene',0)]['nodes']:visit(index,np.eye(4))
    return result

stages={};connectivity={};summary={}
for stage,snapshot_name in [('BASE','BASE_snapshot.json'),('EDIT','EDIT_expected_snapshot.json')]:
    expected=json.loads((OUT/snapshot_name).read_text())['objects']
    meshes=parse(OUT/('D10_'+stage+'.glb'));assert set(meshes)==set(expected)
    max_error=0;triangles=0;degenerate=0;maps={}
    for name,m in meshes.items():
        v,f=m['v'],m['f'];source=np.array(expected[name]['vertices'])
        assert np.isfinite(v).all()
        dist=np.linalg.norm(v[:,None,:]-source[None,:,:],axis=2)
        err=max(float(dist.min(axis=1).max()),float(dist.min(axis=0).max()))
        max_error=max(max_error,err);assert err<1e-4,(stage,name,err)
        mapping=dist.argmin(axis=1)
        maps[name]=sorted(tuple(sorted(mapping[t].tolist())) for t in f)
        area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)/2
        degenerate+=int((area<1e-9).sum());triangles+=len(f)
    assert degenerate==0
    stages[stage]=meshes;connectivity[stage]=maps
    summary[stage]={'meshes':len(meshes),'triangles':triangles,'degenerate_triangles':degenerate,'max_world_coordinate_error_to_saved_mesh_m':max_error}
changed_export_topology=[name for name in connectivity['BASE'] if connectivity['BASE'][name]!=connectivity['EDIT'][name]]
report={'scope':'Independent GLB byte/scene-graph/world-coordinate verification against saved BLEND vertex snapshots',
        'stages':summary,'source_face_topology_unchanged':True,
        'export_triangulation_changed_objects':changed_export_topology,
        'limits':['No water-tightness or union collision claim','No occupancy or full-width route certification','Same assistant wrote both validators; not another agent review'],
        'technical':'TECH LIMITED PASS - actual GLB export matches saved edited meshes in world space'}
(OUT/'INDEPENDENT_GLB_AUDIT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
