# CELESTIAL HALO-9 — R4-E6 新規真正Blender美術候補・直接画像審査

**2026-11-05 JST / ART REJECT / TECH PASS / 正式採択0件。**

## 出典・境界

- 正式方針: `main/docs/policy/PROJECT_CONSTITUTION.md`, `CITY_MASTER_3D_STANDARD.md`。いずれも変更なし。
- E5正本・最新研究起点: `0433a2d529bbfd961d75e0d86459b40fb1fd8256`。今回のR4-E6はそこから分離した研究ブランチ。
- 新作作者ソース: `author_integrated_fault_city.py`。E2/E4/E5/R0BのBLENDを開かない。旧R1の西214m移設は禁止・未実施。
- Blender実行: GitHub Actions [#42020105083](https://github.com/ryomashibaba/celestial-halo-9/actions/runs/42020105083)。Ubuntu標準ランナーの隔離Blender、3カメラで真正レンダー、独立Blender再読込を実施。
- GitHub Actions artifact `HALO9-E6-NATIVE-UNREVIEWED-ISOLATED`（ID 13411621116）は保存期間7日。原画PNGはartifact内。研究リポジトリには編集可能BLENDのgzip圧縮本体と、3枚を合成した縮小比較JPEGを長期保存。
- `E6_INHABITED_FAULT_CITY_WORKING.blend.gz` の解凍後SHA256: `d2fbed7f6ae9ddb38fcd22a067827bcfa6c9da66071fa5c530d8798992d836c3`。実BLENDは約1.98MB、gzip格納で約281KB。これは元のBLENDを編集するのではなく、E6独立候補を再開するための編集可能研究ファイル。
- `E6_NATIVE_THREE_VIEW_ART_REJECT.jpg`: 本物のBlender3枚を縮小・横並びにしたレビュー用画像。生成AI画像でも代替投影でもないが、元PNGと同じバイト列ではない。

## 真正技術結果 — PASS（ARTではない）

- 新規 `E6_INHABITED_FAULT_CITY_WORKING.blend` をBlenderで保存後、**別プロセスのBlenderで独立再読込成功**。
- 960×640 の同一シーン真正レンダー: `human_public_interior.png`, `human_sky_district.png`, `urban_aerial.png`。
- 再読込側のメッシュ数175。研究用30対象レジストリ30件の存在を確認。ただし完成した建築30件ではない。
- `minecraft_write=FORBIDDEN`, `official_coordinates_verified=False`, `formal_art_adoption=False`, `completed_targets=0`。
- GitHub Actions成功はTECH PASSであり、芸術作品の採用や使用可能な公共経路の認証ではない。

## 本物の3レンダーを直接鑑賞したART審査 — REJECT

1. **人間公共内部**: 視線上半分以上が大きな不透明の水平・斜面に塞がれ、外部の地形と巨大な壁状構造が主景になった。多層NAVEで「歩いて入れる公共室」としての階・入口・活動・垂直動線が画面内で読めない。視点だけの調整では空間設計の欠陥を救済できない。
2. **人間高所居住地区**: 彫刻的な壁・尖塔・箱状の外壁が画面を占有する。住宅・学校・商業・市民施設の存在はオブジェクト名やソースで設定されても、歩行者から多層生活都市と読み取れない。人間にとって認識可能な街路・沿道開口・公共目的地が不足。
3. **都市俯瞰**: M247-Cの複数の黒い単純な刃状主質量が構図を支配し、H1は横に突き出す厚い台座と小さな白い街区に見える。W0は巨大な灰色の地面＋東の青い池に見え、地形・都市・内海が一つの文明構造になっていない。中央の空洞と巨大公共室より外側の刃が主役。

**結論**: R0Bより新しい実制作・独立再読込を達成したが、世界水準の超未来都市美術には達していない。今回の主役形状は**ART REJECT**で凍結する。窓・電飾・人口施設名の追加でREJECTを偽装しない。正式ART採択0、完成30対象中0件、Minecraft施工HOLDを継続。

## 次の本質的な制作方向（未実施）

**このE6 BLENDを小修正して採択することはしない**。次の独立候補では、巨壁・鋭い刃・高所台座を都市構造の核に据えるのではなく、公共室・都市の「抜け」・複数街路・厚い居住断面そのものを空間主役にする。遠景の唯一性と2人間視点の生活可読性を、**新候補3視点が描けるまで実制作で照合**する。真の大改善が見えない限り7視点や30施設の量産へ進まない。カメラ移動のみで合格扱いしない。

## 保護確認

`main`、Freeze、旧E2/E3/E4/E5原本、R0B、Minecraftワールドは変更していない。今回のGitHub書込みはR4-E6隔離研究ブランチのみ。Work/Computer Use・有料API・ユーザーのPC GUI操作は使用していない。
