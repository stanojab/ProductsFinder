import unittest
from datetime import date

from finder.grouping import group_ads, normalize_domain
from finder.models import Ad


def make_ad(ad_id, page_id, url):
    return Ad(ad_id=ad_id, page_id=page_id, page_name=f"Page {page_id}",
              start_date=date(2026, 1, 1), landing_url=url)


class NormalizeDomainTest(unittest.TestCase):
    def test_strips_scheme_www_and_path(self):
        self.assertEqual(normalize_domain("https://WWW.Shop.com/p/1?x=2"), "shop.com")

    def test_bare_domain(self):
        self.assertEqual(normalize_domain("SHOP.COM"), "shop.com")

    def test_keeps_subdomain(self):
        self.assertEqual(normalize_domain("https://eu.shop.com"), "eu.shop.com")


class GroupAdsTest(unittest.TestCase):
    def test_same_page_same_domain_is_one_product(self):
        ads = [make_ad("1", "A", "https://www.x.com/a"), make_ad("2", "A", "https://x.com/b")]
        products = group_ads(ads)
        self.assertEqual(len(products), 1)
        self.assertEqual(len(products[0].ads), 2)

    def test_same_page_two_domains_is_two_products(self):
        ads = [make_ad("1", "A", "https://x.com"), make_ad("2", "A", "https://y.com")]
        self.assertEqual({p.domain for p in group_ads(ads)}, {"x.com", "y.com"})

    def test_two_pages_same_domain_is_two_products(self):
        ads = [make_ad("1", "A", "https://x.com"), make_ad("2", "B", "https://x.com")]
        self.assertEqual(len(group_ads(ads)), 2)


if __name__ == "__main__":
    unittest.main()
