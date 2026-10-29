# D34研究用3D公共セクション — 再現手順

目的：3層の公共ギャラリー、室内開口、傾斜路、地上からの公共接続を保存GLBで検証する。**完成都市ではない。施工禁止。**

## 実行

Python 3.13系の隔離環境で、`pip install trimesh numpy vtk pillow scipy` の後、以下を実行する。

```sh
python d34_civic_section.py
python d34_independent_qa.py
python d34_negative_tests.py
python d34_route_graph.py
python d34_replay.py
python d34_render.py
```

実GLB `D34_CIVIC_THREE_LEVEL_REAL.glb` と実レンダー `D34_01_south.png` ... `D34_09_mid_crossing_human.png`、比較図 `D34_9VIEW_REAL_CONTACT.jpg`、QA JSONができる。マニュアルの施工操作、Minecraftワールド編集は一切行わない。

`d34_negative_tests.py` は障害物、傾斜路欠落、入口閉塞の3つの壊れたGLBも生成し、**検査がFAILを検出する**ことを確認する。`d34_replay.py` は独立プロセスでの同一GLB生成を確認する。

## 意味・制限

- 各階の公共室は空洞のある別メッシュ壁・床・屋根で作成。居住設備はない。
- 本検査は5,555地点の床支持と2高度のAABB干渉を調べるが、実地歩行・法規・構造計算とは異なる。
- 9視点は保存済みの同一GLBから描画している。CGイラストであり実3Dであると偽っていない。
- ART REJECT。正式中央建築採用0。CITY MASTER 3D FIRST。Minecraft施工HOLD。
