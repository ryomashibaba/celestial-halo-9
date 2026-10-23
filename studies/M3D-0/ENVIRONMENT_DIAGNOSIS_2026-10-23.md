# M3D-0 Windows環境診断 — ユーザー実測結果

**記録日：2026-10-23 JST**
**入力：HALO-9メインチャットでユーザーが提供したRUN_M3D0_CHECK.cmdの6項目の標準出力**
**機密配慮：ローカルの個人名・絶対パス・Codex設定内容・トークン等は保存しない。**
**判定：READINESS_DETECTED（利用候補あり）／MCP_CONNECTEDではない。**

## 1. 実測

| 項目 | 実際の表示 | 判定と限界 |
|---|---|---|
| [1/6] Blenderプロセス | NOT_RUNNING | 診断時に起動していない。異常ではない |
| [2/6] Blenderパス | NOT_IN_PATH / BLENDER_5_2_STANDARD_PATH_FOUND | 標準のBlender 5.2配置候補を発見。PATHに無くても支障とは限らない |
| [3/6] 旧MCP addon | ADDON_5.2=FOUND; 5.3,5.4,4.5=NOT_FOUND | 5.2用ファイルを検出。Blender内で有効化されているかは未検証 |
| [4/6] uvx | UVX_FOUND_IN_PATH / UVX_USER_LOCAL_FOUND | 実行ファイルを検出。MCPサーバーとの互換・接続は未検証 |
| [5/6] Codex設定 | CODEX_CONFIG=FOUND / BLENDER_MCP_REFERENCE=FOUND | 設定ファイルと参照文字列の存在。現在その設定が有効とは未検証 |
| [6/6] TCP 9876 | PORT_9876=NOT_LISTENING_OR_NOT_VISIBLE | Blender停止中なので自然。接続に失敗したという判定はしない |

## 2. 確認されたこと／確認されていないこと

**実際に確認されたこと：** 旧Blender 5.2本体候補・旧MCP addonのファイル・uvx・Codexの設定候補が現PC上にある。新規インストールより既存環境の復旧を優先する根拠がある。

**未確認：** Blender UIの正常起動、addon有効状態、Blender内のMCPパネル、ポート9876の起動、MCPクライアントとの通信、3Dメッシュの読書き、複数視点レンダー、視覚的な改善、Unreal Engineの実インストール・動作状況。

**実施していないこと：** Blenderのインストール・更新・設定書換え、既存BLENDモデル編集、Minecraftワールド操作、Unreal導入、人工的なQA結果の生成。

## 3. 最短の次手順（Gate 0B）

ユーザーがBlender作業を再開できるときだけ、**Blender 5.2を普通に起動**し、新規Generalシーンで3Dビュー右側のNパネルに旧MCP UIがあるか確認する。存在するなら既存addonの「Start MCP Server」または旧UIの対応する開始操作を試す。

- 旧MCP接続先が localhost:9876 かを確認。無断で別のネットワークインターフェースへ公開しない。
- Blenderを起動したまま既存の読み取り専用CMDの[6/6]を確認。
- LISTENINGなら **MCP SERVER_STARTED** と判定。AIクライアントと通信できることの証明は別ゲート（0C）。
- 未検出ならBlenderのEdit > Preferences > Add-onsからMCPの有無・有効化を確認。再インストール・設定消去は最後の手段。
- 9876待受が見えない場合も、addonの無効化／古いUI／Windows権限／別ポート等を個別診断するまで原因未確定。

**安全：** 原本BLEND、canonical/staging、Freeze、正式Minecraftワールド、main、art/a〜dへの書き込みは禁止。WorkまたはローカルComputer Useはユーザーの新しい明示承認があってから利用する。

## 4. M3D-0全体の審査状態

- Gate 0A（既存環境の検出）：**PASS — presence only**
- Gate 0B（Blender addonのサーバー起動）：**NOT_TESTED**
- Gate 0C（AIクライアントの接続・隔離シーンでの操作）：**NOT_TESTED**
- Gate 0D（実3Dの局所的修正・全視点の見直し）：**NOT_TESTED**
- M3D-1（難しい建築の美術的な改善能力）：**NOT_TESTED**

本資料は環境診断の履歴であり、制作手法としての採択を意味しない。正式な全域詳細完成基準は `main/docs/policy/CITY_MASTER_3D_STANDARD.md` から変更しない。
