"""Offline source, image and measured QA; generates honest research handoff.
Run with python -B -X utf8. Does not regenerate or alter models/renders.
"""
import json,sys,hashlib,ast
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;Q=R/'qa'
qa=json.loads((Q/'BLEND_GLB_READBACK.json').read_text('utf8'))
sp=json.loads((Q/'SPATIAL_INSPECTION.json').read_text('utf8'))
assert qa['basic_persistence_pass'];assert len(qa['models'])==7
assert sp['floor_ray']['pass_1_7m_2mm']
for p in R.glob('*.py'):ast.parse(p.read_text('utf8'),filename=p.name)
for p in R.rglob('*.png'):
 with Image.open(p) as im:assert im.size==(1100,1000),(p,im.size);im.verify()
final=qa['models']['R17_REVISION_2']['native'];floor=sp['floor_ray']
diff=ImageChops.difference(Image.open(R/'revision_2/02_OBLIQUE.png').convert('RGB'),Image.open(Q/'GLB_REIMPORT_OBLIQUE.png').convert('RGB'))
comparison={'mean_absolute_rgb_difference_0_255':ImageStat.Stat(diff).mean,'max_absolute_rgb_difference_0_255':[r[1] for r in diff.getextrema()],'scope':'Native final macro render versus independently imported GLB with appended original studio only. Cycles denoising and normals may differ; not an art certificate.'}
(Q/'GLB_NATIVE_IMAGE_COMPARISON.json').write_text(json.dumps(comparison,indent=2),encoding='utf8')
rows=[]
for name,result in qa['models'].items():
 m=result['native'];c=result['checks'];rows.append('| '+name+' | '+' × '.join(f'{v:.3f}' for v in m['span_xyz_m'])+f" | {m['mesh_objects']:,} / {m['triangles']:,} | {max(c['bounds_max_error_m'],c['vertices_bidirectional_max_error_m'],c['triangle_centroids_bidirectional_max_error_m']):.6f} | {m['separate_mesh_nonmanifold_edges']} |")
