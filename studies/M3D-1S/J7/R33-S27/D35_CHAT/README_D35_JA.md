# R33-S27-D35 研究ZIP（Chat完結）

研究用、正式採択なし。Minecraftへの施工禁止。

## 生成・確認手順

Python環境：numpy, scipy, trimesh, vtk, pillow（確認時にはそれぞれ適切なバージョンが導入済み）。

```bash
python d35_civic_urban_section.py
python d35_independent_qa.py
python d35_render.py
python d35_gate_and_replay.py
```

全工程は同じフォルダー内へ成果物を出力する。D35_GATE_AND_REPLAY.jsonに限定的な判定を保存。`D35_BASE_REVERSE_4VIEW_COMPARE.jpg` で実GLB 4視点を比較する。`D35_..._8VIEW_REAL.jpg` は各8視点の比較画像。

**制約**：RAMP勾配過大（43〜69%）／居住室の実体未完成／高架接続の連続通行未証明／ART REJECT。描画結果はあくまで3D読込画像。正式都市マスター、基礎構造、建築安全、Blender/Work操作なし。
