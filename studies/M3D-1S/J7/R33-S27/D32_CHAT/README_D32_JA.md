# D32研究成果：閲覧と再現

1. ZIPを展開し、`D32_ART_GATE_BOARD.html` をブラウザーで開くと、実GLBから書き出したA/Bの同じ8視点画像を切り替えて比較できる。画像とHTMLは同じディレクトリ内に置く。
2. `D32_4VIEW_A_B_MACRO.jpg` または `D32_8VIEW_A_B_COMPARE.jpg` は一括比較画像。**画像は実GLBの描画だが、研究モデルの建築は美術REJECT**。
3. 生成再現には Python、`trimesh`、`numpy`（描画に `vtk`、`Pillow`）を使用。
   - `python d32_urban_art_gate.py` → 2実GLBと `D32_GEOMETRY_EVIDENCE.json`
   - `python d32_render.py` → 同一8カメラ画像と比較JPG
   - `python d32_art_risk_audit.py` → 実GLBの経路段差・プリズム警告
   - `python d32_review_board.py` → 比較HTML
4. ローカルでの「HTMLファイルを開く」操作は利用環境によって制限される場合がある。D32のChromium試験では隔離実行環境のファイルURLがブロックされたため、インライン画像のテストで表示・切替を確認した。閲覧用リンクをライブWeb公開したという主張はしない。
5. 実GLBは正式な都市本体ではない。すべて独立研究座標、Minecraft施工厳禁。A/B ART REJECT、地上経路は3m段差でTECH FAIL。
