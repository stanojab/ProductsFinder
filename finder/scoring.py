"""Score products 0-100. Each component returns 0..1, or None if no data is available."""
import math
from datetime import date

from finder import config
from finder.models import Product


def score_ad_age(days: int) -> float:
    """Piecewise-linear curve: 30+ days is good, 60-90+ days is very strong."""
    curve = config.AD_AGE_CURVE
    if days <= curve[0][0]:
        return curve[0][1]
    for (d0, s0), (d1, s1) in zip(curve, curve[1:]):
        if days <= d1:
            return s0 + (s1 - s0) * (days - d0) / (d1 - d0)
    return curve[-1][1]


def score_new_creatives(count: int) -> float:
    return min(count / config.NEW_CREATIVES_FOR_MAX, 1.0)


def score_active_ads(count: int) -> float:
    return min(count / config.ACTIVE_ADS_FOR_MAX, 1.0)


def score_eu_reach(reach: int) -> float:
    lo, hi = math.log10(config.EU_REACH_FOR_ZERO), math.log10(config.EU_REACH_FOR_MAX)
    if reach <= 0:
        return 0.0
    return min(max((math.log10(reach) - lo) / (hi - lo), 0.0), 1.0)


def score_reviews(product: Product) -> float | None:
    return None  # TODO: e.g. Trustpilot / on-site review counts


def score_traffic(product: Product) -> float | None:
    return None  # TODO: e.g. Similarweb estimate for product.domain


def weighted_total(components: dict[str, float | None]) -> float:
    """Weighted average over available components, scaled to 0-100."""
    available = {k: v for k, v in components.items() if v is not None}
    weight_sum = sum(config.WEIGHTS[k] for k in available)
    if weight_sum == 0:
        return 0.0
    return round(100 * sum(config.WEIGHTS[k] * v for k, v in available.items()) / weight_sum, 1)


def score_product(product: Product, today: date | None = None) -> Product:
    today = today or date.today()
    ages = [(today - ad.start_date).days for ad in product.ads]

    product.active_ads = len(product.ads)
    product.oldest_ad_days = max(ages, default=0)
    product.new_ads_30d = sum(1 for a in ages if a <= config.NEW_CREATIVE_WINDOW_DAYS)
    product.eu_reach = sum(sum(ad.reach_by_country.values()) for ad in product.ads)
    product.present_in_markets = sorted({
        c for ad in product.ads for c, r in ad.reach_by_country.items()
        if r > 0 and c in config.TARGET_MARKETS
    })

    product.components = {
        "ad_age": score_ad_age(product.oldest_ad_days),
        "new_creatives": score_new_creatives(product.new_ads_30d),
        "active_ads": score_active_ads(product.active_ads),
        "eu_reach": score_eu_reach(product.eu_reach),
        "reviews": score_reviews(product),
        "traffic": score_traffic(product),
    }
    product.score = weighted_total(product.components)
    return product


def rank_products(products: list[Product], today: date | None = None) -> list[Product]:
    for p in products:
        score_product(p, today)
    return sorted(products, key=lambda p: (p.score, p.eu_reach), reverse=True)
