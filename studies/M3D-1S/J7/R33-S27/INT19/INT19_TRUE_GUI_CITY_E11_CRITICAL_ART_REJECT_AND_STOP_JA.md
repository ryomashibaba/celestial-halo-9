# CELESTIAL HALO-9 — INT19 実GUIでの都市メッシュ直接造形・固定E11前後3視点の批判審査（2026-11-06 JST）

## 最終判定

**SOURCE PASS / TRUE X11 GUI MOUSE SCULPT PASS / SAVED EDITABLE BLEND PASS / INDEPENDENT BLENDER REOPEN PASS / E11 3×BEFORE + 3×AFTER IMAGE VALID / ART REJECT / FUNCTION UNKNOWN / FORMAL ART ADOPTION 0 / CITY MASTER COMPLETE 0/30 / MINECRAFT HOLD / COST_AUDIT UNKNOWN.**

新規企画・方針変更ではない。**ART-FIRST / Macro Impact First / CITY MASTER 3D FIRST**、正式M247-C《浮断天核》のα双殻浮断＋β斜裂天脊、約10km級都市と**全30対象の内外詳細完成義務**は変更していない。過去INT16/17の不採用形状は採用しない。

## 本当に行った操作

- **基礎：** INT15の保護済み現物Blenderシーン `HALO9_INT15_H1_OCCUPIED_LIFT_PUBLIC_CORE.blend`、展開SHA256 `e996fab613904dc557638612d4380ba67ef5c6bbd4aa9fb219d9aeaa8f511fb9`。INT18の**X11実マウス操作の技術**だけ継承。旧BLENDや原本を書き換えていない。
- **対象：** 現物3D内の `INT11_M247C_ALPHA_WEST_ACCRETED_ARCHIVE`（6,220頂点）のNAVE側面を、可視3D表面のレイ命中と既存面の頂点付近から選択。他のメッシュは作業中のGUIビューポートでのみ隔離し、**保存前に元の表示を復元**した。レンダーは元の全研究シーンで実行し、特定パーツをCUTAWAYで隠していない。
- **編集方式：** Blender 5.2.1の本当のウィンドウ（Xvfb+Openbox）のスクリーンで、`xdotool` の物理X11イベント（Ctrl+マウス押下・移動・解放）を使用。**`bpy.ops.sculpt.brush_stroke`を偽の代替にはしていない**。3D部品・殻・箱を新規生成する数式方式でもない。
- **検証：** **13/6,220頂点が0.01m超変化し、最大変位16.317060m**。変更された研究COPYの展開済みBLEND SHA256は `14819e62d45854ee64767f3fbaa61e9f7b4eacb756586103ec5cc2a34d820f70`。Blender別プロセスで再読込し、変位数/最大変位、**固定E11 3カメラの不変**、**W0コア4メッシュの頂点指紋不変**、未承認/施工HOLDフラグを照合してPASS。
- **実画像：** 元E11 `NAVE_HUMAN`・`H1_HUMAN`・`URBAN_AERIAL` をそれぞれ編集前と後の**同設定Cycles真正レンダー6枚**にし、同一横並び比較画像を保存した。補助カメラによる差し替えなし。
- **CI：** 初回[#42235720987](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42235720987)では出力名の食い違いで独立読込に至らずTECH全体FAIL。再実行[#42236185529](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42236185529)で編集/再読込/6レンダーまで成功したがPIL保存変数の取り違えでアーカイブFAIL。修正後の最終[Actions #42236789254](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42236789254)は**全ジョブSUCCESS**。過去の失敗を隠さない。

## 直接画像の批判的なART審査

[INT19 固定E11 3視点の真正BEFORE/AFTER](evidence/INT19_GENUINE_E11_BEFORE_AFTER_ART_UNREVIEWED.jpg) を直接開き検討した。

- **NAVE_HUMAN：ART REJECT。** 編集前後で視覚的な差はごく小さく、視界の大部分を巨大板・通路に見えない棚状床・白灰色の単純な殻が支配する。駅・図書館・儀礼公開ホールの荘厳な大空間と内部都市建築の秩序は成立していない。
- **H1_HUMAN：ART REJECT。** 正面の茶色の大面積の遮蔽と単純な架構がそのまま。市場・学校・住宅・昇降交通が一体の都市として読めない。
- **URBAN_AERIAL：ART REJECT。** 丸い巨大双殻、細い連絡構造と空洞が依然として支配。M247-Cの都市級斜裂・巨大な生活構造・W0との地形構造結合の美術に変化なし。

**TECHとしては「本当の都市研究シーンでマウス彫塑→保存→再読込→元カメラ画像審査」が初めて統合実証された。** しかし**スクリーン上の変形が小さすぎ、建築的マクロインパクトを欠く**。局所ブラシによる形状修正を重ねると過去INT1–17の失敗を再発させる可能性が高く、**INT19-R1小修正は行わず、ART REJECTで凍結**する。

## 安全・次工程

- `main`、Freeze、W0正式コア、INT15・INT18原本、既存研究、Minecraftワールドには書込なし。追加課金のあるAPIやWork/Computer Use、ユーザーPC操作はしない。GitHub Actionsの個別の請求残高は未監査のためCOST_AUDIT UNKNOWN。
- GUIの**操作可能**とAIの**都市級アート判断を伴う連続3D造形可能**は違う。真正美術制作に必要なのは、NAVEの内部・H1の街路・M247-C外観・W0の岸壁を**同じ統合シーンで見ながら大きく構図変更する作業**。今の自動X11局所一筆と数式モデル量産を延長しても達成を証明できない。
- 次工程では別手段での視覚的インタラクティブ造形の可用性を確認する。ただしWork/Computer Use、ローカルBlender/MCP接続は毎回明示承認が必要。勝手に開始しない。全30対象完成義務を減らさない。

## 元データと証拠

- [編集可能な真正BLEND](evidence/HALO9_INT19_NAVE_REAL_GUI_SCULPT_RESEARCH.blend.gz)
- [固定E11真正レンダー6枚による前後比較](evidence/INT19_GENUINE_E11_BEFORE_AFTER_ART_UNREVIEWED.jpg)
- [実GUI入力の画像](evidence/INT19_REAL_GUI_SCULPT_EVIDENCE.jpg)
- [独立検証JSON](evidence/INT19_INDEPENDENT_TECH_NOT_ART.json)

**正式ART採用0件、CITY MASTER詳細完成0/30、Minecraft施工HOLD。**
