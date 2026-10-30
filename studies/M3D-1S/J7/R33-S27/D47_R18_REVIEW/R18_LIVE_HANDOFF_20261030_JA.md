# CELESTIAL HALO‑9 / CELESTIAL SPINE — D47 R18 LIVE HANDOFF
**Updated 2026‑10‑30 JST / isolated research, not canonical main**

## 研究状態
- E0《潮光の交差書院》: 実際のBLEND/GLB/真正10視点をGitHub Actions [#41060455276](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41060455276) に保存。造形出力ステップ成功、当初の連結検査はGLBの法線/UV分割により偽陽性FAIL。
- 元GLBを独立再読込し、同位置頂点を結合して実際には**1つながりの閉じた歩行体**であると確認。入口/展示/研究/交通床の接触を各2頂点検証。20三角面を除去した破壊試験では2成分。**実行済み再現CI [#41063490476](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41063490476) SUCCESS**。機能の安全認証はしていない。
- **ART：REJECT**。10視点の実画像で、薄板・箱・壁・折れた梁と小さな断片の羅列、内部視点の遮蔽、公共文化の可読性欠如を確認。E0現形状は詳細化STOP。
- SOURCE TECH：独立実GLBに限る限定PASS。FUNCTION：未認証。正式ART採択0。正式main/M247-C/W0/H1-H6/SB01-SB16/Minecraft正式ワールド変更なし。
- GitHub採択済みCITY MASTER 3D FIRST方針：一般建物の私的内部以外、約10km都市全域の詳細・編集可能・統合実3D完成までMinecraft施工HOLD。

## E0の真正出典
- 原本コード：`D47_R18_NATIVE/r18_first_lived_civic_e0.py`
- 技術監査：`D47_R18_NATIVE/r18_glb_independent_route_qa.py`
- CIアーティファクト：[#12979820538](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41060455276/artifacts/12979820538)（期限付き、約14日）
- 独立成功QA：[#12982380736](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41063490476/artifacts/12982380736)
- 正規研究記録：`D47_R18_REVIEW/R18_E0_TRUE_10VIEW_ART_REJECT_AND_INDEPENDENT_GLB_AUDIT_JA.md` と `R18_E0_INDEPENDENT_GLB_TOPOLOGY_AUDIT.json`

## 次の真の研究 — E1
研究案：`D47_R18_REVIEW/R18_E1_ART_RESET_DESIGN_BRIEF_JA.md`。

**一つの公共生活空間が入口の人間視点から十分に美しく感じられるよう、巨大公共空洞、採光、文化・研究活動、厚い都市地盤、実際の移動を一体の空間として実3D造形する。**
E0の小箱・梁やR17の大アーチ・15層反復をコピーしない。3つの真正3D視点（入口・斜視・背面）で初期審査し、**ART未達ならSTOP**。既存R18-E0形状の小物追加禁止。幾何QAは独立負の検査を継承。

**運用**：Chat中心。GitHub隔離研究ブランチで証拠を残し、独立AIの原本・正式mainは上書きしない。Work/PC操作は事前明示承認制。有料外注なし。工程成功・美術成功・正式採択を混同しない。

---

## 2026-10-30 新ブランチD47-R18-E1の実行済み追補

- **E1研究ブランチ**：`research/r33-s27-d47-r18-e1-civic-void-art-20261030`。E0研究branchから切り分け、旧E0原本には無変更。
- **新造形**：《光潮の交界院》E1-G0。E0のメッシュ流用なし。公開文化・研究・高所交通が同じ空洞を囲む厚い都市地盤の試験。Blender 4.5.15 LTSの編集可能な実BLEND・GLB・入口/斜視/背面の真正3視点を作成。
- **[作成・再読込CI #41066891031](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41066891031)：SUCCESS。** 24メッシュ・342頂点・556三角面、三視点相互に固有。これは美術品質の代理ではない。
- **[実物3視点の美術審査](https://github.com/ryomashibaba/celestial-halo-9/blob/research/r33-s27-d47-r18-e1-civic-void-art-20261030/studies/M3D-1S/J7/R33-S27/D47_R18_E1_REVIEW/R18_E1_G0_ACTUAL_THREE_VIEW_ART_REJECT_JA.md)：ART REJECT。** 巨大岩塊・板・浮遊帯・黒い壁/空洞が支配し、文化研究交通の内部体験は視覚的に成立しなかった。E1-G0現形状の細密化は禁止。
- **[E1真正3D原本の恒久保存CI #41067470222](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41067470222)：SUCCESS。** `D47_R18_E1_EVIDENCE/R18_E1_G0_REAL_BLENDER_3VIEW_ART_REJECT_SOURCE.zip` にBLEND/GLB/3PNG/JSON、隣にSHA256台帳を研究ブランチへ保存した。Actionsの一時保管失効後も研究用原本を参照できる。
- **FUNCTION：未認証。** 低位文化通路の計画勾配だけで建物全体への連続アクセスを証明したとは言わない。高所床の連続移動、障害物、手すり、避難、リフト、構造などは未証明。
- **次工程はE2の制作方式変更。** 単純な`prism/loft/ribbon`の組立順序を変えても効果が薄いことがE0/E1で実画像により確認された。入口の人間視点、文化研究活動、厚い地盤・空洞、建物の表裏を同時に設計する制作法を最初に検討し、3Dとして美術的な飛躍を実証するまで巨大屋根・街区を量産しない。

**不変境界**：正式美術採択0／main・M247-C原本・R17研究・E0研究の書込なし／約10km全域の編集可能詳細City Master完成前はMinecraft正式施工HOLD／Workは明示承認制。
