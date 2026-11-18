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

試聴ミックス（2026-11-15、フィルタは 2026-11-17 に更新）:
`render_mix.py`（標準ライブラリのみ、シード固定で再現可能）が
3層ミックスをオフライン書き出しする。心音 70 BPM（母体安静時
心拍 60〜80 の中央。既定値であり可変）、血流ノイズは心拍同期で
うねる設計。胎内フィルタは当初の仮値（1.5kHz・12dB/oct）から、
文献統合による統合伝達曲線（250Hz の1極ローパス: 250Hz 以下は
平坦で +3.5dB 相当、250Hz 超は −6dB/oct）に置き換え済みで、
血流層と音楽層の両方に同じ曲線を通す。根拠と経緯は
`bed_integration_2026-11-17.md`。書き出しは mix_3layer.wav
（3層）と bed_only.wav（心音＋血流のみ）の60秒。

正本の指定（2026-11-18、ユーザーの決定）: 完成ミックスとベッドの
正本パイプラインは `render_mix.py`（Python）に一本化した。
4曲の完成品セットは `python -m audio.render_mix --out-dir <dir>
--phrases-dir <klank フレーズの dir>` で生成する（bed_only.wav と
mix_<曲>.wav ×4）。SoX 系（`render_bed_sox.py` /
`render_mixes_sox.py`）は独立した整形・ミックス経路による
相互検証専用で、その出力は完成品にしない。SoX 側で生まれた
ベッドのフェード（イン 2 秒／アウト 3 秒、直線）は render_mix.py
に取り込み済みで、正本のベッドも同じフェードを持つ。
