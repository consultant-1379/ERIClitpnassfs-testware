"""
@copyright: LM Ericsson Ltd
@since: July 2015
@authors: Tomas Glynn
@summary: Integration tests for naslib library

"""
from litp_generic_test import GenericTest, attr
import os


class NasSfs(GenericTest):
    """
    LITPCDS-2778
    As a LITP User I want to restore to a SFS snapshot that I have already
    taken, so that my system is in a known good state.
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
        stdout, stderr, exit_code = self.run_command(self.management_server,
                script_cmd)
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

    @attr('all', 'revert', 'story2778', 'story2778_tc01')
    def test_01_p_restore_a_filesystem(self):
        """
        @tms_id: litpcds_2778_tc01
        @tms_requirements_id: LITPCDS-2778
        @tms_title: Restoring a filesystem
        @tms_description: Verify a file system can be restored
        @tms_test_steps:
        @step:Create a file-system
        @result: file-system is created
        @step:Write to a file
        @result: writing to a file is successful
        @step:Create a snapshot of the file-system
        @result: snapshot is created
        @step:Restore the file-system
        @result: file-system is restored
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "2778_test_01.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True,
                          cache=True, snapshot=True)

    @attr('all', 'revert', 'story2778', 'story2778_tc02')
    def test_02_p_restore_a_filesystem_twice(self):
        """Check the restore of a file system
        Inside the script:
            create a fs
            write to a file
            create a snapshot for the fs
            write to a new file
            restore the fs
            ensure the second file is removed
            wait 30 seconds
            restore the fs again
        Outside the script:
        - Call the script

        @tms_id: litpcds_2778_tc02
        @tms_requirements_id: LITPCDS-2778
        @tms_title: Restoring a filesystem twice
        @tms_description: Verify a file system can be restored twice
        @tms_test_steps:
        @step:Create a file-system
        @result: file-system is created
        @step:Write to a file
        @result: writing to a file is successful
        @step:Create a snapshot of the file-system
        @result: snapshot is created
        @step:Write to a second file
        @result: writing to a second file is successful
        @step:Restore the file-system
        @result: file-system is restored
        @result: second file does not exist
        @step:Restore the file-system again
        @result: file-system is restored
        @tms_test_precondition: NA
        @tms_execution_type: Automated

        """
        test_script = "2778_test_02.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True,
                          cache=True, snapshot=True)

    @attr('all', 'revert', 'story2778', 'story2778_tc03')
    def test_03_p_restore_a_filesystem_thats_offline(self):
        """
        @tms_id: litpcds_2778_tc03
        @tms_requirements_id: LITPCDS-2778
        @tms_title: Restoring a filesystem thats offline
        @tms_description: Verify a file system can be restored when its offline
        @tms_test_steps:
        @step:Create a file-system
        @result: file-system is created
        @step:Write to a file
        @result: writing to a file is successful
        @step:Create a snapshot of the file-system
        @result: snapshot is created
        @step:Offline the file-system
        @result: file-system is offline
        @step:Restore the file-system
        @result: file-system is restored
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "2778_test_03.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True,
                          cache=True, snapshot=True)

    @attr('all', 'revert', 'story2778', 'story2778_tc04')
    def test_04_n_restore_a_shared_filesystem(self):
        """
        @tms_id: litpcds_2778_tc04
        @tms_requirements_id: LITPCDS-2778
        @tms_title: Restoring a shared filesystem results in a n error
        @tms_description: Verify a file system cannot be restored when its
        shared
        @tms_test_steps:
        @step:Create a file-system
        @result: file-system is created
        @step: create a share for the fs
        @result: share for the fs created
        @step:Create a snapshot of the file-system
        @result: snapshot is created
        @step:Restore the file-system
        @result: Exception thrown: RestoreException
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "2778_test_04.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True, share=True,
                          cache=True, snapshot=True)

    @attr('all', 'revert', 'story2778', 'story2778_tc05')
    def test_05_n_restore_a_filesystem_with_invalid_snap(self):
        """
        @tms_id: litpcds_2778_tc05
        @tms_requirements_id: LITPCDS-2778
        @tms_title: Restoring a filesystem with invalid snapshot
        @tms_description: Verify restoring a filesystem with invalid snapshot
        results in a DoesNotExist error
        @tms_test_steps:
        @step:Create a file-system
        @result: file-system is created
        @step:Create a snapshot of the file-system
        @result: snapshot is created
        @step:Restore the file-system
        @result: Error thrown: Snapshot.DoesNotExist error
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "2778_test_05.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True,
                          cache=True, snapshot=True)

    @attr('all', 'revert', 'story2778', 'story2778_tc06')
    def test_06_n_restore_a_filesystem_with_invalid_fs(self):
        """
        @tms_id: litpcds_2778_tc06
        @tms_requirements_id: LITPCDS-2778
        @tms_title: Restoring a filesystem with invalid filesystem
        @tms_description: Verify restoring a filesystem with invalid filesystem
        results in a DoesNotExist error
        @tms_test_steps:
        @step:Create a file-system
        @result: file-system is created
        @step:Create a snapshot of the file-system
        @result: snapshot is created
        @step:Restore the file-system with an invalid file-system
        @result: Error thrown: FileSystem.DoesNotExist error
        @tms_test_precondition: NA
        @tms_execution_type: Automated

        """
        test_script = "2778_test_06.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True,
                          cache=True, snapshot=True)
