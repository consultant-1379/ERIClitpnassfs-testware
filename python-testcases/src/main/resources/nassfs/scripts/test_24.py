import sys
import unittest
from naslibtest import NaslibTest


class Test24(NaslibTest):
    """Test script for story 6854"""

    def test_24(self):
        new_fs_name = sys.argv[4]
        with self.connect_to_nfs() as s:
            fs_existence = s.filesystem.exists(new_fs_name)
            self.assertFalse(fs_existence,
                    '%s already exists' % new_fs_name)
            new_fs = s.filesystem.create(new_fs_name, "10M", self.pool_name)
            fs_existence = s.filesystem.exists(new_fs_name)
            self.assertTrue(fs_existence,
                    '%s does not exists' % new_fs_name)
            filesystems = s.filesystem.list()
            self.assertTrue(len(filesystems) > 0)
            fs_names = [f.name for f in filesystems]
            self.assertTrue(new_fs_name in fs_names,
                    '%s not in %s' % (new_fs.name, fs_names))
            fs = s.filesystem.get(new_fs_name)
            self.assertEquals(fs.name, new_fs_name)
            self.assertEquals(fs.pool.name, self.pool_name)
            new_fs.resize("20M")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test24)
    unittest.TextTestRunner(verbosity=2).run(suite)
