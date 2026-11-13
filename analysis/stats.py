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


def mad(values):
    med = median(values)
    return median([abs(float(v) - med) for v in values])


def robust_sd(values):
    return MAD_TO_SD * mad(values)


def summarize(values):
    """§4 の比較表に必要な統計量をまとめて返す。

    ロバスト統計が主役、パラメトリック統計（mean/sd/se/mean_ci_95/
    geometric_mean）は補足。geometric_mean は 0 以下の値を含むと None。
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
        "median": median(xs),
        "q1": q1(xs),
        "q3": q3(xs),
        "iqr": iqr(xs),
        "mad": mad(xs),
        "robust_sd": rsd,
        "min": xs[0],
        "max": xs[-1],
        # 乖離の大きさの記録用（判定の閾値は未定義につき自動判定しない）
        "sd_ratio": (sd / rsd) if (sd is not None and rsd) else None,
    }
