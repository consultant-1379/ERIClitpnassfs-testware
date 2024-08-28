import sys
import unittest
from naslibtest import NaslibTest

from naslib.objects import Pool


class Test6(NaslibTest):
    """Test script for story 6854"""

    def test_06(self):
        new_fs_name = sys.argv[4]
        with self.connect_to_nfs() as s:
            self.assertRaises(Pool.DoesNotExist, s.filesystem.create,
                    new_fs_name, "50M", "Not_A_pool")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test6)
    unittest.TextTestRunner(verbosity=2).run(suite)
