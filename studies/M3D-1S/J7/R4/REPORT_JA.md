# HALO-9 / M3D-1S J7-R4 — Blender本体の実3D直接編集を実証

2026-10-24 JST / Research-only / 正式中央美術採択0 / Minecraft施工HOLD

## 結論
**Blender本体で実GLBを読み込み、既存実メッシュをbmeshで直接編集し、編集前後をWorkBenchレンダー、.blendと.glbに保存・再インポートして確認する手順が実際に成功。** バージョンBlender 4.0.2、GitHub Actionsの隔離されたubuntu-24.04 runnerでxvfb-run headless実行。研究用GLBだけを利用、原本R3・main・Minecraft実ワールドへ書込なし。

**ただし美術の成功ではない。** 床と屋根の拡幅/上部変形の限定試験で、R3中央の「船や帆のような主形状」は依然としてREJECT。Blender GUIを人間やAIがリアルタイムに操作できたことを示すものではない。

## 技術監査（GitHub保存済みの実出力より）
- R3 GLB入力: 164 mesh objects
- 既存NAVE_MAIN_PROCESSIONAL_FLOOR 40頂点、既存NAVE_VAULT_SUSPENDED_NORTH_FOLD 30頂点をBlender bmesh内で直接変更
- **GLB座標規約の問題を発見し修正**：旧Trimesh製R3 GLBをBlenderへ単純インポートすると旧Z-up高さがY軸へ写る。研究座標へ復元するため輸入オブジェクトの親座標をX軸-90度回転。実頂点Z-upを検証後に編集した。正式Minecraft座標が確定したという意味ではない。
- 床の編集前bounds: X[-1180,1170], Y[-1120,-365], Z[1215,1750]m
- 編集後bounds: X[-1180,1170], Y[-1263.45,-221.55], Z[1215,1792]m
- 編集GLB再インポート床bounds: X[-1180,1170], Y[-1263.449,-221.549], Z[1215,1792]m
- 編集後実GLB: 491,552 bytes; 編集可能BLEND: 168,484 bytes; reimport mesh 164
- 同じBlender Workbenchレンダー: 3カメラ x 編集前後 = 6枚
- 編集前後の画像画素差（960×700、各RGB成分の最大絶対差 >8 の画素割合）:
  * 都市正面：0.48631%
  * 都市側面：0.08467%
  * NAVE局所：4.65744%
- 実画素差は一部編集が視認できる証拠であり、建築美術が向上した数値ではない。

## CI上の2つの失敗と修正（隠さず記録）
1. 1回目: Ubuntu Blender 4.0.2でglTFインポータ依存numpyが欠落し失敗。python3-numpyを導入して修正。
2. 3回目: 既存出力がcheckoutに存在するためテストが中断されたが、Blender既定終了コード0をCIが誤判定。**ワークフローに--python-exit-code 23を追加、生成R4出力のみを実行前クリア**。この修正を加えた[実行#40078233663](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/40078233663)で全ステップPASS、GitHubへBLEND/GLB/PNG/証跡JSON自動保存・読戻し検証済み。

## 完了したもの・未完了
**完了:** Blender実インポート、座標正規化、bmeshによる既存ジオメトリ直接編集、6枚のBlender Workbenchレンダー、.blend保存、編集後GLB保存、再インポート、実頂点bbox比較、GitHubブランチ内バイナリ保存、出力JSONと履歴。

**未完了:** Blender GUI/ビューポートをAIが見ながらインタラクティブに作り直す制作ループ、美術的に圧倒的な中央主形状、実歩行・床支持・街区生活・公共室の利用証明、W0/H/SBの正式な座標統合、完成City Master。正式美術採択0件／施工HOLD。

## 次のJ7-R5：本当の美術制作ゲート
Blender技術経路は確立したので、単なる既存床/屋根の微修正ではなく、(1)居住街路と公共室の断面関係、(2)中央本体の巨大な都市質量と空洞、(3)遠景と側面が別の単純形態にならないこと、を主題とした実モデリングを行う。Blender GUI視覚フィードバックができない限り「ビジュアル直接造形を実証した」と主張しない。頭脳も幾何も未採択のR3形状をそのまま詳細化しない。

## 主要なGitHub成果
- `outputs/J7R4_REAL_BLENDER_EDIT.blend` — 実際にBlenderで保存した編集可能なシーン
- `outputs/J7R4_REAL_BLENDER_EDIT.glb` — Blender書き出し＆再インポート済みモデル
- `outputs/J7R4_BLENDER_ACTUAL_EXECUTION.json` — 実行時証拠
- `outputs/BEFORE_*.png` と `outputs/AFTER_*.png` — 3方向比較
- `blender_native_edit_probe.py` — 検証された編集スクリプト
- `.github/workflows/halo9-j7-r4-blender.yml` — Python例外でCIが失敗する防護付きワークフロー

**依存PR: #35/J7-R3。新ブランチは既存原本・mainへ変更を加えない。**
