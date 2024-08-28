"""
@copyright: LM Ericsson Ltd
@since: August 2015
@authors: Rogerio Hilbert Lima
@summary: Script for Integration tests for naslib library
"""

import sys
import unittest

from naslibtest import NaslibTest


class Test02(NaslibTest):
    """ Test script for story 10832
    """

    def test_02(self):
        """ Check restore is running of non restoring fs

         1. create a file system fs
         2. check if the restore is running by executing the method
            nas.filesystem.is_restore_running(fs), should return False

        """
        new_fs_name = sys.argv[4]
        with self.connect_to_nfs() as s:
            # 1. create a file system fs
            fs_existence = s.filesystem.exists(new_fs_name)
            self.assertFalse(fs_existence,
                    '%s already exists' % new_fs_name)
            new_fs = s.filesystem.create(new_fs_name, "20M", self.pool_name)
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

            # 2. check if the restore is running by executing the method
            #    nas.filesystem.is_restore_running(fs), should return False
            self.assertFalse(s.filesystem.is_restore_running(new_fs_name))


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test02)
    unittest.TextTestRunner(verbosity=2).run(suite)
