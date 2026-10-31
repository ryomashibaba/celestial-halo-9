CELESTIAL HALO-9 — R4-E1B WindowsバックグラウンドBlender実機試験
基準：2026-10-31 / 検査治具であり都市美術作品ではありません

機能：既存のBlender（Blender 5.2系を想定）をバックグラウンド起動し、
立方体の既存メッシュ編集、前後2つのBLEND保存、前後2枚のPNGレンダー、
別名保存済みBLENDの再読込と、変更対象外メッシュ・カメラ同一性を照合します。

起動（PCの前面を占有するComputer Useは使用しません）:
1. ZIPを解凍します。
2. 同じフォルダーの Start_E1B_Test.cmd をダブルクリックするか、
   ChatGPTデスクトップアプリのローカルWorkに、同じフォルダーから
   run_background_probe_v2.ps1 を実行するよう依頼します。
3. Blenderが標準位置になければ BLENDER_NOT_FOUND と停止します。
   自動インストール、ネットワーク接続、公式ワールドへの書込はありません。

必要なアクセス：解凍先の3ファイル（.cmd/.ps1/.py）と、
%LOCALAPPDATA%\CelestialHalo9\R4BackgroundProbe\ の検証用書込先だけです。
対象外のプロジェクトやユーザーファイルを読み込む必要はありません。

実行制限：BlenderはGUIなし、2 CPU threads、低プロセス優先度。
最大120秒でタイムアウト・自動再試行なし。PCの完全無負荷は保証できません。

実行ログ：
%LOCALAPPDATA%\CelestialHalo9\R4BackgroundProbe\test_<ID>\report.json
および同ディレクトリのbefore.blend、after.blend、before.png、after.png。
ログは親フォルダーの test_<ID>.stdout.log / stderr.log です。
報告ファイルがない、またはエラーの場合は不合格として扱います。
成功した場合のみ、解凍したフォルダーに E1B_Result_<ID>.zip を自動生成します。
このZIPには検証用の2BLEND、2PNG、report.jsonだけが入り、私的ファイルは含みません。
次の美術レビューのため、その結果ZIPをChatGPTに添付できます。

注意：
- この試験のPASSはBlenderの入出力・限定メッシュ変更に限ります。
- AIが画像を見て建築美術を改善できたことは証明しません。
- たとえ成功してもMinecraft施工やCITY MASTER完成には進みません。
- .cmdは自動実行のためこのプロセスでのみPowerShellのExecutionPolicy Bypassを指定します。
  Windows全体の設定変更は行いません。実行する前に同梱ソースを確認できます。
