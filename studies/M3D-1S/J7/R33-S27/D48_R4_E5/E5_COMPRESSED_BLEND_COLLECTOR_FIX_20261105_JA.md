# E5 回収器の偽HOLD — 圧縮BLENDヘッダー未対応

2026-11-05。E5の真正Blender作者ログから `E4_R0B_WORKING.blend` と最優先2枚の実PNGの保存成功が確認済み。正式ART採用0件、独立BLEND再読込未実施、Minecraft施工HOLD。

## 観察した事実

ユーザーが実行した旧回収器が `RECOVERY HOLD: BLEND header mismatch.` と表示して停止。元のPython作者ソースには `bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)` と明記されている。一方、旧回収器は `BLENDER` の非圧縮ヘッダーだけを受理し、それ以外の圧縮ヘッダーをすべて破損扱いしていた。これが誤停止の**有力な原因**（実BLENDファイルの先頭バイトはまだ未取得）である。

Blender 3.0以降の圧縮は原則Zstandard（`28 B5 2F FD`）、旧形式にはgzip（`1F 8B`）がある。非圧縮BLENDの先頭はASCII `BLENDER`。Blender公式マニュアルとBlender開発ツールのファイル読み取り処理に照らして確認。圧縮の有無だけでファイル破損と判断しない。

## 修正した収集契約

- 既存BLENDの最初の16バイトから非圧縮・Zstandard・gzipを区別。いずれも**ファイルの再読込成功を意味しない**。未知なら `HEADER_UNKNOWN_COLLECT_FOR_DIAGNOSIS` として元バイトと実ファイルを診断用に回収する。
- 実PNGの署名・960×640サイズ、3ファイルのSHA256、元stdout正常終了を記録。
- 保存成功済みのBLEND/PNGを**読み取り専用でZIP収集**。Blender自体を起動しない。既存ファイルを上書きしない。日時付きZIPを作る。
- 画像2枚はZIPなしの直接添付でも美術審査を先行できる。BLENDの独立再読込や同じBLENDの直接編集には実BLENDファイル本体が必要。
- 元実行時のログでBlender作者工程は成功している。**技術的な再読込・画像の直接審査・ART判定は未実施**。

## 検証限界

修正版スクリプトのZIP構造・内容はチェック済みだがWindows/PowerShell実機では未実行。ヘッダーの現物と圧縮データの完全性は元のBLENDバイナリを確認するまで**未検証**。ユーザー側の操作は最低限とし、同じ誤原因で新規Blender作者工程を実行し直さない。

既存研究ブランチ/E2/E3/E4/main/Freeze/Minecraftワールド保護、CITY MASTER 3D FIRST、ART-FIRSTを維持。
