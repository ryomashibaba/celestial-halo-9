# CELESTIAL HALO-9 — D47-R18-E6 LIVE HANDOFF
**2026-10-31 JST／研究専用・正式美術採択0／CI実行結果は必ず確認すること**

## 一切変更しない最上位の原則
- ユーザーの目標は約10kmの圧倒的に美しい実生活のある超未来文明都市。先に全域の詳細・編集可能な統合 City Master 3Dを完成（省略可能なのは一般建物の私的室内のみ）、その後も別途明示承認がなければMinecraft施工HOLD。
- M247-C《浮断天核》α「双殻浮断」＋β「斜裂天脊」／W0／H1–H6／SB01–SB16／HERO4／眺望軸は無変更。main、保護3D、Minecraftワールド、R17〜E5の過去研究原本には書き込まない。Work/ユーザーPC利用は新規の明示承認なし。有料外注なし。
- SOURCE TECH、FUNCTION、ART、正式採択を絶対に同一視しない。

## E5までの厳格な実績
E0〜E4はすべてART REJECT。E5では本物のG0 BLENDを再読込し、同一メッシュ48面→24面の開口編集・他39メッシュの不変性・同一4カメラ画像・BLEND/GLB再読込をGitHub Actionsで再現した。E5技法のみ限定TECH PASS、E5作品ART REJECT、FUNCTION未認証、正式採択0。
E5研究HEAD（分岐元）`6a04ab2e060036fc3abab4dd97db6c34df849809`。

## 今回E6で行った実作業
新研究ブランチ `research/r33-s27-d47-r18-e6-native-art-directed-20261031`。E5の不採択メッシュはコピーしない。

1. `D47_R18_E6_NATIVE/e6_make_new_inhabited_fissure_g0.py`：真正Blenderによる**別の非対称な居住型の公共空洞**の新規実3D制作ソース。文化資料室、公開研究広場、高所交通床、左右非鏡像の彫刻的質量を設計。西の主造形オブジェクト `WEST_INHABITED_FOLD_EDITABLE` は7リング×6頂点＝42頂点・38面で、次段の実編集対象。
2. `.github/workflows/d47-r18-e6-g0-native-art-baseline.yml`：[CI #41129504031](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41129504031) で、編集可能な実BLEND+GLB、地上入口・文化展示・西資料室・斜視・背面の5実PNGを生成し、独立読込とSHA256で確認する。最初の起動 `#41129433789` は面数QA閾値を正すためconcurrencyでキャンセル。**現時点で #41129504031 はGitHubランナー待ちの pending/queued**。画像を見ておらずART判定不可、BLEND生成成功も未確定。
3. `D47_R18_E6_NATIVE/e6_edit_same_native_fold_after_review.py`：次のG1でG0の**本物の同じBLENDを直接開き、G0実画像の観察に応じた変更量で主形状の既存頂点を動かす**専用編集器。非対象メッシュ全ての頂点/面ハッシュ・5実カメラ行列を不変に保持する設計。**編集器保存は編集実施・技法成功の証拠ではない**。
4. `.github/workflows/d47-r18-e6-g1-real-visual-edited-main-form.yml`：G0原本artifactからG0を取得し、**G0画像を実際に見てから作成する** `D47_R18_E6_REVIEW/E6_G0_TRUE_5VIEW_VISUAL_DECISION.json` のコミットでのみ起動。元のBLENDの既存主造形のみ編集、編集後BLEND/GLBと同一カメラ5対の画像、独立QAを出力。
5. `D47_R18_E6_REVIEW/E6_G0_VISUAL_ART_GATE_JA.md`：事前の厳格な視覚・機能・保存境界を記録。

## 次の実作業 — 順序厳守
1. #41129504031の実際の最終結論・ログ・Actions artifactを確認。FAILなら原因を特定して直す。queueのままなら成功を装わない。
2. G0 SUCCESSなら原本の真正5PNGを取得して**実際に見る**。入口・文化・アーカイブ・斜視・背面の「何がどこを遮るか」「左右質量の美術」「都市との接続」「公共室の活動」が見えるかを具体的に批評。G0のARTは良いと確認できるまでHOLD/REJECT。
3. G0 BLENDの実SHA256、真正5画像と観察理由、7リングのどの部分をどう変えるかを `E6_G0_TRUE_5VIEW_VISUAL_DECISION.json` に保存。これがG1起動トリガーとなる。**画像未確認のまま適当にG1編集の値を決めない。**
4. G1の同一原本BLEND直接編集の結果、他メッシュ不変、同一5視点、独立BLEND+GLB再読込を検査。実画像で前後を批判的に比較。視認性向上だけでART PASSにしない。
5. いずれも現状の非公式研究。巨大都市原本への採択・Minecraft施工禁止。

**現時点の正式状態：E6制作コード/CI/実編集器/審査ゲートはGitHub保存済み。G0実モデル出力・G1直接編集・美術評価は未確認。E5作品ART REJECTのまま。**
