# CELESTIAL HALO-9 ローカルWorkセットアップ報告

実施日: 2026-10-14（日本時間）。Chatを開発の中心とし、Workは今回のローカル環境整備を担当。

## リポジトリと取り込み

- 作業フォルダ: `C:\Users\ryoma\Projects\CELESTIAL_HALO9`、チェックアウト: `repo/`。
- GitHub: PRIVATE `ryomashibaba/celestial-halo-9`。接続機能で既定ブランチmainとPRIVATE属性を確認。
- 元のM121ブランチ: `design/m121-human-scale-civic-interiors`。
- 基準コミット: `87f208fe12c0a98d238d19bbcebf5aa2c718b23b`。
- 新規ローカルブランチ: `integration/local-work-m121-setup-20261014`。
- GitHub main: `e9a38f28ed55817369f36d77d5131bd3b305e100`（読み取りのみ）。
- PR #18: Draft / open / 未マージ。headは基準コミット、baseは `design/m120-monumental-spines-and-route-audit` / `37900d296b34b0d88300fad77b3b85e933926753`。既存PR列は変更していない。
- 完全ソース46件を `research/m121/upstream/` にバイト単位でコピー。既存generators、design、survey、governance、CI、基準ファイルは上書きしていない。
- コピー専用の `.gitattributes` で元データの改行変換を無効化。検証ツール、テスト実行ツール、説明書と標準ライブラリ環境指定を追加。
- 差分は追加ファイルのみ。原本にはCRLF atlasと既存末尾空白が含まれるため、Gitの空白チェック警告を修正せずバイト保存を優先。新規作成した説明・検証ツールの空白チェックは別途実施。
- push / merge / PR更新 / 履歴書換えは実施していない。GitHubとChatへの同期は保留。

## 原本照合

元ZIP: `archives/CELESTIAL_HALO9_M121_HumanScale_Civic_Interior_M122_LocalWork_Setup_Handoff_NONCONSTRUCTION.zip`（6,338,295 bytes）。SHA256:

`75eaac00a897afc8b322d61b124a198f9e6de72a07445ec93ce73dd555cdeece`

- M121 manifestの45/45件: SHA256・サイズ一致。
- ZIPの46/46メンバー: CRC正常、展開済み原本と完全一致（manifest自体を含む）。取り込み先も一致。
- M119継承manifest: 16/16件一致。
- M120継承manifest: 非キャッシュ29/29件一致。manifest自体を加えた30件もM121 manifestで一致。旧 `.pyc` 5件は設計どおり対象外。以前のローカル準備で残ったhandoff内キャッシュは今回変更していない。
- GitHub M121 ledgerのモデル・監査・画像4枚、合計6件の記録ハッシュとも一致。
- `protected_original_source_zip_sha256=83201a...` は継承元M120 ZIPのハッシュであり、今回のM121 ZIP全体の期待値ではない。M120元ZIPはローカルにないためZIP全体の照合は未実施。
- M121 ZIP全体の独立した事前期待ハッシュは提供資料に見当たらない。上記は今回計算した指紋と内容照合であり、外部の期待ZIPハッシュとの一致を主張しない。旧SETUP_STATUSの「archive SHA256 verified」はこの限界を記載していなかった。

## Pythonと検証結果

- PATHのPython: 3.13.15。ランチャー `py -0p` は登録済みPythonなしと表示し、PATH実行時にreal location警告あり。
- 安定した基盤としてCodex同梱CPython 3.12.14を使用し、プロジェクト直下 `.venv/` に隔離環境を作成。
- 基盤実体: `C:\Users\ryoma\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`。
- 仮想環境はsystem-site-packages=false。pip 25.0.1を付属wheelからオフライン初期化。今回新たな第三者パッケージはインストールしていない。
- 完全ソースの既存テスト: **15/15 PASS**（M119 5、M120 6、M121 4）。原本と取り込み先で確認。
- GitHub側の既存テスト: **37/37 PASS**。policy checkもPASS。
- 補助照合: M119 A/B、M120モデル/監査、M121モデル/監査の6 JSONをメモリ上で再生成し、JSON表現へ正規化して保存内容と一致。ファイル出力は実施していない。
- サンドボックス内の初回追加テストでは一時領域作成/削除とPath.resolve(strict=True)がWinError 5で拒否された。テスト専用一時領域をrepo/artifacts/test-tempに限定し、自動承認された権限制約外の実行で37件PASS。元のidentity guardや安全判定は変更・迂回していない。ダミーfixtureのみ使用し、実ワールドは参照していない。
- 標準ライブラリだけで必要な検証ができるため、テスト用依存は `research/m121/requirements-tests.lock.txt` に記録。

