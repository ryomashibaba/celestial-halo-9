"""D47-R4/E0: actual saved Blender native mesh -> direct edit -> identical-camera renders.

This is a deliberately bounded capability test on an ART-REJECTED R3 study.
It does not create a brand-new city from primitive generators, and does NOT
claim to rescue R3 art. It corrects a proven fake-window problem in an
existing inhabited-crossing wall, preserving source object identity.
Headless Blender is direct 3D editing, NOT GUI / MCP visual operation.
Usage: python r4_e0_direct_native_window_edit.py OUTPUT_PATH
"""
import bpy,sys,hashlib,zipfile,json
from pathlib import Path
from mathutils import Vector
import math
BASE = Path("studies/M3D-1S/J7/R33-S27/D47_R3_EVIDENCE/D47_R3_ROOM_FIRST_G0_ART_UNREVIEWED.zip")
EXPECTED_SHA="1469035d58ed1cd720ba4d6ad0b1356bfb3d7f1b95cac001e74c0ba252c8205b"
O=Path(sys.argv[-1]).resolve();O.mkdir(parents=True,exist_ok=True)
assert BASE.is_file(), f"Missing genuine archived original: {BASE}"
with zipfile.ZipFile(BASE) as f:
    name="D47_R3_G0_EDITABLE.blend"
    data=f.read(name)
    old_hash=hashlib.sha256(data).hexdigest()
    assert old_hash==EXPECTED_SHA,(old_hash,EXPECTED_SHA)
    original=O/"R3_READONLY_EXTRACTED.blend"
    original.write_bytes(data)
bpy.ops.wm.open_mainfile(filepath=str(original))
scene=bpy.context.scene
assert scene.get("research_phase")=="D47-R3 functional spaces before outer form"
assert not scene.get("art_adopted")
views=[
    '01_arrival','02_shared_public_room','03_west_inhabited_room',
    '04_east_transit_room','05_threequarter_city','06_rear_urban_section']
original_mesh_names=sorted(o.name for o in bpy.data.objects if o.type=='MESH')
assert len(original_mesh_names)==66,len(original_mesh_names)
cam_signatures={n:(tuple(round(x,5) for x in bpy.data.objects[n].location),
                   tuple(round(x,6) for x in bpy.data.objects[n].rotation_euler))
                for n in views}
def render_group(tag):
    folder=O/tag;folder.mkdir(exist_ok=True)
    for name in views:
        scene.camera=bpy.data.objects[name]
        scene.render.filepath=str(folder/(name+'.png'))
        bpy.ops.render.render(write_still=True)
render_group("BASELINE_R3_SAME_ENGINE")

wall=bpy.data.objects['UPPER_CROSS_LIBRARY_WALL']
assert wall.type=='MESH'
assert len(wall.data.polygons)==6
original_vertex_co=[tuple(v.co) for v in wall.data.vertices]
positions=[(-271,-236),(-188,-143),(-91,-45),(2,53),(105,144),(195,251)]
shapes=[]
for i,(x0,x1) in enumerate(positions):
    glass=bpy.data.objects[f'UPPER_CROSS_GLAZED_INHABITED_WINDOW_{i:02d}']
    assert glass.type=='MESH'
    # Temporary cutter is an editing instrument, never part of final scene.
    bpy.ops.mesh.primitive_cube_add(size=2,location=((x0+x1)*.5,169.5,234))
    cutter=bpy.context.object
    cutter.name=f'R4_E0_TEMPORARY_REAL_WINDOW_CUTTER_{i:02d}'
    cutter.scale=((x1-x0+3)/2,22,23)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.context.view_layer.objects.active=wall
    m=wall.modifiers.new(f'R4_E0_CUT_ACTUAL_OPENING_{i:02d}','BOOLEAN')
    m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter
    try:
        bpy.ops.object.modifier_apply(modifier=m.name)
    except Exception:
        raise RuntimeError("Boolean edit failed at window "+str(i))
    bpy.data.objects.remove(cutter,do_unlink=True)
    # Reposition pre-existing glass away from the cut wall into actual aperture plane.
    for v in glass.data.vertices:
        v.co.y += 7.0
    glass.data.update()
    glass['R4_E0_actually_passes_opening_not_flat_overlay']=True
    shapes.append({'window':glass.name,'x_bounds':[x0,x1],
                   'real_cutout_z_bounds_m':[211,257],
                   'new_glazing_offset_m':7.0})
assert len(wall.data.polygons)>6,len(wall.data.polygons)
assert len(original_vertex_co)!=len(wall.data.vertices) or any(
    math.dist(v.co,original_vertex_co[i])>1e-5
    for i,v in enumerate(wall.data.vertices[:len(original_vertex_co)]))

# Explicitly refuse to call the old solid cultural block an inhabited room.
high=bpy.data.objects['HIGH_OCCUPIED_CULTURAL_VOLUME']
high['R4_E0_actual_content']="SOLID_BLOCK_INVALID_OCCUPIED_ROOM"
high['art_gate']="REJECT_PENDING_REMODELLING"
wall['R4_E0_note']="6 actual boolean holes edited directly into original R3 wall mesh"
wall['R4_E0_edit_source']="R3 original .blend archive sha256 "+EXPECTED_SHA
scene['R4_edit_phase']="E0_INITIAL_DIRECT_NATIVE_GEOMETRY_REPAIR"
scene['R4_art']='UNREVIEWED'
scene['R4_method']='real saved native R3 blend opened then selected mesh topology changed'
scene['R4_no_gui_or_mcp_used']=True
scene['art_adopted']=False
scene['official_minecraft_construction']=False

assert sorted(o.name for o in bpy.data.objects if o.type=='MESH')==original_mesh_names
assert all((tuple(round(x,5) for x in bpy.data.objects[n].location),
            tuple(round(x,6) for x in bpy.data.objects[n].rotation_euler))==cam_signatures[n]
           for n in views)
# Generate actual BEFORE/AFTER from exact same six native cameras. No camera moves.
blend=O/'R4_E0_DIRECT_NATIVE_EDIT.blend'
glb=O/'R4_E0_DIRECT_NATIVE_EDIT.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',
                          export_cameras=False,export_lights=False)
render_group('E0_REAL_WINDOW_CUTS')
report={
    'phase':'R4-E0',
    'original_R3_blend_sha256':old_hash,
    'source_blend_from_actual_zip':str(BASE),
    'original_66_mesh_objects_same_names':True,
    'native_selected_wall':'UPPER_CROSS_LIBRARY_WALL',
    'new_actual_wall_faces':len(wall.data.polygons),
    'real_window_openings':shapes,
    'fixed_camera_signatures':cam_signatures,
    'six_baseline_and_six_E0_same_camera_pngs':True,
    'art_adopted':False,
    'art_review':'UNREVIEWED',
    'solid_high_volume_still_not_inhabitable':True,
    'all_upper_transport_still_unverified':True,
    'gui_editing_test':False,
    'true_direct_saved_native_mesh_editing':True,
    'full_10km_city_master':False,
    'minecraft_write':False
}
(O/'R4_E0_SOURCE_AND_EDIT_MANIFEST.json').write_text(
    json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('R4_E0_DIRECT_SAVED_NATIVE_MESH_EDIT_COMPLETE_ART_UNREVIEWED',
      json.dumps({'wall_faces':len(wall.data.polygons),'original_sha':old_hash,
      'objects':len(original_mesh_names)}))
