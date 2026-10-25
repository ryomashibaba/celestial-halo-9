"""Actual saved R2 geometry: internal cameras, two independently cut 3D copies."""
import bpy,bmesh,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).parent;sys.path.insert(0,str(ROOT))
import build_r13 as H
SOURCE=ROOT/'revision_2/R13_C_R2.blend'
INTERIOR={
 '07_MAIN_CAVERN':((0,-250,1000),(-50,1350,2450),'PERSP',21),
 '08_MID_CITY':((-2110,-600,1830),(-1300,900,2110),'PERSP',27),
 '09_HUMAN_EYE_1_7M':((-1985,-180,1601.7),(-1750,500,1770),'PERSP',24),
 '10_REVERSE_WORLD':((100,2360,1030),(-300,1500,2670),'PERSP',23),
 '11_ZENITH_WORLD':((-200,500,3540),(-520,1050,4000),'PERSP',24)
}

def open_source():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));H.attach_existing()

def ray_evidence():
    dg=bpy.context.evaluated_depsgraph_get();result={}
    for name,(origin,target,typ,val) in INTERIOR.items():
        origin=Vector(origin);record={}
        for direction,d in [('up',(0,0,1)),('down',(0,0,-1)),('east',(1,0,0)),('west',(-1,0,0)),('north',(0,1,0)),('south',(0,-1,0))]:
            hit,co,no,idx,ob,mat=bpy.context.scene.ray_cast(dg,origin,Vector(d),distance=10000)
            record[direction]={'hit':bool(hit),'distance_m':(co-origin).length if hit else None,'object':ob.name if hit else None}
        result[name]={'eye_m':list(origin),'six_surface_rays':record}
    result['scope']='Surface rays and source cross-sections only. No full enclosed volume, habitation capacity, route continuity, collision or walking certification.'
    (ROOT/'qa'/'INTERNAL_SURFACE_PROBES.json').write_text(json.dumps(result,indent=2),encoding='utf8')

def section(axis,offset,name):
    open_source()
    # Bake evaluated source to each independent cut copy. Original is never saved here.
    dg=bpy.context.evaluated_depsgraph_get();manifest=[]
    normal=Vector((0,1,0) if axis=='Y' else (1,0,0))
    point=normal*offset
    CUT=H.material('Actual cut solid ochre',(.55,.30,.10),.05,.65)
    for ob in list(H.ARCH.objects):
        if ob.type!='MESH':continue
        ev=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg)
        oldv=len(me.vertices);ob.modifiers.clear();ob.data=me
        # All R13 objects are native metre meshes; matrix transforms retained.
        bm=bmesh.new();bm.from_mesh(me)
        lpoint=ob.matrix_world.inverted()@point
        lnormal=(ob.matrix_world.to_3x3().transposed()@normal).normalized()
        geom=list(bm.verts)+list(bm.edges)+list(bm.faces)
        res=bmesh.ops.bisect_plane(bm,geom=geom,dist=.0001,plane_co=lpoint,plane_no=lnormal,clear_outer=True,clear_inner=False)
        edges=[g for g in res['geom_cut'] if isinstance(g,bmesh.types.BMEdge) and g.is_boundary]
        caps=bmesh.ops.holes_fill(bm,edges=edges,sides=0).get('faces',[]) if edges else []
        matindex=len(me.materials);me.materials.append(CUT)
        for f in caps:f.material_index=matindex
        bm.to_mesh(me);bm.free();me.update()
        manifest.append(dict(object=ob.name,before_vertices=oldv,after_vertices=len(me.vertices),cap_faces=len(caps)))
    if axis=='Y':view=((6500,-11500,7000),(0,400,2300),'ORTHO',8100)
    else:view=((11500,-6500,7000),(-500,500,2300),'ORTHO',8100)
    H.camera(view)
    folder=ROOT/'sections'/name;folder.mkdir(parents=True,exist_ok=True)
    bpy.context.scene['section_plane']=json.dumps(dict(axis=axis,offset_m=offset,kept='negative halfspace'))
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/(name+'.blend')),compress=True)
    bpy.ops.object.select_all(action='DESELECT')
    for o in H.ARCH.objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(folder/(name+'.glb')),export_format='GLB',use_selection=True)
    H.render(folder,{name:view})
    (folder/'actual_cut_manifest.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),plane_axis=axis,offset_m=offset,method='evaluated source BMesh bisect + actual boundary caps',objects=manifest),indent=2),encoding='utf8')

if __name__=='__main__':
    open_source();ray_evidence();H.render(ROOT/'revision_2',INTERIOR)
    section('Y',680,'SECTION_XZ_Y680')
    section('X',0,'SECTION_YZ_X0')
