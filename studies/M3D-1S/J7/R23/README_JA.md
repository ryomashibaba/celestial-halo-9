# J7-R23 — 実Blender中央美術研究

**ART REJECT / 初期美術ゲート不通過。正式中央採択0、施工HOLD。**

[日本語美術審査](R23_ART_REVIEW_JA.md) · [実寸・保存QA](QA_SUMMARY_JA.md) · [短い引継ぎ](R23_HANDOFF.json)

![主形状2回の変更](EVOLUTION.jpg)

これは既存CELESTIAL HALO-9のR21完了HEAD `628abb8d80e3e39a9bad6dd5fe7dec7556a0bcd9` から分岐した独立研究。R22の未採択Chat構想を保存済みモデルと仮定していない。新規プロジェクトや正式都市構成への置換ではない。

| 成果 | 場所 |
|---|---|
| 最終の編集可能モデル | [R23_CROSSING_HORIZONS.blend](final/R23_CROSSING_HORIZONS.blend) |
| 最終実GLB | [R23_CROSSING_HORIZONS.glb](final/R23_CROSSING_HORIZONS.glb) |
| 初回・修正1原本 | [初回BLEND](initial/R23_INITIAL.blend) / [修正1BLEND](revision/R23_REVISED.blend) |
| 全方向画像 | [初回](initial/SIX.jpg) / [修正1](revision/SIX.jpg) / [最終](final/SIX.jpg) |
| 最終床上・背面接近 | [画像一覧](final/FLOORS.jpg) |
| 実断面2方向 | [長手BLEND](sections/LONG_Xminus800.blend) / [横断BLEND](sections/CROSS_Y500.blend) |
| 失敗形状 | [非平面Boolean失敗](qa/FAILED_NONPLANAR_MACRO/README_JA.md) |
| 制作・検証ソース | [create.py](create.py) / [verify.py](verify.py) |

Blender 5.2.1 LTSを独立バックグラウンド実行。Cycles CPU、同時レンダー1本・4スレッド、24 samples、中性材質、発光・霧なし、通常1440×960。全体6方向は同じカメラ。床上は位置・姿勢の修正を審査に明記。実断面のみ橙の切断線を使用する。

再生成順は `create.py -- initial` → `create.py -- revision` → `create.py -- finalmacro`。それぞれBlenderの `-b -t 4 --python` で実行し、引数の `--` 後にモードを渡す。レンダーは `create.py -- render initial|revision|final`。技術QAとGLB書出しは `verify.py -- verify`、実断面は `verify.py -- sections`。通常Python補助処理は `python -B -X utf8` を使う。出力先は本研究ディレクトリのみ。既存原本・上流証拠ディレクトリでは実行しない。

一般建物内部だけを例外とする10km詳細CITY MASTERの完成基準は維持する。本研究はその完成を達成していない。全歩行・空洞体積・構造安全・交通運用・正式座標・Minecraft適合は未認証。前面Computer Useなし、実ワールド非アクセス、main・既存Draft PR・保護資産に変更なし。
