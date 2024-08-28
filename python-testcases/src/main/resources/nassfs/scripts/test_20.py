import sys
import unittest
from naslibtest import NaslibTest


class Test20(NaslibTest):
    """Test script for story 6854"""

    def test_20(self):
        new_cache_name = sys.argv[4]
        with self.connect_to_nfs() as s:
            cache_existence = s.cache.exists(new_cache_name)
            self.assertFalse(cache_existence,
                    '%s should not exist' % new_cache_name)
            new_cache = s.cache.create(new_cache_name, "10M", self.pool_name)
            new_cache.resize("20M")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test20)
    unittest.TextTestRunner(verbosity=2).run(suite)
