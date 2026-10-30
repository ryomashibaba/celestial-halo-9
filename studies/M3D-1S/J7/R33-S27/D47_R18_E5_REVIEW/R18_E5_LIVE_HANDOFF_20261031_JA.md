# CELESTIAL HALO-9 / CELESTIAL SPINE — D47 R18 E5 LIVE_HANDOFF
**2026-10-31 JST／独立E5研究／G1実物監査完了／正式中央採択ゼロ**

## 絶対に動かさない全体計画
- 最高水準の美しい、居住の実体が感じられる約10kmの超未来文明都市。初期研究はAIが作りやすい形・Minecraft仕様に美術を妥協しない。神聖80%／危険・異常20%の中央M247-C《浮断天核》、α双殻浮断＋β斜裂天脊、W0、H1〜H6、SB01〜SB16、HERO4、V1〜V3を保護。
- 一般建物の個々の私的室内のみ簡略化可。**すべての一般建物の外観を含む都市全域・巨大公共建築の全内部・交通・広場・地形・素材・照明の詳細な編集可能・統合済City Master実3Dを先に完成**。その後も別途明示承認がなければMinecraft施工HOLD。
- main、M247-C正式原本、過去の研究ブランチ、Minecraftワールド、保護都市情報への書込・無断マージ禁止。Work/ユーザーPC操作の新たな明示承認なし。外注なし。SOURCE TECHとFUNCTIONとARTと正式採択は必ず別。

## 歴史（再現失敗を誤って成功に変えない）
- E0：小パビリオン、無地板、巨大壁。SOURCE TECH限定PASS、ART REJECT。
- E1：巨岩・細帯。SOURCE TECH限定PASS、ART REJECT。
- E2：峡谷状の大壁・細柱。SOURCE TECH限定PASS、ART REJECT。
- E3：公共資料棚・研究活動が実3Dに初めて見えたがU字図書館スタジアム。SOURCE TECH限定PASS、ART REJECT。
- E4：非対称な左右大岩板＋光帯。SOURCE TECH限定PASS、ART REJECT。
- E5はこれらの不合格形状を細密化・流用せず、新しい**実BLENDを見て編集する方法**を小さな公共室で単独検証。

## E5 G0（実画像を見るまで編集案を決めない）
- ブランチ `research/r33-s27-d47-r18-e5-blend-visual-feedback-20261031`。
- 作成コード `D47_R18_E5_NATIVE/e5_generate_independent_baseline.py`。
- [G0真正CI #41081229554](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41081229554)：**SUCCESS**。Blender4.5.15、40メッシュ、編集可能BLEND `E5_G0_NEW_PUBLIC_ROOM_BEFORE_EDIT.blend`、実4カメラBEFORE PNG、QAを出力。元BLEND SHA256 `5879743ef3c305b30db6c5c1aa3be08c50de83d89a313eee839315e8bb458e4a`。
- 4画像を実際に見て、青黒い壁 `E5_SOURCE_EDITABLE_MAIN_VEIL` が入口・室内の視界を大半覆って文化展示を隠す問題を発見。G0はART REJECT。具体的な編集決定を `D47_R18_E5_REVIEW/E5_G0_REAL_FOUR_CAMERA_VISUAL_DECISION_JA.md` に先行記録。

## E5 G1（本当に同じ原本を実編集）
- 編集コード `D47_R18_E5_NATIVE/e5_edit_reopened_real_blend.py`。
- [G1真正CI #41128671614](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41128671614)：**SUCCESS**。**G0保存済みの元BLENDを再読込**して、同一の既存壁メッシュの中心下部から24面を除去、48→24面、頂点は63のまま。作り直した別のBLENDではない。
- 他39メッシュの頂点/面ハッシュ不変、4カメラの行列/焦点距離/投影設定不変、G1の保存BLENDとGLBの独立再読込成功、同4視点のすべてでBEFOREとAFTERの画像差分を検出。
- G1 BLEND SHA256 `92ddede724eb04775318bbe3336c72d25bcc727876297267b0935873059b764b`。真正G1 Actions artifact [#13012456080](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41128671614/artifacts/13012456080)。G0 artifact [#12989418704](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41081229554/artifacts/12989418704)。
- 同4視点の目視で、入口と内部から本物の研究展示が新たに見えるようになったのは事実。ただし原型は依然として単純な梁・展示柱・室内床。**方法のSOURCE TECH限定PASS、作品ART REJECT、FUNCTION未認証**。
- 実物と写真による厳格評価は `D47_R18_E5_REVIEW/E5_G1_TRUE_SAME_BLEND_BEFORE_AFTER_ART_REJECT_JA.md`。

## 恒久保存と続行
- 期間付きGitHub Actionsアーティファクトを消失させないため、両原本＋8PNG＋両QAのSHA256付き研究専用ZIPを保存するCI [#41128995851](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41128995851) を登録。**この文書作成時点で成果の完了は未確認**。SUCCESSとなったら `D47_R18_E5_EVIDENCE/R18_E5_G0_G1_TRUE_NATIVE_BEFORE_AFTER_ART_REJECT.zip` と `R18_E5_G0_G1_HASHES_AND_DECISION.json` の実在・コミットを確認。
- 次は、技術方式が成立したことを活かし、**美術作品として真に独創的な実3Dへ**観察→大きな主形状編集→多視点で確認する短サイクルを改良する。小さな黒い幕に穴を開けたE5原型をそのまま装飾して正式採用しない。
- 最新HEADはGitHubの実refを別途照合する。現在の正本は常に `main:docs/policy/START_HERE.md` および `PROJECT_CONSTITUTION.md`、`CITY_MASTER_3D_STANDARD.md`。
