"""Product Finder: find products advertising heavily in Europe but not in our markets.

Usage:
    python main.py --demo
    python main.py --demo --keywords socks --countries FR ES
    python main.py --keywords "bamboo boxers" --countries FR ES NL AT   (live, needs API)
"""
import argparse
import os
import sys

from finder import config, demo_data, meta_api
from finder.grouping import group_ads
from finder.output import print_summary, write_csv
from finder.scoring import rank_products


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Find winning products from the Meta Ad Library.")
    parser.add_argument("--keywords", nargs="*", default=config.DEFAULT_KEYWORDS,
                        help="search terms (default: our categories - boxers, briefs, underwear, "
                             "socks, t-shirt, undershirt)")
    parser.add_argument("--countries", nargs="*", default=config.DEFAULT_SOURCE_COUNTRIES,
                        type=str.upper, help="source countries to search (default: FR ES NL AT)")
    parser.add_argument("--demo", action="store_true", help="use built-in sample data instead of the API")
    parser.add_argument("--out", default="results.csv", help="CSV output path (default: results.csv)")
    parser.add_argument("--top", type=int, default=10, help="rows to show in the terminal (default: 10)")
    parser.add_argument("--hide-present", action="store_true",
                        help="drop products that already have reach in our markets")
    return parser.parse_args(argv)


def load_env(path=".env"):
    """Minimal .env reader (KEY=value lines), so demo mode needs no extra packages."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main(argv=None):
    args = parse_args(argv)

    if args.demo:
        print("Running in DEMO mode with sample data.")
        ads = demo_data.load_demo_ads(args.keywords, args.countries)
    else:
        load_env()
        token = os.environ.get("META_ACCESS_TOKEN")
        if not token:
            sys.exit("Error: META_ACCESS_TOKEN is not set. Add it to .env, or run with --demo.")
        try:
            ads = meta_api.fetch_ads(args.keywords, args.countries, token)
        except NotImplementedError as e:
            sys.exit(f"Error: {e}")

    if not ads:
        sys.exit("No ads found for these keywords/countries.")

    products = rank_products(group_ads(ads))
    if args.hide_present:
        products = [p for p in products if not p.in_our_markets]

    write_csv(products, args.out)
    print_summary(products, len(ads), args.out, args.top)


if __name__ == "__main__":
    main()
