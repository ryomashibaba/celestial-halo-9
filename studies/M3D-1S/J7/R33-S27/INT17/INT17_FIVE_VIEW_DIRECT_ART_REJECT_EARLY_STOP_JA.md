# CELESTIAL HALO-9 — INT17 本物のBlender制作と5視点画像審査、批判的ART REJECT・早期停止

基準: 2026-11-06 JST / 対象: `research/r33-s27-int17-urban-architecture-first-20261106`。**新規企画・正式方針変更・ART採用ではない。**

## 最終判定

**SOURCE PASS / EDITABLE TRUE BLENDER 3D PASS / INDEPENDENT REOPEN PASS / 5 VALID REAL NATIVE IMAGES PASS / ART REJECT / FUNCTION UNKNOWN / FORMAL ART ADOPTION 0 / CITY MASTER 0/30 / MINECRAFT CONSTRUCTION HOLD / COST_AUDIT UNKNOWN.**

**旧INT16の卵状殻を後追い修正するのではなく、INT15の検証済みBLEND `e996fab613904dc557638612d4380ba67ef5c6bbd4aa8f511fb9` から独立研究コピーを作った。** COPY上で旧不採用研究メッシュ32件を除去、W0正式コア4メッシュの頂点指紋と固定E11カメラ3行列は保存。正式main、旧INT15/16、Freeze、Minecraftワールド原本は一切書き換えなかった。研究上の空間座標が正式ワールド座標と一致するとは主張しない。

## 実作業・再読込

- Blender 5.2.1公式tar/checksum検証。新しい研究COPYのNAVE、H1、市街地と空中都市を含む**30個の編集可能ネイティブメッシュ**を著作コードから生成。
- 同じBLENDから固定E11のNAVE/H1/URBAN_AERIALと新しいW0_CITY_AERIAL/H1_STREETの5視点を作成。レンダー直前に不採用形状だけを一時非表示にしたCUTAWAYではなく、旧不採用物体を研究コピー上で物理的に整理した別研究シーン（**正式な全都市統合完成を証明するものではない**）。
- BLEND展開SHA256：`f6d8c52d6a047c83e07111060dfa397c5f89e19d16c8b380967586e80c687823`。別Blenderプロセスの独立再読込と5枚の画像SHA照合PASS。
- 初回Actions #42228277382は`REJECTED_STUDY_SCENE_NOT_FOUND`（期待40件に対し実数32件）で制作前にFAIL。W0保持条件を変えずに不適切な数の仮定のみ修正した再実行 [#42228489217](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42228489217) は全ステップSUCCESS。
- 本制作は**Blenderの背景Pythonコードによる幾何編集**であり、GUI手彫りやAIによる実画面のインタラクティブ直接造形ではない。

## 5視点を実際に見て判定した致命的なART不足

[INT17 5真正レンダー](evidence/INT17_FIVE_NATIVE_VIEWS_UNREVIEWED.jpg)

1. `E11_NAVE_HUMAN`: 巨大な板状の屋根・白灰色の塊・不自然な斜めの梁が主画面を占有。駅、図書館、儀礼・公開ホールの空間的秩序、透明感、建築的深さが未成立。**ART REJECT**。
2. `E11_H1_HUMAN`: 巨大な手前の白い床・角柱・横桁・緑の簡易ブロック。市場・学校・住居の用途を視覚から識別できず、実際の生活都市ではない。**ART REJECT**。
3. `E11_URBAN_AERIAL`: 旧卵殻は消えたが、今度は無表情な直方体群、巨大板と細長い桁へ後退した。M247-Cのα双殻浮断＋β斜裂天脊の非対称な都市級存在感、生活層、W0との構造統合を示せない。**ART REJECT**。
4. `INT17_NEW_ARCHITECTURAL_W0_CITY_AERIAL`: 遠くから見ても、長方体の塊・四角い塔・斜桁の集合。明確な都市空間や超文明的な主役性なし。**ART REJECT**。
5. `INT17_NEW_H1_LIVED_STREET`: 視点を移しても、生活街区ではなく巨大な無地の壁・横板・偽のブロックに見える。**ART REJECT**。

同一BLENDの試作でNAVE/H1/W0の要素名と位置を持たせたが、**存在する部品と、芸術的に高品質で住める公共空間を完成させたことは別物**。室内・構造干渉・生活交通・乗降/歩行は検証なし。TECH PASSをART/FUNCTIONに流用しない。

## INT1–INT17全体の技術的・批判的学び

卵殻を削ったINT16から、建築の名前を持つ個別プリズムへ方向を変えても、画面には**コードで定義しやすい塊・板**が再発した。旧来の「式とポリゴン数を増やす」問題を根本的に超えられていない。INT17も繰返し手法の限界を裏付ける**研究上の否定証拠**であり、美術前進として正式採用してはならない。

**STOP:** INT17-R1による軽微な遮蔽物切除、窓・装飾の量産、似た巨体のINT18コード連続生成をしない。ART-FIRST / Macro Impact First / CITY MASTER 3D FIRST、M247-C《浮断天核》、30対象の全詳細完成義務は不変。

次の本質的障害は、**実画像を見ながら空間を選択し、既存3Dメッシュの意味ある主形状と内部公共室を直接造形・再判断できる制作ツール**である。現行Chat/Actions一括コードだけでは未実証。使える接続がないなら`INTERACTIVE_ART_AUTHORING_CAPABILITY=HOLD`。Work/Computer Use・ローカルBlender/MCP・追加課金は新規明示承認制。ユーザー操作原則0回。

## 証拠

- [真正BLEND](evidence/HALO9_INT17_ARCHITECTURE_FIRST_RESEARCH.blend.gz)
- [固定3＋補助2の実レンダー](evidence/INT17_FIVE_NATIVE_VIEWS_UNREVIEWED.jpg)
- [独立検証JSON](evidence/INT17_INDEPENDENT_TECH_NOT_ART.json)
- [正式GitHub Actions SUCCESS #42228489217](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42228489217)

**正式採用0件、全30完成0/30、Minecraft施工HOLDを守る。**
