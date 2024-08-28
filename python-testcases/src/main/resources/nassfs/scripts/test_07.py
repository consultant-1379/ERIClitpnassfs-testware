import sys
import unittest
from naslibtest import NaslibTest


class Test7(NaslibTest):
    """Test script for story 6854"""

    def test_07(self):
        new_fs_name = sys.argv[4]
        new_share_name = sys.argv[5]
        client_ip = sys.argv[1]
        with self.connect_to_nfs() as s:
            s.filesystem.create(new_fs_name, "10M", self.pool_name)
            self.assertFalse(s.share.exists(new_share_name, client_ip),
                    '%s already exists' % new_share_name)
            new_share = s.share.create(new_share_name, client_ip, "ro")
            self.assertTrue(s.share.exists(new_share_name, client_ip),
                    '%s does not exists')
            shares = s.share.list()
            self.assertTrue(len(shares) > 0)
            s_names = [sh.name for sh in shares]
            self.assertTrue(new_share_name in s_names,
                '%s not in %s' % (new_share_name, s_names))
            self.assertEquals(new_share.name, new_share_name)
            self.assertEquals(new_share.client, client_ip)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test7)
    unittest.TextTestRunner(verbosity=2).run(suite)
