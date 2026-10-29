# D31 CAD実形状研究（非正式）

D31ではA/B案の厳密CAD STEP、表示用GLB、多視点レンダリング、技術監査を検証しました。**ART REJECT、正式採択なし、Minecraft施工HOLD**。A/Bは美術的に独立した2方向ではありません。

実行環境: Python 3.13 / CadQuery 2.8 / Trimesh 4.11 / VTK 9.6 / numpy / Pillow。ユーザーのBlender環境での起動は未検証。

再生成：`python d31_cad_artfirst.py`

独立監査：`python d31_independent_audit.py`

**寸法単位:** Python仮座標はm。最終STEPヘッダーはMETRE宣言。GLBもm座標。CadQuery/OCCの最初のimportStep(unit=M)が意図と異なる換算値を返す現象があるため、監査ではM指定で初期化後に再読込し、GLBとのXYZ外寸一致を必須化。

**制約:** 幾何精度は平面多角柱と貫通窓に限定。都市全体、居住内部、通路、構造、法規は未成立。この形状は美術として不採用。
