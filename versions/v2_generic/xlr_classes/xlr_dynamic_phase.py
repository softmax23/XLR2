
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
class XLRDynamicPhase:
    """
    Dynamic phase management for XLR templates.

    This class handles the creation and management of dynamic phases that
    customize the XLR template at runtime based on user selections. It provides:
    - Dynamic phase deletion based on user choices
    - Package filtering and selection
    - Jenkins job management
    - Control-M task customization
    - XLD deployment task filtering
    - Technical task management

    The dynamic phase allows templates to be highly configurable while
    maintaining a clean, focused deployment pipeline. Users can select:
    - Which environments to deploy to
    - Which packages to include
    - Which technical tasks to execute
    - Build and deployment options

    Key functionality:
    - Jython script generation for runtime customization
    - Phase lifecycle management
    - Task filtering and selection
    - Variable management for dynamic behavior
    """
    def script_jython_delete_phase_inc(self,phase):
        if phase == 'dynamic_release':
            url=self.url_api_xlr+''+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+''+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'RELEASE DELETE PHASE' ,
                                                            "script":  "##script_jython_delete_phase_inc\n"
                                                                       "import json\n"
                                                                    "releaseVariables['Release_Email_resquester'] = userApi.getUser('${release.owner}').email\n"
                                                                    "def delete_phase(phases):\n"
                                                                    "           xlr_id_phase_to_delete = phaseApi.searchPhasesByTitle(phase, '${release.id}')\n"
                                                                    "           if len(xlr_id_phase_to_delete) != 0:\n"
                                                                    "               phaseApi.deletePhase(str(xlr_id_phase_to_delete[0]))\n"
                                                                    "list_phase = []\n"  
                                                                    "for phase in  ${dict_value_for_template}['template_liste_phase']:  \n"
                                                                    "   if not releaseVariables[phase]:\n"
                                                                    "       if 'PRODUCTION' in phase:\n"
                                                                    "           list_phase.append('PRODUCTION')\n"
                                                                    "       elif 'BENCH' in phase:\n"
                                                                    "           list_phase.append('BENCH')\n"
                                                                    "           if 'BUILD' in ${dict_value_for_template}['template_liste_phase']\n"
                                                                    "               list_phase.append('BUILD')\n"
                                                                    "\n"
                                                                    "for phase in list_phase:\n"
                                                                    "     delete_phase(phase)\n"
                                                                    "\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'RELEASE DELETE PHASE'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'RELEASE DELETE PHASE'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    def script_jython_define_xld_prefix_new(self,phase):
        if phase in ['DEV','dynamic_release']:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'        
        # url=self.url_api_xlr+'tasks/'+task_id+'/tasks'
        try: 
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'XLD VARIABLE : Defnition Value if MULTIBENCH' ,
                                                            "script":  "##script_jython_define_xld_prefix_new\n"
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
                                                                       "   releaseVariables['BENCH_APPCODE'] = releaseVariables['env_BENCH'].split('_')[0]\n"
                                                                       },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'XLD VARIABLE : Defnition Value if MULTIBENCH'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'XLD VARIABLE : Defnition Value if MULTIBENCH'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    def script_jython_dynamic_delete_task_controlm(self,phase):
        if phase in ['DEV','dynamic_release']:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'DELETE CONTROL-M TASK WITH MASTER OPTION' ,
                                                            "script":  "##script_jython_dynamic_delete_task_controlm\n"
                                                                       "import json\n"
                                                                       "def delete_task(phase,title):\n"
                                                                       "    taskstodelete = taskApi.searchTasksByTitle(title,phase,'${release.id}')\n"
                                                                       "    if len(taskstodelete) != 0:\n"
                                                                       "        taskApi.delete(str(taskstodelete[0]))\n"
                                                                       "        return 'Phase : '+phase+' --- Delete Task : "'+ title+'"' \n"
                                                                       "  \n"
                                                                       "## Test if in releaseVariables['release_Variables_in_progress']['list_package_manage'] at the start of the release is in the list of releaseVariables['release_Variables_in_progress']['package_master']\n"
                                                                       "## If TRUE, we keep controlm task  associed only to CONTROLM folder link to packages master list \n"
                                                                       "##     \n" 
                                                                       "## if FALSE( there is no package from 'package_master' list in  'list_package_manage' )    \n" 
                                                                       "##    so the jython will delete only CONTROLM task link o package define in variable\n" 
                                                                       "##     \n" 
                                                                       "package_master_active = any(item in releaseVariables['release_Variables_in_progress']['list_package_manage'].split(',') for item in releaseVariables['release_Variables_in_progress']['package_master'].split(','))\n"
                                                                       "##     \n" 
                                                                       "## we loop on each phase define in releaseVariables['release_Variables_in_progress']['xlr_list_phase']\n" 
                                                                       "##   we will delete CONTROLM task   \n" 
                                                                        "for phase in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(','):\n"
                                                                        "       if phase != 'BUILD' and phase != 'UAT' and phase != 'DEV' and 'CREATE_CHANGE_' not in phase:\n"
                                                                        "           count_titlegroup = 0 \n"
                                                                        "           if package_master_active: \n"
                                                                        "               for titlegroup  in releaseVariables['template_list_controlm_'+phase]:\n"
                                                                        "                   listfolder_delete = [] \n"
                                                                        "                   listfolder = [] \n"
                                                                        "                   for item in releaseVariables['template_list_controlm_'+phase][titlegroup].split(','):\n"
                                                                        "                       listpackfolder = []\n"
                                                                        "                       listfolder.append(item.split('-')[0]) \n"
                                                                        "                       for pack in item.split('-')[1:]:\n"
                                                                        "                           listpackfolder.append(pack.encode('utf-8'))\n"
                                                                        "                       check = all(item not in listpackfolder for item in releaseVariables['release_Variables_in_progress']['package_master'].split(','))\n"
                                                                        "                       if check:\n"
                                                                        "                               listfolder_delete.append(item.split('-')[0])\n"
                                                                        "                               print(delete_task('CREATE_CHANGE_'+phase,title = 'CONTROLM : ' + item.split('-')[0]))\n"
                                                                        "                               print(delete_task(phase,title =  item.split('-')[0]))\n"
                                                                        "                   if len(listfolder_delete) == len(listfolder):\n"
                                                                        "                           print(delete_task(phase,title =  'CONTROLM : '+ titlegroup))\n"
                                                                        "                           count_titlegroup += 1 \n"
                                                                        "           else:\n"
                                                                        "                   for titlegroup  in releaseVariables['template_list_controlm_'+phase]:\n"
                                                                        "                       listfolder_delete = [] \n"
                                                                        "                       listfolder = [] \n"
                                                                        "                       for item in releaseVariables['template_list_controlm_'+phase][titlegroup].split(','):\n"
                                                                        "                           listpackfolder = []\n"
                                                                        "                           listfolder.append(item.split('-')[0])\n"
                                                                        "                           for pack in item.split('-')[1:]:\n"
                                                                        "                               listpackfolder.append(pack.encode('utf-8'))\n"
                                                                        "                           check = all(item not in listpackfolder for item in releaseVariables['release_Variables_in_progress']['list_package_manage'].split(','))\n"
                                                                        "                           if check:\n"
                                                                        "                               listfolder_delete.append(item.split('-')[0])\n"
                                                                        "                               print(delete_task('CREATE_CHANGE_'+phase,title = 'CONTROLM : ' + item.split('-')[0]))\n"
                                                                        "                               print(delete_task(phase,title =  item.split('-')[0]))\n"
                                                                        "                       if len(listfolder_delete) == len(listfolder):\n"
                                                                        "                               print(delete_task(phase,title = 'CONTROLM : '+ titlegroup))\n"
                                                                        "                               count_titlegroup += 1 \n"
                                                                        "           if len(releaseVariables['template_list_controlm_'+phase.encode('utf-8')]) == count_titlegroup:\n"
                                                                        "            print(delete_task(phase,title =  'Please enter user password for controlm on '+ phase.encode('utf-8')))\n"
                                                                       "       if len(releaseVariables['release_Variables_in_progress']['list_package_manage'].split(',')) == 0:\n"
                                                                       "            for phase in ['BENCH','PRODUCTION']:\n"
                                                                       "                print(delete_task(phase,title =  'Please enter user password for controlm on '+ phase.encode('utf-8')))\n"
                                                                    "       \n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE CONTROL-M TASK WITH MASTER OPTION'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE CONTROL-M TASK WITH MASTER OPTION'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    def script_jython_dynamic_delete_task_controlm_multibench(self,phase):
        if phase in ['DEV','dynamic_release']:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'DELETE CONTROL-M TASK WITH MASTER OPTION AND BENCH MULTI' ,
                                                            "script":  "##script_jython_dynamic_delete_task_controlm_multibench\n"
                                                                       "import json\n"
                                                                       "def delete_task(phase,title):\n"
                                                                       "    taskstodelete = taskApi.searchTasksByTitle(title,phase,'${release.id}')\n"
                                                                       "    if len(taskstodelete) != 0:\n"
                                                                       "        taskApi.delete(str(taskstodelete[0]))\n"
                                                                       "        return 'Phase : '+phase+' --- Delete Task : "'+ title+'"' \n"
                                                                       "  \n"
                                                                       "## Test if in releaseVariables['release_Variables_in_progress']['list_package_manage'] at the start of the release is in the list of releaseVariables['release_Variables_in_progress']['package_master']\n"
                                                                       "## If TRUE, we keep controlm task  associed only to CONTROLM folder link to packages master list \n"
                                                                       "##     \n" 
                                                                       "## if FALSE( there is no package from 'package_master' list in  'list_package_manage' )    \n" 
                                                                       "##    so the jython will delete only CONTROLM task link o package define in variable releaseVariables['dict_value_for_template']\n" 
                                                                       "##     \n" 
                                                                       "package_master_active = any(item in releaseVariables['release_Variables_in_progress']['list_package_manage'].split(',') for item in releaseVariables['release_Variables_in_progress']['package_master'].split(','))\n"
                                                                       "##     \n" 
                                                                       "## we loop on each phase define in releaseVariables['release_Variables_in_progress']['xlr_list_phase']\n" 
                                                                       "##   we will delete CONTROLM task   \n" 
                                                                        "for phase in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(','):\n"
                                                                        "       if phase != 'BUILD' and phase != 'UAT' and phase != 'DEV' and 'CREATE_CHANGE_' not in phase:\n"
                                                                        "           count_titlegroup = 0 \n"
                                                                        "           if package_master_active: \n"
                                                                        "               for titlegroup  in releaseVariables['template_list_controlm_'+phase]:\n"
                                                                        "                   listfolder_delete = [] \n"
                                                                        "                   listfolder = [] \n"
                                                                        "                   for item in releaseVariables['template_list_controlm_'+phase][titlegroup].split(','):\n"
                                                                        "                       listpackfolder = []\n"
                                                                        "                       listfolder.append(item.split('-')[0]) \n"
                                                                        "                       for pack in item.split('-')[1:]:\n"
                                                                        "                           listpackfolder.append(pack.encode('utf-8'))\n"
                                                                        "                       check = all(item not in listpackfolder for item in releaseVariables['release_Variables_in_progress']['package_master'].split(','))\n"
                                                                        "                       if check:\n"
                                                                        "                               listfolder_delete.append(item.split('-')[0])\n"
                                                                        "                               print(delete_task('CREATE_CHANGE_'+phase,title = 'CONTROLM : ' + item.split('-')[0]))\n"
                                                                        "                               print(delete_task(phase,title =  item.split('-')[0]))\n"
                                                                        "                   if len(listfolder_delete) == len(listfolder):\n"
                                                                        "                           print(delete_task(phase,title =  'CONTROLM : '+ titlegroup))\n"
                                                                        "                           count_titlegroup += 1 \n"
                                                                        "           else:\n"
                                                                        "                   for titlegroup  in releaseVariables['template_list_controlm_'+phase]:\n"
                                                                        "                       listfolder_delete = [] \n"
                                                                        "                       listfolder = [] \n"
                                                                        "                       for item in releaseVariables['template_list_controlm_'+phase][titlegroup].split(','):\n"
                                                                        "                           listpackfolder = []\n"
                                                                        "                           listfolder.append(item.split('-')[0])\n"
                                                                        "                           for pack in item.split('-')[1:]:\n"
                                                                        "                               listpackfolder.append(pack.encode('utf-8'))\n"
                                                                        "                           check = all(item not in listpackfolder for item in releaseVariables['release_Variables_in_progress']['list_package_manage'].split(','))\n"
                                                                        "                           if check:\n"
                                                                        "                               listfolder_delete.append(item.split('-')[0])\n"
                                                                        "                               print(delete_task('CREATE_CHANGE_'+phase,title = 'CONTROLM : ' + item.split('-')[0]))\n"
                                                                        "                               print(delete_task(phase,title =  item.split('-')[0]))\n"
                                                                        "                       if len(listfolder_delete) == len(listfolder):\n"
                                                                        "                               print(delete_task(phase,title = 'CONTROLM : '+ titlegroup))\n"
                                                                        "                               count_titlegroup += 1 \n"
                                                                        "           if len(releaseVariables['template_list_controlm_'+phase.encode('utf-8')]) == count_titlegroup:\n"
                                                                        "            print(delete_task(phase,title =  'Please enter user password for controlm on '+ phase.encode('utf-8')))\n"
                                                                       "       if len(releaseVariables['release_Variables_in_progress']['list_package_manage'].split(',')) == 0:\n"
                                                                       "            for phase in ['BENCH','PRODUCTION']:\n"
                                                                       "                print(delete_task(phase,title =  'Please enter user password for controlm on '+ phase.encode('utf-8')))\n"
                                                                        
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE CONTROL-M TASK WITH MASTER OPTION AND BENCH MULTI'. When 'XLD_ENV_BENCH' > 2")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE CONTROL-M TASK WITH MASTER OPTION AND BENCH MULTI'. When 'XLD_ENV_BENCH' > 2")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    def script_jython_dynamic_delete_task_controlm_package_listbox(self,phase):
        if phase in ['DEV','dynamic_release']:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'DELETE CONTROL-M TASK' ,
                                                            "script":   "##script_jython_dynamic_delete_task_controlm_package_listbox\n"
                                                                        "import json\n"
                                                                        "def delete_task(phase,title):\n"
                                                                        "    taskstodelete = taskApi.searchTasksByTitle(title,phase,'${release.id}')\n"
                                                                        "    if len(taskstodelete) != 0:\n"
                                                                        "        taskApi.delete(str(taskstodelete[0]))\n"
                                                                        "        return 'Phase : '+phase+' --- Delete Task : + title+' \n"
                                                                        "     \n"
                                                                        "package_master_active = any(item in releaseVariables['List_package'] for item in releaseVariables['release_Variables_in_progress']['package_master'].split(','))\n"
                                                                        "for phase in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(','):\n"
                                                                        "       if phase != 'BUILD' and phase != 'UAT' and phase != 'DEV' and 'CREATE_CHANGE_' not in phase:\n"
                                                                        "           count_titlegroup = 0 \n"
                                                                        "           if package_master_active: \n"
                                                                        "               for titlegroup  in releaseVariables['template_list_controlm_'+phase]:\n"
                                                                        "                   listfolder_delete = [] \n"
                                                                        "                   listfolder = [] \n"
                                                                        "                   for item in releaseVariables['template_list_controlm_'+phase][titlegroup].split(','):\n"
                                                                        "                       listpackfolder = []\n"
                                                                        "                       listfolder.append(item.split('-')[0]) \n"
                                                                        "                       for pack in item.split('-')[1:]:\n"
                                                                        "                           listpackfolder.append(pack.encode('utf-8'))\n"
                                                                        "                       check = all(item not in listpackfolder for item in releaseVariables['release_Variables_in_progress']['package_master'].split(','))\n"
                                                                        "                       if check:\n"
                                                                        "                               listfolder_delete.append(item.split('-')[0])\n"
                                                                        "                               print(delete_task('CREATE_CHANGE_'+phase,title = 'CONTROLM : ' + item.split('-')[0]))\n"
                                                                        "                               print(delete_task(phase,title =  item.split('-')[0]))\n"
                                                                        "                   if len(listfolder_delete) == len(listfolder):\n"
                                                                        "                       print(delete_task(phase,title =  'CONTROLM : '+ titlegroup))\n"
                                                                        "                       count_titlegroup += 1 \n"
                                                                        "           else:\n"
                                                                        "                   for titlegroup  in releaseVariables['template_list_controlm_'+phase]:\n"
                                                                        "                       listfolder_delete = [] \n"
                                                                        "                       listfolder = [] \n"
                                                                        "                       for item in releaseVariables['template_list_controlm_'+phase][titlegroup].split(','):\n"
                                                                        "                           listpackfolder = []\n"
                                                                        "                           listfolder.append(item.split('-')[0])\n"
                                                                        "                           for pack in item.split('-')[1:]:\n"
                                                                        "                               listpackfolder.append(pack.encode('utf-8'))\n"
                                                                        "                           check = all(item not in listpackfolder for item in releaseVariables['List_package'])\n"
                                                                        "                           if check:\n"
                                                                        "                               listfolder_delete.append(item.split('-')[0])\n"
                                                                        "                               print(delete_task('CREATE_CHANGE_'+phase,title = 'CONTROLM : ' + item.split('-')[0]))\n"
                                                                        "                               print(delete_task(phase,title =  item.split('-')[0]))\n"
                                                                        "                   if len(listfolder_delete) == len(listfolder):\n"
                                                                        "                       print(delete_task(phase,title = 'CONTROLM : '+ titlegroup))\n"
                                                                        "                       count_titlegroup += 1 \n"
                                                                        "           if len(releaseVariables['template_list_controlm_'+phase.encode('utf-8')]) == count_titlegroup:\n"
                                                                        "            print(delete_task(phase,title =  'Please enter user password for controlm on '+ phase.encode('utf-8')))\n"
                                                                        "       if len(releaseVariables['List_package']) == 0:\n"
                                                                        "            for phase in ['BENCH','PRODUCTION']:\n"
                                                                        "                print(delete_task(phase,title =  'Please enter user password for controlm on '+ phase.encode('utf-8')))\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE CONTROL-M TASK WITH MASTER OPTION AND BENCH MULTI'. When 'XLD_ENV_BENCH' > 2")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE CONTROL-M TASK WITH MASTER OPTION AND BENCH MULTI'. When 'XLD_ENV_BENCH' > 2")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    def script_jython_dynamic_delete_task_jenkins_listbox(self,phase):
        if phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'DELETE JENKINS TASK' ,
                                                            "script":  "##script_jython_dynamic_delete_task_jenkins_listbox\n"
                                                                       "import json\n"
                                                                    "for package in releaseVariables['release_Variables_in_progress']['list_package'].split(','):\n"
                                                                    "   if package not in releaseVariables['List_package']: \n"
                                                                    "       for phase in ['DEV','BUILD']:\n"
                                                                    "               title_jenkins_task = 'Jenkins '+package\n"
                                                                    "               xlr_id_task_to_delete = taskApi.searchTasksByTitle(title_jenkins_task, phase, '${release.id}')\n"
                                                                    "               if len(xlr_id_task_to_delete) != 0:\n"
                                                                    "                   taskApi.delete(str(xlr_id_task_to_delete[0]))\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE JENKINS TASK'. Jenkins == listbox")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE JENKINS TASK'. Jenkins == listbox")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    def script_jython_dynamic_delete_task_jenkins_string(self,phase):
        if phase == 'DEV' or phase == 'BUILD' :
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        elif phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'DELETE JENKINS TASK' ,
                                                            "script":  "##script_jython_dynamic_delete_task_jenkins_string\n"
                                                                        "import json\n"
                                                                        "for package in releaseVariables['release_Variables_in_progress']['list_package'].split(','):\n"
                                                                        "    if package.encode('utf-8') not in releaseVariables['release_Variables_in_progress']['list_package_manage'].split(','): \n"
                                                                        "        title_jenkins_task = 'Jenkins '+package.encode('utf-8')\n"
                                                                        "        xlr_id_task_to_delete = taskApi.searchTasksByTitle(title_jenkins_task, 'DEV', '${release.id}')\n"
                                                                        "        if len(xlr_id_task_to_delete) != 0:\n"
                                                                        "           taskApi.delete(str(xlr_id_task_to_delete[0]))\n"
                                                                        "if len(releaseVariables['release_Variables_in_progress']['list_package_manage']) == 0: \n"
                                                                        "   if 'DEV' in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(','):\n"
                                                                        "       print(delete_task(phase,'Jenkins JOBS'))\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE JENKINS TASK'. DEV in phases list")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE JENKINS TASK'. DEV in phases list")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
    def script_jython_dynamic_delete_task_xld(self,phase):
        if phase in ['DEV','dynamic_release']:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'DELETE XLD TASK' ,
                                                            "script":  "##script_jython_dynamic_delete_task_xld\n"
                                                                       "import json\n"
                                                                    "list_package_to_not_undeploy = [] \n"
                                                                    "list_package_package_name_from_jenkins = []\n"
                                                                    "### function to delete a task XLR, it work with name phase and the title of the task\n"
                                                                    "def delete_task(phase,title):\n"
                                                                    "    taskstodelete = taskApi.searchTasksByTitle(title,phase,'${release.id}')\n"
                                                                    "    if len(taskstodelete) != 0:\n"
                                                                    "        taskApi.delete(str(taskstodelete[0]))\n"
                                                                    "        return 'Phase : '+phase+' --- Delete Task : "'+ title+'"' \n"
                                                                    "     \n"
                                                                    "if releaseVariables['release_Variables_in_progress']['auto_undeploy'] != '':\n"
                                                                    "   for item in releaseVariables['release_Variables_in_progress']['auto_undeploy'].split(','):\n"
                                                                    "               key = item.split(':')[0]\n"
                                                                    "               value = item.split(':')[1]\n"
                                                                    "               if '-' in value or value != 'yes':\n"
                                                                    "                   valuesplit = value.split('-')\n"
                                                                    "                   for value2 in valuesplit:\n"
                                                                    "                       if value2 in releaseVariables['release_Variables_in_progress']['list_package_manage'].split(','):\n"
                                                                    "                               list_package_to_not_undeploy.append(key)\n"
                                                                    "               elif value.encode('utf-8') == 'yes':\n"
                                                                    "                               list_package_to_not_undeploy.append(key.encode('utf-8'))\n"
                                                                    "for phase in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(','):\n"
                                                                    "    if 'BUILD' not in phase:\n"
                                                                    "        for pack in releaseVariables['release_Variables_in_progress']['list_package'].split(','):\n"
                                                                    "               if pack not in list_package_to_not_undeploy: \n"
                                                                    "                   if pack not in releaseVariables['release_Variables_in_progress']['list_package_manage'].split(','):\n"
                                                                    "                       print(delete_task(phase,'Deploy '+pack.encode('utf-8')))\n"
                                                                    "                       print(delete_task('CREATE_CHANGE_'+phase,'XLD-Deploy '+pack.encode('utf-8')))\n"
                                                                    "        list_package_really_undeploy = [] \n"
                                                                    "        for pack in releaseVariables['release_Variables_in_progress']['list_auto_undeploy'].split(','):\n"
                                                                    "           if pack not in list_package_to_not_undeploy:\n"
                                                                    "                    list_package_really_undeploy.append(pack)\n"
                                                                    "                    print(delete_task(phase,'Undeploy '+pack.encode('utf-8')))\n"
                                                                    "        for pack in releaseVariables['release_Variables_in_progress']['list_package_not_manage'].split(','):\n"
                                                                    "              print(delete_task(phase,'Check XLD package exist '+pack.encode('utf-8')))\n"
                                                                    "              if pack in releaseVariables['release_Variables_in_progress']['package_name_from_jenkins'].split(','):\n"
                                                                    "                list_package_package_name_from_jenkins.append(pack)\n"
                                                                    "        if len(list_package_really_undeploy) != 0: \n"
                                                                    "           if len(list_package_really_undeploy) == len(releaseVariables['release_Variables_in_progress']['list_auto_undeploy'].split(',')):\n"
                                                                    "               print(delete_task(phase,'Delete undeploy if necessary'))\n"
                                                                    "               print(delete_task(phase,'Re evaluate version package for undeploy'))\n"
                                                                    "               print(delete_task(phase,'Check Version package in XLD BEFORE'))\n"
                                                                    "        if len(list_package_package_name_from_jenkins) != 0: \n"
                                                                    "           if len(list_package_package_name_from_jenkins) == len(releaseVariables['release_Variables_in_progress']['package_name_from_jenkins'].split(',')):\n"
                                                                    "               print(delete_task(phase,'Check if XLD package exist'))\n"
                                                                    "               print(delete_task(phase,'Delete jenkins task if package ever exist in XLD'))\n"
                                                                    "               print(delete_task(phase,'Transformation branch variable'))\n"
                                                                    "        if len(releaseVariables['release_Variables_in_progress']['list_package_manage']) == 0: \n"
                                                                    "                   print(delete_task('CREATE_CHANGE_'+phase,'XLD DEPLOY'))\n"
                                                                    "                   print(delete_task(phase,'XLD DEPLOY'))\n"
                                                                    "                   print(delete_task(phase,'Please enter user password for xldeploy on '+phase))\n"
                                                                    "\n"
                                                                    "\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE XLD TASK'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE XLD TASK'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(reponse.content)
                        self.logger_error.error(e)
    def script_jython_dynamic_controlm_spec(self,phase):
        if phase in ['DEV','dynamic_release']:
            url_dynamic_controlm_spec=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url_dynamic_controlm_spec=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse_dynamic_controlm_spec= requests.post(url_dynamic_controlm_spec, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'DELETE CONTROLM SPEC' ,
                                                            "script":  "##script_jython_dynamic_controlm_spec\n"  
                                                                       "import json\n"
                                                                    "for phase in releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection'].split(','):\n"
                                                                    "    if 'BUILD' not in phase:\n"
                                                                    "       if 'CREATE_CHANGE' in phase:\n"
                                                                    "           nphase = phase.split('CREATE_CHANGE_')[-1]\n"
                                                                    "       else: \n"
                                                                    "           nphase = phase\n"
                                                                    "    for folder in ${dict_value_for_template}['controlmspec'][nphase]:\n"
                                                                    "       controlmspec_active = 'no' \n"
                                                                    "       for value in ${dict_value_for_template}['controlmspec'][nphase][folder]:\n"
                                                                    "               if value != '':\n"
                                                                    "                   controlmspec_active = 'yes' \n"
                                                                    "       if  controlmspec_active == 'yes':    \n"
                                                                    "           task_xld_phase = 'CONTROLM :'+folder\n"
                                                                    "           xlr_id_task_to_delete = taskApi.searchTasksByTitle(task_xld_phase, phase, '${release.id}')\n"
                                                                    "           if len(xlr_id_task_to_delete) != 0:\n"
                                                                    "               taskApi.delete(str(xlr_id_task_to_delete[0]))\n"
                                                            },verify = False)
            reponse_dynamic_controlm_spec.raise_for_status()
            if reponse_dynamic_controlm_spec.content:
                    if 'id' in reponse_dynamic_controlm_spec.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE XLD TASK'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE XLD TASK'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url_dynamic_controlm_spec)
                        self.logger_error.error(reponse_dynamic_controlm_spec.content)
                        self.logger_error.error(e)
    def script_jython_dynamic_delete_task_xld_CAB(self,phase):
        if phase in ['DEV','dynamic_release']:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'DELETE XLD TASK' ,
                                                            "script":  "##script_jython_dynamic_delete_task_xld_CAB\n"
                                                                       "import json\n"
                                                                       "def delete_task(phase,title):\n"
                                                                       "    taskstodelete = taskApi.searchTasksByTitle(title,phase,'${release.id}')\n"
                                                                       "    if len(taskstodelete) != 0:\n"
                                                                       "        taskApi.delete(str(taskstodelete[0]))\n"
                                                                       "        return 'Phase : '+phase+' --- Delete Task : "'+ title+'"' \n"
                                                                       "     \n"
                                                                       "for pack in releaseVariables['release_Variables_in_progress']['list_package_not_manage'].split(','):\n"    
                                                                       "   print(delete_task('PRODUCTION','Deploy '+pack.encode('utf-8')))\n"
                                                                       "   print(delete_task('CREATE_CHANGE_PRODUCTION','XLD-Deploy '+pack.encode('utf-8')))\n"                                                                
                                                                             },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE XLD TASK'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE XLD TASK'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(reponse.content)
                        self.logger_error.error(e)
    def script_jython_dynamic_delete_task_xld_APPCODE(self,phase):
        if phase in ['DEV','dynamic_release']:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'DELETE XLD TASK' ,
                                                            "script":  "##script_jython_dynamic_delete_task_xld_APPCODE\n"
                                                                       "import json\n"
                                                                       "list_package_to_not_undeploy = [] \n"
                                                                       "list_package_package_name_from_jenkins = []\n"
                                                                       "### function to delete a task XLR, it work with name phase and the title of the task\n"
                                                                       "def delete_task(phase,title):\n"
                                                                       "    taskstodelete = taskApi.searchTasksByTitle(title,phase,'${release.id}')\n"
                                                                       "    if len(taskstodelete) != 0:\n"
                                                                       "        taskApi.delete(str(taskstodelete[0]))\n"
                                                                       "        return 'Phase : '+phase+' --- Delete Task : "'+ title+'"' \n"
                                                                       "     \n"
                                                                       "if 'BENCH' in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(','):\n"
                                                                       "   releaseVariables['BENCH_APPCODE'] = releaseVariables['env_BENCH']\n"
                                                                       "### Creation of a list 'list_package_to_not_undeploy' \n"
                                                                       "### below the format of the value 'auto_undeploy' in variable XLR 'dict_value_for_template'  \n"
                                                                       "### PACKAGE_UNDEPLOY , value of package name to undeploy \n"
                                                                       "### and after the list of package when it must be undeploy \n"
                                                                       "### The value of PACKAGE_UNDEPLOY must be in in key list_auto_undeploy in variable XLR 'dict_value_for_template'\n"
                                                                       "###  in the case below SDK must be undeploy when App is inthe list of package to deploy by the release\n"
                                                                       "### 'auto_undeploy': [\n"
                                                                       "###                     \n"
                                                                       "###                         'PACKAGE_UNDEPLOY': 'PACKAGE1-PACKAGE2'\n"
                                                                       "###                     ,\n"
                                                                       "###                     \n"
                                                                       "###                         'SDK': 'App'\n"
                                                                       "###                     \n"
                                                                       "###                 ]\n"
                                                                       "for item in releaseVariables['release_Variables_in_progress']['auto_undeploy'].split(','):\n"
                                                                       "               key = item.split(':')[0]\n"
                                                                       "               value = item.split(':')[1]\n"
                                                                       "               if '-' in value or value != 'yes':\n"
                                                                       "                   valuesplit = value.split('-')\n"
                                                                       "                   for value2 in valuesplit:\n"
                                                                       "                       if value2 in releaseVariables['release_Variables_in_progress']['list_package_manage'].split(','):\n"
                                                                       "                               list_package_to_not_undeploy.append(key)\n"
                                                                       "               elif value.encode('utf-8') == 'yes':\n"
                                                                       "                               list_package_to_not_undeploy.append(key.encode('utf-8'))\n"
                                                                       "### on each phase we will delete task XLD specific at the demand \n"
                                                                       "for phase in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(','):\n"
                                                                       "    if 'BUILD' not in phase:\n"
                                                                       "        for pack in releaseVariables['release_Variables_in_progress']['list_package'].split(','):\n"
                                                                       "               if pack not in list_package_to_not_undeploy: \n"
                                                                       "                   if pack not in releaseVariables['release_Variables_in_progress']['list_package_manage'].split(','):\n"
                                                                       "                       print(delete_task(phase,'Deploy '+pack.encode('utf-8')))\n"
                                                                       "                       print(delete_task('CREATE_CHANGE_'+phase,'XLD-Deploy '+pack.encode('utf-8')))\n"
                                                                       "        list_package_really_undeploy = [] \n"
                                                                       "        for pack in releaseVariables['release_Variables_in_progress']['list_auto_undeploy'].split(','):\n"
                                                                       "           if pack not in list_package_to_not_undeploy:\n"
                                                                       "                    list_package_really_undeploy.append(pack)\n"
                                                                       "                    print(delete_task(phase,'Undeploy '+pack.encode('utf-8')))\n"
                                                                       "        for pack in releaseVariables['release_Variables_in_progress']['list_package_not_manage'].split(','):\n"
                                                                       "              print(delete_task(phase,'Check XLD package exist '+pack.encode('utf-8')))\n"
                                                                       "              if pack in releaseVariables['release_Variables_in_progress']['package_name_from_jenkins'].split(','):\n"
                                                                       "                list_package_package_name_from_jenkins.append(pack)\n"
                                                                       "        if len(list_package_really_undeploy) == len(releaseVariables['release_Variables_in_progress']['list_auto_undeploy'].split(',')):\n"
                                                                       "            print(delete_task(phase,'Delete undeploy if necessary'))\n"
                                                                       "            print(delete_task(phase,'Re evaluate version package for undeploy'))\n"
                                                                       "            print(delete_task(phase,'Check Version package in XLD BEFORE'))\n"
                                                                       "        if len(list_package_package_name_from_jenkins) == len(releaseVariables['release_Variables_in_progress']['package_name_from_jenkins'].split(',')):\n"
                                                                       "            print(delete_task(phase,'Check if XLD package exist'))\n"
                                                                       "            print(delete_task(phase,'Delete jenkins task if package ever exist in XLD'))\n"
                                                                       "            print(delete_task(phase,'Transformation branch variable'))\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE XLD TASK'. APPCODE in IUA ")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE XLD TASK'. APPCODE in IUA")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
    def script_jython_dynamic_delete_task_xld_listbox(self,phase):
        if phase in ['DEV','dynamic_release']:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'DELETE XLD TASK' ,
                                                            "script":  "##script_jython_dynamic_delete_task_xld_listbox\n"
                                                                       "import json\n"
                                                                       "list_package_to_not_undeploy = [] \n"
                                                                       "list_package_package_name_from_jenkins = []\n"
                                                                       "### function to delete a task XLR, it work with name phase and the title of the task\n"
                                                                       "def delete_task(phase,title):\n"
                                                                       "    taskstodelete = taskApi.searchTasksByTitle(title,phase,'${release.id}')\n"
                                                                       "    if len(taskstodelete) != 0:\n"
                                                                       "        taskApi.delete(str(taskstodelete[0]))\n"
                                                                       "        return 'Phase : '+phase+' --- Delete Task : "'+ title+'"' \n"
                                                                       "     \n"
                                                                       "if 'BENCH' in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(','):\n"
                                                                       "   releaseVariables['BENCH_APPCODE'] = releaseVariables['env_BENCH']\n"
                                                                       "### Creation of a list 'list_package_to_not_undeploy' \n"
                                                                       "### below the format of the value 'auto_undeploy' in variable XLR 'dict_value_for_template'  \n"
                                                                       "### PACKAGE_UNDEPLOY , value of package name to undeploy \n"
                                                                       "### and after the list of package when it must be undeploy \n"
                                                                       "### The value of PACKAGE_UNDEPLOY must be in in key list_auto_undeploy in variable XLR 'dict_value_for_template'\n"
                                                                       "###  in the case below SDK must be undeploy when App is inthe list of package to deploy by the release\n"
                                                                       "### 'auto_undeploy': [\n"
                                                                       "###                     \n"
                                                                       "###                         'PACKAGE_UNDEPLOY': 'PACKAGE1-PACKAGE2'\n"
                                                                       "###                     ,\n"
                                                                       "###                     \n"
                                                                       "###                         'SDK': 'App'\n"
                                                                       "###                     \n"
                                                                       "###                 ]\n"
                                                                       "for item in releaseVariables['release_Variables_in_progress']['auto_undeploy'].split(','):\n"
                                                                       "               key = item.split(':')[0]\n"
                                                                       "               value = item.split(':')[1]\n"
                                                                       "               if '-' in value or value != 'yes':\n"
                                                                       "                   valuesplit = value.split('-')\n"
                                                                       "                   for value2 in valuesplit:\n"
                                                                       "                       if value2 in releaseVariables['List_package']:\n"
                                                                       "                               list_package_to_not_undeploy.append(key)\n"
                                                                       "               elif value.encode('utf-8') == 'yes':\n"
                                                                       "                               list_package_to_not_undeploy.append(key.encode('utf-8'))\n"
                                                                       "### on each phase we will delete task XLD specific at the demand \n"
                                                                       "for phase in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(','):\n"
                                                                       "    if 'BUILD' not in phase:\n"
                                                                       "        for pack in releaseVariables['release_Variables_in_progress']['list_package'].split(','):\n"
                                                                       "               if pack not in list_package_to_not_undeploy: \n"
                                                                       "                   if pack not in releaseVariables['List_package']:\n"
                                                                       "                       print(delete_task(phase,'Deploy '+pack.encode('utf-8')))\n"
                                                                       "                       print(delete_task('CREATE_CHANGE_'+phase,'XLD-Deploy '+pack.encode('utf-8')))\n"
                                                                       "        list_package_really_undeploy = [] \n"
                                                                       "        for pack in releaseVariables['release_Variables_in_progress']['list_auto_undeploy'].split(','):\n"
                                                                       "           if pack not in list_package_to_not_undeploy:\n"
                                                                       "                    list_package_really_undeploy.append(pack)\n"
                                                                       "                    print(delete_task(phase,'Undeploy '+pack.encode('utf-8')))\n"
                                                                       "        for pack in releaseVariables['release_Variables_in_progress']['package_name_from_jenkins'].split(','):\n"
                                                                       "            if pack not in releaseVariables['List_package']:\n"
                                                                       "              print(delete_task(phase,'Check XLD package exist '+pack.encode('utf-8')))\n"
                                                                       "              if pack in releaseVariables['release_Variables_in_progress']['package_name_from_jenkins'].split(','):\n"
                                                                       "                list_package_package_name_from_jenkins.append(pack)\n"
                                                                       "        if len(list_package_really_undeploy) == len(releaseVariables['release_Variables_in_progress']['list_auto_undeploy'].split(',')):\n"
                                                                       "            print(delete_task(phase,'Delete undeploy if necessary'))\n"
                                                                       "            print(delete_task(phase,'Re evaluate version package for undeploy'))\n"
                                                                       "            print(delete_task(phase,'Check Version package in XLD BEFORE'))\n"
                                                                       "        if len(list_package_package_name_from_jenkins) == len(releaseVariables['release_Variables_in_progress']['package_name_from_jenkins'].split(',')):\n"
                                                                       "            print(delete_task(phase,'Check if XLD package exist'))\n"
                                                                       "            print(delete_task(phase,'Delete jenkins task if package ever exist in XLD'))\n"
                                                                       "            print(delete_task(phase,'Transformation branch variable'))\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE XLD TASK'. APPCODE in IUA ")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE XLD TASK'. APPCODE in IUA")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
    def script_jython_dynamic_no_dev_phase_mode_skip(self,phase):
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
                                                            "script":  "##script_jython_dynamic_no_dev_phase_mode_skip\n"
                                                                       "import json\n"
                                                                    "if releaseVariables['env_DEV'] == '':\n"
                                                                    "   for  buildtype in releaseVariables['release_Variables_in_progress']['template_liste_package'].split(','): \n"
                                                                    "      for template_package in  releaseVariables['release_Variables_in_progress']['list_package_manage'].split(','):\n"
                                                                    "         if buildtype == template_package.split(',')[0]: \n"
                                                                    "           package = template_package.split(',')[1].split('<version>')[0]\n"
                                                                    "           releaseVariables[buildtype+'_version'] = releaseVariables[buildtype+'_version'].split(package)[1]\n"
                                                                    "       \n"

                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        if self.parameters['general_info']['type_template'] == 'SKIP':
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'GIVE VALUE TO PACKAGE CHOICE. SKIP mode' with precondition : "+ precondition)
                        else:
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'GIVE VALUE TO PACKAGE CHOICE. SKIP mode'")
                              
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'GIVE VALUE TO PACKAGE CHOICE. SKIP mode'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(reponse.content)
                        self.logger_error.error(e)
    def script_jython_List_package_listbox(self,phase):
        if phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'        
        # url=self.url_api_xlr+'tasks/'+task_id+'/tasks'
        try: 
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'PACKAGE Variable for the  RELEASE' ,
                                                            "script":  "##script_jython_List_package_listbox\n"
                                                                       "import json\n"
                                                                       "list_actif_package = []\n"
                                                                       "for template_package in  releaseVariables['release_Variables_in_progress']['template_liste_package'].split(','):\n"
                                                                       "    if template_package in releaseVariables['List_package']: \n" 
                                                                       "                list_actif_package.append(template_package)\n" 
                                                                       "    releaseVariables['release_Variables_in_progress']['list_package_manage'] = list_actif_package\n"
                                                                       "\n"                                                                                                                   
                                                                       },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        if self.parameters['general_info']['type_template'] == 'SKIP':
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'PACKAGE Variable for the RELEASE'. 'template_package_mode': listbox with precondition : "+ precondition) 
                        else:
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'PACKAGE Variable for the RELEASE'. 'template_package_mode': listbox")

        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'PACKAGE Variable for the RELEASE'. 'template_package_mode': listbox")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    def jython_delete_jenkins_task_if_xld_package(self,phase):
        if phase in ['DEV','dynamic_release']:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : False,
                                                            "title" : 'Delete jenkins task if package ever exist in XLD' ,
                                                            "script":  "##deletejenkisntask_if_xld_package\n"
                                                                        "from java.net import URLEncoder\n"
                                                                        "import re\n"
                                                                        "import json\n"
                                                                        "for package in releaseVariables['release_Variables_in_progress']['list_package'].split(','):\n"
                                                                        "   if releaseVariables['check_xld_'+package.encode('utf-8')]: \n"
                                                                        "       title_jenkins_task = 'Jenkins '+package.encode('utf-8')\n"
                                                                        "       xlr_id_task_to_delete = taskApi.searchTasksByTitle(title_jenkins_task, 'DEV', '${release.id}')\n"
                                                                        "       if len(xlr_id_task_to_delete) != 0:\n"
                                                                        "           taskApi.delete(str(xlr_id_task_to_delete[0]))\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        if 'id' in reponse.json():
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : Delete jenkins task if package ever exist in XLD. SKIP mode with precondition : "+ precondition) 
                        else:
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : Delete jenkins task if package ever exist in XLD.")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'Delete jenkins task if package ever exist in XLD'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(reponse.content)
                        self.logger_error.error(e)
    def script_jython_dynamic_delete_xld_undeploy(self,phase):
        if phase in ['DEV','dynamic_release']:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'DELETE XLD TASK' ,
                                                            "script":  "##script_jython_dynamic_delete_xld_undeploy\n"
                                                                       "import json\n"
                                                                    "for phase in releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection'].split(','):\n"
                                                                    "    if 'BUILD' not in phase:\n"
                                                                    "       if 'CREATE_CHANGE' in phase:\n"
                                                                    "           nphase = phase.split('CREATE_CHANGE_')[-1]\n"
                                                                    "       else: \n"
                                                                    "           nphase = phase\n"
                                                                    "       if ${dict_value_for_template}['xld'].get(nphase) is not None:\n"
                                                                    "         for titlegroup  in ${dict_value_for_template}['xld'][nphase]:\n"
                                                                    "           list_package_delete = [] \n"
                                                                    "           listpackfolder = [] \n"
                                                                    "           for pack in ${dict_value_for_template}['xld'][nphase][titlegroup]:\n"
                                                                    "               listpackfolder.append(pack)\n"
                                                                    "           for pack in ${dict_value_for_template}['xld'][nphase][titlegroup]:\n"
                                                                    "               if pack not in releaseVariables['List_package']:\n"
                                                                    "                   list_package_delete.append(titlegroup)\n"
                                                                    "                   task_xld_phase = 'XLD-Deploy '+pack\n"
                                                                    "                   xlr_id_task_to_delete = taskApi.searchTasksByTitle(task_xld_phase, phase, '${release.id}')\n"
                                                                    "                   if len(xlr_id_task_to_delete) != 0:\n"
                                                                    "                       taskApi.delete(str(xlr_id_task_to_delete[0]))\n"
                                                                    "               if ('DEV' in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(',') and phase != 'DEV') or ( 'DEV' not in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(',') and ('BENCH' in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(',') and 'PRODUCTION' in releaseVariables['release_Variables_in_progress']['xlr_list_phase'].split(',')) and phase == 'PRODUCTION' ):\n"
                                                                    "                       XLD_title = 'XLD-Deploy Search last version : '+pack\n"
                                                                    "                       xlr_id_task_to_delete = taskApi.searchTasksByTitle(XLD_title, phase, '${release.id}')\n"
                                                                    "                       if len(xlr_id_task_to_delete) != 0:\n"
                                                                    "                           taskApi.delete(str(xlr_id_task_to_delete[0]))\n"
                                                                    "           if len(listpackfolder) == len(list_package_delete):\n"
                                                                    "               grp_XLD_title = 'GRP-XLD-Deploy '+titlegroup\n"
                                                                    "               xlr_id_task_to_delete = taskApi.searchTasksByTitle(grp_XLD_title, phase, '${release.id}')\n"
                                                                    "               if len(xlr_id_task_to_delete) != 0:\n"
                                                                    "                   taskApi.delete(str(xlr_id_task_to_delete[0]))\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE XLD TASK UNDEPLOY'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE XLD TASK UNDEPLOY'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(reponse.content)
                        self.logger_error.error(e)
    def script_jython_List_package_string(self,phase):
        if phase == 'DEV' or phase == 'BUILD' :
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'

        elif phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'        
        # url=self.url_api_xlr+'tasks/'+task_id+'/tasks'
        try:    
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'PACKAGE Variable for the RELEASE' ,
                                                            "script":  "##script_jython_List_package_string\n"
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
                                                                       "            exit() \n"
                                                                       "    except:\n"
                                                                       "            print('ERROR')\n"
                                                                       "            exit()(1)\n"
                                                                       "\n"
                                                                       "releaseVariables['release_Variables_in_progress']['list_package_manage'] =  ','.join(map(str, list_package_manage))\n"
                                                                       "releaseVariables['release_Variables_in_progress']['list_package_not_manage'] =  ','.join(map(str, list_package_not_manage))\n"
                                                                       },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'PACKAGE Variable for the RELEASE'. 'template_package_mode': string")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'PACKAGE Variable for the RELEASE.' 'template_package_mode': string")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    def script_jython_List_package_jenkinsjobparam_yes(self,phase):
        if phase in ['DEV','dynamic_release']:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'        
        # url=self.url_api_xlr+'tasks/'+task_id+'/tasks'
        try:    
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'PACKAGE Variable for the  RELEASE' ,
                                                            "script":  "##script_jython_List_package_jenkinsjobparam_yes\n"
                                                                       "import json,sys\n"
                                                                       "List_package = []\n"
                                                                       "list_actif_package_build = []\n"
                                                                       "list_actif_package_version = []\n"
                                                                       "list_actif_package_empty = []\n"
                                                                       "list_package_not_demand = []\n"
                                                                       "for package in  ${release_Variables_in_progress}['list_package'].split(','):\n"
                                                                       "    if releaseVariables['release_Variables_in_progress']['package_title_choice'] not in  releaseVariables[package.split(',')[0]+'_version']:\n" 
                                                                       "        if releaseVariables[package.split(',')[0]+'_version'] == '':\n"
                                                                       "            list_actif_package_empty.append(package.split(',')[0].encode('utf-8'))\n"
                                                                       "        elif package.split(',')[1].replace('<version>','') in  releaseVariables[package.split(',')[0]+'_version']: \n"
                                                                       "            list_actif_package_version.append(package.split(',')[0].encode('utf-8'))\n"
                                                                       "            List_package.append(package.split(',')[0].encode('utf-8'))\n"
                                                                       "        else:\n"
                                                                       "            list_actif_package_build.append(package.split(',')[0].encode('utf-8'))\n"
                                                                       "            List_package.append(package.split(',')[0].encode('utf-8'))\n"
                                                                       "    else: \n"
                                                                       "        list_package_not_demand.append(package.split(',')[0].encode('utf-8'))\n"
                                                                       "\n"
                                                                       "if len(list_actif_package_empty) != 0:\n"
                                                                       "    try: \n"
                                                                       "\n"
                                                                       "        print('------   ERROR in declaration   ------')\n"
                                                                       "\n"
                                                                       "        print('Empty is not autorized on package value.')    \n"
                                                                       "        print('Change value for package : ')    \n"
                                                                       "\n"
                                                                       "        for empty_package in list_actif_package_empty:\n"
                                                                       "            print('     - '+empty_package)    \n"
                                                                       "            exit() \n"
                                                                       "    except:\n"
                                                                       "            print('ERROR')\n"
                                                                       "            exit()(1)\n"
                                                                       "\n"
                                                                       "releaseVariables['List_package'] = List_package\n"
                                                                       "releaseVariables['list_actif_package_build'] = list_actif_package_build\n"
                                                                       "releaseVariables['list_actif_package_version'] = list_actif_package_version\n"
                                                                       },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'PACKAGE Variable for the RELEASE'. 'template_package_mode': string")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'PACKAGE Variable for the RELEASE.' 'template_package_mode': string")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    def XLRJython_delete_phase_list_multi_list(self,phase):
        if phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        elif phase == 'BUILD':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try : 
            response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'DELETE PHASE' ,
                                                            "script":  "##script_jython_delete_phase_list_multi_list\n"
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
                                                                    "for phase in xlr_list_phase_selection_to_delete:\n"
                                                                    "   xlr_id_phase_to_delete = phaseApi.searchPhasesByTitle(phase, '${release.id}')\n"
                                                                    "   if len(xlr_id_phase_to_delete) != 0:\n"
                                                                    "       phaseApi.deletePhase(str(xlr_id_phase_to_delete[0]))\n"
                                                            },verify = False)
            response.raise_for_status()
            if response.content:
                    if 'id' in response.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'RELEASE DELETE PHASE'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'RELEASE DELETE PHASE'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(response.content)

                        self.logger_error.error(e)
                        sys.exit(0)
    def XLRJython_delete_phase_one_list(self,phase):
        if phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try : 
            response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'DELETE PHASE' ,
                                                            "script":  "##script_jython_delete_phase_one_list_bis\n"
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
                                                                    "xlr_list_phase_selection.append('DEV')\n"
                                                                    "releaseVariables['release_Variables_in_progress']['xlr_list_phase'] = ','.join(map(str, xlr_list_phase))\n"
                                                                    "releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection'] = ','.join(map(str, xlr_list_phase_selection))\n"
                                                                    "releaseVariables['release_Variables_in_progress']['xlr_list_phase_to_delete'] = ','.join(map(str, xlr_list_phase_to_delete))\n"
                                                                    "releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection_to_delete'] = ','.join(map(str, xlr_list_phase_selection_to_delete))\n"
                                                                    "for phase in xlr_list_phase_selection_to_delete:\n"
                                                                    "   xlr_id_phase_to_delete = phaseApi.searchPhasesByTitle(phase, '${release.id}')\n"
                                                                    "   if len(xlr_id_phase_to_delete) != 0:\n"
                                                                    "       phaseApi.deletePhase(str(xlr_id_phase_to_delete[0]))\n"
                                                                    "\n"
                                                            },verify = False)
            response.raise_for_status()
            if response.content:
                    if 'id' in response.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE PHASE'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE PHASE'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    def XLRJython_delete_phase_one_list_template_package_mode_string(self,phase):
        if phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try : 
            response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'DELETE PHASE' ,
                                                            "script":  "##script_jython_delete_phase_one_list_template_package_mode_string\n"
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
                                                                    "for phase in xlr_list_phase_selection_to_delete:\n"
                                                                    "   xlr_id_phase_to_delete = phaseApi.searchPhasesByTitle(phase, '${release.id}')\n"
                                                                    "   if len(xlr_id_phase_to_delete) != 0:\n"
                                                                    "       phaseApi.deletePhase(str(xlr_id_phase_to_delete[0]))\n"
                                                                    "\n"
                                                            },verify = False)
            response.raise_for_status()
            if response.content:
                    if 'id' in response.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE PHASE'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE PHASE'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    def XLRJython_delete_phase_one_list_template_package_mode_string_with_build(self,phase):
        if phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try : 
            response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'DELETE PHASE' ,
                                                            "script":  "##XLRJython_delete_phase_one_list_template_package_mode_string_with_build\n"
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
                                                                    "           if 'PRODUCTION' in ${Choice_ENV}: \n"
                                                                    "               xlr_list_phase_selection.append('CREATE_CHANGE_BENCH')\n"
                                                                    "               xlr_list_phase_selection.append('BENCH')\n"
                                                                    "               xlr_list_phase.append('BENCH')\n"
                                                                    "       else:\n"
                                                                    "           if phase != 'BUILD':\n"
                                                                    "            xlr_list_phase_selection.append(phase)\n"
                                                                    "            xlr_list_phase.append(phase)\n"
                                                                    "   else:\n"
                                                                    "      if 'PRODUCTION' in ${Choice_ENV} and phase == 'BENCH': \n"
                                                                    "           pass\n"
                                                                    "      else:\n"
                                                                    "        if phase in ['PRODUCTION','BENCH'] :\n"
                                                                    "           xlr_list_phase_selection_to_delete.append('CREATE_CHANGE_'+phase)\n"
                                                                    "           xlr_list_phase_selection_to_delete.append(phase)\n"
                                                                    "           xlr_list_phase_to_delete.append(phase)\n"
                                                                    "        else:\n"
                                                                    "           if phase != 'BUILD':\n"
                                                                    "               xlr_list_phase_selection_to_delete.append(phase)\n"
                                                                    "               xlr_list_phase_to_delete.append(phase)\n"
                                                                    "releaseVariables['release_Variables_in_progress']['xlr_list_phase'] = ','.join(map(str, xlr_list_phase))\n"
                                                                    "releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection'] =  ','.join(map(str, xlr_list_phase_selection))\n"
                                                                    "releaseVariables['release_Variables_in_progress']['xlr_list_phase_to_delete'] = ','.join(map(str, xlr_list_phase_to_delete))\n"
                                                                    "releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection_to_delete'] = ','.join(map(str, xlr_list_phase_selection_to_delete))\n"
                                                                    "for phase in xlr_list_phase_selection_to_delete:\n"
                                                                    "   xlr_id_phase_to_delete = phaseApi.searchPhasesByTitle(phase, '${release.id}')\n"
                                                                    "   if len(xlr_id_phase_to_delete) != 0:\n"
                                                                    "       phaseApi.deletePhase(str(xlr_id_phase_to_delete[0]))\n"
                                                                    "\n"
                                                            },verify = False)
            response.raise_for_status()
            if response.content:
                    if 'id' in response.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE PHASE'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE PHASE'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    # def XLRJython_delete_phase_one_list_bis(self,phase):
    #     if phase == 'dynamic_release':
    #         url_delete_phase_one_list_bis=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
    #     else:
    #         url_delete_phase_one_list_bis=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
    #     try : 
    #         reponse_delete_phase_one_list_bis= requests.post(url_delete_phase_one_list_bis, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
    #                                                         "id" : "null",
    #                                                         "type" : "xlrelease.ScriptTask",
    #                                                         "locked" : True,
    #                                                         "title" : 'DELETE PHASE' ,
    #                                                         "script":  "##XLRJython_delete_phase_one_list_bis\n"
    #                                                                    "import json\n"
    #                                                                 "xlr_list_phase_selection = []\n"
    #                                                                 "xlr_list_phase = []\n"
    #                                                                 "xlr_list_phase_selection_to_delete = []\n"
    #                                                                 "xlr_list_phase_to_delete = []\n"
    #                                                                 "for phase in ${release_Variables_in_progress}['list_package'].split(','):\n"
    #                                                                 "   if phase in ${Choice_ENV}:\n"
    #                                                                 "       if phase in ['PRODUCTION','BENCH'] :\n"
    #                                                                 "           xlr_list_phase_selection.append('CREATE_CHANGE_'+phase)\n"
    #                                                                 "           xlr_list_phase_selection.append(phase)\n"
    #                                                                 "           xlr_list_phase.append(phase)\n"
    #                                                                 "       else:\n"
    #                                                                 "           xlr_list_phase_selection.append(phase)\n"
    #                                                                 "           xlr_list_phase.append(phase)\n"
    #                                                                 "   else:\n"
    #                                                                 "     if phase != 'DEV':\n"
    #                                                                 "       if phase in ['PRODUCTION','BENCH']:\n"
    #                                                                 "           xlr_list_phase_selection_to_delete.append('CREATE_CHANGE_'+phase)\n"
    #                                                                 "           xlr_list_phase_selection_to_delete.append(phase)\n"
    #                                                                 "           xlr_list_phase_to_delete.append(phase)\n"
    #                                                                 "       else:\n"
    #                                                                 "           xlr_list_phase_selection_to_delete.append(phase)\n"
    #                                                                 "           xlr_list_phase_to_delete.append(phase)\n"
    #                                                                 "xlr_list_phase_selection.append('DEV')\n"
    #                                                                 "releaseVariables['release_Variables_in_progress']['xlr_list_phase'] = xlr_list_phase\n"
    #                                                                 "releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection'] = xlr_list_phase_selection\n"
    #                                                                 "releaseVariables['release_Variables_in_progress']['xlr_list_phase_to_delete'] = xlr_list_phase_to_delete\n"
    #                                                                 "releaseVariable['release_Variables_in_progress']s['xlr_list_phase_selection_to_delete'] = xlr_list_phase_selection_to_delete\n"
    #                                                                 "for phase in xlr_list_phase_selection_to_delete:\n"
    #                                                                 "   xlr_id_phase_to_delete = phaseApi.searchPhasesByTitle(phase, '${release.id}')\n"
    #                                                                 "   if len(xlr_id_phase_to_delete) != 0:\n"
    #                                                                 "       phaseApi.deletePhase(str(xlr_id_phase_to_delete[0]))\n"
    #                                                                 "\n"
    #                                                         },verify = False)
    #         reponse_delete_phase_one_list_bis.raise_for_status()
    #         if reponse_delete_phase_one_list_bis.content:
    #                 if 'id' in reponse_delete_phase_one_list_bis.json():
    #                     self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE PHASE'")
    #     except requests.exceptions.RequestException as e:   
    #                     self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE PHASE'")
    #                     self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
    #                     self.logger_error.error("Error call api : "+url_delete_phase_one_list_bis)
    #                     self.logger_error.error(e)
    #                     sys.exit(0)
    # def XLRJython_delete_phase_one_list_template_package_mode_string(self,phase):
    #     if phase == 'dynamic_release':
    #         url_delete_phase_one_list_template_package_mode_string=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
    #     else:
    #         url_delete_phase_one_list_template_package_mode_string=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
    #     try : 
    #         reponse_delete_phase_one_list_template_package_mode_string= requests.post(url_delete_phase_one_list_template_package_mode_string, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
    #                                                         "id" : "null",
    #                                                         "type" : "xlrelease.ScriptTask",
    #                                                         "locked" : True,
    #                                                         "title" : 'DELETE PHASE' ,
    #                                                         "script":  "##script_jython_delete_phase_one_list_template_package_mode_string\n"
    #                                                                    "import json\n"
    #                                                                 "xlr_list_phase_selection = []\n"
    #                                                                 "xlr_list_phase = []\n"
    #                                                                 "xlr_list_phase_selection_to_delete = []\n"
    #                                                                 "xlr_list_phase_to_delete = []\n"
    #                                                                 "for phase in ${dict_value_for_template}['template_liste_phase']:\n"
    #                                                                 "   if phase in ${Choice_ENV} and phase != 'BUILD':\n"
    #                                                                 "       if phase in ['PRODUCTION','BENCH'] :\n"
    #                                                                 "           xlr_list_phase_selection.append('CREATE_CHANGE_'+phase)\n"
    #                                                                 "           xlr_list_phase_selection.append(phase)\n"
    #                                                                 "           xlr_list_phase.append(phase)\n"
    #                                                                 "       else:\n"
    #                                                                 "           if phase != 'BUILD':\n"
    #                                                                 "               xlr_list_phase_selection.append(phase)\n"
    #                                                                 "               xlr_list_phase.append(phase)\n"
    #                                                                 "   else:\n"
    #                                                                 "       if phase in ['PRODUCTION','BENCH'] :\n"
    #                                                                 "           xlr_list_phase_selection_to_delete.append('CREATE_CHANGE_'+phase)\n"
    #                                                                 "           xlr_list_phase_selection_to_delete.append(phase)\n"
    #                                                                 "           xlr_list_phase_to_delete.append(phase)\n"
    #                                                                 "       else:\n"
    #                                                                 "           if phase != 'BUILD':\n"
    #                                                                 "               xlr_list_phase_selection_to_delete.append(phase)\n"
    #                                                                 "               xlr_list_phase_to_delete.append(phase)\n"
    #                                                                 "xlr_list_phase_selection.append('DEV')\n"
    #                                                                 "releaseVariables['release_Variables_in_progress']['xlr_list_phase'] = xlr_list_phase\n"
    #                                                                 "releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection'] = xlr_list_phase_selection\n"
    #                                                                 "releaseVariables['release_Variables_in_progress']['xlr_list_phase_to_delete'] = xlr_list_phase_to_delete\n"
    #                                                                 "releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection_to_delete'] = xlr_list_phase_selection_to_delete\n"
    #                                                                 "for phase in xlr_list_phase_selection_to_delete:\n"
    #                                                                 "   xlr_id_phase_to_delete = phaseApi.searchPhasesByTitle(phase, '${release.id}')\n"
    #                                                                 "   if len(xlr_id_phase_to_delete) != 0:\n"
    #                                                                 "       phaseApi.deletePhase(str(xlr_id_phase_to_delete[0]))\n"
    #                                                                 "\n"
    #                                                         },verify = False)
    #         reponse_delete_phase_one_list_template_package_mode_string.raise_for_status()
    #         if reponse_delete_phase_one_list_template_package_mode_string.content:
    #                 if 'id' in reponse_delete_phase_one_list_template_package_mode_string.json():
    #                     self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE PHASE'")
    #     except requests.exceptions.RequestException as e:   
    #                     self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE PHASE'")
    #                     self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
    #                     self.logger_error.error("Error call api : "+url_delete_phase_one_list_template_package_mode_string)
    #                     self.logger_error.error(e)
    #                     sys.exit(0)

    def XLRJythonScript_define_xld_prefix_new(self,phase):
        if phase == 'Dev':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'

        elif phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['sun_'+phase]['xlr_id_phase'] +'/tasks'        
        # url_format_date_from_xlr_input=self.url_api_xlr+'tasks/'+task_id+'/tasks'
        requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'define prefix XLD' ,
                                                            "script":  "##XLRJythonScript_define_xld_prefix_new\n"
                                                                       "for item in  ${release_Variables_in_progress}['list_env_BENCH'].split(','):\n"
                                                                       "    if releaseVariables['env_BENCH'] == item.split(';')[0]: \n"
                                                                       "        if '-' not in item:\n"
                                                                       "            releaseVariables['controlm_prefix_BENCH'] = 'B'\n"
                                                                       "        else:\n"
                                                                       "            releaseVariables['controlm_prefix_BENCH'] = item.split(';')[1]\n"
                                                                       "    else:\n"
                                                                       "        print('Error in definition Prefixe BENCH')\n"
                                                                       },verify = False)
    def XLRJythonScript_delete_phase_inc(self,phase):
        if phase == 'Dev':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'

        elif phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template['sun_'+phase]['xlr_id_phase'] +'/tasks'
        requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'Delete Phase' ,
                                                            "script": "##XLRJythonScript_delete_phase_inc\n"
                                                                    "\n"
                                                                    "\n"
                                                                    "releaseVariables['Release_Email_resquester'] = userApi.getUser('${release.owner}').email\n"
                                                                    "def delete_phase(phases):\n"
                                                                    "           idphasetodelete = phaseApi.searchPhasesByTitle(phase, '${release.id}')\n"
                                                                    "           if len(idphasetodelete) != 0:\n"
                                                                    "               phaseApi.deletePhase(str(idphasetodelete[0]))\n"
                                                                    "list_phase = []\n"  
                                                                    "for env in  releaseVariables['liste_phase']:  \n"
                                                                    "   if not releaseVariables[env]:\n"
                                                                    "       if 'PROD' in env:\n"
                                                                    "           list_phase.append('PRODUCTION')\n"
                                                                    "       elif 'BENCH' in env:\n"
                                                                    "           list_phase.append('BENCH')\n"
                                                                    "\n"
                                                                    "for phase in list_phase:\n"
                                                                    "     delete_phase(phase)\n"
                                                                    "\n"
                                                            },verify = False)    
    def XLRJythonScript_dynamic_release_delete_technical_task_StringVariable(self,phase):
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
                                                            "locked" : True,
                                                            "title" : 'DELETE TECHNICAL TASK' ,
                                                            "script":  "##XLRJythonScript_dynamic_release_delete_technical_task_StringVariable\n"
                                                                       "import json\n"
                                                                    "list_technical_task_to_delete = []\n"
                                                                    "for step_technical_task in ${dict_value_for_template_technical_task}['technical_task']:\n"
                                                                    "    for technical_task in ${dict_value_for_template_technical_task}['technical_task'][step_technical_task]:\n"
                                                                    "       if releaseVariables[step_technical_task+'_'+technical_task] == '':\n"
                                                                    "           title_task_value =${dict_value_for_template_technical_task}['technical_task'][step_technical_task][technical_task]['sun_title']\n"
                                                                    "           list_technical_task_to_delete.append(title_task_value.encode('utf-8'))\n"
                                                                    "for phase in releaseVariables['release_Variables_in_progress']['xlr_list_phase_selection'].split(','):\n"
                                                                    "   for task_to_delete in list_technical_task_to_delete:\n"
                                                                    "       xlr_id_task_to_delete = taskApi.searchTasksByTitle(task_to_delete, phase, '${release.id}')\n"
                                                                    "       if len(xlr_id_task_to_delete) != 0:\n"
                                                                    "           taskApi.delete(str(xlr_id_task_to_delete[0]))\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'RELEASE DELETE TECHNICAL TASK'. When 'technical_task_mode' == 'string'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" ---  Add task : 'RELEASE DELETE TECHNICAL TASK'. When 'technical_task_mode' == 'string'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    def XLRJythonScript_release_delete_technical_task_ListStringVariable(self,phase):
        if phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'DELETE TECHNICAL TASK' ,
                                                            "script":  "##XLRJythonScript_release_delete_technical_task_ListStringVariable\n"
                                                                       "import json\n"
                                                                    "list_technical_task_to_delete = []\n"
                                                                    "for step_technical_task in ${dict_value_for_template_technical_task}['technical_task']:\n"
                                                                    "    listtask = list(${dict_value_for_template_technical_task}['technical_task'][step_technical_task].keys())\n"
                                                                    "    for technical_task in ${dict_value_for_template_technical_task}['technical_task'][step_technical_task]:\n"
                                                                    "       if ${dict_value_for_template_technical_task}['technical_task'][step_technical_task][technical_task]['xlr_item_name']  not in releaseVariables[step_technical_task]:\n"
                                                                    "           title_task_value =  ${dict_value_for_template_technical_task}['technical_task'][step_technical_task][technical_task]['sun_title']\n"
                                                                    "           list_technical_task_to_delete.append(title_task_value.encode('utf-8'))\n"
                                                                    "for phase in ${xlr_list_phase_selection}:\n"
                                                                    "   for task_to_delete in list_technical_task_to_delete:\n"
                                                                    "       xlr_id_task_to_delete = taskApi.searchTasksByTitle(task_to_delete, phase, '${release.id}')\n"
                                                                    "       if len(xlr_id_task_to_delete) != 0:\n"
                                                                    "           taskApi.delete(str(xlr_id_task_to_delete[0]))\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE TECHNICAL TASK'. When 'technical_task_mode' == 'listbox'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE TECHNICAL TASK'. When 'technical_task_mode' == 'listbox'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)                   
