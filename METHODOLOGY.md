# METHODOLOGY — 文献レビュー方法論

音響パラメータ（BPM・周波数帯域・減衰率・音圧上限）を、出典のない定数では
なく文献の実測集計から決めるための手順。この文書自体が「どの検索式で何件を
集め、どういう基準で何件に絞り、どんな統計量を採用したか」の記録になる。

## 1. 母集団（クエリ v1、2026-11-12 実測）

母集団は「各ジャーナル100件」といった件数目標ではなく、**下記クエリの
全ヒット**とする。件数は PubMed E-utilities（esearch）で 2026-11-12 に
実測した値であり、看板ではなく記録である。クエリを変更した場合は版を
上げ、旧クエリと件数をこの表に残す。

| # | ジャーナル | 件数 | 備考 |
|---|---|---:|---|
| 1 | Pediatrics | 17 | 当初クエリのまま |
| 2 | Early Human Development | 40 | 当初クエリのまま |
| 3 | Infant Behavior & Development | 21 | 誌名表記を修正（下記） |
| 4 | The Journal of the Acoustical Society of America | 258 | 当初クエリのまま |
| 5 | Hearing Research | 196 | クエリを適正化（下記） |
| 6 | Journal of Music Therapy | 31 | 母集団を再定義（下記） |
| | **合計** | **563** | |

参考（誌制限なしの同テーマ件数、同日実測）: 胎内音響 788件 /
乳児×音×睡眠 1,327件。分野自体は相応の規模があり、本設計の件数が
小さいのは「誌×テーマ」の切り口による。

### クエリ

1. Pediatrics
   `"Pediatrics"[Journal] AND (infant OR newborn OR neonate) AND ("white noise" OR "sound" OR "music" OR "lullaby" OR "heartbeat") AND (sleep OR decibel OR hearing)`
2. Early Human Development
   `"Early Human Development"[Journal] AND (fetal OR newborn OR preterm) AND ("intrauterine" OR "heartbeat" OR "maternal voice" OR "auditory") AND (autonomic OR "heart rate" OR sleep)`
3. Infant Behavior & Development
   `"Infant Behavior & Development"[Journal] AND (infant OR newborn) AND (rhythm OR tempo OR music OR lullaby OR "white noise") AND (soothing OR crying OR attention OR preference)`
   - 修正理由: PubMed の誌名は "and" ではなく "&" 表記。当初クエリ
     （"Infant Behavior and Development"）は 0 件で、無言で母集団が
     消えるところだった。
4. JASA
   `"The Journal of the Acoustical Society of America"[Journal] AND (fetal OR intrauterine OR womb OR infant) AND (attenuation OR spectrum OR frequency OR "white noise" OR acoustic)`
5. Hearing Research
   `"Hearing Research"[Journal] AND (fetal OR fetus OR newborn OR neonate OR infant) AND (frequency OR pitch OR threshold OR sensitivity)`
   - 適正化理由: 当初クエリは 3,648 件。聴覚の専門誌に対して
     "auditory" "development" はほぼ全論文に当たる包括語で、母集団の
     定義として機能していなかったため除去した。
6. Journal of Music Therapy
   `"Journal of Music Therapy"[Journal] AND (infant OR NICU OR premature OR preterm OR newborn OR neonate)`
   - 再定義理由: 当初のテーマ絞りクエリは 9 件と小さすぎ、母集団として
     偏る。対象（乳児・NICU）で母集団を取り直し、音響と無関係なものは
     スクリーニングで除外する方式に変更した。

### 既知の限界

- Journal of Music Therapy は PubMed 収載が部分的（誌の総収載 598 件）。
  PubMed のみを母集団とする以上、この誌については収載バイアスが残る。
  将来、誌の公式アーカイブ等で補完する場合は、その旨と件数をここに記録する。
- 件数は取得時点のスナップショットであり、PubMed の収載追加で変動する。
  Phase 1 の書誌 CSV を確定した時点で、取得日と PMID 一覧を正とする。

