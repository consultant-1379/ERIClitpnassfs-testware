import sys
import unittest
from naslibtest import NaslibTest

from naslib.objects import Cache


class Test15(NaslibTest):
    """Test script for story 6854"""

    def test_15(self):
        new_cache_name = sys.argv[4]
        with self.connect_to_nfs() as s:
            s.cache.create(new_cache_name, "10M", self.pool_name)
            self.assertRaises(Cache.AlreadyExists, s.cache.create,
                    new_cache_name, "10M", self.pool_name)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test15)
    unittest.TextTestRunner(verbosity=2).run(suite)
