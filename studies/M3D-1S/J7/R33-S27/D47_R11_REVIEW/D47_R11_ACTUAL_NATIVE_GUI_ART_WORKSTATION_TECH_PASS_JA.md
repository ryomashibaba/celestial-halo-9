# CELESTIAL HALO-9 — D47-R11 真正Blender GUI・可逆編集スタジオの最終実測レビュー

**2026-10-30 JST／R11ワークスペース：TECH限定PASS／美術制作：未実施・採択0件／Minecraft施工HOLD**

## 0. R10までの結果から必ず変えるべき点

R1〜R10の生成・独立A/B比較・原本再撮影では美術的な主役が一度も採用できていない。R10の原本4点の監査では、A2-G7は側面が厚い壁、B2-G6は大きな段状門、C2-G6は生物的な殻、C2-G7 N1は穴のある角張った塊に見えた。C2-G6当時の美術HOLDは後続G7で詳細化STOPに至っている。

R11は新たな「美術原型」制作に見せかけて同じ自動生成手法を続けるのを停止し、**初めて作業者がBlender上で直接編集し、6視点を確認し、編集版を保存できる独立スタジオ**を作った。先行2026-10-24 J7-R7にも実GUIキーボード編集PASSはあり、今回その技術を初めて発見したとはしない。

## 1. 実際に制作し検証したもの

