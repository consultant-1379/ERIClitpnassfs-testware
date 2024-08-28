import sys
import unittest
from naslibtest import NaslibTest

from naslib.objects import FileSystem


class Test04(NaslibTest):
    """Test script for story 2778"""

    def test_04(self):
        new_fs_name = sys.argv[4]
        new_cache_name = sys.argv[6]
        new_snap_name = sys.argv[7]
        new_share_name = sys.argv[5]
        client_ip = sys.argv[1]
        with self.connect_to_nfs() as s:
            s.filesystem.create(new_fs_name, "10M", self.pool_name)
            self.assertFalse(s.share.exists(new_share_name, client_ip),
                    "share %s at %s should not exist" % (new_share_name,
                        client_ip))
            s.share.create(new_share_name, client_ip, "ro")

            cache_existence = s.cache.exists(new_cache_name)
            self.assertFalse(cache_existence,
                    '%s should not exist' % new_cache_name)
            s.cache.create(new_cache_name, "10M", self.pool_name)

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

            self.assertRaises(FileSystem.OfflineException, s.snapshot.restore,
                              new_snap_name, new_fs_name)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test04)
    unittest.TextTestRunner(verbosity=2).run(suite)
