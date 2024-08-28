import sys
import unittest
from naslibtest import NaslibTest

from naslib.objects import FileSystem


class Test2(NaslibTest):
    """Test script for story 6854"""

    def test_02(self):
        new_fs_name = sys.argv[4]
        with self.connect_to_nfs() as s:
            s.filesystem.create(new_fs_name, "10M", self.pool_name)
            self.assertRaises(FileSystem.AlreadyExists, s.filesystem.create,
                    new_fs_name, "10M", self.pool_name)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test2)
    unittest.TextTestRunner(verbosity=2).run(suite)
