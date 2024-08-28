import sys
import unittest
from naslibtest import NaslibTest

from naslib.objects import Share


class Test8(NaslibTest):
    """Test script for story 6854"""

    def test_08(self):
        new_fs_name = sys.argv[4]
        new_share_name = sys.argv[5]
        host_ip = sys.argv[1]
        with self.connect_to_nfs() as s:
            s.filesystem.create(new_fs_name, "10M", self.pool_name)
            s.share.create(new_share_name, host_ip, "ro")
            self.assertRaises(Share.AlreadyExists, s.share.create,
                    new_share_name, host_ip, "ro")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test8)
    unittest.TextTestRunner(verbosity=2).run(suite)
