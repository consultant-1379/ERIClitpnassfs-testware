import unittest
from naslibtest import NaslibTest


class Test11(NaslibTest):
    """Test script for story 6854"""

    def test_11(self):
        with self.connect_to_nfs() as s:
            pools = s.pool.list()
            if len(pools) > 0:
                self.assertTrue(
                        s.pool.exists(pools[0].name))
                self.assertTrue(
                        s.pool.get(pools[0].name))
            self.assertFalse(
                    s.pool.exists("Not_a_Pool"))

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test11)
    unittest.TextTestRunner(verbosity=2).run(suite)
