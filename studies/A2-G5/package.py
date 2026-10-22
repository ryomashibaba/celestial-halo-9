"""Validate and index this CONCEPT submission. No model measurements."""
from pathlib import Path
import json, hashlib, datetime, re, xml.etree.ElementTree as ET
from PIL import Image

F=Path(__file__).resolve().parent
BASE=F.parents[1]
WORK=BASE.parents[1]
BASELINE='34aaf362426aaa3c85b8b745651dabcd6073d4a9'
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

concepts=[]
for id,name,dim,principle,nodes in [
 ('I','交庭聖都',{'width':4800,'depth':4200,'height':5800},'Shared public boundaries generate joined urban grounds',['L','M','U']),
 ('II','群街昇都',{'width':5600,'depth':4600,'height':4800},'Branching streets generate multiple inhabited grounds',['R','B','T'])]:
    a,b,c=nodes
    edges=[[a,b],[b,c],[c,a]]
    edges += [[f'H{i}',a] for i in range(1,7)]
    edges += [[f'H{i}',b] for i in range(1,7)]
    edges += [[f'H{i}',f'H{i%6+1}'] for i in range(1,7)]
    edges += [[f'SB{i:02}',a] for i in range(1,17)]
    edges += [['CELESTIAL_SPINE',b]]
    concepts.append({'id':id,'name':name,'formation_principle':principle,'stage':'CONCEPT',
      'dimensions_m':None,'proposed_dimensions_m':dim,'geometry_3d':None,
      'network':{'nodes':sorted(set(sum(edges,[]))),'edges':edges,'edge_meaning':'undirected conceptual access intention; not actual routes or placement',
      'diagram':'compressed schematic only; not every graph edge drawn',
      'SB_attachment':'all SB to arrival network is a functional grouping, not one shared physical entrance',
      'H_bypass':'H1-H2-... order is an abstract connectivity example, NOT a proposed geographic ring or line order'},
      'anchors':{k:{'coordinates':'UNCONFIRMED','connection_endpoint':'UNDETERMINED','existing_role':'PRESERVED_NOT_REASSIGNED'} for k in [f'H{i}' for i in range(1,7)]+[f'SB{i:02}' for i in range(1,17)]},
      'gravity':'downward; horizontal residential floors','artistic_risk':'bar-gate massing' if id=='I' else 'terraced housing wall',
      'provisional_preference':id=='I','art_review_status':'NOT_REVIEWED'})
write(F/'concepts.json',{'study_id':'A2-G5','city_extent_proposed_m':10000,'city_extent_is_not_registered_boundary':True,
    'source_coordinate_systems':{'M207':'U/H/V per user','M204':'X/H/Z per user','confirmed_common_anchors':0,'transformation':None},'concepts':concepts})

local_sources=[
 WORK/'research/G1-A-submission/studies/A2-G1/REPORT.md',
 WORK/'research/G3-A-submission/studies/A2-G3/REPORT.md',
 WORK/'research/G4-A-submission/studies/A2-G4/REPORT.md',
 Path('C:/Users/ryoma/Projects/CELESTIAL_HALO9/repo/docs/M108_M607_MASTER_PLAN.md'),
 Path('C:/Users/ryoma/Projects/CELESTIAL_HALO9/repo/docs/M119_MONUMENTAL_CITY_REVIEW.md'),
 Path('C:/Users/ryoma/Projects/CELESTIAL_HALO9/repo/research/m121/upstream/data/M118_TWO_REGENERATION_DESIGN_LEDGER.json')]
# M117 was identified as legacy evidence; no claim of full independent raw-atlas analysis.
write(F/'sources.json',{'checked_date_jst':'2026-10-23','baseline_commit':BASELINE,
 'primary_web_sources':[
 {'id':'A1','url':'https://www.safdiearchitects.com/projects/habitat-67','publisher':'Safdie Architects'},
 {'id':'A2','url':'https://www.oma.com/projects/the-interlace','publisher':'OMA'},
 {'id':'A2-supplement','url':'https://buro-os.com/projects/the-interlace','publisher':'Büro Ole Scheeren'},
 {'id':'A3','url':'https://big.dk/projects/8-house-2021','publisher':'BIG'},
 {'id':'A3-supplement','url':'https://kk.sites.itera.dk/apps/kk_pub2/pdf/762_9gqrmgtcg3.pdf','publisher':'City of Copenhagen','printed_page':38,'pdf_page_zero_based':19},
 {'id':'A4','url':'https://whc.unesco.org/en/list/192/','publisher':'UNESCO World Heritage Centre'}],
 'local_readonly_sources':[{'path':str(p),'sha256':sha(p),'scope':'report/text reference only'} for p in local_sources],
 'missing_originals':['G2 independent review original','current integrated W0/H/SB/V/axes/SPINE registered masterplan'],
 'user_clarification':['M117 legacy review world is not current formal-city layout','M207 and M204 have zero verified common anchors; no inferred coordinate fusion','Continue conceptual research without waiting for coordinates'],
 'no_cross_track_concepts_used':True})

