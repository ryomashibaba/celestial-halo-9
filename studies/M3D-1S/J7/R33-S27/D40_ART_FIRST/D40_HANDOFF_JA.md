# CELESTIAL HALO-9 — R33-S27-D40 短い引き継ぎ

**確認基準** 2026-10-29 JST
**変更対象** 新規隔離ブランチ `research/r33-s27-d40-art-first-city-sculpt-20261029` の研究文書のみ。main、D37/D38/D39原本、M247-C、保護アセット、Minecraftワールドは変更していない。
**main確認済みHEAD** `a2f88995eee8d10ee4830dbdf33ccb9c0790de8f`
**継承時のD39 HEAD** `acfaa1bdc5446d75f51c73c05157cf949ec7c2aa`
**D40指示・実験仕様の保存済みコミット** `5212e99df7f820d35cefc401a38d7237eebc4b99`, `a0a2031267b740529a9fb9e8054ccf1191ea5d53`。**本ファイルを含む最新HEADはGitHubで取得すること。**

## 技術の真正結果
D37 https://github.com/ryomashibaba/celestial-halo-9/actions/runs/40842844700 => GLBメッシュ名称不一致でFAIL。
D38 https://github.com/ryomashibaba/celestial-halo-9/actions/runs/40844381800 => Shape Key glTF/Blender座標軸照合不一致1109.1181mでFAIL。
**D39** https://github.com/ryomashibaba/celestial-halo-9/actions/runs/40850025547 => genuine Blender 4.5.15、.blend保存・別プロセス再読込・第三プロセス幾何比較を本物のActionsでSUCCESS。
D39成功コードはコミット `5b7c6e2fb31de940f1add05f66477239f1fda624`。メッシュ名を**無条件に無視せず**名前衝突を修正。入力座標軸0m、Shape Key点群最大誤差0.0000613979m、3メッシュの頂点集合・面積・体積差0。8負例すべて拒否。
ただし全メッシュの数学的水密性・都市内公開経路・建築構造安全性・美術成功を証明したものではない。

## 実3Dの確認
GitHub artifact `12886826525`（2026-11-05頃まで保持予定、期限変更の可能性あり）を本チャットで実際にダウンロード。ZIP SHA256は `db465e3ee71d49139a932aec31319936a1eed7b93dd06343271a8fac299ac30a` とGitHub表示に一致。内部のBLENDおよびGLB実在を確認。GLB SHA256 `54c576aecdcaa405f4844b46458bcba59415e73ab546abb21b78690fbe676daa` が報告値と一致。
GLBをTrimeshで読込み、VTKによる斜視レンダーを観察。球卵形マクロと薄い床・小さい直方体のみ。これは**中立技術試験**であって、数km居住都市、斜裂主公共空洞、多層交通、都市景観を備える中央候補ではない。従って美術はNOT SUBMITTED、正式採択しない。**既存卵形を装飾・細密化しない**。
※斜視画像はBlenderによるD40同条件レンダーではなく、真正D39 GLBのVTKプレビュー。D40のBASE/EDIT同条件レンダーは未作成。

## 新方針
`D40_ART_FIRST_DIRECTIVE_JA.md`：美術最優先、巨大な中央外形×数百m公共・居住空間×10km都市を同時に実造形。技術QAは下限条件。
`D40_ART_TEST_BRIEF_JA.md`：新規造形の8固定カメラ・BASE/EDIT1/EDIT2視覚ループ・真のBLEND編集・早期ART停止ゲート。Claude C55-Fとは評価基準のみ共有し意匠独立。

## D40現在判定
**D39: TECH LIMITED PASS / BLENDER NATIVE VERIFIED（中立形状のみ）**。
**D40: ART NOT SUBMITTED / 実編集同条件レンダー NOT RUN / 正式中央美術採択0件 / CITY MASTER 3D未完成 / Minecraft施工HOLD**。
研究方針と視覚評価規則の文書化は完了したが、D40実造形・反復・8視点比較を実証したと主張しない。

## 次に直接やること
まず完成した都市を想像してから、中心の外殻と居住文明を同時に構想・モデリングする。新しい隔離BLENDにW0/H1–H6/SB全体の粗い同一座標関係、数km中央、数百m公共居住空間を含める。BASE8視点を実際に見てから編集し、同条件EDIT1/EDIT2まで少なくとも2反復。宏観で板/フィン/棚/卵/岩/低層普通施設なら詳細化せずREJECT。改善の証拠が出た場合のみ精密化。
Workは明確に有利な作業範囲を説明しユーザー承認を得るまで使用禁止。Chat中心で進める。
