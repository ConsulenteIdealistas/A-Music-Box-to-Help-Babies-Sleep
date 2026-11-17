# ACID / RASIS 監査（2026-11-17）

## 範囲と方法

対象は PWA の状態・永続化まわり（app/app.js、app/index.html、
app/sw.js）と監査台帳の検証手段。音響パラメータ、プリセット値、
正常系の振る舞いは変更していない。

観点:
- ACID: プリセット適用と保存を「状態遷移のトランザクション」と
  みなし、Atomicity（一部だけ変わった状態を作らない）、
  Isolation（予約済み処理と手動操作の競合）、Durability
  （保存したものが黙って消えない）を点検した
- RASIS: Reliability（失敗が黙って起きない）、Availability
  （一部が欠けても全体が動く）、Serviceability（版数が外から
  分かる）、Integrity（台帳の形式検証）、Security（入力の上限）

方法はコード読み取り＋ Node ハーネスによる動的検証
（DOM / localStorage / タイマのスタブ）。実機・実ブラウザでの
確認は含まない。

## 指摘と修正

| # | 観点 | 問題 | 修正 |
|---|------|------|------|
| F1 | ACID: Atomicity / Isolation | applyPreset が then を素の setTimeout で予約し、取り消し手段が無かった。別のプリセット適用・停止・手動編集の後でも予約が発火し、意図しない状態へ遷移した | 予約を thenTimer ハンドルで保持し、applyPreset の先頭、stop()、bpm スライダと音量スライダの手動入力で取り消すようにした |
| F2 | ACID: Isolation | gain 遷移が 50 ms ごとに音量スライダを書き換え続けるため、ドラッグ中の手動操作と競合した（bpm スライダだけが遷移を取り消していた） | 音量スライダの input で対応する gain 遷移（gain.music / heart / waves）を cancelTween するようにした。bpm と同じパターン |
| F3 | ACID: Atomicity | crossfadeMusicTo が loadSong の await 中に世代管理なしで、ローパスの連続変更で2つのクロスフェードが交錯し、musicSrc / musicOffset の帳尻が壊れ得た | 世代カウンタ musicCrossfadeGen を追加し、await の後に世代が進んでいたら新しい側の状態に触らず中断するようにした |
| F4 | ACID: Durability | loadUserPresets が JSON 破損時に保存分を黙って全捨てしていた | 破損した生文字列を lullaby.presets.corrupt キーへ退避してから [] に初期化するよう変更。配列でない値も同じ扱い |
| F5 | ACID: Durability | storeUserPresets が書き込み失敗（容量超過等）を握りつぶし、保存できたように見えた | 成否を boolean で返すよう変更。保存・削除・読み込みの各ハンドラは、永続化に失敗したら importStatus にその旨を表示する（成功時は従来どおり静か） |
| F6 | Integrity | 正本 presets.json が無検証で読み込まれていた（読み込みファイル側だけ検証していた） | validatePresetData を通してから使うよう変更。不正な場合は標準プリセットなしとして扱い、console.warn を出す |
| F7 | Security | プリセット読み込みがファイルサイズ無制限だった | 1 MB を超えるファイルは読む前に弾き、理由を表示する |
| F8 | Reliability | presets.json の読み込み失敗時にプリセット欄が黙って空になった | importStatus に「標準プリセットを読み込めませんでした」を表示する（形式不正の場合も同じ表示） |
| F9 | Availability | sw.js のインストールが addAll 一括で、presets.json の 404 ひとつでシェル全体が入らずオフラインが成立しなかった | コアシェル（HTML/CSS/JS/manifest）は addAll、presets.json は分けて cache.add し失敗を許容するよう変更。キャッシュ名を lullaby-shell-v4 に更新 |
| F10 | Serviceability | 画面からアプリの版数が分からず、問い合わせ時に切り分けできなかった | index.html のロックボタン下に `app version: lullaby-shell-v4` のフッター注記を追加（sw.js のキャッシュ名と揃える） |
| F11 | Reliability | play() で AudioContext の生成が例外を投げると無反応になった | buildGraph を try/catch で囲み、失敗時は songStatus に「音声を開始できませんでした」を表示する |
| F12 | Integrity | 監査台帳の形式（必須フィールド、ID 一意性、decision の許容値）を機械的に確認する手段が無かった | analysis/validate_audit_ledger.py を追加（標準ライブラリのみ）。台帳 JSON と参照 CSV を検証し、問題があれば一覧と終了コード 1 を返す。現行台帳では OK |

## 確認して問題なかった項目

- プリセット名は textContent で描画されており、innerHTML 経由の
  注入経路は無い（読み込んだ JSON の name も同じ経路）
- 外部データのパースは JSON.parse のみで、eval 等は使っていない
- Service Worker の activate で旧キャッシュを全て削除している
- play / stop の競合には playGen ガードが既にある
- 読み込み（インポート）の検証は全体拒否方式で、部分取り込みに
  よる中途半端な保存状態を作らない

## 先送りした項目

- Content-Security-Policy の meta 付与: 実機で確認できない環境で
  誤ったポリシーを入れるとアプリ自体が動かなくなるため、今回は
  見送り。実機確認の機会に合わせて入れる
- GitHub へのスナップショット push と同期記録への追記が2段に
  分かれている件: 中断すると同期記録がリモートより遅れるが、
  リモートのコミット一覧から復旧できる運用上の注意に留め、
  コード変更はしない

## 検証

- `node --check app/app.js` / `app/sw.js`: 問題なし
- Node ハーネス（新規、DOM / localStorage / フェイクタイマの
  スタブ）: 15/15 パス。動的に確認したのは、validatePresetData が
  正本 presets.json を受理すること、破損 JSON の隔離退避と初期化、
  storeUserPresets の成否返却と保存失敗の表示、then の予約が
  stop() と次の applyPreset で取り消されること、発火した then が
  正常に適用されること、1 MB 超ファイルの事前拒否
- 既存の読み込み検証ハーネス: 13/13 パス（回帰なし）
- `python3 analysis/validate_audit_ledger.py`: OK（終了コード 0）

動的検証の対象外（読み取り確認のみ）: F2 の遷移取り消しの意味論
（再生中にしか発生しない）、F3 の世代ガード、F9 の Service
Worker インストール経路、F10 の表示、F11 の例外経路。
いずれも実ブラウザ・実機での確認が別途必要。

## 対応 Issue（2026-11-17、外部監査レポートを受けて起票）

本監査の残件と、外部監査で新たに見つかった関連指摘は GitHub Issue で追跡する。
- F5 の残件（永続化失敗時のロールバック）: Issue #1
- F2/F3/F9/F11 の実機確認、CSP、A 層校正: Issue #13（Phase 4 前提条件チェックリスト: analysis/phase4_preconditions_checklist_2026-11-17.md）
- 検証ハーネスの所在（本監査が引用したハーネスは app/tests/ に収蔵済み）: Issue #6
- 外部監査の新規指摘（lowpass の状態乖離、loadUserPresets の検証）: Issues #3, #4
- 追跡の土台: Issue #14
