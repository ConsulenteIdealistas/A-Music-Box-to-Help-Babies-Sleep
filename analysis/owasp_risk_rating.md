# OWASP Risk Rating Methodology（EV-R03）— 因子表の実物

- 外部情報源: OWASP Risk Rating Methodology（Author: Jeff Williams、OWASP Foundation）
- URL: https://owasp.org/www-community/OWASP_Risk_Rating_Methodology
- 取得日: 2026-11-20
- 取得方法: 実行時取得
- 備考: ページ自体に版番号の記載はない。ページ冒頭には、Threat Actor Skill の重み付けをめぐる議論があること、および Skill に関する編集・PR は受け付けない旨の DISCLAIMER が明記されている。

## 概要（日本語要約）

標準モデルは Risk = Likelihood × Impact。各因子には選択肢があり、それぞれ 0〜9 の値が対応する。Repeatable Method（再現可能な方法）では、選んだ選択肢の値を平均して全体の Likelihood / Impact を算出する。Impact は、ビジネス影響の情報があればそちらを優先し、なければ技術的影響を使う。Step 6（Customizing Your Risk Rating Model）が、因子の追加・選択肢のカスタマイズ・重み付けといったモデル調整の根拠となる。

## Likelihood 因子

### Threat Agent Factors

| 因子 | 選択肢と値 |
|---|---|
| Skill Level | No technical skills (1), some technical skills (3), advanced computer user (5), network and programming skills (6), security penetration skills (9) |
| Motive | Low or no reward (1), possible reward (4), high reward (9) |
| Opportunity | Full access or expensive resources required (0), special access or resources required (4), some access or resources required (7), no access or resources required (9) |
| Size | Developers (2), system administrators (2), intranet users (4), partners (5), authenticated users (6), anonymous Internet users (9) |

### Vulnerability Factors

| 因子 | 選択肢と値 |
|---|---|
| Ease of Discovery | Practically impossible (1), difficult (3), easy (7), automated tools available (9) |
| Ease of Exploit | Theoretical (1), difficult (3), easy (5), automated tools available (9) |
| Awareness | Unknown (1), hidden (4), obvious (6), public knowledge (9) |
| Intrusion Detection | Active detection in application (1), logged and reviewed (3), logged without review (8), not logged (9) |

## Impact 因子

### Technical Impact Factors

| 因子 | 選択肢と値 |
|---|---|
| Loss of Confidentiality | Minimal non-sensitive data disclosed (2), minimal critical data disclosed (6), extensive non-sensitive data disclosed (6), extensive critical data disclosed (7), all data disclosed (9) |
| Loss of Integrity | Minimal slightly corrupt data (1), minimal seriously corrupt data (3), extensive slightly corrupt data (5), extensive seriously corrupt data (7), all data totally corrupt (9) |
| Loss of Availability | Minimal secondary services interrupted (1), minimal primary services interrupted (5), extensive secondary services interrupted (5), extensive primary services interrupted (7), all services completely lost (9) |
| Loss of Accountability | Fully traceable (1), possibly traceable (7), completely anonymous (9) |

### Business Impact Factors

| 因子 | 選択肢と値 |
|---|---|
| Financial damage | Less than the cost to fix the vulnerability (1), minor effect on annual profit (3), significant effect on annual profit (7), bankruptcy (9) |
| Reputation damage | Minimal damage (1), Loss of major accounts (4), loss of goodwill (5), brand damage (9) |
| Non-compliance | Minor violation (2), clear violation (5), high profile violation (7) |
| Privacy violation | One individual (3), hundreds of people (5), thousands of people (7), millions of people (9) |

## レベル対応（Likelihood / Impact 共通）

| 値の範囲 | レベル |
|---|---|
| 0 to <3 | LOW |
| 3 to <6 | MEDIUM |
| 6 to 9 | HIGH |

## Overall Risk Severity 行列

| Impact ＼ Likelihood | LOW | MEDIUM | HIGH |
|---|---|---|---|
| HIGH | Medium | High | Critical |
| MEDIUM | Low | Medium | High |
| LOW | Note | Low | Medium |

## 算出方法の要点（ページ記載のまま）

- Repeatable Method: 各因子で選択した選択肢の数値を表に入れ、スコアの平均を取って全体の Likelihood を算出する（ページ内の例: 8因子の値 5, 2, 7, 1, 3, 6, 9, 2 → Overall likelihood = 4.375 (MEDIUM)）。Impact も同様に平均する（例: Overall technical impact = 7.25 (HIGH)、Overall business impact = 2.25 (LOW)）。
- ビジネス影響の情報がある場合はそれを使い、ない場合は技術的影響を使う。
- Step 6（Customizing Your Risk Rating Model）: 因子の追加、選択肢とスコアのカスタマイズ、因子への重み付け（加重平均）が調整方法として挙げられている。
