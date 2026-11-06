# CELESTIAL HALO-9 — INT14 H1固定人間視点・真正公共入口切削、独立検証、画像直接批判審査

**基準：2026年11月6日 JST。これは正式方針の変更・新規企画・ART採用ではない。**

## 総合判断

**SOURCE PASS / TRUE NATIVE EDIT PASS / 独立BLEND再読込 PASS / 実レンダー4枚 PASS / H1閉塞実測改善 PASS / ART REJECT / 実歩行 FUNCTION UNKNOWN・勾配上の重大未解決 / 正式ART採用0 / 完成0/30 / Minecraft正式施工HOLD。**

main `AGENTS.md`、`docs/policy/START_HERE.md`、`PROJECT_CONSTITUTION.md`、`CITY_MASTER_3D_STANDARD.md` を確認。**ART-FIRST／Macro Impact First／CITY MASTER 3D FIRST**、M247-C《浮断天核》のα双殻浮断・β斜裂天脊、約10km級全都市30対象の詳細編集可能実3D完成義務は一切変更しない。一般建物の私的室内以外の詳細要件を緩めない。

## 1. 実制作と保護

- 直前のINT13研究ブランチの確定HEAD `927eedbf54a2e05eeeae66b3088bf3acd5c072f8` から、**新しい隔離ブランチ** `research/r33-s27-d48-int14-h1-entry-public-section-20261106` を作成。
- INT13真正編集可能BLEND展開SHA256 `da098354430d0aa62d0f4825c23127340aba8e8c353c6dc33f53c5b8b0fec3c3` のコピーを照合して使用。main・旧研究・Freeze・Minecraft正規ワールド・原本を変更していない。
- 対象の不採用研究メッシュは `INT13_H1_OCCUPIED_SCHOOL_MARKET_COMMONS_MASS` だけ。元E11_H1_HUMANの目の位置に完全に重なっていた実建築を、既存の市場・学校公共入口へ接続する**幅のある連続負空間**として直接Boolean切削した。新しい通常ビル／独立巨大外殻／棚を足していない。
- H1研究メッシュは**33面→108面**。元E11_H1固定カメラの25本の実レイのうち、当該建築に衝突するものが**25本→4本**に減った。中心レイは当該建築に22.413mで衝突→161.889m先の既存市場→学校ルートに衝突。したがって**元の直接閉塞は実形状で解消**したが、室内視界全体は未解決。
- 真正BLEND SHA256 `431f5d1845f04a7fa669e2e230e00298cfedd98ee3d3069eb36c3fc85a7a6146`。元E11 NAVE/H1/俯瞰3カメラ行列とW0北山・断崖・地盤・人工内海の頂点SHAは変更なし。
- Blender 5.2.1公式SHA検証、真正3D編集・保存、**別のBlenderプロセスによる独立再読込**、4枚の真正CyclesレンダーのPNGヘッダー・画像SHA照合、旧急勾配の未認証保持。GitHub Actions [#42191633999](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42191633999) **completed/success**。
- 実行はBlenderバックグラウンドのネイティブBoolean編集であり、**Blender GUIでの手彫りではない**。コードの実行成功は美術採択・全体完成ではない。

## 2. 実画像直接評価（絶対にARTを偽装しない）

[4視点実レンダー](https://github.com/ryomashibaba/celestial-halo-9/blob/research/r33-s27-d48-int14-h1-entry-public-section-20261106/studies/M3D-1S/J7/R33-S27/INT14/evidence/INT14_FOUR_TRUE_FULL_SCENE_VIEWS_UNREVIEWED.jpg) はすべて**旧不採用巨大殻も表示した本来の統合研究シーン**で撮影。救済用CUTAWAY表示ではない。

- **E11_H1_HUMAN**：INT13で全面暗い壁だった画面に奥行きと複数の物体が現れた。ただし濃色の前景と面積の大きい灰・茶の量塊が残り、学校・市場・街路・住居が一体の厚い都市として読み取れない。平均明度42.6→59.767は視認性の数値でありART合格ではない。
- **E11_NAVE_HUMAN**：巨大な板、路面・壁に見える不採用形状が引き続き支配。公共駅・図書館・儀礼堂の巨大内部という体験は成立していない。
- **E11_URBAN_AERIAL**：二つの巨大な卵状殻＋細い架構、低密度の背景が残る。M247-Cの迫力ある斜裂と双殻、W0との統合都市のスケール階層は未達。
- **追加H1内部**：空洞と下部空間の一部は見えるが、市場・教育施設・生活街区としての明快さがない。

**ART REJECT**。表面の穴開けや画像明度改善を巨視的な建築品質の改善と取り違えない。

## 3. 新たに明らかになった閉塞の構成

E11_H1 25レイのINT14後の物理命中先（複数）：
- INT13市場内部床：5本
- INT13市場→学校ルート：4本
- INT13旧H1母体：4本
- INT11旧市場棟：4本
- INT4旧市場接続と公共中庭の壁・ブルバード：計5本
- INT13学校内部床：1本

旧INT4/INT11研究構造物とINT13の新たな公共施設が互いに重なり、**異なる世代の不採用形状を共存させたまま穴を開ける方式は限界**。既存市場→学校ルートの勾配も**37.932%**と急で、元のH1共用→居住区は**66.885%**。9経路中8経路が12%を超える。物理的な昇降機・階段・歩行ナビゲーションは未検証で、**FUNCTION PASSを主張しない**。

## 4. 次工程の固定判断（新方針ではなく失敗修正方針）

1. 今回成功したのは**目の前の閉塞を本当に取り除くTECH**に限る。既存殻をさらに穴だらけにすることも、遮蔽物を都度横へずらすことも**次の本質的ART工程としては繰り返さない**。
2. NAVEの公共室とH1の居住都市を、周辺の古い研究物体の干渉から一度独立して造形するための**単一の代表統合断面を直接美術制作する実方法**が必要。旧研究の混合状態を正式原本へ持ち込まない。しかも元E11固定3視点、俯瞰、内外、W0側を同時に見る。
3. H1内部は連続水平歩行の仮定が破綻。今後の制作物には到着駅、昇降手段、実際の乗降階、公共室、学校、市場、住居という動線関係が**立体として成立すること**を必要条件にする。今の9本の端点グラフを「歩ける」とは呼ばない。
4. 数式・Bezier・Booleanの意味のない小修正、QAの量産、ギャラリーの演出変更では正式ART改善にならないため中止。必要な制作能力が現行Chat/GitHubのみで不足する場合は、その実際の境界を誠実に説明し、Work/Computer Use・ローカルMCPはユーザーの都度明示承認の範囲だけで行う。
5. 完全なCITY MASTER 3D完成義務30対象は不変。研究ARTは正式採用0件、完成0/30、Minecraft施工HOLD。追加有料API未使用・ユーザー操作0回。GitHub Actions残り無料枠／請求実態までは確認していない。

### 保存参照

- [編集可能真正BLEND](https://github.com/ryomashibaba/celestial-halo-9/blob/research/r33-s27-d48-int14-h1-entry-public-section-20261106/studies/M3D-1S/J7/R33-S27/INT14/evidence/HALO9_INT14_H1_PUBLIC_ENTRY_HUMAN_SIGHTLINE.blend.gz)
- [4固定・補助同一3Dレンダー](https://github.com/ryomashibaba/celestial-halo-9/blob/research/r33-s27-d48-int14-h1-entry-public-section-20261106/studies/M3D-1S/J7/R33-S27/INT14/evidence/INT14_FOUR_TRUE_FULL_SCENE_VIEWS_UNREVIEWED.jpg)
- [独立検証・全25レイ証拠](https://github.com/ryomashibaba/celestial-halo-9/blob/research/r33-s27-d48-int14-h1-entry-public-section-20261106/studies/M3D-1S/J7/R33-S27/INT14/evidence/INT14_INDEPENDENT_TECH_NOT_ART.json)

**最終：INT14 SOURCE/REAL BLEND/INDEPENDENT RENDER TECH PASS、視認性部分改善、総合ART REJECT、FUNCTION UNKNOWN/急勾配未解決、正式採用0／0/30／Minecraft HOLD。**
