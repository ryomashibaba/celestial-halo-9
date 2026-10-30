# Claude C55-E — 原本アーカイブ最終保存報告
**確認日：2026-10-30 JST／独立アーカイブ／中央美術 ART HOLD・正式採択なし**

## A. GitHubに実際に存在するもの

保存ブランチ：`archive/claude-c55e-source-and-evidence-20261029`

- 元の **C55-E制作・検証・失敗記録・研究文書のテキスト31ファイル**を原文で保存。メインソースは `code/` にあり、影マップ修正前のコードと修正後の比較も含む。
- 元の実レンダー由来の **EA/EB 6視点比較JPEG** `preview/C55E_EA_EB_OVERVIEW.jpg` をバイナリとして保存。
- **実GLB本体を、元バイトを変えずに2MiB分割で全件保存。** E-Aは `models/parts/EA_000.bin`〜`EA_016.bin`（17分割、計35,478,456 bytes）、E-Bは `EB_000.bin`〜`EB_025.bin`（26分割、計53,010,436 bytes）。**43/43の部品が存在し、欠落0。**
- 43部品それぞれについて、原本ZIPのバイト列から独立計算したGit blobオブジェクトSHA-1がGitHub上の実blob SHAと**43/43一致**。これにより、GitHubの各部品は元データをバイト単位で保持していると検証できた。**再結合後の最終ファイルをクリーン環境でGitHubからダウンロードして実行する工程は別途未実施。**
- `models/RESTORE_ORIGINAL_GLB.py` を使うと、43分割から元GLBファイルへ再結合できる。**元GLB全体のSHA-256、バイト数、GLBヘッダーが一致しない場合は異常終了**する。既存のファイルは上書きしない。
- `models/ORIGINAL_BINARY_MANIFEST.json` に正確な情報を保存。GLBはGitHubでは「.glb単独ファイル」ではなく**再組立て可能な原バイト分割**である。

## B. ライブラリに完全原本を二重保護
利用者のChatGPTファイルライブラリ `/CELESTIAL-HALO-9/C55E-Research-Archive/` に次を保存。

| 原本 | サイズ | 原本SHA-256 |
|---|---:|---|
| `C55E_claude_research_payload.zip` | 89,829,946 bytes | `57448ad64fb4864542ff5cb8448d33a42657ef956e17b6bb7d37656257d0702b` |
| `C55E_research_branch.bundle` | 169,917,412 bytes | `83abd4ecd191d3ecb66a81c9014e9385844b046c7546b1663ed1b86c8399114f` |

ZIP内 `MANIFEST_SHA256.txt` の元ファイル検査 **70/70一致**。Git bundleに対してGit自身の `git bundle verify` による完全履歴検証 **PASS**。bundle内の最終refは `refs/heads/claude/c55e-macro-research`／`f4155c293e2905e7b7910b34d244a5e80cc16bdd`。

**未保存の範囲：** Git bundle本体および完全ZIPを、それぞれGitHubリポジトリに単独ファイルで保管することは未実施。bundleのC55-C/D/Eの独立履歴を、正式GitHub `main` に輸入・マージする操作も未実施。**Libraryへの保存とGitHubへの直接保存は区別する。**

## C. 復元と検証
```bash
git switch archive/claude-c55e-source-and-evidence-20261029
python studies/M3D-1S/claude/C55-E/models/RESTORE_ORIGINAL_GLB.py --verify-only
python studies/M3D-1S/claude/C55-E/models/RESTORE_ORIGINAL_GLB.py --output-dir ./restored-c55e-models
```
想定される最終GLB SHA-256：
- EA `42c2cbd1c51389e55d57b6c2f998a8ecce5219454382a99c16f3c9672024f6d9`
- EB `01ea7a7f5865c569ac41d1e1946cfa366125872f83a058d4759ab341d57b58e2`

外部で本格レンダリング・形状審査をするときは、同じ原本をBlenderで取り込み、C55-Eの独自ラスタライザにしか存在しない表現とジオメトリを区別すること。

## D. 現状と制約
- C55-E ART HOLD。E-Aの現在の貝殻的外観はREJECT、E-Bの巨大ボイドと多方向居住原理だけ研究継承。**中央の正式美術採択0件**。
- 元成果は **Blender/Cycles未実行・実BLENDなし・全自己交差未検査**。アーカイブ保全は美術PASS/技術PASSを意味しない。
- `main`、Freeze、GPT/Workの研究ブランチ、Minecraft本番ワールドには書き込んでいない。CITY MASTER 3D FIRST／Minecraft施工HOLDを維持。
- このステータスは保存時点のスナップショット。今後別の担当がClaude C55-F以降へ進んでも、その研究をこのアーカイブから自動的に置き換えない。
