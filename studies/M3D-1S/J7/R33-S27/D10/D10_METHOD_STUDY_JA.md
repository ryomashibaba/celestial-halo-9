# R33-S27-D10: 美術主導の編集可能3D制作方法の比較
2026-10-28 JST。**方法選定は暫定。建築美術の改善は未実証。**

## 研究問い
文章の構想を単純な断面生成に置換するのではなく、多方向から造形判断した原形を、その固有の比例・接合・非対称性を保ちながら編集し、公共空間変更を外形へ反映できるか。D8/D9の連動原理を継承し、帯/塔の形を継承しない。今回の試験片は完成建築案ではない。

## 比較（点数は付けない）
| 方法 | 美術上の可能性/危険（推論） | 編集/都市との関係 | 証拠と現時点判断 |
|---|---|---|---|
| D8/D9型の意味パラメータ一括再生成 | 局所整合に強い一方、許された形態族へ構想が収束する | 内外連動は過去記録あり。任意の既存形状を保存する仕組みとは異なる | 過去ART REJECT。新中央形態の生成主役として延長しない |
| 直接polygon/patch編集＋必要箇所のSubdivision | 既存形の固有性を人/AIが視覚判断できる。Subdivision自体に構想力はなく、丸まりや開口縮小に注意 | topology/vertex IDを保てる範囲で制約を付与。公共床は水平を別拘束 | 公式Subdivision/Shape Key資料＋今回のopen-patch線形試験。**次の局所視覚試験候補**、美術成功は未実証 |
| 閉じた自由形cageのMesh Deform/Lattice＋意味拘束 | 主外形と複数objectのまとまった修正に向く可能性。bindingの誤り・大変形artifactに注意 | 結合・region maskとsolverを別途実装する必要。Blender標準機能だけで公共動線を保証しない | 公式資料。**本セッションではBlender bind未実行**。今回open patchはMesh Deform用の閉cageではない |
| sculpt/remesh→retopology→意味を再付与 | 初期質量・負空間探索の自由度。rock-likeな塊や空洞だけに回帰する危険 | remeshは新topologyを作るため、vertex対応/Shape Keyをそのまま永続化できる前提を置かない | 公式Remesh/Shape Key資料。局所造形の補助手段候補、内部都市の完成手段とは判定しない |

