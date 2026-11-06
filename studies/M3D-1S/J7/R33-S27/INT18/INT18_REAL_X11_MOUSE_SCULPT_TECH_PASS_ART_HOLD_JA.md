# CELESTIAL HALO-9 — INT18 実GUIマウス彫刻の初成立・美術HOLD（2026-11-06 JST）

**結論: SOURCE PASS / REAL X11 GUI MOUSE SCULPT TECH PASS / EDITABLE BLEND SAVE PASS / INDEPENDENT REOPEN PASS / IMAGE VALID (GUI技術スクリーンショットのみ) / CITY ART NOT EVALUATED / FUNCTION UNKNOWN / FORMAL ART ADOPTION 0 / CITY MASTER COMPLETE 0/30 / MINECRAFT HOLD.**

これは方針変更でも正式美術採用でもない。M247-C《浮断天核》、ART-FIRST、Macro Impact First、CITY MASTER 3D FIRST、全30対象の詳細完成義務を維持。INT17の既存ART REJECTは覆さない。

## 実際に解決した技術的閉塞

過去INT8-R1では、Blenderの投影レイが研究メッシュに命中したにもかかわらずX11実マウスで**頂点変化0**だった。過去の証拠でウィンドウ相対座標のX11物理Yが約20px異なることを再発見し、INT18で**ウィンドウ実ルート座標**へ変更した。X=627,Y=519一致を確認しても初回[#42230785016](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42230785016)は頂点変化0。**座標ずれだけが原因とは言えない。**

保存した実GUI画像では、巨大な平面の中央を直径100px程度のブラシでなぞっており、近傍に編集対象頂点がない可能性が見つかった。INT18-R1で同じ面の**既存頂点付近（面中心→頂点の92%位置）を投影して実レイで再確認**し、X11物理マウスを当てた。形状のプリミティブ追加や `bpy.ops.sculpt.brush_stroke` による偽装フォールバックをしていない。

最初のR1試行[#42231509404](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42231509404)はBlender 5.2.1に存在しない `ToolSettings.unified_paint_settings` の参照エラーによる実GUI準備FAIL。互換性ガード修正後の[#42232035766](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42232035766)はX11実マウスの**43頂点変化・最大19.515124m**をGUIコンソールから記録しBLEND保存したが、独立再読込用BLENDをジョブの別フォルダへコピーし忘れ、総合FAIL。さらにCOPY漏れのみ修正した最終[#42232467089](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42232467089)は**completed/success（すべての工程SUCCESS）**。

## 最終の物理実証

- 隔離実験の研究入力: `INT6/evidence/HALO9_INT6_TRUE_BRUSH_SCULPT_DISTRICTS.blend.gz`、展開SHA256 `51ec4f2c58c74fe03dd44dc7ababcdec315dd77b556d27cfb9541b65d56b28fe`。旧INT6ソース、main、Freeze、過去研究、ユーザーPC、Minecraftワールドへの書込なし。
- Blender 5.2.1 LTSの**非background GUI + Xvfb + xdotool実X11マウス押下・移動・解放**。GUIには対象 `INT6_TRUE_BRUSH_west` 1,680頂点を隔離表示。GUI投影レイで対象を照合し、頂点付近へ実マウス入力。
- **43 / 1,680頂点が0.01m超変化、最大19.692511m**。GUIコンソールで実測後、同一研究COPYをBLENDに保存。元E11 3カメラ・他150メッシュの元の表示状態・ART/完成0/施工HOLDを復元。
- 編集可能な展開済みBLEND SHA256 `fd3796ace910b27a5a48d4d8a69f16d5aff7a3b95bb1a03cdeb2a78967741615`。Blender**別プロセスで独立再読込**し、元頂点との差分、最大変位、固定カメラ、保護フラグを検証してPASS。
- 技術的なGUI比較画像は同じ作業対象と同じ作業ビューを使用。変化は局所であり、全体の都市美術の証拠にはならない。
- **今回はGUIマウスの入力結果を確認したのであって、ChatGPT自体がBlender UIを対話的にリアルタイム操作した証拠ではない**。GitHub Actions内の事前定義イベント実行後に証拠画像を見て判断した段階。真正なリアルタイムART修正ループの完成とは言えない。

## 画像による厳格な境界

[GUI前後画像](evidence/INT18_TRUE_GUI_BEFORE_AFTER.jpg)を直接確認。細部の局所変形は観測できるが、M247-C遠景、NAVE内部、H1居住都市、W0と人工内海の構造結合を同一新候補で審査していない。**CITY ART = NOT EVALUATED, FORMAL ART = 0, COMPLETE = 0/30**。

この技術的成功を巨大都市の美術達成と混同しない。次は**まず本当に高品質な空間の著作・視覚的選択ができる制作手段**を設計し、1代表断面に応用すること。X11座標や小さいブラシテストの量産は禁止。Work/Computer Use、ローカルBlender/MCP、追加課金は事前の新規明示承認が必要。ユーザー操作0。GitHub Actionsの個別請求残高は未監査。

## 保存証拠

- [実マウス編集済みBLEND](evidence/HALO9_INT18_GUI_RAYHIT_MOUSE_EDITED_RESEARCH.blend.gz)
- [同一GUI作業ビュー前後画像](evidence/INT18_TRUE_GUI_BEFORE_AFTER.jpg)
- [実GUI独立検証JSON](evidence/INT8_REAL_UI_SCULPT_NOT_ART.json)
- [最終SUCCESS #42232467089](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42232467089)

**正式ART採用0件／全30完成0/30／Minecraft施工HOLD。**