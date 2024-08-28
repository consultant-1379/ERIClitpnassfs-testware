import sys
import unittest
import re
import time

from naslibtest import NaslibTest

from naslib.objects import Snapshot


class Test01(NaslibTest):
    """ Test script for bug 10890

        1. create a fs
        2. create a cache
        3. create a snapshot for the fs using the above cache
        4. write data in the fs until the cache becomes full
        5. try to create an extra snapshot
        6. ensure we get the Snapshot.CreationException error with a proper
           message saying that the creation failed because the cache was
           full.
    """

    def test_01(self):
        new_fs_name = sys.argv[4]
        new_cache_name = sys.argv[5]
        new_snap_name = sys.argv[6]
        extra_snap_name = sys.argv[7]
        with self.connect_to_nfs() as s:

            # 1. create a fs
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

            # 2. create a cache
            cache_existence = s.cache.exists(new_cache_name)
            self.assertFalse(cache_existence,
                    '%s should not exist' % new_cache_name)
            s.cache.create(new_cache_name, "10M", self.pool_name)

            # 3. create a snapshot for the fs using the above cache
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

            # 4. write data in the fs until the cache becomes full
            # - check before if there is space available
            cache = s.cache.get(new_cache_name)
            self.assertTrue(cache.available)
            # NOTE: initially a cache created starts with 4M used, so it's
            # available now 6M.
            # NOTE 2: the SFS "autogrow" feature increases the cache 20% every
            # time it reaches more than 90% usage.
            # NOTE 3: the intention below is to write 5M to make the usage be
            # 9M and the SFS "autogrow" feature will increase the cache 20%,
            # resulting in 12M size instead of 10M.
            _, out, err = s.ssh.run('dd if=/dev/urandom of=/vx/%s/stuff1.txt '
                                 'bs=1M count=5' % new_fs_name)
            regex = re.compile('[\d+\+]+\s+records\s+in')
            self.assertTrue(bool(regex.search(out + err)))
            _, out, err = s.ssh.run('ls /vx/%s/stuff1.txt' % new_fs_name)
            self.assertNotEquals(out, "")
            self.assertEquals(err, "")
            for i in xrange(2, 10):
                time.sleep(1)
                # this 8 iterations is the minimum necessary to write data on
                # the fs and gets the cache 100% used, because the SFS
                # "autogrow" feature increases the cache 20% every time it
                # reaches more than 90% usage.
                _, out, err = s.ssh.run('dd if=/dev/urandom of=/vx/%s/'
                                     'stuff%s.txt bs=1M count=2' %
                                     (new_fs_name, i))
                regex = re.compile('[\d+\+]+\s+records\s+in')
                self.assertTrue(bool(regex.search(out + err)))
                _, out, err = s.ssh.run('ls /vx/%s/stuff%s.txt' % (new_fs_name,
                                                                i))
                self.assertNotEquals(out, "")
                self.assertEquals(err, "")

            # now the cache must have no space available
            cache = s.cache.get(new_cache_name)
            self.assertFalse(cache.available)

            # 5. try to create an extra snapshot
            err = ""
            try:
                s.snapshot.create(extra_snap_name, new_fs_name, new_cache_name)
            except Exception as err:
                pass

            # 6. ensure we get the Snapshot.CreationException error with a
            # proper message saying that the creation failed because the cache
            # was full
            self.assertTrue(isinstance(err, Snapshot.CreationException))
            kwargs = dict(fs=new_fs_name, cache=new_cache_name,
                          snap=extra_snap_name)
            msg1 = 'Failed to create the snapshot "%(snap)s" for the file ' \
                   'system "%(fs)s" because the cache "%(cache)s" is ' \
                   'full.' % kwargs
            msg2 = 'rollback ERROR V-288-1883 fsck failed ' \
                   'for %(snap)s. Command: storage rollback create ' \
                   'space-optimized %(snap)s %(fs)s %(cache)s' % kwargs
            va_msg = 'rollback ERROR V-493-10-1120 fsck failed ' \
                     'for %(snap)s. Command: storage rollback create ' \
                     'space-optimized %(snap)s %(fs)s %(cache)s' % kwargs

            self.assertTrue(msg1 in str(err))
            self.assertTrue(msg2 in str(err) or va_msg in str(err))


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test01)
    unittest.TextTestRunner(verbosity=2).run(suite)
