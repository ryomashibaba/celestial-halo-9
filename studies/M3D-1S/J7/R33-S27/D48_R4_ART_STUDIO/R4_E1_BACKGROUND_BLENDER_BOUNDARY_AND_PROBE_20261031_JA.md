# CELESTIAL HALO-9 — R4-E1 ローカルBlenderの非占有バックグラウンド経路

記録日：2026-10-31 JST／研究用のみ／正式美術採択0／Minecraft HOLD

## 更新されたユーザー承認
2026-10-31、ユーザーは「自分のPCを操作不能にしない範囲で、表立ったComputer Useではなく裏でBlenderを操作するならPC使用を許可」と明示した。これは**バックグラウンドのBlender処理**を限定して許すもので、Windowsの前面Computer Useによる入力占有、PCの他アプリ・私物ファイル・保護原本への広範なアクセスを許可したものではない。ユーザー作業の妨害、著しいCPU/GPU/RAM負荷、勝手なインストール、有料契約、ネットワーク公開、GitHub main書込、Minecraft施工、旧不採択の正式採用は禁止。ユーザーの最新明示承認を既存の「PC接続全面禁止」より優先するが、一般的な安全境界は維持する。

## 方法の選定
- Windows版のChatGPT Computer Useは前景操作で、ユーザーのマウス・キーボードを占有するため今回は**使用しない**。公式：https://learn.chatgpt.com/docs/computer-use
- Blender 5.2の正式CLIは \`--background\` と \`--python\` をサポート。プロセスのウィンドウを開かず独立シーンを編集・保存できる。公式：https://docs.blender.org/manual/it/5.2/advanced/command_line/arguments.html
- ユーザーPC上での実行は現在のChatから不可。ローカルのシェル/ファイル操作が公開されている**ユーザー承認済みWorkまたはCodexのローカルタスク**で、画面占有せず動かせることを別途確認する。Work CloudがローカルPCに勝手にアクセス可能と仮定しない。公式：https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex
- \`--background\` でBlenderのGUI表示はしないが、本物の .blend とBlenderレンダーを作り、それをAIが目視で批評して修正する循環は可能。**ただし、この実制作・視覚批評ループは未実証**。一括バッチモデル生成を美術成立にすり替えない。

## 今回保存した検査治具
- \`background_probe/run_r4_bg_probe.ps1\`：Windows PowerShell用。Blender exeがPATHまたは標準Program Filesにあるかだけ探索。存在しない場合は停止し、インストールしない。Windows UI・入力を一切操作しない。 \`CreateNoWindow\` + Blender \`--background\` + \`BelowNormal\` プロセス優先度 + CPU 2スレッド指定。タイムアウト120秒、無自動再試行。
- \`background_probe/r4_bg_probe.py\`：独立の小さなテストシーンのみ。新規の立方体を保存し、**同じ既存メッシュの頂点を編集**、Before/AfterのBLENDと320x180 PNGを作り、after.blendを再読込して頂点SHA256を照合。正式作品には一切アクセスしない。
- 出力：\`%LOCALAPPDATA%\CelestialHalo9\R4BackgroundProbe\<run_timestamp>\` 以下。各実行で別フォルダ。report.json と Before/After BLEND/PNG。ログは同専用lab親フォルダ。成果物は**自動的に外部送信しない**。GitHubへの公開前にパス・個人情報・不必要な出力を確認する。
- \`--factory-startup\` で既存ユーザー作業環境を読み込まず、 \`--disable-autoexec\` でBlend内蔵自動スクリプトを抑止する。実行対象の検査スクリプトそのものは明示指定。
- 別プロセスなので入力占有はしないが、物理PCの資源を使うため完全無影響は**保証しない**。重い別作業中は試験を延期/停止する。今後の制作も保守的なCPU/VRAM/RAM監視とユーザー操作の優先を基本とする。

## 実行条件と品質ゲート
1. 既存保護原本やMinecraftと関係ないローカル作業フォルダだけを使用。
2. Windows背景プロセスでBlendを実際に起動し、ユーザー作業を奪わない。
3. 実Blenderから before/after のネイティブBLEND・PNGを生成し、same existing mesh の本物の頂点差分・再読込を記録。
4. プログラムがPASSでも、外観改善能力や本番CITY MASTERを証明しない。別途AIがこれらの**実画像を閲覧**できるルートが必要。
5. AIによる観察→美術批評→同一シーン主形状大規模修正→再観察という**2回以上の別個のループ**が成立した場合に限りR4美術制作方式の効果を議論する。
6. 30対象、M247-C α＋β、H1-H6本格居住都市、16施設、公共室内部、全一般建物外観、全市統合マスターの完成義務は維持。マーカーを完成に数えない。

## 現在の証拠と判定
- この研究ブランチへのPython/PowerShell治具の**原文保存**は実施。コードのPython構文は別の分離コンテナでチェックできるが、**Windows PowerShellやBlender 5.2の実機動作は未検証**。
- このChatからユーザーPCへ接続していない。Blenderの起動、GUI/描画の取得、ローカル生成・再読込、実3D制作・AI視覚反復は未実行。ユーザーPCでの実測PASSは0。
- 現状態：**E1 BACKGROUND PROBE PREPARED / LOCAL EXECUTION PENDING**。ART：HOLD（既存REJECT継続）。正式採択0。CITY MASTER 3D未完成。Minecraft HOLD。
- 次は新規ローカルWork/Codexセッションなどの実行手段が利用できる場合のみ、ユーザーPCの前面操作を使わず、治具を一回実行。失敗時に勝手に権限拡大や本番データへのアクセスを行わない。