measured_table='\n'.join(rows)
handoff={'schema':'halo9.j7r17.grand_central_blender.v1','date_jst':'2026-10-25','research_only':True,'branch':'research/m3d1s-j7-r17-grand-central-blender-20261025','base_R16_head':'0eed6bed7072ceb0782341dad9b50daef523286e','base_R16_pr':48,'verified_main_head':'a2f88995eee8d10ee4830dbdf33ccb9c0790de8f','art_decision':'ART_REJECT','art_improvement_goal_reached':False,'formal_central_art_adoptions':0,'minecraft_construction':'HOLD','city_master_complete':False,'official_coordinate_alignment':'UNVERIFIED','directions':[{'id':'A','name_ja':'天隙大陸','result':'REJECT repeated terraced paired modules; fragmented mass'},{'id':'B','name_ja':'反重層天域','result':'REJECT inverted shelves and disconnected worlds'},{'id':'C','name_ja':'裂層多都市核','result':'REJECT initial blank mass; used only as reconstruction source'}],'concentrated_working_source':'exploration_C/R17_C.blend','selected_for_formal_art':None,'main_form_revisions':[json.loads((R/f'revision_{i}/REVISION_RECORD.json').read_text('utf8')) for i in [1,2]],'latest_attempt_blend':'revision_2/R17_REVISION_2.blend','latest_attempt_glb':'revision_2/R17_REVISION_2.glb','latest_attempt_geometry':final,'sections':['sections/SECTION_XZ_Y500/SECTION_XZ_Y500.blend','sections/SECTION_YZ_X0/SECTION_YZ_X0.blend'],'technical_QA':'qa/BLEND_GLB_READBACK.json','basic_saved_geometry_readback_pass':qa['basic_persistence_pass'],'saved_blend_glb_pairs_checked':len(qa['models']),'human_floor_ray':floor,'interior_altitudes_m':[sp['cameras'][n]['xyz_m'][2] for n in ['08_INTERIOR_LOW','09_INTERIOR_MID','10_INTERIOR_HIGH']],'actual_internal_space':'Real subtracted civic chambers, thick grounds, interior borough masses and cross-level galleries exist. No connected enclosed cavity volume or complete city certified. Visual quality still insufficient.','void_volume_m3':None,'void_volume_status':'UNVERIFIED','foreground_computer_use':False,'live_blender_modified':False,'actual_minecraft_saves_accessed':False,'protected_assets_changed':False,'production':'Blender 5.2.1 LTS background bpy, six CPU threads; actual render review and native mesh replacements; no ImageGen enhancement','report':'R17_ART_REVIEW_JA.md','context':'context/R17_NONCANONICAL_10KM.blend','context_W0_H_SB_integration':False,'unverified':['Full walkability','All inter-solid collisions','Connected void volume','Operational vertical transit','Structural/occupancy feasibility','Detailed human-scale city life','Public interiors completion','W0/H1-H6/SB01-SB16/HERO4/V/axes integration','Formal art adoption'],'next_priority':'Replace shell-and-shelf grammar itself with individually authored district terrains and civic sections in the shared km-scale composition. Do not detail or adopt this rejected main form.','github_delivery':'ARTIFACTS_READY_FOR_NEW_BRANCH_PUSH_AND_DRAFT_PR'}
(R/'R17_HANDOFF.json').write_text(json.dumps(handoff,indent=2,ensure_ascii=False),encoding='utf8')
report=f'''# J7-R17 — 壮大な中央巨大建築・実Blender研究

2026-10-25 JST。**研究自己判定：ART REJECT。** 本物のBLEND・GLB・実レンダー、3方向の探索と2回の主形状修正を制作した。しかし「居住都市そのものが数kmの主質量をつくる」美術目標には到達していない。技術保存の成功を美術の合格に置き換えない。正式中央美術採択0件、Minecraft正式施工HOLD、10km詳細マスター未完成。

## 1. 開始確認と作業境界

GitHubを再照会し、R16 / Draft PR #48の最新HEAD `0eed6bed7072ceb0782341dad9b50daef523286e`、main `a2f88995eee8d10ee4830dbdf33ccb9c0790de8f` を確認。main明示refでAGENTS、START_HERE、憲章、3D完成基準、CURRENT_STATUSを取得し、R15審査・引継ぎ、R16憲章・ゲート、latestと決定ログを読んだ。CURRENT_STATUS内の古い日付・HEADを今回の最新値とは扱っていない。

実ローカルはR15の `a8bb4ea…`。SETUP_STATUS.txtの10月14日記録と相違していたため、実物を優先。参照指定された `docs/LOCAL_WORK_SETUP_20261014_JA.md` は現checkoutに存在せず、読了を主張しない。R16を取得し、新規 `research/m3d1s-j7-r17-grand-central-blender-20261025` を分岐。既存の未追跡research/は保存し、納品へ混入させない。

今回のユーザー指示でローカルBlender制作と新規研究ブランチ・Draft PR納品が許可された。main、既存PR、Freeze、過去BLEND、W0、H1〜H6、SB01〜SB16、HERO4、V1〜V3、都市軸、M247-C研究方向は変更しない。実Minecraft保存先を読み書きしていない。全座標は独立研究用m座標、正式アンカー未接合。

## 2. 各案と同縮尺の実画像比較

| 案 | 狙った立体思想 | 実画像からの判定 |
|---|---|---|
| A《天隙大陸》 | 低位の水辺から4km級へ居住地層が斜めに隆起。複数の実公共街路・立体交通を含む | 対の段状地区と同型部材の反復。分離した棚群、巨大門の面影。REJECT |
| B《反重層天域》 | 厚い都市世界を反転・傾斜し、上下の公共世界を交差 | 反転した棚・板の集合で、中心の一つの文明としてまとまらない。下面も床の反復。REJECT |
| C《裂層多都市核》 | 3つの非対称な居住質量を奥行きへずらし、内部の異なる都市谷を囲む | 一体感と厚みはA/Bより読めるが、広い無地外面と小さな内部建築が主従逆転。初期REJECT |

A/Bは同じ1100×1000px、正面8000m・斜視8700mの正投影等、同じカメラ・照明・m単位で7方向を描画。A/Bを無理に選ばず、異なる母形状Cを追加した。Cも合格案として選んだのではなく、連続質量を本質的に再構成する作業台として選択した。R15原本・門メッシュのコピーは使用していない。

![A/Bの7方向実比較](qa/AB_ALL_VIEWS.jpg)

![第三案の全方向](qa/C_INITIAL_VIEWS.jpg)

## 3. 集中制作の理由と主形状修正1

Cは共有空洞の前後に地区を置ける厚みがあり、反復モジュールのA/Bより主質量の置換を検証しやすかった。最初の正面・斜視・背面画像で岩塊状の無地外面を確認後、西と背面の2大質量を完全に削除。4つの異なる位置・高さ・奥行を持つ居住稜へ置換し、各稜を実公共空洞で切削。7つの都市地盤を広げ、背面へ巨大公共室を開いた。最高部を非対称に引き上げた。色・窓の変更ではなく、母体と空洞の実メッシュ変更である。

初期 `exploration_C/R17_C.blend` と修正1 `revision_1/R17_REVISION_1.blend`、GLB、前後の同じ広域カメラを独立保存。画像では背面・内部の奥行きが増えた一方、長い白い上端、細い横断部、閉じた東面が残った。

## 4. 主形状修正2

修正1の実画像を見て、東の閉じた大質量を削除。新しい内陸都市と2本の縦峡谷を造形した。中央には厚い居住半島を新設し、単一の正面穴を低位の公共空間と奥の高位都市空間へ分節。上端の無地の先端を実際に切除し、3540〜4440mの厚い地盤・3大建築・公共谷を持つ高高度都市へ置換。内部横断体を幅320m・厚さ115mの斜交する都市地盤へ再構成した。

`revision_2/R17_REVISION_2.blend` / GLBと `REVISION_RECORD.json` が対応。最上部の左右は全体対称ではなく、局所的な都市谷として異なる高さを持つ。2回とも装飾のみの変更ではない。ただし最終の外形はなお巨大部材と段床の印象が強く、目標達成とは判定しない。

![同カメラでの初期→修正1→修正2](qa/MAIN_FORM_REVISIONS.jpg)

## 5. 最終の全方向審査

| 視点 | 確認できた点 | 未達・不合格理由 |
|---|---|---|
| 正面 | 非対称の上昇、中央半島による空間の分節 | 白い斜部材と段床が外形を支配。都市大陸に見えない |
| 斜視 | 前後の都市高度と厚み、東側の切込み | 大きな部材の間に小建築を置いた印象が残る |
| 側面 | 東西・前後の重なりは存在 | 曲がった帯・板の見え方。地区全体の個性が弱い |
| 背面 | 初期の無地壁を撤去し、多高度の都市室が開く | 同じ床と部材の反復。生活都市としての豊かさが不足 |
| 俯瞰 | 広い地盤、裂け目の方向と高低差 | 地区が空洞と一体の人工地形になる造形は未達 |
| 下面 | 厚い床、内部構造は実在 | 低位都市の底面が広く閉じ、独自の下面文明は未達 |
| 地上見上げ | 立ち上がる高さはある | 高さの数値と巨大部材への畏圧に留まり、荘厳な文明として未完成 |

![最終7方向](qa/FINAL_ALL_DIRECTIONS.jpg)

## 6. 内部都市、実空洞、居住地盤

初期Cで約900〜1590m級の異なる地盤・都市コアを10箇所設計。低位の水庭（地盤295/400m）、中位の段状地形・公共交差室（975/1120/1245/1750/1930/2140m）、高位の公共都市（2770/3015m）、修正2の半島（280/1125/1620m）と最高部3690mの公共地盤が存在する。これらのm値は研究モデル内の地盤高度で、公式座標ではない。

実体は床・厚い地盤・大きな公共街路の差分切削・内部建築・斜めの交通形状である。暗いシェーダーや背景だけを空洞の証拠にしていない。中高度1550mの視点近傍の6方向レイなど、実際の面までの距離は `qa/SPATIAL_INSPECTION.json`。ただし1本ずつの面距離は連続空洞体積や地区の居住可能性を証明しない。

最終内部撮影は低位650m・中位1550m・高位2650m。最初と2回目のカメラは壁や床に遮られ、失敗画像もqaに保存。実メッシュへの視線・位置検査で候補を選び直した。画像には実床、天井、壁、異なる高度の建築が写るが、内部の単調な大面、閉塞、小さく読める都市コアが残る。成功した巨大生活世界とは扱わない。

人間視点は実床 `C_W0_ESTUARY_public_ground` Z={floor['floor_xyz_m'][2]:.6f}m、カメラZ={floor['camera_xyz_m'][2]:.6f}m、床上 **{floor['distance_m']:.9f}m** を下向きレイで確認。これは一点の床・視点確認であり、歩行可能性の全域合格ではない。人間尺度の生活密度、入口、用途、公共交通の実運用は未達。

![内部3高度・地区・人間視点](qa/INTERIOR_AND_HUMAN.jpg)

## 7. 2方向の実断面

最終保存BLENDを別プロセスで開き、XZ（Y=500m）とYZ（X=0m）でBMeshの頂点・面を実切断し、境界にキャップを作成して別BLEND・GLBへ保存。画像のクリップや透過ではない。切断面は黄土色。除去数・切断数・元BLENDのSHA256は `qa/ACTUAL_SECTIONS.json`。

個別メッシュの非多様体辺は次表の通り。0以外の断面は閉じた体積計測モデルとして使えない。0でも別ソリッド間の重なり・支持・歩行・空洞体積は保証しない。空洞体積は **UNVERIFIED / 数値未算出**、上下交通は形状だけで運用未検証。

![実断面2方向](qa/SECTIONS.jpg)

## 8. 寸法・境界・BLEND/GLBの独立検証

スタジオ地面・カメラ・照明を除き、建築コレクションの世界座標頂点を実測。単位m。最終境界は min={final['min_m']}、max={final['max_m']}。

| 保存モデル | X × Y × Z（m） | メッシュ / 三角形 | 形状照合最大差（m） | 個別メッシュ非多様体辺 |
|---|---|---|---|---|
{measured_table}

7組の保存BLEND再読込と、各GLBの空シーンへの再インポートを実施。境界、三角形数、有限頂点、両方向の最近傍頂点位置・三角形重心位置を2cm以内で照合。詳細は `qa/BLEND_GLB_READBACK.json`。これは単なるオブジェクト数一致より強いが、完全な位相同一証明・全ソリッド衝突検査・居住体積認証ではない。

最終GLBだけを空シーンへ読み、原本からはスタジオとカメラ・ワールド照明のみを追加して独立レンダー（`qa/GLB_REIMPORT_OBLIQUE.png`）。元建築を再追加していない。原本画像との画素差は `qa/GLB_NATIVE_IMAGE_COMPARISON.json`。実形状を画像生成AIで補完していない。

## 9. 10km構図と非占有制作

`context/R17_NONCANONICAL_10KM.blend` は約10kmの境界と中立の比較質量だけを置いた実3D。中央は高さ・占有として大きく、周辺の余地はある。ただし**W0・H1〜H6・16施設を実統合した都市ではなく、全都市マスター完成でもない**。見栄えだけで正式位置を登録していない。

![非公式10km縮尺比較](context/12_CITY_10KM.png)

Blender 5.2.1 LTSのMCP接続を読取り確認したが、旧プロトコルだったためライブR13シーンは変更せず、独立バックグラウンドbpyで制作。6 CPUスレッドを指定。前面GUI、マウス、キーボード、Computer Useは使用していない。CPU負荷は発生しているため「無負荷」とは言わない。作業途中の不要な材質が再読込で消えるKeyErrorを修正し、ログを保存。Windowsサムネイル用のユーザーフォルダ書込は環境制限で失敗したが、成果BLEND・PNGの保存とは分離して検証した。

## 10. R11〜R15から脱却できたか・次の課題

**十分には脱却できていない。ART REJECT。** R15の対称メッシュを拡大コピーせず、独立3方向と実画像に基づく2回の母体置換を行った点は事実。しかし最終も「巨大な部材／曲がった板／棚の間に都市コア」という構成が支配し、数百m級都市が数kmの主形状を形成する要求に達していない。Cの初期は岩塊、R1/R2は部材骨格の印象へ問題を移した面がある。大きな寸法、多い画像、技術PASSでART HOLDへ格上げしない。

次工程の最優先はこの形を細密化することではなく、**地区固有の厚い地盤、立体的な公共世界、都市断面、交通到着部が主質量そのものになる別の構成へ置き換えること**。同じロフト・切欠き・段床生成器のパラメータ増加に留めない。300〜1200mの異なる地区を、最初から数kmの同一構図内で設計し、遠景と内部の双方から審査する。今回の不合格外形は正式採択しない。

## 11. 成果物とGitHub納品

ローカル：`C:/Users/ryoma/Projects/CELESTIAL_HALO9/repo/studies/M3D-1S/J7/R17/`。

再現用スクリプト：`atelier.py`、`explore.py`、`sculpt_c.py`、`revise.py`。内部と縮尺比較：`spatial_review.py`、`find_interior_views.py`。独立QA：`verify_and_section.py`。オフライン確認：`python -B -X utf8 studies/M3D-1S/J7/R17/package_evidence.py`。モデル再制作は出力を上書きするため、別コピーで行う。過去研究やarchives/handoff/upstreamで実行しない。

主要モデル：[BLEND](revision_2/R17_REVISION_2.blend) / [GLB](revision_2/R17_REVISION_2.glb)。機械引継ぎ：[R17_HANDOFF.json](R17_HANDOFF.json)。全モデル・画像ハッシュ：[MODEL_IMAGE_MANIFEST.json](qa/MODEL_IMAGE_MANIFEST.json)。新規Draft PR・成果固定コミット・GitHub再取得照合は納品記録追記で示す。既存PR #48およびmainは変更しない。
'''
(R/'R17_ART_REVIEW_JA.md').write_text(report,encoding='utf8')
manifest=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(R.rglob('*')) if p.is_file() and p.suffix in ['.blend','.glb','.png','.jpg']]
(Q/'MODEL_IMAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
(Q/'OFFLINE_EVIDENCE_QA.json').write_text(json.dumps({'all_source_ast_parse':True,'all_png_decode':True,'saved_model_pairs':len(qa['models']),'saved_geometry_basic_QA_pass':qa['basic_persistence_pass'],'human_floor_1_7m':floor['pass_1_7m_2mm'],'model_image_files':len(manifest),'actual_blender_pngs':len(list(R.rglob('*.png'))),'pixel_processing':'Contact sheets resize/place/label only; no generated or painted architectural imagery.','art':'ART_REJECT','construction':'HOLD','full_city_master_complete':False},indent=2),encoding='utf8')
latest={'schema':'halo9.research.latest.v1','research_id':'M3D-1S/J7-R17','date_jst':'2026-10-25','status':'REAL_BLENDER_3_DIRECTIONS_2_MAIN_FORM_REVISIONS_SAVED__ART_REJECT','research_branch':handoff['branch'],'approval':'RESEARCH_ONLY','canonical_adoption':'NONE','construction':'HOLD','formal_central_art_adopted':0,'city_master_complete':False,'official_alignment':'UNVERIFIED','work_status':'LOCAL_BACKGROUND_BLENDER_NO_FOREGROUND_GUI','outputs':{'report':'studies/M3D-1S/J7/R17/R17_ART_REVIEW_JA.md','handoff':'studies/M3D-1S/J7/R17/R17_HANDOFF.json','latest_attempt_blend':'studies/M3D-1S/J7/R17/revision_2/R17_REVISION_2.blend','latest_attempt_glb':'studies/M3D-1S/J7/R17/revision_2/R17_REVISION_2.glb','macro_views':'studies/M3D-1S/J7/R17/qa/FINAL_ALL_DIRECTIONS.jpg','main_form_revisions':'studies/M3D-1S/J7/R17/qa/MAIN_FORM_REVISIONS.jpg','QA':'studies/M3D-1S/J7/R17/qa/BLEND_GLB_READBACK.json'},'previous_pointer':{'commit':'0eed6bed7072ceb0782341dad9b50daef523286e','path':'studies/M3D-1S/latest.json','research_id':'M3D-1S/J7-R16'},'next_priority':handoff['next_priority']}
(R.parents[1]/'latest.json').write_text(json.dumps(latest,indent=2,ensure_ascii=False),encoding='utf8')
print('OFFLINE QA PASS; ART REJECT;',len(manifest),'model/image files;',len(qa['models']),'native/GLB readback pairs')
