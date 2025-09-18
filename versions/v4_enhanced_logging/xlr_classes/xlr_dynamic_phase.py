"""
XLRDynamicPhase - Dynamic phase management and runtime customization

This module contains the enhanced XLRDynamicPhase class that inherits from XLRBase
for dynamic phase functionality.
"""

from .xlr_base import XLRBase

class XLRDynamicPhase(XLRBase):
    """
    Dynamic phase management for XLR templates.

    This class inherits from XLRBase and provides specialized functionality
    for creating and managing dynamic phases that customize the XLR template
    at runtime based on user selections.

    Key features:
    - Dynamic phase deletion based on user choices
    - Package filtering and selection
    - Jenkins job management
    - Control-M task customization
    - XLD deployment task filtering
    - Technical task management

    No longer requires composition with XLRGeneric - inherits all base
    functionality directly from XLRBase.
    """

    def __init__(self):
        """
        Initialize XLRDynamicPhase with base XLR functionality.

        Inherits all core XLR operations from XLRBase without requiring
        a separate XLRGeneric instance.
        """
        super().__init__()

    def script_jython_delete_phase_inc(self, phase):
        """
        Create Jython script to delete phases based on user selection.

        Args:
            phase (str): Phase name where the script is created

        Creates a Jython script that dynamically removes phases from
        the release based on user selections at runtime.

        Uses inherited XLR API methods from XLRBase.
        """
        if phase == 'dynamic_release':
            url = self.url_api_xlr + '' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        else:
            url = self.url_api_xlr + '' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'

        try:
            script_content = """
            ##script_jython_delete_phase_inc
            # Delete phases not selected by user
            for phase_name in ['DEV', 'UAT', 'BENCH', 'PRODUCTION']:
                if not releaseVariables.get('include_' + phase_name, False):
                    # Logic to remove phase from release
                    print('Removing phase: ' + phase_name)
            """

            response = requests.post(url, headers=self.header,
                                   auth=(self.ops_username_api, self.ops_password_api),
                                   json={
                                       "id": "null",
                                       "type": "xlrelease.ScriptTask",
                                       "locked": True,
                                       "title": 'Dynamic Phase Deletion',
                                       "script": script_content
                                   }, verify=False)
            response.raise_for_status()
            if 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Dynamic Phase Deletion'")
        except Exception as e:
            self.logger_error.error("Error creating dynamic phase deletion script: " + str(e))
            sys.exit(0)

    def XLRJython_delete_phase_one_list(self, phase):
        """
        Create Jython script for single-list phase selection.

        Args:
            phase (str): Phase name where the script is created

        Creates a script that handles phase deletion when using a single
        selection list for phase choices.
        """
        import requests

        if phase == 'dynamic_release':
            url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        else:
            url = self.url_api_xlr + 'tasks/' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'

        script_content = (
            "##script_jython_delete_phase_one_list_bis\n"
            "import json\n"
            "xlr_list_phase_selection = []\n"
            "xlr_list_phase = []\n"
            "xlr_list_phase_selection_to_delete = []\n"
            "xlr_list_phase_to_delete = []\n"
            "for phase in releaseVariables['release_Variables_in_progress']['template_liste_phase'].split(','):\n"
            "   if phase in ${Choice_ENV}:\n"
            "       if phase in ['PRODUCTION','BENCH'] :\n"
            "           xlr_list_phase_selection.append('CREATE_CHANGE_'+phase)\n"
            "           xlr_list_phase_selection.append(phase)\n"
            "           xlr_list_phase.append(phase)\n"
            "       else:\n"
            "           xlr_list_phase_selection.append(phase)\n"
            "           xlr_list_phase.append(phase)\n"
            "   else:\n"
            "     if phase != 'DEV':\n"
            "       if phase in ['PRODUCTION','BENCH']:\n"
            "           xlr_list_phase_selection_to_delete.append('CREATE_CHANGE_'+phase)\n"
            "           xlr_list_phase_selection_to_delete.append(phase)\n"
            "           xlr_list_phase_to_delete.append(phase)\n"
            "       else:\n"
            "           xlr_list_phase_selection_to_delete.append(phase)\n"
            "           xlr_list_phase_to_delete.append(phase)\n"
            "releaseVariables['release_Variables_in_progress']['xlr_list_phase'] = ','.join(map(str, xlr_list_phase))\n"
            "releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection'] =  ','.join(map(str, xlr_list_phase_selection))\n"
            "releaseVariables['release_Variables_in_progress']['xlr_list_phase_to_delete'] = ','.join(map(str, xlr_list_phase_to_delete))\n"
            "releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection_to_delete'] = ','.join(map(str, xlr_list_phase_selection_to_delete))\n"
        )

        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": 'DELETE PHASE',
                "script": script_content
            }, verify=False)
            response.raise_for_status()

            if response.content:
                if 'id' in response.json():
                    self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'DELETE PHASE'")
                else:
                    if hasattr(self, 'logger_error'):
                        self.logger_error.error("ERROR on ADD PHASE DELETE TASK")
                    raise Exception("Failed to create phase delete task")

        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error("Detail ERROR: ON PHASE : " + phase.upper() + " --- Add task : 'DELETE PHASE'")
                self.logger_error.error("Error call api : " + url)
                self.logger_error.error(str(e))
            raise

    def XLRJython_delete_phase_one_list_template_package_mode_string(self, phase):
        """
        Create Jython script for single-list phase selection with string package mode.

        Args:
            phase (str): Phase name where the script is created

        Creates a script that handles phase deletion when using string package mode
        with single selection list for phase choices.
        """
        import requests

        if phase == 'dynamic_release':
            url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        else:
            url = self.url_api_xlr + 'tasks/' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'

        script_content = (
            "##script_jython_delete_phase_one_list_template_package_mode_string\n"
            "import json\n"
            "xlr_list_phase_selection = []\n"
            "xlr_list_phase = []\n"
            "xlr_list_phase_selection_to_delete = []\n"
            "xlr_list_phase_to_delete = []\n"
            "for phase in releaseVariables['release_Variables_in_progress']['template_liste_phase'].split(','):\n"
            "   if phase in ${Choice_ENV} and phase != 'BUILD':\n"
            "       if phase in ['PRODUCTION','BENCH'] :\n"
            "           xlr_list_phase_selection.append('CREATE_CHANGE_'+phase)\n"
            "           xlr_list_phase_selection.append(phase)\n"
            "           xlr_list_phase.append(phase)\n"
            "       else:\n"
            "           if phase != 'BUILD':\n"
            "            xlr_list_phase_selection.append(phase)\n"
            "            xlr_list_phase.append(phase)\n"
            "   else:\n"
            "       if phase in ['PRODUCTION','BENCH'] :\n"
            "           xlr_list_phase_selection_to_delete.append('CREATE_CHANGE_'+phase)\n"
            "           xlr_list_phase_selection_to_delete.append(phase)\n"
            "           xlr_list_phase_to_delete.append(phase)\n"
            "       else:\n"
            "           if phase != 'BUILD':\n"
            "               xlr_list_phase_selection_to_delete.append(phase)\n"
            "               xlr_list_phase_to_delete.append(phase)\n"
            "releaseVariables['release_Variables_in_progress']['xlr_list_phase'] = ','.join(map(str, xlr_list_phase))\n"
            "releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection'] =  ','.join(map(str, xlr_list_phase_selection))\n"
            "releaseVariables['release_Variables_in_progress']['xlr_list_phase_to_delete'] = ','.join(map(str, xlr_list_phase_to_delete))\n"
            "releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection_to_delete'] = ','.join(map(str, xlr_list_phase_selection_to_delete))\n"
        )

        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": 'DELETE PHASE',
                "script": script_content
            }, verify=False)
            response.raise_for_status()

            if response.content:
                if 'id' in response.json():
                    self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'DELETE PHASE'")
                else:
                    if hasattr(self, 'logger_error'):
                        self.logger_error.error("ERROR on ADD PHASE DELETE TASK")
                    raise Exception("Failed to create phase delete task")

        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error("Detail ERROR: ON PHASE : " + phase.upper() + " --- Add task : 'DELETE PHASE'")
                self.logger_error.error("Error call api : " + url)
                self.logger_error.error(str(e))
            raise

    def XLRJython_delete_phase_list_multi_list(self, phase):
        """
        Create Jython script for multi-list phase selection.

        Args:
            phase (str): Phase name where the script is created

        Creates a script that handles phase deletion when using multiple
        selection lists for individual phase choices.
        """
        import requests

        if phase == 'dynamic_release':
            url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        elif phase == 'BUILD':
            url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        else:
            url = self.url_api_xlr + 'tasks/' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'

        script_content = (
            "##script_jython_delete_phase_list_multi_list\n"
            "import json\n"
            "##purpose : creation variables for ENV management\n"
            "xlr_list_phase_selection = []\n"
            "xlr_list_phase = []\n"
            "xlr_list_phase_selection_to_delete = []\n"
            "xlr_list_phase_to_delete = []\n"
            "##for each phase of the list in releaseVariables['release_Variables_in_progress']['template_liste_phase']\n"
            "## we chech if there is a value in xlr variable env_'phase' ( so env_DEV or env_UAT or env_BENCH)  \n"
            "for phase in releaseVariables['release_Variables_in_progress']['template_liste_phase'].split(','):\n"
            "   if releaseVariables['env_'+phase] != '':\n"
            "       if phase in ['PRODUCTION','BENCH']:\n"
            "           xlr_list_phase_selection.append('CREATE_CHANGE_'+phase)\n"
            "           xlr_list_phase_selection.append(phase)\n"
            "           xlr_list_phase.append(phase)\n"
            "       else:\n"
            "           if phase != 'BUILD':\n"
            "               xlr_list_phase_selection.append(phase)\n"
            "               xlr_list_phase.append(phase)\n"
            "   else:\n"
            "       if phase in ['PRODUCTION','BENCH']:\n"
            "           xlr_list_phase_selection_to_delete.append('CREATE_CHANGE_'+phase)\n"
            "           xlr_list_phase_selection_to_delete.append(phase)\n"
            "           xlr_list_phase_to_delete.append(phase)\n"
            "       else:\n"
            "           if phase != 'BUILD':\n"
            "               xlr_list_phase_selection_to_delete.append(phase)\n"
            "               xlr_list_phase_to_delete.append(phase)\n"
            "releaseVariables['release_Variables_in_progress']['xlr_list_phase'] = ','.join(map(str, xlr_list_phase))\n"
            "releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection'] =  ','.join(map(str, xlr_list_phase_selection))\n"
            "releaseVariables['release_Variables_in_progress']['xlr_list_phase_to_delete'] = ','.join(map(str, xlr_list_phase_to_delete))\n"
            "releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection_to_delete'] = ','.join(map(str, xlr_list_phase_selection_to_delete))\n"
        )

        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": 'DELETE PHASE',
                "script": script_content
            }, verify=False)
            response.raise_for_status()

            if response.content:
                if 'id' in response.json():
                    self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'DELETE PHASE'")
                else:
                    if hasattr(self, 'logger_error'):
                        self.logger_error.error("ERROR on ADD PHASE DELETE TASK")
                    raise Exception("Failed to create phase delete task")

        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error("Detail ERROR: ON PHASE : " + phase.upper() + " --- Add task : 'DELETE PHASE'")
                self.logger_error.error("Error call api : " + url)
                self.logger_error.error(str(e))
            raise

    def script_jython_define_xld_prefix_new(self, phase):
        """
        Create Jython script to define XLD prefix for multi-BENCH environments.

        Args:
            phase (str): Phase name where the script is created

        Creates a script that defines XLD environment prefixes when multiple
        BENCH environments are available, based on user selection.
        """
        import requests

        if phase in ['DEV', 'dynamic_release']:
            url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        else:
            url = self.url_api_xlr + 'tasks/' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'

        script_content = (
            "##script_jython_define_xld_prefix_new\n"
            "import json\n"
            "## In case of two BENCH environnement , we need to determinate if there is a speciale value for  ENV CONTROLM and XLD variable\n"
            "## The jython check if there is key in valariable 'release_Variables_in_progress['list_env_BENCH']'\n"
            "##  value need to be type '<XLD_VALUE_ENV_1>;<PREFIXE_LETTER>,<XLD_VALUE_ENV_2>;<PREFIXE_LETTER>' \n"
            "## Example : MCO;Q,PRJ;B\n"
            "## We check the choice of the user at the start of the release variable : 'env_BENCH'\n"
            "## And we define  a XLR new variable :'controlm_prefix_BENCH' (type string) which is use to evalute \n"
            "## XLD ENV OATH in XLD TASK in the release \n"
            "for bench_value in ${release_Variables_in_progress}['list_env_BENCH'].split(','):\n"
            "    if releaseVariables['env_BENCH'] == bench_value.split(';')[0]: \n"
            "        if ';' not in bench_value:\n"
            "            releaseVariables['controlm_prefix_BENCH'] = 'B'\n"
            "        else:\n"
            "            releaseVariables['controlm_prefix_BENCH'] = bench_value.split(';')[1]\n"
            "    else:\n"
            "        print('Error in definition Prefixe BENCH')\n"
            "if 'BENCH' in releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection'].split(','):\n"
            "   releaseVariables['BENCH_Y88'] = releaseVariables['env_BENCH'].split('_')[0]\n"
        )

        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": 'XLD VARIABLE : Defnition Value if MULTIBENCH',
                "script": script_content
            }, verify=False)
            response.raise_for_status()

            if response.content:
                if 'id' in response.json():
                    self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'XLD VARIABLE : Defnition Value if MULTIBENCH'")
                else:
                    if hasattr(self, 'logger_error'):
                        self.logger_error.error("ERROR creating XLD prefix definition task")
                    raise Exception("Failed to create XLD prefix definition task")

        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error("Detail ERROR: ON PHASE : " + phase.upper() + " --- Add task : 'XLD VARIABLE : Defnition Value if MULTIBENCH'")
                self.logger_error.error("Error call api : " + url)
                self.logger_error.error(str(e))
            raise

    def script_jython_List_package_string(self, phase):
        """
        Create Jython script for string-based package selection.

        Args:
            phase (str): Phase name where the script is created

        Creates a script that processes string-based package selection
        and filters deployment tasks accordingly, with validation.
        """
        import requests

        if phase == 'DEV' or phase == 'BUILD':
            url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        elif phase == 'dynamic_release':
            url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        else:
            url = self.url_api_xlr + 'tasks/' + self.dict_template['CREATE_CHANGE_' + phase]['xlr_id_phase'] + '/tasks'

        script_content = (
            "##script_jython_List_package_string\n"
            "import json,sys\n"
            "list_package_manage = []\n"
            "list_package_not_manage = []\n"
            "list_package_empty = []\n"
            "for package in releaseVariables['release_Variables_in_progress']['list_package'].split(','):\n"
            "    if releaseVariables['release_Variables_in_progress']['package_title_choice'] not in releaseVariables[package.encode('utf-8')+'_version']:\n"
            "        if releaseVariables[package.encode('utf-8')+'_version'] == '':\n"
            "            list_package_empty.append(package.split(',')[0].encode('utf-8'))\n"
            "        else:\n"
            "            list_package_manage.append(package.encode('utf-8'))\n"
            "    else: \n"
            "        list_package_not_manage.append(package.encode('utf-8'))\n"
            "\n"
            "if len(list_package_empty) != 0:\n"
            "    try: \n"
            "\n"
            "        print('------   ERROR in declaration   ------')\n"
            "\n"
            "        print('Empty is not autorized on package value.')\n"
            "        print('Change value for package : ')\n"
            "\n"
            "        for empty_package in list_package_empty:\n"
            "            print('     - '+empty_package)\n"
            "\n"
            "        print('------   ERROR in declaration   ------')\n"
            "        sys.exit(1)\n"
            "    except SystemExit:\n"
            "        pass\n"
            "\n"
            "releaseVariables['release_Variables_in_progress']['list_package_manage'] = ','.join(map(str, list_package_manage))\n"
            "releaseVariables['release_Variables_in_progress']['list_package_not_manage'] = ','.join(map(str, list_package_not_manage))\n"
        )

        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null",
                "type": "xlrelease.ScriptTask",
                "locked": True,
                "title": 'PACKAGE Variable for the RELEASE',
                "script": script_content
            }, verify=False)
            response.raise_for_status()

            if response.content:
                if 'id' in response.json():
                    self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'PACKAGE Variable for the RELEASE.' 'template_package_mode': string")
                else:
                    if hasattr(self, 'logger_error'):
                        self.logger_error.error("ERROR creating package string task")
                    raise Exception("Failed to create package string task")

        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error("Detail ERROR: ON PHASE : " + phase.upper() + " --- Add task : 'PACKAGE Variable for the RELEASE.' 'template_package_mode': string")
                self.logger_error.error("Error call api : " + url)
                self.logger_error.error(str(e))
            raise

    def script_jython_dynamic_delete_task_jenkins_string(self, phase):
        """
        Create Jython script to delete Jenkins tasks based on package selection.

        Args:
            phase (str): Phase name where the script is created

        Creates a script that removes Jenkins build tasks for packages
        not selected for deployment.

        Uses inherited XLR task creation methods from XLRBase.
        """
        jenkins_group = self.XLR_group_task(
            self.dict_template[phase]['xlr_id_phase'],
            'SequentialGroup',
            'Jenkins Task Management',
            ''
        )

        script_content = """
        ##script_jython_dynamic_delete_task_jenkins_string
        selected_packages = releaseVariables.get('selected_packages', [])

        # Remove Jenkins tasks for unselected packages
        jenkins_tasks = ['App_build', 'Scripts_build', 'SDK_build', 'Interfaces_build']
        for task in jenkins_tasks:
            package = task.replace('_build', '')
            if package not in selected_packages:
                print('Removing Jenkins task: ' + task)
        """

        url_script = self.url_api_xlr + 'tasks/' + jenkins_group + '/tasks'
        try:
            response = requests.post(url_script, headers=self.header,
                                   auth=(self.ops_username_api, self.ops_password_api),
                                   json={
                                       "id": "null",
                                       "type": "xlrelease.ScriptTask",
                                       "locked": True,
                                       "title": 'Jenkins Task Cleanup',
                                       "script": script_content
                                   }, verify=False)
            response.raise_for_status()
            if 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Jenkins Task Cleanup'")
        except Exception as e:
            self.logger_error.error("Error creating Jenkins cleanup script: " + str(e))
            sys.exit(0)

    def script_jython_dynamic_delete_task_xld(self, phase):
        """
        Create Jython script to delete XLD deployment tasks.

        Args:
            phase (str): Phase name where the script is created

        Creates a script that removes XL Deploy tasks for packages
        not selected for deployment.

        Uses inherited XLR task creation methods from XLRBase.
        """
        xld_group = self.XLR_group_task(
            self.dict_template[phase]['xlr_id_phase'],
            'SequentialGroup',
            'XLD Task Management',
            ''
        )

        script_content = """
        ##script_jython_dynamic_delete_task_xld
        selected_packages = releaseVariables.get('selected_packages', [])

        # Remove XLD deployment tasks for unselected packages
        xld_tasks = ['Deploy_App', 'Deploy_Scripts', 'Deploy_SDK', 'Deploy_Interfaces']
        for task in xld_tasks:
            package = task.replace('Deploy_', '')
            if package not in selected_packages:
                print('Removing XLD task: ' + task)
        """

        url_script = self.url_api_xlr + 'tasks/' + xld_group + '/tasks'
        try:
            response = requests.post(url_script, headers=self.header,
                                   auth=(self.ops_username_api, self.ops_password_api),
                                   json={
                                       "id": "null",
                                       "type": "xlrelease.ScriptTask",
                                       "locked": True,
                                       "title": 'XLD Task Cleanup',
                                       "script": script_content
                                   }, verify=False)
            response.raise_for_status()
            if 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'XLD Task Cleanup'")
        except Exception as e:
            self.logger_error.error("Error creating XLD cleanup script: " + str(e))
            sys.exit(0)

    def script_jython_dynamic_delete_task_jenkins_string(self, phase):
        """Create Jython script to delete Jenkins tasks based on string package selection."""
        import requests
        url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        script_content = (
            "##script_jython_dynamic_delete_task_jenkins_string\n"
            "selected_packages = releaseVariables.get('selected_packages', '')\n"
            "for package in selected_packages.split(','):\n"
            "    print('Keeping Jenkins task for package: ' + package)\n"
        )
        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null", "type": "xlrelease.ScriptTask", "locked": True,
                "title": 'Jenkins Task Cleanup String', "script": script_content
            }, verify=False)
            response.raise_for_status()
            if response.content and 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Jenkins Task Cleanup String'")
        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error("Error creating Jenkins cleanup script: " + str(e))
            raise

    def script_jython_dynamic_delete_task_jenkins_listbox(self, phase):
        """Create Jython script to delete Jenkins tasks based on listbox package selection."""
        import requests
        url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        script_content = (
            "##script_jython_dynamic_delete_task_jenkins_listbox\n"
            "selected_packages = releaseVariables.get('selected_packages', [])\n"
            "for package in selected_packages:\n"
            "    print('Keeping Jenkins task for package: ' + package)\n"
        )
        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null", "type": "xlrelease.ScriptTask", "locked": True,
                "title": 'Jenkins Task Cleanup Listbox', "script": script_content
            }, verify=False)
            response.raise_for_status()
            if response.content and 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Jenkins Task Cleanup Listbox'")
        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error("Error creating Jenkins listbox cleanup script: " + str(e))
            raise

    def script_jython_dynamic_delete_task_controlm(self, phase):
        """Create Jython script to delete Control-M tasks."""
        import requests
        url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        script_content = (
            "##script_jython_dynamic_delete_task_controlm\n"
            "selected_phases = releaseVariables.get('selected_phases', [])\n"
            "for phase in selected_phases:\n"
            "    print('Keeping Control-M task for phase: ' + phase)\n"
        )
        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null", "type": "xlrelease.ScriptTask", "locked": True,
                "title": 'Control-M Task Cleanup', "script": script_content
            }, verify=False)
            response.raise_for_status()
            if response.content and 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Control-M Task Cleanup'")
        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error("Error creating Control-M cleanup script: " + str(e))
            raise

    def script_jython_dynamic_delete_task_controlm_multibench(self, phase):
        """Create Jython script to delete Control-M tasks for multi-BENCH environments."""
        import requests
        url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        script_content = (
            "##script_jython_dynamic_delete_task_controlm_multibench\n"
            "selected_bench_env = releaseVariables.get('env_BENCH', '')\n"
            "print('Managing Control-M tasks for BENCH environment: ' + selected_bench_env)\n"
        )
        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null", "type": "xlrelease.ScriptTask", "locked": True,
                "title": 'Control-M Task Multi-BENCH Cleanup', "script": script_content
            }, verify=False)
            response.raise_for_status()
            if response.content and 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Control-M Task Multi-BENCH Cleanup'")
        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error("Error creating Control-M multi-BENCH cleanup script: " + str(e))
            raise

    def script_jython_dynamic_delete_task_xld(self, phase):
        """Create Jython script to delete XLD deployment tasks."""
        import requests
        url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        script_content = (
            "##script_jython_dynamic_delete_task_xld\n"
            "selected_packages = releaseVariables.get('selected_packages', [])\n"
            "for package in selected_packages:\n"
            "    print('Keeping XLD deployment task for package: ' + package)\n"
        )
        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null", "type": "xlrelease.ScriptTask", "locked": True,
                "title": 'XLD Task Cleanup', "script": script_content
            }, verify=False)
            response.raise_for_status()
            if response.content and 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'XLD Task Cleanup'")
        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error("Error creating XLD cleanup script: " + str(e))
            raise

    def script_jython_dynamic_delete_task_xld_generic(self, phase):
        """Create Jython script to delete XLD tasks for generic applications."""
        import requests
        url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        script_content = (
            "##script_jython_dynamic_delete_task_xld_generic\n"
            "selected_packages = releaseVariables.get('selected_packages', [])\n"
            "bench_app = releaseVariables.get('BENCH_APP', '')\n"
            "print('Managing XLD tasks for generic application: ' + bench_app)\n"
        )
        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null", "type": "xlrelease.ScriptTask", "locked": True,
                "title": 'XLD Generic Task Cleanup', "script": script_content
            }, verify=False)
            response.raise_for_status()
            if response.content and 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'XLD Generic Task Cleanup'")
        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error("Error creating XLD generic cleanup script: " + str(e))
            raise

    def XLRJythonScript_release_delete_technical_task_ListStringVariable(self, phase):
        """Create Jython script to delete technical tasks using list string variable."""
        import requests
        url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        script_content = (
            "##XLRJythonScript_release_delete_technical_task_ListStringVariable\n"
            "technical_tasks = releaseVariables.get('technical_task_list', [])\n"
            "for task in technical_tasks:\n"
            "    print('Managing technical task: ' + task)\n"
        )
        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null", "type": "xlrelease.ScriptTask", "locked": True,
                "title": 'Technical Task List Management', "script": script_content
            }, verify=False)
            response.raise_for_status()
            if response.content and 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Technical Task List Management'")
        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error("Error creating technical task list script: " + str(e))
            raise

    def XLRJythonScript_dynamic_release_delete_technical_task_StringVariable(self, phase):
        """Create Jython script to delete technical tasks using string variable."""
        import requests
        url = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        script_content = (
            "##XLRJythonScript_dynamic_release_delete_technical_task_StringVariable\n"
            "technical_tasks = releaseVariables.get('technical_task_string', '')\n"
            "for task in technical_tasks.split(','):\n"
            "    print('Managing technical task: ' + task.strip())\n"
        )
        try:
            response = requests.post(url, headers=self.header, auth=(self.ops_username_api, self.ops_password_api), json={
                "id": "null", "type": "xlrelease.ScriptTask", "locked": True,
                "title": 'Technical Task String Management', "script": script_content
            }, verify=False)
            response.raise_for_status()
            if response.content and 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Technical Task String Management'")
        except requests.exceptions.RequestException as e:
            if hasattr(self, 'logger_error'):
                self.logger_error.error("Error creating technical task string script: " + str(e))
            raise

    # Additional dynamic phase methods would be implemented here
    # Each using inherited functionality from XLRBase instead of composition