checks={}
for c in concepts:
    ns=set(c['network']['nodes']);edges=c['network']['edges'];seen={next(iter(ns))}
    while True:
        nxt=seen|{q for p,q in edges if p in seen}|{p for p,q in edges if q in seen}
        if nxt==seen:break
        seen=nxt
    assert seen==ns
    checks[c['id']]={'conceptual_graph_connected':True,'node_count':len(ns),'edge_count':len(edges),
      'actual_traversability_tested':False,'protected_clearance_tested':False,'physical_positions_registered':False}
imgs=[]
for n in ['concept-I','concept-II','comparison']:
    with Image.open(F/(n+'.png')) as im:
        im.verify()
    with Image.open(F/(n+'.png')) as im:size=list(im.size)
    root=ET.parse(F/(n+'.svg')).getroot()
    assert [int(root.attrib['width']),int(root.attrib['height'])]==size
    imgs.append({'path':n+'.png','pixels':size,'svg_dimensions_match':True,'human_visual_review':'reviewed all three PNGs; diagram labels/sections legible; small connector/label corrections applied'})
interfaces=(F/'INTERFACES.md').read_text(encoding='utf-8')
assert all(re.search(r'\|'+re.escape(k)+r'\|',interfaces) for k in [f'H{i}' for i in range(1,7)]+[f'SB{i:02}' for i in range(1,17)])
assert not list(F.glob('*.glb')) and not list(F.glob('*.blend'))
validation={'scope':'CONCEPT documentation, graph and diagram-file integrity only','model_created':False,'dimensions_m':None,
 'not_3d_measured':True,'network_checks':checks,'interfaces_H_count':6,'interfaces_SB_count':16,'precedents_count':4,
 'images':imgs,'visualization_limits':['Plans and sections are schematic; not projections from one 3D model','Plan and section do not certify geometric consistency','Comparison silhouettes are explanatory symbols, not validated hero art','No actual W0 or protected building reproduction'],
 'review':{'formal':'NOT_REVIEWED','internal':'I provisionally preferred; both unaccepted','independent_external_reviewer':False},
 'holds':{'detailed_3d':True,'work_transfer':'PRIOR_APPROVAL_REQUIRED','minecraft_construction':True,'formal_M247C_modified':False},
 'coordinate_fusion_performed':False,'source_files_modified':False}
write(F/'validation.json',validation)

old=json.loads((BASE/'previous-index.json').read_text(encoding='utf-8'))
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
assets=[]
for p in sorted(F.iterdir()):
    if not p.is_file() or p.name in ['manifest.json','SHA256SUMS.txt']:continue
    ext=p.suffix.lower();kind={'.md':'REPORT','.py':'CODE','.json':'JSON','.png':'PNG','.svg':'SVG'}[ext]
    assets.append({'path':p.relative_to(BASE).as_posix(),'kind':kind,'sha256':sha(p),'size_bytes':p.stat().st_size})
entry={'study_id':'A2-G5','title':'交庭聖都／群街昇都 — 三次元居住文明都市と中央建築の統合構想','stage':'CONCEPT',
 'art_review_status':'NOT_REVIEWED','updated_at':stamp,'dimensions_m':None,'proposed_dimensions_m':concepts[0]['proposed_dimensions_m'],
 'dimensions_scope':'Proposed candidate I only; candidate II dimensions in concepts.json. No measured 3D geometry.',
 'assets':assets,'validation':validation,'notes':'I provisionally preferred, no formal art acceptance. G5 supervisor concept review before 3D. Coordinates/endpoints unconfirmed; no M207/M204 fusion.'}
manifest={'schema_version':'1.0','branch':'art/a','track':'A',**entry,'provenance':{'baseline_commit':BASELINE,'previous_study':'A2-G4'},
 'execution':{'new_work_handoff':False,'native_image_generation':False,'3d_model_created':False,'diagrams':'authored 2D vector and matching PNG; no precedent-image copying'}}
write(F/'manifest.json',manifest)
ma={'path':'studies/A2-G5/manifest.json','kind':'JSON','sha256':sha(F/'manifest.json'),'size_bytes':(F/'manifest.json').stat().st_size}
hist=list(old['history'])
if not any(x['study_id']==old['latest']['study_id'] for x in hist):hist.append({'study_id':old['latest']['study_id'],'manifest_path':'studies/'+old['latest']['study_id']+'/manifest.json'})
assert hist[:len(old['history'])]==old['history']
write(BASE/'latest.json',{**old,'latest':{**entry,'assets':assets+[ma]},'history':hist,'last_submission_at':stamp})
(F/'SHA256SUMS.txt').write_text(''.join(a['sha256']+'  '+a['path']+'\n' for a in assets+[ma]),encoding='utf-8')
for a in assets+[ma]:assert sha(BASE/a['path'])==a['sha256']
files=[p for p in F.iterdir() if p.is_file()]+[BASE/'latest.json']
# Binary-safe transfer payload; local staging file excluded from submission.
import base64
write(BASE/'transfer.json',[{'path':p.relative_to(BASE).as_posix(),'content':base64.b64encode(p.read_bytes()).decode(),'git_blob_sha':hashlib.sha1(b'blob '+str(p.stat().st_size).encode()+b'\0'+p.read_bytes()).hexdigest()} for p in files])
print(json.dumps({'files':len(files),'bytes':sum(p.stat().st_size for p in files),'max_file':max(p.stat().st_size for p in files),'history':hist,'checks':'PASS, within stated CONCEPT scope'}))
