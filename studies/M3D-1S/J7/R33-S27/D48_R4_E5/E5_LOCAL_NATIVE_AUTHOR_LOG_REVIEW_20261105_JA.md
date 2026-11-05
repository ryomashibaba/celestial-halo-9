# E5 — Windows真正Blender R0B制作ログ・誤判定訂正（2026-11-05）

## 根拠

ユーザーから `author.stdout.txt` と `author.stderr.txt` の実ログを受領し直接照合。ユーザー環境の絶対パス・氏名は公開研究記録に転載しない。

- stdout: `render | Saved: .../renders/human_sky_district.png`
- stdout: `render | Saved: .../renders/human_public_interior.png`
- stdout: `Info: Saved as "E4_R0B_WORKING.blend"`
- stdout: `HALO9_E4_R0_RESULTS`：`native_blender_saved=true`、`geometry_object_count=522`、`art_pass=false`、`completed_targets=0`、`minecraft=HOLD`、`e2_files_touched=false`
- stdout: `Blender 5.2.1 LTS`、`Blender quit`
- stderr: `DeprecationWarning: Material.use_nodes`（Blender 6.0に向けた予告警告。今回の中止原因と判断する根拠はない）

BlenderMCPアドオンがバックグラウンドモードではサーバー起動できない旨の表示もあるが、その後に実レンダー保存、BLEND保存、正常終了の記録が続いている。このアドオン表示をBlender制作失敗と解釈しない。

## 訂正した結論

**R0Bの真正Blender作者工程はログ上で成功した。** 元 `run_E5_background.ps1` は `Start-Process -PassThru -RedirectStandardOutput -RedirectStandardError` の後の `$p.ExitCode` が空欄となって成功工程を失敗扱いし、独立再読込と共有用ZIP作成へ進めなかった可能性が極めて高い。

現時点での正確なステータス：

- AUTHOR_NATIVE_BLEND_SAVED: **LOG_CONFIRMED**
- AUTHOR_NATIVE_TWO_RENDERS_SAVED: **LOG_CONFIRMED**
- ORIGINAL_OUTPUT_BINARY_SIGNATURES: **NOT_YET_OBSERVED_HERE**
- INDEPENDENT_REOPEN_VERIFIED: **NO**
- REAL_IMAGE_DIRECT_ART_REVIEW: **PENDING**
- ART_APPROVED: **0**
- CITY_MASTER_FINISHED: **NO**
- MINECRAFT_WRITE: **HOLD**

**ログだけではBLENDの内容・完成品質・カメラ位置・画像の見た目は証明できない。**

## 次工程（再制作禁止）

既存出力フォルダにある `E4_R0B_WORKING.blend` と2枚の実PNG、ログを**読み取り専用で回収**。実Blender再実行・新規メッシュ生成・再レンダーを行わない。

チャットで提供するワンクリック回収器は、対象ファイル存在、BLENDの `BLENDER` ヘッダー、PNG署名と960×640、作者ログの正常完了を確認し、1つのZIPにまとめる。元フォルダを上書きしない。対象パスは前回出力日時に固定し、別原本を推測しない。

ZIP入手後、実PNGを直接開いてH1/NAVEのART厳格審査。未採用なら既存BLENDの**保存複製**を別ファイルに直接編集し、固定カメラで真正再レンダーする。修正が元BLENDへ逆流しないことをハッシュで確認。

E2/E3/E4/E5既存原本・main・Freeze・正式ワールド保護、CITY MASTER 3D FIRST、30対象を維持。GUI操作やWork/Computer Useの新規承認は得ていない。

**注意：GitHub Actionsのrunが未確認であることは、ユーザーWindowsで成功したBlender作者工程を否定しない。**
