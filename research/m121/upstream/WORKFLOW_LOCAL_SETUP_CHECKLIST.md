# これから最初に行うこと：ローカルWork用プロジェクト初期セットアップ

## 目的
Chatメイン・GitHub共通保管・必要な作業のみWork。最初はローカルWorkプロジェクトを作成し、GitHubとM121 ZIPを安全に統合する開発環境を作る。Minecraftへの施工は一切行わない。

## セットアップ候補
- ローカルフォルダ例：`C:\Projects\CELESTIAL_HALO9`（Minecraftの`saves`配下を絶対に使わない）
- GitHubプライベートリポジトリ：`ryomashibaba/celestial-halo-9`
- 本ZIPの M120 内ソースがM119→M121の再生成ソース正本
- Python依存：numpy, matplotlib, Pillow, vtk（本ZIP requirementsファイル参照）
- GitHubの既存PR列は未マージ、`main`を書換えず新しい作業ブランチで段階移行

## 決してしないこと
- `CH9_D6D_REVIEW_COPY` のレビュー用データに施工コマンドを書き込まない。
- 別の `saves/imagine` を「ゲーム内ワールド名がimagineだから」と自動的に選ばない。
- Frozen408、public959、SB09/SB13、88空洞、道路、公園、M101比較基準を書き換えない。
- 未承認のPRをまとめてマージしない／無断push forceをしない。
- M121の0件「旧人工材タイルAABBヒット」を保護クリアランスと見なさない。

## セットアップ成功の確認
- Chat/Work双方が同じGitHub元リポジトリと作業ブランチを参照
- M119/M120/M121全ソースを読める
- ユーザーのローカルWork作業フォルダを正しく選べる
- テスト15件PASS
- 元のレビュー用ワールドのファイルに一切変更なし
- スクリプトや3Dレンダラーを次回も再生成可能
