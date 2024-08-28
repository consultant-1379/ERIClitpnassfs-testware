import unittest
from naslibtest import NaslibTest


class Test12(NaslibTest):
    """Test script for story 6854"""

    def test_12(self):
        with self.connect_to_nfs() as s:
            disks = s.disk.list()
            if len(disks) > 0:
                self.assertTrue(
                        s.disk.exists(disks[0].name))
                self.assertTrue(
                        s.disk.get(disks[0].name))
            self.assertFalse(
                    s.disk.exists("Not_a_Disk"))

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test12)
    unittest.TextTestRunner(verbosity=2).run(suite)
