# A2-G6 — 交庭聖都の実メッシュ研究

**BLOCKOUT_3D / 美術HOLD / 正式採択なし**

共有公共施設を上下の生活都市が同じ境界として使う断面を実3D化した。初期2案の比較と主質量の再設計を行ったが、遠景の棚状反復を解決できていない。次の細密化へ進む推奨案ではない。

- [研究報告](REPORT.md)
- [比較一覧](comparison.png) / [六つの外観](six_views.png)
- [人間視点](renders/07_human.png) / [公共広間](renders/08_public_hall.png)
- [生活地区の俯瞰](renders/09_pair_aerial.png) / [共有断面](renders/10_pair_section.png)
- [中央建築GLB](selected.glb) / [Blenderファイル](selected.blend)
- [独立したGLB検証](mesh-qa.json) / [座標・カメラ・形状記録](geometry-record.json)
- [ローカル閲覧ページ](review.html)

再生成：Blender 5.2.1で `build.py -- compare`、続いて `build.py -- selected` を実行（Blenderの `--python` 引数を使用）。外部アセット不要。`qa.py`と`package.py`はPython、trimesh、numpy、Pillowを使用する。

GLBは中央建築のみ。BLENDの概念背景は`CONCEPT_CONTEXT_10KM_NOT_W0`コレクションに分離。背景の6地区は座標未登録の尺度用構想であり、正式W0やH1〜H6を再現していない。M204／M207の推測統合は行わない。

単画像を元解像度で収録。一覧シートだけを検証資料にはしない。画像は同じ実GLBの再読込から描画し、断面のみ同じ形状のコピーを切断している。
