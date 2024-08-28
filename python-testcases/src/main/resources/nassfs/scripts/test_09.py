import sys
import unittest
from naslibtest import NaslibTest


class Test9(NaslibTest):
    """Test script for story 6854"""

    def test_09(self):
        new_fs_name = sys.argv[4]
        new_share_name = sys.argv[5]
        host_ip = sys.argv[1]
        with self.connect_to_nfs() as s:
            s.filesystem.create(new_fs_name, "10M", self.pool_name)
            new_share = s.share.create(new_share_name, host_ip, "ro")
            new_share.delete()
            self.assertFalse(s.share.exists(new_share_name, host_ip))

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test9)
    unittest.TextTestRunner(verbosity=2).run(suite)
