"""
@copyright: LM Ericsson Ltd
@since: July 2015
@authors: Rogerio Hilbert Lima
@summary: Integration tests for naslib library

"""

import os

from litp_generic_test import GenericTest, attr


class NasSfs(GenericTest):
    """
    Bug LITPCDS-10890
    Create SFS snapshot fails when cache is at 100%
    """

    def setUp(self):
        """
        Description:
            Runs before every test
        Actions:
            Determine
                management server,
                list of all managed nodes
                location of script src dir
        Results:
            Class variables that are required to execute tests
        """
        super(NasSfs, self).setUp()
        self.management_server = self.get_management_node_filename()
        self.nas_server = self.get_sfs_node_filenames()[0]
        self.nas_server_ip = self.get_node_att(self.nas_server, "ipv4")
        self.nas_server_user = self.get_node_att(self.nas_server, "username")
        self.nas_server_pw = self.get_node_att(self.nas_server, "password")
        self.list_managed_nodes = self.get_managed_node_filenames()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.script_src_dir = os.path.join(current_dir, "scripts")
        self.remote_path = "/tmp"
        self.test_fs_name = "some_fs"
        self.test_share_name = "/vx/some_fs"
        self.test_cache_name = "some_cache"
        self.test_snapshot_name = "some_snap"
        self.test_extra_snapshot_name = "extra_snap"

        self.python_path = "/usr/bin/python"
        self.copy_script_to_ms("test_teardown.py")
        self.copy_script_to_ms("naslibtest.py")

    def tearDown(self):
        """
        Description:
            Runs after every single test
        Actions:
            -
        Results:
            The super class prints out diagnostics and variables
        """
        script_path = self.script_remote_location("test_teardown.py")
        _, stderr, _ = self.run_script(script_path,
                    [self.nas_server_ip, self.nas_server_user,
                     self.nas_server_pw, self.test_fs_name,
                     self.test_share_name, self.test_cache_name,
                     self.test_snapshot_name, self.test_extra_snapshot_name])
        self.assertTrue(self.is_text_in_list("OK", stderr),
                "\n".join(stderr))
        super(NasSfs, self).tearDown()

    def script_remote_location(self, script_name):
        """Give the remote location for for a script, given it's name.
        Args:
            script_name. (str) The script file name
        Returns:
            str. The script remote location
        """
        return os.path.join(self.remote_path, script_name)

    def script_local_location(self, script_name):
        """Give the local location for for a script, given it's name.
        Args:
            script_name. (str) The script file name
        Returns:
            str. The script local location
        """
        return os.path.join(self.script_src_dir, script_name)

    def copy_script_to_ms(self, script):
        """Copy a script to a MS
        Args:
            scripts. (str) A script file name

        Returns:
            bool. True if successful.
        """
        script_path = self.script_local_location(script)
        copy_success = self.copy_file_to(self.management_server, script_path,
                self.remote_path)
        return copy_success

    def run_script(self, script_path, args=None):
        """Runs a python script.
        Args:
           script_path. (str) A string representing a script path on
           the Ms file
           system
           args. (list) A list of args to be passed to the string

        Returns:
            stdout. (list) A list of the standart output
            stderr. (list) A list of the standart error output
            exit_code. (int) A integer represeting the exit code
        """
        args = args or []
        args = ' '.join(args)
        script_cmd = "%s %s %s" % (self.python_path, script_path, args)
        stdout, stderr, exit_code = self.run_command(self.management_server,
                script_cmd)
        return stdout, stderr, exit_code

    def _test_script(self, script_name):
        """Runs a python test file on the MS
        Args:
            script_name. (str) The script's name
        Returns:
            stdout. (list) A list of the standard output
            stderr. (list) A list of the standard error output
            exit_code. (int) A integer representing the exit code
        """
        script_path = self.script_remote_location(script_name)
        params = [
            self.nas_server_ip,
            self.nas_server_user,
            self.nas_server_pw,
            self.test_fs_name,
            self.test_cache_name,
            self.test_snapshot_name,
            self.test_extra_snapshot_name
        ]
        stdout, stderr, exit_code = self.run_script(script_path, params)
        self.assertTrue(self.is_text_in_list("OK", stderr), "\n".join(stderr))
        return stdout, stderr, exit_code

    @attr('all', 'revert', 'bug10890', 'bug10890_tc01')
    def test_01_n_create_snapshot_when_cache_is_full(self):
        """
        @tms_id: litpcds_10890_tc01
        @tms_requirements_id: LITPCDS-10832
        @tms_title: Create snapshot when cache is full
        @tms_description: Verify creating a snapshot when cache is full
        will result in an exception
        @tms_test_steps:
        @step:Create a file-system
        @result: file-system is created
        @step:Create cache for snapshot
        @result: Cache is created
        @step:Create a snapshot of the file-system
        @result: snapshot is created
        @step:Write to the file-system
        @result: Writing to the file system is successful
        @step:Create a snapshot of the file-system
        @result: Exception raised: Snapshot.CreationException
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "bug_10890_test_01.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script)
