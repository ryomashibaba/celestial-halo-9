"""Separate Blender process checks the actual saved sources, images and safety metadata.
Not an ART test, construction clearance or route/accessibility certification.
"""
import bpy,pathlib,json,hashlib,math,struct
from mathutils import Vector
R=pathlib.Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fingerprint(o):
    h=hashlib.sha256()
    if o.type=='MESH':
        for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
        for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
    return h.hexdigest()
before={o.name:fingerprint(o) for o in bpy.data.scenes['E11_INHABITED_SECTION_RESEARCH'].objects if o.type=='MESH'}
cams0={o.name:[list(row) for row in o.matrix_world] for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('E11_')}
bpy.ops.wm.open_mainfile(filepath=str(R/'E11_INHABITED_SECTION_WORKING.blend'))
S=bpy.data.scenes['E11_INHABITED_SECTION_RESEARCH'];bpy.context.window.scene=S
bpy.context.view_layer.update()
after={o.name:fingerprint(o) for o in S.objects if o.type=='MESH'}
changed=[n for n in before.keys()&after.keys() if before[n]!=after[n]]
finite=all(math.isfinite(c) for o in S.objects if o.type=='MESH' for v in o.data.vertices for c in v.co)
cams1={o.name:[list(row) for row in o.matrix_world] for o in S.objects if o.type=='CAMERA'}
assert all(cams0[n]==cams1[n] for n in cams0),'CAMERA_MATRIX_CHANGED'
assert finite and len(changed)>20,'MESH_EDITS_NOT_PROVEN'
assert S['FORMAL_ART_ACCEPTED']==0 and S['COMPLETED_TARGETS']==0 and S['CONSTRUCTION']=='HOLD'
assert S['COORDINATES']=='ISOLATED_RESEARCH_METRES_NOT_WORLD_REGISTERED'
assert len(json.loads(bpy.data.texts['E11_30_TARGET_OBLIGATIONS_NOT_COMPLETION.json'].as_string()))==30
assert not bpy.data.libraries,'EXTERNAL_BLEND_DEPENDENCY'
ground=[]
for name in ['E11_NAVE_HUMAN','E11_H1_HUMAN']:
    cam=bpy.data.objects[name];hit,loc,normal,face,obj,m=S.ray_cast(bpy.context.evaluated_depsgraph_get(),cam.location,Vector((0,0,-1)),distance=10)
    assert hit,'NO_WALKABLE_SUPPORT_BELOW_CAMERA'
    clearance=(cam.location-loc).length
    assert 1.4<clearance<2.1,(name,clearance)
    ground.append({'camera':name,'support_object':obj.name,'eye_clearance_m':clearance})
image_checks=[]
manifest=json.loads((R/'R2'/'render_manifest.json').read_text(encoding='utf-8'))
assert len(manifest)==3
for rec in manifest:
    p=R/'R2'/rec['file'];data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n'
    w,h=struct.unpack('>II',data[16:24]);assert (w,h)==(1200,900)
    assert sha(p)==rec['sha256']
    image=bpy.data.images.load(str(p),check_existing=False)
    pixels=image.pixels[:];rgb=[pixels[i] for i in range(0,len(pixels),16)]
    lo,hi=min(rgb),max(rgb);mean=sum(rgb)/len(rgb)
    assert hi-lo>.1 and .005<mean<.995,'IMAGE_BLACK_OR_UNIFORM'
    image_checks.append({'file':rec['file'],'width':w,'height':h,'sha256':sha(p),'sample_min':lo,'sample_max':hi,'sample_mean':mean})
    bpy.data.images.remove(image)
report={'result':'TECH_PASS_NOT_ART','blender_version':bpy.app.version_string,
        'source_sha256':sha(R/'E11_INHABITED_SECTION_WORKING.blend'),
        'revision':S['REVISION'],'mesh_objects':len(after),'changed_existing_meshes':len(changed),
        'changed_mesh_names':sorted(changed),'finite_vertices':finite,'same_camera_matrices':True,
        'camera_ground_checks':ground,'images':image_checks,
        'external_blend_libraries':0,'formal_art_accepted':0,'completed_targets':0,
        'minecraft':'HOLD_NO_WORLD_ACCESS','official_coordinates_verified':False,
        'limitations':['No world/canonical coordinate or construction clearance check',
                      'Open façade meshes are not claimed to be watertight',
                      'Public routes and stairs are not accessibility-certified',
                      'Image non-uniformity is not aesthetic approval']}
(R/'INDEPENDENT_TECH_REOPEN.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('E11_INDEPENDENT_REOPEN_PASS',len(changed),'CHANGED_MESHES',flush=True)
