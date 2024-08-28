import sys
import unittest
from naslibtest import NaslibTest

from naslib.objects import Cache


class Test17(NaslibTest):
    """Test script for story 6854"""

    def test_17(self):
        new_cache_name = sys.argv[4]
        with self.connect_to_nfs() as s:
            cache_existence = s.cache.exists(new_cache_name)
            self.assertFalse(cache_existence,
                    '%s should not exist' % new_cache_name)
            new_cache = s.cache.create(new_cache_name, "10M", self.pool_name)
            new_cache.delete()
            self.assertRaises(Cache.DoesNotExist, new_cache.delete)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test17)
    unittest.TextTestRunner(verbosity=2).run(suite)
