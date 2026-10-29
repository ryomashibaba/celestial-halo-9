# CELESTIAL HALO-9 / R33-S27-D37: Blender native gate

## 目的・絶対条件

D35/D36の不採用形状を美術採択しない。**今回の対象は中立な技術検証モデル**であり、中央M247-C・CITY MASTER 3D・Minecraft施工にはいっさい反映しない。コードだけがあっても「Blender実機PASS」と言わない。

## Chat内で実際に通過した工程

1. `python d37_prepare.py /path/to/input` で、水密な3メッシュのGLBとソースSHA固定の編集プランを生成。
2. `python d37_offline_reference.py input/D37_EDIT_PLAN.json input/D37_REFERENCE_EDIT.glb` で非Blender参照GLBを作成。
3. `python d37_local_gate.py` で同一出力の別プロセス再生成、10種類の不正計画の拒否、Python構文チェックを実行。
4. `python d37_render_real_glb.py` で実GLBのBASE/EDITを6視点ずつ描画。

ChatではBlender実行ファイルも`bpy`モジュールもありません。このため`.blend`は**生成していません**。

## Blender実機でのみ検証できる工程

研究ブランチ内の `.github/workflows/d37-blender-native-gate.yml` を使い、GitHub ActionsのUbuntu/Python 3.11に公式 `bpy==4.5.15` をインストールし、以下を順番に実行する。

1. `d37_blender_execute.py`：既存GLBをBlenderに読み込み、ベース＋編集Shape Keyを持つネイティブ`.blend`を保存。続いて**別の焼き付けたメッシュ**をGLBとして書き出す。取り込んだ元GLBや保護メッシュを編集しない。
2. `d37_blender_reopen.py`：別のPythonプロセスで`.blend`を開き直し、Shape Keyと保護メッシュを再確認。
3. `d37_glb_crosscheck.py`：第三のプロセスがBlender出力GLBとPythonで生成した独立参照GLBの頂点位置を照合。並び順が異なっても最近傍距離0.05m以内、保護メッシュの改変なし、対象形状が変化していることを条件にする。
4. すべて通過した場合のみ**Blender 4.5対応環境での限定TECH PASS**。WebGL UI、Blender GUIでのマウス操作、作画品質、都市連絡路の通行、安全性は別途未検証。

GitHub上でCIが実行できない、PyPIインストールに失敗、Blenderがクラッシュ、GLB位置一致を満たさない等の場合は**TECH FAILまたはNOT RUN**であり、後から成功を推定しない。

## Windows 11で使う場合

Blender本体（GUI可）と、対応するPython環境が利用可能なら、`blender --background --factory-startup --python-exit-code 12 --python d37_blender_execute.py -- ...` と同じ動作を実装するには `bpy` 取り込み環境に依存するため、今回の入口は Python 3.11 + `pip install bpy==4.5.15 numpy trimesh scipy` を推奨する。`python d37_blender_execute.py INPUT/D37_EDIT_PLAN.json OUTPUT_NEW_DIRECTORY`、`python d37_blender_reopen.py ...`、`python d37_glb_crosscheck.py INPUT/D37_EDIT_PLAN.json OUTPUT_NEW_DIRECTORY INPUT/D37_REFERENCE_EDIT.glb` を順に実行する。

**ユーザーへの実行要求ではない。** 研究ブランチの自動実行を優先し、手作業を増やさない。正式都市成果への取り込みには別途アートゲートが必要。
