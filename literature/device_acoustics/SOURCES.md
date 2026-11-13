# 端末スピーカー一次情報コレクション — 方法論メモ

作成: 2026-11-13。対象は DESIGN.md パラメータフロー (5)「端末スピーカー
補正」の根拠データ。**PubMed 母集団（563件・層別 A/B/C）とは別の
コレクション**であり、混ぜて集計しない。母集団は「研究」ではなく
「デバイス」。

## 1. ソース別: 何が測れて、何が測れないか

### GSMArena（主ソース候補・周波数特性とラウドネス）
- 現行テスト（2020-03 開始）: 統制環境で複数トラック＋全域スイープを
  再生・録音し、周波数特性グラフ（±30dB）と平均ラウドネス（LUFS、
  0 に近いほど大きい）を得る。手法説明:
  https://fo.gsmarena.com/gsmarena_lab_tests-review-751p7.php
- 取れる: 機種横断で同一手法の FR 形状と LUFS。レビュー母数が最大級。
- 取れない: 歪み（THD）の数値。
- 注意: 旧ラウドネステスト（ピーク dB 方式）とは**比較不可**と公式が
  明言。母集団は現行テストのあるレビューのみ。

### DXOMARK Audio（主ソース候補・低域の切れ方と歪み）
- 無響室で純音を再生した 1/12 オクターブ FR グラフ、最大音量時の
  SPL 実測（dBA、楽曲別）、音量依存性、Artifacts（歪み・ポンピング・
  クリッピング）の評価が公開記事に含まれる。低域の切れ方も本文に
  明記されることがある（例: Honor V30 Pro「150Hz 以下で急峻にカット」）。
  例: https://www.dxomark.com/apple-iphone-xs-max-audio-review/
- 取れる: FR、低域カットオフの記述、最大音量 SPL、歪みの定性評価。
- 取れない: 詳細レポートは有償（upon request）。母集団は公開記事から
  取れる範囲に限る。

### Notebookcheck（主ソース候補・母数と帯域別分析）
- 全レビューにピンクノイズ FR 図、最大音量 dB(A)、帯域別分析
  （Bass 100–315Hz / Mids 400–2000Hz / Highs 2–16kHz の中央値比）が
  定型で付く。
- 注意: 測定系の版が年代で変わる（記事内に v5/v6/v7 等の表記）。
  抽出時に版を記録し、版をまたぐ比較では注記する。

### RTINGS（外部スピーカー専用）
- 測定の作法（校正マイク、ピンクノイズで目標レベルに設定、反復平均）
  は厳密だが、対象は単体 Bluetooth スピーカー / サウンドバーであり、
  スマホ内蔵スピーカーの母集団は持たない。「外部スピーカー時
  プロファイル」の根拠としてのみ使う。

### SoundGuys / HEAD acoustics MDAQS（方法論の参照のみ）
- B&K 5128 等の測定系と MDAQS による音質評価。スマホ内蔵スピーカーの
  母集団ではないため主ソースにしない。測定作法の参照として置く。

## 2. 物理の前提（一次資料）と設計規則

- TI SmartAmp アプリケーションノート SLAA858: 保護アルゴリズムは
  スピーカーの**振幅（excursion）と温度を監視し、クリッピング回避の
  ために出力を絞る**。すなわち再生可能域以下を EQ で持ち上げても、
  端末側リミッタが先に効いて音圧は増えず、消費電力と歪みだけが増える。
  https://www.ti.com/jp/lit/an/slaa858/slaa858.pdf
- Cirrus Logic の過振幅保護特許（US9992571B2 等）も同じ前提:
  過大な振幅は機械的損傷・歪みの原因としてモデル化され、能動的に
  抑えられる。https://patents.google.com/patent/US9992571B2/en
- 仮想低音（Virtual Bass Enhancement）の研究（Wallace et al.,
  Reproduced Sound 2022）: ミッシング・ファンダメンタルによる倍音生成は
  EQ ブーストと比較して同一駆動量で強い低音感が得られ、見かけの
  低域拡張は約 1.5 オクターブ。EQ ブーストが有効なのは入力レベルが
  低い場合に限られる。

設計規則（DESIGN の端末補正に適用）:
1. 再生可能域（クラス別カットオフ）**以下はブーストしない**。
   低音の知覚は倍音（ミッシング・ファンダメンタル）で作る。
2. ブースト量の上限は「音圧が増える範囲」までに限る。リミッタが
   効く域への投入は電力と歪みの無駄になるため行わない。
3. カットオフ等のクラス別パラメータは本コレクションの実測分布
   （ロバスト統計、§4 と同じ流儀）から決める。

## 3. 抽出ルール（次工程・本コレクション用）

- FR はグラフ読み取り値になる。読み取りであることを明記し、出典 URL・
  測定条件（ソース、版、音量条件）を必ず併記する。
- 読み取り点は 1/3 オクターブ標準周波数に揃える（125/250/500/1k/2k…）。
  補間した値は「補間」と分かるように記録する。
- LUFS・SPL・FR はソース間で単位系と条件が違うため、**ソースを
  またいで生値を混ぜない**。クラス別パラメータはソース内分布から
  決め、ソース間は順序と傾向の照合に使う。
