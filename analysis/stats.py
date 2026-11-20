"""Phase 1 の統計量（METHODOLOGY.md §4）。Python 標準ライブラリのみ。

統計の二層構造（2026-11-13 決定）:
- 主役はロバスト統計（中央値・Q1/Q3・正規化MAD）。設計値の決定は
  この層だけで行う。
- パラメトリック統計（平均・SD・SE・幾何平均）は補足として併記する。
  役割は (1) 論文側の「平均±SD」報告との比較、(2) 平均の精度の表示、
  (3) 周波数のような対数尺度での中心の表示に限る。補足の値から
  設計値を決めることはしない。検定（t検定等）は入れない。

定義の固定（再現性のため、ここで決めて変えない）:
- SD は標本標準偏差（ddof=1）。n=1 では定義できないため None を返す。
- パーセンタイルは線形補間（type 7、numpy の既定・Excel PERCENTILE.INC
  と同じ方式）。Q1 = 25%、中央値 = 50%、Q3 = 75%。
- ロバストSD（正規化MAD）= 1.4826 × MAD。定数 1.4826 は、正規分布の
  とき MAD を SD の一致推定量にするための標準的な換算係数。
- SE（平均の標準誤差）= SD ÷ √n。n<2 では None。
- 平均の 95% CI は t 分布による区間（自由度 n-1、両側 95%）。
  補足表示専用であり、設計値の決定には使わない。n<2 では None。
- 幾何平均 = exp(平均(log x))。周波数 Hz のような比の尺度で使う。
  0 以下の値を含む場合は定義できない（geometric_mean は ValueError、
  summarize では None）。
- Sn / Qn 推定量（Rousseeuw & Croux 1993）は補足のロバスト尺度。
  中心（中央値）を介さず全ペア差 |x_i − x_j| から作るため、左右非対称な
  分布でも MAD より歪みに引きずられにくい。正規化MAD が主役のままで、
  主役の交代は実データの分布（歪み・同点率・n）を見てから判断する。
  - Sn = 1.1926 · c_n · lowmed_i( highmed_j |x_i − x_j| )。
    high median は順序統計量の ⌊n/2⌋+1 番目、low median は ⌊(n+1)/2⌋ 番目。
  - Qn = 2.219144 · d_n · {|x_i − x_j|; i<j} の k 番目（k = C(⌊n/2⌋+1, 2)）。
    定数 2.219144 = 1/(√2·Φ^-1(5/8))。原論文等の 2.2219 は誤植であり
    使わない（Akinshin 2022, arXiv:2209.12268 が指摘）。
  - 有限標本修正: Sn の c_n は Croux & Rousseeuw (1992) の表（n≤9）と
    予測式（n≥10: 奇数 n/(n−0.9)・偶数 1）のまま。これは R robustbase の
    Sn とも全 n で一致することを 2026-11-17 に実測で確認した。
    Qn の d_n は当初 CR92 の近似（表 n≤9 + 予測式 奇数 n/(n+1.4)・
    偶数 n/(n+3.8)）を使い「補足用途では十分」と判断していたが、
    2026-11-17 の robustbase とのクロスチェックで、CR92 の係数は
    後年の文献（Akinshin 2022）が "rough approximations" と記す粗い
    近似であり、系統差が n=10 で最大 0.62%・実データの n=110 でも
    0.093% あると判明したため、同日に robustbase の係数へ切り替えた
    （ユーザーの決定）。robustbase の d_n は Maechler の大規模
    シミュレーション由来で、n≤12 は精密な表、n>12 は 1/n の
    3次/4次多項式モデル（Qn.finite.c の逆数）。Akinshin (2022) の
    refined 係数とも n=100 で 0.002% 差で一致する。
  - Qn はペアが存在しない n=1 では定義できないため None を返す。
- 四分位ベースの補足（2026-11-13 追加）: 四分位偏差 = (Q3−Q1)/2、
  IQR 正規化 SD = IQR / 1.3489795（1.3489795 = 2·Φ^-1(0.75)、正規分布の
  IQR が σ のこの倍数になることからの換算で、MAD の 1.4826 と同種）。
  四分位は外れ値に触れないためロバストだが、崩壊点は 25% で
  MAD / Sn / Qn（50%）より低い。Bowley 歪度 = (Q3 + Q1 − 2·中央値) / IQR
  は −1〜+1 で分布の左右非対称そのものを測る（主役交代の判断材料）。
  IQR = 0 では Bowley 歪度は定義できないため None を返す。

§4 の「通常SD ≈ ロバストSD」の判定は、乖離の許容幅という新しい定数を
必要とするため、ここでは自動判定せず sd_ratio（通常SD ÷ ロバストSD）を
返すところまでとする。許容幅は別途、根拠つきで決める。
"""
import math

