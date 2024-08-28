"""
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     June 2018
@author:    Philip Daly
@summary:   Integration tests for Story: TORF-275856
"""
from litp_generic_test import GenericTest, attr
from redhat_cmd_utils import RHCmdUtils
from litp_cli_utils import CLIUtils
import test_constants
import copy
import random
import collections
CONSTANT_OPTIONS = \
    {"rw": "ro", "ro": "rw", "sync": "async",
     "async": "sync", "secure": "insecure",
     "insecure": "secure",
     "secure_locks": "insecure_locks",
     "insecure_locks": "secure_locks",
     "root_squash": "no_root_squash",
     "no_root_squash": "root_squash",
     "wdelay": "no_wdelay",
     "no_wdelay": "wdelay",
     "subtree_check": "no_subtree_check",
     "no_subtree_check": "subtree_check"}
CONSTANT_OPTIONS_LIST = \
    CONSTANT_OPTIONS.keys()


class Story275856(GenericTest):
    """
    TORF-275856:
    As a LITP user I want be able to modify the 'options'
    property in the 'sfs-export' item type so that I can
    update how an NFS share is exported
    """

    def setUp(self):
        """
        Runs before every single test
        """
        # 1. Call super class setup
        super(Story275856, self).setUp()
        self.redhat = RHCmdUtils()
        self.cli = CLIUtils()

        self.management_server = self.get_management_node_filename()

    def tearDown(self):
        """
        Runs after every single test
        """
        super(Story275856, self).tearDown()

    def get_sfs_exports_urls_from_model(self):
        """
        Function which returns a list of all
        specified sfs-exports residing within the
        LITP model.

        Returns:
            list. all sfs-exports in the LITP model.
        """
        storage_path = \
            self.find(self.management_server,
                      '/infrastructure',
                      'storage')[0]
        sfs_export_paths = \
            self.find(self.management_server,
                      storage_path,
                      'sfs-export')
        return sfs_export_paths

    def map_sfs_filesystem_to_exports_paths(self, urls):
        """
        Function which sets a list of exports urls as
        a dictionary value to a filesystem key.

        Args:
            urls (list): List of sfs-exports in the LITP model.

        Returns:
            dict. sfs-filesystems to sfs-exports mapping dict.
        """
        file_sys_to_export_mapping_dict = collections.defaultdict(list)
        for url in urls:
            # ASCERTAIN THE SFS-FILESYSTEM PARENT OF THE SFS-EXPORT
            fs_url = \
                self.find_parent_path_from_item_type(self.management_server,
                                                     'sfs-filesystem', url)

            # COLLECT ALL SFS-EXPORT CHILDREN URLS BELOW THE
            # SFS-FILESYSTEM OBJECT KEY INDEX.
            file_sys_to_export_mapping_dict[fs_url].append(url)

        return file_sys_to_export_mapping_dict

    def map_sfs_service_to_filesystems_paths(self, mapping_dict):
        """
        Function which creates a dictionary, with the sfs service
        as a key, which identifies its child sfs filesystems and
        sfs exports.

        Args:
            mapping_dict (dict): A dictionary containing
                                 sfs filesystem keys with
                                 a list of sfs exports values.

        Returns:
            dict. A mapping of sfs service to filesystems.
        """
        sfs_service_to_fs_mapping_dict = collections.defaultdict(dict)
        for fs_url in mapping_dict:
            # ASCERTAIN THE PARENT SFS SERVICE OF THE SFS FILESYSTEM
            service_url = \
                self.find_parent_path_from_item_type(self.management_server,
                                                     'sfs-service', fs_url)

            # COLLECT ALL SFS-FILESYSTEM CHILDREN URLS BELOW THE
            # SFS-SERVICE OBJECT KEY INDEX.
            sfs_service_to_fs_mapping_dict[service_url][fs_url] = \
                mapping_dict[fs_url]

        return sfs_service_to_fs_mapping_dict

    def create_props_dict_from_mappings_dict(self, mappings_dict):
        """
        Function which creates a dictionary of property values
        from the supplied dictionary of sfs object urls.

        Args:
            mappings_dict (dict): dictionary of sfs objects.

        Returns:
            dict. A dictionary of sfs properties.
        """
        props_dict = {}
        for sfs_url in mappings_dict:
            sfs_ip = \
                self.get_props_from_url(self.management_server,
                                        sfs_url, "management_ipv4")
            sfs_filename = self.get_sfs_node_from_ipv4(sfs_ip)[0]
            props_dict[sfs_filename] = {}
            for fs_url in mappings_dict[sfs_url]:
                fs_path = \
                    self.get_props_from_url(self.management_server,
                                            fs_url, "path")
                props_dict[sfs_filename][fs_path] = {}
                for exports_url in mappings_dict[sfs_url][fs_url]:

                    ipaddreses = \
                        self.get_props_from_url(self.management_server,
                                                exports_url,
                                                "ipv4allowed_clients")
                    options = \
                        self.get_props_from_url(self.management_server,
                                                exports_url, "options")
                    ip_list = ipaddreses.split(',')
                    props_dict[sfs_filename][fs_path]["ips"] = \
                        ip_list
                    props_dict[sfs_filename][fs_path]["options"] = \
                        options
        return props_dict

    def verify_sfs_exports(self):
        """
        Function which verifies whether the properties specified
        for sfs-export objects in the LITP model is what is
        currently configured on the SFS's.
        """
        sfs_export_paths = self.get_sfs_exports_urls_from_model()
        file_sys_to_export_mapping_dict = \
            self.map_sfs_filesystem_to_exports_paths(sfs_export_paths)
        sfs_service_to_fs_mapping_dict = \
            self.map_sfs_service_to_filesystems_paths(
                file_sys_to_export_mapping_dict)

        props_dict = \
            self.create_props_dict_from_mappings_dict(
                sfs_service_to_fs_mapping_dict)

        for sfs_node in props_dict:
            # SET USER TO SUPPORT
            self.assertTrue(
                self.set_node_connection_data(
                    sfs_node, username=test_constants.SFS_SUPPORT_USR,
                    password=test_constants.SFS_SUPPORT_PW))
            # ASCERTAIN THE FILESTORE SOLUTION IMPLEMENTED
            # REQUIRES SETTING THE USER TO MASTER
            solution = \
                self.identify_filestore_solution(sfs_node)
            self.assertTrue(
                self.set_node_connection_data(
                    sfs_node, username=test_constants.SFS_MASTER_USR,
                    password=test_constants.SFS_MASTER_PW))
            shares_dict = \
                self.get_sfs_shares_list(sfs_node)

            self.chk_sfs_shares(sfs_node,
                                props_dict, shares_dict, solution)

    def chk_sfs_shares(self, sfs_node, props_dict, shares_dict, solution):
        """
        Function which compares the expected properties against
        the properties currently configured on the SFS.

        Args:
            sfs_node (str): Node filename.
            props_dict (dict): Identifies all the properties to
                               be verified for the sfs.
            shares_dict (dict): Properties currently configured
                                on the SFS.
            solution (str): Identifies whether solution is SFS or VA.
        """
        for filesystem in props_dict[sfs_node]:
            ips = props_dict[sfs_node][filesystem]["ips"]
            options = \
                props_dict[sfs_node][filesystem]["options"]
            for share in shares_dict:
                if share["PATH"] == filesystem:
                    options_list = options.split(',')
                    if solution == "VA":
                        options_list.append("nordirplus")
                    options_list.sort()
                    share["PERM"] = share["PERM"].replace('(', '')
                    share["PERM"] = share["PERM"].replace(')', '')
                    share_ops_list = share["PERM"].split(',')
                    share_ops_list.sort()
                    # ENSURE THE SPECIFIED PROPERTIES ARE WHAT IS
                    # CURRENTLY CONFIGURED.
                    self.assertEqual(options_list,
                                     share_ops_list)
                    self.assertTrue(share["IP"] in ips,
                                    "No export entry "
                                    "found for IP: {0}".format(share["IP"]))
                    index = ips.index(share["IP"])
                    ips.pop(index)

            self.assertEqual([], ips)

    @staticmethod
    def remove_used_props_from_list_of_available_opts(existing_options):
        """
        Function which identifies the remaining available options
        from which new values can be drawn for the property.

        Args:
            existing_options (str): Options already set in the object.

        Returns:
            list. All available options remaining from which to choose.
        """
        existing_opts_list = existing_options.split(',')
        available_options = copy.deepcopy(CONSTANT_OPTIONS_LIST)
        for existing_option in existing_opts_list:
            # FOR EACH EXISTING PROPERTY VALUE
            # ASCERTAIN WHAT ITS OPPOSITE VALUE IS.
            # TYPICAL BOOL VALUE - IF ONE IS SET THEN THE OTHER
            # CANNOT, LEST A VALIDATION ERROR BE THROWN.
            # IE. RO & RW CANNOT BE SET SIMULTANEOUSLY.
            mirror_option = CONSTANT_OPTIONS[existing_option]

            # REMOVE BOTH THE SELECTED OPTION VALUE AND ITS OPPOSITE
            # FROM THE LIST OF AVAILABLE OPTIONS
            available_options.pop(available_options.index(existing_option))
            available_options.pop(available_options.index(mirror_option))

        return available_options

    def add_random_props_to_property(self, available_options, num_of_props=1):
        """
        Function which compiles a random list of options from the
        supplied list of available options.

        Args:
            available_options (list): Available options from which
                                      to draw a random list.

        KwArgs:
            num_of_props (int): Number of properties to draw,
                                defaults to 1.

        Returns:
            list. A random list of options.
        """
        counter = 0
        new_opts_list = []
        self.assertTrue(num_of_props <= len(available_options),
                        "The number of requested options exceeds "
                        "the number available.")
        while counter < num_of_props:
            # SELECT A RANDOM OPTION FROM THE AVAILABLE LIST
            choice = random.choice(available_options)
            new_opts_list.append(choice)

            # ASCERTAIN WHAT ITS OPPOSITE VALUE IS.
            # TYPICAL BOOL VALUE - IF ONE IS SET THEN THE OTHER
            # CANNOT, LEST A VALIDATION ERROR BE THROWN.
            # IE. RO & RW CANNOT BE SET SIMULTANEOUSLY.
            mirror_option = CONSTANT_OPTIONS[choice]

            # REMOVE BOTH THE SELECTED OPTION VALUE AND ITS OPPOSITE
            # FROM THE LIST OF AVAILABLE OPTIONS
            available_options.pop(available_options.index(choice))
            available_options.pop(available_options.index(mirror_option))
            counter = counter + 1

        return new_opts_list

    def replace_xml_property_values(self, filepath, tag, options,
                                    append=False):
        """
        Function which replaces, or appends values to, the values
        specified in the xml tag.

        Args:
            filepath (str): path to the file on the MS.

            tag (str): Tag within the XML file to be altered.

            options (list): Properties to be specified for the tag.

        KwArgs:
            append (bool): Flag specifying whether the options
                           should be appended to, or replace the
                           existing values. Defaults to False,
                           which will replace the existing value(s)..

        """
        # CAPTURE THE LINE CONTAINING THE DESIRED TAG
        file_contents_cmd = self.redhat.get_grep_file_cmd(filepath, tag)
        stdout, _, _ = \
            self.run_command(self.management_server, file_contents_cmd)
        original_options = stdout[0]

        # REFORMAT THE STRING WITH ESCAPE SLASH FOR SED PARSING
        reformated_orig_options = original_options.replace("/", "\\/")

        # ASCERTAIN THE STRING PLACEMENT OF THE XML TAGS
        counter = 0
        indexes = []
        for char in reformated_orig_options:
            if char == "<" or char == ">":
                indexes.append(counter)
            counter = counter + 1
        prefix = reformated_orig_options[:indexes[1] + 1]
        suffix = reformated_orig_options[indexes[2]:]

        # COMPILE THE VALUES TO BE PASSED TO THE PROPERTY.
        # EITHER AN OVERWRITE OF THE EXISTING VALUES OR
        # ADDED AS AN EXTRA VALUE TO THE EXISTING VALUES.
        if append:
            current = \
                reformated_orig_options[indexes[1] + 1:indexes[2]]
            contents = "{0},{1}".format(current, ",".join(options))
            new_options = "{0}{1}{2}".format(prefix, contents, suffix)
        else:
            new_options = \
                "{0}{1}{2}".format(prefix, ",".join(options), suffix)

        # EXECUTE THE COMMAND TO POPULATE THE XML TAG
        replace_cmd = \
            self.redhat.get_replace_str_in_file_cmd(reformated_orig_options,
                                                    new_options,
                                                    filepath, "-i")
        self.run_command(self.management_server, replace_cmd,
                         default_asserts=True)

    @staticmethod
    def swap_options(existing_options):
        """
        Function to swap the options provided to their
        boolean alternative.

        Args:
            existing_options (str): A string of the current
                                    options set for the
                                    sfs-export.

        Returns:
            list. A list of the swapped options.
        """
        options_list = existing_options.split(',')
        opposite_options = []
        for option in options_list:
            opposite_options.append(CONSTANT_OPTIONS[option])
        return opposite_options

    def identify_filestore_solution(self, node):
        """
        Function to identify whether the filestore solution
        utilised in the deployment is SFS or VA.

        Args:
            node (str): Connection data file name of the
                        filestore server name.

        Returns:
            str. Identifier of filestore solution: VA / SFS.
        """
        # THERE IS NO INDEPENDENT VERSION COMMAND THAT
        # IDENTIFIES THE SOLUTION INSTALLED. THE SSH
        # BANNER SEEMS TO BE THE EASIEST IDENTIFIER TO ACCESS.
        # FIND THE BANNER FILE.
        find_cmd = \
            self.redhat.get_find_cmd("/ -name banner")
        find_cmd = "/usr{0}".format(find_cmd)
        # IGNORE ANY UPGRADE RPM DIRS AND FOCUS ON THE LIVE CONFIG
        find_cmd = \
            find_cmd + " |{0} -v upgrade".format(self.redhat.grep_path)
        stdout, _, _ = \
            self.run_command(node, find_cmd)
        self.assertNotEqual([], stdout)
        # GATHER THE HEADER INFO
        cat_cmd = self.redhat.get_cat_cmd(stdout[0])
        stdout, _, _ = \
            self.run_command(node, cat_cmd)
        # BASE DECISION ON BANNER CONTENT.
        if self.is_text_in_list("Symantec FileStore", stdout):
            return "SFS"
        elif self.is_text_in_list("Veritas Access", stdout):
            return "VA"
        else:
            # RAISE AN ASSERTION AS FILESTORE SOLUTION NOT KNOWN
            self.assertTrue(False,
                            "Filestore solution not ascertained.")

    @attr('all', 'revert', 'story275856', 'story275856_tc01')
    def test_01_p_verify_initial_sfs_export_options(self):
        """
        @tms_id: TORF_275856_tc01
        @tms_requirements_id: TORF-275856
        @tms_title: Deploy SFS Export Options
        @tms_description: Verify the initial deployed
        sfs-export options
        @tms_test_steps:
        @step: Gather all sfs-exports in the deployment.
        @result: sfs-exports are gathered.
        @step: Ensure one or more sfs-exports is found.
        @result: More than zero sfs-exports are found.
        @step: Verify the deployment of all sfs-exports
               options and ips.
        @result: All sfs-exports are verified.
        @tms_test_precondition: sfs-exports deployed
        @tms_execution_type: Automated
        """
        self.log('info',
                 "Gathering all sfs-exports in the LITP model.")
        sfs_export_paths = \
            self.get_sfs_exports_urls_from_model()
        self.assertTrue(len(sfs_export_paths) > 0,
                        "No sfs-exports found in LITP model.")
        self.log('info',
                 "Verifying all sfs-exports found.")
        self.verify_sfs_exports()

    @attr('all', 'revert', 'story275856', 'story275856_tc02')
    def test_02_p_update_sfs_export_options_additional(self):
        """
        @tms_id: TORF_275856_tc02
        @tms_requirements_id: TORF-275856
        @tms_title: Deploy updated SFS Export Options
        @tms_description: Ensure it is possible to add extra values
        to the sfs-exports options property.
        @tms_test_steps:
        @step: Gather all sfs-exports in the deployment.
        @result: sfs-exports are gathered.
        @step: Ensure two or more sfs-exports are found.
        @result: Two or more sfs-exports are found.
        @step: Verify the deployment of all sfs-exports,
               options and ips.
        @result: All sfs-exports are verified.
        @step: Specify three new property values through the LITP CLI.
        @result: New values are specified through the LITP CLI.
        @step: Specify three new property values through the LITP XML.
        @result: New values are specified through the LITP XML.
        @step: Deploy the new configuration through create & run plan.
        @result: New configuration is deployed.
        @step: Verify the deployment of all sfs-exports
               options and ips.
        @result: All sfs-exports are verified.
        @tms_test_precondition: sfs-exports deployed
        @tms_execution_type: Automated
        """
        # ENSURE THERE ARE AT LEAST TWO SFS EXPORTS IN THE MODEL
        self.log('info',
                 "Gathering all sfs-exports in the LITP model.")
        sfs_export_paths = \
            self.get_sfs_exports_urls_from_model()
        self.assertTrue(len(sfs_export_paths) >= 2,
                        "Less than two sfs-exports were "
                        "found in the LITP model.")

        # ENSURE THE SFS EXPORTS ARE DEPLOYED CORRECTLY
        # BEFORE CONTINUING WITH UPDATE TEST.
        self.log('info',
                 "Verifying all sfs-exports found.")
        self.verify_sfs_exports()

        # ASCERTAIN PROPERTIES ALREADY DEFINED FOR THE
        # PROPERTY AND BACKUP EXISTING
        sfs_export_url_1 = sfs_export_paths[0]
        self.backup_path_props(self.management_server, sfs_export_url_1)
        self.log('info', "#1. TS2 SFS - Get existing options")
        existing_options = \
            self.get_props_from_url(self.management_server,
                                    sfs_export_url_1, "options")
        self.log('info', "Ascertain the available options")
        available_options = \
            self.remove_used_props_from_list_of_available_opts(
                existing_options)

        # SPECIFY THREE RANDOM NEW ADDITIONAL PROPERTY VALUES
        new_opts_list = \
            self.add_random_props_to_property(available_options, 3)

        # UPDATE OBJECT WITH NEW VALUES THROUGH THE CLI
        new_opts_string = \
            "{0},{1}".format(existing_options, ",".join(new_opts_list))
        self.log('info', "Specify the new options for the property")
        self.execute_cli_update_cmd(self.management_server,
                                    sfs_export_url_1,
                                    "options={0}".format(new_opts_string))

        # GET XML PATH
        sfs_export_url_2 = sfs_export_paths[1]
        self.backup_path_props(self.management_server, sfs_export_url_2)
        xml_file_path = '/home/litp-admin/exported_xml_tc_02_27856'
        xml_export_cmd = \
            self.cli.get_xml_export_cmd(sfs_export_url_2, xml_file_path)
        self.run_command(self.management_server, xml_export_cmd)
        self.log('info', "#2. TS2 XML - Get existing options")
        existing_options = \
            self.get_props_from_url(self.management_server,
                                    sfs_export_url_2, "options")
        self.log('info', "Ascertain the available options")
        available_options = \
            self.remove_used_props_from_list_of_available_opts(
                existing_options)

        # SPECIFY THREE RANDOM NEW ADDITIONAL PROPERTY VALUES
        new_opts_list = \
            self.add_random_props_to_property(available_options, 3)
        self.log('info',
                 "Replace the old prop value in the "
                 "XML with the new one")
        self.replace_xml_property_values(xml_file_path,
                                         'options',
                                         new_opts_list, True)

        export_collection_path = \
            self.find_parent_path_from_item_type(self.management_server,
                                                 'collection-of-sfs-export',
                                                 sfs_export_url_2)

        # LOAD THE XML FILE IN TO THE LITP MODEL.
        self.log('info', "Load in the XML")
        xml_load_cmd = \
            self.cli.get_xml_load_cmd(export_collection_path,
                                      xml_file_path, '--merge')
        self.run_command(self.management_server, xml_load_cmd)

        # DEPLOY NEW SFS-EXPORTS CONFIGURATION
        self.log('info', "Deploy the configuration.")
        self.run_and_check_plan(self.management_server,
                                test_constants.PLAN_COMPLETE,
                                20)

        # ENSURE THE SFS EXPORTS ARE DEPLOYED CORRECTLY
        self.log('info',
                 "Verifying all sfs-exports found.")
        self.verify_sfs_exports()

    @attr('all', 'revert', 'story275856', 'story275856_tc03')
    def test_03_p_update_sfs_export_options_swapped(self):
        """
        @tms_id: TORF_275856_tc03
        @tms_requirements_id: TORF-275856
        @tms_title: Deploy updated SFS Export Options
        @tms_description: Ensure it is possible to swap existing
        values to their boolean alternative.
        @tms_test_steps:
        @step: Gather all sfs-exports in the deployment.
        @result: sfs-exports are gathered.
        @step: Ensure two or more sfs-exports are found.
        @result: Two or more sfs-exports are found.
        @step: Verify the deployment of all sfs-exports,
               options and ips.
        @result: All sfs-exports are verified.
        @step: Swap existing values for the opposites through the LITP CLI.
        @result: New values are specified through the LITP CLI.
        @step: Swap existing values for the opposites through the LITP XML.
        @result: New values are specified through the LITP XML.
        @step: Deploy the new configuration through create & run plan.
        @result: New configuration is deployed.
        @step: Verify the deployment of all sfs-exports
               options and ips.
        @result: All sfs-exports are verified.
        @tms_test_precondition: sfs-exports deployed
        @tms_execution_type: Automated
        """
        # ENSURE THERE ARE AT LEAST TWO SFS EXPORTS IN THE MODEL
        self.log('info',
                 "Gathering all sfs-exports in the LITP model.")
        sfs_export_paths = \
            self.get_sfs_exports_urls_from_model()
        self.assertTrue(len(sfs_export_paths) >= 2,
                        "Less than two sfs-exports were "
                        "found in the LITP model.")

        # ENSURE THE SFS EXPORTS ARE DEPLOYED CORRECTLY
        # BEFORE CONTINUING WITH UPDATE TEST.
        self.log('info',
                 "Verifying all sfs-exports found.")
        self.verify_sfs_exports()

        # ASCERTAIN PROPERTIES ALREADY DEFINED FOR THE
        # PROPERTY
        sfs_export_url_1 = sfs_export_paths[0]
        self.backup_path_props(self.management_server, sfs_export_url_1)
        self.log('info', "#3. TS3 SFS - Get existing options")
        existing_options = \
            self.get_props_from_url(self.management_server,
                                    sfs_export_url_1, "options")

        # ASCERTAIN THE BOOLEAN OPPOSITE OF THE SPECIFIED
        # OPTIONS OF THE SFS-EXPORT
        self.log('info',
                 "Ascertain the boolean opposite of the specified options.")
        swapped_options = \
            self.swap_options(existing_options)

        # UPDATE OBJECT WITH NEW VALUES THROUGH THE CLI
        swapped_options_str = ",".join(swapped_options)
        self.log('info', "Specify the new options for the property")
        self.execute_cli_update_cmd(self.management_server,
                                    sfs_export_url_1,
                                    "options={0}".format(swapped_options_str))

        # GET XML PATH
        sfs_export_url_2 = sfs_export_paths[1]
        self.backup_path_props(self.management_server, sfs_export_url_2)
        xml_file_path = '/home/litp-admin/exported_xml_tc_03_27856'
        xml_export_cmd = \
            self.cli.get_xml_export_cmd(sfs_export_url_2, xml_file_path)
        self.run_command(self.management_server, xml_export_cmd)
        self.log('info', "#4. TS3 XML - Get existing options")
        existing_options = \
            self.get_props_from_url(self.management_server,
                                    sfs_export_url_2, "options")

        # ASCERTAIN THE BOOLEAN OPPOSITE OF THE SPECIFIED
        # OPTIONS OF THE SFS-EXPORT
        swapped_options = \
            self.swap_options(existing_options)

        # REPLACE THE PROPERTY VALUES WITH THEIR OPPOSITES.
        self.log('info',
                 "Replace the old prop value in the "
                 "XML with the new one")
        self.replace_xml_property_values(xml_file_path,
                                         'options',
                                         swapped_options)

        # LOAD THE XML FILE IN TO THE LITP MODEL.
        export_collection_path = \
            self.find_parent_path_from_item_type(self.management_server,
                                                 'collection-of-sfs-export',
                                                 sfs_export_url_2)
        self.log('info', "Load in the XML")
        xml_load_cmd = \
            self.cli.get_xml_load_cmd(export_collection_path,
                                      xml_file_path, '--merge')
        self.run_command(self.management_server, xml_load_cmd)

        # DEPLOY NEW SFS-EXPORTS CONFIGURATION
        self.log('info', "Deploy the configuration.")
        self.run_and_check_plan(self.management_server,
                                test_constants.PLAN_COMPLETE,
                                20)

        # ENSURE THE SFS EXPORTS ARE DEPLOYED CORRECTLY
        self.log('info',
                 "Verifying all sfs-exports found.")
        self.verify_sfs_exports()

    @attr('all', 'revert', 'story275856', 'story275856_tc04')
    def test_04_p_delete_sfs_export_options(self):
        """
        @tms_id: TORF_275856_tc04
        @tms_requirements_id: TORF-275856
        @tms_title: Deploy updated SFS Export Options,
                    deleting existing.
        @tms_description: Ensure it is possible to remove
        values from the existing options property.
        @tms_test_steps:
        @step: Gather all sfs-exports in the deployment.
        @result: sfs-exports are gathered.
        @step: Ensure two or more sfs-exports are found.
        @result: Two or more sfs-exports are found.
        @step: Verify the deployment of all sfs-exports,
               options and ips.
        @result: All sfs-exports are verified.
        @step: Specify only one of the existing values through the LITP CLI.
        @result: New value is specified through the LITP CLI.
        @step: Specify only one of the existing values through the LITP XML.
        @result: New value is specified through the LITP XML.
        @step: Deploy the new configuration through create & run plan.
        @result: New configuration is deployed.
        @step: Verify the deployment of all sfs-exports
               options and ips.
        @result: All sfs-exports are verified.
        @tms_test_precondition: sfs-exports deployed
        @tms_execution_type: Automated
        """
        # ENSURE THERE ARE AT LEAST TWO SFS EXPORTS IN THE MODEL
        self.log('info',
                 "Gathering all sfs-exports in the LITP model.")
        sfs_export_paths = \
            self.get_sfs_exports_urls_from_model()
        self.assertTrue(len(sfs_export_paths) >= 2,
                        "Less than two sfs-exports were "
                        "found in the LITP model.")

        # ENSURE THE SFS EXPORTS ARE DEPLOYED CORRECTLY
        # BEFORE CONTINUING WITH UPDATE TEST.
        self.log('info',
                 "Verifying all sfs-exports found.")
        self.verify_sfs_exports()

        # ASCERTAIN PROPERTIES ALREADY DEFINED FOR THE
        # PROPERTY
        sfs_export_url_1 = sfs_export_paths[0]
        self.backup_path_props(self.management_server, sfs_export_url_1)
        self.log('info', "#5. TS4 SFS - Get existing options")
        existing_options = \
            self.get_props_from_url(self.management_server,
                                    sfs_export_url_1, "options")

        # ENSURE THERE IS MORE THAN ONE OPTION SET FOR THE EXPORT
        existing_ops_list = existing_options.split(',')
        self.assertTrue(existing_ops_list > 1)

        # UPDATE OBJECT WITH NEW VALUE THROUGH THE CLI
        self.log('info', "Specify the new option for the property")
        self.execute_cli_update_cmd(self.management_server,
                                    sfs_export_url_1,
                                    "options={0}".format(existing_ops_list[0]))

        # GET XML PATH
        sfs_export_url_2 = sfs_export_paths[1]
        self.backup_path_props(self.management_server, sfs_export_url_2)
        xml_file_path = '/home/litp-admin/exported_xml_tc_04_27856'
        xml_export_cmd = \
            self.cli.get_xml_export_cmd(sfs_export_url_2, xml_file_path)
        self.run_command(self.management_server, xml_export_cmd)
        self.log('info', "#6. TS4 XML - Get existing options")
        existing_options = \
            self.get_props_from_url(self.management_server,
                                    sfs_export_url_2, "options")

        # ENSURE THERE IS MORE THAN ONE OPTION SET FOR THE EXPORT
        existing_ops_list = existing_options.split(',')
        self.assertTrue(existing_ops_list > 1)

        # UPDATE OBJECT WITH NEW VALUE THROUGH THE XML.
        self.log('info',
                 "Replace the old prop value in the "
                 "XML with the new one")
        self.replace_xml_property_values(xml_file_path,
                                         'options',
                                         [existing_ops_list[0]])

        # LOAD THE XML FILE IN TO THE LITP MODEL.
        export_collection_path = \
            self.find_parent_path_from_item_type(self.management_server,
                                                 'collection-of-sfs-export',
                                                 sfs_export_url_2)
        xml_load_cmd = \
            self.cli.get_xml_load_cmd(export_collection_path,
                                      xml_file_path, '--merge')
        self.run_command(self.management_server, xml_load_cmd)

        # DEPLOY NEW SFS-EXPORTS CONFIGURATION
        self.log('info', "Deploy the configuration.")
        self.run_and_check_plan(self.management_server,
                                test_constants.PLAN_COMPLETE,
                                20)

        # ENSURE THE SFS EXPORTS ARE DEPLOYED CORRECTLY
        self.log('info',
                 "Verifying all sfs-exports found.")
        self.verify_sfs_exports()

    @attr('all', 'revert', 'story275856', 'story275856_tc05')
    def test_05_n_sfs_exports_xml_validation(self):
        """
        @tms_id: TORF_275856_tc05
        @tms_requirements_id: TORF-275856
        @tms_title: Validating SFS Export Options through LITP XML load.
        @tms_description: Ensure that the correct validation
        errors are thrown when an invalid XML file is loaded.
        @tms_test_steps:
        @step: Gather all sfs-exports in the deployment.
        @result: sfs-exports are gathered.
        @step: Ensure at least one sfs-export is found.
        @result: One or more sfs-exports are found.
        @step: Attempt to specify an additional
        invalid value through the LITP XML.
        @result: A validation error is thrown.
        @step: Attempt to specify an additional
        invalid and valid value through the LITP XML.
        @result: A validation error is thrown.
        @step: Attempt to swap an existing
        valid value with an invalid one through the LITP XML.
        @result: A validation error is thrown.
        @step: Attempt to specify an empty string
        for the options through the LITP XML.
        @result: A validation error is thrown.
        @tms_test_precondition: sfs-exports deployed
        @tms_execution_type: Automated
        """
        self.log('info',
                 "test_05_p_update_sfs_export_options_additional_invalid")
        # ENSURE THERE IS AT LEAST ONE SFS EXPORT IN THE MODEL
        self.log('info',
                 "Gathering all sfs-exports in the LITP model.")
        sfs_export_paths = \
            self.get_sfs_exports_urls_from_model()
        self.assertTrue(len(sfs_export_paths) >= 1,
                        "No sfs-exports found in LITP model.")

        # GET XML PATH
        sfs_export_url_1 = sfs_export_paths[1]
        self.backup_path_props(self.management_server, sfs_export_url_1)
        xml_file_path = '/home/litp-admin/exported_xml_tc_05_27856'
        xml_export_cmd = \
            self.cli.get_xml_export_cmd(sfs_export_url_1, xml_file_path)
        self.run_command(self.management_server, xml_export_cmd)
        self.log('info', "#7. TS5 XML - Get existing options")
        existing_options = \
            self.get_props_from_url(self.management_server,
                                    sfs_export_url_1, "options")

        # ENSURE THERE IS MORE THAN ONE OPTION SET FOR THE EXPORT
        self.log('info', "Verify that there is more then one option "
                         "set for the export")
        existing_ops_list = existing_options.split(',')
        self.assertTrue(existing_ops_list > 1)

        # ADD AN ADDITIONAL INVALID VALUE.
        self.log('info',
                 "Add an additional invalid value to the property")
        self.replace_xml_property_values(xml_file_path,
                                         'options',
                                         ["INVALID"], True)

        # LOAD THE XML FILE IN TO THE LITP MODEL.
        self.log('info', " TS5 - Load the XML file into the LITP model")
        export_collection_path = \
            self.find_parent_path_from_item_type(self.management_server,
                                                 'collection-of-sfs-export',
                                                 sfs_export_url_1)
        xml_load_cmd = \
            self.cli.get_xml_load_cmd(export_collection_path,
                                      xml_file_path, '--merge')
        _, stderr, _ = \
            self.run_command(self.management_server, xml_load_cmd)

        validation_error = \
            "Invalid value \'{0},INVALID\'.".format(existing_options)
        self.assertTrue(self.is_text_in_list(validation_error, stderr),
                        "Validation error"
                        " for {0},INVALID.".format(",".join(existing_options)))
        validation_error = "The value '{0},INVALID' is " \
            "not accepted by the pattern".format(existing_options)
        self.assertTrue(self.is_text_in_list(validation_error, stderr),
                        "Validation error, "
                        "no regex for "
                        "{0},INVALID.".format(",".join(existing_options)))

        # test_06_p_update_sfs_export_options_additional_invalid_and_valid
        # ASCERTAIN THE OPTIONS REMAINING TO SET.
        self.log('info',
                 "test_06_p_update_sfs_export_"
                 "options_additional_invalid_and_valid")
        self.log('info', "Ascertain the available options")
        available_options = \
            self.remove_used_props_from_list_of_available_opts(
                existing_options)

        # SPECIFY ONE RANDOM NEW ADDITIONAL PROPERTY VALUES
        new_opts_list = \
            self.add_random_props_to_property(available_options)

        # ADD AN ADDITIONAL INVALID VALUE.
        new_options = copy.deepcopy(existing_ops_list)
        new_options.extend(new_opts_list)
        new_options.append('INVALID')
        self.log('info',
                 "Add additional valid values and "
                 "an invalid value to the property")
        self.replace_xml_property_values(xml_file_path,
                                         'options',
                                         new_options)

        # LOAD THE XML FILE IN TO THE LITP MODEL.
        self.log('info', " TS6 - Load the XML file into the LITP model")
        export_collection_path = \
            self.find_parent_path_from_item_type(self.management_server,
                                                 'collection-of-sfs-export',
                                                 sfs_export_url_1)
        xml_load_cmd = \
            self.cli.get_xml_load_cmd(export_collection_path,
                                      xml_file_path, '--merge')
        _, stderr, _ = \
            self.run_command(self.management_server, xml_load_cmd)

        validation_error = \
            'Invalid value \'{0}\'.'.format(",".join(new_options))
        self.assertTrue(self.is_text_in_list(validation_error, stderr),
                        "Validation error"
                        " for {0}.".format(",".join(new_options)))
        validation_error = \
            "The value '{0}' is not " \
            "accepted by the pattern".format(",".join(new_options))
        self.assertTrue(self.is_text_in_list(validation_error, stderr),
                        "Validation error, "
                        "no regex for {0}.".format(",".join(new_options)))

        # test_07_p_update_sfs_export_options_swapped_invalid
        # SWAP OUT AN EXISTING VALUE FOR AN INVALID VALUE
        self.log('info', "test_07_p_update_sfs_export_options_swapped_invalid")
        new_options = copy.deepcopy(existing_ops_list)
        new_options.pop(-1)
        new_options.append("INVALID")
        self.log('info',
                 "Replace a valid value with "
                 "an invalid value")
        self.replace_xml_property_values(xml_file_path,
                                         'options',
                                         new_options)

        # LOAD THE XML FILE IN TO THE LITP MODEL.
        self.log('info', " TS7 - Load the XML file into the LITP model")
        export_collection_path = \
            self.find_parent_path_from_item_type(self.management_server,
                                                 'collection-of-sfs-export',
                                                 sfs_export_url_1)
        xml_load_cmd = \
            self.cli.get_xml_load_cmd(export_collection_path,
                                      xml_file_path, '--merge')
        _, stderr, _ = \
            self.run_command(self.management_server, xml_load_cmd)

        validation_error = \
            'Invalid value \'{0}\'.'.format(",".join(new_options))
        self.assertTrue(self.is_text_in_list(validation_error, stderr),
                        "Validation error "
                        "for {0}.".format(",".join(new_options)))
        validation_error = \
            "The value '{0}' is not " \
            "accepted by the pattern".format(",".join(new_options))
        self.assertTrue(self.is_text_in_list(validation_error, stderr),
                        "Validation error, "
                        "no regex for {0}.".format(",".join(new_options)))

        # test_08_p_delete_sfs_export_options_all
        # SWAP OUT AN EXISTING VALUE FOR AN INVALID VALUE
        self.log('info', "test_08_p_delete_sfs_export_options_all")
        self.log('info',
                 "Delete an existing value from the options")
        self.replace_xml_property_values(xml_file_path,
                                         'options',
                                         [])

        # LOAD THE XML FILE IN TO THE LITP MODEL.
        self.log('info', " TS8 - Load the XML file into the LITP model")
        export_collection_path = \
            self.find_parent_path_from_item_type(self.management_server,
                                                 'collection-of-sfs-export',
                                                 sfs_export_url_1)
        xml_load_cmd = \
            self.cli.get_xml_load_cmd(export_collection_path,
                                      xml_file_path, '--merge')
        _, stderr, _ = \
            self.run_command(self.management_server, xml_load_cmd)

        validation_error = \
            'The value \'\' is not accepted by the pattern'
        self.assertTrue(self.is_text_in_list(validation_error, stderr),
                        "Validation error, blank options allowed.")
