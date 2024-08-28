import sys
import unittest
from naslibtest import NaslibTest
from naslib.nasexceptions import NasException


class Test18(NaslibTest):
    """Test script for story 6854"""

    def test_18(self):
        new_cache_name = sys.argv[4]
        with self.connect_to_nfs() as s:
            self.assertRaises(NasException, s.cache.create,
                    new_cache_name, "99999T", self.pool_name)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test18)
    unittest.TextTestRunner(verbosity=2).run(suite)
