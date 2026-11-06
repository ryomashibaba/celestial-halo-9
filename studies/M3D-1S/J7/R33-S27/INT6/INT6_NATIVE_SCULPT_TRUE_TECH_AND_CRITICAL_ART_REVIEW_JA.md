# CELESTIAL HALO-9 — INT6 真正Blenderスカルプト制作・直接画像ART審査（2026-11-06 JST）

**最終判定: 既存BLEND原本検証 PASS / Blender Sculpt Mode真正ブラシ操作 PASS / 保存された頂点座標の変化 PASS / 別プロセス再読込 PASS / 4視点真正画像 PASS / 統合ART REJECT / FUNCTION UNKNOWN / 正式採用0 / 完成0/30 / Minecraft施工HOLD。**

この文書は正式方針変更ではない。過去の「プログラムで巨大殻/棚/箱を増設する」路線へ戻さないため、新しい制作操作の成立と芸術上の限界を同時に記録する。

## 研究原本、隔離、真正成果

- 元: `research/r33-s27-d48-int4-r1-image-guided-sculpt-20261106` の真正編集可能BLENDをSHA256 `7cf765923b91f06cce7951fc3558f042e488bf9f1157791b59b14d11954dc2bb` で照合した独立コピー。INT5はβの0面構造欠陥があり制作起点に使っていない。
- 最終真正Actions: [#42154050965](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42154050965) SUCCESS。Blender 5.2.1 の公的配布SHA検証、Sculpt Mode の実ブラシ、4レンダー、別プロセスでの保存済みBLEND再読込と頂点変化証拠の照合成功。
- 保存実物: `INT6/evidence/HALO9_INT6_TRUE_BRUSH_SCULPT_DISTRICTS.blend.gz`。展開済みBLEND SHA256 `51ec4f2c58c74fe03dd44dc7ababcdec315dd77b556d27cfb9541b65d56b28fe`。サンプル数/頂点数/各画像SHAは `INT6/evidence/INT6_TECH_NOT_ART.json`。
- 実画像: `INT6/evidence/INT6_TRUE_FOUR_VIEW_ACTUAL_BLENDER_UNREVIEWED.jpg`。上段 NAVE/H1 E11元固定視点、下段左 URBAN AERIAL E11固定視点、下段右は新設の西側彫塑クローズアップ。クローズアップの位置は元E11カメラ位置とは別である。元の3カメラ行列は完全に不変。
- 対象は`INT4_M247_WEST_LOWER_INHABITED_LIMESTONE_urban_occupied_stratum_2`の研究コピー。元オブジェクトは削除せず非レンダー化しており、編集されたコピーは`INT6_TRUE_BRUSH_west`として同一シーンに保存。元の公共機能・W0・H1・NAVEなどはそのまま。
- 成果: Essentials Clay Strips ブラシの4回の真正`bpy.ops.sculpt.brush_stroke`操作後、1,680頂点のうち**172頂点が0.02m超変形**、最大変位**2.31011m**。単なるオペレータの`FINISHED`返却ではなく、編集前後の頂点差を確認。ソース更新のための最初の2試行はTECH FAIL、投影位置を改善した3対象試験は西側で実変形成功・東側の投影失敗で未完成。直交投影への変更は西側でも失敗。**成功が再現した西側1対象に実装を絞り、保存と独立検証まで完了。** これ以外の対象成功を主張しない。
- 手法は「Blender背景実行からの真正Sculpt Modeブラシ」であり、**ローカルPCやGUIマウスの人手彫刻をした証拠ではない**。

## 4視点の直接ART審査

- **NAVE HUMAN：ART REJECT**。元INT4-R1で解消したカメラ近接遮蔽は維持。ただし目の前の白い矩形建築と板状の橋が支配し、図書館・鉄道駅・儀礼の巨大内部が見える建築的統合に至らない。
- **H1 HUMAN：ART REJECT**。市場・学校・住居・連続街路の機能的豊かさや高密度居住都市の迫力は不足。浮いた箱や平たい接続がまだ視線を占める。
- **URBAN AERIAL：ART REJECT**。細い高所の棚・小型建造物の構成は、M247-Cの巨大双殻と斜裂天脊の記念碑的主題を十分に表さない。W0は景観背景のままで一体の建築作品とまでは読めない。
- **西側近景：ART REJECT**。新しいブラシ技術で変形したメッシュが保存されていても、画像上は他の箱状構造と平たい橋が主役。2.31mという巨視的スケールに対して小さい変形は、形状品質の決定的改善とは認定できない。

**最終評価: 制作方法の真正なTECH突破であり、完成美術の前進は未実証。TECHをARTと取り違えない。**

## 失敗を踏まえた次の制作実務

1. INT6を正式ARTベースラインにしない。結果は「Blender Sculpt Mode のブラシで既存実3Dを改変できる」制作技術証拠としてだけ保持する。
2. 次回は全都市の微小なブラシストロークや大きな殻を大量に作るのではなく、**一つの巨大公共内部を画像を見ながら空間的に設計・彫塑し、同一シーンの遠景と人間視点の両方で根本的な改善を証明する工程**を選ぶ。
3. 西側以外の対象では投影更新が失敗したので、対話的な画面状態を切り替える信頼できる方法が実証されるまで「3地区を一括Sculpt済み」と表記しない。背景実行で生産品質が到達できると根拠なく楽観しない。
4. GitHub Actionsを動かすだけで0円無制限とは言えない。請求残量は直接未監査。外部有料API・Work・Computer Use・ユーザーPC操作を本工程で開始していない。
5. **固定継承**：ART-FIRST / Macro Impact First / CITY MASTER 3D FIRST、M247-C《浮断天核》のα双殻・β斜裂、W0・H1〜H6・16施設等を含む30対象の約10km級の施工前詳細完成義務。原本/main/Freeze/既存研究/Minecraftワールドを保護。正式ART採用0、完成0/30、施工HOLD。

本資料は既存憲章や完全統合引き継ぎ正本を上書きせず、検証済みの実結果のみを追補する。
