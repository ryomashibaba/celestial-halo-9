# CELESTIAL HALO-9 — D47-R18 E4 完全LIVE_HANDOFF
**最終更新：2026-10-31 JST／研究E4／正式美術採択なし**

## 公式不変条件
正式方針：`main:docs/policy/PROJECT_CONSTITUTION.md` と `CITY_MASTER_3D_STANDARD.md`（原本を都度main明示refで確認）。約10km級、中央M247-C《浮断天核》（α双殻浮断＋β斜裂天脊）、W0、H1–H6、SB01–SB16、HERO4、主要眺望軸。全一般建物外観、公共巨大施設内部、全交通、地形、灯火等を**詳細で編集可能な統合City Master実3D**にしてからMinecraft施工を検討。Minecraft施工HOLD、main/正式原本/全旧研究原本保護。Work/ローカルGUIは毎回新規明示承認制。有料外注なし。ART・FUNCTION・SOURCE TECH・採択は別判定。

## E0–E3 の実画像での失敗
- E0：小さな断片と空白壁、真正BLEND/GLB／10視点。ART REJECT。実GLBでの位置統合と負の断裂テストという限定技術資産だけ継承。
- E1：岩塊・板・浮遊梁、BLEND/GLB／3視点。ART REJECT。
- E2：大峡谷の左右大壁と細柱、BLEND/GLB／4視点。ART REJECT。
- E3：実生活向けの公開研究台・資料棚等が初めて視覚的に現れたが、円形アリーナ・U字劇場に退化。G1の真正4視点でART REJECT。研究ブランチ恒久保管済み。

## E4 実際に作ったもの
- **新しいE4隔離研究ブランチ**：`research/r33-s27-d47-r18-e4-chiral-civic-nave-20261031`（E3最終HEAD `5be47cf94223e3cd245fac423f7b968bcc912345` から分岐）。
- 新規Blenderソース：`studies/M3D-1S/J7/R33-S27/D47_R18_E4_NATIVE/e4_chiral_civic_nave.py`。研究仮称《斜光の記憶路》、非対称な公開文化・研究・高所都市空間の原寸実3D試作。E0–E3既存造形再利用なし。
- [真正制作・独立再読込CI #41078220711](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41078220711)：**SUCCESS**。Blender4.5.15 LTSで **170 meshes／1,447 vertices／2,214 triangles** のBLEND+GLB、入口/文化広場/西アーカイブ/斜視/背面の真正5PNG、manifest、独立再読込監査JSONを生成。
- 保存元Actions artifact [#12988706049](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41078220711/artifacts/12988706049)。
- [真正5視点の厳格な美術評価](https://github.com/ryomashibaba/celestial-halo-9/blob/research/r33-s27-d47-r18-e4-chiral-civic-nave-20261031/studies/M3D-1S/J7/R33-S27/D47_R18_E4_REVIEW/E4_G0_TRUE_FIVE_VIEWS_ART_REJECT_AND_E5_METHOD_GATE_JA.md)：**ART REJECT**。非対称化自体はできたが黒い大質量、白い板、大きな無地床、細い帯が公共研究・文化活動を遮り、正背面とも独自未来建築にならず。現形状の細密化・ライト追加・窓追加は禁止。
- [真正原本恒久保存CI #41078701101](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41078701101)：**SUCCESS**。過去モデルの再レンダリングではなく、上記CIの本物のBLEND/GLB/5PNG/2JSONを読み込み、`D47_R18_E4_EVIDENCE/R18_E4_G0_TRUE_NATIVE_FIVE_VIEW_ART_REJECT.zip` (5,464,020 bytes)、`R18_E4_G0_EVIDENCE_HASHES.json` としてE4隔離研究ブランチにSHA256付きで保存済み。
- 最終：**SOURCE TECH限定PASS／FUNCTION未認証／ART REJECT／正式採択ゼロ／10km Master未完成／Minecraft HOLD**。
- E4で試みた「左右非対称＋採光の斜め裂け目」は美術品質を保証しなかった。形状を変えたことと造形が美しいことは別。

## 次の工程 E5：実物を見て編集する制作方式の試験

**同じ一括Python生成法で新しい大岩塊を何度も作らないこと。**

本当に必要な新技術：最初に実BLENDから人間視点を撮影→遮蔽と占有比率・建築の実生活が見えるかを具体評価→その実モデルを**実際に局所編集**→同カメラのBefore/After比較→改善の正否を複数視点と独立再読込で厳格確認。重要なのは人が見て価値のある造形が残ること。数値的な遮蔽の改善だけでもART PASSにはならない。

- E5は**E4の不合格形状を修復・正式化しない**。新たに隔離した少数の新規3Dモジュールで制作方式そのものを比較。
- 最初は巨大都市ではなく1個の強い公共室で検証。資料や研究の活動の読み取れる**人間視点**を最優先。主形状の編集で達成し、窓・装飾・発光は主形状の弱さを補わない。
- Work/実PC/Blender GUI操作にはユーザーの新規明示承認が必要。未承認の場合は隔離GitHub Actions上の本物のBlenderでBLENDを再読込・編集・同条件再撮影する方法を試せるが、単に一括生成を2回呼んだだけで新制作方法と偽らない。
- 必ずSOURCE TECH、FUNCTION、ART、採択を独立採点。アーティファクトを保存するだけのCI成功を美術向上と混同しない。

**実際のE4完了HEADはGitHubの研究refを確認**。E4外のmain/E3研究はこの工程では変更なし。G0の不合格形状は証拠として保存して終了。
