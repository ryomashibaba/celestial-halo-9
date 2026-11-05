# CELESTIAL HALO-9 — R4-E9 / R1 統合真正BLEND直接編集・美術審査記録

**2026-11-05 JST / 技術：PASS / 美術：REJECT / 正式ART採用0件 / 全30対象完成0件 / Minecraft正式施工HOLD**

## 目的と制作の境界

- 正式方針：mainのART-FIRST、CITY MASTER 3D FIRST。一般建物内部を除く都市全域と中央・NAVE・H1・W0の詳細な編集可能3Dを施工前に完成させる条件を変更しない。
- E8 ART REJECTから、同じ箱を大量生成する方法を停止。R4-E9では**E8の圧縮保存済み編集可能BLENDのバイナリSHA256を独立検証し、真正Blender内で直接メッシュを修正**した。単なる新規Pythonモックの量産でもカメラ変更のみでもない。
- E9原本、E8原本、既存のE2〜E7、Freeze、canonical、main、Minecraftワールドを変更していない。実3Dは研究専用座標で、正式Minecraft座標には未対応。
- Work、Computer Use、ローカルPC操作、有料APIは未使用。使用の際はユーザー事前明示承認が必要。

## E9の本制作：真正3D TECH PASS
- Actions [#42028877887](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42028877887) 成功。
- E8保存BLENDのSHA256：a2ea634f4df04226cf089419110bbb3b8986789f2d49c8b7a5d16bb0f0a9b7c6。
- E9保存BLENDのSHA256：3b5d22960fd9fc6c8b28db915ae5dc3ba0d02e91d970c0fe4cac260258471697。
- 同一の3視点で修正前後計6枚の真正Blender PNGを生成、別プロセスBlender再読込に成功。
- 大規模構造メッシュ2件の立体外形変更、6件の3D Boolean貫通開口、H1視界遮断物の撤去・配置変更、NAVEとH1公開用途の実メッシュ追加。
- **直接美術審査では不合格**。NAVEの市民公共室が一般的な長い街路に見え、中央外形は矩形基壇中心のまま。H1のafterは真っ黒だった。これは視点内に後付けした公開歩道の上面が位置したためで、単なる未読込やレンダー失敗と混同しない。E9 R0 の三視点比較画像を研究ブランチに保持し、成功扱いしない。

## E9-R1：実画像を見た直接再編集とTECH PASS
- 失敗した初回 [#42029759447](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42029759447) は Blender位置変更後の評価更新を待たずカメラ境界を判定した結果、AssertionErrorで安全停止。これも記録し、成功扱いしない。
- 更新後、真正Blender Actions [#42030036959](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42030036959) **SUCCESS**。
- E9の実保存BLENDの**コピーを開いて直接変更**。H1公開歩道を研究z=845mから約839.4mへ下げ、元の歩行者カメラ位置のまま約1.7mの視点余裕と支柱4本を付与。カメラのワールド行列は変更なし。
- 修正前H1と修正後H1＋修正後NAVE＋都市俯瞰のPNGを同一Blenderシーンからレンダリングし、別Blenderプロセスの独立再読込・PNG寸法／SHA照合・実形状変更の確認に成功。
- 永続証拠：e9r1_evidence/E9R1_TRUE_SAME_BLENDER_CORRECTED_CITY.blend.gz（編集可能真正BLEND圧縮）、E9R1_TRUE_H1_BEFORE_AFTER_NATIVE_4VIEW.jpg（実画像4視点の連結）、E9R1_TECH_NOT_ART.json。元PNGと元BLENDはActions Artifact ID 13416340777（7日間保持）。

## 直接ART審査 — REJECT（技術と混同しない）
1. **H1：** R1では黒い画像が解消し、人間視点に建物壁と交通構造が実在することを確認。ただし大きな橋／壁が画面を支配し、厚い居住都市の内部街路、屋外生活、学校・住宅・公共機能の建築差異が分からない。世界水準の高所都市には未到達。
2. **NAVE：** 公開歩道が視認できるが、数百m級の独創的巨大内部公共室ではなく、両側に箱建築がある普通の広い道路に近い。
3. **都市俯瞰：** 6つの貫通穴は実メッシュ改修として存在するが、中央・H1・W0がひとつの超未来文明建築の圧倒的な都市景観として読めず、巨大な長方形基壇2本と反復小建物に見える。
4. 検査結果や保存ファイルの存在を正式ART採用と主張しない。**E9、E9-R1の美術合格0件**。30対象の構造はまだ登録用プレースホルダーが中心であり、完成0件。Minecraft施工はHOLD。

## 批判的な次工程方針（従来の固定方針は変更しない）

E6〜E9R1から、単純な一括Python/Boolean/箱・道路・配列建築を何度も追加しても根本的な世界水準の中央美術を達成できないことが明確になった。小QA、監督器、ファイル数・レンダー枚数の増加を品質と見なさない。**次に同じ手法でE10の箱型建築を量産しない**。

まとまった制作単位は変えず、中央の公共空洞、NAVE、H1厚い生活都市、W0の地形と水際を**同じ大きな芸術的立体断面の中で直接彫塑**すること。明確な建築美術の視覚フィードバック（Blender GUI／実メッシュの手編集）に基づく制作ループが必要。旧R0B、E6〜E9の不合格外観を延命せず、反省点と技術資産のみを使用。

Work/Computer UseなどのGUI直接操作は事前明示承認が必要。今回の成果がそれを勝手に承認したことにはならない。正式ART採択0・CITY MASTER完成0/30・Minecraft施工HOLD・main/Freeze/原本保護を継承。
