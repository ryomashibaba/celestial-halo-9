# HALO-9 R4-E8 真正美術審査・改善方針の継承

**2026-11-05 JST / TECH PASS / ART REJECT / 正式採用0件 / CITY MASTER完成0/30 / Minecraft HOLD**

## 実行・保存の確認
- 研究HEAD起点：E7 ART REJECT審査コミット 3babf506dbf47267fa610971f6455fb61342627b。
- 最初のGitHub Actions #42025280864 は **FAILURE**。真正BLEND・3PNGは生成されたが、独立検査がコレクション名を取り違えてPython例外を発生。Blender 4が終了コード0を返すことがあり、ステップ表示を成功と誤認した。この失敗は隠さない。
- 修正で、実在するREGISTRY_30_UNFINISHEDを検査し、Blender stdout に R4_E8_REAL_NATIVE_REOPEN_PASS を明示的に要求、JSON存在も検証。正常終了だけではTECH PASSと宣言しない。
- 修正後のActions [#42025644586](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42025644586) **SUCCESS**。Blender真正BLEND生成・同一BLENDからのPNG3視点・別Blenderプロセスによる独立再読込・正式ART未採用の検証・GitHub研究ブランチへの証拠保存すべてPASS。
- 永続ファイル：e8_evidence/E8_LIVED_SPINE_PUBLIC_CITY_WORKING.blend.gz（編集可能BLEND gzip）、E8_TRUE_THREE_VIEW_ART_UNREVIEWED.jpg（真正PNG3枚から構成した比較画像）、E8_TECH_NOT_ART.json。PNG原画と編集可能BLEND本体はActions Artifact ID 13414650054にも格納（短期保持）。画像生成による代替ではない。

## E7からの変更と直接ART判断
1. **human_public_interior**：E7の白い不定形塊を廃し、NAVE中央の南北公開街路、左右の複数階公共建築、横断連絡橋、沿道植栽が視認可能になった。改善は事実。ただし普通の広幅都市道路・箱型建築に近く、数百m級公共室としての特殊な建築断面や内部生活、真正の壮大さが依然ない。**ART REJECT**。
2. **human_sky_district**：歩行者カメラは大きな青い外壁に塞がれてしまい、地区内の可視施設と街路を認証できない。これはまず **CAMERA OCCLUSION / REVIEW INVALID FOR H1 DETAIL** と記録する。カメラ修正のみでは都市全体のART採用を許可しない。
3. **urban_aerial**：E7の同心円状の外観は解消。しかし、巨大な矩形基壇2つと小型の反復建物群に見え、中央M247-Cの異常な主役性、立体的な居住都市、W0山岳・断崖・人工内海と都市間の断面の統合が不成立。**ART REJECT**。
- TECH PASSは美術品質保証・路線歩行検証・正規座標検証・Minecraft施工承認ではない。
- 3視点比較は元のBlender同一シーンに基づく。縮小JPEGはPNG原本ではない。

## 苦しいが重要な批判的判断
E6の刃／基壇、E7の同心円＋ファセット塊、E8の箱形公開街路＋箱形高所地区。異なる幾何案に移っても、**プログラムで大きな箱・床・反復を並べるだけでは美術としての核心が生まれない** ことを繰り返し確認した。

同じ手段でE9/E10の主造形を追加量産するのは避ける。必要なのは新しい監督器や数十のテストではなく、**真正Blenderの実体に対し、アーティストが見ながら中央空洞・都市断面・主建築外観そのものを直接彫塑／編集できる制作ループ**。次の制作対象は中央・NAVE・H1・W0の統合主形状のまま。最初に人間視点で居住と公共施設が読める断面を成立させ、それが遠景で異様な都市シルエットとなるよう一体編集する。

Work / Computer Use、ローカルGUI操作はユーザーの個別明示承認が必要。実接続も未確認。無承認で起動した・利用可能と主張しない。テキストだけで新たな美術採用を捏造しない。既存のE8 BLENDを完成形扱いせず記録として凍結する。

## 保護
main a2f88995eee8d10ee4830dbdf33ccb9c0790de8f、E2/E3/E4/E5/E6/E7、原本、Freeze、Minecraftワールド無変更。M247-C正式研究方向は保持し、E8試作品を正式メッシュ採用しない。追加課金なし、世界施工なし、正式ART採用0件。
