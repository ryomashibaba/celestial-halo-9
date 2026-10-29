# D30 — 実GLBへの曲線・斜行空洞編集（隔離研究）

## 対象・目的
D29の軸に平行な箱穴とは異なり、非直方体で水密な研究用GLBに曲線通路、公共空洞、斜め天窓を実三角形として作る。
これは約10km級 CITY MASTER 3D の正式形状ではなく、Minecraft施工にも一切使用しない。

## 起動（Python 3.13系）
依存: `pip install numpy trimesh vtk scipy scikit-image pillow fastapi uvicorn`
既に同梱された `D30_BASE.glb` と3つの `D30_PLAN_*.json` を同一フォルダに置く。

```
python d30_freeform_csg.py D30_BASE.glb D30_PLAN_TUNNEL.json out_tunnel.glb
python d30_freeform_csg.py D30_BASE.glb D30_PLAN_ROOM.json out_room.glb
python d30_freeform_csg.py D30_BASE.glb D30_PLAN_SKYLIGHT.json out_sky.glb
python d30_independent_qa.py
python d30_repro.py
python d30_render.py
```

- JSONの `baseline_sha256` に一致する場合のみ実行。出力先の既存ファイルは上書き拒否。
- D30は検証した3段階の固定空洞設計のみ対応。自由入力の任意3DメッシュのCSG保証はない。
- 実GLBレンダリングはVTKのオフスクリーン処理。D28/D29の `d28_visual_workbench.py` と `d29_render.py` を補助コードとして同梱。
- WindowsのBlender GUI／MCP統合、全都市共通座標、街区生活動線、現実の構造安全は未検証。

再構築用fixtureの生成例：`python -c "from d30_freeform_csg import source_glb; open('D30_BASE.glb','wb').write(source_glb())"`。保存GLBのハッシュが同梱PLANと一致することを確認する。
