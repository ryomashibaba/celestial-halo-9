"""Close out only after actual immutable-commit GitHub byte verification succeeds."""
import json,sys
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
read=json.loads((R/'qa/GITHUB_READBACK.json').read_text(encoding='utf8'))
assert read['all_match'] and read['checked_files']==99
pr='https://github.com/ryomashibaba/celestial-halo-9/pull/51'
data={'research_branch':'research/m3d1s-j7-r19-living-horizon-blender-20261025','draft_pr':51,'draft_pr_url':pr,
 'base_pr':50,'base_branch':'research/m3d1s-j7-r18-civilization-landscape-art-20261025',
 'artifact_commit':read['artifact_commit'],'remote_files_checked':read['checked_files'],'remote_bytes_checked':read['checked_bytes'],'remote_all_bytes_match':True,
 'verification':'Independent authenticated GitHub HTTPS raw file reads; exact committed bytes, sizes and SHA256.',
 'readback_scope':'ALL R19 files plus studies/M3D-1S/latest.json at the fixed artifact commit. Subsequent delivery metadata and transport-repaired readback source are a follow-up commit, not recursively included in this snapshot.',
 'branch_head':'Resolve current HEAD from Draft PR #51. artifact_commit pins the raw art/QA snapshot.',
 'initial_transport_failure':'gh api binary responses returned transform: short source buffer. Replaced transport with urllib identity-encoding GitHub raw HTTPS; all 99 files then matched.',
 'push_authorization':'Current user delegated request attachment section 9 explicitly says to save a new independent GitHub research branch and create a Draft PR. First automatic review rejected for missing visible authorization; exact section was read back and scope-checked, then re-review accepted. No workaround bypass.',
 'art_decision':'ART_REJECT','art_goal_reached':False,'formal_central_art_adoptions':0,'minecraft_construction':'HOLD','city_master_complete':False,
 'protected_data_changed':False,'previous_PR_changed':False,'main_written':False,'merge_performed':False,
 'foreground_computer_use':False,'actual_minecraft_saves_accessed':False}
(R/'qa/GITHUB_DELIVERY.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
path=R/'R19_HANDOFF.json';handoff=json.loads(path.read_text(encoding='utf8'))
handoff.update(github_delivery='PUSHED_NEW_DRAFT_PR_FULL_ARTIFACT_COMMIT_HTTPS_READBACK_MATCH',draft_pr_url=pr,draft_pr=51,artifact_commit=read['artifact_commit'],remote_checked_files=99,remote_checked_bytes=read['checked_bytes'],remote_all_hashes_match=True,branch_head='Resolve from Draft PR head; art bytes pinned at artifact_commit')
path.write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
path=R.parents[1]/'latest.json';latest=json.loads(path.read_text(encoding='utf8'));latest.update(draft_pr_url=pr,artifact_commit=read['artifact_commit'],github_readback_all_files_match=True)
path.write_text(json.dumps(latest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
path=R/'R19_ART_REVIEW_JA.md';text=path.read_text(encoding='utf8')
marker='## GitHub納品確認'
if marker in text:text=text.split(marker)[0]
text+='\n'+marker+'\n\n'
text+='新規[Draft PR #51]('+pr+')。baseはR18。既存PR #50・main・既存原本は変更なし。固定成果コミット `'+read['artifact_commit']+'` から、R19全ファイルとlatest.jsonの **99ファイル・106,416,894 bytes** をGitHub HTTPSで独立再取得し、全サイズ・SHA256・実バイト列が一致。`qa/GITHUB_READBACK.json` が個別証跡、`qa/GITHUB_DELIVERY.json` が納品識別である。\n\n'
text+='最初のGitHub CLI取得は圧縮通信エラー（transform: short source buffer）で失敗し、HTTPSの生ファイル読取りへ修理して全件照合した。納品メタデータと読取りソースの修理は後続コミットとして追加する。固定成果コミットの完全照合を、後から追加されたメタデータ自身の再帰照合と混同しない。最新HEADはPRのheadを参照。**保存と同一性確認の成功はART REJECTを変えない。**\n'
path.write_text(text,encoding='utf8')
print(json.dumps({k:v for k,v in data.items() if k in ['draft_pr_url','artifact_commit','remote_files_checked','remote_bytes_checked','remote_all_bytes_match','art_decision']},ensure_ascii=False,indent=2))
