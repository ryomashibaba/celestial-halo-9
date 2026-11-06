"""A single image-led revision of saved A0, not regeneration.
Target: roof-like thinness, disconnected inhabited gallery, obstructing market soffit.
"""
import bpy,pathlib,json,hashlib
R=pathlib.Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(R/'SPATIAL_A0.blend'),load_ui=False,use_scripts=False)
changes=[]
def edit(name,positions,reason):
    o=bpy.data.objects[name];before=[list(v.co) for v in o.data.vertices]
    for idx,co in positions.items():o.data.vertices[idx].co=co
    o.data.update()
    changes.append({'object':name,'reason':reason,'vertex_count':len(before),'changed_vertices':sum(tuple(v.co)!=tuple(p) for v,p in zip(o.data.vertices,before)),'before':before,'after':[list(v.co) for v in o.data.vertices]})
edit('SC_WEST_PUBLIC_VAULT',{
  2:(-440,-500,210),3:(-265,-450,300),4:(-90,-390,365),5:(35,-330,345),
  8:(-410,-240,330),9:(-195,-210,430),10:(45,-170,500),11:(180,-100,465),
  14:(-430,40,470),15:(-135,70,605),16:(160,100,715),17:(310,180,650),
  20:(-400,370,644),21:(-85,420,820),22:(245,460,965),23:(380,530,895),
  26:(-300,690,815),27:(20,730,1030),28:(310,770,1155),29:(440,800,1050)
},'A0 nave/aerial: broad empty roof; rebuild transverse section with an inhabited shoulder over the upper gallery and a deeper rising inner edge')
o=bpy.data.objects['SC_WEST_PUBLIC_VAULT'];sol=next(m for m in o.modifiers if m.type=='SOLIDIFY')
changes.append({'object':o.name,'modifier':'structural_depth','before_thickness':sol.thickness,'after_thickness':105,'reason':'A0 membrane silhouette lacked occupied/structural depth; substantive section experiment, not an ART guarantee'});sol.thickness=105;sol.offset=.1
edit('SC_EAST_INHABITED_VAULT',{
  0:(255,-240,290),1:(415,-280,345),2:(620,-300,330),3:(845,-320,210),
  5:(340,10,435),6:(500,-10,515),7:(730,0,545),8:(1010,30,420),
  10:(460,260,620),11:(620,280,715),12:(850,300,725),13:(1090,330,570),
  15:(530,510,775),16:(720,530,880),17:(950,550,865),18:(1160,590,690),
  20:(600,740,930),21:(800,780,1030),22:(1040,800,990)
},'A0 aerial: smooth roof pierced by an isolated hole; fold the occupied shoulders around the public city void rather than shifting the object')
o=bpy.data.objects['SC_EAST_INHABITED_VAULT'];sol=next(m for m in o.modifiers if m.type=='SOLIDIFY')
changes.append({'object':o.name,'modifier':'structural_depth','before_thickness':sol.thickness,'after_thickness':120,'reason':'Make the exposed rim a deep section instead of a thin canopy'});sol.thickness=120;sol.offset=.2
edit('SC_H1_MARKET_ROOM',{
  0:(650,300,437),1:(675,300,493),2:(750,300,515),3:(840,300,500),4:(880,300,437),
  5:(635,390,437),6:(670,390,505),7:(755,390,535),8:(855,390,515),9:(900,390,437),
  10:(650,485,437),11:(690,485,498),12:(770,485,525),13:(850,485,500),14:(890,485,437)
},'A0 fixed H1: near soffit masks the city. Widen the market room and lift its actual ceiling section; fixed camera untouched')
# Lift the existing arcade roof/floor stack to meet the reconstructed western shoulder.
# This mesh remains a room volume, not a moved exterior facade attached as decoration.
o=bpy.data.objects['SC_WEST_UPPER_INHABITED_STREET'];before=[list(v.co) for v in o.data.vertices]
for v in o.data.vertices:
    # Rear part of the gallery follows the increasing roof level along its length.
    t=max(0,min(1,(v.co.y-300)/320));v.co.z+=t*95
o.data.update()
changes.append({'object':o.name,'reason':'A0 upper inhabited gallery was visually detached from the canopy. Regrade its actual section along the ascending roof shoulder; no matrix change','changed_vertices':sum(tuple(v.co)!=tuple(p) for v,p in zip(o.data.vertices,before))})
(R/'IMAGE_LED_REVISION.json').write_text(json.dumps({'observed':['A0/E11_NAVE_HUMAN.png','A0/E11_H1_HUMAN.png','A0/E11_URBAN_AERIAL.png'],'source_blend_sha256':hashlib.sha256((R/'SPATIAL_A0.blend').read_bytes()).hexdigest(),'objects_added':0,'objects_removed':0,'method':'Existing control-point and mesh-vertex authoring plus real thickness edits; Python aided, no GUI brush','changes':changes},indent=2),encoding='utf8',newline='\n')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'SPATIAL_A1.blend'))
print('IMAGE_LED_REVISION_SAVED',flush=True)
