# J7-R28《天潮院 / CELESTIAL ESTUARY》

2026-10-26 JST。独立した相対座標の実3D美術研究。**正式都市原本、完成CITY MASTER、正式採択作品ではない。** 制作AIの暫定美術判定は `ART_REVIEW_JA.md`、技術数値は `qa/DELIVERY_SUMMARY.json` を参照。

## 着想と実制作

海へ向けて開く長い公共院を、三つの段状居住翼が抱き、その奥から細いSPINEと傾いた一つの環が立ち上がる。外側の上昇する輪郭と、内側の屋根・公開回廊・庭・空中街区を同時に設計する。《天潮院》は独立研究名で、正式名称やM247-Cの変更ではない。

背景Blender Pythonで、床・後退した部屋帯・開いたギャラリー・厚みのある曲面屋根・連続する構造リブを個別に生成した。床と開口の位置を直接共有でき、保存した実立体を見て大開口や屋根配分を修正できるため、この方法を選んだ。Geometry Nodes、ライブBlender MCP、前面Computer Use、画像生成AI、追加有料サービスは使っていない。新規生成コードは `build_estuary.py`。

実成果は `model/R28_CELESTIAL_ESTUARY.blend` と `model/R28_CELESTIAL_ESTUARY.glb`。244メッシュ、1,265,352三角形。これは編集時の用途・材質別バッチ数であり、建物数でも美術得点でもない。

| 対象 | 実際に制作した範囲 | 未完成の範囲 |
|---|---|---|
| 中央 | 三つの立上がる円弧状の翼、環状階床を持つSPINE、傾斜環、北翼の大開口、東側の開口 | 各居住帯の大部分は簡略化した私室コア。全公共内部・全階アクセス・用途設計は未完成 |
| 公共院 | 約1.71kmの屋根リブ列、厚い屋根片と空のスリット、1.8kmの下層空間サンプル、4段の側廊、階段、橋、庭、店舗型街区 | 全ての橋や上層回廊への到達・避難・連続歩行は未認証。大きすぎる舗床と繰返しが残る |
| 近景 | 実床上の庇下街路、入口を塞がない店舗形状、ベンチ、樹木、簡略人物、机と椅子のある海側読書回廊 | 人物・植栽・家具は簡易表現。住戸・図書館・商業機能全体の詳細はない |
| 空中地区 | 六つの未割当て研究類型A〜F。厚い多層の円弧、内部街路、建築群、下面の籠状構造 | 六地区に共通する造形が依然強い。正式H1〜H6との対応、全公共内部、生活機能の完成なし |
| 周辺 | 未割当ての双ヴォールト、海側帆型、山岳ギャラリー、南側ゲート。地区別の地上街区・高架研究 | 正式SB01〜SB16/HERO4の資産・配置・内部を統合していない。交通運行・勾配・全接続は未設計 |
| 地形 | 北山稜、西の断崖、東海盆、南西の空白を持つ新規研究地形 | 正式W0ではない。地質・水際・地形と建物の接合、広域市街の詳細は未完成 |

地形の広さや撮影用の遠方地面を都市規模の完成証拠にしない。背景用の地面は300km四方であり、「300km都市」ではない。建築と交通の実分布、中央の実寸は納品集計に別記する。

## 実画像と途中の改善

最終画像はすべて同じ保存BLENDからの実Cyclesレンダー。1600×1000、32 samples、CPU 4 threads、同じ太陽・背景。公共院の固定した建築照明も同じシーンに保存した。霧や画像合成で形状を追加していない。

| 画像 | 視点 |
|---|---|
| `renders/01_ESTUARY_CITY.png` | 南東内海側の都市構図、空中位置 |
| `renders/02_CENTRAL_CHOIR.png` | 中央の斜視。初回の頂端の見切れを画角修正 |
| `renders/03_FORUM_HUMAN.png` | 巨大公共院、実床上1.7m |
| `renders/04_LIBRARY_LANE.png` | 公共院内の庇下街路、実床上1.7m |
| `renders/05_SEA_TERRACE.png` | 海側テラスから中央、実床上1.7m |
| `renders/06_REAR_NORTH.png` | 北側の背面と地形、空中位置 |
| `renders/07_SKY_COURT.png` | 未割当て空中地区Bの実街路床上1.7m |
| `renders/08_WHOLE_CITY.png` | 全域俯瞰。正式全都市の完成証拠ではない |
| `renders/09_UPPER_CIVIC_PROMENADE.png` | 高度650mの屋外公共回廊、実床上1.7m。遠方の別地区を望む |

