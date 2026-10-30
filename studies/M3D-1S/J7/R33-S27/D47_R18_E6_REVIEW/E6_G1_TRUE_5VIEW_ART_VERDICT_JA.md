# D47-R18-E6 G1 — 真正BLEND同一主形状のBEFORE/AFTER美術最終判定
**2026-10-31 JST／非公式独立研究／ART REJECT／正式採択0／Minecraft施工HOLD**

## 真正証拠
- G0成功CI：[#41131230334](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41131230334)。原本BLEND SHA256 `164f592a7a35408cb611774a0c0db919e5378f06d6d128c49531f863fea8aedf`。
- G1実編集CI：[#41131680045](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/41131680045)。**編集ステップは成功、独立QAステップはFAIL**（03_WEST_ARCHIVE_VIEWが完全に変化なし）。ワークフロー全体はFAILのまま。
- G1編集後BLEND SHA256：`b49ab607ecf5f34ce642a44bfdc5ad9521cd52aa3bc6091e3156579b57cc06b4`。編集後GLB SHA256：`e124d853c06202b4ae39bdc7aab48561642547fded18cd08181ef1dcd678ff19`。
- E6-G0の真正5視点を目視して編集値を決め、G1はそのRunからG0原本を取得して直接編集した。G1編集器監査はWEST_INHABITED_FOLD_EDITABLEの42頂点中28頂点を変更し、他メッシュと5カメラの不変を報告。独立3D再読込QAの完了は未認証。

## 固定5視点の画像比較（同一解像度1160×760、画素単位の差。差分率は美術品質指標ではない）
| 視点 | 差分画素率 | 目視評価 |
|---|---:|---|
| 01 HUMAN ARRIVAL | 20.9% | 左暗色外殻が移動したが、入口からの公共生活の訴求は弱いまま |
| 02 HUMAN CULTURAL ATLAS | 26.5% | 左側の質量境界は変化したが、柱状展示と薄い床の組み合わせに留まる |
| 03 WEST ARCHIVE VIEW | 0.0% | 完全に画像同一。資料室視点の遮蔽・見え方は改善せず |
| 04 CITY ANGLED | 15.8% | 西側外殻のシルエットが変わったが、二つの巨大塊と斜め帯が支配 |
| 05 CITY REAR | 7.0% | 西側外殻の形に差はあるが、主造形の結びつきと都市生活は弱いまま |

## 判定
- **SOURCE TECH：編集器の同一原本BLENDの直接28頂点変更と5枚生成は実行成功。元CIの独立QAはFAILであるため、独立SOURCE TECH PASSとは現段階で認定しない。**
- **FUNCTION：UNCERTIFIED。** 景観画像や接続面の一部だけでは機能全体の認証にならない。
- **ART：REJECT（G0・G1とも）。** 造形の比率、東西の接合、公共室と巨大空洞の関係、人間視点、斜視と背面を含む建築美術の質が不足。画素変化は美術改善と同じではない。
- **FORMAL ADOPTION：0件。CITY MASTER 3D：未完成。Minecraft施工：HOLD。**

## 開発方針への帰結
E6では、真正Blender編集技法の範囲と限界を確認できたが、最高水準の建築造形への改善を立証できなかった。E6の同じ外形を窓・照明・追加部材で延命しない。E7等で同様の簡易ロフト公共室を機械的に増産せず、**ART-FIRST／MACRO IMPACT FIRSTに戻り、中央M247-C・W0・H1〜H6・SB01〜SB16との都市全域の構成と、造形自由度の高い実3D制作方法**を優先して再設計する。既存の正式構成、main、保護原本は変更しない。

本判定は実際の5組の画像比較による美術評価であり、技術CIの成功を美術合格に読み替えない。
