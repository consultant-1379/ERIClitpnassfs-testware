import sys
import unittest
from naslibtest import NaslibTest

from naslib.objects import Share


class Test10(NaslibTest):
    """Test script for story 6854"""

    def test_10(self):
        new_fs_name = sys.argv[4]
        new_share_name = sys.argv[5]
        host_ip = sys.argv[1]
        with self.connect_to_nfs() as s:
            s.filesystem.create(new_fs_name, "10M", self.pool_name)
            self.assertFalse(s.share.exists(new_share_name, host_ip),
                    "share %s at %s should not exist" % (new_share_name,
                        host_ip))
            new_share = s.share.create(new_share_name, host_ip, "ro")
            new_share.delete()
            self.assertRaises(Share.DeletionException, new_share.delete)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test10)
    unittest.TextTestRunner(verbosity=2).run(suite)
