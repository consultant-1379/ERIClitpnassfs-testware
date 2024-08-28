import sys
import unittest
from naslibtest import NaslibTest


class Test3(NaslibTest):
    """Test script for story 6854"""

    def test_03(self):
        new_fs_name = sys.argv[4]
        with self.connect_to_nfs() as s:
            new_fs = s.filesystem.create(new_fs_name, "10M", self.pool_name)
            fs_existence = s.filesystem.exists(new_fs_name)
            self.assertTrue(fs_existence,
                    '%s fs failed at creation' % new_fs_name)
            new_fs.delete()
            fs_existence = s.filesystem.exists(new_fs_name)
            self.assertFalse(fs_existence,
                    '%s fs failed at removal' % new_fs_name)
            filesystems = s.filesystem.list()
            fs_names = [f.name for f in filesystems]
            self.assertFalse(new_fs_name in fs_names,
                    '%s fs found in %s' % (new_fs.name, fs_names))


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test3)
    unittest.TextTestRunner(verbosity=2).run(suite)
