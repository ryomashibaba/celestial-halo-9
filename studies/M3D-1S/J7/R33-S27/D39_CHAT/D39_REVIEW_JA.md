# D39 — GLB座標軸とBlenderネイティブ証拠の独立照合

基準: D38 `62a02e1e85c3ea038776b5967960ae16d05ac9ee`。この研究ブランチの結果は技術限定であり、美術の正式採択ではない。

## D37・D38の真正Actions失敗

- D37 run 40842844700: Blender保存・再読込成功、出力GLBメッシュ名の不一致で最終FAIL。
- D38 run 40844381800: Blender 4.5.15の実行、.blend保存・独立再読込成功、Shape KeyとglTF参照形状の差1109.1181mで最終FAIL。
- 原因仮説: trimeshで記録したGLB座標（glTF Y-up）と、bpyのBlender Z-up座標を比較したこと。同時にBlenderの元メッシュデータ名が衝突し、GLB出力名が変わる問題。
- 今回は固定の右手系回転 (x,y,z)glTF -> (x,-z,y)Blender を双方の独立コードで適用し、変換前後のBasisとShape Keyを明示検証する。
- Blender GLB書き出しでは元のオブジェクト・メッシュデータの名前を退避し、出力メッシュ名を実際に維持する。
- 新ワークフローは実Blender処理・独立再読込・厳密な面積/体積/頂点/面数/保護メッシュ検証とD38の8負例をすべて維持する。
- CIの成功ログを実際に再確認するまで NATIVE TECH PASS を宣言しない。美術は NOT SUBMITTED、正式採択0件、Minecraft施工HOLD、main変更禁止。

## 成功判定

真正Actions runの各ステップ成功、保存済み.blend再読込、Basis軸誤差・Shape Key軸誤差 <=0.05m、出力GLBの全3メッシュ名一致、面積・体積・面向き・保護メッシュ・変形の全比較PASS。過去の偽PASSを回避するため、データの存在だけでは認定しない。
