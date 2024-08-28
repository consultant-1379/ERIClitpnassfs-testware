"""
@copyright: LM Ericsson Ltd
@since: November 2014
@authors: Lucas Nemeth, Tomas Glynn
@sumary: Integration tests for naslib library

"""
from litp_generic_test import GenericTest, attr
import test_constants
import os


class NasSfs(GenericTest):
    """
    LITPCDS-6854
    As a LITP Architect, I want to have separate PSL library for SFS, so I can
    split specific SFS implementation from LITP plugin.
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

    @attr('all', 'revert', 'story6854', 'story6854_tc01')
    def test_01_p_create_fs(self):
        """
        @tms_id: litpcds_6854_tc01
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Create a filesystem
        @tms_description: Verify creating a file-system
        @tms_test_steps:
        @step:Create a file-system
        @result: file-system is created
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_01.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True)
        self.assertTrue(
            self.set_node_connection_data(
                self.nas_server, username=test_constants.SFS_MASTER_USR,
                password=test_constants.SFS_MASTER_PW))
        self.assertTrue(self.is_sfs_filesystem_present(
            self.nas_server, self.test_fs_name))

    @attr('all', 'revert', 'story6854', 'story6854_tc02')
    def test_02_n_duplicate_fs_creation(self):
        """
        @tms_id: litpcds_6854_tc02
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Creating a duplicate filesystem
        @tms_description: verify creating a duplicate filesystem results
        in an error
        @tms_test_steps:
        @step:Create a file-system
        @result: file-system is created
        @step:Create the same file-system again
        @result: Error is thrown: FileSystem.AlreadyExists
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_02.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True)

    @attr('all', 'revert', 'story6854', 'story6854_tc03')
    def test_03_p_delete_fs(self):
        """
        @tms_id: litpcds_6854_tc03
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Deleting filesystem
        @tms_description: Verify deleting a filesystem is successful
        @tms_test_steps:
        @step:Create a file-system
        @result: file-system is created
        @step:Remove a file-system
        @result: file-system is removed
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_03.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True)
        self.assertTrue(
            self.set_node_connection_data(
                self.nas_server, username=test_constants.SFS_MASTER_USR,
                password=test_constants.SFS_MASTER_PW))
        self.assertFalse(self.is_sfs_filesystem_present(
            self.nas_server, self.test_fs_name))

    @attr('all', 'revert', 'story6854', 'story6854_tc04')
    def test_04_n_delete_nonexistent_fs(self):
        """
        @tms_id: litpcds_6854_tc04
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Deleting a non existing filesystem
        @tms_description: Verify deleting a non existing filesystem results
        in an exception
        @tms_test_steps:
        @step:Remove a non existing file-system
        @result: Exception raised: FileSystem.DeletionException
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_04.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True)

    @attr('all', 'revert', 'story6854', 'story6854_tc05')
    def test_05_n_fs_size_too_large(self):
        """
        @tms_id: litpcds_6854_tc05
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Create an over-sized filesystem
        @tms_description: Verify creating a filesystem where its size exceeds
        that of available space results in an exception
        @tms_test_steps:
        @step: Create file-system where it's size exceeds that of available
               space
        @result: Exception raised: NasException
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_05.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True)

    @attr('all', 'revert', 'story6854', 'story6854_tc06')
    def test_06_n_fs_with_invalid_pool(self):
        """
        @tms_id: litpcds_6854_tc06
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Create an invalid pool name
        @tms_description: Verify creating an invalid pool name results in an
        exception
        @tms_test_steps:
        @step: Create an invalid pool name
        @result: Exception raised: Pool.DoesNotExist
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_06.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True)

    @attr('all', 'revert', 'story6854', 'story6854_tc07')
    def test_07_p_create_share(self):
        """
        @tms_id: litpcds_6854_tc07
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Create a share
        @tms_description: Verify creating a share is successful
        @tms_test_steps:
        @step:Create a share
        @result: Share is created
        @step:Remove a file-system
        @result: file-system is removed
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_07.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True, share=True)
        self.assertTrue(
            self.set_node_connection_data(
                self.nas_server, username=test_constants.SFS_MASTER_USR,
                password=test_constants.SFS_MASTER_PW))
        self.assertTrue(self.is_sfs_share_present(
            self.nas_server, self.test_share_name))

    def obsolete_08_n_duplicate_share_creation(self):
        """Check if duplicate share creation raises the expected exception
        Inside the script:
         - Create a share
         - Try to create the same share
         - check exception
         **** This test has been made obsolete as this functionality has
         been moved from the psl to the nas plugin. The test
         test_33_n_create_duplicate_export in testset_story8524.py
         covers this code.****


        """
        test_script = "test_08.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True, share=True)

    @attr('all', 'revert', 'story6854', 'story6854_tc09')
    def test_09_p_delete_share(self):
        """
        @tms_id: litpcds_6854_tc09
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Delete a share
        @tms_description: Verify deleting a share is successful
        @tms_test_steps:
        @step:Create a share
        @result: Share is created
        @step:Delete a share
        @result: Share is deleted
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_09.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True, share=True)
        self.assertTrue(
            self.set_node_connection_data(
                self.nas_server, username=test_constants.SFS_MASTER_USR,
                password=test_constants.SFS_MASTER_PW))
        self.assertFalse(self.is_sfs_share_present(
            self.nas_server, self.test_share_name))

    @attr('all', 'revert', 'story6854', 'story6854_tc10')
    def test_10_n_delete_nonexistent_share(self):
        """
        @tms_id: litpcds_6854_tc10
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Delete a share
        @tms_description: Verify deleting a non existing results in an
        exception
        @tms_test_steps:
        @step:Delete a non existing share
        @result: Exception raised: DeletionException
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_10.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True, share=True)

    @attr('all', 'revert', 'story6854', 'story6854_tc11')
    def test_11_p_query_pools(self):
        """
        @tms_id: litpcds_6854_tc11
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Query pools
        @tms_description: Verify querying list pools returns pool information
        @tms_test_steps:
        @step:Query the list of pools
        @result: List of pools is returned
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_11.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script)

    @attr('all', 'revert', 'story6854', 'story6854_tc12')
    def test_12_p_query_disks(self):
        """
        @tms_id: litpcds_6854_tc12
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Query disks
        @tms_description: Verify querying list disks returns disk information
        @tms_test_steps:
        @step:Query the list of disks
        @result: List of disks is returned
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_12.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script)

    @attr('all', 'revert', 'story6854', 'story6854_tc13')
    def test_13_p_vxcommands(self):
        """
        @tms_id: litpcds_6854_tc13
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Execute vxcommands
        @tms_description: Verify executing vxcommands return expected results
        @tms_test_steps:
        @step:Query the list of pools
        @result: List of pools is returned
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_13.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script)

    @attr('all', 'revert', 'story6854', 'story6854_tc14')
    def test_14_p_create_cache(self):
        """
        @tms_id: litpcds_6854_tc14
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Create cache
        @tms_description:  Verify querying list cache returns cache information
        @tms_test_steps:
        @step:Create a cache
        @result: Cache is created
        @step:Verify cache is in cache list
        @result: Cache is in cache list
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_14.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, cache=True)
        self.assertTrue(
            self.set_node_connection_data(
                self.nas_server, username=test_constants.SFS_MASTER_USR,
                password=test_constants.SFS_MASTER_PW))
        self.assertTrue(self.is_sfs_cache_present(
            self.nas_server, self.test_cache_name))

    @attr('all', 'revert', 'story6854', 'story6854_tc15')
    def test_15_n_duplicate_cache_creation(self):
        """
        @tms_id: litpcds_6854_tc15
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Create duplicate cache
        @tms_description: Verify creating a duplicate cache results in an
        exception
        @tms_test_steps:
        @step:Create a cache
        @result: Cache is created
        @step:Create duplicate cache
        @result: Exception thrown: CacheAlreadyExists
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_15.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, cache=True)

    @attr('all', 'revert', 'story6854', 'story6854_tc16')
    def test_16_p_delete_cache(self):
        """
        @tms_id: litpcds_6854_tc16
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Delete cache
        @tms_description: Verify deleting a cache is successful
        @tms_test_steps:
        @step:Create a cache
        @result: Cache is created
        @step:Delete a cache
        @result: Cache is deleted
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_16.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, cache=True)
        self.assertTrue(
            self.set_node_connection_data(
                self.nas_server, username=test_constants.SFS_MASTER_USR,
                password=test_constants.SFS_MASTER_PW))
        self.assertFalse(self.is_sfs_cache_present(
            self.nas_server, self.test_cache_name))

    @attr('all', 'revert', 'story6854', 'story6854_tc17')
    def test_17_n_delete_nonexistent_cache(self):
        """
        @tms_id: litpcds_6854_tc17
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Delete cache
        @tms_description: Verify deleting a non-existing cache results in an
        exception
        @tms_test_steps:
        @step:Delete a non-existing cache
        @result: Exception thrown: DoesNotExist
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_17.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, cache=True)

    @attr('all', 'revert', 'story6854', 'story6854_tc18')
    def test_18_n_cache_size_too_large(self):
        """
        @tms_id: litpcds_6854_tc18
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Delete cache
        @tms_description: Verify create a cache larger than available spaces
        throws an exception
        @tms_test_steps:
        @step:Create a cache
        @result: Exception thrown: NasException
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_18.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, cache=True)

    @attr('all', 'revert', 'story6854', 'story6854_tc19')
    def test_19_n_cache_with_invalid_pool(self):
        """
        @tms_id: litpcds_6854_tc19
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Delete cache
        @tms_description: Verify creating a cache with an invalid pool name
        results in an exception
        @tms_test_steps:
        @step:Create a cache
        @result: Exception raised: Pool.DoesNotExist
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_19.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, cache=True)

    @attr('all', 'revert', 'story6854', 'story6854_tc20')
    def test_20_p_resize_cache(self):
        """
        @tms_id: litpcds_6854_tc20
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Resize cache
        @tms_description: Verify resizing the cache is successful
        @tms_test_steps:
        @step:Create a cache
        @result: Cache is created
        @step:Re-size the cache
        @result: Cache is re-sized
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_20.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, cache=True)
        self.assertTrue(
            self.set_node_connection_data(
                self.nas_server, username=test_constants.SFS_MASTER_USR,
                password=test_constants.SFS_MASTER_PW))
        self.assertTrue(self.is_sfs_cache_present(
            self.nas_server, self.test_cache_name, "20"))

    @attr('all', 'revert', 'story6854', 'story6854_tc21')
    def test_21_p_create_snapshot(self):
        """
        @tms_id: litpcds_6854_tc21
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Create snapshot
        @tms_description: Verify creating a snapshot is successful
        @tms_test_steps:
        @step:Create a filesystem
        @result: filesystem is created
        @step:Create snapshot
        @result: snapshot is created
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_21.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True,
                          cache=True, snapshot=True)
        self.assertTrue(
            self.set_node_connection_data(
                self.nas_server, username=test_constants.SFS_MASTER_USR,
                password=test_constants.SFS_MASTER_PW))
        self.assertTrue(self.is_sfs_snapshot_present(
            self.nas_server, self.test_snapshot_name))

    @attr('all', 'revert', 'story6854', 'story6854_tc22')
    def test_22_n_duplicate_snap_creation(self):
        """
        @tms_id: litpcds_6854_tc22
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Create snapshot
        @tms_description: Verify re-creating a snapshot results in an
        exception
        @tms_test_steps:
        @step:Create a filesystem
        @result: filesystem is created
        @step:Create snapshot
        @result: snapshot is created
        @step:Re-create snapshot
        @result: Exception raised: Snapshot.AlreadyExists
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_22.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True,
                          cache=True, snapshot=True)

    @attr('all', 'revert', 'story6854', 'story6854_tc23')
    def test_23_p_delete_snapshot(self):
        """
        @tms_id: litpcds_6854_tc23
        @tms_requirements_id: LITPCDS-6854
        @tms_title: delete a snapshot
        @tms_description: Verify deleting a snapshot is successful
        @tms_test_steps:
        @step:Create a filesystem
        @result: filesystem is created
        @step:Create snapshot
        @result: snapshot is created
        @step:Remove snapshot
        @result:Snapshot is removed
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_23.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True,
                          cache=True, snapshot=True)
        self.assertTrue(
            self.set_node_connection_data(
                self.nas_server, username=test_constants.SFS_MASTER_USR,
                password=test_constants.SFS_MASTER_PW))
        self.assertFalse(self.is_sfs_snapshot_present(
            self.nas_server, self.test_snapshot_name))

    @attr('all', 'revert', 'story6854', 'story6854_tc24')
    def test_24_p_resize_filesystem(self):
        """
        @tms_id: litpcds_6854_tc24
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Resize a filesystem
        @tms_description: Verify deleting a snapshot is successful
        @tms_test_steps:
        @step:Create a filesystem
        @result: filesystem is created
        @step:re-size filesystem
        @result: filesystem is re-sized
        @tms_test_precondition: NA
        @tms_execution_type: Automated

        """
        test_script = "test_24.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True)
        self.assertTrue(
            self.set_node_connection_data(
                self.nas_server, username=test_constants.SFS_MASTER_USR,
                password=test_constants.SFS_MASTER_PW))
        self.assertTrue(self.is_sfs_filesystem_present(
            self.nas_server, self.test_fs_name, size="20.00M"))

    @attr('all', 'revert', 'story6854', 'story6854_tc25')
    def test_25_n_shrink_filesystem(self):
        """
        @tms_id: litpcds_6854_tc25
        @tms_requirements_id: LITPCDS-6854
        @tms_title: Shrink a file-sytem
        @tms_description: Verify shrinking a file-system results in an
        exception
        @tms_test_steps:
        @step:Create a filesystem
        @result: filesystem is created
        @step:Shrink filesystem
        @result:Exception raised: FileSystem.CannotShrinkException
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        test_script = "test_25.py"
        copy_success = self.copy_script_to_ms(test_script)
        self.assertTrue(copy_success, "Failed to copy files to MS")
        self._test_script(test_script, file_system=True)
        self.assertTrue(
            self.set_node_connection_data(
                self.nas_server, username=test_constants.SFS_MASTER_USR,
                password=test_constants.SFS_MASTER_PW))
        self.assertTrue(self.is_sfs_filesystem_present(
            self.nas_server, self.test_fs_name, size="10.00M"))
