# J7-R7 / Blender GUI編集経路検証

**2026-10-24 JST / 独立研究 / ART-FIRST、CITY MASTER 3D FIRST / Minecraft施工HOLD**

## 目的
J7-R1〜R6の生成主体の試作が美術REJECTとなったため、さらに大型の手続き的モデルを量産する代わりに、Blenderの**本物のGUIウィンドウと編集モードで既存GLB/BLENDの一部を編集する方法**を検証する。

## 固定方針
正式憲章をmainから明示的に再確認済み。約10km都市をMinecraft施工前に詳細編集可能3Dとして完成。一般建物の私的内部以外は、周辺・地形・各巨大施設の外観と必要内部も含め詳細設計する。M247-Cの研究方向、W0、H1〜H6、SB01〜SB16、HERO4、原本/Freeze/mainは保護。美術正式採択0件、Minecraft施工HOLD。

## 実施した技術作業（現時点での確定）
- J6以前から続く既存幾何の量産を止め、J7-R6実BLENDの**非正式な公共室の床**を対象にしたGUI実験だけを設計。
- GitHub Actions (Ubuntu + Xvfb + Blender 4.0.2 + xdotool + scrot)で**実際のウィンドウ付きBlender GUI**を起動するコードを研究ブランチに保存。
- 編集用研究コピーをBlenderのEDIT_MESHモードで保存し、GUIへ読み込む。元のR6モデルは無変更。
- X11画面のBlenderウィンドウを発見し、3DビューポートのフレームバッファからGUIスクリーンショットを採取するところまでは**実際に確認**した。
- キー入力で既存公共室の床をX方向1.35倍に拡幅し、Y軸-65m移動してUI保存することを目標とした。
- 保存の有無だけでは合格とせず、別のBlenderプロセスで**前後の実頂点bounds、変形比、無関係の基盤モデルが不変であること、GLB再輸出・再インポート**を検証する。
- 仮想ディスプレイには通常のEWMHウィンドウマネージャーが無く `windowactivate` に失敗 → X11の `windowfocus` に切り替えてGUI操作の継続を確認。
- 2回目のGUI実行はスクリーンショットとBLEND保存に到達したものの、頂点幅が所定の1.35倍に達しておらず**CI FAILURE**。成功とは扱わない。
- 対応として、GUI描画時間の確保、NumPad変換ではなく直接キーイベントによる数値入力、変形直後スクリーンショット、boundsの詳細診断出力を追加。

## 結果の扱い
**現状はGUI起動・画面取得・編集コマンド投入・保存までの部分確認に留まる。** 実形状への意図した操作の厳密なPASSは次のCI実行ログで初めて確定する。前処理がエラーでも緑になる偽陽性は禁止し、--python-exit-code 23でスクリプト例外を失敗とする。

本技術試験でGUI操作が成功した場合も、美術品質の向上は別評価。キーボードによるスケール編集は、AIが画面を観察しながら手作業の彫刻・ブラシ操作をできることを証明しない。

## 次工程への判断
実GUIの読込・選択・幾何変形・視覚確認・保存を一連の証拠で示せた場合、次は単一公共室／街区の彫刻品質を高める視覚編集試験に移る。未達の場合、新規キロメートル級モデルを作らず、このUI実証のボトルネック解決が先。

実行はChat側のGitHub Actions研究環境のみ。ユーザーのローカルPC操作、Work/Computer Use使用、Minecraft施工、mainマージは行っていない。

## 2026-10-24 JST — 最終実行結果（追記）

**確定：R7 GUI編集経路の技術PASS。美術ART REJECT／施工HOLDを維持。**

- 実Blender 4.0.2 GUI、X11の仮想画面で実際にウィンドウのスクリーンショットを取得。`01_REAL_GUI_BEFORE.png`に編集モードと本物の公共室メッシュが映ることを画像で確認。
- 前工程の失敗の根本原因はBlender初回起動の**Quick Setup**が画面中央を占有して最初のS/X操作を消費していたこと。実スクリーンショットを見て特定。既存研究コピーのみで初回設定画面を閉じ、ビューを正常に表示した後に再編集。
- 完全成功した[GitHub Actions #40082186677](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/40082186677)でX方向1.35倍の拡幅とY方向-65mの頂点移動が成立。
- 対象:`04_GRAND_CIVIC_FORUM_ACTUAL_PUBLIC_FLOOR`、**18頂点**。実メッシュのXYZ bounds:
  - GUI編集前：X[-910,870], Y[-1420,490], Z[680,733] (m)
  - GUI編集後：X[-1205.1666,1197.8334], Y[-1485,425], Z[680,733] (m)
  - **X幅1780→2403m（1.350倍）、Y移動-65m**。
- Blenderに保存したBLENDを、別のBlenderプロセスが読み直し実頂点測定。163メッシュ維持。他の巨大都市基盤モデルの頂点データ不変。
- 編集後モデルを実BlenderでGLB書き出し（230,816バイト）、空シーンへ読み込み直して**163/163メッシュ一致**を確認。
- 本物のGUIをキャプチャした前後PNG2枚、Blender Workbenchによる編集後の局所／都市全体レンダー2枚、編集前後の`.blend`原本、GLB、JSON実測証拠はすべてGitHub研究ブランチ内`outputs/`に保存。
- このGUI方式はxvfb + xdotoolによる**キーボード操作**。人間のブラシスカルプトやAIのマウス操作を伴う高品質芸術造形を実証したものではない。
- **美術評価：R6マクロ形状はREJECTのまま**。今回の拡幅はUI実証であり、中央建築を正式採択しない。

## 証拠
- 成功実行：[#40082186677](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/40082186677)
- 実行証拠：`outputs/J7R7_REAL_GUI_EXECUTION_PROOF.json`
- スクリーンショット：`outputs/01_REAL_GUI_BEFORE.png`／`outputs/02_REAL_GUI_AFTER.png`
- BLEND：`outputs/J7R7_BEFORE_REAL_GUI_EDIT.blend`／`outputs/J7R7_AFTER_REAL_GUI_EDIT.blend`
- GLB：`outputs/J7R7_GUI_EDITED_ACTUAL_MODEL.glb`

## 次のR8実務優先
**GUI操作の再実証や、R6の岩柱への窓追加を繰り返さない。** 実GUI画面に出る公共室の外観・内部と人間尺度の街路の形状を観察しながら、ひとつの本格的な公共建築断面を造形・修正して審査する。都市マクロへの展開は美術的・空間的に合格するまで保留。CITY MASTER 3D FIRSTとH/SB/W0の全詳細完成義務は維持。実行権限が必要なWork/ローカルComputer Useを独断で使用しない。