### 別コレクション: 端末スピーカー一次情報

端末補正（DESIGN パラメータフロー (5)）の根拠は、上記 PubMed 母集団とは
**別のコレクション**として literature/device_acoustics/ に置く（母集団は
研究でなくデバイス）。方法論・物理前提・抽出ルールは同フォルダの
SOURCES.md を正とし、層別 A/B/C と混ぜて集計しない。

## 2. スクリーニング（PRISMA 方式）

1. **Identification**: 上記クエリで書誌データ（タイトル・抄録・PMID）を
   ジャーナル別 CSV で取得し、統合する（`literature/`）。
2. **Screening**: 抄録を読み、除外基準に当たるものを機械的に弾く。
   件数の推移（何件→何件）を記録する。
3. **Eligibility**: 残った論文について、Methods（実験刺激の音響
   パラメータ）と Results（睡眠・心拍への効果）から数値を抽出する。
4. **Synthesis**: 抽出値の統計量から設計パラメータを決定する（§4）。

### 層別と除外基準

対象年齢で**層別**する。捨てるのではなく、分けて集計する。

- **Stratum A（主対象）**: 胎児・新生児・乳児（2 歳未満）を含む研究。
  設計パラメータの統計はこの層だけで取る。
- **Stratum B（参照層）**: 対象が 2 歳以上の幼児・成人のみの研究。
  個別に集計し、A の統計には**混ぜない**。用途は (1) 聴覚・鎮静反応の
  発達変化の対照（月齢別プロファイルの裏付け）、(2) A でデータが薄い
  パラメータの参照（参照であることを必ず明示する）。
- **Stratum C（補足層）**: 動物実験のみの研究。補足として保持し、
  個別に集計する。A・B の統計には**混ぜない**。組織の音響減衰など
  物理量の参照に限りうるもので、ヒトの設計値の根拠にはしない。

除外基準（層別とは別に、全層共通で落とすもの）:

- 聴覚障害の診断手法のみを扱う研究
- 音響刺激の条件（音の種類・dB・Hz・BPM のいずれか）が抄録から
  一切読み取れない研究（数値抽出の対象外。ただし件数には数える）

実施記録（2026-11-13）: キーワード一次判定（firstpass）で確定できない
126件（REVIEW 98件＋診断可能性フラグ28件）について、抄録に基づく
手動スクリーニングを実施した（`literature/screening_manual.csv`、
全件に原文の根拠引用つき）。結果: 層別は A 31 / B 12 / C 58 /
UNDETERMINED 25、診断手法のみとして除外 10件、抽出候補は合計
498件（firstpass 確定 437件＋手動 61件）。UNDETERMINED 25件
（抄録なし7件・年齢記載なし18件）は推測で埋めず、本文確認まで
未確定として残す。残り437件の層別は抽出時に再確認する。

## 3. 抽出ルール（恣意性とハルシネーションの排除）

- 抄録内に**明記されている数値のみ**を抽出する。推測・補完はしない。
  記載がない項目は `N/A`。
- 抽出した数値には、根拠として抄録内の該当フレーズ（原文）を必ず併記する
  （抽出シートの `Evidence_Quote` 列）。
- 抽出項目は `literature/extraction_sheet_template.csv` の列定義に従う。
- **照合（二重ろ過）**: 抽出（むぎ）が終わったバッチは、統合前に必ず
  `analysis/validate_extraction.py` で照合する。Evidence_Quote の
  verbatim 一致、数値の引用内存在（kHz→Hz 換算は WARN として記録）、
  PMID の参照整合性、妥当域チェック（WARN のみ、却下には使わない）を
  機械判定し、ERROR が残る行は統合しない。WARN はスポットチェックの
  キューとして扱う。
