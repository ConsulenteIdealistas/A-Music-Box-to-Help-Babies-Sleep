# literature/

文献レビュー（README フェーズ1）の作業場所。手順は `../METHODOLOGY.md`。

- `extraction_sheet_template.csv` — 抽出シートの列定義（雛形）。
  ジャーナル別に取得した書誌 CSV をこの列に揃えて統合する。
  - `Stratum`: A（主対象: 2歳未満を含む）/ B（参照層: 2歳以上のみ）/
    C（補足層: 動物実験のみ）。層を混ぜて集計しない
  - `Evidence_Quote`: 抽出した数値の根拠となる抄録内の原文フレーズ（必須）
  - `Decision`: 語彙は `METHODOLOGY.md` の「抽出ルール」の節に従う
    （同節が定める `Decision=Count_only` と `Decision=Reference` を含む）。
    完全な一覧は【要決定：CONF-029】とする。裁定記録は
    `../CONTRADICTIONS.md` の CA-023 の項参照
  - `Exclude_Reason`: 除外基準のどれに当たったか
- ジャーナル別書誌 CSV（取得後に配置）:
  `bibliography_pediatrics.csv` など。ファイル名・取得日・クエリ版を
  取得時のメモに残すこと。
- `device_acoustics/` — 端末スピーカー一次情報の別コレクション
  （GSMArena / DXOMARK / Notebookcheck / RTINGS 等）。方法論は
  同フォルダの `SOURCES.md`、対象機種リストは `devices.csv`。
  PubMed 母集団とは混ぜない。