- 原本研究隔離ブランチ：`research/r33-s27-d47-r11-native-visual-workstation-20261030`。
- 実行：[GitHub Actions #41000246873](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41000246873) **全工程SUCCESS**。
- **ネイティブBLEND原本**：`R11_OPEN_IN_BLENDER_VISUAL_SCULPT_STUDIO.blend`。SHA256 `c3c23d5ceedf9b922d0c62ca8ed7550079c243847dc5376a2444aee8b243ec66`。
- 初期試験メッシュ：**1,189頂点／1,120四角面**の中立布状面。美術作品、都市形状、M247-C原型ではない。
- **Basis＋可逆シェイプキー`R11_ARTIST_REVERSIBLE_LAYER`**を保存。元のBasisに試験変更を混入させない。
- 正面・側面・斜視・背面・低所公共視点・高所別世界視点の**6台の固定カメラ**。
- R10四系統の不採択研究から作った実画像一覧を、元の原本に手を加えず**読取専用の歴史的参照画像としてBLEND内部へPACK**した。
- `R11_RUN_THIS_FOR_NATIVE_ART_TOOLBAR.py`をBLEND内のテキストブロックへ埋込み。ユーザーはBlender Text EditorでRun Scriptし、サイドバーの`HALO9 Art`を使う。

## 2. 実GUI上の成功と厳密な区別

GitHub Actionsの使い捨てLinux仮想画面で**本物のBlender 4.0.2デスクトップGUIを起動**し、GUIでTab→Edit Mode、A→全頂点選択、G X 30→確定、Ctrl+S→保存した。前・後の**X11画面からの実スクリーンショット**を保全。

独立処理は保存済み原本BLENDとGUI編集版BLENDを別々に読み込んで比較した。

- シェイプキーの全頂点**X方向移動量の中央値は実測30.000m**。全頂点の移動量に有意なばらつきなし。
- Basisの全頂点は元と一致。元のネイティブ原本BLENDもSHA256が一致し、**バイト不変**。
- 元の6台のカメラ位置は不変。
- UIの`r11.select_review_view`演算子をBlenderで6回呼び、すべて対応するCamera名へ切替成功。
- `r11.freeze_artist_evidence`演算子をBlenderで呼び出して、**新規別BLEND・GLB・同一モデルからの6枚の実カメラPNG・監査JSON**を新規リビジョンディレクトリに保存。
- そのチェックポイントBLENDとGLBを**別処理で再読込**。成功。
- **重要：カメラ切替ボタン・保存ボタンをGUI上でマウスクリックしたとは主張しない。** ボタンと同じ演算子を真正Blenderプロセスで単体試験した。GUIによる形状変形とCtrl+S自体はX11上の実入力を独立確認。

これにより本R11の「ネイティブ編集ワークスペース＋GUI編集＋可逆化＋6視点チェックポイント」の技術条件はPASSとした。

## 3. 失敗履歴も含めた再現性

- 初回CI [#40999796775](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/40999796775)：Ubuntu Blenderが`libEGL.so.1`を読めず、実モデル生成前にFAIL。描画依存を明示追加しXvfbでBlenderを実行するよう変更。
- 次回CI [#40999962832](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/40999962832)：原本BLEND生成とGUI実編集はPASS、BLENDの保存別読取も通過。一方、GLB書出し演算子で`numpy`不足によりFAIL。
- 最終CI [#41000246873](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41000246873)：`python3-numpy`を追加し、全証拠・本物のチェックポイント再読込・研究ブランチ証拠保存までSUCCESS。QAを弱くして形式的な合格にしていない。

## 4. R11成果ファイル

- `studies/M3D-1S/J7/R33-S27/D47_R11_WORKSTATION/r11_create_visual_workspace.py`：中立実メッシュ、6固定カメラ、参照画像、内部テキストの制作。
- `.../r11_art_direction_toolbar.py`：BlenderネイティブUIサイドバーのカメラ切替と独立チェックポイント。
- `.../r11_test_real_gui.sh`：Linux Blender実GUIでの本物のキーボード変形・画面保存。
- `.../r11_independent_gui_and_checkpoint_audit.py`：元原本ハッシュ・Basis不変・30m頂点変化・GLB/BLEND再読込・カメラ切替とチェックポイント検査。
- `.../R11_GUI_STUDIO_USER_GUIDE_JA.md`：Windows Blender 5.2.1利用手順。
- `studies/M3D-1S/J7/R33-S27/D47_R11_EVIDENCE/R11_NATIVE_ARTIST_STUDIO_GUI_AND_CHECKPOINT_TECH_ONLY.zip`：技術証拠の公式アーカイブ。
- アーカイブSHA256：`8167e53d032c811be0ffcb76734bd51e0045edde3038043f6f738a1214f66f70`。23の所定ファイルを保存し、別紙JSONにファイル別SHA256を記録。

## 5. 美術に関する厳密な判定

本R11は、**新たな都市美術案を制作したのではない**。モデルは1枚の中立形状であり、現時点で「実在する都市生活の断面」「圧倒的な非対称の建築外形」「神聖80%・危険20%」「α双殻浮断＋β斜裂天脊」「10km詳細都市マスター」のいずれも成立したわけではない。

**ART：NOT EVALUATED（正式採択0件）。** 中立テスト形状を「ART REJECTされた都市の第11案」と数えない。編集・出力の技術を測るための治具と明示する。

## 6. 次工程R12へ持ち越す条件

R12では同じ中立メッシュを美術案として勝手に採択しない。これまで全て失敗してきた巨大シルエット・側面板・段状棚・空洞の意味不足を、アーティストが**本物の画面で全方向の構図を見ながら**主形状から修正するワークフローへ移る。

本R11スタジオをユーザーがBlenderで操作することも可能になったが、これをもってユーザーに作業を丸投げしてはいけない。WorkのGUI操作はユーザーの事前明示許可が必要。Chat/GitHub中心で、追加の創作方法は正式政策に基づき独立研究で検討する。

**main HEAD・正式M247-C・保護原本・Minecraftを変更しない。10km級W0/H1〜H6/SB01〜SB16/HERO4全部の詳細統合3D完成要件は緩めず、Minecraft施工HOLDを継続。**

**最終：R11 GUI EDIT / ARTIST NATIVE STUDIO / SIX CAMERA CAPTURE TECH LIMITED PASS；ART成果なし；M247C正式採択0。**
