import sys
import unittest
from naslibtest import NaslibTest


class Test16(NaslibTest):
    """Test script for story 6854"""

    def test_16(self):
        new_cache_name = sys.argv[4]
        with self.connect_to_nfs() as s:
            new_cache = s.cache.create(new_cache_name, "10M", self.pool_name)
            cache_existence = s.cache.exists(new_cache_name)
            self.assertTrue(cache_existence,
                    '%s cache failed at creation' % new_cache_name)
            new_cache.delete()
            cache_existence = s.cache.exists(new_cache_name)
            self.assertFalse(cache_existence,
                    '%s cache failed at removal' % new_cache_name)
            caches = s.cache.list()
            cache_names = [c.name for c in caches]
            self.assertFalse(new_cache_name in cache_names,
                    '%s cache found in %s' % (new_cache.name, cache_names))


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test16)
    unittest.TextTestRunner(verbosity=2).run(suite)
