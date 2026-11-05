# CELESTIAL HALO-9 — INT4→INT4-R1 真正制作・画像直接審査（2026-11-06 JST）

**結論: SOURCE/TECH PASS、IMAGE VALID、FUNCTION UNKNOWN、ART REJECT、FORMAL_ADOPTION 0、完成 0/30、Minecraft HOLD。**

## 原本・固定方針
最上位 ART-FIRST / Macro Impact First / CITY MASTER 3D FIRST / M247-C《浮断天核》(α双殻浮断＋β斜裂天脊) / 30対象施工前詳細3D義務を変更していない。研究メートルは正式Minecraft座標未認証。既存のINT1・INT2・INT3・main・Freeze・Minecraft原本に上書きしない。R1は隔離枝の独立研究コピー。

## 実制作・厳密な技術証拠
- 初回INT4: [Actions #42125006044](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42125006044) SUCCESS。INT1不採用建築6439を研究コピーで撤去。NAVE40 / H135 / M247 48 / W0 20 の研究メッシュ。別の制作方法として、巨大な二本の一枚壁やBoolean空洞の反復をやめ、建築用途・歩行動線・複数居住テラスを明示配置。Blender 5.2.1で実BLEND・3枚の固定レンダー、別プロセス再読込/ハッシュ一致。
- INT4実画像を直接見た初回ART: **REJECT**。NAVEとH1の眼前に床／通路が入り画像体験が破綻。俯瞰は無数ではないが、小さな箱・薄い浮遊棚が優勢でM247-Cの二重巨大都市主質量と都市級斜裂が成立しない。平均明度が高くても「公共空間が読める」ことは証明しない。
- 読取り専用のBlender実レイキャスト [Actions #42125996618](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42125996618) SUCCESS。原本固定NAVE中心レイは `INT4_W0_PORT_NAVE_WALK` に5.228mで衝突、H1は `INT4_W0_NAVE_H1_LIVING_TRANSIT` に8.444mで衝突。実結果は `INT4_R1/evidence/INT4_R1_ORIGINAL_RAYCAST.json` に保存。
- 根拠に基づく真正R1の直接メッシュ修正: [Actions #42126489952](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42126489952) SUCCESS。**同じINT4真正BLENDをSHA `c71dbe46f7fda20aee6d1355720fc76b5c64d6c0a4ccf0b8bbaa0e210d2fff41`で照合して別コピーを編集**。公共通路4本の頂点高度を場面に応じて修正、H1の過高な12頂点の床を18m低くし、図書館公開踊場ほか3個を実造形。元カメラは3つとも不変、近景を偽装していない。
- 修正後レイ: NAVE中心は約601.272m先の式典室の日除けまで通る。H1は中心レイがSKY（5km以内の中心レイ交差なし）。NAVE/H1真正レンダーは直接視認可能に改善。技術結果は `INT4_R1/evidence/INT4_R1_TECH_NOT_ART.json` に保存。
- R1真正編集可能BLEND: `INT4_R1/evidence/HALO9_INT4_R1_SCULPTED_VIEW_AND_PUBLIC_ACCESS.blend.gz`、展開後SHA256 `7cf765923b91f06cce7951fc3558f042e488bf9f1157791b59b14d11954dc2bb`。
- R1の3固定画像: `INT4_R1/evidence/INT4_R1_ACTUAL_THREE_SAME_CAMERAS_UNREVIEWED.jpg`。3枚とも1100×825 PNGを元とする同一BLENDの縮小画像。IMAGE_VALIDは読み取り・非暗転の最小限であってARTではない。

## 画像を実際に見た美術審査

| 固定視点 | 観察 | 判定 |
| --- | --- | --- |
| NAVE HUMAN | R0の巨大白面による眼前遮蔽は解消。両側に建物と上空接続が見えるが、白い直方体の仮室・浮いたブロックが支配的で、駅・図書館・儀礼室が巨大主建築の一体空間に見えない。 | 部分視線改善 / **ART REJECT** |
| H1 HUMAN | R0のほぼ全面暗転から、床・高所連結・建築群が見える空間へ改善。ただし頭上の板、四角柱的な住居、薄い高所床が多く、学校／市場の生きた厚い都市体験として弱い。 | 部分視線改善 / **ART REJECT** |
| URBAN AERIAL | 実画像はR0とほぼ同じ浮遊床群。中央に数km級の圧倒的な非対称主質量と斜裂負空間の関係が成立していない。W0は景観背景・足場に近い。 | **ART REJECT** |

**重要な反省:** カメラ近接の黒画像修復には実際に成功した。しかし外形と内部の巨大な都市的美術の両立を確立したわけではない。小さな通路・装飾・住宅をさらに足しても芸術的な根本問題は解けない。見せかけの明度、検査、メッシュ数、Actions成功、少数の実Booleanを「最高品質ART」としない。

## 次工程の選択
INT4-R1も**不合格研究標本として保存し、この手続き的な床・多角形プリミティブ増殖路線を停止**する。ART-FIRSTは撤回しない。正式M247-C研究方向も変更しない。

次のまとまった制作工程は、隔離された編集可能BLENDに対し、**本物のBlenderシーンを視認しながら、手動の造形判断を持つAIの彫塑/メッシュ操作を可能にする経路**を安全に検証すること。旧GitHub Actionsの背景Python形状生成だけでは、今の厳しいART基準に到達する根拠が弱い。Work/Computer UseやユーザーPCを使う場合は、その回ごとの事前明示承認を要し、現時点では使用していない。0円制約・原本非改変・Minecraft HOLDを継承。実環境に接続できない場合は成功を偽らずHOLD。環境未検証で次の候補を大量自動生成しない。

公式ART採用0、完成0/30、FUNCTION未認証、施工HOLD。GitHub Actions無料枠残量や実請求について独立した監査は未実施。追加の有料API・外注・Work呼出はしていない。
