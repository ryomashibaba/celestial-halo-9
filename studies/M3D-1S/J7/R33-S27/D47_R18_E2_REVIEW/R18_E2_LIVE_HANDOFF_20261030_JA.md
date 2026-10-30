# CELESTIAL HALO‑9 / CELESTIAL SPINE — D47 R18 E2 LIVE HANDOFF
**2026-10-30 JST／E2非正式研究／実行結果・美術採択は必ずCIと実画像を確認**

## これまでの実績と問題の継承
- R17-A／R17-B：SOURCE TECH限定成功もART REJECT。R17-Bの階段は168の非接続踏面、FUNCTION FAIL。
- R18-E0：実BLEND+GLB+10画像生成。検査のGLB分割46成分は同座標頂点統合後1成分、負の破断テスト2成分。独立再現CI `#41063490476` SUCCESS。**ART REJECT**。小パビリオン、板・梁と無地壁が中心で生活空間として不足。
- R18-E1：新規BLEND+GLB+入口/斜視/背面の3画像を作成・独立再読込 CI `#41066891031` SUCCESS。ART REJECT。岩塊・巨大板・宙に浮く梁が主役で、公共文化・研究・都市交通の生活が内部から感じられない。E1-G0現形状は細密化STOP。

## E2 G0 の今回の進展
- 隔離研究ブランチ：`research/r33-s27-d47-r18-e2-inhabited-void-20261030`。前工程E1の保存済みHEAD `b3e6d3d09b0d243b2bc3391d7e7df1a75d04795f` から分岐。
- 新造形コード：`studies/M3D-1S/J7/R33-S27/D47_R18_E2_NATIVE/e2_inhabited_civic_canyon.py`。
- 研究仮称：《生きた光峡谷》。作品起点は中央の公的研究実演広場、文化収蔵バルコニー、公開研究テラス、高所の文化観察・交通床。実在する各用途に合わせた相互非鏡像の手編集可能な都市断面をつくる。
- 作成済みCI：`#41068540782` / `HALO9 R18 E2 new inhabited civic canyon genuine 4-view art G0`。Blender4.5.15 LTSで真正BLEND+GLB、地上入口・広場人間視点・遠方斜視・背面の4PNGを生成し独立再読込。実際の美術審査は画像取得後に行う。
- 先行審査基準：`D47_R18_E2_REVIEW/E2_ART_GATE_BEFORE_REAL_IMAGES_JA.md`。E1の単なる大規模化に見えたら即ART REJECT / STOP、装飾や窓追加で延命しない。
- **作成コードやCI登録は、美術合格・実モデル生成成功の証明ではない。** 最終CIと4つの真正画像を取得してから断言する。

## 次の作業の具体的手順
1. [CI #41068540782](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41068540782) の実際のステップ／エラー／最終状態を確認。現時点で**queued**だったため、実行結果はこの記録の作成時点で未検証。
2. SUCCESSならGitHub Actionsの`HALO9-R18-E2-NEW-GENUINE-CIVIC-4VIEWS-BLEND-GLB`原本ZIPを取得して、本当のPNGの地上入口、広場、斜視、背面を**画素を見て**評価する。未確認の美術的改善を想像で主張しない。
3. FUNCTIONは高所の4用途全体の動線・橋の端・支持構造・避難・アクセシビリティ未認証。少数ルートの計画勾配だけでFUNCTION PASSを言わない。
4. ART REJECTなら美術原本は隔離して原形の細密化STOP。ART HOLDなら何が変われば合格するか**具体的に**示し、同じ作品の装飾付加はしない。
5. 合格相当の実作品に到達した場合も即正式採択せず、第三者照合・実内部QA・全10kmの詳細City Masterとの整合審査を経る。

## 守る契約
M247-C《浮断天核》、W0/H1–H6/SB01–SB16、正式main、過去E0/E1研究原本、Minecraft世界を無断変更しない。中央正式ART採択0。約10km全市の全建物外観・巨大施設内観・交通・地形・公共内部・材質・照明の**統合済み編集可能詳細City Master**完成前のMinecraft施工を許可しない。外注しない。Work操作は明示承認制。Chat主体・本当の美術成果を目標とする。

## 実行後追補：E2初回CIの実際の失敗と最小修正

- [初回CI #41068540782](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41068540782) は **failure**。実Blender起動後、`scene.world.color` が `NoneType` のため失敗。出力モデル・画像は生成されなかった。これは幾何美術の採否ではなく、`read_factory_settings(use_empty=True)` 後に世界データが存在しないことが原因。
- Blender 4.5のワールドを明示生成してから色を指定する最小修正を、同じ独立研究ブランチのコミット `8dccd29d644af5da9c2ff395c91e43385569a16e` に保存。アート形状、公共用途、判定閾値を変えていない。
- [修正後CI #41069377264](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41069377264) を起動したが、記録時点では **queued／最終結果未確認**。結果を勝手にPASSと書かず、真正4視点の美術審査も未実施。
- 本研究の真の現状は「E2新規3D制作ソース・CI登録済み／Blender背景初期化バグ修正済み／修正版実行待ち」。E1-G0の美術REJECTを解除しない。

## 最終確定追補：修正版実3D・目視美術・恒久保存完了

- **[修正版真正Blender制作CI #41069377264](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41069377264)：SUCCESS。** 実BLEND/GLB再読込・真正4カメラ画像、35 mesh・1,074頂点・1,912三角面。初回のBlender world初期化失敗は修正された。
- **[実画像4視点の審査報告](https://github.com/ryomashibaba/celestial-halo-9/blob/research/r33-s27-d47-r18-e2-inhabited-void-20261030/studies/M3D-1S/J7/R33-S27/D47_R18_E2_REVIEW/E2_G0_TRUE_FOUR_VIEWS_ART_REJECT_JA.md)：ART REJECT。** 人間入口は無地の灰色床・細柱・水平板、広場も活動の見えない細柱、斜視・背面は左右の岩壁状の質量と板。文化・研究・交通の都市生活が建築から伝わらず、E1からの美術飛躍なし。
- **[真正原本恒久保存CI #41070572289](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41070572289)：SUCCESS。** 本物のBLEND、GLB、4PNG、manifest、独立再読込監査JSONを `studies/M3D-1S/J7/R33-S27/D47_R18_E2_EVIDENCE/R18_E2_G0_TRUE_BLENDER_FOUR_VIEW_ART_REJECT_SOURCE.zip` にZIP保管。隣にSHA256台帳。最終research HEADは実際のGitHub refを参照。E2以外の研究原本およびmainは未変更。
- **最終：SOURCE TECH限定PASS／FUNCTION未認証／ART REJECT／正式採択0／E2現形状STOP**。これは「元のE2を修復して本番化する」許可ではない。

### 次の真の工程：制作方式自体の美術ゲート
E0（小さい抽象物）→E1（大きい岩・板）→E2（左右の壁・板・細柱）と、繰り返し同じ結果に到達。モデルの拡大・単純関数メッシュの追加・演出だけでは解決していない。E3でまず**人間目線の一つの圧倒的な公共内部を本当の造形として成立させること**を優先し、映像と照明だけでごまかさない。具体的には、入場口→奥の公開研究・資料空間→上層都市の活動が一つの画面で伝わる美術的な「構図・断面・連続性」を3Dで編集確認し、正面の成立前には巨大な左右外壁や道路を作らない。Pythonの同型の組合せを使い続けているだけなら不適切。Blender GUI/Workはユーザーの新規明示許可なしに利用しない。
