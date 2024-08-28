import sys
import unittest
import re
import time
from naslibtest import NaslibTest


class Test02(NaslibTest):
    """Test script for story 2778"""

    def test_02(self):
        new_fs_name = sys.argv[4]
        new_cache_name = sys.argv[5]
        new_snap_name = sys.argv[6]
        with self.connect_to_nfs() as s:
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

            cache_existence = s.cache.exists(new_cache_name)
            self.assertFalse(cache_existence,
                    '%s should not exist' % new_cache_name)
            new_cache = s.cache.create(new_cache_name, "10M", self.pool_name)
            new_cache.resize("20M")

            _, out, err = s.ssh.run('dd if=/dev/zero of=/vx/%s/stuff1.txt '
                                    'bs=1M count=5' % new_fs_name)
            regex = re.compile('[\d+\+]+\s+records\s+in')
            self.assertTrue(bool(regex.search(out + err)))
            _, out, err = s.ssh.run('ls /vx/%s/stuff1.txt' % new_fs_name)
            self.assertNotEquals(out, "")
            self.assertEquals(err, "")

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

            _, out, err = s.ssh.run('dd if=/dev/zero of=/vx/%s/stuff2.txt '
                                    'bs=1M count=3' % new_fs_name)
            regex = re.compile('[\d+\+]+\s+records\s+in')
            self.assertTrue(bool(regex.search(out + err)))
            _, out, err = s.ssh.run('ls /vx/%s/stuff2.txt' % new_fs_name)
            self.assertNotEquals(out, "")
            self.assertEquals(err, "")

            s.snapshot.restore(new_snap_name, new_fs_name)
            _, out, err = s.ssh.run('ls /vx/%s/stuff1.txt' % new_fs_name)
            self.assertNotEquals(out, "")
            self.assertEquals(err, "")
            _, out, err = s.ssh.run('ls /vx/%s/stuff2.txt' % new_fs_name)
            self.assertEquals(out, "")
            self.assertNotEquals(err, "")

            time.sleep(30)

            s.snapshot.restore(new_snap_name, new_fs_name)
            _, out, err = s.ssh.run('ls /vx/%s/stuff1.txt' % new_fs_name)
            self.assertNotEquals(out, "")
            self.assertEquals(err, "")
            _, out, err = s.ssh.run('ls /vx/%s/stuff2.txt' % new_fs_name)
            self.assertEquals(out, "")
            self.assertNotEquals(err, "")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test02)
    unittest.TextTestRunner(verbosity=2).run(suite)
