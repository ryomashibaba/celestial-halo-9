# 再実行の入口

ローカル操作はプロジェクトのWork事前承認規則に従う。新しい空の研究出力フォルダを用い、正式原本・この納品のBASE/EDITを上書きしない。

`create_study.py` はBlenderの新規factory sceneを作り、`-- <新出力フォルダ>` を引数に受け取る。
`render_views.py` は保存BLENDを開いたBlenderで `-- <新出力フォルダ> BASE` または `EDIT` を受け取り、6枚描画する。
`direct_edit.py` は新出力のD10_BASE.blendを開いたBlenderで `-- <新出力フォルダ>` を受け取り、BASE GLB、直接編集後のEDIT BLEND/GLB、snapshotと編集ログを保存する。**基準画像の観察を先に行う。**
`reload_audit.py` はD10_EDIT.blendを新規Blenderプロセスで開き、`-- <新出力フォルダ>` を渡して検証する。
`verify_glb.py` はBlenderを使わず、NumPyのあるPythonで `<新出力フォルダ>` を渡してGLBを解析する。
`package_evidence.py` はPillowのあるPythonで `<新出力フォルダ>` を渡して比較画像/manifest/ZIPを組み立てる。Windows標準Arialを利用する。REVIEW_JA.mdは観察に基づく審査文で、自動生成の合格判定ではない。

この試験で使用したBlenderは5.2.1 LTS、実エンジンはCycles。原寸画像は1100×825、24 samples、denoise有効。画像/BLENDを新規に作る再実行がユーザーの美術採択に相当することはない。
