# CELESTIAL HALO-9 R4-E10 — 真正3D審査と次の制作方式

**日付：2026-11-05 JST／真正Blender TECH PASS・ART REJECT／正式採用0・完成30対象中0・Minecraft施工HOLD。**

## 事実と保護

- 正式方針：mainのPROJECT_CONSTITUTION、CITY_MASTER_3D_STANDARD、AGENTS.mdに従う。ART-FIRST／CITY MASTER 3D FIRST（一般建物の私的室内以外の全域を詳細な統合3Dにしてから施工）。正式M247-C研究方向・W0・H1〜H6・SB01〜SB16・HERO4・交通軸・V1〜V3は維持。
- 研究起点：E9-R1研究HEAD 8d972d135c5fb8e149203029fb58cf73bd143bb4。E9-R1は技術的に成功／美術不採用。E10は原本不使用の新規スカルプトコントロール形状研究。旧形状を移植していない。
- 制作成果：自作した非均一な3D制御輪郭から、中央の左右異形都市崖、NAVEの公共床・階段・回廊・公共空洞、H1の厚い高所市街基盤と4公共施設、W0の地形・水際研究コンテクストを同じBlender研究シーン内に制作。
- GitHub Actions [#42032218274](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42032218274) SUCCESS。Blender真正BLEND作成、3つの同一シーン実PNG、別プロセスBlender再読込、PNGヘッダー・寸法検査、SHA照合を実施。
- 技術報告：mesh_count=73、actual_cavity_operations=10、編集可能BLEND SHA256 e9a1d095d619d923c614d326c2ecb4747ea8e48640bd2304965d3f082e97a091。これらは美術の良し悪しを証明する数値ではない。
- 長期保存：e10_evidence/E10_HAND_SCULPTED_LIVED_RIFT_WORKING.blend.gz（本物の編集可能BLENDのgzip）、E10_REAL_NATIVE_THREE_VIEW_ART_UNREVIEWED.jpg（同じBLENDからのPNG3枚の縮小比較）、E10_TECH_NOT_ART.json。フル解像度のPNG・BLEND本体はActions Artifact ID 13416503484（7日間保持）。
- Work/Computer Use、有料API、ユーザーのローカルBlenderは起動していない。GitHubの隔離研究ブランチ以外に書き込んでいない。main、原本、Freeze、Minecraftワールド無変更。

## 実画像の直接美術審査 — ART REJECT

1. **NAVE人間視点：REJECT。** 巨大な浮いた殻状屋根と地上の単純な段状床が主景。数百メートル級の使える公共室、都市活動の密度と場所の序列、垂直動線、圧倒的な内部建築美術が読み取れない。かつて失敗した「巨大殻と床」の印象に戻っている。
2. **H1人間視点：IMAGE INVALID。** 得られたPNGは全面黒であり、実3Dの評価に使えない。カメラ内部遮蔽などの可能性はあるが、現時点で遮蔽物の同定や原因検証は未実施。技術的レンダー生成の成功と有効な視覚審査の成功は別。
3. **都市俯瞰：REJECT。** 建物が二つの大きな曲面塊と、端に接続された小型の板状高所地盤に見える。遠景で独立した超未来都市の文明、神聖さと危険な異常さ、中央の斜裂都市級空洞、W0地形との一体性、巨大生活都市が立ち上がっていない。
4. よって、**TECH PASS／ART REJECT**。正式採用0件、30対象完成0件、CITY MASTER未完成、Minecraft施工HOLD。R4-E10主形状を増築・装飾で採用させない。

## 自己批判と確定方針の継続

E6〜E10まで別のスクリプトで生成しても、主形状が「巨大な殻・箱・板」のいずれかへ収束し、居住・内部空間の美術品質が上がっていない。これは工程番号やCI検査数の不足ではなく、**Blender上の立体を直接視覚的に操作する美術制作が足りない**問題。E10の手指定制御輪郭も単独では十分な品質に至らないことを実画像で確認した。

**同じ手法のE11自動生成を継続しない。** これ以上の新規QA監督器や差分報告のために時間を費やさない。次のまとまった実制作では、中央・NAVE・H1・W0を同時に扱う独立の真正3Dアート制作環境で、Blender GUI等を通じて主要空洞・都市断面・建築質量を絵で見ながら直接編集する。E10は不合格の比較証拠であり、制作上の正規マスターとしては使わない。

Work/Computer UseによるGUI制作は毎回事前のユーザー明示承認が必要。実装されている接続・PC操作能力は未検証。新規承認がなければ勝手に開始しない。正式ART採用・mainへのマージ・Minecraft正式ワールド施工は、これとは別に明示承認が必要。
