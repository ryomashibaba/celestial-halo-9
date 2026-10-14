# M120 開始・M119全量引き継ぎ

1. まず `M119_REPORT_JA.md` を読む。
2. `data/M117_USER_READONLY_ATLAS.json` はユーザーが実ワールドから採取したレビューコピーの**不変の実データ**。上書き・施工用変換しない。
3. 2案の独立JSON：`data/M119_A_CROWNED_MERIDIAN.json`、`data/M119_B_FRACTURED_SKY_TERRACES.json`。提案はすべて `approved_for_world_write:false`、`collision_certified:false`。
4. `source/m119_city_model.py` で再生成、`source/render_m119.py`、`source/render_m119_sections.py`で四枚の比較／内部図を再生成できる。`python -m unittest discover -s tests -v` で5検証。
5. M119形状は**完成建築ではなく造形模型**。`relative-H↔real Y`はまだ未確定。現実の既存建築と新図案は重複し得る。
6. Bは研究優先だけ。Frozen408/public959/SB09 upper/SB13 3x4/88 voids/道路/公園・世界への書込はすべてHOLD。正式施工対象は未登録。
7. M120の最大効果は、旧建築を守りながら最終都市らしい高品質造形と実歩行できる公共空間へ進むこと。繰り返す細かな環のQAより美術・都市構造を優先。
