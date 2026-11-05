"""Package already inspected REAL Blender images. Standard library only.
Does not render, generate art, or declare an art pass.
Run: python -B -X utf8 package_review.py
"""
import hashlib, json, html, struct
from pathlib import Path

P=Path(__file__).resolve().parent
VIEWS=['urban_aerial','central_front','central_rear','east_seafront','human_street','human_public_interior','human_sky_district']
LABELS=['全都市俯瞰','中央正面','中央背面','東内海','地上入口・眼高1.65m','公共内部・眼高1.65m','高所街路・眼高1.65m']
FINAL=[
 'W0は人工的な粗い地形。主役と周辺都市の統合は未成立。24対象未制作。',
 '切除で空洞は開いたが、湾曲殻と住区台の関係がなお主で都市断面が弱い。',
 '天脊の貫通空間は見えるが、単純な刃状質量と広い無開口面が残る。上端のフレーミングも不十分。',
 '東殻の巨大室の切断と厚い居住地盤は見える。住宅都市としての厚みと用途階層は未達。',
 '本物の地上斜路と入口。巨大壁・梁が支配し、人間尺度の行先・街路の設計が弱い。',
 '床欠損状表示と背後の閉塞は改善。巨大空間に対する公共用途・建築密度が不足。',
 '壁の先の見通しが開いた。少数の中庭翼であり、本格的な高所生活都市ではない。']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
states={r:json.loads((P/f'{r}_geometry.json').read_text()) for r in ['R0','R1','R2']}
assert states['R0']['cameras']==states['R1']['cameras']==states['R2']['cameras']
expected1={'ALPHA_EAST_DISPLACED_SHELL','ALPHA_WEST_INHABITED_SHELL','BETA_OBLIQUE_SPINE','GROUND_PROCESSIONAL_RISE','H1_PUBLIC_PROMENADE','NAVE_NORTH_PUBLIC_STREET'}
expected2={'ALPHA_EAST_DISPLACED_SHELL','ALPHA_WEST_INHABITED_SHELL','BETA_OBLIQUE_SPINE','EAST_CIVIC_SECTION','H1_INHABITED_TERRAIN','H1_PUBLIC_MARKET_WEST','PUBLIC_ASSEMBLY_NORTH','GROUND_PROCESSIONAL_RISE','H1_PUBLIC_PROMENADE','NAVE_NORTH_PUBLIC_STREET','CIVIC_NAVE_FOUNDATION'}
expected2|={n for n in states['R1']['meshes'] if n.startswith('H1_RESIDENTIAL_COURT_B')}
audits=[]
for a,b,expected in [('R0','R1',expected1),('R1','R2',expected2)]:
    before=states[a]['meshes'];after=states[b]['meshes'];assert before.keys()==after.keys()
    changed={n for n in before if before[n]!=after[n]}
    assert changed==expected,(changed^expected)
    audits.append({'from':a,'to':b,'same_saved_scene_lineage':True,
      'changed_existing_meshes':sorted(changed),'untargeted_meshes_identical_count':len(before)-len(changed),
      'object_names_and_mesh_count_unchanged':True,'camera_matrices_lenses_clip_planes_identical':True,
      'source_blend_sha256':sha(P/f'{a}.blend'),'result_blend_sha256':sha(P/f'{b}.blend'),
      'art':'REJECT','note':'Geometry hashes captured each checkpoint. Native file digests catalogued at close-out; no claim of independent contemporaneous before/after file-hash capture.'})
images=[]
for r in ['R0','R1','R2']:
    for v in VIEWS:
        p=P/'renders'/r/(v+'.png');data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n'
        w,h=struct.unpack('>II',data[16:24]);assert (w,h)==(900,600)
        images.append({'stage':r,'view':v,'path':p.relative_to(P).as_posix(),'sha256':sha(p),
          'width':w,'height':h,'directly_opened_and_visually_reviewed_by_coordinator':True,
          'renderer':'Blender 5.2.1 LTS / Cycles CPU / 12 samples','art':'REJECT'})
