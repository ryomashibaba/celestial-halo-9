# HALO-9 — CURRENT STATUS (rolling)
**確認基準：2026-10-23 JST（PR #25マージ済み／M3D-0 PC診断結果受領後）**
**性質：随時更新。長期憲章や完成基準を上書きしない。**

## 最重要状態

- **最終目的**：約10km級の単一超未来文明都市をMinecraft Java Editionに完成。
- **現在の最上位設計工程**：CITY MASTER 3D FIRST（正式施工前に、一般建物内部だけを例外として全都市の詳細編集可能3Dを完成）。
- **Minecraft正式施工**：**HOLD**（承認なし）。
- **正式な中央建築美術採択**：**0件**。
- **保護する正式研究方向**：M247-C 浮断天核（α双殻浮断＋β斜裂天脊）。具体的な完成メッシュは未採択。
- **過去の長期本線**：M247-B2-39 Stage 12Wは美術REJECT、Stage 12Xは計画のみ（完了と主張しない）。
- **A–D研究**：G7まで提出完了。現在のG7試作はいずれも精密化を止め、アーカイブ・一時停止。
- **現在の第一実験**：M3D-0 Windows診断Gate 0AはPASS（既存ソフト・設定の存在確認のみ）。Blender上のMCPサーバー起動・AI接続・実3D編集は未実施。次に小規模隔離シーンで視覚反復能力を検証する。
- **ユーザーPC実測（2026-10-23）**：Blender 5.2標準パスFOUND、addon 5.2 FOUND、uvx FOUND、Codex設定とBlender MCP参照FOUND、Blender NOT_RUNNING、9876 NOT_LISTENING。**存在のみ確認**。未起動時の非待受は異常でない。秘密情報や絶対パスは保存していない。
- **Work**：都度事前相談・ユーザー明示承認。
- **有料外部コンセプトアーティストへの外注**：ユーザー意向で実施しない。
- **GitHub正式方針文書**：PR #25は2026-10-23にmainへマージ済み。正式入口は main/docs/policy/START_HERE.md。初版の旧状態説明の修正はDraft PR #26で提案中（まだmain未反映）。
- **新技術の研究評価**：UltraはUnreal Engine + PCGを都市全体統合の強力な候補、Blenderを専用造形候補、Houdiniを必要時の追加候補と評価。公式資料でUnreal 5.8のPCG/MCP等の機能を確認。**Unreal/Houdiniの正式採択・実機検証は未実施**。詳しくは studies/M3D-0/ULTRA_PRODUCTION_STRATEGY_REVIEW_2026-10-23.md。

## GitHub確認済みHEAD（2026-10-23現在）

Repository: ryomashibaba/celestial-halo-9

| Branch | HEAD | Status |
|---|---|---|
| main | a2f88995eee8d10ee4830dbdf33ccb9c0790de8f | PR #25で正式憲章・詳細完成基準を追加済み |
| art/a | 1eb3121df4f0ede679c201cb40d611409309511e | A2-G7 HOLD。共有公共屋根原理を保存、現巨大アーチ形状は精密化禁止 |
| art/b | bf8c802fbb7b6521f85d050ede837cc3e711c166 | B2-G7 BOTH_REJECT |
| art/c | 4c55052f5ec3c2037f0b3ad83a8f372dff1199bf | C2-G7 G6最終＋新N1 REJECT |
| art/d | 5ec09bbed91ac7935fb035d03fff63b3da9b0bde | D2-G7 生息冠HOLD。季節差あり、樹木/花冠に見えるリスク |

上記は確認した当時の値。今後の各新しいセッションでは必要な対象ブランチのHEADを再確認する。ここに書かれたSHAを永続不変の「最新」と呼ばない。

## Next responsible actions

1. **完了**：PR #25をmainへマージ。ChatGPTプロジェクト共通指示もユーザーが設定済み。
2. **完了／存在検査**：M3D-0読み取り専用CMDをユーザーPCで実行し、Blender 5.2・5.2 addon・uvx・Codex MCP設定候補を検出（Gate 0A PASS）。実測の機密情報を除いた記録は studies/M3D-0/ENVIRONMENT_DIAGNOSIS_2026-10-23.md。
3. **次のBlender操作（未実施）**：Blender 5.2を新規Generalシーンで起動 → MCP addon UIを確認 → localhost:9876を安全に起動 → 旧診断の[6/6]で待受を確認。設定の初期化・再インストールは不要な限り行わない。
4. **Gate 0C/0D（未実施）**：ユーザーが別途許可した場合だけ、隔離された新規3DシーンでAIの読取り・局所編集・復元・6視点レビューを検証。
5. **技術研究（未採択）**：Ultraの提案に基づき、実3D美術の改善M3D-1Aと完成代表経路M3D-1Bを先に実証。Unreal PCG統合はその後の候補、Houdiniは必要な場合のみ検証。
6. 完成基準の緩和は行わず、美術的成果が乏しければ手法を見直す。正式Minecraft施工は独立承認まで禁止。

## 更新ルール

定常的なステータス更新では**このファイルだけ**と、必要に応じてDECISION_LOGの末尾を更新。PROJECT_CONSTITUTIONとCITY_MASTER_3D_STANDARDを毎回書き換えない。

毎回記録すべき内容：確認日時/実測HEAD/本当に存在する成果/美術採否/未検証点/次の行動/承認必要箇所。推測を実績として記録しない。
