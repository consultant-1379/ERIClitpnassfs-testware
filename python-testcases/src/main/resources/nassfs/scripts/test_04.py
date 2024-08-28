import sys
import unittest
from naslibtest import NaslibTest

from naslib.objects import FileSystem


class Test4(NaslibTest):
    """Test script for story 6854"""

    def test_04(self):
        new_fs_name = sys.argv[4]
        with self.connect_to_nfs() as s:
            fs_existence = s.filesystem.exists(new_fs_name)
            self.assertFalse(fs_existence,
                    '%s should not exist' % new_fs_name)
            new_fs = s.filesystem.create(new_fs_name, "10M", self.pool_name)
            new_fs.delete()
            self.assertRaises(FileSystem.DeletionException, new_fs.delete)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test4)
    unittest.TextTestRunner(verbosity=2).run(suite)