## 参照した一次資料（アクセス2026-10-28 JST）
- [Blender Mesh Deform](https://docs.blender.org/manual/en/latest/modeling/modifiers/deform/mesh_deform.html): 任意の閉meshをcageにできる。bindが必要。大きなcage変化にartifactの既知限界あり。
- [Blender Lattice](https://docs.blender.org/UATEST/manual/en/dev/modeling/modifiers/deform/lattice.html): 複数objectへの共有変形、vertex groupによる領域限定。これはdev資料として扱い、導入済み版の機能確認とはしない。
- [Subdivision Surface 4.5 manual](https://docs.blender.org/manual/id/4.5/modeling/modifiers/generate/subdivision_surface.html): 少数の基底頂点で曲面を編集できる一方、crease/edge loopなど形状制御が必要。4.5資料であり、現地5.2.1での操作実証ではない。
- [Shape Keys 4.5 manual](https://docs.blender.org/manual/id/4.5/animation/shape_keys/introduction.html): 同じmesh接続に対する頂点位置を記録する。安定topology後に用いることが推奨される。
- [Remesh 4.5 manual](https://docs.blender.org/manual/id/4.5/modeling/modifiers/generate/remesh.html): 新topologyを生成する。既存IDと意味付けの追跡には別処理が必要というのが本研究の推論。
- [Sorkine & Alexa, As-Rigid-As-Possible Surface Modeling (2007)](https://igl.ethz.ch/projects/ARAP/arap_web.pdf): 局所回転を含めた非線形変形法。大きな回転を扱う将来候補。**今回の線形graph変位補間をARAPと呼ばない。**

資料上の機能、今回実行した実験、未実施のBlender試験を区別する。料金、新規アカウント、外注、ソフト更新は発生させていない。

## 今回実装した差分と実験範囲
D8/D9は少数の生成パラメータから建物を再構成した。今回の試験は、明示的に列挙した不規則な20頂点open patchと既存の面接続を固定し、その**頂点変位**を解いた。patchの見た目から建築美術を主張しない。

変位dはX方向のみ。目的関数は
`1/2 * sum_edges (d_i-d_j)^2 + 0.05/2 * sum_i d_i^2`。
固定点、直接handle、重み付き空間幅の変更をhard equalityとしてKKT連立一次方程式を解く。これは均一重みのgraph smoothingであり、局所体積/剛性/曲率保存や回転不変性の保証はない。20点規模のdense solverを10km都市へそのまま拡大しない。

床はz=88m/184mにある2枚のゼロ厚quad試料。外周の仮想attachmentはそれぞれ2つのpatch頂点の正規化固定重みと12m offsetで定義。実際の面上のbarycentric binding、外壁厚、全幅接合、室volumeを再構築したものではない。床の左端を固定して右端をattachmentに追従させる。床の水平性はZを動かさない設計によるもので、任意3D変形を自動修復する能力の証明ではない。

1. BASEを保存。
2. 同じ32m外形handle操作で、床追従を外す対照と、拘束付き連動を比較。
3. 床幅を+24m/+12mに指定し、既存patchを拘束変形。
4. 公共床A側のattachmentを同じ24m動かす全体X拡大を対照とし、固定点破壊とB側の過剰変形を測定。
5. 互いに矛盾する同一handle目標を与え、solverが結果を公開せず停止することを確認。ただし現在は冗長制約もsingularとして拒否し、矛盾/冗長を分類できない。
6. solver出力をOBJ文字列へ保存し、別実装のparser/座標測定で照合。検証者は同じAIであり、別作者/別エージェントの独立審査ではない。

## 数値結果（OBJ再読込後）
| 操作 | 床A幅差 | 床B幅差 | 最大固定点ずれ | 最大attachment gap |
|---|---:|---:|---:|---:|
| 外形handleのみ32m、床更新なし | 0 | 0 | 0 | 19.2m |
| 全体X拡大（A attachment +24m） | +24m | +45.427451m | 89.725490m | <1e-7m |
| 2床幅の意味拘束 | +24m | +12m | 0 | <1e-7m |
| 外形handle32m＋拘束連動 | +11.871808m | +27.063558m | 0 | <1e-7m |

連動2試験でface接続不変、有限値、非退化、基準に対する三角形法線反転0、床Zばらつき0を確認。NaN混入とface接続改変の負試験はそれぞれ検出した。逆符号の線形変位を加算したround-trip誤差0は、**この線形モデルの性質**であり、BlenderでのUndo/保存再読込実証ではない。

## 判断
**TECH LIMITED PASS（隔離JS内の既存patch＋床試料の限定連動のみ）。ART HOLD（建築案未制作・美術改善未検証）。**
良い絵や美しい建築ができた、D10全工程完了、完全双方向メッシュ編集、Blender実証、居住認証、全都市完成とは主張しない。

今回の新しい知見は、少数の造形パラメータに建築全体を閉じ込めなくても、既存頂点の自由度を残したまま内部寸法と保護点を局所拘束できること。ただし20点・一方向・固定対応の範囲に限る。D8/D9からの改善は**自由造形へ接続するための制御構造**であり、建築美術の改善そのものではない。

## 次に検証すべき具体物
承認された隔離Blender sceneで、造形と重要内部を同時に観察できる局所断面を一つ制作し、直接polygon/patch編集＋意味拘束を試す。M247-C正式モデルではなく、独立した未採択研究。既存D9塔を増築しない。固定した同一sceneの遠景/斜視/背面/俯瞰/内部/人間視点で基準と編集を比較し、灰色geometryでの主質量・接合・都市の可読性を先に審査する。美術不合格なら装飾を増やさず停止する。

都市C、W0の北山岳/西断崖/東内海/南西負空間、H1〜6、SB01〜16、HERO4、V1〜3/都市軸を削らない。試験の仮座標を正式座標へ昇格させない。全域設計との関係は別の完成マトリクスで未達のまま追跡する。

Workの利点は、実際のBlender meshを観察して修正し、同一sceneの背面/内部を描画し、編集可能BLEND保存・再読込を実証できること。**事前の明示承認が必要。まだ実行していない。** 同じPython生成をMCP経由で呼ぶだけでは今回必要な比較を満たさない。
