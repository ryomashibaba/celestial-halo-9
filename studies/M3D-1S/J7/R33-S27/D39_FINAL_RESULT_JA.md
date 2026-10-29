# CELESTIAL HALO-9 — D39 真正Blenderネイティブ検証最終報告

日時: 2026-10-29 JST
研究ブランチ: `research/r33-s27-d39-blender-axis-mesh-20261029`
**真正CI成功の対象コミット**: `5b7c6e2fb31de940f1add05f66477239f1fda624`
GitHub Actions: https://github.com/ryomashibaba/celestial-halo-9/actions/runs/40850025547
Run ID: `40850025547` / Job ID: `123366905515` / push / completed / success

## D37・D38の確認済み失敗と原因
- D37 run `40842844700` は、本物のBlender保存と再読込まで進んだが、GLBのメッシュ名に `.001` および `_BAKED_DATA` が付加されたため形状比較FAIL。
- D38 run `40844381800` は、第三BlenderプロセスでShape Keyと独立参照の座標差が1109.1181mとなりFAIL。
- 原因は、TrimeshのGLB座標とBlenderのネイティブZ-up座標の比較に固定の軸変換が欠けたこと、および一時エクスポートメッシュのデータ名衝突。D39ではGLB→Blender変換を `(x,y,z)->(x,-z,y)` として明示し、読み込み側／検証側で独立に照合。元オブジェクトのデータ名を隔離してからGLBに元のメッシュ名を与える。

## 真正D39 CI結果（予測・静的テストではない）
- Ubuntu 24.04 / Python 3.11.17 / genuine bpy 4.5.15 LTSの実行成功。
- 入力GLBからネイティブ `.blend` 保存成功。
- 別のbpyプロセスによる保存済み `.blend` 再読込成功。
- さらに別の第三bpyプロセスで、Shape Key値・基準メッシュ・保護形状・GLB形状を独立照合成功。
- GLB→Blender入力軸の誤差: `0.0 m`。
- 保存されたBasisの独立参照との軸誤差: `0.0 m`。
- 造形Shape Key最大点群誤差: `0.00006139790456214765 m`（約0.0614mm、閾値0.05m）。
- 対象 `D37_SCULPT_TARGET` 5120面、保護 `D37_PROTECTED_FLOOR` 12面、`D37_PROTECTED_MARKER` 12面について、独立GLB比較の頂点集合最大誤差 `0.0m`、相対面積誤差 `0.0`、相対体積誤差 `0.0`。
- D38の偽陽性防止テスト: 8種類すべて不正を拒否。旧D37の偽PASS再現も確認。
- すべてのJobステップ成功、真正GitHub Actions最終結論 `success`。

## 実出力の監査識別子
- 真正保存済み `.blend` SHA256: `77b1dee0602ae2d887a27ad655e07a0736e9d6fa70c3c307147bd301d4e7d66e`
- 真正Blender出力GLB SHA256: `54c576aecdcaa405f4844b46458bcba59415e73ab546abb21b78690fbe676daa`
- Actions artifact ID: `12886826525`
- Artifact: `HALO9-D39-AXIS-AND-TOPOLOGY-TECH-NOT-ART`
- ZIP size: `380628 bytes`
- ZIP SHA256: `db465e3ee71d49139a932aec31319936a1eed7b93dd06343271a8fac299ac30a`
- Artifact URL: https://github.com/ryomashibaba/celestial-halo-9/actions/runs/40850025547/artifacts/12886826525
- **保存期限注意**: Actions artifact保持設定7日間。研究Gitのコードとこの記録は残るが、artifact内バイナリの長期保存を保証しない。

## 判定・禁止事項
**D39: TECH LIMITED PASS / BLENDER NATIVE VERIFIED（対象は中立テスト形状のみ） / ART NOT SUBMITTED / 正式採択0件 / CITY MASTER 3D未完成 / Minecraft施工HOLD。**

本CIは真正なBlender APIを使う保存・再読込・Shape Key・GLB一貫性の技術的実証。Blender GUIの視覚フィードバックに基づく自由美術造形、中央建築品質、公共空間成立、都市全域設計は未実証。単発の編集はD40の視覚反復能力の実証に代替しない。

main・M247-C正式原本・保護研究ブランチ・Minecraftワールドは未変更。Workは使用していない。

## 次工程 D40
- 保存済みの真正3D成果から同条件の6〜8視点（遠景と人間視点を含む）を生成し、失敗した巨大箱・岩塊・棚の反復を避ける。
- 画像批評→編集可能な実3Dの直接変更→再読込→同視点再審査を最低2回繰り返して、制作方法が美術的に改善できるか実証する。
- 形態・巨大公共空洞・居住生活・上下交通の関係を早期評価し、ART REJECTなら詳細化を停止する。
- Minecraft正式施工と中央正式美術採択は引き続き禁止。

注: この結果報告だけを追加する後続コミットはCI検証対象コミットそのものではない。合格判定は上記SHAのコードにのみ対応する。
