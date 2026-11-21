# Google SRE Book, Appendix E "Launch Coordination Checklist"（EV-R05）— 項目リスト実物

- 外部情報源: Google SRE Book, Appendix E "Launch Coordination Checklist"
- URL: https://sre.google/sre-book/launch-checklist/
- 取得日: 2026-11-20
- 取得方法: 実行時取得
- 原典の注記: ページ冒頭に「This is Google's original Launch Coordination Checklist, circa 2005, slightly abridged for brevity」と明記されている（2005年頃の原典を若干省略した版）。

## 数値閾値について（明示記録）

このチェックリストは、**合格・不合格の数値閾値（合格ラインとなる件数や割合）を規定していない**。取得した付録Eのページにも、後述の SRE Book 本文（Reliable Product Launches at Scale）にも、数値による合否基準は存在しない。充足率の分母として項目数を使うことはできても、合否閾値をこの資料から作ることはできない。

## 項目数

- カテゴリ: 10件
- 項目（末端の箇条書き）: 31件
- このほかに、配下の項目を束ねる導入句（太字のリードイン）が2件ある（"What happens when:" と "For each type of server that talks to other servers (its backends):"）。導入句は項目数に含めていない。

## 項目リスト（カテゴリ見出し・項目名はページの原文のまま）

### Architecture

- Architecture sketch, types of servers, types of requests from clients — アーキテクチャの概要図、サーバの種類、クライアントからのリクエストの種類
- Programmatic client requests — プログラム的なクライアントリクエストの扱い

### Machines and datacenters

- Machines and bandwidth, datacenters, N+2 redundancy, network QoS — マシンと帯域、データセンター、N+2 冗長性、ネットワーク QoS
- New domain names, DNS load balancing — 新規ドメイン名、DNS ロードバランシング

### Volume estimates, capacity, and performance

- HTTP traffic and bandwidth estimates, launch "spike," traffic mix, 6 months out — HTTP トラフィックと帯域の見積もり、ローンチ時の「スパイク」、トラフィック構成、6か月先までの見通し
- Load test, end-to-end test, capacity per datacenter at max latency — 負荷テスト、エンドツーエンドテスト、最大レイテンシ時のデータセンターごとの容量
- Impact on other services we care most about — 最も重視する他サービスへの影響
- Storage capacity — ストレージ容量

### System reliability and failover

- **What happens when:**（導入句：次の事態に何が起きるか）
  - Machine dies, rack fails, or cluster goes offline — マシン故障、ラック障害、クラスタがオフラインになった場合
  - Network fails between two datacenters — 2つのデータセンター間のネットワークが故障した場合
- **For each type of server that talks to other servers (its backends):**（導入句：バックエンドと通信するサーバの種別ごとに）
  - How to detect when backends die, and what to do when they die — バックエンドの停止をどう検知し、停止時にどうするか
  - How to terminate or restart without affecting clients or users — クライアントやユーザーに影響を与えずに終了・再起動する方法
  - Load balancing, rate-limiting, timeout, retry and error handling behavior — ロードバランシング、レート制限、タイムアウト、リトライ、エラー処理の挙動
- Data backup/restore, disaster recovery — データのバックアップ／リストア、災害復旧

### Monitoring and server management

- Monitoring internal state, monitoring end-to-end behavior, managing alerts — 内部状態の監視、エンドツーエンド挙動の監視、アラートの管理
- Monitoring the monitoring — 監視そのものの監視
- Financially important alerts and logs — 財務的に重要なアラートとログ
- Tips for running servers within cluster environment — クラスタ環境でサーバを運用する際の留意点
- Don't crash mail servers by sending yourself email alerts in your own server code — 自分のサーバコードから自分宛てにメールアラートを送ってメールサーバを落とさないこと

### Security

- Security design review, security code audit, spam risk, authentication, SSL — セキュリティ設計レビュー、セキュリティコード監査、スパムリスク、認証、SSL
- Prelaunch visibility/access control, various types of blacklists — ローンチ前の公開範囲／アクセス制御、各種ブラックリスト

### Automation and manual tasks

- Methods and change control to update servers, data, and configs — サーバ、データ、設定を更新する手順と変更管理
- Release process, repeatable builds, canaries under live traffic, staged rollouts — リリースプロセス、再現可能なビルド、本番トラフィックでのカナリア、段階的ロールアウト

### Growth issues

- Spare capacity, 10x growth, growth alerts — 余剰容量、10倍の成長、成長アラート
- Scalability bottlenecks, linear scaling, scaling with hardware, changes needed — スケーラビリティのボトルネック、線形スケーリング、ハードウェアによる拡張、必要な変更
- Caching, data sharding/resharding — キャッシュ、データのシャーディング／リシャーディング

### External dependencies

- Third-party systems, monitoring, networking, traffic volume, launch spikes — サードパーティシステム、監視、ネットワーク、トラフィック量、ローンチスパイク
- Graceful degradation, how to avoid accidentally overrunning third-party services — グレースフルデグラデーション、サードパーティサービスを誤って過負荷にしない方法
- Playing nice with syndicated partners, mail systems, services within Google — シンジケーションパートナー、メールシステム、Google 内のサービスとの協調

### Schedule and rollout planning

- Hard deadlines, external events, Mondays or Fridays — ハードな締切、外部イベント、月曜や金曜への配慮
- Standard operating procedures for this service, for other services — このサービス向け、および他サービス向けの標準運用手順

## SRE Book 本文「Reliable Product Launches at Scale」が加えるもの

URL: https://sre.google/sre-book/reliable-product-launches/（取得日: 2026-11-20、取得方法: 実行時取得）

この章は付録Eの項目リスト自体は増やさないが、次を加える。

- チェックリストの位置づけ: Launch Coordination Engineering（LCE）がローンチの資格審査に使うもので、本文から付録E（Launch Coordination Checklist）へ明示的にリンクされている。
- 質問／アクション項目の形式の例: 「Do you need a new domain name?」（アクション: マーケティングと調整しドメイン登録を依頼する）、「Are you storing persistent data?」（アクション: バックアップを実装する）、「Could a user potentially abuse your service?」（アクション: レート制限とクォータを実装する）。
- 「Developing a Launch Checklist」の節では、テーマ別の例示質問群（アーキテクチャレビュー、社内インフラへの組み込み、ローンチスパイクと容量、障害モード、クライアントの abusive な挙動、手作業プロセス、バージョン管理、外部依存、ロールアウト計画）が示される。これらは例示であり、付録Eの項目リストそのものではない。
- キュレーション方針: 各質問の重要性は（理想的には過去のローンチ障害によって）裏付けられなければならないこと、指示は具体的・実践的・合理的でなければならないこと、チェックリストは継続的に手入れされ、年1〜2回全体レビューが行われること。
- 段階的ロールアウト、カナリア、フィーチャーフラグ、指数バックオフとジッタ等の技法は本文の別節（Selected Techniques for Reliable Launches 等）で扱われ、チェックリスト項目としては数えない。
- 初期の Launch Engineers 時代のチェックリストの話題として、法務部門へ相談すべきタイミング、ドメイン名の選定、DNS を誤設定せずに新規ドメインを登録する方法、設計と本番デプロイの典型的な落とし穴、が挙げられている。