MAD_TO_SD = 1.4826


def _sorted_floats(values):
    xs = sorted(float(v) for v in values)
    if not xs:
        raise ValueError("values must not be empty")
    return xs


def mean(values):
    xs = _sorted_floats(values)
    return sum(xs) / len(xs)


def sample_sd(values):
    xs = _sorted_floats(values)
    if len(xs) < 2:
        return None
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def se_mean(values):
    """平均の標準誤差 SD/√n。n<2 では None。"""
    xs = _sorted_floats(values)
    sd = sample_sd(xs)
    if sd is None:
        return None
    return sd / math.sqrt(len(xs))


def _betacf(a, b, x):
    """正則化不完全ベータ関数の連分数（Numerical Recipes の betacf）。"""
    max_iter, eps, fp_min = 200, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fp_min:
        d = fp_min
    d = 1.0 / d
    h = d
    for m in range(1, max_iter + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fp_min:
            d = fp_min
        c = 1.0 + aa / c
        if abs(c) < fp_min:
            c = fp_min
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fp_min:
            d = fp_min
        c = 1.0 + aa / c
        if abs(c) < fp_min:
            c = fp_min
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def _betainc(a, b, x):
    """正則化不完全ベータ関数 I_x(a, b)。"""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(x) + b * math.log(1.0 - x)
    )
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def _t_cdf(t, df):
    x = df / (df + t * t)
    ib = _betainc(df / 2.0, 0.5, x)
    if t >= 0:
        return 1.0 - 0.5 * ib
    return 0.5 * ib


def t_critical_975(df):
    """t 分布の両側 95% の臨界値（97.5 パーセンタイル）。二分探索で求める。"""
    if df < 1:
        raise ValueError("df must be >= 1")
    lo, hi = 0.0, 1.0
    while _t_cdf(hi, df) < 0.975:
        hi *= 2.0
    for _ in range(100):
        mid = (lo + hi) / 2.0
        if _t_cdf(mid, df) < 0.975:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def mean_ci_95(values):
    """平均の 95% 信頼区間 (low, high)。n<2 では None。補足表示専用。"""
    xs = _sorted_floats(values)
    se = se_mean(xs)
    if se is None:
        return None
    m = mean(xs)
    if se == 0.0:
        return (m, m)
    margin = t_critical_975(len(xs) - 1) * se
    return (m - margin, m + margin)


def geometric_mean(values):
    """幾何平均 exp(平均(log x))。0 以下の値を含む場合は ValueError。"""
    xs = _sorted_floats(values)
    if any(x <= 0.0 for x in xs):
        raise ValueError("geometric mean requires all values > 0")
    return math.exp(sum(math.log(x) for x in xs) / len(xs))


SN_CONSTANT = 1.1926
QN_CONSTANT = 2.21914446598508  # 1/(sqrt(2) * Phi^-1(5/8)); 2.2219 は原論文の誤植

# 有限標本修正: Sn は Croux & Rousseeuw (1992) の表（n<=9）、
# Qn は robustbase の精密な表（n<=12、Maechler のシミュレーション由来）
_SN_FINITE = {2: 0.743, 3: 1.851, 4: 0.954, 5: 1.351, 6: 0.993,
              7: 1.198, 8: 1.005, 9: 1.131}
_QN_FINITE = {2: 0.399356, 3: 0.99365, 4: 0.51321, 5: 0.84401, 6: 0.6122,
              7: 0.85877, 8: 0.66993, 9: 0.87344, 10: 0.72014, 11: 0.88906,
              12: 0.75743}


def _sn_correction(n):
    if n in _SN_FINITE:
        return _SN_FINITE[n]
    return n / (n - 0.9) if n % 2 == 1 else 1.0


