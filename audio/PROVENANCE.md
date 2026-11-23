# 採譜とツールの来歴記録

レパートリー4曲について、「どの出典から・どのツールで・どう採譜し、
どう生成したか」を固定する記録。出典（旋律ソース）の一覧は
audio/SONGS.md が正本で、本書は方法とツールの記録である。
各 MusicXML の <identification> にも要約（source / transcription /
tools）を埋め込んである。

## ツール構成

主たるツールは Python / SuperCollider / SoX の3つ。

- **Python**（標準ライブラリのみ）: 音符データの保持と MusicXML
  生成（make_musicxml.py）、楽譜の読み込みと試聴用加算合成
  レンダー（render_songs.py）、SuperCollider の制御
  （render_klank.py）、ループ化（make_loop.py）、心音・血流
  ベッドの生成とミックス（render_mix.py、正本）、測定
  スクリプト群。
- **SuperCollider**（sclang / scsynth、ホーム導入）: オルゴール
  音色の合成。Klank（倍音比 1 : 6.267 : 17.548 : 34.386、振幅
  1 : 0.32 : 0.12 : 0.05、減衰 4.0 / 0.45 / 0.18 / 0.09 秒、
  Impulse 駆動）。render_klank.py が曲ごとに .scd を生成し、
  sclang をヘッドレスで実行してレンダーする。2026-11-12 の
  試聴比較で Python 加算合成に勝ち、正式エンジンに採用された。
- **SoX**（ホーム導入）: 相互検証と測定。ベッド／ミックスの
  SoX 版レンダー（render_bed_sox.py / render_mixes_sox.py）は
  2026-11-18 以降「相互検証専用、完成品にはしない」。ピーク・
  RMS 等の測定にも使う。
- 補助: **ffmpeg**（ebur128 による LUFS 測定）、**R +
  robustbase**（統計の相互検証。音の生成には使わない）。

使っていないもの:

- 譜面作成ソフト（MuseScore 等）は使っていない。MusicXML は
  Python スクリプトが生成するため、ファイルに <software> の
  記録はない。
- LilyPond は出典（Wikipedia 記事内の楽譜）のソース形式で
  あって、本プロジェクトで実行したツールではない。

## パイプライン

出典 → 音符データ（make_musicxml.py 内のデータが転記記録
そのもの）→ audio/scores/*.musicxml（楽譜の正本。再生成は
バイト単位で決定的）→ render_songs.py が読み込み →
render_klank.py が Klank でレンダー → make_loop.py で
ループ化 → app/assets/*.wav（生成記録は app/assets/README.md）。

注記: render_klank.py は render_songs から SONGS を import
するが、render_songs は XML を読み込むだけなので、音符
データの正本は XML とその生成元データである（音符データを
別に保持するモジュールは無い）。

## 曲ごとの採譜記録

### ブラームス 子守歌

Wikipedia「Wiegenlied (Brahms)」記事内の LilyPond 楽譜
（Eb長調）のソーステキストを読み、音符データとして
make_musicxml.py に入力した。C長調への移調と +8va は
データ側で適用。
.ly ファイルは当時保存されていなかったが、2026-11-23 に
採譜時点で有効だった版（oldid 1315867230、2025-10-09 の
版）から回収し、brahms_wiegenlied.ly として作業フォルダ
に保存した。あわせて機械照合（verify_brahms_lilypond.py）
を行い、全54音の音高と長さが転記と一致することを確認
した。例外は2点のみ: 最終音は出典の2拍から3拍に伸ばして
小節を満たしてある（ピックアップとの釣り合いの分）、
装飾音符3つ（前打音1つと後打音2つ）は転記に含めていない。

### モルダウ主題

Wikipedia「我が祖国」記事内の LilyPond 楽譜（E短調・6/8）。
ソースは score_0.ly として作業フォルダに保存してある。
2026-11-15 に LilyPond を再取得して機械照合し、全音・
リズム・音域の一致を確認した（照合データは作業フォルダの
mavlast.json）。IMSLP のピアノ独奏版 PDF でも主題提示部の
音域と輪郭を確認した。最終小節は出典の抜粋が小節途中で
終わるため、E を付点四分に伸ばして補完した（編曲側の処理）。

### 歌に生き、愛に生き

IMSLP の Ricordi 1910 ボーカルスコア（plate 113189）の
歌唱スタッフを、スキャン画像から読み取って転記した。
初回転記には低解像度での読み違いが複数あったため、300 dpi
拡大＋五線グリッド重ねでの再読と、Ricordi フルスコア
（IMSLP 608234）との突き合わせで全て訂正した（個別の訂正
内容は SONGS.md の注記が正本）。転記範囲は冒頭セクション
のみで、中間部以降は未転記。

### ゆりかごのうた

公開カリンバ譜（えほん日和、class101 配布 PDF）の旋律線
（C長調）を音符データ化した。伴奏の和音スタックは低音の
簡易形に置換し、リズムは 4/4 に整えた編曲であり、検証
済みの転記ではない。
出典 PDF は当時保存されていなかったが、配布元（class101
の CDN）にまだ残っていたため 2026-11-23 に回収し、
yurikago_kalimba_class101.pdf として作業フォルダに保存
した。旋律線が転記データと一致することは PDF のテキスト
で確認した。

## 作業材料の所在

一次材料と作業画像は ~/workspace/lullaby-scores/（リポジトリ
外）に残してある: vissi_vocal_score_ricordi1910.pdf /
vissi_full_score_ricordi.pdf / vltava_piano_solo.pdf /
score_0.ly（モルダウ）/ brahms_wiegenlied.ly（2026-11-23
回収）/ yurikago_kalimba_class101.pdf（同回収）/
mavlast.json / 歌に生きの確認用切り出し画像とグリッド
重ね画像（check_*.png、*_grid.png 等）。

回収と再現の記録（2026-11-23）:

- ブラームスの .ly とカリンバ譜 PDF は上記のとおり回収
  済み（各曲の節を参照）。
- 五線グリッド重ね画像の生成スクリプトは原物が残って
  いないため、staff_grid.py として再現版を作成し、同
  フォルダに保存した。残存グリッド画像3枚での検証では、
  線の間隔は約1%以内、位置は数px〜20pxのズレ（ピクセル
  単位の再現ではない）。正確な配置には手動指定を使う。
- score_1.ly / score_2.ly は同時期に取得した別の抜粋で、
  レパートリー4曲には使っていない
