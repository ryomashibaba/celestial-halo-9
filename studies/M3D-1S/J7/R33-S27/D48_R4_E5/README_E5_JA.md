# R4-E5 — R0Bの真正Blender 2視点制作ゲート

2026-11-05。これはE3/E4からの**継続**。研究作品の正式ART採用は0、CITY MASTERは未完成、Minecraft施工HOLD。

## 実際に実施・確認したこと

- GitHub `main` の正式方針とE3研究結果、E4ソースの一部を照合。
- E4 `1f4ff4e9dc67c60298f53981356b0f99559535dc` から**独立E5研究ブランチ**を作成。E2/E3/E4の既存制作・主原本を上書きしない。
- R0Bの人間視点ソース由来プレビューを観察。高所街路には水平梁・大きな支持地盤、NAVEには横桟と浅い公共空間がまだ目立つ。E4記録の評価はART HOLDであり、真正Blenderレンダーに基づく採択ではない。
- R0Bの**編集可能なBlender制作ソース全体** `author_R0B.py` を保存。原版SHA256: `97978dc77aa012fe77ce775931b44a8779861a9664df6347eff4024a2a898cb4`。
- 研究限定の `.github/workflows/halo9-r4-e5-native-h1-nave.yml` を追加。このブランチだけのGitHub-hosted runnerでBlenderを起動し、R0Bの新規BLENDを生成し、`human_sky_district` と `human_public_interior` の2画像をレンダーして、**別Blenderプロセスで実BLENDを再読込**する。成功時は同研究ブランチに成果をコミットする。既存Blenderや正式ワールドを書き換える手順はない。

## 重要な未確認事項

- **この記録時点ではBlender実行・PNG・真正BLEND・再読込の成功を確認できていない。** GitHub Actionsが開始されるか、Linux UbuntuでBlender 4以上が導入されるか、GitHub tokenで研究ブランチへ保存できるかは結果を待たずにPASSと言わない。
- GitHub Actionsの履歴取得機能は、現在のコネクタではPRトリガーrunを中心に返し、pushトリガーrunを網羅できない。Actions一覧を取得できないことだけで失敗や未実行と断定しない。
- 新規E5画像が存在する場合は**必ず本物の画像バイナリを開いて**視覚審査し、問題メッシュを指定、同じ保存BLENDへの直接編集→固定2カメラ再レンダーを実施する。元のR0Bソースを修正して新規生成し直しただけでは同一BLEND直接編集と呼ばない。
- R0Bの形状に問題があればART REJECT。目標物が「単なる梁・箱・棚」なら外殻追加・窓・照明で救済しない。H1の生活、NAVEの公共施設、視線先、複数高度の用途、交通・歩行経路を先に改善する。
- 30必須対象の義務は維持し、未作成を完成扱いしない。約10kmのCITY MASTERが完成するまではMinecraft施工へ進まない。

## 権限・運用境界

- Work / Computer Use / 前面GUI操作を新たに使っていない。GitHub研究ブランチへの書込のみ。
- GitHub Actionsが使用不能であれば、過去の限定許可に沿った**ユーザー明示起動の1クリック背景Blender**が予備経路。CPU 2スレッド/BelowNormal、既存Blender、オフライン、GPUレンダーなし、マウス操作なし。Windows実機での成功はこの会話で未確認。
- `main`、Freeze、正式原本、旧REJECT原本、他研究ブランチ、Minecraftワールドは保護。正式ART採用・mainマージ・Minecraft施工は承認なしで行わない。

**現在の最重要作業は計画や比較図の増産ではなく、真正2画像の取得→美術評価→同じBLENDへの実質的な直接修正である。**
