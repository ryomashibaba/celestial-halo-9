"""One direct mesh revision after examining all three genuine R0 images.
Correct observed H1 burial and oversized nave plates; no regeneration or detail batch.
"""
import bpy,pathlib,json,math
ROOT=pathlib.Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'GATE_B_R0.blend'),load_ui=False,use_scripts=False)
changes=[]
o=bpy.data.objects['GB_EAST_OCCUPIED_URBAN_GROUND']
before=[list(v.co) for v in o.data.vertices]
# Authored upper boundary of the occupied foundation, below the 437m public street.
heights={5:390,6:420,7:420,8:420,9:400,10:390}
n=len(o.data.vertices)//2
for offset in (0,n):
    for i,z in heights.items():o.data.vertices[offset+i].co.z=z
o.data.update()
changes.append({'object':o.name,'reason':'R0 fixed H1 image was inside the east solid; reconstruct the upper section under the public ground','vertices_changed':sum(tuple(v.co)!=tuple(p) for v,p in zip(o.data.vertices,before)),'before':before,'after':[list(v.co) for v in o.data.vertices]})
# Re-author rib outlines on the existing mesh, narrowing their inner/outside spacing.
# This is a spatial daylight experiment, not an ART pass or merely moving objects.
for side in ('WEST','EAST'):
    for i in range(4):
        o=bpy.data.objects['GB_NAVE_'+side+'_BRANCH_'+str(i)]
        vs=o.data.vertices;n=len(vs)//2
        before=[list(v.co) for v in vs]
        # Front/back depth reduced 32 -> 22m. Front y and world matrices remain fixed.
        for j in range(n):vs[j+n].co.y=vs[j].co.y+22
        # Pair opposite outline points around the shaped rib centreline.
        pairs=[(0,n-1),(1,n-2),(2,n-3),(3,n-4),(4,n-5)] if side=='WEST' else [(0,11),(1,10),(2,9),(3,8),(4,7),(5,6)]
        for a,b in pairs:
            center=(vs[a].co.x+vs[b].co.x)/2
            for k in (a,b):
                vs[k].co.x=center+(vs[k].co.x-center)*.55
                vs[k+n].co.x=vs[k].co.x
        o.data.update()
        changes.append({'object':o.name,'reason':'R0 nave dominated by flat ribs; narrow actual cross-sections to reveal adjacent occupied galleries','vertices_changed':sum(tuple(v.co)!=tuple(p) for v,p in zip(vs,before))})
# No camera, W0, facade, colour, or lighting changes in this revision.
(ROOT/'R1_image_driven_changes.json').write_text(json.dumps({'observed_images':['R0/E11_NAVE_HUMAN.png','R0/E11_H1_HUMAN.png','R0/E11_URBAN_AERIAL.png'],'method':'direct existing mesh vertex edits via Python, not GUI brush','changes':changes,'objects_added':0,'objects_deleted':0},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'GATE_B_R1.blend'))
print('OBSERVED_SECTION_REVISED',len(changes))
