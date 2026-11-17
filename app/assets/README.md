# app/assets — ループ音源の生成記録

アプリの音楽層が使うループ WAV の対応表。WAV 本体は容量
（合計 約14 MB）のためリポジトリには含めない。clone しただけでは
音楽層は鳴らないが、心音・血流層だけでもアプリは動作し、画面に
音源が無い旨が表示される（app.js の loadSong の失敗経路）。

## 生成手順

1. 楽譜（audio/scores/*.musicxml、正本）から SuperCollider/Klank で
   レンダーする（audio/render_klank.py、倍音比・減衰は同ファイルの
   定数が正本）。
2. audio/make_loop.py でループ化する: 最後の可聴サンプル
   （−60 dB 閾値）まで＋無音 1.0 秒を残し、ゼロ交差で切る。
3. ここに <曲名>_klank_loop.wav として置く。

## 対応表（2026-11-15 生成）

| ファイル | 曲 / 楽譜 | 長さ | サイズ | SHA-256 |
|---|---|---|---|---|
| brahms_wiegenlied_klank_loop.wav | ブラームスの子守歌（Eb→C 移調＋1オクターブ、Wikipedia LilyPond 由来） | 48.5 秒 | 4,280,974 B | 43b5ece040f4a7f312711f052969bdc9f913d3bd4aa21ea97512a164535a5def |
| moldau_theme_klank_loop.wav | モルダウ主題（Wikipedia LilyPond＋IMSLP ピアノ版で照合済み） | 42.9 秒 | 3,780,986 B | 41b6484254325d9fe44d418bdc44ded81750d159c7705dfccf5eb983b0d346a9 |
| vissi_darte_klank_loop.wav | 歌に生き、愛に生き（冒頭のみ。IMSLP Ricordi 1910 で二重チェック済み。中間部以降は未転記） | 22.1 秒 | 1,952,864 B | 81bb424d16ca37ed9402025bd24a7620487009699cd8bf8e1a7a6fb7842bc8e1 |
| yurikago_no_uta_klank_loop.wav | ゆりかごのうた（公開カリンバ譜からの編曲） | 49.2 秒 | 4,339,624 B | 212589881ed80cf1ec165972d18c90bc3d82d3700fe4e5c59f8ab86c7a7624a1 |

形式は全て 44.1 kHz / 16 bit / モノラル。再生時にはアプリ側で
統合伝達曲線（250 Hz 折れ点）の適用と RMS 正規化が行われるため、
この WAV 自体は無加工の Klank レンダーである。

再生成したら、この表のハッシュと日付を更新すること（生成物の
版とアプリの対応を追えるようにするため）。
