
"""
XLR Template Generation Classes

This module contains all the specialized classes for creating XebiaLabs Release (XLR) templates
that orchestrate complex deployment pipelines across multiple environments.

Classes:
    XLRControlm: Control-M batch job scheduling integration
    XLRGeneric: Base XLR operations and template management
    XLRDynamicPhase: Dynamic phase creation and management
    XLRSun: ServiceNow (SUN) approval workflow integration
    XLRTaskScript: Custom script task generation and management

The classes work together through multiple inheritance to provide comprehensive
deployment automation including:
- Multi-environment deployments (DEV, UAT, BENCH, PRODUCTION)
- Approval workflows for production environments
- Batch job scheduling coordination
- Build system integration (Jenkins)
- Deployment tool integration (XL Deploy)
- Email notifications and reporting

Author: Generated for generic application deployment
Version: 2.0 (Generic)
"""

from base64 import b64encode
import os,sys,requests,urllib3,inspect,configparser,json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
class XLRTaskScript:
    """
    Custom script task generation and management for XLR templates.

    This class provides functionality to create various types of script tasks
    within XLR templates, particularly Jython scripts for:
    - Variable manipulation and calculation
    - Dynamic content generation
    - Jenkins integration and parameter passing
    - Date/time formatting for external systems
    - Release metadata management
    - Custom business logic execution

    Script tasks are used for:
    - Runtime template customization
    - Data transformation and formatting
    - External system integration
    - Workflow decision making
    - Parameter validation and processing

    The class generates Jython scripts that execute within the XLR environment
    to provide dynamic behavior and integration capabilities.
    """

    def __init__(self,parameters):
        """
        Initialize XLRTaskScript with configuration parameters.

        Args:
            parameters (dict): YAML configuration containing template settings

        Sets up the script task generator with access to template configuration
        for creating context-appropriate script tasks.
        """
        self.parameters = parameters
    def script_jython_get_user_from_task(self,phase,task_id):
        url_get_user_from_task=self.url_api_xlr+'tasks/'+task_id+'/tasks'
        requests.post(url_get_user_from_task, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'Put date from input at format for COTROLM demand' ,
                                                            "script":  "##script_jython_get_user_from_task\n"
                                                                        "from time import strftime\n"
                                                                        "date_format = strftime('%Y%m%d')\n"
                                                                        "print(date_format)\n"
                                                                        "releaseVariables['controlm_today'] = date_format\n"                                                                     
                                                                        },verify = False)
    def script_jython_define_variable_release(self,phase):
        if phase == 'DEV':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        if phase == 'BUILD':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        elif phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'        
        reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'define Variable date for jenkinks build' ,
                                                            "script":  "##script_jython_define_variable_release\n"
                                                                       "from time import strftime\n"
                                                                       "releaseVariables['Date'] = strftime('%Y%m%d')\n"
                                                                       "\n"},verify = False)

    def script_jython_put_value_version(self,phase):
        if phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        try: 
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'Give value to package if no build' ,
                                                            "script":  "##script_jython_put_value_version\n"
                                                                       "import json\n"
                                                                    "if 'BENCH' in ${release_Variables_in_progress}['xlr_list_phase'].split(',') and len(releaseVariables['env_BENCH']) == 0:\n"
                                                                    "   for package in releaseVariables['release_Variables_in_progress']['list_package_manage'].split(','):\n"
                                                                    "       releaseVariables[package+'_version'] = '${NAME_VERSION}'\n"
                                                                    "else:   \n"
                                                                    "   for package in releaseVariables['release_Variables_in_progress']['list_package_manage'].split(','):\n"
                                                                    "       releaseVariables[package+'_version'] = '${NAME_VERSION}'\n"
                                                                    "   \n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'Give value to package if no build'. When 'FROM_NAME_BRANCH' in 'type_template' from yaml conf file")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'Give value to package if no build'. When 'FROM_NAME_BRANCH' in 'type_template' from yaml conf file")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)

    def script_jython_put_value_version_listox(self,phase):
        if phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        try: 
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'Give value to package if no build' ,
                                                            "script":  "##script_jython_put_value_version\n"
                                                                       "import json\n"
                                                                    "if 'BENCH' in ${release_Variables_in_progress}['xlr_list_phase'].split(',') and len(releaseVariables['env_BENCH']) == 0:\n"
                                                                    "   for package in releaseVariables['List_package']:\n"
                                                                    "       releaseVariables[package+'_version'] = '${NAME_VERSION}'\n"
                                                                    "else:   \n"
                                                                    "   for package in releaseVariables['List_package']:\n"
                                                                    "       releaseVariables[package+'_version'] = '${NAME_VERSION}'\n"
                                                                    "   \n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'Give value to package if no build'. When 'FROM_NAME_BRANCH' in 'type_template' from yaml conf file")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'Give value to package if no build'. When 'FROM_NAME_BRANCH' in 'type_template' from yaml conf file")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)

    def get_num_version_from_jenkins_static(self,phase):
        if phase in ['DEV','dynamic_release']:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : False,
                                                            "title" : 'GIVE VALUE TO PACKAGE CHOICE' ,
                                                            "script":  "##get_num_version_from_jenkins_static\n"
                                                                       "import json\n"  
                                                                       "for package in ${release_Variables_in_progress}['list_package_manage'].split(','):\n"
                                                                       "        num_version  = releaseVariables[package+'_version']\n"
                                                                       "        ref_name_package = releaseVariables['defintion_'+package.encode('utf-8')]['XLD_PACKAGE_PATERN']\n"
                                                                       "        releaseVariables[package] = ref_name_package.replace('<version>',num_version)\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        if 'id' in reponse.json():
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : GET number version from JENKINS. SKIP mode with precondition : "+ precondition) 
                        else:
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : GET number version from JENKINS. SKIP mode")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'GIVE VALUE TO PACKAGE CHOICE. SKIP mode'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(reponse.content)
                        self.logger_error.error(e)      
    def get_num_version_from_jenkins_skip(self,phase):
        if phase in ['DEV','dynamic_release']:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : False,
                                                            "title" : 'GIVE VALUE TO PACKAGE CHOICE' ,
                                                            "script":  "##get_num_version_from_jenkins_skip\n"
                                                                       "import json\n"  
                                                                       "for package in ${release_Variables_in_progress}['list_package']:\n"
                                                                       "    if releaseVariables[package+'_version'] != ${release_Variables_in_progress}['package_title_choice']:\n"
                                                                       "        num_version  = releaseVariables[package+'_version']\n"
                                                                       "        ref_name_package = releaseVariables['defintion_'+package.encode('utf-8')]['XLD_PACKAGE_PATERN']\n"
                                                                       "        releaseVariables[package+'_version'] = ref_name_package.replace('<version>',num_version)\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        if 'id' in reponse.json():
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : GET number version from JENKINS. SKIP mode with precondition : "+ precondition) 
                        else:
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : GET number version from JENKINS. SKIP mode")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'GIVE VALUE TO PACKAGE CHOICE. SKIP mode'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(reponse.content)
                        self.logger_error.error(e)              
    def reevaluate_variable_package_version(self,phase):
        if phase == 'DEV' or phase == 'UAT' or phase == 'BUILD':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        elif phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : False,
                                                            "title" : 'GIVE VALUE TO PACKAGE CHOICE' ,
                                                            "script":  "##reevaluate_variable_package_version\n"
                                                                       "import json\n"
                                                                       "for build_name in ${release_Variables_in_progress}['list_build_name'].split(','):\n"
                                                                       "    if build_name.split('-')[0] not in ${release_Variables_in_progress}['package_name_from_jenkins'].split(','):\n"
                                                                       "        if not releaseVariables['check_xld_'+build_name.split('-')[0]]:\n"
                                                                       "                ref_name_package = build_name.split('-')[1]\n"
                                                                       "                version = releaseVariables[build_name.split('-')[0]+'_version']\n"
                                                                       "                releaseVariables[build_name.split('-')[0]+'_version'] = ref_name_package.replace('<version>',version)\n"
                                                            },verify = False)              
            reponse.raise_for_status()                                                      
            if reponse.content:
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        if 'id' in reponse.json():
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : GET number version from JENKINS. SKIP mode with precondition : "+ precondition) 
                        else:
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : GET number version from JENKINS. SKIP mode")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'GIVE VALUE TO PACKAGE CHOICE. SKIP mode'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(reponse.content)
                        self.logger_error.error(e)    
    def get_num_version_from_jenkins(self,phase):
        if phase == 'DEV' or phase == 'UAT' or phase == 'BUILD':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        elif phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : False,
                                                            "title" : 'GIVE VALUE TO PACKAGE CHOICE' ,
                                                            "script":  "##get_num_version_from_jenkins\n"
                                                                       "import json\n"
                                                                       "for build_name in ${release_Variables_in_progress}['list_build_name'].split(','):\n"
                                                                       "    if build_name.split('-')[0] not in ${release_Variables_in_progress}['package_name_from_jenkins'].split(','):\n"
                                                                       "        if not releaseVariables['check_xld_'+build_name.split('-')[0]]:\n"
                                                                       "                ref_name_package = build_name.split('-')[1]\n"
                                                                       "                version = releaseVariables[build_name.split('-')[0]+'_version']\n"
                                                                       "                releaseVariables[build_name.split('-')[0]+'_version'] = ref_name_package.replace('<version>',version)\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        if 'id' in reponse.json():
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : GET number version from JENKINS. SKIP mode with precondition : "+ precondition) 
                        else:
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : GET number version from JENKINS. SKIP mode")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'GIVE VALUE TO PACKAGE CHOICE. SKIP mode'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(reponse.content)
                        self.logger_error.error(e)                  
    def get_version_of_the_package_listbox(self,phase):
        if phase == 'DEV' or phase == 'UAT' or phase == 'BUILD':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        elif phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : False,
                                                            "title" : 'GIVE VALUE TO PACKAGE CHOICE' ,
                                                            "script":  "##get_version_of_the_package_listbox\n"
                                                                       "import json\n"
                                                                       "for build_name in ${release_Variables_in_progress}['list_build_name'].split(','):\n"
                                                                       "    if build_name.split('-')[0] in releaseVariables['List_package']:\n"
                                                                       "        if build_name.split('-')[0] not in ${release_Variables_in_progress}['package_name_from_jenkins'].split(','):\n"
                                                                       "                ref_name_package = build_name.split('-')[1]\n"
                                                                       "                version = releaseVariables[package+'_version']\n"
                                                                       "                releaseVariables[package+'_version'] = ref_name_package.replace('<version>',version)\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        if 'id' in reponse.json():
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : GET number version from JENKINS. SKIP mode with precondition : "+ precondition) 
                        else:
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : GET number version from JENKINS. SKIP mode")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'GIVE VALUE TO PACKAGE CHOICE. SKIP mode'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(reponse.content)
                        self.logger_error.error(e)  

    def get_version_of_the_package(self,phase):
        if phase in ['DEV','dynamic_release']:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : False,
                                                            "title" : 'GIVE VALUE TO PACKAGE CHOICE' ,
                                                            "script":  "##get_version_of_the_package\n"
                                                                       "import json\n"
                                                                       "for package in ${list_actif_package_version}:\n"
                                                                       "        for ref_package in ${release_Variables_in_progress}['list_package'].split(','):\n"
                                                                       "            if  package == ref_package.split(',')[0].replace('<version>',''):\n"
                                                                       "                ref_name_package = releaseVariables['defintion_'+package.encode('utf-8')]['XLD_PACKAGE_PATERN']\n"
                                                                       "                version = releaseVariables[package+'_version'].replace(ref_name_package,'')\n"
                                                                       "                releaseVariables[package+'_version'] = version\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        if 'id' in reponse.json():
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : GIVE VALUE TO PACKAGE CHOICE. SKIP mode with precondition : "+ precondition) 
                        else:
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : GIVE VALUE TO PACKAGE CHOICE. SKIP mode")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'GIVE VALUE TO PACKAGE CHOICE. SKIP mode'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(reponse.content)
                        self.logger_error.error(e)
    def task_xlr_if_name_from_jenkins(self,phase):
        if phase == 'DEV' or phase == 'BUILD':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        elif phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'

        reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : False,
                                                            "title" : 'Assign value to VARIABLE_XLR_ID_ for each package' ,
                                                            "script":  "##task_xlr_if_name_from_jenkins\n"
                                                                        "## purpose : \n"
                                                                        "##for package that the XLD application name come from jenkins\n"
                                                                        "## the variable 'VARIABLE_XLR_ID_<package_name>' is use in task jenkins \n"
                                                                        "## in order to send the id of the XLR variable '<package_name>_version' as a parameter : \n"
                                                                        "## through the jenkins jobs, it update the variable at the end of the jenkins job with the xld application verion : \n"
                                                                        "from java.net import URLEncoder\n"
                                                                        "import json\n"
                                                                        "## get id of the current release\n"
                                                                        "current_release = getCurrentRelease()\n"
                                                                        "## for each package define in the list  'package_name_from_jenkins'  \n"
                                                                        "## we search for the key: '<package_name>_version' in the variable current_release which contain all the XLR id variable of the release \n"
                                                                        "## and we assign the 'id' to the variable '<package_name>_version' to XLR variable : 'VARIABLE_XLR_ID_<package_name>'\n"
                                                                        "for package in ${release_Variables_in_progress}['package_name_from_jenkins'].split(','):\n"
                                                                        "        id_package_version = [var.id for var in current_release.variables if var.key == package+'_version' ]\n"
                                                                        "        releaseVariables['VARIABLE_XLR_ID_'+package+'_version'] ='${release.id}/'+id_package_version[0].split('/')[-1]\n"
                                                            },verify = False)

                        

    def task_xlr_transformation_variable_branch(self,phase):
        if phase == 'DEV' or phase == 'BUILD':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        elif phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : False,
                                                            "title" : 'Transformation branch variable' ,
                                                            "script":  "##transformation_variable_branch\n"
                                                                        "from java.net import URLEncoder\n"
                                                                        "import json\n"
                                                                        "myRelease = getCurrentRelease()\n"
                                                                        "for package in  ${release_Variables_in_progress}['package_name_from_jenkins'].split(','):\n"
                                                                        "    version_string = releaseVariables[package + '_version']\n"
                                                                        "    if '/' in releaseVariables[package+'_version']:\n"
                                                                        "      tmp_package_version = URLEncoder.encode(version_string, 'UTF-8')\n"
                                                                        "      releaseVariables[package+'_version'] = tmp_package_version\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        if 'id' in reponse.json():
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'Transformation branch variable'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'Transformation branch variable.'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(reponse.content)
                        self.logger_error.error(e)
                        

    def XLD_directory_evaluation(self,phase):
        if phase in ['DEV','dynamic_release']:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : False,
                                                            "title" : 'XLD_directory_evaluation' ,
                                                            "script":  "##XLD_directory_evaluation\n"
                                                                        "from java.net import URLEncoder\n"
                                                                        "import re\n"
                                                                        "import json\n"
                                                                        "RELEASE_VERSION_REGEX = r'(.*release.*)|(v\d\.\d.*)'\n"
                                                                        "def is_release_version(value):\n"
                                                                        "    match = re.match(RELEASE_VERSION_REGEX, value)\n"
                                                                        "    return match is not None\n"
                                                                        "for package in  ${dict_value_for_template}['package']:\n"
                                                                        "    result = is_release_version(releaseVariables[package + '_version']):\n"
                                                                        "    print(result)\n"
                                                                        "    if result: \n"
                                                                        "       print('package in Release directory in XLD')"
                                                                        "       releaseVariables['TYPEPACKAGE-'+package] = 'Release'\n"
                                                                        "       releaseVariables['TYPEPACKAGE2-'+package] = 'release'\n"
                                                                        "    else:\n"
                                                                        "       print('package in Snapshot directory in XLD')"
                                                                        "       releaseVariables['TYPEPACKAGE-'+package] = 'Snapshot'\n"
                                                                        "       releaseVariables['TYPEPACKAGE2-'+package] = 'snapshot'\n"

                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        if 'id' in reponse.json():
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'XLD_directory_evaluation'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'XLD_directory_evaluation'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(reponse.content)
                        self.logger_error.error(e)
    
    
    def script_jython_xld_undeploy_revaluate_version_package(self,phase,step):
        url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : False,
                                                            "title" : 'Re evaluate version package for undeploy' ,
                                                            "script":  "##script_jython_xld_undeploy_revaluate_version_package\n"
                                                                       "import json\n"
                                                                        "step='"+step+"'\n"
                                                                        "phase_title = getCurrentPhase().title\n"
                                                                        "for package in ${release_Variables_in_progress}['list_auto_undeploy'].split(','):\n"
                                                                        "   if releaseVariables[package+'_version'] == ${release_Variables_in_progress}['package_title_choice']:\n"
                                                                        "      releaseVariables[package+'_version'] = releaseVariables['version_deployed_'+package+'_'+phase_title+'_'+step].split('/')[-1]\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE XLD TASK'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'RE EVALUATION PACKAGE VERSION'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(reponse.content)
                        self.logger_error.error(e)
         
