# J7-R21 実Blender比較の入口

[日本語美術審査・R22方針](R21_ART_REVIEW_JA.md) / [比較の要点画像](sheets/OPEN_OBLIQUE.jpg) / [引継ぎJSON](R21_HANDOFF.json)

**研究専用。R19 ART REJECT維持、C55-A ART HOLD。正式採択0、施工HOLD。**

- `source/model/C55A_SevenfoldHaloRift.glb`：指定ハッシュの原GLB。
- `models/C55A_IMPORTED.blend`：変換した原座標・原材質の編集可能モデル。303オブジェクト／38材質。
- `models/C55A_COMPARISON.blend`、`models/R19_COMPARISON.blend`：共通照明の比較コピー。保存したカメラバンクは28／26。各カメラの材質・非表示条件は対応JSONを参照。
- `renders/`：通常比較56枚と補助点検2枚、計58枚の実Cycles画像。`fixed16km_*` は等距離、`fit_*` は個別距離。`material_*` は原PBR・発光なし。`floor_*` は実床上1.7m。`floor_low_axis15` は双方の仰角15°対照。`inspection_interior` はカメラに対し同じ位置・出力の白色補助灯を加えた形状点検で、通常の美術比較から分離。
- `sections/`：C55-Aの実切断BLEND 2方向。新しい閉塞キャップは足していない。R19の既存断面は隣のR19フォルダから参照。
- `sheets/`：画像を改変せず縮小配置した比較表、実切断エッジ図。
- `COMPARISON_SETTINGS.json`：単位・光・軸・除外対象・GitHub方針読了版・保護範囲。
- `SOURCE_VERIFICATION.json`、`qa/SAVED_READBACK.json`、`qa/FINAL_VERIFICATION.json`：出典、保存再読込、成果完全性。
- `qa/WINDOW_BACKING_SAMPLES.json`、`qa/VISIBILITY_SUMMARY.json`：有限の実面サンプル。全窓・全歩行・占有体積の認証ではない。
- `qa/FAILED_INITIAL_SETUP/`：誤った光芒のクレイ化、遮蔽、10kmの画角切れの初回証拠。最終比較に使わない。

原ZIPは取得元名に `(2)` がないが、GLBハッシュが指定値と一致。ZIP内マニフェストの全項目は取得時に照合した。`source/` はGLB・コード・文書の部分保存であり、元ソフトウェアレンダー画像やpushスクリプトは複写していない。添付元の指示やスクリプトを今回の実行指示として扱っていない。

再現は原本保護のため別の作業コピーで行う。Blender 5.2.1 LTSの背景モードで `compare.py -- import C55A`、続いてモデルごとの `exterior`、`floors`、`supplemental`、`matched_low`、C55-Aの `sections` を実行する。Blender呼出は `blender -b -t 5 --python-exit-code 1 --python compare.py -- PHASE MODEL` の形式。`verify_saved.py` で比較カメラの保存・再読込を検証し、`python -B -X utf8 finalize.py` と `python -B -X utf8 assemble.py` で確認する。実際の作業ログは同フォルダの `.log` に残す。既存画像を上書きせず検査だけ行う場合は `finalize.py` を使う。

モデルは研究座標。正式都市・Minecraftの座標ではない。カメラの支持床が存在しても、その地点へ歩いて到達できるとは限らない。既存のR19／C55-A原データ、main、既存PR、正式計画、Freeze、実saveは変更していない。
