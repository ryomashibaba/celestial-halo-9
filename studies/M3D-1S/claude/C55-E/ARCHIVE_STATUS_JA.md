# Claude C55-E 原本アーカイブの保存実績と未完了項目
**更新基準：2026-10-30 JST／保存場所：独立 `archive/claude-c55e-source-and-evidence-20261029`／ART HOLD**

## 何が実際に保存されたか
- C55-E ZIP内の **制作・再レンダリング・検証・失敗記録・状態説明など31個のテキスト原本**を、`studies/M3D-1S/claude/C55-E/` に原文で保存。
- 実レンダー由来の **EA/EB 6視点比較の縮小JPEG** `preview/C55E_EA_EB_OVERVIEW.jpg` をGitHubの実バイナリとして保存。
- オリジナル **EA GLBの先頭5個**（2MiB×5＝10,485,760 bytes）を `models/parts/EA_000.bin` ... `EA_004.bin` として、元の生バイトのままGitHub保存。残りEA_005〜016とEB_000〜025は**未保存**（この文書作成時の確認）。
- **厳格な復元・ハッシュ照合スクリプト** `models/RESTORE_ORIGINAL_GLB.py` と、`models/ORIGINAL_BINARY_MANIFEST.json` を登録。スクリプトは欠損があれば失敗終了し、「復元成功」と虚偽表示しない。
- **完全なC55-E成果ZIP（89,829,946 bytes; SHA-256 `57448ad64fb4864542ff5cb8448d33a42657ef956e17b6bb7d37656257d0702b`）とGit bundle（C55-C→D→Eの履歴）**は、同一ChatGPT利用者のファイルライブラリ
  `/CELESTIAL-HALO-9/C55E-Research-Archive/` に別々に保存。元のZIP内部の `MANIFEST_SHA256.txt` **70/70件 SHA-256一致**を確認。ライブラリバックアップとGitHubアーカイブは**別の保管場所**であり、このリポジトリだけで全原本を復元可能と主張してはならない。

## 不足と原因
- **GitHubでは2個のGLBは未完成。** EAは17分割中5つだけ、EBは26分割中0。したがって「全GLBのGitHub保存PASS」は **FALSE**。GitHubへの転送中、ChatGPTファイル連携の一時コンテナが `container_session_expired` となり、追加のバイナリ転送片をファイル連携が取得できなくなった。ZIPとbundleはLibraryで保護されているため原本消失ではない。
- Git bundle本体（数百MB級の履歴保存ファイル）はGitHubにアップロードできていない。bundleの独立したコミット履歴を、既存mainやGPT系ブランチへ直接混ぜない。
- C55-Eの実Blender/Cyclesレンダー、編集可能BLEND、BVH自己交差完全検査はもともと未実施。本アーカイブが技術・美術合格を追加証明することはない。
- このGitHubブランチにある31ソースは**C55-Eの収録部分**。C55-C/Dの全原本と履歴は別途Libraryのbundleと先行研究ファイルを参照する必要がある。

## 後で全バイナリをGitHub保存する際の安全な手順
1. ライブラリ保管のZIPとbundleのSHA-256を再確認。ZIPを開き `claude_c55e/model/C55E_EA_terra_turn_open_lattice_v2.glb` と `.../C55E_EB_yori_well_v3.glb` を得る。
2. 他系列の HEAD が変わっていないか確認し、**このClaude専用archive研究ブランチだけ**に続きの `models/parts/EA_NNN.bin`（EA_005〜016）と `EB_NNN.bin`（EB_000〜025）を2,097,152バイトずつ保存。既存EA_000〜004は変えない。
3. `python studies/M3D-1S/claude/C55-E/models/RESTORE_ORIGINAL_GLB.py --verify-only` で双方の部品数・元GLBヘッダー・元SHAを検証（**不完全なら終了コード1が正しい**）。
4. `--output-dir <隔離フォルダ>` を指定して元GLBを復元、ファイルサイズ／SHAを再照合。その後、別ツールでBlenderで開いて幾何・見た目を確認（未実施ならBlender PASSと記録しない）。
5. 原本のGit bundle全体をそのままGitHubに重複保存する必要が本当にあるか、履歴のimport・GitHub Release資産・Git LFS等の容量/管理方法を**別途検討**。いずれもmainへの直接マージは禁止。

## 美術・運用状態
- Claude C55-E：**ART HOLD**、E-Aの現外観REJECT、E-Bは巨大ボイド／多方向居住原理のみ継続HOLD。C55-Fは別研究として独立。
- main/Freeze・GPT/Work本線には一切変更を加えない。正式中央美術採択0件、CITY MASTER 3D FIRST維持、Minecraft施工HOLD。
- 本ファイルは2026-10-30の事実のスナップショットである。後続研究はGitHubの現HEAD・ライブラリバックアップと照合してから最新状態を更新する。
