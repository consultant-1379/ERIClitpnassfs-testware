import sys
import time
import unittest

from naslibtest import NaslibTest

from naslib.nasexceptions import DeletionException, DoesNotExist
from naslib.objects import Snapshot


class TestTearDown(NaslibTest):
    """ TearDown script for naslib tests
    """
    def silently_delete(self, resource, *args):
        try:
            resource.delete(*args)
        except Snapshot.RollsyncRunning:
            # because sometimes a snapshot deletion fails because restore is
            # still in progress.
            time.sleep(2)
            self.silently_delete(resource, *args)
        except (DeletionException, DoesNotExist) as err:
            print err
            pass

    def test_01(self):
        new_fs_name = sys.argv[4]
        new_share_name = sys.argv[5]
        new_cache_name = sys.argv[6]
        new_snap_name = sys.argv[7]
        extra_snap_name = sys.argv[8] if len(sys.argv) > 8 else None
        host_ip = sys.argv[1]
        with self.connect_to_nfs() as s:
            self.silently_delete(s.share, new_share_name, host_ip)
            self.silently_delete(s.snapshot, new_snap_name, new_fs_name)
            if extra_snap_name:
                self.silently_delete(s.snapshot, extra_snap_name, new_fs_name)
            self.silently_delete(s.filesystem, new_fs_name)
            self.silently_delete(s.cache, new_cache_name)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTearDown)
    unittest.TextTestRunner(verbosity=2).run(suite)
