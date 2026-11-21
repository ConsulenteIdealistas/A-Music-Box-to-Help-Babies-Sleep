# 外部根拠資料パック（第3弾）— 第2次監査用

監査要項 NewOrderSecondV1.1 が内蔵せず「実行時取得」としている項目リスト（EV-R04 ASVS、EV-R05 SRE チェックリスト）と、因子表の実値（EV-R03）、および内蔵レジストリ（EV-R01 / EV-R02）の再検証結果を、2026-11-20 に実際に取得して備蓄したもの。

（2026-11-21 にリポジトリの analysis/ へ収蔵した。本ファイルは収蔵時に README.md から second_audit_evidence_pack.md へ改名した。他4ファイルは元のファイル名のまま。）

## ファイル構成

| ファイル | 内容 |
|---|---|
| second_audit_evidence_pack.md | 本ファイル。根拠台帳（§17.2 形式）と競合の記録 |
| asvs_level1.md | EV-R04: OWASP ASVS 5.0.0 の Level 1 要件 70件（公式 XML エクスポートから抽出） |
| sre_launch_checklist.md | EV-R05: Google SRE Book 付録E のチェックリスト項目（10カテゴリ・31項目）と、本文が加えるもの |
| owasp_risk_rating.md | EV-R03: OWASP Risk Rating Methodology の因子表（選択肢と 0–9 の値）、レベル対応、重大度行列 |
| iso_models.md | EV-R01 / EV-R02: 内蔵レジストリと二次資料の照合結果 |

## 根拠台帳（§17.2 形式）

| EV-ID | 外部情報源 | 版・発行年 | URL | 取得日 | 根拠として使う内容（日本語で言い換え） | 取得方法 |
|---|---|---|---|---|---|---|
| EV-R01 | Lubos et al. "Leveraging LLMs for the Quality Assurance of Software Requirements"（arXiv:2408.10886） | 2024年 | https://arxiv.org/html/2408.10886v1 | 2026-11-20 | ISO/IEC/IEEE 29148 が定める個別要件の品質特性9件を Table I に整理したもの。要件単体の採点区分Aの判定単位の裏付け | 二次資料で確認 |
| EV-R01 | ISO/IEC/IEEE 29148 チュートリアル（xopsschool.com） | 版の記載なし（29148:2018 の解説） | https://www.xopsschool.com/mod/page/view.php?id=3365 | 2026-11-20 | 要件セットの特性5件（complete, consistent, feasible, comprehensible, able to be validated）の要約。採点区分Bの判定単位の裏付け | 二次資料で確認 |
| EV-R02 | quality.arc42.org "ISO/IEC 25010 - Systems and Software Quality" | 版の記載なし（ISO/IEC 25010:2023 の解説ページ、取得時点の内容） | https://quality.arc42.org/standards/iso-25010 | 2026-11-20 | ISO/IEC 25010:2023 製品品質モデルの9特性と各副特性の一覧。採点区分C1〜C9の判定単位の裏付け | 二次資料で確認 |
| EV-R02 | utaa.org "ISO 25010 and 25059 in the context of software quality" | ページに "As of: 2026-04" の記載 | https://utaa.org/en/dossier/iso-25010-25059-qa-dossier/ | 2026-11-20 | 9特性・40副特性の全表。Testability の所属（Maintainability 側）についての裏付け | 二次資料で確認 |
| EV-R03 | OWASP Risk Rating Methodology（OWASP Foundation、Author: Jeff Williams） | 版番号の記載なし | https://owasp.org/www-community/OWASP_Risk_Rating_Methodology | 2026-11-20 | 脅威エージェント／脆弱性／技術的影響／ビジネス影響の各因子の選択肢と 0–9 の値、LOW・MEDIUM・HIGH の範囲対応、Overall Risk Severity 行列。重大度算出の実値 | 実行時取得 |
| EV-R04 | OWASP Application Security Verification Standard (ASVS)、公式 XML エクスポート（OWASP/ASVS リポジトリ、5.0/docs_en/） | 5.0.0（2025年5月） | https://github.com/OWASP/ASVS/blob/master/5.0/docs_en/OWASP_Application_Security_Verification_Standard_5.0.0_en.xml | 2026-11-20 | Level 1 要件70件（全345件・17章から抽出）。採点区分Dの判定単位（目標レベル未指定時の床 = Level 1） | 実行時取得 |
| EV-R05 | Google SRE Book, Appendix E "Launch Coordination Checklist" | SRE Book オンライン版（チェックリスト原典は circa 2005 とページに明記、若干の省略あり） | https://sre.google/sre-book/launch-checklist/ | 2026-11-20 | ローンチ調整チェックリストの項目（10カテゴリ・31項目）。採点区分Eの判定単位。数値の合否閾値は規定されていない | 実行時取得 |
| EV-R05 | Google SRE Book, "Reliable Product Launches at Scale" | SRE Book オンライン版 | https://sre.google/sre-book/reliable-product-launches/ | 2026-11-20 | チェックリストの位置づけ（LCE による資格審査）、質問／アクション項目の形式例、キュレーション方針。付録Eの項目は増やさない | 実行時取得 |

## 内蔵レジストリ（§17.3）との競合

### 競合あり: EV-R02 の Testability の所属

- 内蔵レジストリは Testability を Maintainability の副特性としている（Maintainability 5件 / Flexibility 4件）。
- レジストリの引用元の一つである arc42 の standards ページは、Testability を Flexibility 側に置いている（Maintainability 4件 / Flexibility 5件）。
- 他方、utaa.org ドシエ等の複数の二次資料と、取得した規格本文抜粋の条項構成（3.7 = Maintainability）はレジストリ側の配置と一致する。
- 特性数（9）と副特性の総数（40）は全資料で一致する。詳細は iso_models.md を参照。
- 影響範囲: §17.5 の採点行 C7 保守性と C8 柔軟性の判定単位数。レジストリの数え方（C7 = 5単位 / C8 = 4単位）が裏付け多数側と一致するが、arc42 を根拠に数える場合は C7 = 4 / C8 = 5 になるため、判定明細ではどちらの配置で数えたかを明示すべきである。

### 競合なし

- EV-R01: 個別要件の特性9件・要件セットの特性5件とも、取得した二次資料と内蔵レジストリが完全一致。
- EV-R03: 因子表、レベル対応（0 to <3 = LOW、3 to <6 = MEDIUM、6 to 9 = HIGH）、重大度行列のいずれも内蔵レジストリと完全一致。
- EV-R04 / EV-R05: 内蔵レジストリは項目リストを持たない（実行時取得が前提）ため、競合は生じない。本パックで取得したリストが実物となる。
- 表記差異のみ（競合ではない）: arc42 の "Appropriateness Recognisability"、"Time Behavior"、"Operational Constraints" は、レジストリの "Appropriateness recognizability"、"Time behaviour"、"Operational constraint" と綴り・単複が異なるだけで、指す内容は同じ。

## 取得できなかった資料

該当なし（計画した全資料を 2026-11-20 に取得できた）。
