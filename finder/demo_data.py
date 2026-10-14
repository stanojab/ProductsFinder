"""Realistic fake ads for --demo mode.

Dates are relative to today, so ad ages stay meaningful whenever the demo runs.
A fixed random seed makes every run produce the same data.
"""
import random
from datetime import date, timedelta

from finder.models import Ad

# Reach per ad (min, max), split across the ad's countries.
REACH = {"high": (30_000, 70_000), "medium": (5_000, 20_000), "low": (300, 2_000)}

# (page_id, page_name, landing_url, ad copy, oldest_days, total_ads, new_ads_30d, reach, countries)
PRODUCTS = [
    # Clear winners: long-running, scaling, big reach, not in our markets
    ("101", "BambooBro", "https://www.bamboobro.com/products/boxers-3-pack",
     "Bamboo boxers that never ride up. Softer than cotton, 3-pack for men.",
     112, 26, 8, "high", ["FR", "ES", "NL", "AT"]),
    ("102", "Merinoo", "https://merinoo.fr/merino-socks",
     "Merino wool socks that don't smell, even after 3 days. 5-pair everyday pack.",
     95, 22, 7, "high", ["FR", "ES", "BE"]),
    ("103", "HeavyCotton Co.", "https://www.heavycotton.eu/oversized-t-shirt",
     "300 gsm heavyweight oversized t-shirt. Holds its shape after 100 washes.",
     74, 18, 6, "high", ["NL", "AT", "FR", "SE"]),
    ("104", "AirPouch", "https://airpouch.shop/pouch-boxers",
     "Pouch boxers with separate support. No chafing, no adjusting, all day.",
     88, 20, 5, "high", ["FR", "ES", "NL"]),
    ("105", "Undershirt Club", "https://undershirtclub.com/invisible-v-neck",
     "Invisible V-neck undershirt. Sweat-proof, stays tucked, can't be seen under a shirt.",
     67, 17, 6, "high", ["ES", "FR", "PT"]),
    # Promising: a month or two old, medium activity
    ("106", "CompressFit", "https://compressfit.com/compression-socks",
     "Graduated compression socks for flights, runs and long shifts.",
     48, 9, 4, "medium", ["NL", "BE", "FR"]),
    ("107", "DailyBasics", "https://www.dailybasics.store/t-shirt-5-pack",
     "Organic cotton t-shirt 5-pack. The only basics you need, one price.",
     41, 8, 3, "medium", ["AT", "FR", "ES"]),
    ("108", "ThermoFeet", "https://thermofeet.com/thermal-socks",
     "Thermal socks rated to -20C. Warm feet all winter long.",
     35, 6, 2, "medium", ["ES", "PT"]),
    ("109", "Basics Hub", "https://seamlessbriefs.store/briefs",
     "Seamless briefs with no lines and no seams. Underwear you forget you're wearing.",
     52, 10, 3, "medium", ["FR", "NL", "BE"]),
    # Weak: very new, few ads, small reach
    ("109", "Basics Hub", "https://www.noshowsocks.store/no-show",
     "No-show socks with silicone heel grip. They never slip off.",
     9, 2, 2, "low", ["FR"]),
    ("110", "ToeRun", "https://toerun.co/toe-socks",
     "Running toe socks. Say goodbye to blisters.",
     10, 3, 3, "low", ["NL"]),
    ("111", "GymTee Lab", "https://gymteelab.com/quick-dry",
     "Quick-dry gym t-shirt with anti-odor fabric.",
     6, 2, 2, "low", ["ES"]),
    ("112", "FunkyFeet", "https://funkyfeet.shop/gift-box",
     "Funny pattern socks gift box. The perfect present for him.",
     12, 1, 1, "low", ["AT"]),
    ("113", "SilkTouch", "https://silktouch-men.com/silk-boxers",
     "Pure mulberry silk boxers. Pure luxury.",
     4, 2, 2, "low", ["FR"]),
    # Strong, but already advertising in our markets
    ("114", "BoldBoxers", "https://www.boldboxers.com/subscription",
     "Boxers subscription: fresh underwear every 3 months, delivered free.",
     102, 24, 7, "high", ["FR", "ES", "DE", "IT", "PL"]),
    ("115", "StrideSocks", "https://stridesocks.de/sport",
     "Cushioned sports socks built for 10,000 steps a day.",
     80, 19, 5, "high", ["AT", "DE", "NL"]),
    ("116", "DryTee", "https://drytee.eu/anti-sweat",
     "Anti-sweat t-shirt with underarm pads. No more sweat stains.",
     44, 8, 3, "medium", ["NL", "PL", "CZ", "SK"]),
    ("117", "CoolBriefs", "https://coolbriefs.shop/cooling",
     "Cooling mesh briefs for hot summer days. Breathable underwear for men.",
     70, 15, 4, "high", ["FR", "ES", "IT", "HR", "SI"]),
]


def _ad_ages(oldest: int, total: int, new: int, rng: random.Random) -> list[int]:
    """Ages in days: the oldest ad, `new` ads from the last 30 days, the rest in between."""
    ages = [oldest]
    remaining_new = max(new - (1 if oldest <= 30 else 0), 0)
    ages += [rng.randint(0, min(30, oldest)) for _ in range(remaining_new)]
    while len(ages) < total:
        ages.append(rng.randint(31, oldest) if oldest > 31 else rng.randint(0, oldest))
    return ages[:total]


def _split_reach(total: int, countries: list[str], rng: random.Random) -> dict[str, int]:
    weights = [rng.random() + 0.2 for _ in countries]
    s = sum(weights)
    return {c: int(total * w / s) for c, w in zip(countries, weights)}


def generate_demo_ads(seed: int = 42, today: date | None = None) -> list[Ad]:
    rng = random.Random(seed)
    today = today or date.today()
    ads = []
    ad_counter = 900_000_000
    for page_id, page_name, url, body, oldest, total, new, reach, countries in PRODUCTS:
        for age in _ad_ages(oldest, total, new, rng):
            ad_counter += rng.randint(1, 50)
            ad_id = str(ad_counter)
            ads.append(Ad(
                ad_id=ad_id,
                page_id=page_id,
                page_name=page_name,
                start_date=today - timedelta(days=age),
                landing_url=url,
                body=body,
                snapshot_url=f"https://www.facebook.com/ads/library/?id={ad_id}",
                reach_by_country=_split_reach(rng.randint(*REACH[reach]), countries, rng),
            ))
    return ads


def load_demo_ads(keywords: list[str], countries: list[str]) -> list[Ad]:
    """Demo stand-in for the API: filter by keywords and reached countries, like the real query."""
    ads = generate_demo_ads()
    if keywords:
        kws = [k.lower() for k in keywords]
        ads = [a for a in ads
               if any(k in f"{a.page_name} {a.body} {a.landing_url}".lower() for k in kws)]
    if countries:
        ads = [a for a in ads if any(a.reach_by_country.get(c, 0) > 0 for c in countries)]
    return ads
