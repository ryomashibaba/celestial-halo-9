# C55-E 成果物（Claude独立美術研究）
- `LATEST_STATE.md` 状態要約 / `ART_REVIEW_C55E.md` 審査 / `E1_FORM_PRINCIPLE_ANALYSIS.md` 形態原理分析 / `REJECTED_ITERATIONS.md` 失敗記録 / `NEXT_STEPS_AND_E4_POLICY.md` / `GITHUB_STATUS.md`
- `model/` GLB（E-A, E-B）— 材質は中性のみ。
- `renders/` 最終画像（EA_v2_*, EB_v3_*, 補正後C55C_*, D1e_*, COMPARE_*）。
- `code/` 生成・描画・検証コード（`core.py`は影反転を修正した版）。
- `validation/` 影反転テスト、GLB再読込・寸法・クリアランス。
- `input_references/` 入力ファイルのSHA-256と、前工程画像との対応。
再現：`python3 code/eb_well.py` → `code/ea_terraturn.py` → `code/final_render.py ea|eb` → `code/export_and_validate.py`（パスは/home/claude/c55e前提）。
