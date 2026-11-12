"""Phase 1 の統計量（METHODOLOGY.md §4）。Python 標準ライブラリのみ。

定義の固定（再現性のため、ここで決めて変えない）:
- SD は標本標準偏差（ddof=1）。n=1 では定義できないため None を返す。
- パーセンタイルは線形補間（type 7、numpy の既定・Excel PERCENTILE.INC
  と同じ方式）。Q1 = 25%、中央値 = 50%、Q3 = 75%。
- ロバストSD（正規化MAD）= 1.4826 × MAD。定数 1.4826 は、正規分布の
  とき MAD を SD の一致推定量にするための標準的な換算係数。

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
    """§4 の比較表に必要な統計量をまとめて返す。"""
    xs = _sorted_floats(values)
    sd = sample_sd(xs)
    rsd = robust_sd(xs)
    return {
        "n": len(xs),
        "mean": mean(xs),
        "sd": sd,
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
