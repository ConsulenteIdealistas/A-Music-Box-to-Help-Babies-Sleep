# ISO モデルの再検証（EV-R01 / EV-R02）

- 取得日: 2026-11-20
- 取得方法: 二次資料で確認（両規格とも本文は有料のため、規格本文そのものは読んでいない）
- 検証対象: 監査要項 NewOrderSecondV1.1 の §17.3 内蔵レジストリ（verified 2026-11-12）の記載

## EV-R01: ISO/IEC/IEEE 29148:2018

### 個別要件の特性（9件）

レジストリ記載: Necessary, Appropriate, Unambiguous, Complete, Singular, Feasible, Verifiable, Correct, Conforming

照合元: Lubos et al., "Leveraging LLMs for the Quality Assurance of Software Requirements"（arXiv:2408.10886、2024年）の Table I
URL: https://arxiv.org/html/2408.10886v1

Table I の9件: Appropriate, Complete, Conforming, Correct, Feasible, Necessary, Singular, Unambiguous, Verifiable

→ **一致**（集合として完全一致。並び順のみ異なる）

### 要件セットの特性（5件）

レジストリ記載: Complete, Consistent, Feasible, Comprehensible, Able to be validated

照合元:
- ISO/IEC/IEEE 29148 チュートリアル（xopsschool.com）: "each set should be complete, consistent, feasible, comprehensible and able to be validated" と要約されている。URL: https://www.xopsschool.com/mod/page/view.php?id=3365
- 検索で取得した 29148:2018 本文抜粋でも、§5.2.6 "Characteristics of a set of requirements" の冒頭項目として Complete, Consistent, Feasible が確認できた（抜粋の範囲では残り2件の表示は途中で切れている）。

→ **一致**（5件とも確認できた）

## EV-R02: ISO/IEC 25010:2023（製品品質モデル）

### 特性の数（9件）

レジストリ記載: 9特性。照合元 arc42 の standards ページ（https://quality.arc42.org/standards/iso-25010）も "nine characteristics" と明記。

→ **一致**

### 副特性の総数（40件）

レジストリ記載: 合計40件。arc42 ページの各特性の副特性数を合計しても40件になる。

→ **一致**

### 特性ごとの副特性

| 特性 | レジストリ（件数） | arc42（件数） | 判定 |
|---|---|---|---|
| Functional suitability | 3 | 3 | 一致 |
| Performance efficiency | 3 | 3 | 一致 |
| Compatibility | 2 | 2 | 一致 |
| Interaction capability | 8 | 8 | 一致 |
| Reliability | 4 | 4 | 一致 |
| Security | 6 | 6 | 一致 |
| Maintainability | 5（Testability を含む） | 4（Testability を含まない） | **不一致** |
| Flexibility | 4 | 5（Testability を含む） | **不一致** |
| Safety | 5 | 5 | 一致 |

### 不一致の内容（Testability の所属）

- レジストリ: Testability は Maintainability の副特性（Maintainability 5件 / Flexibility 4件）。
- arc42 の standards ページ: Testability は Flexibility の副特性として並び、Maintainability は Modularity, Reusability, Analysability, Modifiability の4件のみ。
- 裏付け側の二次資料: utaa.org の ISO 25010/25059 ドシエ（https://utaa.org/en/dossier/iso-25010-25059-qa-dossier/）は Maintainability = Modularity · Reusability · Analysability · Modifiability · Testability、Flexibility = Adaptability · Scalability · Installability · Replaceability としており、レジストリと一致する。他の二次資料（cslearningportal、tiespecialistas）も同じ配置だった。
- さらに、検索で取得した ISO/IEC 25010:2023 本文抜粋では、条項 3.7 が Maintainability で、3.7.1 Modularity、3.7.2 Reusability、3.7.3 Analysability、3.7.4 Modifiability と続く構成が確認でき、レジストリ側の配置と整合する。

→ 結論: **Testability の所属について、取得した二次資料の間で競合がある。** レジストリの配置は、arc42 以外の複数の二次資料および規格本文抜粋の条項構成と一致する。ただしレジストリ自身が引用元の一つとして挙げる arc42 の standards ページは異なる配置を示しているため、この点は競合として記録する（README.md の台帳にも記載）。監査要項 §17.5 の採点行では、C7 保守性 = 5単位 / C8 柔軟性 = 4単位というレジストリ側の数え方が、裏付け多数側と一致する。

### 表記差異（実質の不一致ではないもの）

- arc42: "Appropriateness Recognisability" / レジストリ: "Appropriateness recognizability"（綴りの差異）
- arc42: "Time Behavior" / レジストリ: "Time behaviour"（英米綴りの差異）
- arc42: "Operational Constraints"（複数形）/ レジストリ: "Operational constraint"（単数形）。utaa.org ドシエは単数形 "Operational Constraint" でレジストリ寄り。
