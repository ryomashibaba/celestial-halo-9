# R33-D43 — 真正Blender実制作・視覚ゲート結果

**基準日**: 2026-10-29 JST  
**直前D42 HEAD**: `a1b740a7c42e834d051eec8d735f68e34767e008`  
**main確認HEAD**: `a2f88995eee8d10ee4830dbdf33ccb9c0790de8f`。mainとD37〜D42の研究原本は変更せず、隔離ブランチ `research/r33-s27-d43-native-city-form-20261029` で実行。  
**正式美術採択0件 / CITY MASTER 3D FIRST / Minecraft施工HOLD**。

## 実行したこと（証拠がある範囲）

1. `D43_NATIVE/d43_base.py` により真正 `bpy==4.5.15` で中央数km級の研究用メッシュ、実公共床、居住コート、縦交通の試作、W0研究用10km敷地、H1〜H6・SB01〜SB16の仮位置を**同一の編集可能なBLEND**へ作成。既存のD40/D41/D42のメッシュ形状を転用していない。
2. native BLEND `D43_BASE_EDITABLE.blend` を保存し、GLB `D43_BASE.glb` を書き出し、真正Blender Workbenchで固定カメラ8枚を描画した。画像をChat側でダウンロードして**実際に目視**。
3. `D43_NATIVE/d43_reopen.py` を別のPython/bpyプロセスで起動し、**独立にBLEND再読込＋GLB再インポート**。全238メッシュについて同一識別名を要求し、ワールド変換済みの頂点点群で双方向の最近傍誤差を照合。名前の無条件無視は行っていない。
4. glTF出力は平面の三角形化と法線の分割で頂点数・ポリゴン数が増加するため、それらの**個数同一条件は不適切**。初回実行では描画環境のEGL不足で失敗、次回はGLBの頂点分割で検証が誤ってFAIL、3回目に識別名と頂点点群を確かめた真正CI SUCCESSに到達。各失敗はGitHub Actionsの実ログに記録した。

## 実際のActionsと成果

- FAIL（libEGL.so.1欠落）: https://github.com/ryomashibaba/celestial-halo-9/actions/runs/40865137592
- FAIL（gltf頂点分割を形状不一致と誤判定）: https://github.com/ryomashibaba/celestial-halo-9/actions/runs/40865253208
- **SUCCESS（D43技術限定）**: https://github.com/ryomashibaba/celestial-halo-9/actions/runs/40865597562 （実行コードコミット `b309800b1eceef9c5676e939424123e5bbd0e5e3`）
- 確認済みArtifact ID: `12893053840`、https://github.com/ryomashibaba/celestial-halo-9/actions/runs/40865597562/artifacts/12893053840
- ZIP SHA256: `09ea5397ab9c3e17564d52e7c578c26c0bf38c54b73071264c3b6eaf6ddaf76c` （会話内ダウンロードで実ファイルと照合）。
- 保存済み編集可能BLEND SHA256: `429222e8d613dd72c00815b8f78f0f19f5b29603b8020f03203b9e98d3c65f96`。
- GLB SHA256: `adc5fce0cec214bb56d755e8fff2a8e213943a4750af19125a7f3b2007560d2a`。
- Artifactには上記BLEND/GLB、8枚PNG、シーンmanifest、独立幾何監査JSONを含む。**保持期間は7日**。GitHubリポジトリ自体にバイナリを保存したと主張してはいけない。
- 技術実測: native Blender 4.5.15 LTS、編集可能シーン246オブジェクト／うちメッシュ238、保存再読込・GLB再インポート、同名メッシュ238/238、点群最大誤差0.0m、W0研究地面と海の点群誤差0.0m、Blender実レンダー8/8。
- **未証明**: GLB面接続の完全一致、全メッシュの水密・干渉・支持・入口・公共経路、公式W0/H/SB座標、都市完成度、実Blender GUIでAIがインタラクティブに直接彫刻したこと。

## 実画像に基づく美術審査

**ART REJECT / G0 STOP**：巨柱・屈曲する板状量塊に主役性を支配され、床と居住区が細い棚・後付け小施設にしか読めない。中央公共空洞の空間秩序・巨大内部都市の密度・圧倒的超未来性・左右非対称性の美術的統合が成立しない。

- 都市鳥瞰：周辺地区が浮遊床と仮マーカーにしか見えず、10km都市の統合景観は成立していない。
- 正面・斜視：巨大な屈曲柱が主で、「生活文明が外形を形成する」関係は読めない。正面上部も画面で一部切れている。
- 側面・背面：中央が2–3本の厚い巨大棒状で、連続した居住街区の外観には見えない。
- 地上視点：前景地盤の遮蔽が大きく、人間スケール／建築の上昇感を適切に評価できない。
- 公共空洞・高高度居住：本物の階・床の存在は認めるが、「積層された棚」に後退し、通路や出入口の物理成立は未証明。

**この不合格マクロをディテール追加や2回の表面的パラメータ編集で延命しない。** D43の当初目標だった2回の視覚駆動直接BLEND編集は未実行。そのため「AIが実BLENDを見ながら造形を改善できた」とは宣言しない。

## D44への重要な方式変更

D40〜D43を比較して技術的にはVTK生成から真正Blender原本・レンダーへ進んだが、美術はいまだ不成立。**簡易Python/Loftにより巨大形を作る限り、変形しても巨大棒・板・棚へ収束する**ことが画像から判明した。

D44ではまず完全に新しい美術レイアウトを考え、巨大質量と街区の**相互制約**を具体化する。画像を増やすだけ、同じメッシュへの表面装飾、テスト合格数増加では不可。原本をBlenderで視覚的に見て編集できるAI GUIワークフローが最有力となるが、**Workには都度事前に範囲・理由を説明しユーザーの明示承認が必要**。承認なしのWork移行はしない。Blenderを使う場合、同一8視点の画角不良もBASEから再固定する。

**D43最終状態**: TECH LIMITED PASS (native 3D, object names+vertex positions), ART REJECT/G0 STOP, DIRECT GUI SCULPT NOT VERIFIED, FORMAL CENTRAL ART ADOPTION 0, CITY MASTER 3D INCOMPLETE, MINECRAFT HOLD.