- devices.csv の URL 列は、実在を確認したレビューだけを記入する
  （未確認は空欄＋ Status=To_located）。

## 4. 規格（電気通信・音響標準）

レビュー実測（§1）が「個々の機種の実力」なら、規格は「測定法・
ラウドネスの定義・許容マスク」という物差しそのものの出典になる。
設計定数を規格の定義に紐付けることで恣意性を排除する。

正直な限界も明記する: 下記規格の主対象は**通話音声**（狭帯域 3.1kHz /
広帯域 7kHz / スーパーワイド帯域）であり、音楽再生の直接の要求規格
ではない。使うのは、測定セットアップ、ラウドネス・レーティングの
定義、FR マスクの考え方、最大音圧の安全側の枠組みである。

- **ITU-T P.313**（2015-06、現行）: 携帯端末・ヘッドセット・
  スピーカーフォンセットの電気音響要求。送受信レベル、周波数特性、
  歪み、線形性の要求と試験法を含む。スピーカーフォンセットの節
  （狭帯域 §10 / 広帯域 §13）が端末スピーカー再生に最も近い。
  https://www.itu.int/dms_pubrec/itu-t/rec/p/T-REC-P.313-201506-I!!SUM-HTM-E.htm
- **3GPP TS 26.131 / TS 26.132**: 端末音響特性の要求（26.131）と
  試験仕様（26.132）。ハンドヘルド・ハンズフリー（=スピーカー
  フォンモード）のラウドネス・レーティングと周波数特性マスクを
  帯域別に規定し、CTIA の認証テストプランもこれを参照する。
  https://api.ctia.org/docs/default-source/default-document-library/ctia-speech-performance-test-plan.pdf
- **ETSI STQ（Speech and multimedia Transmission Quality）**:
  TS 103 738（狭帯域ワイヤレス・ハンズフリー伝送要求）、
  TS 103 740（広帯域版、送受信 FR マスクを含む）、
  EG 202 518（端末音響出力の最大レベルと測定法。聴覚安全側の
  上限を考える際の出典）。測定環境の再現法として TS 103 224
  （背景雑音）/ TS 103 557（残響）もある。
  https://standards.iteh.ai/catalog/standards/etsi/a96e0e20-129a-49ae-9224-bd7c1e3a78b5/etsi-ts-103-740-v1-1-2-2010-09
- 関連: ITU-T P.341（広帯域ハンズフリー端末の伝送特性）、
  ITU-T P.79（ラウドネス・レーティングの計算法）、P.501（試験信号）。

## 5. マイクロスピーカーの物理モデリング文献（AES / JASA）

端末スピーカーの低域限界と歪みは、ドライバの物理パラメータ
（Thiele–Small パラメータ、共振周波数 Fs、最大振幅 Xmax、非線形
パラメータ）で決まる。クラス別カットオフやブースト上限を
「レビュー記事の印象」でなく物理量で語るための基盤文献。

- Klippel, W. "Modeling the Large Signal Behavior of Micro-Speakers"
  (2012): 携帯電話用マイクロスピーカーの非線形集中定数モデル。
  Bl(x)・Kms(x) に加え、マイクロスピーカーでは機械・音響損失
  Rms(v) が歪みの支配要因になることを実測で検証。
  https://www.klippel.de/fileadmin/klippel/Files/Know_How/Literature/Papers/KLIPPEL%20Modeling%20the%20Large%20Signal%20Behavior%20of%20Micro-Speakers.pdf
- Klippel, W. "Tutorial: Loudspeaker Nonlinearities — Causes,
  Parameters, Symptoms", J. Audio Eng. Soc. 54(10), 907–939 (2006):
  非線形の原因・パラメータ・症状（高調波/相互変調歪み）の総説。
- Bai, M. R. & Liao, J. "Acoustic Analysis and Design of Miniature
  Loudspeakers for Mobile Phones", J. Audio Eng. Soc. 53(11),
  1061–1076 (2005): 携帯電話内蔵の小型スピーカーについて、
  Thiele–Small パラメータの同定、電気-機械-音響等価回路、ダクト
  構造とヘッド回折を含むシミュレーション。
  https://secure.aes.org/forum/pubs/journal/?elib=13399
- "Preventing damage to miniature-loudspeaker by means of dynamic
  detection of excessive diaphragm displacement", J. Acoust. Soc.
  Am. 141, 1615–1626 (2017): 非線形パラメータ推定と振幅リミッタ
  による損傷防止。スマートアンプの保護が物理量（振幅）ベースで
  あることの学術側の裏付けで、§2 の設計規則 1・2 の根拠になる。
  https://pubs.aip.org/asa/jasa/article-abstract/141/3/1615/1056445/Preventing-damage-to-miniature-loudspeaker-by
- Brunet, P. et al. "Specifying Xmax for micro-speakers and smart
  amplifiers", 137th AES Convention (2014), e-Library 9114:
  マイクロスピーカーの Xmax の定義（ブースト上限を語る際の物差し）。

使い方: カットオフは Fs と筐体（背気積・ダクト）の帰結として、
ブースト上限は Xmax と非線形症状の発現レベルとして説明できる
形にする。数値そのものは §1 の実測分布と突き合わせて決める。
