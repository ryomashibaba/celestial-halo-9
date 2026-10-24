"""Offline evidence packaging; uses only this research and immutable source hashes.
Run with Python -B -X utf8. Pillow is used only for labelled render contact sheets.
No generative images, retouching, actual Minecraft save access, or world data I/O.
"""
import ast
import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageStat

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
BASE='c57c0b419d91fe44e75bcd945ed596800023cd4f'
MAIN='a2f88995eee8d10ee4830dbdf33ccb9c0790de8f'
BRANCH='research/m3d1s-j7-r11-local-blender-art-20261025'

def run(*args):
    return subprocess.check_output(['git',*args],cwd=REPO)

def dump(p,data):
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def sheet(filename,names,folders,labels,width=480):
    h=round(width*1100/1440)
    canvas=Image.new('RGB',(len(folders)*width,len(names)*(h+31)+60),'#0b1720')
    d=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
    d.text((16,12),'CELESTIAL HALO-9 | J7-R11 | REAL BLENDER RENDERS | ART: REJECT',font=font,fill='#f0ede5')
    sources=[]
    for col,(folder,label) in enumerate(zip(folders,labels)):
        for row,name in enumerate(names):
            p=ROOT/folder/(name+'.png')
            im=Image.open(p).convert('RGB')
            im=im.resize((width,h),Image.Resampling.LANCZOS)
            y=60+row*(h+31)
            canvas.paste(im,(col*width,y+31))
            d.text((col*width+12,y+6),label+' | '+name,font=font,fill='#c4e4e7')
            sources.append(str(p.relative_to(ROOT)).replace('\\','/'))
    canvas.save(ROOT/'qa'/filename,quality=93)
    return {'file':'qa/'+filename,'sources':sources,'operations':'resize and captions only; no retouch or synthesis'}

