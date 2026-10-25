"""Record the immutable artifact commit and the newly created Draft PR only."""
import json,sys
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
remote=json.loads((R/'qa/GITHUB_READBACK.json').read_text('utf8'));assert remote['all_match']
qa=json.loads((R/'qa/BLEND_GLB_READBACK.json').read_text('utf8'))
h=json.loads((R/'R15_HANDOFF.json').read_text('utf8'))
h.update(github_delivery='PUSHED_NEW_DRAFT_PR_CREATED_ALL_MODEL_IMAGE_BYTES_REDOWNLOADED_MATCH',draft_pr=47,draft_pr_url='https://github.com/ryomashibaba/celestial-halo-9/pull/47',artifact_commit=remote['commit'],remote_checked_files=remote['checked_files'],remote_checked_bytes=remote['checked_bytes'],remote_all_hashes_match=True,remote_readback='qa/GITHUB_READBACK.json',section_topology={k:v['native']['separate_solid_nonmanifold_edges'] for k,v in qa['models'].items() if k.startswith('SECTION')},section_limitation='XZ section has 88 nonmanifold edges; use as an actual cut visualization, not a closed volume model.',final_branch_head='Current new PR head; artifact bytes pinned separately by artifact_commit. This metadata commit is later.')
(R/'R15_HANDOFF.json').write_text(json.dumps(h,indent=2),encoding='utf8')
p=R/'R15_ART_REVIEW_JA.md';txt=p.read_text('utf8').split('\n## GitHub納品記録')[0]
sha=remote['commit'];prefix='https://github.com/ryomashibaba/celestial-halo-9/blob/'+sha+'/studies/M3D-1S/J7/R15/'
txt+=f'''\n## GitHub納品記録

新規[Draft PR #47](https://github.com/ryomashibaba/celestial-halo-9/pull/47)。baseはR14、既存PR #44／#45／#46は編集していない。成果固定コミットは `{sha}`。納品メタデータはその後のコミットで追加するため、最終ブランチHEADはPRのheadを参照する。

固定成果：[BLEND]({prefix}revision_2/R15_FINAL.blend) ／ [GLB]({prefix}revision_2/R15_FINAL.glb) ／ [広域比較]({prefix}qa/R15_MACRO_VIEWS.jpg) ／ [主形状修正比較]({prefix}qa/R15_MAIN_FORM_REVISIONS.jpg) ／ [人間視点と実断面]({prefix}qa/R15_SPATIAL_EVIDENCE.jpg)。

GitHubの固定コミットから独立HTTPSで **{remote['checked_files']}ファイル・{remote['checked_bytes']:,} bytes** を再取得し、サイズとSHA256がすべて一致。記録は `qa/GITHUB_READBACK.json`。これは保存と受渡しの確認であり、美術の不合格を変更しない。
'''
p.write_text(txt,encoding='utf8')
print('Recorded Draft PR 47 and immutable artifacts',sha)
