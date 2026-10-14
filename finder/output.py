"""Ranked CSV export and terminal summary."""
import csv

from finder.models import Product

CSV_COLUMNS = [
    "rank", "score", "page_name", "domain", "oldest_ad_days", "new_ads_30d", "active_ads",
    "eu_reach", "ad_age_score", "new_creatives_score", "active_ads_score", "eu_reach_score",
    "reviews_score", "traffic_score", "in_our_markets", "present_in", "sample_ad_url",
]


def _fmt(value: float | None) -> str:
    return "" if value is None else f"{value:.2f}"


def write_csv(products: list[Product], path: str) -> None:
    # utf-8-sig so Excel opens it with the right encoding
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_COLUMNS)
        for rank, p in enumerate(products, 1):
            c = p.components
            newest = max(p.ads, key=lambda a: a.start_date)
            writer.writerow([
                rank, p.score, p.page_name, p.domain, p.oldest_ad_days, p.new_ads_30d,
                p.active_ads, p.eu_reach,
                _fmt(c["ad_age"]), _fmt(c["new_creatives"]), _fmt(c["active_ads"]),
                _fmt(c["eu_reach"]), _fmt(c["reviews"]), _fmt(c["traffic"]),
                "yes" if p.in_our_markets else "no", " ".join(p.present_in_markets),
                newest.snapshot_url,
            ])


def print_summary(products: list[Product], ads_count: int, csv_path: str, top: int) -> None:
    present = [p for p in products if p.in_our_markets]
    opportunities = [p for p in products if not p.in_our_markets]

    print()
    print(f"Analysed {ads_count} active ads -> {len(products)} products")
    print(f"  {len(opportunities)} not in our markets (opportunities)")
    print(f"  {len(present)} already advertising in our markets")
    print()

    header = f"{'#':>2}  {'Score':>5}  {'Page':<18} {'Domain':<24} {'Age':>4} {'New':>4} {'Ads':>4} {'EU reach':>10}  Our markets"
    print(header)
    print("-" * len(header))
    for rank, p in enumerate(products[:top], 1):
        markets = ", ".join(p.present_in_markets) if p.present_in_markets else "-"
        print(f"{rank:>2}  {p.score:>5.1f}  {p.page_name[:18]:<18} {p.domain[:24]:<24} "
              f"{p.oldest_ad_days:>4} {p.new_ads_30d:>4} {p.active_ads:>4} {p.eu_reach:>10,}  {markets}")
    if len(products) > top:
        print(f"... {len(products) - top} more in CSV")

    if opportunities:
        best = opportunities[0]
        print()
        print(f"Top opportunity: {best.page_name} ({best.domain}), score {best.score}, "
              f"running {best.oldest_ad_days} days with {best.active_ads} active ads.")
    print(f"Full ranking saved to {csv_path}")
    print()
