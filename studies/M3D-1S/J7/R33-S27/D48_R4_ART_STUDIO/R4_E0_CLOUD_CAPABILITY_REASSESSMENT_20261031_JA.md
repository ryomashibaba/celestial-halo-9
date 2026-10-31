# CELESTIAL HALO-9 / CELESTIAL SPINE — R4-E0 クラウド視覚制作環境 再調査
確認日：2026-10-31 JST
分類：研究記録 / 公開仕様調査 + Chat実行面のツール棚卸し / 真正GUI・実3D制作は未実行
判定：**E0 CAPABILITY RESEARCH DONE / E0 GUI PATH BLOCKED（当該Chatでは未確立）**
正式美術採択：0 / CITY MASTER 3D：未完成 / Minecraft施工：HOLD

## 0. 原本と優先順位
- リポジトリ：ryomashibaba/celestial-halo-9
- 照合時のmain：`a2f88995eee8d10ee4830dbdf33ccb9c0790de8f`。
- 親R4：`4f6268f0048a10f0cc75055335332d851766e181`。
- 前回Cloud PHASE 0停止報告：`c719de3baf0c64a31e54be74a19a2025384ac2e3`。
- 本文書は前回停止ブランチHEADを親に持つ**新規独立研究ブランチ**に追加。main・親R4・前回停止報告・Minecraft・正式研究原本は変更しない。
- main/docs/policy/ の指定7文書を明示refから取得。固定憲章、CITY MASTER 3D FIRST、ART-FIRST、30対象、一般建物私室のみ詳細省略、M247-C α＋βの保護を引き継ぐ。
- mainのSTART_HERE/CURRENT_STATUSに残る2026-10-23時点の「未マージ」記載は古い。現時点でmainに各文書は実在。

## 1. 今回の新しい事実（公開仕様）
1. OpenAI「Manage dots in ChatGPT workspaces」は **Cloud browser use / Cloud network access / Cloud computer use** を区別し、Cloud computer useをWork Cloud / dotsの**クラウドコンピューターのデスクトップとアプリケーションの操作許可**と説明。したがって「Workのブラウザが使える」だけで独立CloudのBlenderネイティブGUIを操作できると結論しない。https://help.openai.com/en/articles/20001554-manage-dots-in-chatgpt-workspaces
2. OpenAI「Using cloud browser in ChatGPT」は、Work Cloudブラウザが独立コンピューターのWebタスクを扱うと説明するが、**BlenderのネイティブGUI起動・操作を保証しない**。https://help.openai.com/en/articles/20001280-using-cloud-browser-in-chatgpt
3. OpenAI「ChatGPT Work and Codex」は、Web/モバイルのWorkがクラウドで動き、デスクトップ版Workには許可次第で**ローカル**ファイルやアプリも利用できると説明。両者のアクセス境界を混同しない。https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex
4. Blender公式MCP ServerはBlender 5.1+、アドオン、LLMクライアント、MCP Serverを要し、**AI生成コードの無防備な実行リスク**を公式警告。独立VMなどの隔離を推奨。利用・インストール・接続の実証は今回行っていない。https://www.blender.org/lab/mcp-server/

これらは製品機能・要件の公開情報であり、**ユーザーアカウント・当該Workセッションの権限・環境に存在する能力の実測値ではない**。

## 2. このChatでの実際の棚卸し
- 現在のChatから利用可能なツール記述を探索。専用のBlender GUI、Cloud desktop画面操作、Cloud環境ID取得、Cloud GUIセッション起動への明示的ツールを確認できなかった。
- プラグイン検索を「Blender MCP 3D modeling」「cloud desktop computer virtual machine」「3D scene editor modeling Spline」で実施。3Dネイティブ編集を直ちに行える確証ある専用プラグインは取得できなかった。検索は網羅的ではない。
- Workの当該アカウントにおけるCloud computer use権限設定、独立コンピューターの状態、シェル、デスクトップの画面、Blenderインストール有無は**わからない**。
- 今回のChatでは別のWork Cloud実行を開始していない。以前のユーザーPCや稼働中Blenderを対象とするMCPは使用していない。
- 真正GUIスクリーンショット0、Blender起動0、BLEND/GLB作成0、新規7視点画像0、視覚批評・直接造形0。AI美術改善の証拠は0。

## 3. 修正した次工程：E0アクセス経路を先に確定
新たなWork Cloudセッション等の権限は本記録だけで自動付与されない。改めてユーザーの実行許可が必要。**許可を得た場合のみ**、次の最小分岐を確認する。

**E0-A：隔離Cloudへの実アクセス**
- 対象がユーザーPCではないことを示す環境情報、明示的なCloud操作モード、デスクトップ画面の取得能力、デスクトップ入力能力、研究用書込先を確定する。
- Cloud computer use、Cloud browser use、Cloud network accessの公開仕様と実際の有効権限を混同しない。
- GUI/入力/書込先のいずれかが得られない場合は原因を記録し**BLOCKED STOP**。旧Workプロンプトを無変更で再実行しない。

**E0-B：Cloud上のBlender確認**
- E0-Aが通った場合だけ、Cloud上のBlender存在とバージョン、起動可能性、Blender 3Dビューポートの実画面を調べる。
- インストールが必要な場合は、対象環境・ネットワーク・安全境界と事前承認を確認。Blender公式MCPをユーザーPCへ接続しない。
- Blenderの真正GUIで画面観察→使い捨て既存メッシュ修正→別名BLEND保存→再読込→実画面再確認を**1回のみ**実証。成功しても新美術ART PASSとは呼ばない。

**E0-C：制作能力の妥当性**
- E0-B成功後も「動いた」だけではR4成功としない。現物を見て実際の主形状欠陥を指摘し、同一ソースの既存メッシュを改善し、前後画像を同一条件で独立評価できるかを別ゲートで検証する。
- 本格案は最大2案・同じ研究用都市台帳内の30対象を維持。7固定視点に地上・公共室・高所居住の人間視点を含む。装飾や大量自動生成で弱い主形状を覆わない。

## 4. 明示的に除外した迂回策
- Work CloudのブラウザだけをBlenderのGUI操作に読み替えない。
- ユーザーPC/ローカルBlenderへのComputer Use、無隔離MCP、古いポート9876へのアクセスを無断で行わない。
- GitHub Actions/bpyの一括生成を「視覚主導の改善能力」と偽らない。
- 未認証のM204/W0/M207正式座標、Minecraft書込、Freeze改変、mainの変更・マージを行わない。
- 新規外部有料サービス契約、アカウント作成、MCP導入、ネットワーク公開を無断で行わない。

## 5. 状態と次の証拠
| 対象 | 現判定 |
|---|---|
| 正式方針 | VERIFIED（mainから取得） |
| R4-E0 公開仕様・接続手段の再調査 | DONE（調査のみ） |
| R4-E0 隔離Cloud GUI実操作経路 | **BLOCKED / 未実証** |
| Blender起動・編集・BLEND再読込 | NOT EXECUTED |
| SOURCE TECH（新規） | HOLD |
| ART（新規） | HOLD、過去R1〜R3-G2 REJECT維持 |
| FUNCTION | UNCERTIFIED |
| 正式ART採択 | 0 |
| CITY MASTER 3D | 未完成 |
| Minecraft | HOLD |

**結論**：Cloud desktop操作機能の存在は公式仕様で確認できたが、当該アカウント・セッションにおけるBlender操作能力の実証とは異なる。次回は無差別な接続試験ではなく、隔離Work Cloudの実画面・入力・書込能力を確認できる環境でのみE0-Aへ進む。不可ならSTOPし別方式を比較する。正式方針の変更なし。
