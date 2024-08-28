"""
@copyright: LM Ericsson Ltd
@since: August 2015
@authors: Rogerio Hilbert Lima
@summary: Integration tests for naslib library
"""

import os

from litp_generic_test import GenericTest, attr


class NasSfs(GenericTest):
    """
    LITPCDS-10832
    As an ERIClitpnassfs user I want ERIClitpnassfs to implement polling of
    filesystems so that I know if rollback sync is being performed on a SFS
    filesystem
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
                     self.test_snapshot_name])
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
        stdout, stderr, exit_code = self.run_command(
            self.management_server, script_cmd, connection_timeout_secs=2500)
        return stdout, stderr, exit_code

    def _test_script(self, script_name, file_system=False, share=False,
                     cache=False, snapshot=False):
        """Runs a python test file on the MS
        Args:
            script_name. (str) The script's name
            fs. (bool) A flag indicating if the script must
            create a file system
            share. (bool) A flag indicating if the script must create a share

        Returns:
            stdout. (list) A list of the standart output
            stderr. (list) A list of the standart error output
            exit_code. (int) A integer represeting the exit code

        """
        script_path = self.script_remote_location(script_name)
        params = [self.nas_server_ip, self.nas_server_user, self.nas_server_pw]
        if file_system:
            params += [self.test_fs_name]
        if share:
            params += [self.test_share_name]
        if cache:
            params += [self.test_cache_name]
        if snapshot:
            params += [self.test_snapshot_name]
        stdout, stderr, exit_code = self.run_script(script_path, params)
        self.assertTrue(self.is_text_in_list("OK", stderr),
                        "\n".join(stderr))
        return stdout, stderr, exit_code

    @attr('all', 'revert', 'story10832', 'story10832_tc01')
    def test_01_p_check_is_restore_running(self):
        """
        @tms_id: litpcds_10832_tc01
        @tms_requirements_id: LITPCDS-10832
        @tms_title: Check if restore is running
        @tms_description: Verify a restore is running when restoring a
        filesystem
        @tms_test_steps:
        @step:Create a file-system
        @result: file-system is created
        @step:Create cache for snapshot
        @result: Cache is created
        @step:Create a snapshot of the file-system
        @result: snapshot is created
        @step:Write to the file-system
        @result: Writing to the file system is successful
        @step:Restore the file-system
        @result: Filesystem is restoring
        @tms_test_precondition: NA
        @tms_execution_type: Automated

        """
        test_script = "10832_test_01.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True,
                          cache=True, snapshot=True)

    @attr('all', 'revert', 'story10832', 'story10832_tc02')
    def test_02_n_check_restore_of_a_non_restoring_fs(self):
        """
        @tms_id: litpcds_10832_tc02
        @tms_requirements_id: LITPCDS-10832
        @tms_title: Check if restore is not running on a non restored
        filesystem
        @tms_description: Verify a restore is not running when restoring a
        non restored filesystem
        @tms_test_steps:
        @step:Create a file-system
        @result: file-system is created
        @step:Check file restore is running
        @result: file restore is not running
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "10832_test_02.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True)

    @attr('all', 'revert', 'story10832', 'story10832_tc03')
    def test_03_n_restore_fs_while_rollsync_is_running(self):
        """
        @tms_id: litpcds_10832_tc03
        @tms_requirements_id: LITPCDS-10832
        @tms_title: Restore a filesystem while restore is running
        @tms_description: Verify restoring a filesystem while restore is
        running will result in an exception
        @tms_test_steps:
        @step:Create a file-system
        @result: file-system is created
        @step:Create cache for snapshot
        @result: Cache is created
        @step:Create a snapshot of the file-system
        @result: snapshot is created
        @step:Write to the file-system
        @result: Writing to the file system is successful
        @step:Restore the file-system
        @result: Filesystem is restoring
        @step:Restore the file-system while previous restore is runing
        @result: Exception raised: Snapshot.RollsyncRunning
        @tms_test_precondition: NA
        @tms_execution_type: Automated

        """
        test_script = "10832_test_03.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True,
                          cache=True, snapshot=True)
