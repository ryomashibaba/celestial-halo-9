# CELESTIAL HALO-9 — INT5 真正造形・画像審査・構造欠陥の確定記録（2026-11-06 JST）

**INT5最終判定：SOURCE PASS / BLENDER EXECUTION PASS / INDEPENDENT FILE REOPEN PASS / GEOMETRY INVALID / IMAGE VALID / ART REJECT / FUNCTION UNKNOWN / FORMAL_ART_ADOPTION 0 / 30対象完成0/30 / Minecraft CONSTRUCTION HOLD。**

これはINT5の実結果と停止理由を保存する文書であり、新憲章・正式ART採択・完成宣言ではない。INT4-R1を更新する「正式ベースライン」にしない。

## 原本・実際に行った制作と証拠

- 起点: 保存済みINT4-R1真正BLEND（SHA256 `7cf765923b91f06cce7951fc3558f042e488bf9f1157791b59b14d11954dc2bb`）。原本から完全に独立したGitHub Actionsの研究コピーを編集。
- [実制作・独立再読込GitHub Actions #42146504532](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42146504532) SUCCESS。Blender 5.2.1。公的配布元SHAを照合。
- 編集内容: INT4の不採用薄型テラスと街路22要素を研究コピーから除去。NAVEの公共図書館・駅・式典室、H1の市場・学校・居住街路、W0水際と元カメラを残して、左右の連続巨大居住塊、公開内部、上部斜裂交通を制作。新メッシュはM247 9・CITY 52（点数はART品質の根拠ではない）。
- 保存先: `INT5/evidence/HALO9_INT5_INHABITED_RUPTURE_SCULPT.blend.gz`。展開した編集可能BLEND SHA256 `be64b47413d43159f82be570abf4be9d4ddff722fcdd595736d775d3c7c9a77f`。画像は `INT5/evidence/INT5_TRUE_THREE_FIXED_CAMERAS_UNREVIEWED.jpg`（同一シーン・元E11カメラ3視点、実Cycles PNGから作成）。実現物と画像SHAは `INT5/evidence/INT5_TECH_NOT_ART.json`。
- 元カメラ位置変更なし・研究メートルで正式Minecraft座標未認証・施工書込なし。Blender GUI手彫り、Work、Computer Useは実行していない。

## 本物の画像を直接見た厳格なART審査

| E11固定視点 | 観察 | 判定 |
|---|---|---|
| NAVE HUMAN | 旧INT4-R1の見えていた公共室の側に巨大な新石塊が割り込み、大きな橋と白い矩形空間が依然主役。駅／図書館／儀礼の巨大公共内部を豊かな単一建築として感じられない。 | ART REJECT |
| H1 HUMAN | 床と頭上の大塊／壁の間に狭い通路があり、H1の厚い住区・店・学校の可視性や立体都市生活が改善していない。 | ART REJECT |
| URBAN AERIAL | 左右の大きな白灰色巨塊／巨大斜材を海岸に突き立てたように見え、高所の生活都市とW0の共生が映像上成立しない。以前のINT2/INT3の巨体問題へ再発。 | ART REJECT（重大） |

平均明度は NAVE 142.42 / H1 93.53 / 俯瞰 103.07。「暗転していない」ことと「都市級公共・住居美術に合格する」ことは別。

## 実物の構造完全性：CI SUCCESSでもMODEL INVALID

INT5_TECH_NOT_ART.json 内の実Boolean対象メッシュ面数（before, after）で、
`BETA_HIGH_PUBLIC_VOID = [20, 0]` を確認。**斜裂の高所居住主質量の対象オブジェクトが切削後0面になった。**
CIはBLEND再読込・カメラ・PNG・ハッシュ・保存を検証したが、**主質量の非空メッシュ／体積／用途の確保を検証していなかった。** よって「真正ファイルの存在と技術的再現」はPASSでも、3D造形としての構造完全性はFAIL。これをTECH全面合格やβ造形成功と呼ばない。

モデル無効のINT5を設計原本・正式採用・次の制作起点にしない。INT5のBLENDは不合格研究証拠のみ。凍結原本・main・過去E/LCS/INT研究・WorldEdit/セーブへの更新は行わない。

## 批判的方針判断

INT2（筒状双塊）→INT3（巨壁）→INT4（薄い棚／普通の箱）→INT4-R1（視点修復）→INT5（巨大斜材・巨塊再発）は、**背景Pythonで簡易質量を自動生成するだけでは、人間尺度の公共内部と数km級の非凡な居住都市を同時に美術成立させられていない**という実証的な失敗列である。

ART-FIRST、Macro Impact First、CITY MASTER 3D FIRST、M247-C《浮断天核》＝α双殻浮断＋β斜裂天脊、30対象の完成義務は変更しない。背景PythonをGUIの直接手彫りと称さない。INT5をさらに同型Booleanで修復・巨大化するためにCI枠やユーザー操作を浪費しない。

次の本質的制作工程は、**実Blenderを視覚的に反復操作する安全な編集環境で、主建築の彫塑的な外形と内部空間を同時に判断して改造**すること。現在のChat/GitHub Actionsは真正ファイルの生成と画像審査ができるが、実時間のBlender GUIを操作する権限は持たない。Work/Computer UseやユーザーPC接続はユーザーの事前明示承認が必要。承認がないまま起動しない。許可されるまで本ART候補はHOLD。新たな有料API/外注は使っていない。GitHub Actionsの請求額・無料枠残量はユーザーの請求画面を監査していないので0円確約はしない。

固定状態：**正式ART採用0、30対象完成0/30、Minecraft施工HOLD。**
