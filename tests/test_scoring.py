import unittest
from datetime import date, timedelta

from finder.models import Ad, Product
from finder.scoring import (
    rank_products, score_ad_age, score_eu_reach, score_new_creatives,
    score_product, weighted_total,
)

TODAY = date(2026, 10, 14)


def make_product(ages, reach_by_country=None):
    reach_by_country = reach_by_country or {"FR": 10_000}
    ads = [Ad(ad_id=str(i), page_id="P", page_name="Page", landing_url="https://x.com",
              start_date=TODAY - timedelta(days=age), reach_by_country=dict(reach_by_country))
           for i, age in enumerate(ages)]
    return Product(page_id="P", page_name="Page", domain="x.com", ads=ads)


class ComponentTest(unittest.TestCase):
    def test_ad_age_curve(self):
        self.assertEqual(score_ad_age(0), 0.0)
        self.assertEqual(score_ad_age(7), 0.0)
        self.assertAlmostEqual(score_ad_age(30), 0.5)
        self.assertAlmostEqual(score_ad_age(60), 0.8)
        self.assertAlmostEqual(score_ad_age(90), 1.0)
        self.assertAlmostEqual(score_ad_age(365), 1.0)
        self.assertTrue(score_ad_age(30) < score_ad_age(45) < score_ad_age(60))

    def test_new_creatives_caps_at_one(self):
        self.assertEqual(score_new_creatives(0), 0.0)
        self.assertEqual(score_new_creatives(50), 1.0)

    def test_eu_reach_log_scale(self):
        self.assertEqual(score_eu_reach(0), 0.0)
        self.assertEqual(score_eu_reach(500), 0.0)
        self.assertAlmostEqual(score_eu_reach(31_623), 0.5, places=2)
        self.assertEqual(score_eu_reach(5_000_000), 1.0)


class TotalTest(unittest.TestCase):
    def test_placeholders_are_rescaled_out(self):
        perfect = {"ad_age": 1, "new_creatives": 1, "active_ads": 1, "eu_reach": 1,
                   "reviews": None, "traffic": None}
        self.assertEqual(weighted_total(perfect), 100.0)

    def test_all_zero(self):
        self.assertEqual(weighted_total({"ad_age": 0, "reviews": None}), 0.0)


class ProductTest(unittest.TestCase):
    def test_metrics(self):
        p = score_product(make_product([100, 40, 10, 5]), TODAY)
        self.assertEqual(p.oldest_ad_days, 100)
        self.assertEqual(p.new_ads_30d, 2)
        self.assertEqual(p.active_ads, 4)
        self.assertEqual(p.eu_reach, 40_000)

    def test_market_flag(self):
        clean = score_product(make_product([60], {"FR": 1000, "ES": 500}), TODAY)
        present = score_product(make_product([60], {"FR": 1000, "DE": 10, "PL": 0}), TODAY)
        self.assertEqual(clean.present_in_markets, [])
        self.assertFalse(clean.in_our_markets)
        self.assertEqual(present.present_in_markets, ["DE"])  # PL has 0 reach
        self.assertTrue(present.in_our_markets)

    def test_ranking_order(self):
        strong = make_product([95] + [5] * 15, {"FR": 80_000})
        weak = make_product([3], {"FR": 500})
        ranked = rank_products([weak, strong], TODAY)
        self.assertIs(ranked[0], strong)
        self.assertGreater(strong.score, 90)
        self.assertLess(weak.score, 10)


if __name__ == "__main__":
    unittest.main()
