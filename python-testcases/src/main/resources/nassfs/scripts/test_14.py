import sys
import unittest
from naslibtest import NaslibTest


class Test14(NaslibTest):
    """Test script for story 6854"""

    def test_14(self):
        new_cache_name = sys.argv[4]
        with self.connect_to_nfs() as s:
            cache_existence = s.cache.exists(new_cache_name)
            self.assertFalse(cache_existence,
                    '%s already exists' % new_cache_name)
            new_cache = s.cache.create(new_cache_name, "10M", self.pool_name)
            cache_existence = s.cache.exists(new_cache_name)
            self.assertTrue(cache_existence,
                    '%s does not exist' % new_cache_name)
            caches = s.cache.list()
            self.assertTrue(len(caches) > 0)
            cache_names = [f.name for f in caches]
            self.assertTrue(new_cache_name in cache_names,
                    '%s not in %s' % (new_cache.name, cache_names))
            cache = s.cache.get(new_cache_name)
            self.assertEquals(cache.name, new_cache_name)
            self.assertEquals(cache.pool.name, self.pool_name)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test14)
    unittest.TextTestRunner(verbosity=2).run(suite)
