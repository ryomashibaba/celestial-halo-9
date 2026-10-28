"""Fresh-process BLEND reload verification. Not a whole-city/occupancy certification."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(sys.argv[sys.argv.index('--')+1]).resolve()
expected=json.loads((OUT/'EDIT_expected_snapshot.json').read_text())
base=json.loads((OUT/'BASE_snapshot.json').read_text())
scene=bpy.context.scene
report={'stage':'fresh BLEND reload','mesh_count':0,'changed':{},'max_reload_error_m':0,'cameras_unchanged':True,'object_set_unchanged':True,'topology_unchanged':True}
obs={o.name:o for o in scene.objects if o.type=='MESH'}
assert set(obs)==set(expected['objects'])
for name,ob in obs.items():
    v=[list(ob.matrix_world@p.co) for p in ob.data.vertices]
    f=[list(p.vertices) for p in ob.data.polygons]
    assert f==expected['objects'][name]['faces']==base['objects'][name]['faces']
    error=max(math.dist(p,q) for p,q in zip(v,expected['objects'][name]['vertices']))
    report['max_reload_error_m']=max(error,report['max_reload_error_m'])
    assert all(math.isfinite(x) for p in v for x in p)
    dist=[math.dist(p,q) for p,q in zip(v,base['objects'][name]['vertices'])]
    if max(dist)>1e-6:report['changed'][name]={'vertices':sum(d>1e-6 for d in dist),'max_m':max(dist)}
    report['mesh_count']+=1
for name,c in base['cameras'].items():
    ob=bpy.data.objects[name]
    assert [list(r) for r in ob.matrix_world]==c['matrix']
    assert ob.data.lens==c['lens'] and ob.data.type==c['type'] and ob.data.ortho_scale==c['ortho_scale']
assert report['max_reload_error_m']<1e-6
assert set(report['changed'])=={'EAST_EXCHANGE_BODY','FORUM_FLOOR','UPPER_PUBLIC_FLOOR','EAST_GROUND_LANDING','EAST_UPPER_LANDING','REAR_OBLIQUE_HABITAT'}

# Probe real top triangles of the two public floors at multiple interior sample points.
deps=bpy.context.evaluated_depsgraph_get()
floor_report={}
for name,z in [('FORUM_FLOOR',36),('UPPER_PUBLIC_FLOOR',112)]:
    ob=obs[name];tree=BVHTree.FromObject(ob,deps)
    hits=0;missing=[]
    for y in [-40,0,30]:
        for x in [20,50,80,105,125]:
            loc,norm,index,dist=tree.ray_cast(Vector((x,y,z+10)),Vector((0,0,-1)),20)
            if loc is not None and abs(loc.z-z)<1e-4:hits+=1
            else:missing.append([x,y])
    floor_report[name]={'top_surface_hits':hits,'samples':15,'missing_points':missing}
report['floor_probe']=floor_report
# Floor contact with the planar east inner boundary, not a whole-body clearance test.
for name in ['FORUM_FLOOR','UPPER_PUBLIC_FLOOR']:
    indices=expected['objects'][name]['bindings']
    assert all(abs(obs[name].data.vertices[i].co.x-138)<1e-6 for i in indices)
east=obs['EAST_EXCHANGE_BODY']
assert all(abs(east.data.vertices[i].co.x-138)<1e-6 for i in [0,5,6,11])
report['east_boundary_x_m']=138
report['local_contact_scope']='Shared X plane at authored boundary vertices, NOT all-width seam watertightness.'
report['technical']='LIMITED PASS for actual saved mesh editing and reload; NOT circulation/collision/structure.'
report['art']='REJECT recorded separately from camera images'
(OUT/'BLEND_RELOAD_AUDIT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('D10_RELOAD_AUDIT',json.dumps(report))
