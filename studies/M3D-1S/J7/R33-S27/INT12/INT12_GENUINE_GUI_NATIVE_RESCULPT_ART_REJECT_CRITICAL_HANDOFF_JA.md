# CELESTIAL HALO-9 — INT12 固定E11実画面誘導・真正メッシュ彫塑／画像直接批判審査（2026年11月6日 JST）

**最終：SOURCE PASS / REAL GUI + NATIVE MESH EDIT PASS / 独立BLEND再読込 PASS / 真正レンダー6枚 PASS / 保存復旧 PASS / 総合ART REJECT / FUNCTION UNKNOWN / 正式ART採択0件 / 完成0/30 / Minecraft施工HOLD。**

本記録は固定方針ART-FIRST／Macro Impact First／CITY MASTER 3D FIRST、中央M247-C《浮断天核》の巨大双殻浮断・斜裂天脊、W0・NAVE・H1、10km級30対象詳細3D完成義務をいっさい変更しない。main、Freeze、保存原本・過去研究・Minecraftワールドは変更なし。

## 1. 真正成果の実測

- 親研究：不合格だったINT11の真正Blender 5.2.1 BLEND（展開SHA256 `2ec37b65868509060a499e9c648c3030aa3d008a7a9f603a2598dc4358b2140e`）のみ、別の隔離ブランチ `research/r33-s27-d48-int12-screen-directed-sculpt-20261106` の研究コピーで開いた。既存の本物のM247-C西・東メッシュを**新しい箱・巨殻・板・巨大楕円体を生成せず直接編集**。
- GUI表示した元固定E11カメラの画面空間に既存メッシュ頂点を投影し、NAVEの既存西母体736頂点を変更（最大380.74848m）、H1の既存東母体576頂点を変更（最大543.24411m）。実行方式は**真のBlender GUI内でのPythonネイティブ頂点移動**。GUIの見た目を根拠とするが、`bpy.ops.sculpt.brush_stroke`やX11マウス手彫りが成功したわけではなく、そのように称しない。
- INT11レンダーを支配していた繰り返し青色アーチ・支柱（研究不採用9オブジェクト）を**当該研究コピー内だけ**で削除。M247-Cの斜裂を表す既存の主接続オブジェクトは残した。
- 元E11 NAVE・H1・俯瞰3カメラの位置・姿勢行列不変、元W0北山・西断崖・地盤・人工内海の頂点SHA不変。Minecraft正式施工なし。完成フラグ0を保存。
- 実GUIのBEFORE/AFTER PNGを保存。別Blenderプロセスで保存BLENDを再読込、変形済み実メッシュの存在・保護フラグ・W0・カメラ行列を照合し、元固定E11の3画像と追加3画像、全6枚の本物のCycles画像を生成して画像SHAまで検証。
- 展開済みINT12真正BLEND SHA256 `563773c54328f249978c0ed6d989edfc437d467a9d543a0b21511f99d6a508a1`。研究成果 `INT12/evidence/HALO9_INT12_E11_SCREEN_DIRECT_NATIVE_RESCULPT.blend.gz`。
- 本番生成ラン [#42184896560](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42184896560) は、**編集と独立再読込・レンダーの全工程がPASS**だったが、実行中に別のドキュメントコミットが入り、pushがnon-fast-forwardとなりActions全体としてFAIL。この失敗を「全工程SUCCESS」と改ざんしない。
- 重い編集・レンダーを繰り返さず、元ランのActions保管アーティファクト `13487072666` を使った[復旧ラン #42185919808](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42185919808) がSUCCESS。既存の実BLENDと6画像SHA、先行独立再読込PASS結果を検査し、証拠を再生成せず隔離研究ブランチへ保存。今後のActionsは、実行開始後の同じ研究ブランチへの別コミットを凍結するか、既存コミットとのrebaseをpush前に行う。

## 2. 固定・追加6視点を直接比較しての美術審査

| 視点 | INT11→INT12 画像に実際に表れた変化 | 判定 |
|---|---|---|
| E11 NAVE HUMAN | 目立つ青色の太いリブが複数消え、周囲の空洞壁・段状構造が以前より見える。ただし白い大質量、細い浮いた床、用途不明の大きな筒や空洞が依然支配。巨大な単一公共内部・図書館・駅・儀礼堂としての明瞭な空間経験には未到達。平均明度122.64→128.01は美術合否と無関係。 | **局所的IMAGE READABILITY改善／ART REJECT** |
| E11 H1 HUMAN | 射影頂点576個を最大543m動かした結果、以前の青い手前リブは消えた。しかし見えるのは巨大な白灰色の曲面と正体不明のブロックで、通り・市場・学校・住区の立体都市として読めない。明度155.89→157.68は視覚品質の証明ではない。 | **ART REJECT** |
| E11 URBAN AERIAL | 外周表面の凹みや稜線は変わったが、巨大な二つの卵状塊と水平に細い連絡部分が都市の主役。浮断・斜裂・内部都市・W0が一つの象徴的建築として読めない。 | **ART REJECT** |
| 追加NAVE/H1/W0 | 同じBLENDの中間空洞、近接居住室、W0側からも確認。空洞は真正メッシュだが用途や内部の生活密度が不足。追加カメラの映りだけで救済しない。 | **ART REJECT** |

## 3. 重要な失敗の原因と次工程の停止条件

- 「一括生成で新しい殻に交換」から「既存頂点を固定E11に投影して直接彫り直す」技術的改良をしても、**巨視的な建築の発想・公共空間の内外の実用関係・居住都市の密度が画像から読み取れるようになるわけではなかった**。
- 単に頂点数・変位m・厚い塊・大きい穴・画像枚数を増やす方式はここで停止。同じ画像投影アルゴリズムの数値だけ変えて再試行することを禁止。
- 次の本質的工程では、巨大公共内部と生活街区の**実際に利用できる断面構成**を画像・編集可能な3Dで同時に造形する、さらに別の視覚的制作方法が必要。Blenderの実操作を見て場所を理解し、何を削る・残すか選ぶ制作が条件であり、マスク関数を微修正する手法は無効。
- FUNCTION（真正入口・歩行到達・水密性・全都市単位・W0登録）は未検証＝UNKNOWN。総合ARTが不合格のため正式採択なし。30対象完成数0、Minecraft施工HOLD。固定憲章を勝手に緩和しない。
- Work/Computer Use・ユーザーPCへのアクセスは事前承認制、追加課金原則0円、ユーザー操作0回。 GitHub標準ランナーは利用したがユーザー個別の請求状況までは未監査。

**最終証拠：**
- [INT12 編集可能真正BLEND](https://github.com/ryomashibaba/celestial-halo-9/blob/research/r33-s27-d48-int12-screen-directed-sculpt-20261106/studies/M3D-1S/J7/R33-S27/INT12/evidence/HALO9_INT12_E11_SCREEN_DIRECT_NATIVE_RESCULPT.blend.gz)
- [INT12 実Blender固定3＋追加3画像](https://github.com/ryomashibaba/celestial-halo-9/blob/research/r33-s27-d48-int12-screen-directed-sculpt-20261106/studies/M3D-1S/J7/R33-S27/INT12/evidence/INT12_TRUE_SIX_VIEW_UNREVIEWED.jpg)
- [独立検証結果](https://github.com/ryomashibaba/celestial-halo-9/blob/research/r33-s27-d48-int12-screen-directed-sculpt-20261106/studies/M3D-1S/J7/R33-S27/INT12/evidence/INT12_INDEPENDENT_TECH_NOT_ART.json)

**総合INT12：真の編集と検証TECH PASS / ART REJECT / FUNCTION UNKNOWN / 正式採用0 / 0-of-30 / Minecraft HOLD。**