inspect=json.loads((P/'PRODUCTION_INSPECTION.json').read_text())
for v in VIEWS[-3:]:assert abs(inspect['cameras'][v]['eye_above_support_m']-1.65)<.001
registry=json.loads((P/'30_TARGETS.json').read_text());assert len(registry)==30
resources=[json.loads(p.read_text(encoding='utf-8-sig')) for p in P.glob('render_*_resources.json')]
report={'art':'REJECT','formal_adoption':False,'city_master_complete':False,'minecraft':'HOLD',
 'basis_branch':'research/r33-s27-d48-r4-e1b-oneclick-windows-20261031',
 'basis_head':'f14e8561a5a8d169d7995c83f47020a6161d5861',
 'production_branch':'research/r33-s27-d48-r4-e2-art-production-20261105',
 'art_improvement_cycles_completed':2,'directly_reviewed_delivery_images':21,
 'actual_render_executions':28,'discarded_render_count':7,
 'discard_reason':'R2 draft floor-height correction, final full suite rerendered',
 'source_policy':'main explicit refs; see README_JA.md for blob SHAs',
 'user_authorized_background_blender':True,'computer_use':False,'new_installations':False,
 'render_device':'CPU','render_threads':2,'observed_process_priority':'BelowNormal',
 'maximum_sampled_render_ram_mb':max(r['peak_sampled_ram_mb'] for r in resources),
 'fully_completed_targets':0,'partial_study_targets':6,'not_made_targets':24,
 'cameras_identical_all_three_stages':True,'edit_audits':audits,'images':images,
 'final_visual_findings':dict(zip(VIEWS,FINAL)),
 'limitations':['ART REJECT; no detailed master city produced','No complete route / lift operation certification','Official historical/world coordinate transforms unverified','PC responsiveness and all GPU activity not independently certified','Native source digests recorded at close-out, not independently captured before each edit']}
(P/'REVIEW.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
cards=[]
for i,v in enumerate(VIEWS):
    ims=''.join(f'<figure><a href="renders/{r}/{v}.png"><img loading="lazy" src="renders/{r}/{v}.png" alt="{html.escape(LABELS[i])} {r} 実Blenderレンダー"></a><figcaption>{r} — ART REJECT</figcaption></figure>' for r in ['R0','R1','R2'])
    cards.append(f'<section><h2>{html.escape(LABELS[i])}</h2><p>{html.escape(FINAL[i])}</p><div class="row">{ims}</div></section>')
page='''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HALO-9 R4-E2 / ART REJECT</title><style>body{background:#10191e;color:#e3eaed;font:16px/1.7 system-ui,sans-serif;max-width:1650px;margin:32px auto;padding:0 24px}h1{font-size:30px}.status{color:#ffbe9d}a{color:#9ad9ed}.row{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}figure{margin:0}img{width:100%;height:auto}figcaption{font-size:13px;color:#adbcc3}section{border-top:1px solid #34454e;padding:22px 0}h2{font-size:21px;margin:0}p{max-width:1000px}nav{display:flex;gap:22px;flex-wrap:wrap}@media(max-width:850px){.row{grid-template-columns:1fr}}</style><body><h1>CELESTIAL HALO-9 / R4-E2</h1><p class="status">ART REJECT · 正式採択0 · CITY MASTER未完成 · Minecraft HOLD</p><p>同じBLENDの主形状を実画像から批評し2回直接修正。実際の7カメラ・同一照明の比較。クリックで元PNGを開く。画像生成AI・画像上の美化なし。30対象中、6対象は部分研究、24対象は未制作、完成対象0。</p><nav><a href="E2_WORKING.blend">編集可能な最終BLEND</a><a href="README_JA.md">制作・美術審査記録</a><a href="30_TARGETS.json">全30対象の状態</a><a href="REVIEW.json">画像とメッシュ変更記録</a></nav>'''+''.join(cards)+'</body></html>'
(P/'review.html').write_text(page,encoding='utf-8')
files=[]
for p in sorted(P.rglob('*')):
    if p.is_file() and p.name!='FILE_MANIFEST.json' and p.suffix not in ('.blend1','.blend2') and '__pycache__' not in p.parts:
        files.append({'path':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
(P/'FILE_MANIFEST.json').write_text(json.dumps({'files':files},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':'PACKAGED_ART_REJECT','delivered_images':len(images),'art_cycles':2,'changed_meshes':[len(a['changed_existing_meshes']) for a in audits],'file_count':len(files),'bytes':sum(x['bytes'] for x in files)},ensure_ascii=False))