再実行（repoフォルダから）:

```powershell
../.venv/Scripts/python.exe -B -X utf8 tools/m121_offline_check.py --repo-tests
```

別のChat実行環境ではPython 3.11〜3.13を使い、同じツールを `python -B -X utf8 tools/m121_offline_check.py --repo-tests` で実行可能。今回の実証済みバージョンは3.12.14。サンドボックスで追加37件が権限エラーになる場合は環境制約として扱い、guardを緩和しない。

## 未同期3Dコードの監査と安全な扱い

- 生成/監査5ソースは標準ライブラリとバンドル内M117 atlasを使用。確認したファイルI/Oはバンドル相対のdata/imagesのみ。実Minecraft保存先へのI/O、外部サービス呼び出し、施工処理は見つからない。
- ただし元CLIは保存済みJSON/画像を同じ場所に上書きする。`render_m119_sections.py` はimport時にも画像を出力するため、原本を参照する環境でレンダラーをimport/実行しない。
- 原本の一部read_text/write_textはencoding未指定。Windowsでは `-X utf8` が必要。検証では `-B` でキャッシュ出力も抑止。
- M121レンダラーのFONTはLinuxの `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` 固定。Windowsでそのまま画像4枚を再描画できる状態ではない。
- 同梱基盤にはnumpy 2.3.5、Pillow 12.3.0があるが、隔離環境には導入していない。matplotlib・VTKは基盤にも不足。PATH Pythonのnumpy 2.5.3とも環境が異なる。
- `requirements_m121_reference.txt` は最低バージョンの参考指定であり、描画用検証済みlockではない。重量級描画依存の導入、Windowsフォント対応、別作業コピーへの出力、4枚の再描画比較は未実施。
- 将来の描画変更はupstream外の作業コピー/adapterで実施し、レビュー後に別差分で管理する。原本を直接修正しない。
- M117 atlasはユーザー由来資料。今回ローカルのprivate repo候補に含めたが、外部アップロードはしていない。GitHub同期前に含有範囲をレビューする。
- 38件のM120重複候補は未分類。M121追加566件の限定人工材AABBヒット0は保護クリアランスを証明しない。全メッシュは施工未検証。

## 保護と未解決事項

Minecraft実ワールドには一切アクセス・書き込みをしていない。ワールドを読まないため、実セーブの前後ハッシュ比較も行っていない。Freeze408/public959/SB09/SB13 3×4/88空洞/道路公園/M101/正式設計は未変更。M122建築実装は未開始。施工先登録と施工はHOLDのまま。

未解決は、M121 ZIPの独立期待ハッシュ、元M120 ZIPの所在、描画依存lock/Windows対応/画像再描画、ローカル成果のGitHub同期。ローカルgitネットワークはDNS解決できず、GitHub読み取り確認は接続機能で代替した。

## Chatでの開発再開

Chatはローカルのみのブランチやファイルを直接読めるとは限らない。現時点のGitHub #18には完全ソースの取り込みはまだない。

1. 今回用意したレビュー用ZIPをユーザーがChatに添付する。ZIPには既存リポジトリ全体と今回の完全ソース・検証ツール・本報告を含める。元handoff ZIPは別途必要に応じて添付。
2. Chatに本報告を先に読み、`research/m121/upstream/` を原本、M121基準commitを既存GitHub正本として扱うよう依頼する。
3. Chatとユーザーが取り込み差分をレビューし、別途指示した場合にだけprivate GitHubの新ブランチへpush/Draft PRを作成する。既存Draft PRのbase/head変更や一括mergeはしない。
4. M122の開始は次の明示的な指示を待つ。Chat優先・Minecraftアクセス禁止・正式設計とFreeze維持を引き続き適用する。

レビュー用ZIPはローカル成果の受け渡し用であり、配布先へアップロード済みではない。
