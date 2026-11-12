# analysis/

抽出データの統計解析（Phase 1 後半）。

- 入力: `../literature/` の統合済み抽出シート
- 出力: パラメータ表（Frequency_Hz / Sound_Level_dB / Tempo_BPM ごとに
  N・平均・SD・中央値・IQR・正規化MAD、外れ値の PMID と条件メモ、
  METHODOLOGY.md §4 の規則で決まった設計値とその根拠）
- 実装は Python。統計量の定義は METHODOLOGY.md §4 に従う。
