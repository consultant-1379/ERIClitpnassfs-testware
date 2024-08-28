import sys
import unittest
from naslibtest import NaslibTest
from naslib.nasexceptions import NasException


class Test5(NaslibTest):
    """Test script for story 6854"""

    def test_05(self):
        new_fs_name = sys.argv[4]
        with self.connect_to_nfs() as s:
            self.assertRaises(NasException, s.filesystem.create,
                    new_fs_name, "99999T", self.pool_name)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test5)
    unittest.TextTestRunner(verbosity=2).run(suite)
