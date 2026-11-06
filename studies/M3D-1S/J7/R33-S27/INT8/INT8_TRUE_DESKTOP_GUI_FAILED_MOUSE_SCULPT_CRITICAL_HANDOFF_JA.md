# CELESTIAL HALO-9 INT8 — 真正Blender GUI視認・X11操作の実測と安全な停止（2026-11-06 JST）

**最終: SOURCE PASS / REAL GUI OPEN PASS / ACTUAL GUI SCREENSHOT PASS / SCULPT MODE PASS / GUI CONSOLE PASS / X11 MOUSE MESH CHANGE FAIL / NEW EDITED BLEND NOT SAVED / ART NOT REVIEWED / FORMAL ART 0 / COMPLETE 0/30 / Minecraft HOLD.**

## 目的と固定方針

INT2〜INT7-R1まで同型の巨大楔、板、箱、外殻を自動生成し続けても公共内部・居住都市のARTが不合格だった。INT8はこれらの形状候補を増やす工程ではなく、現物のBlender GUIを見ながら特定メッシュを直接編集し、スクリーンショットと独立検証を連結する制作環境実証である。ART-FIRST / Macro Impact First / CITY MASTER 3D FIRST、M247-C《浮断天核》のα双殻浮断＋β斜裂天脊、10km級30対象詳細完成義務は変更しない。

## 実際に完了したこと

- 完全隔離研究ブランチ `research/r33-s27-d48-int8-visual-blender-ui-20261106`。親研究INT7-R1のHEAD `2467679894e82aa83b389464e9691e005d9f2ec2` から分岐。
- 公開リポジトリのGitHub標準ランナー Ubuntu 24.04 上に Xvfb・Openbox・xdotool・scrot を導入。Blender 5.2.1 LTSの公式配布SHAを照合し、`--background`を指定しない本物のGUIで研究BLENDを開いた。
- ソース研究BLENDはINT6で技術検証された `HALO9_INT6_TRUE_BRUSH_SCULPT_DISTRICTS.blend.gz`、展開後 SHA256 `51ec4f2c58c74fe03dd44dc7ababcdec315dd77b556d27cfb9541b65d56b28fe`。原本への書込なし。
- 実画面に `Sculpt Mode`、`Clay Strips`ブラシ、既存 `INT6_TRUE_BRUSH_west` 1680頂点を表示。読み込みタイミングの問題を GUIイベントループで解決。最初のBlender Quick Setup表示も実スクリーンショットを見て修正。
- X11マウスドラッグ前後の実デスクトップPNG、GUI Python Consoleからのメッシュ検証、起動ログを実行。3つの元E11カメラの行列・formal ART 0・完成0・Minecraft HOLDを検査対象として固定。
- 前景遮蔽による対象違いを疑い、**GUI作業時にだけ研究シーン内150メッシュを非表示**として対象を単独表示。ソースファイルは変更せず、保存する場合は非表示状態を元に戻すコードを実装した。

## 失敗として確定する事項

- **X11マウスを動かしただけでは対象の実頂点は変わらなかった**。GUI Python Consoleで読み出した物理頂点数は1680、変位閾値超えは0個、最大変位0m。単独表示でも同じ。原因の確定はできておらず、マウスイベントのスクリーン→3D位置対応・ブラシのターゲットヒット判定・入力状態などの問題が考えられるが、未実証の断定をしない。
- GUI編集成功を偽るような`bpy.ops.sculpt.brush_stroke`をバックアップ経路で実行することはしていない。**INT8で新たな編集済みBLENDは生成・独立再読込・保存できていない**。INT6既存成果とは区別する。
- すべての起動・画面・マウス・コンソール実験はTECH研究のみであり、ART改良・作品完成の主張ではない。プログラムによる単純な楔・殻・棚量産にも戻っていない。
- GitHub Actionsの初期数回のTECH FAILを隠さない。第1回は `xdpyinfo` の不足、第2回はBlender GUI起動直後の資産読み込み未完、第3回以降は物理頂点変化0。詳しいログ・GUI証拠は同枝 `INT8/debug/` にある。実ジョブは失敗で終了。

## 安全条件と今後の実工程

- Main・正式憲章・Freeze・全旧研究原本・ユーザーPC・Minecraftワールドの変更なし。Work/Computer Use、ユーザーローカルBlender/ポート9876、外部APIを無断利用していない。
- 次にこの方式を再開する場合は**目視とオブジェクトレイヒットを一致させるテスト**を最初に作り、正しい対象に当たったことを確認したときだけ実ブラシで変更する。停止済み形状の自動生成・同じ無根拠なマウス操作・高コストQAを繰り返さない。
- リアルタイムの視覚判断と3D編集のループが実証されるまでは美術採択しない。継続的なGUIデスクトップ利用やWork/Computer Useは未承認。原本保護条件を守る。
- 公開GitHub標準Hosted RunnerはGitHub公式の料金説明上無料だが、個別の請求画面の監査はしていない。

**状態：REAL_GUI_TECH_PARTIAL_PASS / MOUSE_SCULPT_HOLD / ART 0 / CITY_MASTER 0/30 / MINECRAFT HOLD。**
