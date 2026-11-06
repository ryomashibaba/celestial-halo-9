# Gate B AFTER INT21 — 新規断面の真正3D制作と早期棄却

2026-11-07 JST。**ART REJECT / Gate B未達 / 正式採用0件 / 完成0/30 / 施工HOLD。**

## 実物と判定

- [最終研究BLEND](GATE_B_R1.blend)、[初稿BLEND](GATE_B_R0.blend)
- 固定E11画像：[NAVE R0](R0/E11_NAVE_HUMAN.png) → [R1](R1/E11_NAVE_HUMAN.png)、[H1 R0](R0/E11_H1_HUMAN.png) → [R1](R1/E11_H1_HUMAN.png)、[俯瞰R0](R0/E11_URBAN_AERIAL.png) → [R1](R1/E11_URBAN_AERIAL.png)
- [画像を受けた頂点修正](R1_image_driven_changes.json)、[独立再読込検査](INDEPENDENT_REOPEN.json)、[状態台帳](STATUS.json)

INT21の不採用卵形主質量を継承せず、W0とE11カメラだけを保持した独立コピーに新規著作。水際の到着路、NAVE公開室、図書館回廊、H1市場・学校中庭・住宅中庭、昇降核、高高度転位部分を同一研究シーンに置いた。用途名だけでは機能成立と認定していない。

R0の真正3画像を直接見たところ、NAVEは太い平板骨格の反復、H1は東母体内への埋没、俯瞰は巨大壁と小さな街区の分離となった。同じBLENDの既存9メッシュの頂点を編集。東母体上縁を街路下へ再構成し、NAVEリブ断面を細くした。オブジェクト移動だけの修正ではない。R1の3画像も直接確認した。

**R1批評：** H1の埋没は解消し中庭街区と市場が見える。しかし単調な水平ファサード、空白の広場、薄い市場屋根で、厚い独自の生活都市には至らない。NAVEはまだ大きな板状の反復骨格が主役で、公開室・図書館・斜裂・居住母体が一体の建築になっていない。俯瞰の西巨大壁、東の棚状地盤、切れた高高度部分も統合不足。これはINT21に対する美術合格や完成度向上の主張ではない。**ART REJECTとしてこの形状の窓・小物・色彩による延命、追加多視点レンダー、機能QAの拡張を停止した。**

## 制作方法と限界

Blender MCPは接続不可だった。既存ローカルBlender 5.2.1を画面を出さないbackground / factory-startup / disable-autoexec / CPU2スレッドで実行。新規主輪郭と中庭・回廊の制作はPython補助による明示的ポリゴン著作。**GUIブラシ手彫り、ライブMCP制作、専門家水準の直接彫塑とは呼ばない。**

真正画像を見る → 問題を特定 → 保存済みメッシュ9件の頂点修正 → 同じ固定3視点の真正画像を再確認、という限定的な視覚ループは実施した。美術制作能力の成功とは別であり、高品質な建築著作能力はHOLD。初稿作者スクリプトの再実行を再開方法にしない。

レンダーはR0/R1計6枚、960×720、Cycles CPU 12samples・denoise。どちらも全シーン、非CUTAWAY。W0が簡略な既存研究地形であること、機能・交通の干渉や歩行・学校の全内部が未検証であることを含め、都市完成証拠ではない。

## 正本・再取得したHEAD

AFTER INT21全文とmainの憲章・3D完成基準・決定ログ・AGENTSを取得。main CURRENT_STATUSは10月23日の古い状態として区別。

- main：a2f88995eee8d10ee4830dbdf33ccb9c0790de8f
- AFTER INT21引き継ぎ枝：b921db20f17b424b9e1e9f187631f2874616f8d8
- INT21成果枝：d5bcda16b1f2f0e39c530b52f1d7124ad97acf5e
- Actions 42295170314：completed/success。ただし実行コードHEADはc673443b2fdf8bd4519f02141344e08c5e33dd47で、成果保存後HEADとは異なる。
- 参照展開BLEND：SHA256 9b950f0b9d5315605d5dc0bec252950e0c150739c94249a201667c9e2d675a27。取得後・再読込後とも一致。

取得した正本は [reference/AFTER_INT21_JA.md](reference/AFTER_INT21_JA.md)。GitHub取得はconnector経由。ローカルgit fetchはDNS失敗のため、全リモート履歴同期済みとは主張しない。新規ローカル統合枝は既存E11のb9aa433を親とし、固定INT21の参照データを別フォルダへ追加した。

## 保全・次回

独立した別BlenderプロセスでR1を再読込。4件のW0メッシュの頂点・面トポロジー・行列と5件のE11カメラの行列・焦点距離・センサー幅・遠クリップが参照状態と一致。旧建築オブジェクトのシーン内残存0。これは全面干渉検証やART PASSではない。

Minecraft保存データへのアクセス0。archives、handoff/M121、research/m121/upstream、Freeze、正式原本、既存Draft PR、mainの変更0。GitHub push/merge・Actions起動・有料API・新規インストール・画像生成・外部素材・画面占有なし。Blenderは保存時にユーザーサムネイル領域への出力を試みて権限エラーを出したが、研究BLENDの保存・別プロセス再読込は成功。

次はこの骨格や巨大壁を細密化しない。再開するなら、最終主形状を生成し直す前に、NAVEの室・H1の生活街区・斜裂の外観を同じ建築として造形できる方法を確保する。今回のPython輪郭方式を高品質制作方法として採択しない。正式研究方向や完成条件は維持する。費用監査は過去GitHub分UNKNOWN、今回追加サービス課金の呼び出し0（ローカルCPUのみ）。

## 再検証

`blender --background --factory-startup --disable-autoexec --threads 2 --python verify_reopen.py`

オフラインPython補助は `python -B -X utf8` を使う。元の参照BLENDから作者スクリプトを無断再実行しない。最終画像の再現は `render_section.py -- R1` だが、棄却済みのため目的のない再レンダーを行わない。
