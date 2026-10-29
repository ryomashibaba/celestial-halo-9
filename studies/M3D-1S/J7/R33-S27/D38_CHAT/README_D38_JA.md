# HALO-9 D38 — Blenderネイティブ真正性ゲート（研究用）

## 目的と実績
D37の旧`d37_glb_crosscheck.py`は、`.blend`が存在しなくても、コピーした参照GLB・空の再読込JSON・偽の実行報告により`real_blender_native_reopened: true`を出力して成功終了してしまう。この**真正性の欠陥をD38で修正**した。

`d38_negative_audit.py`はD37の旧誤PASSを隔離した一時ディレクトリで再現し、D38の8負例検査を実行する。D38の`d38_native_gate.py`は、検証済み出力ファイルの存在・SHA256・実Blenderファイルのヘッダー・再読込記録の内容・実際の`bpy`での第三プロセス再読込・Shape Key・保護メッシュ・GLBの頂点集合/面数/面積/体積を検査する。真正のBlenderを使えない場合、絶対にネイティブPASSを出さない。

## フォルダー構成
GitHub上ではD37依存コードを`studies/M3D-1S/J7/R33-S27/D37_CHAT/`、D38修正コードを同じ親にある`D38_CHAT/`へ配置。GitHub Actions workflowはリポジトリ直下`.github/workflows/d38-blender-proof-regression.yml`にある。研究ブランチだけで動作する予定のpushトリガーを使用し、デフォルトブランチにないworkflow_dispatchでの手動起動は前提としない。

## Chat側で実行済み

```shell
python studies/M3D-1S/J7/R33-S27/D38_CHAT/d38_negative_audit.py
```

別の一時ディレクトリにD37・D38最小コードをコピーした独立検証でも、旧コードの偽PASS再現とD38の8負例拒否を確認。`d38_runtime_preflight.py`はbpy未導入のChat環境で明確なエラー終了を確認。

## Blenderでのみ実行できるステップ
WorkflowはPython 3.11上に公式`bpy==4.5.15`を導入し、`d38_runtime_preflight.py`でglTF入出力演算子を検証した後、D37の原本生成→独立参照GLB生成→本物の`.blend`保存→別プロセス再読込→`d38_native_gate.py`の第三プロセスによる照合を実行する。

**Chatにはbpyが存在せず、`.blend`本体を生成していない。GitHub Actionsの実行結果もこの作業時点では未確認。** Run ID、ジョブログ、成果物に基づかずに「BLENDER PASS」と表現してはいけない。`d38_native_gate.py`の未実行を「環境の検査が終わった」と言い換えない。

## 適用範囲の制限
今回は3個の中立メッシュからなる技術素材であり、建築案を制作・採択していない。形態美術、居住機能、公共動線、構造、法規、安全、CITY MASTER 3D、Minecraft施工の認定とは無関係。M247-C保護、main変更なし、Work未使用、Minecraft施工HOLD。
