# R4-E11 — MCPによる居住断面・公共空洞の隔離真正3D研究

2026-11-05 JST。ART-FIRST / CITY MASTER 3D FIRSTを継承する研究成果。
**正式ART採択0件・30対象完成0/30・Minecraft施工HOLD。正式採用案ではない。**

## 開く実物

- `E11_INHABITED_SECTION_WORKING.blend`：最終編集可能ソース。Blender 5.2.1 LTS。
- シーン `E11_INHABITED_SECTION_RESEARCH`、カメラ `E11_NAVE_HUMAN` / `E11_H1_HUMAN` / `E11_URBAN_AERIAL`。
- `R2/*.png`：同一BLENDの真正Cycles CPUレンダー。1200×900。
- `E11_FIXED_CAMERA_R0_R1_R2_ART_REJECT.jpg`：同一カメラによる3段階比較。ラベル・縮小以外の画像内容の合成・補筆なし。
- `E10_E11_CONTEXT_NOT_SAME_CAMERA.jpg`：E10凍結像との参考比較。**E10とE11のカメラは異なる**。
- `E11_R0_BEFORE_REVIEW.blend` / `E11_R1_AFTER_FIRST_REVIEW.blend`：今回の修正前後の実ソース。
- `INDEPENDENT_TECH_REOPEN.json`：別Blenderプロセスによる再読込検査。美術合格証ではない。
- `SHA256SUMS.txt`：成果のSHA256。自身はハッシュ対象外。
- `E11_ART_JURY_AND_HANDOFF_JA.md`：最終審査・次回への正本。

## 今回の実制作と方法上の限界

元E10の不合格メッシュは移植せず、今回専用の研究メートル座標で中央・NAVE・H1・W0を制作した。
初回の実レンダーを見て、同じBLENDの既存メッシュを切断・欠き込み・高高度転位し、公共室の分岐柱、階段、公開回廊、水際、H1貫通公共ホールを追加。人間2視点と俯瞰のカメラ行列を維持して比較した。

ユーザーの追加指示に従い、9876のライブBlender MCPで編集し、最初の起動試行以後は前面のマウス・キーボード操作を行っていない。レンダー・再読込は画面を出さない別プロセス、CPU2スレッド、BelowNormal優先度で実行。

**GUIの手彫り・ブラシ彫塑を実施したとは主張しない。** 主形状の制御輪郭と直接メッシュ修正にもPythonを用いた。反復床・外壁帯が美術を支配する問題が残り、ツール接続と実メッシュ編集の成功を新制作方法の美術的成功と扱わない。生成AI画像、外部3D生成、有料API、外部アセット、追加インストールは使用していない。

## 起点・安全境界

- main確認HEAD：`a2f88995eee8d10ee4830dbdf33ccb9c0790de8f`。
- E10確認HEAD・本枝の親：`94073f97cd65e346e5a3a9846f8dd48a73c6e8e4`。
- 研究枝：`research/r33-s27-d48-r4-e11-mcp-inhabited-section-20261105`。
- mainの7正式文書、E5統合正本、E6/E8/E9-R1審査、E10引き継ぎ正本を確認。mainのCURRENT_STATUSには古い2026-10-23時点の運用記述が残るため、最新HEADの実取得と区別した。
- 正式M247-C方向、W0、H1〜H6、SB01〜SB16、HERO4、V1〜V3、3軸の義務を変更しない。E11で未制作の対象を完成と数えない。
- Minecraftセーブは参照も書込もしていない。Freeze・原本・既存研究成果・main・既存PRを変更しない。研究メートルは正式ワールドに未登録。
- 起動時の未保存Blenderセッションはローカルの `SESSION_BEFORE_E11.blend` にコピー保存し、GitHub送信対象外とした。

## 再現・再開

まず最終BLENDを開く。初期作者スクリプトを再実行して実物を上書きすることを再開手順にしない。
編集履歴は `01_author_section.py` → `02_recompose_same_mesh.py` → `03_open_h1_public_atrium.py`。
今回のR2初回では補助関数 `tree` のスコープ不足で停止し、既に編集済みのシーンを維持して未実行末尾だけを再開した。スクリプトは補助関数の明示読込に修正済み。全体を再実行して二重変形させていない。

レンダーは `render_views.py`、再読込検査は `verify_independent.py`。後者はR0を最初に開いた**別プロセス**で実行し、最終BLENDを読み直す。実行結果は専用JSONと完了マーカーで確認し、プロセス終了コードだけを根拠にしない。
画像比較は `build_review_sheets.py`。Pythonのオフライン確認・比較生成では `-B -X utf8` を使用。
ログ公開版からローカル絶対パスを除いた。現行BLENDには自動実行Python Textは埋め込んでいない。