- **三層目（絞った独立再読）**: 機械照合では捕まえられない「数字の
  意味の取り違え」対策として、対象を絞って一次抽出を見せない再読を
  行い、`analysis/triple_check.py` で突き合わせる。対象は
  (1) A 層で数値を持つ行の全件、(2) 値に関する WARN 行、
  (3) 残りからの無作為サンプル（ミス 0 件なら真のミス率の 95% 上限が
  約 3/n になる rule of three で、上限 5% を狙い n=60、母数が
  小さければ全件）。不一致は抄録で裁定するまで統合しない。

## 4. 統計処理とパラメータ決定ルール

抽出値（Frequency_Hz / Sound_Level_dB / Tempo_BPM）ごとに、通常統計量
（平均 ± SD）とロバスト統計量（中央値 ± 正規化MAD / IQR）を併記し、
以下の規則で設計値へ反映する。

統計の二層構造（2026-11-13 決定）: **設計値の決定はロバスト統計
（中央値・Q1/Q3・正規化MAD）だけで行う**。パラメトリック統計は補足
として併記するもので、その役割は (1) 論文側の「平均 ± SD」報告との
比較、(2) 平均の精度の表示（SE = SD/√n、平均の 95% CI は t 分布に
よる）、(3) 対数尺度での中心の表示に限る。補足の値から設計値を
決めることはしない。検定（t 検定・分散分析等の推測統計）は、比較
する群と問いが具体化するまで入れない。

ロバスト尺度の補足（2026-11-13 決定）: 主役は正規化MAD のまま、
Sn・Qn 推定量（Rousseeuw & Croux 1993）を補足として併記する。
どちらも中心を介さず全ペア差から作るため、左右非対称な分布でも
MAD より歪みに引きずられにくく、効率も高い（Sn 約58% / Qn 約82%、
MAD は約37%）。主役の交代は、抽出値の実分布（歪み・同点率・n）を
見てから根拠つきで判断する。なお同点が過半数を占める場合は
MAD・Sn・Qn とも 0 に潰れる（分布自体が一点集中に近いことの
表れとして記録する）。定義と定数の出典は analysis/stats.py 冒頭に固定。
あわせて四分位ベースの補足として、四分位偏差 (Q3−Q1)/2、IQR を σ 相当に
正規化した IQR/1.3489795 と、非対称の検出器として Bowley 歪度
（(Q3+Q1−2·中央値)/IQR）も併記する（四分位の崩壊点は 25% のため、
こちらも主役にはしない）。

可視化は analysis/plots.py（ドットプロット / 散布図、SVG、標準ライブラリ
のみ）が担う。周波数は対数化が確定しているため対数軸を既定とし、ドット
プロットには Q1〜Q3 の帯と中央値を重ねて、非対称・同点の集中・外れ値を
数値化の前に目で確認する（主役交代の判断はこの確認と Bowley 歪度・
同点率を根拠に行う）。

尺度ごとの扱い:

- Tempo_BPM は線形尺度であり、算術平均をそのまま補足に使う。
- Frequency_Hz は比の尺度であり算術平均は高音側に引っ張られるため、
  補足として幾何平均（exp(平均(log x))）を併記する。
- Sound_Level_dB は既に対数値であり、報告値の算術平均は「文献値の
  中心」であって音響エネルギーの平均ではない。その区別を明記する。

| 条件 | 採用 |
|---|---|
| 通常SD ≈ ロバストSD | コンセンサスが確立した領域として固定値（デフォルト）に採用 |
| 通常SD > ロバストSD | 外れ値混入とみなし、中央値とロバストSD の範囲を標準プリセットに採用。外れ値の PMID と実験条件の特殊性を記録する |
| ロバストSD 自体が大きい | 個体差・条件差が大きい領域として、ロバストSD（±1σ相当）をアプリのスライダー可変域として実装 |

- 安全上限（音圧 dB）は、聴覚保護の観点から統計の下限（安全側）を基準に
  最大音量リミッターを設定する。
- どの規則でどの値になったかは、パラメータ表（Phase 1 の成果物）に
  論文側の根拠とともに記録する。
