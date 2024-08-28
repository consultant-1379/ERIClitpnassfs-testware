"""
@copyright: LM Ericsson Ltd
@since: August 2015
@authors: Rogerio Hilbert Lima
@summary: Script for Integration tests for naslib library
"""

import re
import sys
import time
import unittest

from naslibtest import NaslibTest

from naslib.objects import Snapshot


class Test03(NaslibTest):
    """ Test script for story 10832
    """
    dd_regex = re.compile('[\d+\+]+\s+records\s+in')

    def test_03(self):
        """ Restore a file system while rollsync is running

         1. create a file system fs big enough to have rollsync action take a
            reasonable time to run
         2. create a cache for the snapshot
         3. create a snapshot for the fs
         4. write considerable amount of data in the file system fs
         5. restore the fs
         6. immediately after the previous restore, restore again expecting the
            exception *Snapshot.RollsyncRunning* to be raised
        """
        new_fs_name = sys.argv[4]
        new_cache_name = sys.argv[5]
        new_snap_name = sys.argv[6]
        with self.connect_to_nfs() as s:
            # 1. create a file system fs big enough to have rollsync action
            # take a reasonable time to run
            fs_existence = s.filesystem.exists(new_fs_name)
            self.assertFalse(fs_existence,
                             '%s already exists' % new_fs_name)
            new_fs = s.filesystem.create(new_fs_name, "30G", self.pool_name)
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

            # 2. create a cache for the snapshot
            cache_existence = s.cache.exists(new_cache_name)
            self.assertFalse(cache_existence,
                             '%s should not exist' % new_cache_name)
            s.cache.create(new_cache_name, "15G", self.pool_name)

            # write considerable amount of data in the file system fs
            s.ssh.run('dd if=/dev/urandom of=/vx/%s/stuff.txt '
                      'bs=1M count=100' % new_fs_name)
            for i in xrange(149):
                s.ssh.run('cp /vx/%s/stuff.txt /vx/%s/stuff_%s.txt' %
                          (new_fs_name, new_fs_name, i))
            s.ssh.run('/bin/sync')

            # 3. create a snapshot for the fs
            snap_existence = s.snapshot.exists(new_snap_name)
            self.assertFalse(snap_existence,
                             '%s already exists' % new_snap_name)
            new_snap = s.snapshot.create(new_snap_name, new_fs_name,
                                         new_cache_name)
            snap_existence = s.snapshot.exists(new_snap_name)
            self.assertTrue(snap_existence,
                            '%s does not exists' % new_snap_name)
            snapshots = s.snapshot.list()
            self.assertTrue(len(snapshots) > 0)
            snap_names = [sn.name for sn in snapshots]
            self.assertTrue(new_snap_name in snap_names,
                            '%s not in %s' % (new_snap.name, snap_names))
            snap = s.snapshot.get(new_snap_name)
            self.assertEquals(snap.name, new_snap_name)

            # 4. write considerable amount of data in the file system fs
            s.ssh.run('dd if=/dev/urandom of=/vx/%s/stuff.txt '
                      'bs=1M count=100' % new_fs_name)
            for i in xrange(149):
                s.ssh.run('cp /vx/%s/stuff.txt /vx/%s/stuff_%s.txt' %
                          (new_fs_name, new_fs_name, i))
            s.ssh.run('/bin/sync')

            # 5. restore the fs
            s.snapshot.restore(new_snap_name, new_fs_name)

            # 6. immediately after the previous restore, restore again
            # expecting the exception Snapshot.RollsyncRunning to be raised
            self.assertRaises(Snapshot.RollsyncRunning, s.snapshot.restore,
                              new_snap_name, new_fs_name)

            # wait until the rollsync finishes before tear down
            while s.filesystem.is_restore_running(new_fs_name):
                time.sleep(2)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test03)
    unittest.TextTestRunner(verbosity=2).run(suite)
