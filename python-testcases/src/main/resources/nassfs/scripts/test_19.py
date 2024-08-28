import sys
import unittest
from naslibtest import NaslibTest

from naslib.objects import Pool


class Test19(NaslibTest):
    """Test script for story 6854"""

    def test_20(self):
        new_cache_name = sys.argv[4]
        with self.connect_to_nfs() as s:
            self.assertRaises(Pool.DoesNotExist, s.cache.create,
                    new_cache_name, "10M", "Not_A_pool")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test19)
    unittest.TextTestRunner(verbosity=2).run(suite)
