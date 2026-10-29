# CELESTIAL HALO-9 — D36 Blender直接造形・技術ゲート

## 今回の実証範囲

このZIPは**正式な中央建築案ではありません**。D33〜D35で美術REJECTが続いたため、失敗形状をまた生成する代わりに、Chatで検証できる頂点編集と、Blender 5.2（ユーザーPC）でネイティブの編集可能`.blend`を作るための連携経路を独立研究しました。

**実際にChatで実行できたこと:** 保存済みの中立GLBをTrimeshで読み、指定した曲面メッシュの頂点を変更。保護メッシュの不変性、GLBの再読込、別Pythonプロセスでのバイト単位の再現、異常入力の拒否、VTKによる6視点×2実GLB画像と3視点比較を確認。

**Chatでは実行できなかったこと:** Blenderそのもの、`bpy`の実動作、`.blend`生成、Blenderの独自レンダー、Blenderによる書き出し結果の再検証。従って「Blenderで成功した」とは判定しない。

## Windows 11 / Blender 5.2.1 で確認する場合（任意・ワンクリック）

1. このZIPを一度だけ展開します。
2. `D36_RUN_ON_WINDOWS.bat`をダブルクリックします。BlenderがPATHまたは標準の `Program Files/Blender Foundation/Blender 5.2` に入っている必要があります。適合しなければ、バッチ内の `BLENDER_EXE` を自分のインストール先に修正します。
3. 新たに作成される `D36_BLENDER_RUN_...` フォルダーに `D36_EDITABLE_SCULPT_STUDY.blend`、GLB、6視点PNG、監査JSON、独立したBlender再読込検査JSONが出力されます。**これは今後の実機試験で想定する成果であって、Chatで生成済みのものではありません。**
4. この `.blend` を開いて `D36_SCULPT_TARGET` の Shape Keys から `D36_SCULPT_EDIT` を調整できます。正式中央造形とは切り離された中立テストです。

**保護:** 元のGLBは読取専用入力として扱い、SHA256不一致や想定外のメッシュは拒否。出力は新しいフォルダー。正式M247-C原本、main、Minecraftワールドは一切書き換えません。

## 技術的な注意

- Blenderで開き、形状と保護メッシュが再現されたかを、必ず実機で確認してください。**Blender連携の実行判定はPENDING**。
- 既存のD33不採用GLBを素材として検査したところ、全3メッシュで面の向きに不整合がありました。そのため配布素材は、別途作った水密かつ一貫した面向きを持つ中立GLBへ切り替えました。D33の不採用美術形状は引き継いでいません。
- BlenderのGLBインポート・エクスポートで頂点数や順序、重複頂点、morph target処理が変わることがあります。Chatの参照GLBとBlenderのGLBをバイト単位で同一と期待しないでください。`D36_BLENDER_REOPEN_AUDIT.json`はBlender内部の再読込検査です。
- 6視点の変化率・頂点移動量は建築の美術評価点ではありません。実居住室、上層交通、公共の動線、構造安全、10km都市の完成は今回まったく検証していません。
- Blenderへの自動コマンドは外部ファイルのPythonコードを実行します。使用前にコードを確認してください。任意のネットワークアクセスやMinecraftワールド操作は含めていません。

## 判定

- Chatでの頂点編集・GLB再現・保護: **TECH LIMITED PASS**。
- Blenderネイティブ生成・再読込: **NOT RUN**（本環境にBlender / bpyなし）。
- 美術: **NOT SUBMITTED**。球状テスト形状は美術案ではありません。
- 正式中央美術採択: **0件**。Minecraft施工: **HOLD**。CITY MASTER 3D FIRSTは不変。

## 次工程D37

ユーザーのBlender実機でワンクリック検査を行える場合は、作成された監査JSONと6視点レンダーを元に、Blender Native PASSを確定する。その後にだけ、多層居住都市と公共空洞を実際の編集対象として設計。実機テストが得られない場合は、未検証を維持したまま、Chatでの形状量産に戻らない。