def _qn_finite_c(n):
    """robustbase の Qn.finite.c（n>12 用）。d_n の逆数を返す。

    1/n の多項式モデル: 奇数 n は3次、偶数 n は4次（robustbase の
    ヘルプ Details: 大規模シミュレーションへの多項式フィット）。
    """
    if n % 2 == 1:
        return 1.0 + (1.60188 + (-2.1284 - 5.172 / n) / n) / n
    return 1.0 + (3.67561 + (1.9654 + (6.987 - 77.0 / n) / n) / n) / n


def _qn_correction(n):
    if n in _QN_FINITE:
        return _QN_FINITE[n]
    return 1.0 / _qn_finite_c(n)


def sn_estimator(values):
    """Sn 推定量（Rousseeuw & Croux）。補足のロバスト尺度。"""
    xs = _sorted_floats(values)
    n = len(xs)
    if n == 1:
        return 0.0
    # inner: high median（⌊n/2⌋+1 番目、0-indexed では ⌊n/2⌋）
    inner = []
    for x in xs:
        diffs = sorted(abs(x - y) for y in xs)
        inner.append(diffs[n // 2])
    inner.sort()
    # outer: low median（⌊(n+1)/2⌋ 番目、0-indexed では ⌊(n+1)/2⌋−1 = n//2 if odd else n//2−1）
    low_med = inner[(n + 1) // 2 - 1]
    return SN_CONSTANT * _sn_correction(n) * low_med


def qn_estimator(values):
    """Qn 推定量（Rousseeuw & Croux）。補足のロバスト尺度。n=1 では None。"""
    xs = _sorted_floats(values)
    n = len(xs)
    if n < 2:
        return None
    diffs = sorted(abs(xs[i] - xs[j]) for i in range(n) for j in range(i + 1, n))
    h = n // 2 + 1
    k = h * (h - 1) // 2  # C(h, 2)、1-indexed の順序統計量
    return QN_CONSTANT * _qn_correction(n) * diffs[k - 1]


def percentile(values, p):
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be in [0, 1]")
    xs = _sorted_floats(values)
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * p
    f = math.floor(k)
    c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)


def median(values):
    return percentile(values, 0.5)


def q1(values):
    return percentile(values, 0.25)


def q3(values):
    return percentile(values, 0.75)


def iqr(values):
    return q3(values) - q1(values)


IQR_TO_SD = 1.3489795003921634  # 2 * Phi^-1(0.75)


def quartile_deviation(values):
    """四分位偏差 (Q3−Q1)/2。補足のロバスト尺度。"""
    return iqr(values) / 2.0


def iqr_sd(values):
    """IQR を σ 相当に正規化した尺度 IQR/1.3489795。補足。"""
    return iqr(values) / IQR_TO_SD


def bowley_skewness(values):
    """Bowley 歪度 (Q3+Q1−2·中央値)/IQR。IQR=0 では None。"""
    xs = _sorted_floats(values)
    spread = iqr(xs)
    if spread == 0.0:
        return None
    return (q3(xs) + q1(xs) - 2.0 * median(xs)) / spread


def mad(values):
    med = median(values)
    return median([abs(float(v) - med) for v in values])


def robust_sd(values):
    return MAD_TO_SD * mad(values)


def summarize(values):
    """§4 の比較表に必要な統計量をまとめて返す。

    ロバスト統計が主役、パラメトリック統計（mean/sd/se/mean_ci_95/
    geometric_mean）は補足。geometric_mean は 0 以下の値を含むと None。
    sn / qn は補足のロバスト尺度（主役は正規化MAD のまま）。
    """
    xs = _sorted_floats(values)
    sd = sample_sd(xs)
    rsd = robust_sd(xs)
    return {
        "n": len(xs),
        "mean": mean(xs),
        "sd": sd,
        "se": se_mean(xs),
        "mean_ci_95": mean_ci_95(xs),
        "geometric_mean": geometric_mean(xs) if all(x > 0.0 for x in xs) else None,
        "sn": sn_estimator(xs),
        "qn": qn_estimator(xs),
        "median": median(xs),
        "q1": q1(xs),
        "q3": q3(xs),
        "iqr": iqr(xs),
        "quartile_deviation": quartile_deviation(xs),
        "iqr_sd": iqr_sd(xs),
        "bowley_skewness": bowley_skewness(xs),
        "mad": mad(xs),
        "robust_sd": rsd,
        "min": xs[0],
        "max": xs[-1],
        # 乖離の大きさの記録用（判定の閾値は未定義につき自動判定しない）
        "sd_ratio": (sd / rsd) if (sd is not None and rsd) else None,
    }