def main():
    assert run('branch','--show-current').decode().strip()==BRANCH
    # Only newly authored R11 text: canonical LF before computing byte manifests.
    for p in ROOT.rglob('*'):
        if p.is_file() and (p.suffix in {'.json','.md','.py'} or p.name in {'.gitattributes','.gitignore'}):
            data=p.read_bytes()
            if b'\r\n' in data:p.write_bytes(data.replace(b'\r\n',b'\n'))
    for p in ROOT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'),filename=p.name)
    # Check 46 immutable imported files against their original Git blobs without executing any source.
    original='7e23de66c21450c3f75a5217d933ef514627c6c9'
    names=run('ls-tree','-r','--name-only',original,'research/m121/upstream').decode().splitlines()
    immutable=[]
    for name in names:
        expected=run('show',original+':'+name)
        actual=(REPO/name).read_bytes()
        assert expected==actual,name
        immutable.append({'path':name,'sha256':hashlib.sha256(actual).hexdigest(),'bytes':len(actual)})
    dump(ROOT/'qa'/'IMMUTABLE_SOURCE_READBACK.json',{'source_commit':original,'files':immutable,'all_46_equal':len(immutable)==46})
    # Main policy source stamps refer to fetched commits, not the rolling prose in CURRENT_STATUS.
    policy=[]
    for name in ['AGENTS.md','docs/policy/START_HERE.md','docs/policy/PROJECT_CONSTITUTION.md',
                 'docs/policy/CITY_MASTER_3D_STANDARD.md','docs/policy/CURRENT_STATUS.md',
                 'docs/policy/DECISION_LOG.md','docs/policy/SOURCE_REGISTER.md']:
        contents=run('show',MAIN+':'+name)
        policy.append({'path':name,'commit':MAIN,'sha256':hashlib.sha256(contents).hexdigest()})
    dump(ROOT/'qa'/'PREFLIGHT.json',{
        'date_jst':'2026-10-25','repository':'ryomashibaba/celestial-halo-9',
        'R10_PR':42,'R10_PR_confirmed_draft_open':True,'R10_verified_head':BASE,
        'main_verified_head':MAIN,'policies_read':policy,
        'current_status_freshness_note':'main CURRENT_STATUS prose is dated 2026-10-23 and predates R10; actual PR42/API head verified separately.',
        'blender_version':'5.2.1 LTS','mcp_addon_version':[1,6],'mcp_protocol_actual':5,
        'mcp_protocol_expected':15,'mcp_actual_read_edit_save_and_look':'SUCCEEDED_WITH_LEGACY_FALLBACK',
        'gpu':'NVIDIA GeForce RTX 5080 Laptop GPU','renderer':'Cycles / OptiX',
        'initial_gui_scene':'unsaved clean default: Cube, Camera, Light; no project original open',
        'live_primary_revision':True,'native_brush_sculpt_or_manual_GUI_mesh_edit':'NOT_PERFORMED; bpy mesh edits via MCP',
        'actual_minecraft_save_access':False,'official_coordinate_registration':'UNVERIFIED',
        'neutral_10km_datum_is_city_master':False,'other_work_untracked_preserved':True,
        'protected_paths_changed':False,'main_written':False,'existing_PRs_updated':False,
        'construction':'HOLD','formal_art_adopted':0})
    readback=json.loads((ROOT/'qa'/'BLEND_GLB_READBACK.json').read_text(encoding='utf8'))
    images=[];models={};camera_sets=[]
    for folder,label in [('concept_A','A'),('concept_B','B'),('refined','B_REFINED')]:
        cams=json.loads((ROOT/folder/'cameras.json').read_text(encoding='utf8'))
        camera_sets.append(cams)
        expected=[f'{i:02d}_' for i in range(1,10)]
        renders=sorted((ROOT/folder).glob('*.png'))
        assert len(renders)==9,folder
        for p,prefix in zip(renders,expected):
            assert p.name.startswith(prefix)
            with Image.open(p) as im:
                assert im.size==(1440,1100)
                stat=ImageStat.Stat(im.convert('RGB'))
                assert max(stat.stddev)>5 and max(stat.mean)>10,(folder,p.name,stat.mean)
                images.append({'path':str(p.relative_to(ROOT)).replace('\\','/'),'size':im.size,
                               'mean_rgb':stat.mean,'stddev_rgb':stat.stddev})
        m=json.loads((ROOT/folder/'measured.json').read_text(encoding='utf8'))
        assert m['architecture_objects']==readback[label]['native_blend_readback']['objects']
        models[label]={'blend':folder+'/R11_'+label+'.blend','glb':folder+'/R11_'+label+'.glb',
                       'span_m':m['span_m'],'objects':m['architecture_objects'],
                       'triangles':m['evaluated_triangles'],'art':'REJECT',
                       'bounds_and_reimport':'PASS_BASIC_PERSISTENCE_ONLY',
                       'below_neutral_datum':readback[label]['model_below_neutral_datum'],
                       'walkability':'UNVERIFIED','public_detail_complete':False}
    for key in list(camera_sets[0])[:6]:
        assert camera_sets[0][key]==camera_sets[1][key]==camera_sets[2][key],key
    contacts=[sheet('R11_COMPARE_OBLIQUE.jpg',['02_OBLIQUE'],
                    ['concept_A','concept_B','refined'],['A / reversing land','B / initial fault','B / revised fault']),
              sheet('R11_SIX_VIEW_COMPARISON.jpg',list(camera_sets[0])[:6],
                    ['concept_A','concept_B','refined'],['A','B before','B revised']),
              sheet('R11_INTERIOR_COMPARISON.jpg',list(camera_sets[0])[6:],
                    ['concept_A','concept_B','refined'],['A','B before','B revised']),
              sheet('R11_BEFORE_AFTER.jpg',['02_OBLIQUE','07_PUBLIC_VOID'],
                    ['concept_B','refined'],['B / before','B / after'],640)]
    dump(ROOT/'qa'/'IMAGE_EVIDENCE.json',{'actual_final_source_renders':27,'rendered_model_states':3,
         'matched_wide_view_camera_sets':True,'six_wide_views_include_eye_1_7m_ground':True,
         'additional_close_views_per_model':3,'images':images,'contact_sheets':contacts,
         'generated_or_retouched_model_evidence_images':False})
    dump(ROOT/'R11_HANDOFF.json',{
         'schema':'halo9.j7r11.handoff.v1','date_jst':'2026-10-25','research_branch':BRANCH,
         'base_commit':BASE,'head_locator':'Resolve branch head / git rev-parse HEAD; final receipt is in the chat.',
         'status':'DELIVERED_RESEARCH_MODELS__ART_REJECT__NO_CANONICAL_ADOPTION',
         'models':models,'primary_revision_record':'qa/main_form_revision.json',
         'model_readback':'qa/BLEND_GLB_READBACK.json','image_evidence':'qa/IMAGE_EVIDENCE.json',
         'review':'R11_ART_REVIEW_JA.md','wide_comparison':'qa/R11_SIX_VIEW_COMPARISON.jpg',
         'before_after':'qa/R11_BEFORE_AFTER.jpg','construction':'HOLD',
         'formal_art_accepted':0,'city_master_10km_complete':False,
         'canonical_world_access':False,'protected_originals_changed':False,
         'official_anchor_validation':'UNVERIFIED; no W0/H/SB coordinates invented or integrated',
         'limitations':['A reads as a giant ramp; B as repeated shelves.',
             'Revised B has a larger irregular sky fissure but still reads as curved blades plus floor strips.',
             'Human city density, urban hierarchy, functional public interiors, and continuous circulation remain inadequate.',
             'Inclined retained floorplates require a future design of usable living surfaces; gravity system not resolved.',
             'No structural support, comprehensive collision, watertightness, full void clearance, or traversal certification.',
             'Some study parts extend below neutral ground datum; no official terrain integration.',
             'Initial close cameras inside solids were replaced, not accepted as successful interior evidence.'],
         'next_J7_R12':'Do not decorate these rejected macro shapes. Visually establish a convincing monumental inhabited cross-section with genuinely intersecting city worlds and civic voids, testing side/back/ground before repeating detail; retain only the useful spatial principles.',
         'resume':'Open refined/R11_B_REFINED.blend to inspect the last research state; read review first; macro is REJECT, not an adopted direction.'})
    latest_path=REPO/'studies'/'M3D-1S'/'latest.json'
    latest=json.loads(latest_path.read_text(encoding='utf8'))
    latest.update({'research_id':'M3D-1S/J7-R11','date_jst':'2026-10-25','research_branch':BRANCH,
                   'status':'LOCAL_BLENDER_TWO_CONCEPTS_AND_LIVE_PRIMARY_REVISION_DELIVERED__ART_REJECT',
                   'work_status':'EXECUTED_BY_EXPLICIT_J7_R11_USER_REQUEST',
                   'rebuild_status':'REAL_BLENDER_5_2_1_MODELS_RENDERED_AND_GLB_REIMPORTED',
                   'art_review':'REJECT','next_gate':'J7-R12: overcome ramp/shelf/blade macro and prove inhabited urban scale; no formal adoption or Minecraft construction.'})
    repo_models=json.loads(json.dumps(models))
    for model in repo_models.values():
        for field in ['blend','glb']:model[field]='studies/M3D-1S/J7/R11/'+model[field]
    latest['outputs']['j7']['r11']={'handoff':'studies/M3D-1S/J7/R11/R11_HANDOFF.json',
          'review':'studies/M3D-1S/J7/R11/R11_ART_REVIEW_JA.md','models':repo_models,
          'final_actual_renders':27,'formal_art_accepted':0,'construction':'HOLD'}
    latest.setdefault('historical_missing_through_r10',latest['missing'])
    latest['missing']=['J7_R11_CENTRAL_ART_STILL_REJECT',
          'INHABITED_CITY_SCALE_AND_ARCHITECTURAL_COHERENCE',
          'COMPLETED_PUBLIC_INTERIORS_AND_ACTUAL_TRAVERSAL',
          'FULL_CITY_TRANSPORT_AND_TERRAIN_INTEGRATION',
          'VALIDATED_CANONICAL_COORDINATES',
          'FULL_COLLISION_VOID_CLEARANCE_AND_STRUCTURAL_VALIDATION',
          'REAL_10KM_CITY_ALL_DETAIL','HUMAN_ART_ACCEPTANCE']
    dump(latest_path,latest)
    dump(ROOT/'qa'/'PACKAGE_CHECKS.json',{'script_syntax':'PASS','final_pngs_27_nonblank':'PASS',
          'exact_six_camera_equality':'PASS','three_blend_glb_pairs':'PASS',
          'immutable_upstream_46_exact_bytes':'PASS','art':'REJECT',
          'claim_scope':'Persistence and image completeness only; no aesthetic, construction or city-completion PASS.'})
    # Exclude temporary logs, backup .blend1 and bytecode from deliverables.
    files=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts
           and p.suffix not in ['.log','.blend1','.pyc'] and p.name!='FILES_SHA256.json']
    dump(ROOT/'qa'/'FILES_SHA256.json',{'files':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),
          'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)],
          'note':'The manifest excludes itself, local logs, caches and Blender backup files.'})
    print(json.dumps({'models':models,'final_renders':27,'all_46_immutable_exact':True},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
