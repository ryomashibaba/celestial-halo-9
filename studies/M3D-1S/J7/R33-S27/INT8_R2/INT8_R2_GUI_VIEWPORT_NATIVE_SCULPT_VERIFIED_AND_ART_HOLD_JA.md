# CELESTIAL HALO-9 — INT8-R2 真正Blender GUI視覚連動スカルプト実装・批判的引き継ぎ（2026-11-06 JST）

**状態：REAL_GUI_TECH_PASS / X11_MOUSE_SCULPT_UNPROVEN / GUI_VIEWPORT_SCULPT_OPERATOR_PASS / INDEPENDENT_BLENDER_REOPEN_PASS / ART_HOLD / FORMAL_ART_0 / CITY_MASTER_0_OF_30 / MINECRAFT_HOLD。**

本書はINT8の技術継続記録であり、新規企画や正式憲章変更ではない。INT7-R1 ART REJECTと、2026-11-06完全統合・批判的引き継ぎ正本を上書きしない。

## 検証した実際の成果

- 保護された親研究の真正BLEND：INT6の `HALO9_INT6_TRUE_BRUSH_SCULPT_DISTRICTS.blend`、展開SHA256 `51ec4f2c58c74fe03dd44dc7ababcdec315dd77b556d27cfb9541b65d56b28fe`。GitHub Actions上で研究コピーへ読み込むだけで、過去のBLEND・main・Freeze・Minecraftワールドは更新しない。
- Blender 5.2.1 LTS公式バイナリのSHA256検証後、Xvfbの**非background GUI**を開き、実ビューを表示。対象 `INT6_TRUE_BRUSH_west` は1680頂点。
- INT8-R1で`bpy_extras.view3d_utils`によって対象面のGUI投影座標 `(622.5,406.5)`、対象オブジェクトへのレイヒット、実画面との一致を確認。しかし**X11マウスによる頂点変更は0**であり、**GUIでマウス手彫りが成功したとは言わない**。
- R2の初期失敗はX11キーボード入力で長いパスの一部が欠落し、GUI Consoleに `FileNotFoundError` が現れたことが実画面で判明。入力コマンドを短い`z.py`に切り替え、入力遅延を延ばして解消。原因を証拠なしにBlender本体の不具合としない。
- **最終真正成功：[GitHub Actions #42163907820](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42163907820)**。可視状態のVIEW_3DからBlender標準の`bpy.ops.sculpt.brush_stroke`を4回実行し、操作前後の頂点差を実測。
- **49 / 1680頂点が0.01m超変化、最大4.504028m**。単なるオペレーター`FINISHED`を成功とみなさず、研究BLENDを保存し別プロセスで再読込後、差分頂点数、元3カメラ、すべての表示フラグ、未承認フラグの一致を検証。
- 出力真正BLEND：`INT8_R2/evidence/HALO9_INT8_R2_VISIBLE_GUI_SCULPT_OPERATOR.blend.gz`。展開後のSHA256 `c68697d483114f30698c158d0bf108a5796f865b804b14c86fdfe5074e4a11ac`。GUI前後の実スクリーンショット：`INT8_R2/evidence/INT8_R2_ACTUAL_GUI_BEFORE_AFTER.jpg`。数値証拠：`INT8_R2/evidence/INT8_R2_TRUE_GUI_TECH_NOT_ART.json`。
- 元のE11固定3カメラ行列および150研究メッシュの表示状態を復元。追加課金を伴うAPI、Work/Computer Use、ユーザーPCへの接続をしていない。GitHub公開リポジトリの標準Hosted Runnerを使用（請求画面・個別無料枠残量までは未監査）。

## 不合格を合格にすり替えない判定

**TECH PASSはGUI表示とスカルプト実編集・保存・再読込の技術経路に限定。ART採択とは別。** GUI比較画像では前側は対象メッシュを単独表示、後側は元の他オブジェクト表示を復元しているため、**同条件の形状の美術比較には使えない**。既存NAVE巨大内部、H1居住都市、M247-Cの双殻と斜裂、W0との統合は完成していない。

この49頂点・最大4.5mの局所変形を都市級の造形改善と認定しない。正式ART採用0件、30対象完成0/30、Minecraft施工HOLD。

## 次の本質的な実制作手段

1. INT8-R2の成功したGUI/画面レイヒット→ブラシ適用→再撮影→独立再読込経路を、NAVEの巨大公共内部とH1実居住部の**主形状修正**に限定して再利用する。ただし投影座標に合う大規模な空洞・空間を視覚で審査し、既存の棚・箱・楔を量産しない。
2. 編集前後のスクリーンショットは**同じ可視オブジェクト・同じ視点・同じシェーディング**で比較し、正式アート画像は固定E11人間視点・俯瞰、公開室内部で独立に判断。自動レンダー枚数や頂点変化数を美術合格の代用にしない。
3. X11マウスによる手彫りは未実証として停止し、任意の再試行で実変位を偽装しない。GUI命令とマウス手彫りは明確に別証拠のまま扱う。
4. ART-FIRST／Macro Impact First／CITY MASTER 3D FIRST、M247-C《浮断天核》、10km級の30対象詳細完成義務を維持。main・Freeze・原本・過去研究・Minecraftワールド保護。Work/Computer Useは明示事前承認。追加課金原則0円。

**制作エンジンの可視実行と保存の技術経路が新たに実証されたが、実際の都市美術は未解決。ここを次工程の正直な出発点とする。**
