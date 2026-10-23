# M3D-0 — Blender環境・安全な再利用準備

**研究用・読み取り専用診断／基準：2026-10-23 JST**

- 正式方針：必ず main/docs/policy/START_HERE.md を確認
- 目的：旧Blender MCP環境を再インストールせず再利用できるか診断
- **実際に完了**：ユーザーPC上で診断CMDを実行。Blender 5.2本体・MCP addon・uvx・Codex設定候補の存在を確認。詳細は [ENVIRONMENT_DIAGNOSIS_2026-10-23.md](ENVIRONMENT_DIAGNOSIS_2026-10-23.md)。
- **未実施**：Blenderアドオンの有効化・localhost:9876起動、MCP接続、AIによる3D編集、建築美術改善。
- **新しい技術の比較**：Ultraの独立評価と公式技術資料は [ULTRA_PRODUCTION_STRATEGY_REVIEW_2026-10-23.md](ULTRA_PRODUCTION_STRATEGY_REVIEW_2026-10-23.md) に記録。Unreal/Houdiniの採用決定ではない。
- 厳禁：Blender原本、Minecraftワールド、Freeze、M247-C正式原本の変更と施工

## 確認済みの過去履歴

2026-09-10〜09-15の以前のチャット記録では、Blender 5.2.1 LTS、uvx導入、Blender 5.2用MCPアドオン、Connected on port 9876の表示があった。後日、接続切断（WinError 10054）の報告もある。別のCG制作でBLEND保存の実績はあるが、HALO-9の複雑な建築造形をAIが視覚反復で改善できるかは**未検証**。

MCPの公式プロジェクトは新名称 mcp-for-blender を使用するが、旧uvx blender-mcpも使えると説明している。**この診断では更新・インストールを行わない**。
公式：https://github.com/ahujasid/mcp-for-blender

## 実施済み：ユーザー操作（Windows、原則1ファイルのみ）

1. GitHub上の RUN_M3D0_CHECK.cmd を開き、右上の **Download raw file（ダウンロード）** でWindowsのダウンロードフォルダへ保存。
2. 保存したファイルを**ダブルクリック**。管理者として実行しない。
3. 黒い画面に [1/6]〜[6/6] の診断結果が出る。画面全体のスクリーンショットをHALO-9メインチャットへ添付。
4. 何かキーを押して黒い画面を閉じる。

保存先以外の個人名やユーザーフォルダのフルパス、Codex設定の内容、トークン等は出力しない設計。**秘密情報を含むコマンドや設定の中身をGitHubに貼らないでください。** ファイル内容を事前に確認してください。Windowsがセキュリティ警告で停止した場合は、保護機能を無理に無効化せず、メインチャットで状況を伝えてください。

## 結果の読み方

| 表示 | 意味 |
|---|---|
| RUNNING | Blender実行中 |
| BLENDER_5_2_STANDARD_PATH_FOUND または FOUND_IN_PATH | Blender本体の発見 |
| ADDON_5.2=FOUND | 旧アドオンファイルが存在。アドオンが有効とは限らない |
| UVX_FOUND_IN_PATH または UVX_USER_LOCAL_FOUND | 既存uvxが利用候補 |
| BLENDER_MCP_REFERENCE=FOUND | 旧Codex設定にBlender MCPの記述がある可能性 |
| PORT_9876=LISTENING | 旧MCPサーバーの待受がある |
| PORT_9876=NOT_LISTENING_OR_NOT_VISIBLE | 未起動、またはポートを検出できない |

Blenderを起動していなければ、PORT_9876のNOT_LISTENINGは正常。アドオンが他のバージョンフォルダに入っていたり、Blender本体が標準外フォルダにある場合も未検出になり得る。**NOT_FOUNDだけで再インストールしない**こと。

## 実3D制作までの今後のゲート

- Gate 0A：Blender・アドオン・uvx・AIクライアントの実在を確認
- Gate 0B：localhost:9876接続を安全に確認
- Gate 0C：独立テストシーンを読み取り → 小さな実3D編集 → 保存・再読込 → レンダリング確認
- Gate 0D：複数視点を観察し、局所編集が適切に行われたことを検証
- Gate 1：M3D-1の美術実証。高品質建築への改善が実際に見えないなら方式を見直す

Gate 0C以降でWorkやローカルComputer Useを使う場合は事前説明と明示承認が必要。過去の承認は再利用しない。

## GitHub保護

この研究は独立した research/m3d0-blender-readiness-20261023 に保存。main、art/a〜d、正式ワールド・既存モデルを変更しない。個人端末の診断結果を許可なく公開GitHubへ保存しない。

次工程ではBlender 5.2の新規Generalシーンで旧MCPアドオンを起動し、ポート9876の待受を確認する。結果が未確認の段階では再インストールせず、AI接続・実メッシュ編集は別ゲートとする。
