# J7-R11 再開方法

最初に`R11_ART_REVIEW_JA.md`と`R11_HANDOFF.json`を読む。美術判定は全案REJECT。採択形状の原本ではない。

GitHub納品先は[Draft PR #43](https://github.com/ryomashibaba/celestial-halo-9/pull/43)。実アセットのコミットと6バイナリのリモートblob照合は`qa/GITHUB_DELIVERY_READBACK.json`に記録。

BlenderのGUIでは`concept_A/R11_A.blend`、`concept_B/R11_B.blend`、`refined/R11_B_REFINED.blend`を個別に開ける。カメラ・照明・中立地面は別コレクション、建築は`01_EDITABLE_ARCHITECTURE`。単位m、Z上。実Minecraftファイルは使用しない。

## 再制作

上書きを避けるため、このR11フォルダを**新しい独立研究コピー**へ複製してから実行する。既存研究成果・immutable原本で実行しない。Blender 5.2.1で確認済み。

1. `blender --background --factory-startup --python-exit-code 23 --python build_r11.py -- A all`
2. `blender --background --factory-startup --python-exit-code 23 --python build_r11.py -- B all`
3. BlenderでBの保存ファイルを開き、`refine_r11.py`を実行。R11では実際にMCP経由のライブBlenderで適用した。再実行する場合も初回Bから始めること。冪等スクリプトではない。
4. `render_saved.py -- refined B`で修正版を撮影。
5. `repair_human_views.py -- concept_A A`、`-- concept_B B`、`-- refined B`を各々Blenderバックグラウンドで実行。最初のカメラ位置を実観察床へ補修する。
6. `render_saved.py`を3状態に実行し、補修後の同じ最終モデルから各9方向を揃える。保存済み人間カメラ位置を継承する。
7. `verify_blender.py`をBlenderで実行し、保存BLEND/GLBを検証。
8. `python -B -X utf8 package_r11.py`で最終画像とソースを検査し、縮小比較表とハッシュを作る。PillowとWindows Arialフォントを使用。

フォルダ名や形状を変えた新しい研究では、パッケージャー内のR11固定ブランチ・ファイル指定を読み、R11へ上書きしないよう変更する。

## 記録した実行上の問題

- 初回の通常Git接続はDNS解決に失敗。許可されたネットワーク実行でfetchを完了。
- MCPの旧アドオンでread/edit/look/saveは動作。アップデート・外部有料生成器導入は実施していない。
- 未使用材質はBLEND保存時に消えるため、ライブ編集スクリプトの材質取得を修正した。失敗した最初の2呼出しは主形状変更前で停止した。
- 人間カメラ補修スクリプトの構文・未使用材質参照を修正し、各最終実行は終了0。
- boolean適用時に「最初のmodifierでない」旨のBlenderメッセージが出た。実形状は保存・描画・GLB再読込で確認したが、全面的なトポロジー合格を意味しない。
- 最終BLEND保存時にユーザーフォルダの自動サムネイル作成が拒否された。研究フォルダのBLEND保存と再読込は成功した。成果のPNG出力には影響なし。
- 初期の人間視点には壁内で黒くなった画像があった。合格として扱わず、実床へ移して最終全27画像を再描画した。

一時ログ・キャッシュ・Blenderの`.blend1`バックアップはローカルに残し、研究Git納品から除外する。正式証拠は保存モデル、最終PNG、JSONの読戻し・ハッシュ・評価記録。
