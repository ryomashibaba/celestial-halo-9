# CELESTIAL HALO-9 / INT16 — 直接3D造形実施、実画像批判審査・早期停止（2026-11-06 JST）

## 総合判定

**SOURCE PASS / TRUE BLENDER MESH EDIT PASS / INDEPENDENT REOPEN PASS / IMAGE VALID（固定E11 3枚＋補助1枚） / ART REJECT / FUNCTION UNKNOWN / FORMAL ART ADOPTION 0 / CITY MASTER COMPLETION 0/30 / MINECRAFT HOLD / COST_AUDIT UNKNOWN.**

新規企画でも方針変更でもない。正式な `main`、Freeze、原本、W0地形、以前の研究HEAD、ワールドを無断書換えせず、INT15研究HEAD `0dd41bb19738acbc321e5d71989c7aa9965b81b9` から隔離した `research/r33-s27-int16-macro-scarp-direct-shape-20261106` で実行した。これはM247-C《浮断天核》α双殻浮断＋β斜裂天脊の美術方向や全30対象の完成義務を縮小しない。

## 本当に作ったもの（作ったと誇張してはいけないもの）

- ソースはINT15の保存済み真正BLEND（展開SHA256 `e996fab613904dc557638612d4380ba67ef5c6bbd4aa9fb219d9aeaa8f511fb9`）で、書込は新しい研究COPYのみ。
- 旧INT11のM247-C西東**既存実メッシュ**をその場で直接座標編集。西3,526頂点（最大245.43m）、東3,013頂点（最大259.85m）。新しい「卵オブジェクト」を増やしてはいない。
- 手作業で個別輪郭を指定した西のPUBLIC_LIBRARY_CANYON、EAST_H1_EXPOSED_CIVIC_TERRACE、西上部SKY_READING_COURT、東上部HIGH_CITY_BROKEN_CROWNの**計4か所を真正Booleanで掘削**し、全てトポロジー変化を確認した。
- 固定E11 3カメラ行列とW0主要4地形の頂点指紋は保存、研究上の既存中央主構造も残した。CUTAWAY用に他の母体をレンダー時だけ隠した画像ではない。
- Blender 5.2.1でレンダー4視点・BLENDを保存し、別Blenderプロセスで独立再読込成功。検証：[Actions #42226019249](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42226019249) **completed/success**。
- 展開後の真正BLEND SHA256: `f98bce5184bf772df427a7d003ba44f3905ac227038bf86da5babc0a1f4a8605`。
- 作業手法は**Blender背景実行によるスクリプト頂点編集とBoolean**であり、GUI手彫り・AIによるインタラクティブSculptの実証ではない。

## 同じ真正3Dからの4視点直接審査

[実レンダー4視点](evidence/INT16_FOUR_REAL_SCENE_VIEWS_ART_UNREVIEWED.jpg)を画像として実際に開き、INT15の真正5視点とも照合した。

1. **E11_NAVE_HUMAN：ART REJECT。** 依然として近景の薄板と白灰色の塊が視界を占める。駅・図書館・大礼拝的公開大室の空間構成は人間視点で読めず、広大な街路や使える施設の奥行きが見えない。
2. **E11_H1_HUMAN：ART REJECT。** 暗い巨体と茶色の全面前景は依然強く、学校・市場・厚い住宅街区・垂直交通が人間尺度の都市として読めない。
3. **E11_URBAN_AERIAL：ART REJECT。** 旧二つの巨大卵形の一部が鋭い切断面と洞窟になったが、かえって**巨大な穴のあいた卵殻/貝殻**という読みに近い。中央級の斜裂・異高度の居住街区とW0を統合した文明の都市構造は実証されない。
4. **INT16_ARCHITECTURAL_FRONT_EXTRA：ART REJECT。** 正面からもほぼ同じ丸殻輪郭が支配し、内側の都市は造形の背後に隠れている。補助視点が良好でも元E11を置換しない原則を守る。

今回の頂点移動数・切削成功・レンダー成功は**TECH**の進歩だが、形状の根本思想に起因するART不合格を打ち消さない。「直接頂点を編集したから良い美術になった」という誤認を明確に棄却する。

## 次の行動と厳格な停止

**今回のINT16自体はART REJECTで凍結する。** 同じ巨大卵殻を切り進めるINT16-R1や、数式で別の巨体・高層ビル・板・穴を量産するINT17を開始しない。3Dコードの実行可否と芸術的な真の造形判断の可否は別である。

次の本質工程は、利用可能な視覚的インタラクティブBlender/MCP操作の実確認を行い、NAVE・H1・M247-C斜裂・W0水際を**同じ真正3Dで観察しながら**、形状主導の代表断面を大きく著作し直すこと。現行Chat/GitHubだけでそれが成立しなければ、**制作能力HOLD**を維持する。Work/Computer Use、ユーザーのローカル環境、有料サービスは必ず事前に明示承認を得る。

### 実体の参照

- [INT16真正BLEND](evidence/HALO9_INT16_MACRO_CIVIC_SCARPS.blend.gz)
- [INT16 4視点実画像](evidence/INT16_FOUR_REAL_SCENE_VIEWS_ART_UNREVIEWED.jpg)
- [INT16検証記録](evidence/INT16_INDEPENDENT_TECH_NOT_ART.json)

**正式ART採用 0、完成0/30、Minecraft施工HOLD。この記録は正式な採用判断・憲章改訂ではない。**