`process/INITIAL_CITY.png`、`INITIAL_FORUM.png`、`INITIAL_LANE.png` は初期形状。初期の視線閉塞と地区の反復を確認し、北翼に約520m高の切通し、東翼に開口、12段ごとの開いた多層帯を設けた。屋根の空スリットを増やし、公共院内に小さな行先・庭を置いた。地区ごとの円弧長・偏心・後退方向も変更。北山稜と海岸の形状も改めた。これらは実メッシュ変更。

読書回廊のカメラは天井・下面を大きく写し、遠方の生活街区の評価に向かなかった。最終09は既存の高度650mの屋外公共回廊へ移した。室内から別都市を望む完成証明とは扱わない。北側カメラが地形に入った撮影ミスも位置を修正した。中央斜視の見切れと海側の橋による遮蔽も撮影位置・画角を修正。これらは形状の美術改善に数えない。失敗画像は `process/INITIAL_READING_GALLERY_CEILING.png` と `FAILED_NORTH_CAMERA_TERRAIN.png` に保存する。初期のBLENDは最終納品に含めず、途中画像は最終形状の証明に用いない。

## 既往研究との関係

R27Bのソリッドの結晶群から、階床・後退した部屋帯・開いた側廊によって外形を作る構成へ変更した。大きな私室コアの省略はなお残り、全てが詳細な居住都市になったわけではない。

C55-Aの `c55a_city.py`、`c55a_geom.py`、`c55a_hall.py`、`blender_build.py` を読んだ。長距離公共空間の位置・幅・高度を周辺と共有する原理を参照したが、七環モデル・元メッシュ・元コードをコピーしていない。今回も単一のパラメトリックな反復に依存する弱さがあり、C55-Aより総合的に優れるという比較証明はない。

R26の全都市構想とR27Aの実資産台帳を参照した。認証済みの正式W0/H/SB/三軸/Vの共通座標は未解決のまま。**全て新規の仮配置、1 Blender unit=1m、+X東/+Y北/+Z上、研究原点。Minecraft保存座標でも公認アンカーでもない。** 旧16施設912×416ブロックを拡大転用していない。

## 検証と再現

`qa/STARTUP_PROVENANCE.json` にmain `a2f88995eee8d10ee4830dbdf33ccb9c0790de8f`、R27B `60bff854b8cec7265a50de34190d740a626d4c13`、19件の固定出典を記録した。両HEADは開始時にGitHubへ実接続して確認。PR #60はDraft/open/unmerged。古いSETUP_STATUSやCURRENT_STATUSの工程表を現在の制作状態と誤認しない。

Blender 5.2.1 LTSで保存BLENDを独立に開き、GLBを空のシーンへ別読込。全頂点と全三角形重心を双方向比較し、三角形数・境界も照合した。人間視点5点で1.7mの床支持、足元5サンプル、頭部まわり22cmの短いレイも確認。3本の代表的な空間・開口レイは通過した。これらは**全公共体積、全衝突、構造、連続移動、居住・交通運用の認証ではない**。

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --factory-startup -b -t 4 --python-exit-code 1 --python studies/M3D-1S/J7/R28/build_estuary.py -- build
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --factory-startup -b -t 4 --python-exit-code 1 --python studies/M3D-1S/J7/R28/build_estuary.py -- render
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --factory-startup -b -t 4 --python-exit-code 1 --python studies/M3D-1S/J7/R28/verify_saved.py
python -B -X utf8 studies/M3D-1S/J7/R28/capture_sources.py
python -B -X utf8 studies/M3D-1S/J7/R28/package_review.py
```

既存原本ディレクトリから実行しない。追加依存はレビューシート用Pillowのみで、既存環境のものを使用。新規インストールなし。各スクリプトはbytecode書込を無効化する。

buildログには、作業フォルダ外のBlenderサムネイルキャッシュへの書込失敗と、`use_nodes` の将来廃止警告がある。成果BLEND/GLBの保存・再読込・形状比較と実画像出力は別に成功を確認した。外部キャッシュへの書込を許可するための権限変更は行っていない。

## 保存と次の引継ぎ

R27Bを親とする新規R28ブランチへ、このR28ディレクトリだけを追加する。新しいDraft PRのbaseもR27B。PRと納品HEADは最終報告およびPR本文で確定し、push後にその固定コミットの全ファイルをHTTPSで再取得してローカルGitの保存バイトと比較する。受領記録は再帰コミットを避けて `deliverables/` に置く。

main、既存Draft PR、Freeze、M247-C、正式W0/H1〜H6/SB01〜SB16/HERO4/三軸/V、旧研究原本、archives/handoff/upstream、実Minecraftセーブは変更していない。実セーブにはアクセスしていない。正式中央採択0、Minecraft施工HOLD、CITY MASTER 3D FIRST LOCKEDを維持する。
