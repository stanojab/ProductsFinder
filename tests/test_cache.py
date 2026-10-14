import unittest

from finder import cache
from finder.demo_data import generate_demo_ads


class CacheTest(unittest.TestCase):
    def setUp(self):
        self.conn = cache.connect(":memory:")
        self.ads = generate_demo_ads()

    def tearDown(self):
        self.conn.close()

    def test_round_trip(self):
        cache.save_ads(self.conn, self.ads)
        loaded = {a.ad_id: a for a in cache.load_ads(self.conn)}
        self.assertEqual(len(loaded), len(self.ads))
        self.assertEqual(loaded[self.ads[0].ad_id], self.ads[0])

    def test_save_is_idempotent(self):
        cache.save_ads(self.conn, self.ads)
        cache.save_ads(self.conn, self.ads)
        self.assertEqual(len(cache.load_ads(self.conn)), len(self.ads))

    def test_load_by_ids(self):
        cache.save_ads(self.conn, self.ads)
        ids = [self.ads[0].ad_id, self.ads[5].ad_id, "missing"]
        self.assertEqual(len(cache.load_ads(self.conn, ids)), 2)


if __name__ == "__main__":
    unittest.main()
