# M121 開始 — M120統合モデルを引き継ぐ

1. `M120_REPORT_JA.md`と`data/M120_NONCONSTRUCTION_AUDIT.json`を最初に読む。特に**130新規メッシュ中38が旧実材AABB重複候補**の点を確認。
2. `data/M117_USER_READONLY_ATLAS.json`は**実測資料として不変**、`data/M119_B_FRACTURED_SKY_TERRACES.json`はM119 B案原本。`data/M120_B_ARCHITECTURAL_SPINE_REVISION.json`は未承認の案。
3. `source/m119_city_model.py` → `source/m120_city_model.py`、`source/render_m120.py`、`source/m120_audit.py`の順で理解する。`python -m unittest discover -s tests -v`。
4. M120は**模型733メッシュ**で前より少し改善したが、**完成建築、正確な保護衝突検査、歩ける公開経路、施工図はない**。
5. 中央の提案歩行経路は10ノード、9セグメント、2本の未実装リフト。連続は数学的な端点一致のみ。入口の実位置・現実の道路・88空洞・リフト・交通機能は未承認・未検証。
6. M121の最大目標は、旧建築の保護レイヤー精査と**主役級の地上／内部の実スケールでの体験品質**。小さな環改善に戻らない。M120からの段階的巨大街区計画。
7. レビューセーブ`CH9_D6D_REVIEW_COPY`、もうひとつの`imagine`はどちらも書込禁止。正式施工先未登録。Freeze408/Public959/SB09/SB13 3x4/88 voids/道路・公園/M101比較基準/HOLD不変。
