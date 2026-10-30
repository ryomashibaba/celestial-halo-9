# CELESTIAL HALO-9 — D47-R18 E3 完全LIVE_HANDOFF
**基準日：2026-10-30 JST／新E3研究専用／正式都市・Minecraft施工なし**

## 不変な最上位方針

約10km級のCEL​ESTIAL HALO‑9 / CELESTIAL SPINE全体において、**中央・周辺各地区・建物外観全棟・必須公共内部・都市交通・地形・素材・照明の詳細な編集可能統合City Master 3Dを先に完成**する。それまでMinecraft施工HOLD。M247-C《浮断天核》α《双殻浮断》＋β《斜裂天脊》、W0/H1〜H6/SB01〜SB16、HERO4は保護する。ART/FUNCTION/SOURCE TECH/正式採択は別のゲート。main、正式原本、Minecraft世界、過去E0〜E2研究HEAD変更禁止、Workと外部PC操作は新規明示許可なしにしない。有料外注なし。最上位の成果は美しい住まわれる未来文明であってCIの数ではない。

## 実際のE3作業

- **研究ブランチ** `research/r33-s27-d47-r18-e3-civic-interior-20261030`。E2最終 `f365b1ad1f01bcf53b8d85de3e09fbb504140673` から独立派生。
- **E3原型は新規実メッシュ。** `D47_R18_E3_NATIVE/e3_lived_archive_amphitheatre.py`。E0/E1/E2形状は流用せず、中央公開科学展示、複数の資料棚・実際の棚板・閲覧席、公開研究台、公共の歩行面と各階のテラスを最初に制作。外側の大岩塊ではなく公共室の体験起点。
- 初回 [#41074274477](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41074274477)：材質名 `E3_white_ceramic` 未定義で生成失敗。登録済み材質名へ直して再試行。
- G0 [#41074492050](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41074492050)：**SUCCESS**。493 mesh／6,535頂点／10,988三角面、真正BLEND・GLB・4視点PNGを出力、独立再読込PASS。3枚目のカメラが青緑の面に遮蔽され美術判定に使えなかった。
- G1 [#41074809860](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41074809860)：カメラ位置・視線だけ変更して**SUCCESS**。G0/G1の真正GLB SHA256同一＝形状自体は無変更。真正4視点の独立Blender原本を取得、目視美術審査済。
- **E3-G1 ART REJECT**。入口・研究広場から資料棚や室内活動の輪郭を確かに確認できる点は以前の無人小物／岩壁より進歩した。しかし全体構成は平凡なU字の円形図書館スタジアムになり、中央リングと単純な繰り返し棚に支配される。閲覧バルコニーも無地の床と大箱が主景。ユーザーの求める唯一無二の超未来都市の美術には未達。詳細は `D47_R18_E3_REVIEW/E3_G1_REAL_4VIEW_ART_REJECT_AND_ARTIFACT_AUDIT_JA.md`。
- SOURCE TECH：新3D生成・BLEND/GLB再読込・4カメラ限定PASS。FUNCTION：高所移動の実接続・出口・支持構造・避難・リフト・アクセス/バリアフリー等未認証。正式ART採択0・City Master未完成・Minecraft HOLD。

## 原本と保存

- E3 G1元原本：Actions成果物 [#12985743777](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41074809860/artifacts/12985743777)（約14日限定）。元の実BLEND+GLB+4PNG+manifest+独立監査JSON。
- 永続化専用のresearch-only Actions：[#41075266266](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41075266266) を登録・起動。**この文書作成時点の完了状態は未確認**。完了なら研究ブランチ `D47_R18_E3_EVIDENCE/R18_E3_G1_ACTUAL_NATIVE_BLENDER_4VIEW_ART_REJECT.zip`、同名HASHES台帳を確認して判定を更新する。
- 個別の画像は各ランの同一実BLENDから撮影されたもの。imagegenイラストを3Dの証拠として採用しない。

## 次工程E4の本質的変更

E0の断片、E1の岩板、E2の峡谷壁、E3の円形スタジアムに共通して不足したのは、独創的な**造形そのものの美しさと人間視点の空間体験**。E3現形状の細密化禁止。E4を単なる半円の細工や光の演出へ転用しない。新たな作品造形は、最も印象的な一つの室内眺望・活動を**本物の3Dの彫刻的な空間構成**で実現し、同一原本で別視点の対称性破壊・奥行き・接続を最初に確かめる。次に実機能を検査。実3D美術が未成立なら巨大都市地区へ拡大しない。外部GUI/Work承認を得たと勝手に仮定しない。

**現時点の正式結論：SOURCE TECH限定PASS／FUNCTION未認証／ART REJECT／正式中央採択0／City Master完成0／Minecraft施工HOLD。**
