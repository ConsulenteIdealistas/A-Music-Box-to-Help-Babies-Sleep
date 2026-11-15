# audio/

音源素材（Phase 2 で制作）。

- 基準曲 1 曲（オルゴール）＋心音＋さざ波のステム音源を配置する。
- さざ波はノイズジェネレータから完全自作（権利クリア）。
- 楽曲はパブリックドメイン限定。編曲ルールは `../DESIGN.md` §3・§4。
- 自作音源のライセンスは CC0 または CC BY とし、ファイルごとに
  このディレクトリへ明記する。

試聴メモ（2026-11-12）: 同一フレーズで Python 加算合成 / Csound /
SuperCollider (Klank) / FluidSynth (GM) を比較し、現時点では
SuperCollider + Klank（共振器バンクによる櫛歯モデル）が最も良いという
判断。Phase 2 の合成系の第一候補とする。実録サンプル（Pianobook
「Simple Musicbox」、Freesound CC0）との比較は未実施。
デモ一式は ~/workspace/your_files/musicbox-demo/。

試聴ミックス（2026-11-15）: `render_mix.py`（標準ライブラリのみ、
シード固定で再現可能）が3層ミックスをオフライン書き出しする。
心音 70 BPM（母体安静時の中央、仮値）、胎内フィルタ 1.5kHz・
12dB/oct（仮値）、血流ノイズは心拍同期でうねる設計。パラメータは
全て仮値で、文献の数値抽出が終わったら差し替える。書き出しは
mix_3layer.wav（3層）と bed_only.wav（心音＋血流のみ）の60秒。
