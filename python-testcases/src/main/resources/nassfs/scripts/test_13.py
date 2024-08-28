import unittest
from naslibtest import NaslibTest

from naslib.drivers.sfs.utils import VxCommands


class Test13(NaslibTest):
    """Test script for story 6854"""

    def test_13(self):
        with self.connect_to_nfs() as s:
            vxc = VxCommands(s)
            disks = s.disk.list()
            vx_disk_list = vxc.execute("vxdisk list | awk 'NR > 1 {print $1}'")
            vx_disk_list = vx_disk_list.split()

            if len(disks) > 0:
                disk = None
                # Fix for TORF-322689
                for s_disk in disks:
                    if s_disk.name in vx_disk_list:
                        disk = s_disk
                        break
                self.assertFalse(disk is None, "No disk in system disk list "
                                               "({0}) exists in the VA disk "
                                               "list ({1})"
                                               "".format(disks, vx_disk_list))
            filesystems = s.filesystem.list()
            if len(filesystems) > 0:
                fs = filesystems[0]
                fs_d = vxc.vxprint(fs.name)
                self.assertTrue(fs_d)
                fss = vxc.vxprint()
                self.assertTrue(fs.name in fss)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test13)
    unittest.TextTestRunner(verbosity=2).run(suite)
