
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
class XLRGeneric:
    """
    Base class for XLR (XebiaLabs Release) template operations.

    This class provides core functionality for XLR template creation and management:
    - Template creation and deletion
    - Phase management (DEV, UAT, BENCH, PRODUCTION)
    - Variable creation and management
    - XLR API communication
    - Folder and task organization
    - Logging and error handling

    The class serves as the foundation for all XLR operations and is inherited
    by specialized classes for specific functionality like Control-M integration,
    SUN approval workflows, and dynamic phase management.

    Key operations:
    - Creating XLR release templates
    - Managing template phases and tasks
    - Variable definition and lifecycle management
    - XLR folder structure management
    - API authentication and error handling
    """

    def CreateTemplate(self):
        """
        Create a new XLR release template.

        Returns:
            tuple: (dict_template, XLR_template_id) containing template metadata

        Creates a new XLR release template in the specified folder with:
        - Template title from configuration
        - TEMPLATE status for reuse
        - Script authentication credentials
        - Proper API authentication

        Raises:
            SystemExit: On template creation failure or API errors
        """
        url_createtemplate=self.url_api_xlr+"templates/?folderId="+self.dict_template['template']['xlr_folder']
        try:
            reponse_createtemplate= requests.post(url_createtemplate, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                "id" : None,
                                "type" : "xlrelease.Release",
                                "title" : self.parameters['general_info']['name_release'],
                                "status" : "TEMPLATE",
                                "scheduledStartDate" : "2023-03-09T17:56:54.786+01:00",
                                "scriptUsername" : self.ops_username_api,
                                "scriptUserPassword" : self.ops_password_api
                                },verify = False)
            reponse_createtemplate.raise_for_status()
            if 'template' not in self.dict_template:
                            try:
                                self.XLR_template_id = reponse_createtemplate.json()['id']
                                self.dict_template.update({'template': {'xlr_id': reponse_createtemplate.json()['id']}})
                                self.logger_cr.info("CREATE TEMPLATE in XLR FOLDER : "+ self.parameters['general_info']['xlr_folder'])
                                self.logger_cr.info(self.parameters['general_info']['name_release'])
                                # dir_template=self.dict_template['template']['xlr_id'].replace("Applications/", "").replace('/','-')
                                self.template_url = 'https://release-pfi.mycloud.intranatixis.com/#/templates/'+self.XLR_template_id.replace("Applications/", "").replace('/','-')
                            except TypeError as e:
                                self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                                self.logger_error.error("Update Dico 'dict_template' in error")
                                self.logger_error.error( e)
                                sys.exit(0)
                            except  Exception as e:
                                self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                                self.logger_error.error("Update Dico 'dict_template' in error")
                                self.logger_error.error( e)
                                sys.exit(0)
            else:
                            try:
                                self.XLR_template_id = reponse_createtemplate.json()['id']
                                self.dict_template['template'].update({'xlr_id': reponse_createtemplate.json()['id']})
                                self.template_url = 'https://release-pfi.mycloud.intranatixis.com/#/templates/'+self.XLR_template_id.replace("Applications/", "").replace('/','-')
                                self.logger_cr.info("")
                                self.logger_cr.info("CREATE TEMPLATE In FOLDER XLR: "+ self.parameters['general_info']['xlr_folder'])
                                self.logger_cr.info("")
                                self.logger_cr.info("                 NAME : "+self.parameters['general_info']['name_release'])
                                self.logger_cr.info("                 LINK : "+self.template_url)
                                self.logger_cr.info("")
                            except TypeError as e:
                                self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                                self.logger_error.error("Update Dico 'dict_template' in error")
                                self.logger_error.error( e)
                                sys.exit(0)
                            except  Exception as e:
                                self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                                self.logger_error.error("Update Dico 'dict_template' in error")
                                self.logger_error.error( e)
                                sys.exit(0)
        except requests.exceptions.RequestException as e:
                    self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                    self.logger_error.error("Detail ERROR create template ")
                    self.logger_error.error(e)
                    sys.exit(0)
        return self.dict_template,self.XLR_template_id
    
    def parameter_phase_task(self,phase):
        self.auto_undeploy_done = False
        if  phase == 'DEV' or phase == 'BUILD' or phase == 'UAT':
                if  (self.parameters['general_info']['template_package_mode'] == 'listbox' \
                        and 'DEV' not in self.parameters['general_info']['phases'])  \
                        or \
                        (self.parameters['general_info']['template_package_mode'] == 'listbox' \
                        and 'DEV' in self.parameters['general_info']['phases'] \
                        and (phase =='UAT' or phase =='DEV'))\
                        or \
                        (self.parameters['general_info']['template_package_mode'] == 'string' 
                        and 'DEV' in self.parameters['general_info']['phases'] \
                        and (phase =='UAT' or phase =='DEV')):
                        if  any(phase+'_username_xldeploy' in d for d in self.dict_template[phase]):
                                pass
                        else:
                                XLRGeneric.add_task_user_input(self,phase=phase,type_userinput='xldeploy',link_task_id=self.dict_template['template']['xlr_id']+'/'+self.dict_template[phase]['xlr_id_phase'] )
                ##si DEV est dans la liste de phase et que la key: jenkins est présente dans le YAML 
                ## creation des task jenkins dans un group de task XLR 
                if self.parameters.get('jenkins') is not None and  phase == 'DEV':
                            name_from_jenkins = 'no'
                            if self.name_from_jenkins_value == "yes" or (self.parameters['general_info'].get('package_mode') is not None and self.parameters['general_info']['package_mode'] == 'generic'):
                                if  any(phase+'_username_xldeploy' in d for d in self.dict_template[phase]):
                                    pass
                                else:
                                    XLRGeneric.add_task_user_input(self,phase=phase,type_userinput='xldeploy',link_task_id=self.dict_template[phase]['xlr_id_phase_full'])
                            group_done = 'no'
                            for packagename,package_value in self.parameters['template_liste_package'].items():
                                if  packagename in self.release_Variables_in_progress['list_package']:
                                    if package_value.get('mode') is not None:
                                        if package_value['mode'] == 'name_from_jenkins' or package_value['mode'] == 'CHECK_XLD':
                                            name_from_jenkins = 'yes'
                                            if group_done == "no":
                                                self.grp_id_xldeploy = XLRGeneric.XLR_group_task(self,
                                                    ID_XLR_task= self.dict_template[phase]['xlr_id_phase'],
                                                    type_group="SequentialGroup",
                                                    title_group="Check if XLD package exist",     
                                                    precondition='')
                                                group_done = 'yes'
                                            self.create_variable_bolean('check_xld_'+packagename)
                                            self.xld_check_package(packagename,package_value,phase,self.grp_id_xldeploy)
                            if name_from_jenkins == 'yes':
                                XLRDynamicPhase.jython_delete_jenkins_task_if_xld_package(self,phase)
                if (self.parameters.get('jenkins') is not None and  (phase == 'DEV' and 'BUILD' not in self.parameters['general_info']['phases'] )) \
                    or \
                    (self.parameters.get('jenkins') is not None and  (phase == 'BUILD')) \
                    or \
                    (self.parameters['general_info'].get('jenkins_UAT') is not None \
                        and self.parameters['general_info']['jenkins_UAT']\
                        and  phase == 'UAT'):
                        if self.transformation_variable_branch :
                            XLRTaskScript.task_xlr_transformation_variable_branch(self,phase)
                        self.grp_id_jenkins = XLRGeneric.XLR_group_task(self,
                            ID_XLR_task= self.dict_template[phase]['xlr_id_phase'],
                            type_group="SequentialGroup",
                            title_group="Jenkins JOBS",     
                            precondition='')
                        self.jenkins_token = False
                        if self.parameters.get('jenkins') is not None:
                            for jenkinsjob,jenkinsjob_value in self.parameters['jenkins']['jenkinsjob'].items():
                                if not self.jenkins_token and self.parameters['jenkins'].get('valueapiToken') is not None:
                                    XLRGeneric.template_create_variable(self,key='apiToken_jenkins_iua', 
                                                                        typev='PasswordStringVariable', 
                                                                        label='', 
                                                                        description='', 
                                                                        value=self.parameters['jenkins']['valueapiToken'], 
                                                                        requiresValue=False, 
                                                                        showOnReleaseStart=False, 
                                                                        multiline=False)
                                    self.jenkins_token = True
                                if jenkinsjob in self.release_Variables_in_progress['list_package']:
                                        self.add_task_jenkins(phase,jenkinsjob,jenkinsjob_value)
                                elif self.parameters['general_info']['type_template'] == 'MULTIPACKAGE_AT_ONCE' :
                                        self.add_task_jenkins(phase,jenkinsjob,jenkinsjob_value)
                            if self.parameters['general_info']['template_package_mode'] == 'string':
                                if self.parameters['general_info']['type_template'] == 'SKIP':
                                    XLRTaskScript.get_num_version_from_jenkins_skip(self,'DEV')
                                elif self.parameters['general_info']['type_template'] == 'STATIC':
                                    XLRTaskScript.get_num_version_from_jenkins_static(self,'DEV')
                                elif self.parameters['general_info']['type_template'] != 'MULTIPACKAGE_AT_ONCE':
                                    if self.parameters['general_info'].get('package_name_from_jenkins') is not None:
                                        if not self.parameters['general_info']['type_template']:
                                            XLRTaskScript.get_num_version_from_jenkins(self,phase)
                                    elif self.name_from_jenkins_value == "no":
                                            XLRTaskScript.get_num_version_from_jenkins(self,phase)
                                    elif self.check_xld_exist: 
                                            XLRTaskScript.reevaluate_variable_package_version(self,phase)
                            elif self.parameters['general_info']['template_package_mode'] == 'listbox':
                                if phase == 'DEV':
                                    XLRTaskScript.get_version_of_the_package_listbox(self,'DEV')
        if self.parameters['Phases'].get(phase) is not None:
            count_number_xld_task = 0
            LAST8XLD = 'no'
            for task in self.parameters['Phases'][phase]:
                if '_xldeploy' in task:
                    count_number_xld_task += 1
            for numtask,task in enumerate(self.parameters['Phases'][phase]):
                if isinstance(task, dict) and 'xldeploy' in list(task.keys())[0]:
                        count_number_xld_task += 1
                        if phase not in ['BUILD','UAT','DEV']:
                            XLRGeneric.creation_technical_task(self,phase,'before_deployment')
                            XLRGeneric.creation_technical_task(self,phase,'before_xldeploy')
                        count_deliverable = 0
                        if  any(phase+'_username_xldeploy' in d for d in self.dict_template[phase]):
                            pass
                        else:
                            XLRGeneric.add_task_user_input(self,phase=phase,type_userinput='xldeploy',link_task_id=self.dict_template[phase]['xlr_id_phase_full'])
                        try:
                            check_version_before
                        except NameError:
                            # self.grp_id_xldeploy_check = XLRGeneric.create_group_task(self,phase=phase,type_task='checkversion',title_group='Check Version package in XLD BEFORE',cat_technicaltask=None,precondition='')
                            check_version_before = 'yes'
                            # print(self.release_Variables_in_progress['list_auto_undeploy'])
                            if self.release_Variables_in_progress['list_auto_undeploy'] != '': 
                                self.grp_id_xldeploy_check = XLRGeneric.XLR_group_task(self,
                                            ID_XLR_task= self.dict_template[phase]['xlr_id_phase'],
                                            type_group="ParallelGroup",
                                            title_group='Check Version package in XLD BEFORE',     
                                            precondition='')
                                # print(self.release_Variables_in_progress['list_auto_undeploy'])
                                if self.release_Variables_in_progress['list_auto_undeploy'] != '':
                                    for package in self.release_Variables_in_progress['list_auto_undeploy'].split(','):
                                                XLRGeneric.template_create_variable(self,key='version_deployed_'+package+'_'+phase+'_BEFORE', typev='StringVariable', label='', description='', value=[], requiresValue=False, showOnReleaseStart=False, multiline=False)
                                                XLRGeneric.xld_get_version_deploy(self,package_name=package,phase=phase,grp_id_xldeploy=self.grp_id_xldeploy_check,step='BEFORE')
                                # XLRGeneric.XLRJython_markdown_version_package(self,phase,'BEFORE')
                        if (self.release_Variables_in_progress['auto_undeploy'] != '' and not self.auto_undeploy_done):
                            XLRGeneric.XLRJythonScript_xld_delete_undeploy_after_get_version(self,phase,'BEFORE')
                            self.auto_undeploy_done = True
                        ####add task if auto_undeploy present
                        if self.release_Variables_in_progress['auto_undeploy'] != '':
                                try:
                                    undeploy_task_done
                                except NameError:
                                    undeploy_task_done = "yes"
                                    self.add_task_undeploy(phase)
                                    XLRTaskScript.script_jython_xld_undeploy_revaluate_version_package(self,phase,'BEFORE')
                                else:
                                    pass
                        # ####add task if auto_undeploy present
                        xld_group = False
                        for self.demandxld,grtp_xld_value in task[list(task.keys())[0]].items():
                            if self.parameters['general_info']['xld_group']:
                                xld_group = True
                                if 'xld_XLR_grp_'+phase not in self.list_xlr_group_task_done :
                                    self.xld_ID_XLR_group_task_grp = XLRGeneric.XLR_group_task(self,
                                        ID_XLR_task= self.dict_template[phase]['xlr_id_phase'],
                                        type_group='SequentialGroup',
                                        title_group='XLD DEPLOY',     
                                        precondition='')
                                    self.list_xlr_group_task_done.append('xld_XLR_grp_'+phase)
                            # self.grp_id_xldeploy = XLRGeneric.create_group_task(self,phase=phase,type_task=list(task.keys())[0],title_group=self.demandxld,cat_technicaltask=None,precondition='')
                            for pack_xld in grtp_xld_value:
                                    if pack_xld in self.list_package:
                                        self.under_grp_id_xldeploy = XLRGeneric.XLR_group_task(self,
                                                ID_XLR_task= self.dict_template[phase]['xlr_id_phase'] if not xld_group else self.xld_ID_XLR_group_task_grp,
                                                type_group="SequentialGroup",
                                                title_group='Deploy '+ pack_xld,     
                                                precondition='')
                                        # self.under_grp_id_xldeploy = XLRGeneric.create_group_under_group_task(self,phase=phase,task=list(task.keys())[0],grp_id=self.grp_id_xldeploy,cases=pack_xld,other='')
                                        if  not self.parameters['general_info']['option_latest']:
                                            # print('tototto')
                                            # print(pack_xld)
                                            self.add_task_xldeploy_auto(package_xld=pack_xld,phase=phase,grp_id_xldeploy=self.under_grp_id_xldeploy)
                                        elif self.parameters['general_info']['option_latest']:
                                            self.add_task_xldeploy_auto(package_xld=pack_xld,phase=phase,grp_id_xldeploy=self.under_grp_id_xldeploy)
                                        if phase not in ['UAT','DEV']:
                                            task_to_close = '${task_sun_xld_'+pack_xld+'_'+phase+'}'
                                            XLRSun.XLRSun_task_close_sun_task(self,task_to_close=task_to_close,title=pack_xld,id_task=self.under_grp_id_xldeploy,type_task='xldeploy',phase=phase)
                                        count_deliverable += 1
                        listA= []
                        for num,dictionnaire in enumerate(self.parameters['Phases'][phase]):
                                    if num > numtask and 'xldeploy' in list(dictionnaire.keys())[0]:
                                        listA.append(num)
                        
                        if len(listA)  == 0:
                                if phase not in ['BUILD','UAT','DEV']:
                                    XLRGeneric.creation_technical_task(self,phase,'after_xldeploy')
                        if count_deliverable == 0 :
                            self.dynamic_release(self.grp_id_xldeploy)
                if isinstance(task, dict) and 'launch_script_windows' in list(task.keys())[0]:
                        if phase not in ['BUILD','UAT','DEV']:
                            XLRGeneric.creation_technical_task(self,phase,'before_deployment')
                        if  any(phase+'_username_launch_script_windows' in d for d in self.dict_template[phase]):
                            pass
                        else:
                            XLRGeneric.add_task_user_input(self,phase=phase,type_userinput='launch_script_windows',link_task_id=self.dict_template[phase]['xlr_id_phase_full'])
                        for groupwin_task,groupwin_task_value in task[list(task.keys())[0]].items():            
                            self.grp_id = XLRGeneric.XLR_group_task(self,
                                                    ID_XLR_task= self.dict_template[phase]['xlr_id_phase'],
                                                    type_group="SequentialGroup",
                                                    title_group=list(groupwin_task.keys())[0].split('launch_script_windows')[1],     
                                                    precondition='')
                            for index,sunscript_windows_item in enumerate(groupwin_task[list(groupwin_task.keys())[0]]):
                                XLRGeneric.launch_script_windows(self,phase,self.grp_id,sunscript_windows_item,'launch_script_windows',index)
                                if phase != 'DEV':
                                    task_to_close = '${task_launch_script_windows_'+list(sunscript_windows_item.keys())[0].replace(' ','')+str(index)+'_'+phase+'}'
                                    XLRSun.XLRSun_task_close_sun_task(self,task_to_close=task_to_close,title=task,id_task=self.grp_id,type_task='launch_script_windows',phase=phase)
                if isinstance(task, dict) and 'launch_script_linux' in list(task.keys())[0]:
                        if phase not in ['BUILD','UAT','DEV']:
                            XLRGeneric.creation_technical_task(self,phase,'before_deployment')
                        if  any(phase+'_username_launch_script_linux' in d for d in self.dict_template[phase]):
                            pass
                        else:
                            XLRGeneric.add_task_user_input(self,phase=phase,type_userinput='launch_script_linux',link_task_id=self.dict_template[phase]['xlr_id_phase_full'])
                        for grouplinux_task,grouplinux_task_value in  task[list(task.keys())[0]].items():
                            self.grp_id = XLRGeneric.XLR_group_task(self,
                                                    ID_XLR_task= self.dict_template[phase]['xlr_id_phase'],
                                                    type_group="SequentialGroup",
                                                    title_group=list(grouplinux_task.keys())[0].split('launch_script_windows')[1],     
                                                    precondition='')
                            for index,sunscript_linux_item in enumerate(grouplinux_task[list(grouplinux_task.keys())[0]]):
                                XLRGeneric.launch_script_linux(self,phase,self.grp_id,sunscript_linux_item,'launch_script_linux',index)
                                if phase != 'DEV':
                                    task_to_close = '${task_launch_script_linux_'+list(sunscript_linux_item.keys())[0].replace(' ','')+str(index)+'_'+phase+'}'
                                    XLRSun.XLRSun_task_close_sun_task(self,task_to_close=task_to_close,title=task,id_task=self.grp_id,type_task='launch_script_linux',phase=phase)
                if isinstance(task, dict) and list(task.keys())[0] == 'set_variables_release':
                        XLRTaskScript.script_jython_define_variable_release(self,phase)
                elif isinstance(task, dict) and 'XLR_task_controlm' in  list(task.keys())[0] :
                    task_XLR_controlm = list(task.keys())[0]
                    if phase not in ['BUILD','UAT','DEV']:
                        XLRGeneric.creation_technical_task(self,phase,'before_deployment')
                    if 'var_jython_date_'+phase not in self.dic_for_check:
                        XLRControlm.script_jython_date_for_XLR_task_controlm(self,phase,self.dict_template[phase]['xlr_id_phase'])
                        self.dic_for_check['var_jython_date_'+phase] = True
                    for value in ['controlm_today']:
                        XLRGeneric.template_create_variable(self,key=value, 
                                                    typev='DateVariable',
                                                    label='date controlm demand',
                                                    description='',
                                                    value=None,
                                                    requiresValue=False,
                                                    showOnReleaseStart=False,
                                                    multiline=False)
                    for XLR_group_task_name,XLR_group_task_controlm_value in task[task_XLR_controlm].items():
                        ctrl_group = False
                        if 'STOP' in XLR_group_task_name or 'START' in XLR_group_task_name: 
                            # print(self.list_xlr_group_task_done)
                            if 'STOP' in XLR_group_task_name : 
                                titlegrp = 'STOP'
                            else: 
                                titlegrp = 'START'
                            if 'XLR_grp_'+titlegrp+'_'+phase not in self.list_xlr_group_task_done :
                                    self.ID_XLR_group_task_grp = XLRGeneric.XLR_group_task(self,
                                        ID_XLR_task= self.dict_template[phase]['xlr_id_phase'],
                                        type_group='SequentialGroup',
                                        title_group='CONTROLM : '+titlegrp,     
                                        precondition='')
                                    self.list_xlr_group_task_done.append('XLR_grp_'+titlegrp+'_'+phase)
                            ctrl_group = True
                        ID_XLR_group_task = XLRGeneric.XLR_group_task(self,
                            ID_XLR_task= self.dict_template[phase]['xlr_id_phase'] if not ctrl_group else self.ID_XLR_group_task_grp,
                            type_group=XLR_group_task_controlm_value['type_group'],
                            title_group='CONTROLM : '+XLR_group_task_name,     
                            precondition='')
                        XLR_group_task_controlm_value.pop('type_group', None)
                        for sub_item_name,sub_item_value in XLR_group_task_controlm_value.items() :
                            sub_group = False
                            if 'folder' in sub_item_value:
                                ID_XLR_sub_group = XLRGeneric.XLR_group_task(self,
                                                    ID_XLR_task= ID_XLR_group_task,
                                                    type_group= sub_item_value['XLR_group_folder_type'],
                                                    title_group= 'CONTROLM : '+sub_item_name,
                                                    precondition='')
                                sub_item_value = sub_item_value['folder']
                                sub_group = True
                                sub_item_value.pop('type_group', None)
                            for folder in sub_item_value:
                                if type(folder) == str:
                                    foldername = folder
                                    folder= {foldername: {}}
                                else:
                                    foldername = list(folder.keys())[0] 
                                ID_XLR_group_for_folder = XLRGeneric.XLR_group_task(self,
                                                    ID_XLR_task= ID_XLR_group_task if not sub_group else ID_XLR_sub_group,
                                                    type_group= 'SequentialGroup',
                                                    title_group= foldername if folder[foldername].get('hold') is None or not folder[foldername]['hold']  else foldername,
                                                    precondition='')
                                #XLRGeneric.template_create_variable(self,key="all_id_"+foldername, typev='MapStringStringVariable', label='', description='', value=None, requiresValue=False, showOnReleaseStart=False, multiline=False)
                                XLRControlm.XLR_plugin_controlm_OrderFolder(self,folder,ID_XLR_group_for_folder)
                                if folder[foldername].get('hold') is not None and folder[foldername]['hold']: 
                                        XLRGeneric.XLR_GateTask(self,phase=phase,
                                                            gate_title='Check result on controlm for folder are order is OK',
                                                            description='',
                                                            cond_title="Check if folder order is ok",
                                                            type_task= "_".join(task_XLR_controlm.split("_")[1:]),
                                                            XLR_ID=ID_XLR_group_for_folder)      
                                
                                if (folder[foldername].get('hold') is None or not folder[foldername]['hold']):
                                    if folder[foldername].get('runnow') is not None: 
                                        XLRControlm.XLR_plugin_controlm_edit_job(self,foldername,'RUN_NOW',ID_XLR_group_for_folder)
                                    XLRControlm.XLR_plugin_controlm_WaitJobStatusById(self,foldername,'Ended OK',ID_XLR_group_for_folder)
                                if (folder[foldername].get('free_folder') is not None and folder[foldername]['free_folder']) \
                                    and \
                                    (folder[foldername].get('hold') is not None and folder[foldername]['hold']):
                                        self.dic_for_check['XLR_group_task_type_free_'+XLR_group_task_name] = True
                                        XLRGeneric.XLR_GateTask(self,phase=phase,
                                                            gate_title='Check result on controlm for folder are order is OK',
                                                            description='',
                                                            cond_title="Check if folder order is ok",
                                                            type_task= "_".join(task_XLR_controlm.split("_")[1:]),
                                                            XLR_ID=ID_XLR_group_for_folder)      
                                        ID_XLR_group_for_folder_free = XLRGeneric.XLR_group_task(self,
                                            ID_XLR_task= ID_XLR_group_for_folder,
                                            type_group='SequentialGroup',
                                            title_group='CONTROLM : '+foldername,
                                            precondition='')
                                        XLRControlm.XLR_plugin_controlm_edit_job(self,foldername,'FREE',ID_XLR_group_for_folder_free)
                                        if folder[foldername].get('runnow') is not None and folder[foldername]['runnow']: 
                                            XLRControlm.XLR_plugin_controlm_edit_job(self,foldername,'RUN_NOW',ID_XLR_group_for_folder_free)
                                        XLRControlm.XLR_plugin_controlm_WaitJobStatusById(self,foldername,'Ended OK',ID_XLR_group_for_folder_free)
                                if self.parameters.get('XLD_ENV_BENCH') is not None and len(self.parameters['XLD_ENV_BENCH']) >1:
                                    task_to_close = '${task_sun_'+task_XLR_controlm+'_'+foldername.replace('${controlm_prefix_BENCH}','')+'_'+phase+'}'
                                else:
                                    task_to_close = '${task_sun_'+task_XLR_controlm+'_'+foldername+'_'+phase+'}'
                                title = 'Check demand controlm: ' + foldername + ' is ok'
                                XLRSun.XLRSun_task_close_sun_task(self,task_to_close=task_to_close, title=title,id_task=ID_XLR_group_for_folder,type_task=task_XLR_controlm,phase=phase)

    


    def template_create_variable(self,key,typev,label,description,value,requiresValue,showOnReleaseStart,multiline ):
        """
        Create a variable in the XLR template.

        Args:
            key (str): Variable name/key
            typev (str): Variable type (StringVariable, PasswordStringVariable, etc.)
            label (str): Display label for the variable
            description (str): Variable description
            value (str): Default value
            requiresValue (bool): Whether value is required at release start
            showOnReleaseStart (bool): Whether to show in release start form
            multiline (bool): Whether to use multiline input

        Creates various types of variables in the XLR template for:
        - Configuration parameters
        - Environment selection
        - Package versions
        - Approval workflow data
        - Runtime customization
        """
        if 'variables' not in self.dict_template:
                        self.dict_template.update({'variables': []})
        everexist = 'no'
        if type(key) != list:
            if any(key in d for d in self.dict_template['variables']):
                everexist = 'yes'
        if everexist == 'no':
                if hasattr(self, 'type_action'):
                    url=self.url_api_xlr+'releases/Applications/'+self.dict_template['template']['xlr_id']+'/variables'
                else: 
                    url=self.url_api_xlr+'releases/Applications/'+self.dict_template['template']['xlr_id']+'/variables'
                try:
                    response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                "id" : None,
                                                "key" : key,
                                                "type" : "xlrelease."+typev,
                                                "requiresValue" : requiresValue,
                                                "showOnReleaseStart" : showOnReleaseStart,
                                                "value" : value,
                                                "label" : label,
                                                "description" : description,
                                                "multiline" : multiline,
                                                "inherited" : False,
                                                "externalVariableValue" : None,
                                                "valueProvider" : None
                                                },verify = False)
                    if 'A variable already exists by key' not in str(response.content):
                            try:
                                self.dict_template['variables'].append({key: response.json()['id']})
                                if 'version' in key:
                                    self.id_variable = response.json()['id']
                            except TypeError as e:
                                self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                                self.logger_error.error("Update Dico 'dict_template' in error for key : "+ key+" with value: "+value )
                                self.logger_error.error("TypeError : "+str(e))
                                self.logger_error.error("Exception : "+str(response.content))
                                sys.exit(0)
                            except  Exception as e:
                                self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                                self.logger_error.error("Update Dico 'dict_template' in error for key : "+ key+" with value: "+value )
                                self.logger_error.error("Exception : "+str(e))
                                self.logger_error.error("Exception : "+str(response.content))
                                sys.exit(0)
                            if 'password'in key or 'Token' in key:
                                value = 'secret'
                            if value =='':
                                value = 'Empty'
                            if label == '':
                                label = 'No Label'

                            if key in  ['list_actif_package_latest']:
                                    self.variables_manage.update({'list_actif_package_latest': response.json()['id']})
                                    self.update_variable(self,'variables_manage',self.variables_manage,False,False )
                            self.logger_detail.info("CREATE VARIABLE : "+key+" with label : " + label +" --- XLD type variable : "+ typev+ " With value: "+str(value))
                    elif 'A variable already exists by key' in str(response.content):
                         pass
                    else:
                        response.raise_for_status()
                except requests.exceptions.RequestException as e:
                        self.logger_error.error("Detail ERROR: CREATE VARIABLE : "+key+" with label : " + label +" --- XLD type variable : "+ typev+ " With value: "+str(value))
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(response.content)
                        self.logger_error.error(e)
                        sys.exit(0)
        return self.dict_template
    def create_variable_list_box_package(self,key,value,requiresValue,showOnReleaseStart):
        url=self.url_api_xlr+'releases/Applications/'+self.dict_template['template']['xlr_id']+'/variables'
        try:
            response_forlist_box= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                        "key" : key,
                                        "label": key,
                                        "type" : "xlrelease.ListStringVariable",
                                        "requiresValue" : requiresValue,
                                        "showOnReleaseStart" : showOnReleaseStart,
                                        "valueProvider" : {
                                                        "id" : "",
                                                        "type": "xlrelease.ListOfStringValueProviderConfiguration",
                                                        "values": value
                                                            }
                                        },verify = False)
            if 'A variable already exists by key' in str(response_forlist_box.content):
                 pass
            else:
                response_forlist_box.raise_for_status()

            if 'A variable already exists by key' not in str(response_forlist_box.content):
                    try:
                        if "variables" not in self.dict_template:
                           self.dict_template['variables'] = []
                        self.dict_template['variables'].append({key: response_forlist_box.json()['id']})
                    except TypeError as e:
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Update Dico 'dict_template' in error for key : "+ key+" with value: "+str(value) )
                        self.logger_error.error("TypeError : "+str(e))
                        sys.exit(0)
                    except  Exception as e:
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Update Dico 'dict_template' in error for key : "+ key+" with value: "+str(value) )
                        self.logger_error.error("Exception : "+str(e))
                        self.logger_error.error(response_forlist_box.content)
                        sys.exit(0)
            self.logger_detail.info("CREATE VARIABLE LISTBOX PACKAGE : "+key+" with label : " + key +" --- XLD type variable : ListStringVariable . With value : "+ str(value))
        except requests.exceptions.RequestException as e:
                # Affichage d'un message d'erreur en cas d'échec de la requête
                        self.logger_error.error("CREATE VARIABLE LISTBOX PACKAGE : "+key+" with label : " + key +" --- XLD type variable : ListStringVariable . With value : "+ str(value))
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    def create_variable_list_box_package_from_list_variable(self,key,value,requiresValue,showOnReleaseStart):
        url=self.url_api_xlr+'releases/Applications/'+self.dict_template['template']['xlr_id']+'/variables'
        try:
            response_forlist_box= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                        "key" : key,
                                        "label": key,
                                        "type" : "xlrelease.ListStringVariable",
                                        "requiresValue" : requiresValue,
                                        "showOnReleaseStart" : showOnReleaseStart,
                                        "valueProvider" : {
                                                        "id" : "",
                                                        "type": "xlrelease.ListOfStringValueProviderConfiguration",
                                                        "variableMapping": {
                                                            "values": value
                                                        }
                                                            }
                                        },verify = False)
            if 'A variable already exists by key' in str(response_forlist_box.content):
                 pass
            else:
                response_forlist_box.raise_for_status()

            if 'A variable already exists by key' not in str(response_forlist_box.content):
                    try:
                        if "variables" not in self.dict_template:
                           self.dict_template['variables'] = []
                        self.dict_template['variables'].append({key: response_forlist_box.json()['id']})
                    except TypeError as e:
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Update Dico 'dict_template' in error for key : "+ key+" with value: "+str(value) )
                        self.logger_error.error("TypeError : "+str(e))
                        sys.exit(0)
                    except  Exception as e:
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Update Dico 'dict_template' in error for key : "+ key+" with value: "+str(value) )
                        self.logger_error.error("Exception : "+str(e))
                        self.logger_error.error(response_forlist_box.content)
                        sys.exit(0)
            self.logger_detail.info("CREATE VARIABLE LISTBOX PACKAGE : "+key+" with label : " + key +" --- XLD type variable : ListStringVariable . With value : "+ str(value))
        except requests.exceptions.RequestException as e:
                # Affichage d'un message d'erreur en cas d'échec de la requête
                        self.logger_error.error("CREATE VARIABLE LISTBOX PACKAGE : "+key+" with label : " + key +" --- XLD type variable : ListStringVariable . With value : "+ str(value))
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    def create_variable_list_box_env(self,key,value):
        if key == 'env_BENCH':
              label = key.split('env_')[1]
              list_value_phase = []
              for item in value:
                    list_value_phase.append(item.split(';')[0])
        elif 'Choice_ENV' in key:
              label = key
              list_value_phase = value
        else:
              list_value_phase = value
              label = key.split('env_')[1]
        url=self.url_api_xlr+'releases/Applications/'+self.dict_template['template']['xlr_id']+'/variables'
        try:
            response_forlist_box= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                    "key" : key,
                                    "label": label,
                                    "type" : "xlrelease.StringVariable",
                                    "requiresValue" : False,
                                    "showOnReleaseStart" : True,
                                    "valueProvider" : {
                                                    "id" : "",
                                                    "type": "xlrelease.ListOfStringValueProviderConfiguration",
                                                    "values": list_value_phase
                                                        }
                                    },verify = False)

            if 'A variable already exists by key' in str(response_forlist_box.content):
                 pass
            else:
                response_forlist_box.raise_for_status()
                if response_forlist_box.content:
                            if 'id' in response_forlist_box.json():
                                self.logger_detail.info("CREATE VARIABLE LISTBOX : "+key +" --- label "+label+" with value "+ str(list_value_phase))
        except requests.exceptions.RequestException as e:
                        self.logger_error.error("CREATE VARIABLE LISTBOX : "+key +" --- label "+label+" with value "+ str(list_value_phase))
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(response_forlist_box.content)
                        self.logger_error.error(e)
                        sys.exit(0)
    def XLR_group_task(self,ID_XLR_task,type_group,title_group,precondition):
        
        response= requests.post(self.url_api_xlr+'tasks/'+ID_XLR_task+'/tasks', headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                "id" : "null",
                                "type" : "xlrelease."+type_group,
                                "title" : title_group,
                                "status" : "PLANNED",
                                "precondition": precondition,
                                },verify = False)
        return response.json()['id']
    def find_xlr_folder(self):
        url=self.url_api_xlr+"folders/find?byPath="+self.parameters['general_info']['xlr_folder']
        try :
            reponse= requests.get(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api),verify = False)
            if "Could not find folder" in str(reponse.content):
                    self.logger_cr.info("XLR folder : "+self.parameters['general_info']['xlr_folder'] +" Not found.")
                    self.logger_error.error("Detail ERROR")
                    self.logger_error.error("Error call api : "+url)
                    self.logger_error.error('The folder :'+self.parameters['general_info']['xlr_folder']+' doesn t exit')
                    sys.exit(0)
            reponse.raise_for_status()
            self.logger_cr.info("XLR folder search: "+self.parameters['general_info']['xlr_folder']+" found.")
            if 'template' not in self.dict_template:
                    try:
                        self.dict_template.update({'template': {'xlr_folder': reponse.json()['id']}})
                    except TypeError as e:
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Update Dico 'dict_template' in error : "+url)
                        self.logger_error.error( e)
                        sys.exit(0)
                    except  Exception as e:
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Update Dico 'dict_template' in error : "+url)
                        self.logger_error.error( e)
                        sys.exit(0)
            else:
                    try:
                            self.dict_template['template'].update({'xlr_folder': reponse.json()['id']})
                    except TypeError as e:
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Update Dico 'dict_template' in error : "+url)
                        self.logger_error.error( e)
                        sys.exit(0)
        except requests.exceptions.RequestException as e:
            # Affichage d'un message d'erreur en cas d'échec de la requête
            self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
            self.logger_error.error("Error call api : "+url)
            self.logger_error.error("Detail ERROR")
            self.logger_error.error(reponse.content)
            self.logger_error.error( e)
            sys.exit(0)
    def add_task_user_input(self,phase,type_userinput,link_task_id):
        for value in [phase +'_username_' + type_userinput,phase + '_password_'+ type_userinput]:
            if 'password' in value:
                self.template_create_variable(key=value, typev='PasswordStringVariable', label=value, description='', value='', requiresValue=False, showOnReleaseStart=False, multiline=False)
            else:
                if 'controlm' in type_userinput:
                    self.template_create_variable(key=value, typev='StringVariable', label=value, description='', value=self.ops_username_controlm, requiresValue=False, showOnReleaseStart=False, multiline=False)
                elif 'windows' in type_userinput:
                    self.template_create_variable(key=value, typev='StringVariable', label=value, description='', value=self.ops_username_windows, requiresValue=False, showOnReleaseStart=False, multiline=False)
                else:
                    self.template_create_variable(key=value, typev='StringVariable', label=value, description='', value='', requiresValue=False, showOnReleaseStart=False, multiline=False)

        variables_userinput = []
        l_name_variable= []
        for value in self.dict_template['variables']:
            if list(value.keys())[0] == phase+'_username_'+type_userinput:
                variables_userinput.append(value[phase+'_username_'+type_userinput])
                l_name_variable.append(phase+'_username_'+type_userinput)
            elif list(value.keys())[0] == phase+'_password_'+type_userinput:
                    variables_userinput.append(value[phase+'_password_'+type_userinput])
                    l_name_variable.append(phase+'_password_'+type_userinput)
        url=self.url_api_xlr+'tasks/'+link_task_id +'/tasks'
        # print('ppppp')
        # print(link_task_id)
        try:
            response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : "null",
                            "type" : "xlrelease.UserInputTask",
                            "title" : "Please enter user password for "+ type_userinput+' on '+ phase ,
                            "status" : "PLANNED",
                            "variables": variables_userinput
                            },verify = False)
            # print(response.content)
            response.raise_for_status()
            if response.content:
                if 'id' in response.json():
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        self.logger_cr.info("ON PHASE : "+ phase+" --- Add task : 'user_input - "+type_userinput+"' with precondition : "+ precondition)
                    else:
                        self.logger_cr.info("ON PHASE : "+ phase+" --- Add task : 'user_input - "+type_userinput+"'")
                    for variable in l_name_variable:
                        if phase not in self.dict_template:
                                self.dict_template.update({phase: {variable: response.json()['id']}})
                        else:
                                self.dict_template[phase].update({variable: response.json()['id']})
        except requests.exceptions.RequestException as e:
                    self.logger_error.error("Detail ERROR: ON PHASE : "+ phase+" ---Add task : user_input - "+type_userinput)
                    self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                    self.logger_error.error("Error call api : "+url)
                    self.logger_error.error(response.content)
                    self.logger_error.error(e)
                    sys.exit(0)
        return self.dict_template
    def add_variable_release_ListStringVariable(self,key,value,requiresValue,showOnReleaseStart):
            url=self.url_api_xlr+'releases/Applications/'+self.dict_template['template']['xlr_id']+'/variables'
            # print(type(value))
            response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                        "id" : None,
                                        "key" : key,
                                        "type" : "xlrelease.ListStringVariable",
                                        "requiresValue" : requiresValue,
                                        "showOnReleaseStart" : showOnReleaseStart,
                                        "valueProvider" : {
                                                    "id" : "",
                                                    "type": "xlrelease.ListOfStringValueProviderConfiguration",
                                                    "values": value
                                                        },
                                        "inherited" : False,
                                        },verify = False)
            # print(response.content)
            if 'A variable already exists' not in str(response.content):
                if 'variables' not in self.dict_template:
                        self.dict_template.update({'variables': [{key: response.json()['id']}]})
                else:
                            self.dict_template['variables'].append({key: response.json()['id']})     
    def find_template(self):
        url_find_template=self.url_api_xlr+"templates?title="+self.parameters['general_info']['name_release']
        response= requests.get(url_find_template, headers=self.header,auth=(self.ops_username_api, self.ops_password_api),verify = False)
        for template in response.json():
            if template['title'] ==  self.parameters['general_info']['name_release']:
                if 'template' not in self.dict_template:
                        self.dict_template.update({'template': {'xlr_id': (response.json()[0]['id']).replace("Applications/", "")}})
                else: 
                        self.dict_template['template'].update({'xlr_id': (response.json()[0]['id']).replace("Applications/", "")})
        
        for phase in response.json()[0]['phases']:
                if phase['title'] not in self.dict_template:
                        self.dict_template.update({ phase['title']: {'xlr_id_phase': phase['id']}})
                else: 
                        self.dict_template[phase['title']].update({'xlr_id_phase': phase['id']})
        return self.dict_template
    def XLR_GateTask(self,phase,gate_title,description,cond_title,type_task,XLR_ID):
        description =''   
        try:
            response= requests.post(self.url_api_xlr+'tasks/'+XLR_ID+'/tasks', headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : "null",
                            "type" : "xlrelease.GateTask",
                            "title" : gate_title,
                            "description": description,
                            },verify = False)
            response.raise_for_status()
            
            if response.content:
                    if 'id' in response.json():
                            self.logger_cr.info("ON PHASE : "+ phase+" --- Add task : 'GATE' : "+type_task+"'")

        except requests.exceptions.RequestException as e:
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase+" --- Add task : 'GATE' : "+type_task)
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+self.url_api_xlr+'tasks/'+XLR_ID+'/tasks')
                        self.logger_error.error(e)
                        self.logger_error.error( response.content)
                        sys.exit(0)
        if cond_title != None:
            url_create_condition=self.url_api_xlr+'tasks/'+response.json()['id']+'/conditions'
            try:
                reponse_create_conditione= requests.post(url_create_condition, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                    "title": cond_title,
                                    "checked": False,
                                },verify = False)
                reponse_create_conditione.raise_for_status()
            except requests.exceptions.RequestException as e:
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase+" ---Add task : condition to GATE : "+type_task)
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url_create_condition)
                        self.logger_error.error(reponse_create_conditione.content)
                        self.logger_error.error(e)
                        sys.exit(0)
    def launch_script_windows(self,phase,grp_id_task,sunscript_windows_item,type_userinput,index):
        for value in self.dict_template['variables']:
            if list(value.keys())[0] == phase+'_username_'+type_userinput:
                username_launch_script_windows = phase+'_username_'+type_userinput
            elif list(value.keys())[0] == phase+'_password_'+type_userinput:
                password_launch_script_windows = phase+'_password_'+type_userinput
        urtcontrolmfolderdemand=self.url_api_xlr+'tasks/'+ grp_id_task+'/tasks'
        reponse_add_webhook_demand_folder= requests.post(urtcontrolmfolderdemand, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.CustomScriptTask",
                                                            "title" : list(sunscript_windows_item.keys())[0],
                                                            "locked" : True,
                                                            "pythonScript": {
                                                                        "type":"remoteScript.WindowsSmb",
                                                                        "id" : "null",
                                                                        "script": sunscript_windows_item[list(sunscript_windows_item.keys())[0]]['script'],
                                                                        "remotePath": sunscript_windows_item[list(sunscript_windows_item.keys())[0]]['remotePath'],
                                                                        "temporaryDirectoryPath": "",
                                                                        "address": sunscript_windows_item[list(sunscript_windows_item.keys())[0]]['address'],
                                                                        "username": "${"+phase+"_username_"+type_userinput+"}",
                                                                        "password": "${"+phase+"_password_"+type_userinput+"}",
                                                                        "connectionType": 'WINRM_NATIVE'
                                                                        # 'result': 'orderjob'
                                                                        }
                                                            },verify = False)
        if 'id' in reponse_add_webhook_demand_folder.json():
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : WindowsSmb : "+list(sunscript_windows_item.keys())[0]+" with script : "+sunscript_windows_item[list(sunscript_windows_item.keys())[0]]['script']+" with precondition : "+ precondition) 
                    else:
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : WindowsSmb : "+list(sunscript_windows_item.keys())[0]+" with script : "+sunscript_windows_item[list(sunscript_windows_item.keys())[0]]['script'] )  
    def launch_script_linux(self,phase,grp_id_task,sunscript_linux_item,type_userinput,index):
        for value in self.dict_template['variables']:
            if list(value.keys())[0] == phase+'_username_'+type_userinput:
                username_launch_script_linux = phase+'_username_'+type_userinput
            elif list(value.keys())[0] == phase+'_password_'+type_userinput:
                password_launch_script_linux = phase+'_password_'+type_userinput
        url=self.url_api_xlr+'tasks/'+ grp_id_task+'/tasks'
        response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.CustomScriptTask",
                                                            "title" : list(sunscript_linux_item.keys())[0],
                                                            "locked" : True,
                                                            "pythonScript": {
                                                                        "type":"remoteScript.Unix",
                                                                        "id" : "null",
                                                                        "script": sunscript_linux_item[list(sunscript_linux_item.keys())[0]]['script'],
                                                                        "remotePath": sunscript_linux_item[list(sunscript_linux_item.keys())[0]]['remotePath'],
                                                                        "temporaryDirectoryPath": sunscript_linux_item[list(sunscript_linux_item.keys())[0]]['remotePath'],
                                                                        "address": sunscript_linux_item[list(sunscript_linux_item.keys())[0]]['address'],
                                                                        "username": "${"+username_launch_script_linux+"}",
                                                                        "password": "${"+password_launch_script_linux+"}",
                                                                        "scriptIgnoreVariableInterpolation": True,
                                                                        "remoteCharacterEncoding": "UTF-8",
                                                                        "port": 22,
                                                                        "privateKey": None,
                                                                        "sudoUsername": None,
                                                                        "suUsername": None,
                                                                        "suPassword": None,
                                                                        "connectionType": "SCP",
                                                                        "sudo": True
                                                                        }
                                                            },verify = False)
        if 'id' in response.json():
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : remoteScript.Unix : "+list(sunscript_linux_item.keys())[0]+" with script : "+sunscript_linux_item[list(sunscript_linux_item.keys())[0]]['script']+" with precondition : "+ precondition) 
                    else:
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : remoteScript.Unix : "+list(sunscript_linux_item.keys())[0]+" with script : "+sunscript_linux_item[list(sunscript_linux_item.keys())[0]]['script'] )                  
    
    def dict_value_for_tempalte_technical_task(self):
        ## Creation de variables permettant de manager les task OPS et DBA si 'technical_task_list' est défini dans le fichier YAML
            ##Creation d une variable de type dico permettant de savoir ce que le tempalte va manager et cette variable sera utiliser 
            ## pour creer les task XLR selon leur positionnement : before_deployment,before_xldeploy, after_xldeploy,after_deployment
            self.dict_value_for_template_technical_task = {}
            if self.parameters.get('technical_task_list') is not None:
                   self.dict_value_for_template_technical_task['technical_task'] = {}
                   lsit_technical_task = []
                   for technical_task in self.parameters['technical_task_list']:
                       if self.parameters['technical_task_list'].get(technical_task) is not None:
                            if  technical_task not in self.dict_value_for_template_technical_task['technical_task'] :
                                    self.dict_value_for_template_technical_task['technical_task'][technical_task]= {}
                            dict_count={}
                            dict_count['count_task_dba_factor']= 1
                            dict_count['count_task_dba_other'] = 1
                            dict_count['count_task_ops'] = 1
                            for task in self.parameters['technical_task_list'][technical_task]:
                                    ##selon le type de task on va creer les variable qui seront afficher au start de la release
                                    ## task_ops task_dba_other task_dba_factor
                                    if 'task_dba_factor' in task :
                                        if technical_task == 'before_deployment':
                                            title = 'Action DBA FACTOR SQL '+ str(dict_count['count_task_dba_factor'])+' before STOP '+self.parameters['general_info']['appli_name']
                                        elif technical_task == 'before_xldeploy':
                                            title = 'Action DBA FACTOR SQL '+ str(dict_count['count_task_dba_factor'])+' before XLD'
                                        elif technical_task == 'after_xldeploy':
                                            title = 'Action DBA FACTOR SQL '+ str(dict_count['count_task_dba_factor'])+' after XLD'
                                        elif technical_task == 'after_deployment':
                                            title = 'Action DBA FACTOR SQL '+ str(dict_count['count_task_dba_factor'])+' after START '+self.parameters['general_info']['appli_name']
                                        self.dict_value_for_template_technical_task['technical_task'][technical_task]['task_dba_factor_'+str(dict_count['count_task_dba_factor'])] = {'sun_title': title,
                                                                                                                'xlr_item_name': 'Action DBA FACTOR SQL '+ str(dict_count['count_task_dba_factor']),
                                                                                                                'xlr_variable_name': technical_task+'_task_dba_factor_'+str(dict_count['count_task_dba_factor']),
                                                                                                                'xlr_sun_task_variable_name': technical_task+"_task_sun_task_dba_factor_"+str(dict_count['count_task_dba_factor']) }
                                        if self.parameters['general_info']['technical_task_mode'] != 'listbox':
                                            self.template_create_variable(key=technical_task+'_task_dba_factor_'+str(dict_count['count_task_dba_factor']), typev='StringVariable', label=title, description='', value='', requiresValue=False, showOnReleaseStart=True, multiline=True)
                                            lsit_technical_task.append(technical_task+'_task_dba_factor_'+str(dict_count['count_task_dba_factor']))
                                        dict_count['count_task_dba_factor']+=1

                                    elif  'task_dba_other' in task :
                                        if technical_task == 'before_deployment':
                                            title = 'Action DBA '+ str(dict_count['count_task_dba_other'])+' before STOP '+self.parameters['general_info']['appli_name']
                                        elif technical_task == 'before_xldeploy':
                                            title = 'Action DBA '+ str(dict_count['count_task_dba_other'])+' before XLD'
                                        elif technical_task == 'after_xldeploy':
                                            title = 'Action DBA '+ str(dict_count['count_task_dba_other'])+' after XLD'
                                        elif technical_task == 'after_deployment':
                                            title = 'Action DBA '+ str(dict_count['count_task_dba_other'])+' after START '+self.parameters['general_info']['appli_name']
                                        self.dict_value_for_template_technical_task['technical_task'] [technical_task]['task_dba_other_'+str(dict_count['count_task_dba_other'])] = {'sun_title': title,
                                                                                                                'xlr_item_name': 'Action DBA '+ str(dict_count['count_task_dba_other']),
                                                                                                                'xlr_variable_name': technical_task+'_task_dba_other_'+str(dict_count['count_task_dba_other']),
                                                                                                                'xlr_sun_task_variable_name': technical_task+"_task_sun_task_dba_other_"+str(dict_count['count_task_dba_other']) }
                                        if self.parameters['general_info']['technical_task_mode'] != 'listbox':
                                            self.template_create_variable(key=technical_task+'_task_dba_other_'+str(dict_count['count_task_dba_other']), typev='StringVariable', label=title, description='', value='', requiresValue=False, showOnReleaseStart=True, multiline=True)
                                            lsit_technical_task.append(technical_task+'_task_dba_other_'+str(dict_count['count_task_dba_other']))
                                        dict_count['count_task_dba_other'] +=1

                                    elif 'task_ops' in task:
                                        if technical_task == 'before_deployment':
                                            title = 'Action OPS '+ str(dict_count['count_task_ops'])+' before STOP '+self.parameters['general_info']['appli_name']
                                        elif technical_task == 'before_xldeploy':
                                            title = 'Action OPS '+ str(dict_count['count_task_ops'])+' before XLD'
                                        elif technical_task == 'after_xldeploy':
                                            title = 'Action OPS '+ str(dict_count['count_task_ops'])+' after XLD'
                                        elif technical_task == 'after_deployment':
                                            title = 'Action OPS '+ str(dict_count['count_task_ops'])+' after START '+self.parameters['general_info']['appli_name']
                                        elif technical_task == 'before_action':
                                            title = 'Action OPS '+ str(dict_count['count_task_ops'])+' before_action'
                                        elif technical_task == 'after_action':
                                            title = 'Action OPS '+ str(dict_count['count_task_ops'])+' after_action'
                                        self.dict_value_for_template_technical_task['technical_task'] [technical_task]['task_ops_'+str(dict_count['count_task_ops'])] = {'sun_title': title,
                                                                                                                'xlr_item_name': 'Action OPS '+ str(dict_count['count_task_ops']),
                                                                                                                'xlr_variable_name': technical_task+'_task_ops_'+str(dict_count['count_task_ops']),
                                                                                                                'xlr_sun_task_variable_name': technical_task+"_task_sun_task_ops_"+str(dict_count['count_task_ops']) }
                                        if self.parameters['general_info']['technical_task_mode'] != 'listbox':
                                            if self.parameters['general_info']['type_template'] != 'SEMI_DYNAMIC':
                                                self.template_create_variable(key=technical_task+'_task_ops_'+str(dict_count['count_task_ops']), typev='StringVariable', label=title, description='', value='', requiresValue=False, showOnReleaseStart=True, multiline=True)
                                            else:
                                                self.template_create_variable(key=technical_task+'_task_ops_'+str(dict_count['count_task_ops']), typev='StringVariable', label=title, description='', value='', requiresValue=False, showOnReleaseStart=False, multiline=True)
                                            lsit_technical_task.append(technical_task+'_task_ops_'+str(dict_count['count_task_ops']))
                                        dict_count['count_task_ops'] +=1
            self.update_variable('dict_value_for_template',self.dict_value_for_template,False,False )
            ## Creation d une variable de type list si technical_task_mode ==list
            if self.parameters.get('technical_task_list') is not None and len(self.dict_value_for_template_technical_task['technical_task'] ) != 0:
                for type_technical_task in self.dict_value_for_template_technical_task['technical_task'] :
                            liste_title = []
                            for tilte in self.dict_value_for_template_technical_task['technical_task'][type_technical_task]:
                                liste_title.append(self.dict_value_for_template_technical_task['technical_task'][type_technical_task][tilte]['xlr_item_name'])
                            if self.parameters['general_info']['technical_task_mode'] == 'string':
                                pass
                            else:
                                self.add_variable_release_ListStringVariable(key=type_technical_task,value=liste_title,requiresValue=False,showOnReleaseStart=True)
            return self.dict_value_for_template_technical_task
    def creation_technical_task(self,phase,cat_technicaltask):
        if len(self.dict_value_for_template_technical_task) != 0:
            if  'technical_task' in self.dict_value_for_template_technical_task:
              if cat_technicaltask in self.dict_value_for_template_technical_task['technical_task'] :
                if cat_technicaltask+'_done_'+phase not in self.list_technical_task_done:
                    if  self.dict_value_for_template_technical_task['technical_task'] .get(cat_technicaltask) is not None:
                        for technical_task in  self.dict_value_for_template_technical_task['technical_task'] [cat_technicaltask]:
                            if  'task_dba_factor' in technical_task or 'task_dba_other' in technical_task:
                                precondition = ''
                                self.XLRSun_check_status_sun_task(phase,self.dict_value_for_template_technical_task['technical_task'] [cat_technicaltask][technical_task]['xlr_sun_task_variable_name']+"_"+phase,technical_task,cat_technicaltask,precondition)
                            elif 'task_ops' in technical_task:
                                title = self.dict_value_for_template_technical_task['technical_task'] [cat_technicaltask][technical_task]['sun_title']
                                precondition = ''
                                self.grp_id = self.XLR_group_task(
                                        ID_XLR_task= self.dict_template[phase]['xlr_id_phase'],
                                        type_group="SequentialGroup",
                                        title_group=title,     
                                        precondition='')
                                self.XLR_GateTask(phase=phase,
                                                gate_title=title,
                                                description="See Change to action OPS",
                                                cond_title= None,
                                                type_task='check_sun_by_ops',
                                                XLR_ID=self.grp_id)
                                if self.parameters['general_info']['type_template'] != 'SEMI_DYNAMIC' and 'INC' not in self.parameters['general_info']['type_template']:
                                    if phase != 'DEV' or phase != 'UAT' :
                                        task_to_close = '${'+self.dict_value_for_template_technical_task['technical_task'] [cat_technicaltask][technical_task]['xlr_sun_task_variable_name']+"_"+phase+'}'
                                        self.XLRSun_task_close_sun_task(task_to_close,task_to_close,self.grp_id,'task_ops',phase)
        self.list_technical_task_done.append(cat_technicaltask+'_done_'+phase)
    def delete_template(self):
        """
        Delete existing XLR template if it exists.

        Searches for and deletes any existing template with the same name
        to ensure clean template creation. This prevents conflicts when
        regenerating templates and ensures the latest configuration is used.

        The deletion is performed by:
        1. Searching for templates by name
        2. Checking template status
        3. Deleting found templates
        4. Logging the deletion operation
        """
        url_find_template=self.url_api_xlr+"templates?title="+self.parameters['general_info']['name_release']
        try:
            response= requests.get(url_find_template, headers=self.header,auth=(self.ops_username_api, self.ops_password_api),verify = False)
            if "Could not find folder" in str(response.content):
                    self.logger_error.error("Detail ERROR")
                    self.logger_error.error("Error call api : "+url_find_template)
                    self.logger_error.error('The folder :'+self.parameters['general_info']['xlr_folder']+' doesn t exit')
                    sys.exit(0)
            response.raise_for_status()
            if response.content:
                if len(response.json()) == 0:
                                self.logger_cr.info("SEARCH TEMPLATE : No template find with name: "+self.parameters['general_info']['name_release'])
                else:
                                self.logger_cr.info("SEARCH TEMPLATE : Template : "+ self.parameters['general_info']['name_release'] +" find.")
        except requests.exceptions.RequestException as e:
                    self.logger_error.error("Error call api : "+url_find_template)
                    self.logger_error.error("Detail ERROR")
                    self.logger_error.error(e)
                    sys.exit(0)
        # with open('data.json', 'w') as file:
        #     json.dump(response.json(), file)
        count_template = 0
        template_present = 'no'
        for template in response.json():
             if template['title'] == self.parameters['general_info']['name_release']:
                template_present = 'yes'
                template_id_to_delete = template['id']
                count_template += 1
        if template_present == 'yes' and count_template == 1:
                    delete_template=self.url_api_xlr+"templates/"+template_id_to_delete
                    header = {'content-type': 'application/json','Accept': 'application/json' }
                    try:
                        response_delete = requests.delete(delete_template, headers=header,auth=(self.ops_username_api, self.ops_password_api),verify = False)
                        if response_delete.status_code == 204:
                                    self.logger_cr.info("DELETE TEMPLATE : DONE")
                        response_delete.raise_for_status()
                    except requests.exceptions.RequestException as e:
                        # Affichage d'un message d'erreur en cas d'échec de la requête
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+delete_template)
                        self.logger_error.error("Detail ERROR")
                        self.logger_error.error( e)
                        sys.exit(0)
        elif count_template  > 1:
            self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
            self.logger_error.error("DELETE TEMPLATE : There is more than one template with name: "+ self.parameters['general_info']['name_release'] )
            sys.exit(0)
        elif count_template == 0:
             pass
    def delete_phase_default_in_template(self):
        url_delete_phase_default_in_template=self.url_api_xlr+"phases/search?phaseTitle=New Phase&releaseId="+self.dict_template['template']['xlr_id']+"&phaseVersion=ALL"
        response= requests.get(url_delete_phase_default_in_template, headers=self.header,auth=(self.ops_username_api, self.ops_password_api),verify = False)
        # sys.exit(0)releases/
        if len(response.json()) != 0:
            delete_phase=self.url_api_xlr+"phases/"+response.json()[0]['id']
            requests.delete(delete_phase, headers=self.header,auth=(self.ops_username_api, self.ops_password_api),verify = False)
    def python_technical_task(self,phase):
        if  self.parameters.get('technical_task_list') is not None:
            if self.parameters['general_info']['technical_task_mode'] == 'listbox':
                self.XLRJythonScript_release_delete_technical_task_ListStringVariable(self,phase)
            elif self.parameters['general_info']['technical_task_mode'] == 'string':
                self.XLRJythonScript_dynamic_release_delete_technical_task_StringVariable(self,phase)
    def create_variable_bolean_requires(self,value,type_env_boolean):
        url=self.url_api_xlr+'releases/Applications/'+self.dict_template['template']['xlr_id']+'/variables'
        requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                    "id" : None,
                                    "key" : value,
                                    "type" : "xlrelease.BooleanVariable",
                                    "requiresValue" : False,
                                    "showOnReleaseStart" : True,
                                    "label" : value,
                                    "description" : value,
                                    "multiline" : False,
                                    "inherited" : False,
                                    "externalVariableValue" : None,
                                    "valueProvider" : None
                                    },verify = False)
    def xld_get_version_deploy(self,package_name,phase,grp_id_xldeploy,step):
        if phase == 'DEV':
                xld_prefix_env = 'D'
                if self.parameters.get('XLD_ENV_DEV') is not None:
                    xld_env = '${env_'+phase+'}'
                else: 
                    xld_env = 'DEV'
                xld_directory_env = 'DEV'
        elif phase == 'UAT':
                xld_prefix_env = 'U'
                if self.parameters.get('XLD_ENV_UAT') is not None:
                    xld_env = '${env_'+phase+'}'
                else: 
                    xld_env = 'UAT'
                xld_directory_env = 'UAT'
        elif phase == 'BENCH':
                if self.parameters.get('XLD_ENV_BENCH') is not None  and len(self.parameters['XLD_ENV_BENCH']) >1:
                        xld_prefix_env = "${controlm_prefix_BENCH}"
                elif 'NXFFA' in self.parameters['general_info']['iua']:
                        xld_prefix_env = 'Q'
                else:
                        xld_prefix_env = 'B'
                if self.parameters.get('XLD_ENV_BENCH') is not None:
                    xld_env = '${env_'+phase+'}'
                else: 
                    xld_env = 'BCH'
                xld_directory_env = 'BCH'
        elif phase == 'PRODUCTION':
                xld_prefix_env = 'P'
                if self.parameters.get('XLD_ENV_PRODUCTION') is not None:
                    xld_env = '${env_'+phase+'}'
                else: 
                    xld_env = 'PRD'
                xld_directory_env = 'PRD'

        package_value = next(package for package in self.parameters['template_liste_package'] if package_name in package)
        if 'APPCODE' in self.parameters['general_info']['iua'] and phase == 'BENCH':
            value_env = ''
            if package_name == 'Interfaces':
                value = 'INT'
            elif package_name in ['Interface_summit','Interface_summit_COF','Interface_TOGE','Interface_TOGE_ACK','Interface_NON_LOAN_US','DICTIONNAIRE','Interface_MOTOR','Interface_ROAR_ACK','Interface_ROAR']:
                value = 'INT'
                value_env ='_NEW'
            elif package_name == 'Scripts':
                value = 'SCR'
            elif package_name == 'SDK':
                value = 'SDK'
            elif package_name == 'App':
                value = 'APP'
            elif 'FILEBEAT' in package_name:
                value = 'THEIA'

            tempo_XLD_environment_path = 'Environments/PFI/APPCODE_APPLICATION/7.6/<ENV>/${BENCH_APPCODE}/${BENCH_APPCODE}_01/'+value+'/<xld_prefix_env>APPCODE_'+value+'_<XLD_env>_01_ENV'+value_env
            xld_path_deploymentEnvironment = tempo_XLD_environment_path.replace('<XLD_env>',xld_env).replace('<xld_prefix_env>',xld_prefix_env).replace('<ENV>',xld_directory_env)
        else:
            xld_path_deploymentEnvironment = self.parameters['template_liste_package'][package_name]['XLD_environment_path'].replace('<XLD_env>',xld_env).replace('<xld_prefix_env>',xld_prefix_env).replace('<ENV>',xld_directory_env)

        url_add_task_xldeploy_auto=self.url_api_xlr+'tasks/'+grp_id_xldeploy +'/tasks'
        if self.parameters['template_liste_package'][package_name].get('XLD_application_name') is not None:
            applicationName = self.parameters['template_liste_package'][package_name]['XLD_application_name']
        else: 
            applicationNametmp = self.parameters['template_liste_package'][package_name]['XLD_application_path']
            if applicationNametmp.endswith('/'):
                applicationName = applicationNametmp.rstrip('/').split('/')[-1]
            else:
                applicationName = applicationNametmp
        reponse_add_task_xldeploy_auto= requests.post(url_add_task_xldeploy_auto, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                        "id" :  None,
                                        "type" : "xlrelease.CustomScriptTask",
                                        "title" : "Get package version "+package_name,
                                        "status" : "PLANNED",
                                        "locked" : False,
                                        "taskRecoverOp": "RUN_SCRIPT",
                                        "taskFailureHandlerEnabled": True,
                                        "failuresCount": 0,
                                        "failureHandler": "releaseVariables['version_deployed_"+package_name+"_"+phase+"_"+step+"'] = 'Not Deploy'\n"
                                                          "taskApi.skipTask(getCurrentTask().getId(), 'Package "+package_name+" not deploy on "+phase+"')\n",
                                        "variableMapping": {
                                                    "pythonScript.applicationId": '${version_deployed_'+package_name+'_'+phase+'_'+step+'}'
                                                            },
                                        "waitForScheduledStartDate": True,
                                        "pythonScript": {
                                                "xldeployServer": "Configuration/Custom/XLDeploy PFI PROD",
                                                "type": "xldeploy.GetLastVersionDeployedTask",
                                                "id":  None,
                                                "username": "${"+phase+"_username_xldeploy}",
                                                "password": "${"+phase+"_password_xldeploy}",
                                                "environmentId": xld_path_deploymentEnvironment,
                                                "applicationName": applicationName,
                                                }
                                        },verify = False)
        reponse_add_task_xldeploy_auto.raise_for_status()
        if reponse_add_task_xldeploy_auto.content:
            if 'id' in reponse_add_task_xldeploy_auto.json():
                    self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'Get version XLdeploy PACKAGE: "+package_name+"'" )
    def jython_markdown_version_package(self,phase,step):
        if phase == 'DEV':
            url_format_date_from_xlr_input=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        elif phase == 'dynamic_release':
            url_format_date_from_xlr_input=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url_format_date_from_xlr_input=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse_format_date_from_xlr_input= requests.post(url_format_date_from_xlr_input, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : False,
                                                            "title" : 'Recap version package '+step ,
                                                            "script":  "##jython_markdown_version_package\n"
                                                                        "import re\n"
                                                                        "import json\n"
                                                                        "out='| PACKAGE NAME | Version |\\n| --- | --- |\\n'\n"
                                                                        "phase_title = getCurrentPhase().title\n"
                                                                        "step='"+step+"'\n"
                                                                        "for package in ${release_Variables_in_progress}['list_package'].split(','):\n"
                                                                        "       version =  releaseVariables['version_deployed_'+package+'_'+phase_title+'_'+step].split('/')[-1]\n"
                                                                        "       out += '| {0} | {1} |\\n'.format(package, version) \n"
                                                                        "task.description = out\n"
                                                                        "taskApi.updateTask(task)\n"
                                                            },verify = False)
            reponse_format_date_from_xlr_input.raise_for_status()
            if reponse_format_date_from_xlr_input.content:
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : jython_markdown_version_package.")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'jython_markdown_version_package. SKIP mode'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url_format_date_from_xlr_input)
                        self.logger_error.error(reponse_format_date_from_xlr_input.content)
                        self.logger_error.error(e)
    def XLRJythonScript_format_date_from_xlr_input(self,variables_date_sun,phase):
        url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase']+'/tasks'
        newformatdate = []
        for variable in variables_date_sun:
            newformatdate.append("releaseVariables['"+variable.replace("_date","_format")+"'] = date_format.format(releaseVariables['"+variable+"'])")
        var = '\n'.join(newformatdate)
        reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'Put date from input at format for SUN CHANGE' ,
                                                            "script":  "##XLRJythonScript_format_date_from_xlr_input\n"
                                                                        "from java.text import SimpleDateFormat\n"
                                                                        "import java.util.Date\n"
                                                                        "date_formatctrlm = java.text.SimpleDateFormat('yyMMdd')\n"
                                                                        "releaseVariables['controlm_today'] = date_formatctrlm\n"
                                                                        "releaseVariables['Release_Email_resquester'] = userApi.getUser('${release.owner}').email\n"
                                                                        "date_format = java.text.SimpleDateFormat('dd-MM-yyyy HH:mm:ss')\n"
                                                                        +var
                                                                        },verify = False)
        if 'id' in reponse.json():
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add SUN task : 'Put date from input at format for SUN CHANGE' with precondition : "+ precondition) 
                    else:
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add SUN task : 'Put date from input at format for SUN CHANGE' " ) 
    def script_jython(self,phase,task_id):
        url=self.url_api_xlr+'tasks/'+task_id+'/tasks'
        requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'Put date from input at format for COTROLM demand' ,
                                                            "script":  "##script_jython\n"
                                                                        "from time import strftime\n"
                                                                        "date_format = strftime('%Y%m%d')\n"
                                                                        "print(date_format)\n"
                                                                        "releaseVariables['controlm_today'] = date_format\n"                                                                     
                                                                        },verify = False)
    def XLRJython_markdown_version_package(self,phase,step):
        if phase == 'DEV':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        elif phase == 'dynamic_release':
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        else:
            url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : False,
                                                            "title" : 'Recap version package '+step ,
                                                            "script":  "##XLRJython_markdown_version_package\n"
                                                                        "import re\n"
                                                                        "import json\n"
                                                                        "out='| PACKAGE NAME | Version |\\n| --- | --- |\\n'\n"
                                                                        "phase_title = getCurrentPhase().title\n"
                                                                        "step='"+step+"'\n"
                                                                        "for package in ${release_Variables_in_progress}['list_package'].split(','):\n"
                                                                        "       version =  releaseVariables['version_deployed_'+package+'_'+phase_title+'_'+step].split('/')[-1]\n"
                                                                        "       out += '| {0} | {1} |\\n'.format(package, version) \n"
                                                                        "task.description = out\n"
                                                                        "taskApi.updateTask(task)\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        if 'id' in reponse.json():
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : jython_markdown_version_package. SKIP mode with precondition : "+ precondition) 
                        else:
                            self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : jython_markdown_version_package.")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'jython_markdown_version_package. SKIP mode'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(reponse.content)
                        self.logger_error.error(e)
    def XLRJythonScript_xld_delete_undeploy_after_get_version(self,phase,step):
        url_delete_undeploy_after_get_version=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        try:
            reponse= requests.post(url_delete_undeploy_after_get_version, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : False,
                                                            "title" : 'Delete undeploy if necessary' ,
                                                            "script":   "##XLRJythonScript_xld_delete_undeploy_after_get_version\n"
                                                                        "import json\n"
                                                                        "phase_title = getCurrentPhase().title\n"
                                                                        "step='"+step+"'\n"
                                                                        "list_package_to_not_undeploy = [] \n"
                                                                        "for item in releaseVariables['release_Variables_in_progress']['auto_undeploy'].split(','):\n"
                                                                        "       key = item.split(':')[0]\n"
                                                                        "       value = item.split(':')[1]\n"
                                                                        "       if value.encode('utf-8') == 'yes':\n"
                                                                        "           list_package_to_not_undeploy.append(key.encode('utf-8'))\n"
                                                                        "       else: \n"
                                                                        "           list_package_to_not_undeploy.append(key.encode('utf-8'))\n"
                                                                        "for package in list_package_to_not_undeploy:\n"
                                                                        "       if releaseVariables[package+'_version'] == releaseVariables['release_Variables_in_progress']['package_title_choice']:\n"
                                                                        "           task_xld_phase = 'Undeploy '+package\n"
                                                                        "           xlr_id_task_to_delete = taskApi.searchTasksByTitle(task_xld_phase, phase_title, '${release.id}')\n"
                                                                        "           if len(xlr_id_task_to_delete) != 0:\n"
                                                                        "               taskApi.delete(str(xlr_id_task_to_delete[0]))\n"
                                                            },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                    if 'id' in reponse.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper() +" --- Add task : 'DELETE XLD TASK'")
        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper() +" --- Add task : 'RE EVALUATION PACKAGE VERSION'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url_delete_undeploy_after_get_version)
                        self.logger_error.error(reponse.content)
                        self.logger_error.error(e)                  
    def add_task_xldeploy_get_last_version(self,demandxld,xld_value,phase,grp_id_xldeploy):
        package_value = next(package for package in self.parameters['template_liste_package'] if demandxld in package)
        verion_package = "${"+demandxld+"_version}"
        url=self.url_api_xlr+'tasks/'+grp_id_xldeploy +'/tasks'
        try:
            response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : "null",
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : 'XLD-Deploy Search last version : '+demandxld,
                            "status" : "PLANNED",
                            "color" : "#00ff00",
                            "variableMapping": {
                                            "pythonScript.packageId": verion_package,
                                                },
                            "locked" : False,
                            "waitForScheduledStartDate": True,
                            "checkAttributes": False,
                            "pythonScript": {
                                "server": "Configuration/Custom/XLDeploy PFI PROD",
                                "type": "xld.GetLatestVersion",
                                "id": "null",
                                "username": "${"+phase+"_username_xldeploy}",
                                "password": '${'+phase+'_password_xldeploy}',
                                "connectionFailureCount": 0,
                                "applicationId": self.parameters['template_liste_package'][package_value]['XLD_application_path'],
                                "stripApplications": False,
                                "throwOnFail": False
                                }
                                },verify = False)
            response.raise_for_status()
            if 'id' in response.json():
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'XLD-Deploy Search last version : "+package_value+"' with precondition : "+ precondition)
                    else:
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'XLD-Deploy Search last version : "+package_value+"'" )
        except requests.exceptions.RequestException as e:
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper()+" --- Add task : XLDEPLOY : "+package_value+" with title : 'XLD-Deploy Search last version : '"+package_value)
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(response.content)
                        self.logger_error.error(e)
                        sys.exit(0)
    def add_phase_tasks(self,phase):
        """
        Add a new phase to the XLR template.

        Args:
            phase (str): Phase name (DEV, UAT, BENCH, PRODUCTION, dynamic_release)

        Returns:
            dict: Updated dict_template with new phase information

        Creates a new phase in the XLR template with:
        - Phase-specific configuration
        - Task organization structure
        - Environment-appropriate settings
        - Integration with parent template

        Different phase types:
        - Development phases: Standard deployment workflow
        - Production phases: Approval workflow integration
        - Dynamic phase: Runtime template customization
        """
            url_add_phase_tasks=self.url_api_xlr+'phases/'+self.XLR_template_id+'/phase'
            try:
                reponse_url_add_phase_tasks= requests.post(url_add_phase_tasks, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                "id" : None,
                                "type" : "xlrelease.Phase",
                                "flagStatus" : "OK",
                                "title" : phase,
                                "status" : "PLANNED",
                                "color" : "#00FF00"
                                },verify = False)
                reponse_url_add_phase_tasks.raise_for_status()
                if reponse_url_add_phase_tasks.content:
                        if 'id' in reponse_url_add_phase_tasks.json():
                                self.logger_cr.info("       ADD PHASE : "+phase)                
                                self.dict_template[phase] = {'xlr_id_phase': reponse_url_add_phase_tasks.json()["id"],
                                            'xlr_id_phase_full': reponse_url_add_phase_tasks.json()["id"]
                                            }
                                self.logger_cr.info("               CREATION PHASE NAME : "+ phase+' OK')
                        else:
                                self.logger_error.error("ERROR on ADD PHASE : "+ phase)
                                self.logger_error.error(reponse_url_add_phase_tasks.content)
                                sys.exit(0)
            except requests.exceptions.RequestException as e:
                        self.logger_error.error("Detail ERROR on ADD PHASE : "+ phase)
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url_add_phase_tasks)
                        self.logger_error.error( e)
                        sys.exit(0)
            return self.dict_template
    def add_variable_deliverable_item_showOnReleaseStart(self):
                if self.parameters.get('template_liste_package') is not None:
                    if len(self.parameters['template_liste_package']) == 1:
                        self.add_variable_showOnReleaseStart(self.parameters['template_liste_package'])
                    else:
                        self.add_variable_showOnReleaseStart(self.parameters['template_liste_package'])
    def add_variable_showOnReleaseStart(self,template_liste_package):
        for package_name,package_value in template_liste_package.items():
            if 'BUILD' in self.parameters['general_info']['phases']:
                value_des = 'NO DEPLOY'
                #self.dict_value_for_template['package_title_choice'] = value_des
                self.release_Variables_in_progress['package_title_choice'] = value_des
            elif self.parameters['general_info'].get('package_mode') is not None and self.parameters['general_info']['package_mode'] == 'generic':
                if 'DEV' in self.parameters['general_info']['phases'] :
                    self.release_Variables_in_progress['package_title_choice'] = 'BRANCH NAME'
                else: 
                    self.release_Variables_in_progress['package_title_choice'] = '<version>'
                    
            elif self.transformation_variable_branch:
                if self.parameters['general_info']['option_latest']:
                     value_des = 'XLD PACKAGE NAME or LATEST to get the last VERSION of XLD package'
                else:
                    value_des = 'XLD PACKAGE NAME or BRANCH NAME'
                self.release_Variables_in_progress['package_title_choice']= value_des
            elif self.parameters['general_info']['type_template'] == 'BUILD_NO_DEV':
                    value_des = 'BRANCH_NAME'
                    value = ''
                    self.release_Variables_in_progress['package_title_choice']= value_des
            elif ('PRODUCTION' in self.parameters['general_info']['phases'] \
                    and len(self.parameters['general_info']['phases']) == 1) \
                    or self.parameters.get('jenkins') is None:
                if self.parameters['general_info']['option_latest']:
                     value_des = 'XLD PACKAGE NAME or LATEST to get the last VERSION of XLD package'
                else:
                    value_des = 'XLD PACKAGE NAME'
                self.release_Variables_in_progress['package_title_choice']= value_des
            elif 'BENCH' in self.parameters['general_info']['phases'] \
                    and len(self.parameters['general_info']['phases']) == 1:
                if self.parameters['general_info']['option_latest']:
                     value_des = 'XLD PACKAGE NAME or LATEST to get the last VERSION of XLD package'
                else:
                    value_des = 'XLD PACKAGE NAME'
                self.release_Variables_in_progress['package_title_choice']= value_des
            elif 'BENCH' in self.parameters['general_info']['phases'] \
                    and 'PRODUCTION' in self.parameters['general_info']['phases']\
                    and len(self.parameters['general_info']['phases']) == 2:
                if self.parameters['general_info']['option_latest']:
                     value_des = 'XLD PACKAGE NAME or LATEST to get the last VERSION of XLD package'
                else:
                    value_des = 'XLD PACKAGE NAME'
                #self.dict_value_for_template['package_title_choice'] = value_des
                self.release_Variables_in_progress['package_title_choice']= value_des
            elif "DEV" not in self.parameters['general_info']['phases']:
                if self.parameters['general_info']['option_latest']:
                     value_des = 'XLD PACKAGE NAME or LATEST to get the last VERSION of XLD package'
                else:
                    value_des = 'XLD PACKAGE NAME'
                #self.dict_value_for_template['package_title_choice'] = value_des
                self.release_Variables_in_progress['package_title_choice']= value_des
            else:
                    if self.jenkinsjobparam =='Yes':
                        if self.BRANCH_NAME:
                            if len(self.parameters['general_info']['phases']) == 1 and self.parameters['general_info']['phases'][0] == 'DEV':
                                value_des = 'BRANCH_NAME'
                            else:
                                value_des = 'XLD PACKAGE NAME or BRANCH_NAME if you select DEV'
                        else:
                            value_des = 'XLD PACKAGE NAME or BUILD if you select DEV'
                    elif  self.jenkinsjobparam =='No':
                            if len(self.parameters['general_info']['phases']) == 1 and self.parameters['general_info']['phases'][0] == 'DEV':
                                value_des = 'NO BUILD'
                            else:
                                value_des = 'XLD PACKAGE NAME or BUILD if you select DEV'

                # self.dict_value_for_template['package_title_choice'] = value_des
                    self.release_Variables_in_progress['package_title_choice'] = value_des
            if self.release_Variables_in_progress['package_title_choice'] == 'NO BUILD':
                valuenew =  'NO BUILD'
            elif self.parameters['general_info'].get('package_mode') is not None and self.parameters['general_info']['package_mode'] == 'generic':
                if 'DEV' in  self.parameters['general_info']['phases']:
                    valuenew = package_value['package_build_name'] + ' or ' + self.release_Variables_in_progress['package_title_choice']
                else: 
                    valuenew = package_value['package_build_name']
            else:
                if 'BUILD' not in self.parameters['general_info']['phases']:
                    valuenew = self.release_Variables_in_progress['package_title_choice']
                else: 
                    valuenew = self.release_Variables_in_progress['package_title_choice']
            url_add_variable_showOnReleaseStart=self.url_api_xlr+'releases/Applications/'+self.dict_template['template']['xlr_id']+'/variables'
            response= requests.post(url_add_variable_showOnReleaseStart, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                        "id" : None,
                                        "key" : package_name+'_version',
                                        "type" : "xlrelease.StringVariable",
                                        "requiresValue" : False,
                                        "showOnReleaseStart" : True,
                                        "value" :valuenew,
                                        "label": package_name,
                                        "description" : '',
                                        "multiline" : False,
                                        "inherited" : False,
                                        "externalVariableValue" : None,
                                        "valueProvider" : None
                                        },verify = False)
            if 'A variable already exists' not in str(response.content):
                if 'variables' not in self.dict_template:
                        self.dict_template.update({'variables': [{package_name: response.json()['id']}]})
                else:
                        self.dict_template['variables'].append({package_name: response.json()['id']})
                        if self.dict_value_for_template.get('XLR_ID_variable') is None:
                            self.dict_value_for_template['XLR_ID_variable'] = []
                        if package_value.get('mode')  is not None:
                                if package_value['mode'] == "name_from_jenkins":
                                    XLRGeneric.template_create_variable(self,key='VARIABLE_XLR_ID_'+package_name+'_version', typev='StringVariable', label='', description='', value='', requiresValue=False, showOnReleaseStart=False, multiline=False)
        return self.dict_template
    def add_task_jenkins(self,phase,jenkinsjob,jenkinsjob_value):
        branch = ''
        variableMapping = "${"+jenkinsjob+"_version}"
        if  jenkinsjob_value.get('parameters') is not None:
            if 'None' not in jenkinsjob_value['parameters']:
                if 'VARIABLE_XLR_ID' in jenkinsjob_value['parameters']:
                    tmp_parameter_jenkins_job = []
                    tmp_parameter_jenkins_job.append('VARIABLE_XLR_ID=${VARIABLE_XLR_ID_'+jenkinsjob+'_version}')
                    tmp_parameter_jenkins_job.append('VARIABLE_XLR_NAME='+jenkinsjob+'_version')
                    if self.parameters['general_info']['type_template'] == 'FROM_NAME_BRANCH':
                        tmp_parameter_jenkins_job.append('BRANCH_NAME=${'+jenkinsjob+'_version}')
                    parameter_jenkins_job = '\n'.join(tmp_parameter_jenkins_job)
                    branch = "${"+jenkinsjob+"_version}"
                    variableMapping = ''
                else:
                    for paramater in jenkinsjob_value['parameters']:
                        parameter_jenkins_job = '\n'.join(jenkinsjob_value['parameters'])
            else:
                parameter_jenkins_job = None
        else:
              parameter_jenkins_job = ''
        if self.parameters['jenkins'].get('apiToken') is not None:
            apiToken = self.parameters['jenkins']['apiToken']
        else:
              apiToken = None
        if self.parameters['jenkins'].get('password') is not None:
            passwordjenkins = self.parameters['jenkins']['password']
        else:
              passwordjenkins = None
        url_add_task_jenkins=self.url_api_xlr+'tasks/'+self.grp_id_jenkins+'/tasks'
        try :
            reponse_add_task_jenkins= requests.post(url_add_task_jenkins, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : "null",
                            "type" : "xlrelease.CustomScriptTask",
                            "title" :"Jenkins "+jenkinsjob,
                            "variableMapping": {
                                        "pythonScript.buildNumber": variableMapping
                                                },
                            "pythonScript": {
                                "type": "jenkins.Build",
                                "id": "null",
                                "jenkinsServer": self.parameters['jenkins']['jenkinsServer'],
                                "buildStatus": "SUCCESS",
                                "buildNumber": "5",
                                "username":self.parameters['jenkins']['username'],
                                "password":passwordjenkins,
                                "jobName":jenkinsjob_value['jobName'],
                                "apiToken":apiToken,
                                "jobParameters": parameter_jenkins_job,
                                 "branch": branch,
                                } },verify = False)
            reponse_add_task_jenkins.raise_for_status()
            if reponse_add_task_jenkins.content:
                    if 'id' in reponse_add_task_jenkins.json():
                        if self.parameters['general_info']['type_template'] == 'SKIP':
                            self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'Jenkins For Package: "+ jenkinsjob + "' with precondition : " +precondition)
                        else:
                            self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'Jenkins For Package: "+ jenkinsjob+"'" )

        except requests.exceptions.RequestException as e:
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper()+ "--- Add task : Jenkins. For Package: "+ jenkinsjob)
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url_add_task_jenkins)
                        self.logger_error.error(e)
                        self.logger_error.error(reponse_add_task_jenkins.content)
                        sys.exit(0)
    def add_task_xldeploy_auto(self,package_xld,phase,grp_id_xldeploy):
        if phase == 'DEV':
                xld_prefix_env = 'D'
                if self.parameters.get('XLD_ENV_DEV') is not None:
                    xld_env = '${env_'+phase+'}'
                elif self.parameters['general_info'].get('xld_standard') is not None and self.parameters['general_info']['xld_standard']: 
                    xld_env = '10-DEV'
                    xld_directory_env = 'DEV'
                else:     
                    xld_env = 'DEV'
                xld_directory_env = 'DEV'
        elif phase == 'TEST':
                xld_prefix_env = 'T'
                if self.parameters.get('XLD_ENV_TEST') is not None:
                    xld_env = '${env_'+phase+'}'
                elif self.parameters['general_info'].get('xld_standard') is not None and self.parameters['general_info']['xld_standard']: 
                    xld_env = '20-TEST'
                    xld_directory_env = 'TST'
                else:     
                    xld_env = 'TST'
                xld_directory_env = 'TST'
        elif phase == 'UAT':
                xld_prefix_env = 'U'
                if self.parameters.get('XLD_ENV_UAT') is not None:
                    xld_env = '${env_'+phase+'}'
                elif self.parameters['general_info'].get('xld_standard') is not None and self.parameters['general_info']['xld_standard']: 
                    xld_env = '30-UAT'
                    xld_directory_env = 'UAT'
                else:     
                    xld_env = 'UAT'
                xld_directory_env = 'UAT'
        elif phase == 'BENCH':
                if self.parameters.get('XLD_ENV_BENCH') is not None  and len(self.parameters['XLD_ENV_BENCH']) >1:
                        xld_prefix_env = "${controlm_prefix_BENCH}"
                elif 'NXFFA' in self.parameters['general_info']['iua']:
                        xld_prefix_env = 'Q'
                else:
                        xld_prefix_env = 'B'
                if self.parameters.get('XLD_ENV_BENCH') is not None:
                    xld_env = '${env_'+phase+'}'
                elif self.parameters['general_info'].get('xld_standard') is not None and self.parameters['general_info']['xld_standard']: 
                    xld_env = '40-BENCH'
                    xld_directory_env = 'BCH'
                else:     
                    xld_env = 'BCH'
                xld_directory_env = 'BCH'
        elif phase == 'PRODUCTION':
                xld_prefix_env = 'P'
                if self.parameters.get('XLD_ENV_PRODUCTION') is not None:
                    xld_env = '${env_'+phase+'}'
                elif self.parameters['general_info'].get('xld_standard') is not None and self.parameters['general_info']['xld_standard']: 
                    xld_env = '50-PROD'
                    xld_directory_env = 'PRD'
                else:     
                    xld_env = 'PRD'
                xld_directory_env = 'PRD'
        package_value = next(package for package in self.parameters['template_liste_package'] if package_xld in package)
        if 'APPCODE' in self.parameters['general_info']['iua'] and phase == 'BENCH':
            value_env = ''
            if package_xld == 'Interfaces':
                value = 'INT'
            elif package_xld in ['Interface_summit','Interface_summit_COF','Interface_TOGE','Interface_TOGE_ACK','Interface_NON_LOAN_US','DICTIONNAIRE','Interface_MOTOR','Interface_ROAR_ACK','Interface_ROAR']:
                value = 'INT'
                value_env ='_NEW'
            elif package_xld == 'Scripts':
                value = 'SCR'
            elif package_xld == 'SDK':
                value = 'SDK'
            elif package_xld == 'App':
                value = 'APP'
            elif 'FILEBEAT' in package_xld:
                value = 'THEIA'
            tempo_XLD_environment_path = 'Environments/PFI/APPCODE_APPLICATION/7.6/<ENV>/${BENCH_APPCODE}/${BENCH_APPCODE}_01/'+value+'/<xld_prefix_env>APPCODE_'+value+'_<XLD_env>_01_ENV'+value_env
            xld_path_deploymentEnvironment = tempo_XLD_environment_path.replace('<XLD_env>',xld_env).replace('<xld_prefix_env>',xld_prefix_env).replace('<ENV>',xld_directory_env)
        elif self.parameters['general_info'].get('xld_standard') is not None and self.parameters['general_info']['xld_standard']: 
            xld_path_deploymentEnvironment = self.parameters['template_liste_package'][package_value]['XLD_environment_path'].replace('<XLD_env>',xld_env).replace('<xld_prefix_env>',xld_prefix_env).replace('<ENV>',xld_directory_env)
        else: 
            xld_path_deploymentEnvironment = self.parameters['template_liste_package'][package_value]['XLD_environment_path'].replace('<XLD_env>',xld_env).replace('<xld_prefix_env>',xld_prefix_env).replace('<ENV>',xld_directory_env)
        if self.parameters['general_info']['type_template'] == 'MULTIPACKAGE_AT_ONCE':
            verion_package = self.parameters['template_liste_package'][package_value]['package_build_name']
        elif self.parameters['general_info']['type_template'] == 'FROM_NAME_BRANCH':
            verion_package = self.parameters['template_liste_package'][package_value]['package_build_name'].replace('<version>','').replace('NAME PACKAGE','')+"${"+package_value+"_version}"
        else:
            verion_package = "${"+package_value+"_version}"
        if not self.parameters['template_liste_package'][package_value]['XLD_application_path'].endswith("/"):
            self.parameters['template_liste_package'][package_value]['XLD_application_path'] += "/"
        if not self.parameters['general_info']['option_latest']:
            if "<SNAPSHOT-RELEASE>" in self.parameters['template_liste_package'][package_value]['XLD_application_path']:
                if phase != 'PRODUCTION':
                    tmp_deploymentPackage = self.parameters['template_liste_package'][package_value]['XLD_application_path'].replace('<SNAPSHOT-RELEASE>','Snapshot')
                    deploymentPackage = tmp_deploymentPackage+''+verion_package
                else:
                    tmp_deploymentPackage = self.parameters['template_liste_package'][package_value]['XLD_application_path'].replace('<SNAPSHOT-RELEASE>','Release')
                    deploymentPackage = tmp_deploymentPackage+''+verion_package
            else:
                deploymentPackage = self.parameters['template_liste_package'][package_value]['XLD_application_path']+''+verion_package
        elif self.parameters['general_info']['option_latest']:
            deploymentPackage =self.parameters['template_liste_package'][package_value]['XLD_application_path']+''+verion_package
        url=self.url_api_xlr+'tasks/'+grp_id_xldeploy +'/tasks'
        try:
            response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : "null",
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : 'XLD-Deploy '+package_xld,
                            "status" : "PLANNED",
                            "locked" : False,
                            "waitForScheduledStartDate": True,
                            "pythonScript": {
                                "server": "Configuration/Custom/XLDeploy PFI PROD",
                                "type": "xldeploy.Deploy",
                                "continueIfStepFails": False,
                                "displayStepLogs": True,
                                "retryCounter": {
                                    "currentContinueRetrial": "0",
                                    "currentPollingTrial": "0"
                                },
                                "id": "null",
                                "username": "${"+phase+"_username_xldeploy}",
                                "password": '${'+phase+'_password_xldeploy}',
                                "deploymentPackage": deploymentPackage,
                                "deploymentEnvironment": xld_path_deploymentEnvironment,
                                "overrideDeployedProps": {},
                                "rollbackOnFailure": False,
                                "cancelOnError": False,
                                "failOnPause": False,
                                "keepPreviousOutputPropertiesOnRetry": False}
                                },verify = False)

            response.raise_for_status()
            if response.content:
                if 'id' in response.json():
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'XLD-Deploy "+package_xld+"' with precondition : "+ precondition)
                    else:
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'XLD-Deploy "+package_xld+"'" )

        except requests.exceptions.RequestException as e:
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper()+" --- Add task : XLDEPLOY : "+package_xld+" with title : 'XLD-Deploy "+package_xld)
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
        return self.dict_template
    def add_task_xldeploy_auto_listbox_package(self,xlditemtodeliver,phase,grp_id_xldeploy):
        if phase == 'DEV':
                xld_prefix_env = 'D'
                if self.parameters.get('XLD_ENV_DEV') is not None:
                    xld_env = '${env_'+phase+'}'
                elif self.parameters['general_info'].get('xld_standard') is not None and self.parameters['general_info']['xld_standard']: 
                    xld_env = '10-DEV'
                    xld_directory_env = 'DEV'
                else:     
                    xld_env = 'DEV'
                xld_directory_env = 'DEV'
        elif phase == 'TEST':
                xld_prefix_env = 'T'
                if self.parameters.get('XLD_ENV_TEST') is not None:
                    xld_env = '${env_'+phase+'}'
                elif self.parameters['general_info'].get('xld_standard') is not None and self.parameters['general_info']['xld_standard']: 
                    xld_env = '20-TEST'
                    xld_directory_env = 'TST'
                else:     
                    xld_env = 'TST'
                xld_directory_env = 'TST'
        elif phase == 'UAT':
                xld_prefix_env = 'U'
                if self.parameters.get('XLD_ENV_UAT') is not None:
                    xld_env = '${env_'+phase+'}'
                elif self.parameters['general_info'].get('xld_standard') is not None and self.parameters['general_info']['xld_standard']: 
                    xld_env = '30-UAT'
                    xld_directory_env = 'UAT'
                else:     
                    xld_env = 'UAT'
                xld_directory_env = 'UAT'
        elif phase == 'BENCH':
                if self.parameters.get('XLD_ENV_BENCH') is not None  and len(self.parameters['XLD_ENV_BENCH']) >1:
                        xld_prefix_env = "${controlm_prefix_BENCH}"
                elif 'NXFFA' in self.parameters['general_info']['iua']:
                        xld_prefix_env = 'Q'
                else:
                        xld_prefix_env = 'B'
                if self.parameters.get('XLD_ENV_BENCH') is not None:
                    xld_env = '${env_'+phase+'}'
                elif self.parameters['general_info'].get('xld_standard') is not None and self.parameters['general_info']['xld_standard']: 
                    xld_env = '40-BENCH'
                    xld_directory_env = 'BCH'
                else:     
                    xld_env = 'BCH'
                xld_directory_env = 'BCH'
        elif phase == 'PRODUCTION':
                xld_prefix_env = 'P'
                if self.parameters.get('XLD_ENV_PRODUCTION') is not None:
                    xld_env = '${env_'+phase+'}'
                elif self.parameters['general_info'].get('xld_standard') is not None and self.parameters['general_info']['xld_standard']: 
                    xld_env = '50-PROD'
                    xld_directory_env = 'PRD'
                else:     
                    xld_env = 'PRD'
                xld_directory_env = 'PRD'
        package_value = next(package for package in self.parameters['template_liste_package'] if xlditemtodeliver in package)
        if 'APPCODE' in self.parameters['general_info']['iua'] and phase == 'BENCH':
            value_env = ''
            if xlditemtodeliver == 'Interfaces':
                value = 'INT'
            elif xlditemtodeliver in ['Interface_summit','Interface_summit_COF','Interface_TOGE','Interface_TOGE_ACK','Interface_NON_LOAN_US','DICTIONNAIRE','Interface_MOTOR','Interface_ROAR_ACK','Interface_ROAR']:
                value = 'INT'
                value_env ='_NEW'
            elif xlditemtodeliver == 'Scripts':
                value = 'SCR'
            elif xlditemtodeliver == 'SDK':
                value = 'SDK'
            elif xlditemtodeliver == 'App':
                value = 'APP'
            elif 'FILEBEAT' in xlditemtodeliver:
                value = 'THEIA'
            tempo_XLD_environment_path = 'Environments/PFI/APPCODE_APPLICATION/7.6/<ENV>/${BENCH_APPCODE}/${BENCH_APPCODE}_01/'+value+'/<xld_prefix_env>APPCODE_'+value+'_<XLD_env>_01_ENV'+value_env
            xld_path_deploymentEnvironment = tempo_XLD_environment_path.replace('<XLD_env>',xld_env).replace('<xld_prefix_env>',xld_prefix_env).replace('<ENV>',xld_directory_env)
        elif self.parameters['general_info'].get('xld_standard') is not None and self.parameters['general_info']['xld_standard']: 
            xld_path_deploymentEnvironment = self.parameters['template_liste_package'][package_value]['XLD_environment_path'].replace('<XLD_env>',xld_env).replace('<xld_prefix_env>',xld_prefix_env).replace('<ENV>',xld_directory_env)
        else: 
            xld_path_deploymentEnvironment = package_value[list(package_value.keys())[0]]['XLD_environment_path'].replace('<XLD_env>',xld_env).replace('<xld_prefix_env>',xld_prefix_env).replace('<ENV>',xld_directory_env)
        url=self.url_api_xlr+'tasks/'+grp_id_xldeploy +'/tasks'
        try:
            response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : "null",
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : 'XLD-Deploy '+xlditemtodeliver,
                            "status" : "PLANNED",
                            "locked" : False,
                            "color" : "#00ff00",
                            "waitForScheduledStartDate": True,
                            "pythonScript": {
                                "server": "Configuration/Custom/XLDeploy PFI PROD",
                                "type": "xldeploy.Deploy",
                                "continueIfStepFails": False,
                                "displayStepLogs": True,
                                "retryCounter": {
                                    "currentContinueRetrial": "0",
                                    "currentPollingTrial": "0"
                                },
                                "id": "null",
                                "username": "${"+phase+"_username_xldeploy}",
                                "password": '${'+phase+'_password_xldeploy}',
                                "deploymentPackage": "Applications/${"+xlditemtodeliver+'_version}',
                                "deploymentEnvironment": xld_path_deploymentEnvironment,
                                "overrideDeployedProps": {},
                                "rollbackOnFailure": False,
                                "cancelOnError": False,
                                "failOnPause": False,
                                "keepPreviousOutputPropertiesOnRetry": False}
                                },verify = False)
            response.raise_for_status()
            if response.content:
                if 'id' in response.json():
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'XLD-Deploy "+xlditemtodeliver+"' with precondition : "+ precondition)
                    else:
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'XLD-Deploy "+xlditemtodeliver+"'" )
        except requests.exceptions.RequestException as e:
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper()+" --- Add task : XLDEPLOY : "+xlditemtodeliver+" with title : 'XLD-Deploy "+xlditemtodeliver)
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(response.content)
                        self.logger_error.error(e)
                        sys.exit(0)
        return self.dict_template
    def template_delete_variable(self,key):
                url_get_variable=self.url_api_xlr+'releases/Applications/'+self.dict_template['template']['xlr_id']+'/variables'
                reponse_get_variable= requests.get(url_get_variable, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), verify = False)
                for item in reponse_get_variable.json():
                      if key == item["key"]:
                        idget = item['id']
                url_create_variable=self.url_api_xlr+'releases/'+idget
                reponse_template_delete_variable= requests.delete(url_create_variable, headers=self.header,auth=(self.ops_username_api, self.ops_password_api),verify = False)
    def dynamic_release(self,id_task):
        url_dynamic_release=self.url_api_xlr+'tasks/'+id_task
        reponse_dynamic_release= requests.delete(url_dynamic_release, headers=self.header,auth=(self.ops_username_api, self.ops_password_api),verify = False)
    def webhook_get_email_ops_on_change(self,phase):
        task_release = 'Applications/'+self.dict_template['template']['xlr_id']+'/'+self.dict_template[phase]['xlr_id_phase']
        urtcontrolmfolderdemand=self.url_api_xlr+'tasks/'+ task_release+'/tasks'
        value = "change_user_assign"
        XLRGeneric.template_create_variable(self,key=value, typev='StringVariable', label='', description='', value='', requiresValue=False, showOnReleaseStart=False, multiline=False)
        try:
            reponse_add_webhook_demand_folder= requests.post(urtcontrolmfolderdemand, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.CustomScriptTask",
                                                            "title" : "Search in SUN user assign to the change",
                                                            "variableMapping": {
                                                                    "pythonScript.result": '${change_user_assign}',
                                                                        },
                                                            "locked" : True,
                                                            "pythonScript": {
                                                                        "type":"webhook.JsonWebhook",
                                                                        "id": "null",
                                                                        "URL" : "https://itaas.api.intranatixis.com/support/sun/change/v1/getList?query=number%3D${"+phase+".sun.id}&offset=0",
                                                                        "method": "GET",
                                                                        "username":  self.ops_username_api,
                                                                        "password": self.ops_password_api,
                                                                        "jsonPathExpression": 'Data',
                                                                        }},verify = False)
            reponse_add_webhook_demand_folder.raise_for_status()
            if reponse_add_webhook_demand_folder.content:
                if 'id' in reponse_add_webhook_demand_folder.json():
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : WEBHOOK SUN : 'Search in SUN user assign to the change' with precondition : "+ precondition)
                    else:
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : WEBHOOK SUN : 'Search in SUN user assign to the change'")

        except requests.exceptions.RequestException as e:
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper()+" --- Add task : webhook : 'Search in SUN user assigne to the change' ")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+urtcontrolmfolderdemand)
                        self.logger_error.error(e)
                        sys.exit(0)
    def script_jython_get_email_ops_on_change(self,phase):
        task_release = 'Applications/'+self.dict_template['template']['xlr_id']+'/'+self.dict_template[phase]['xlr_id_phase']
        url=self.url_api_xlr+'tasks/'+task_release+'/tasks'
        try :
            reponse= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'Get email Of the user assign to the CHANGE' ,
                                                            "script":  "##script_jython_get_email_ops_on_change\n"
                                                                        "import json\n"
                                                                        "null = None\n"
                                                                        "result_json = json.loads(releaseVariables['change_user_assign'])\n"
                                                                        "releaseVariables['change_user_assign'] = result_json[0]['assigned_to.email']\n"
                                                                        "releaseVariables['email_owner_release'] = userApi.getUser('${release.owner}').email\n"
                                                                        "print(userApi.getUser('${release.owner}').email)\n"
                                                                        },verify = False)
            reponse.raise_for_status()
            if reponse.content:
                if 'id' in reponse.json():
                        if self.parameters['general_info']['type_template'] == 'SKIP':
                                self.logger_cr.info("ON PHASE : "+phase.upper()+" --- Add task : 'Get email Of the user assign to the CHANGE' with precondition : "+ precondition)
                        else:
                                self.logger_cr.info("ON PHASE : "+phase.upper()+" --- Add task : 'Get email Of the user assign to the CHANGE'" )
        except requests.exceptions.RequestException as e:
                        self.logger_error.error("Detail ERROR: ON PHASE : "+phase.upper()+" --- Add task : Get email Of the user assign to the CHANGE'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    def dict_value_for_tempalte(self):
            dict_value_for_template = {}
            self.release_Variables_in_progress = {}
            self.release_Variables_in_progress['template_liste_phase'] =  ','.join(map(str, self.parameters['general_info']['phases']))
            if self.parameters.get('XLD_ENV_BENCH') is not None:
                for index,env_bench in enumerate(self.parameters['XLD_ENV_BENCH']):
                    if index  == 0:
                        XLD_ENV_BENCH = env_bench
                    else:     
                        XLD_ENV_BENCH += ','+env_bench
                self.release_Variables_in_progress['list_env_BENCH'] = XLD_ENV_BENCH
            self.package_name_from_jenkins = []
            self.package_master = []
            self.list_package = []
            self.auto_undeploy = []
            self.list_auto_undeploy = []
            self.transformation_variable_branch = False
            self.list_package_name = []
            self.check_xld_exist = False
            for package,package_value in self.parameters['template_liste_package'].items():
                    self.list_package.append(package)
                    if package_value['controlm_mode'] == 'master':
                        self.package_master.append(package)
                    if package_value.get('mode')  is not None:
                        if package_value['mode'] == "name_from_jenkins":
                            XLRGeneric.template_create_variable(self,key=package+'_XLR_ID', typev='StringVariable', label='', description='', value='', requiresValue=False, showOnReleaseStart=False, multiline=False)
                            self.transformation_variable_branch = True
                            self.package_name_from_jenkins.append(package)
                    if package_value['package_build_name'] != 'NAME PACKAGE':
                        self.list_package_name.append(package+'-'+package_value['package_build_name'])
                    if package_value.get('mode') is not None and package_value['mode'] == 'CHECK_XLD':
                        self.check_xld_exist = True
                    if package_value.get('auto_undeploy')  is not None:
                        if isinstance(package_value['auto_undeploy'],list):
                            listundeploy=''
                            maxvalueliste = len(package_value['auto_undeploy'])
                            for num,depend_undeploy in enumerate(package_value['auto_undeploy']):
                                if num < maxvalueliste - 1:
                                    listundeploy += depend_undeploy+'-'
                                else:
                                    listundeploy += depend_undeploy
                                self.auto_undeploy.append(package+':'+listundeploy)
                                self.list_auto_undeploy.append(package)
                            self.set_undeploy_task = True
                        elif package_value['auto_undeploy']:
                                self.auto_undeploy.append({package: 'yes'})
                                self.list_auto_undeploy.append(package)                           
                                self.set_undeploy_task = True
                        elif package_value['package_build_name'] != '':
                            def_package = {}
                            def_package['XLD_PACKAGE_PATERN'] = package_value['package_build_name']
                        
            self.release_Variables_in_progress['auto_undeploy'] = ','.join(self.auto_undeploy)
            self.release_Variables_in_progress['list_auto_undeploy'] = ','.join(self.list_auto_undeploy)
            self.release_Variables_in_progress['package_name_from_jenkins'] = ','.join(self.package_name_from_jenkins)
            self.release_Variables_in_progress['list_package'] =  ','.join( self.list_package)
            self.release_Variables_in_progress['package_master'] =  ','.join(self.package_master)
            self.release_Variables_in_progress['list_build_name'] =  ','.join(self.list_package_name)
            self.template_controlm = {}
            dict_value_for_template['controlm'] = {}
            dict_value_for_template['controlmspec'] = {}
            for phase in self.parameters['general_info']['phases']:
                if phase != 'BUILD':
                    self.template_controlm[phase] = {}
                    for phase_task in self.parameters['Phases'][phase]:
                        if 'controlm' in list(phase_task.keys())[0]:
                            for controlm_item,controlm_item_value in phase_task[list(phase_task.keys())[0]].items():
                                for folder_list in controlm_item_value['folder']:
                                    if phase not in dict_value_for_template['controlm']:
                                        dict_value_for_template['controlm'][phase] = {}
                                    if controlm_item not in dict_value_for_template['controlm'][phase]:
                                        dict_value_for_template['controlm'][phase][controlm_item] = []
                                    if type(phase_task[list(phase_task.keys())[0]][controlm_item]['folder']) == str: 
                                        for folder in phase_task[list(phase_task.keys())[0]][controlm_item]['folder']:
                                            if  type(folder) == str:
                                                    dict_value_for_template['controlm'][phase][controlm_item].append({folder:{'case': ''} })
                                            else:
                                                        if  'case' in folder[list(folder.keys())[0]]:
                                                            dict_value_for_template['controlm'][phase][controlm_item].append({list(folder.keys())[0]: folder[list(folder.keys())[0]]['case']} )
                                                        else:
                                                            dict_value_for_template['controlm'][phase][controlm_item].append({list(folder.keys())[0]: {'case': ''} })
                                    else: 
                                        value_for_controlm = ''
                                        for folder in phase_task[list(phase_task.keys())[0]][controlm_item]['folder']:
                                            if 'case' in folder[list(folder.keys())[0]]: 
                                                listcase = '-'.join(folder[list(folder.keys())[0]]['case'])
                                                if value_for_controlm == '': 
                                                    value_for_controlm += list(folder.keys())[0]+'-'+listcase
                                                else: 
                                                    value_for_controlm += ','+list(folder.keys())[0]+'-'+listcase
                                                dict_value_for_template['controlm'][phase][controlm_item].append({list(folder.keys())[0]: folder[list(folder.keys())[0]]['case']} )
                                            else:
                                                dict_value_for_template['controlm'][phase][controlm_item].append({list(folder.keys())[0]: {'case': ''} })
                                    self.template_controlm[phase][controlm_item] = value_for_controlm
                        if 'controlmspec' in list(phase_task.keys())[0] :
                            if phase_task[list(phase_task.keys())[0]].get('mode') is not None: 
                                    if phase_task[list(phase_task.keys())[0]]['mode'] == 'profil':
                                        dict_value_for_template['controlmspec'][phase] = {}
                                        if phase not in dict_value_for_template['controlmspec']:
                                            dict_value_for_template['controlmspec'][phase] = {'profil':phase_task[list(phase_task.keys())[0]]['name_profil']}
                                            self.control_spec_profil = 'yes'
                                    elif phase_task[list(phase_task.keys())[0]]['mode'] == 'free':
                                        dict_value_for_template['controlmspec'][phase] = {}
                                        dict_value_for_template['controlmspec'][phase]['mode'] = 'free'
                                        dict_value_for_template['controlmspec'][phase]['render'] = phase_task[list(phase_task.keys())[0]]['render']
                                        self.control_spec_free = 'yes'
                            else:
                                dict_value_for_template['controlmspec'][phase] = {}
                                dict_value_for_template['controlmspec'][phase] = 'json'
                    
                    self.template_create_variable('template_list_controlm_'+phase,
                                                  'MapStringStringVariable',
                                                  '',
                                                  '',   
                                                  self.template_controlm[phase],
                                                  False,
                                                  False,
                                                  False )
            if 'FROM_NAME_BRANCH' in self.parameters['general_info']['type_template']: 
                self.release_Variables_in_progress['xlr_list_phase_selection'] = 'BENCH,PRODUCTION'
                self.release_Variables_in_progress['xlr_list_phase'] = 'BENCH,PRODUCTION'
            return dict_value_for_template
    def task_notification(self,phase,email_item,aim):
        if aim == "email_close_release":
            toAddresses = "${email_owner_release}"
            if email_item.get('cc') is not None:
                list_cc_email = email_item["cc"]
                ccAddresses = ", ".join(list_cc_email)
        elif aim == "email_end_release":
            list_dest_email = email_item["destinataire"]
            toAddresses = ", ".join(list_dest_email)
            ccAddresses = "ld-dsi-r2c-rpa-pfi@natixis.com"
        task_release= 'Applications/'+self.dict_template['template']['xlr_id']+'/'+self.dict_template[phase]['xlr_id_phase']
        url_task_notification=self.url_api_xlr+'tasks/'+ task_release+'/tasks'
        if aim == 'email_close_release':
            reponse_add_webhook_demand_folder= requests.post(url_task_notification, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "locked" : True,
                                                            "type" : "xlrelease.CustomScriptTask",
                                                            "title" : "EMAIL : Close Release ${release.title}",
                                                            "pythonScript": {
                                                                        "type":"nxsCustomNotification.MailNotification",
                                                                        "id": "null",
                                                                        "smtpServer": "Configuration/Custom/Server Mail",
                                                                        "fromAddress": "ld-dsi-r2c-rpa-pfi@natixis.com",
                                                                        "toAddresses": toAddresses,
                                                                        "ccAddresses": ccAddresses,
                                                                        "priority": "Normal",
                                                                        "subject": "XLR - Deployment  FINISH - Release name : ${release.title}",
                                                                        "body":  " The XLR Release : ${release.title} is finish OK. \n"
                                                                                "  \n"
                                                                                " Thanks to close the release. In order to close the SUN CHANGE. "
                                                                                " \n"
                                                                                " Description : \n"
                                                                                " \n"
                                                                                " ${Long_description_SUN_CHANGE}\n"
                                                                                " \n"
                                                                                " \n"
                                                                                " Link to the release: https://release-pfi.mycloud.intranatixis.com/${release.id} \n"
                                                                                " \n"
                                                                                " Thanks\n"
                                                                            }
                                                                        },verify = False)
            if 'id' in reponse_add_webhook_demand_folder.json():
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'EMAIL : "+phase+" Validation Release' with precondition : "+ precondition)
                    else:
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'EMAIL : "+phase+" Validation Release'")
        elif aim == 'email_end_release':

            reponse_add_webhook_demand_folder= requests.post(url_task_notification, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "locked" : True,
                                                            "type" : "xlrelease.CustomScriptTask",
                                                            "title" : "EMAIL : "+phase+" Validation Release",
                                                            "pythonScript": {
                                                                        "type":"nxsCustomNotification.MailNotification",
                                                                        "id": "null",
                                                                        "smtpServer": "Configuration/Custom/Server Mail",
                                                                        "fromAddress": "ld-dsi-r2c-rpa-pfi@natixis.com",
                                                                        "toAddresses": toAddresses,
                                                                        "ccAddresses": ccAddresses,
                                                                        "priority": "Normal",
                                                                        "subject": "XLR - Deployment  FINISH - Release name : ${release.title}",
                                                                        "body": " The XLR Release : ${release.title} is finish OK.  \n"
                                                                                " Description : \n"
                                                                                "  \n"
                                                                                " ${Long_description_SUN_CHANGE}\n"
                                                                                "  \n"
                                                                                "  \n"
                                                                                " Link to the release: https://release-pfi.mycloud.intranatixis.com/${release.id} \n"
                                                                                "  \n"
                                                                                " Thanks \n"
                                                                            }
                                                                        },verify = False)
            if 'id' in reponse_add_webhook_demand_folder.json():
                    if self.parameters['general_info']['type_template'] == 'SKIP':
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'EMAIL : "+phase+" Validation Release' with precondition : "+ precondition)
                    else:
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'EMAIL : "+phase+" Validation Release'")
    def create_phase_env_variable(self):
            ## si type_template est CAB
            if  self.parameters['general_info']['type_template'] == 'CAB' :
                         phase = 'PRODUCTION'
                         XLRGeneric.template_create_variable(self,key='env_'+self.parameters['general_info']['phases'][0], 
                                                             typev='StringVariable', label='', 
                                                             description='', 
                                                             value= phase, 
                                                             requiresValue=False, 
                                                             showOnReleaseStart=False, multiline=False)
            else:
                ## si  une seule phase défini dans la liste ['general_info']['phases']
                if len(self.parameters['general_info']['phases']) == 1:
                    if self.parameters.get('XLD_ENV_'+self.parameters['general_info']['phases'][0]) is None :
                        XLRGeneric.template_create_variable(self,key='env_'+self.parameters['general_info']['phases'][0], 
                                                             typev='StringVariable', 
                                                             label='', 
                                                             description='', 
                                                             value=self.parameters['general_info']['phases'][0], 
                                                             requiresValue=False, 
                                                             showOnReleaseStart=False, 
                                                             multiline=False)
                    ## si  une seule phase défini dans la liste mais plusieurs ENV possible défini dans 'XLD_ENV_'+phase
                    ##creation dune variable de type listbox sous XLR 
                    elif len(self.parameters['XLD_ENV_'+self.parameters['general_info']['phases'][0]]) > 1 :
                        XLRGeneric.create_variable_list_box_env(self,key='env_'+self.parameters['general_info']['phases'][0],
                                                            value=self.parameters['XLD_ENV_'+self.parameters['general_info']['phases'][0]])
                        ## spécifique  APPLICATION pour manager le prefix des env XLD et CONTROLM MCO et PRJ
                        if self.parameters['general_info']['phases'][0] == 'BENCH':
                            if len(self.parameters['XLD_ENV_BENCH']) >= 1:
                                XLRGeneric.template_create_variable(self,key='controlm_prefix_'+self.parameters['general_info']['phases'][0], 
                                                                    typev='StringVariable', 
                                                                    label='controlm_prefix_'+self.parameters['general_info']['phases'][0],
                                                                    description='', 
                                                                    value='', 
                                                                    requiresValue=False, 
                                                                    showOnReleaseStart=False, 
                                                                    multiline=False)
                ##  si plusieur phase demandé dans le YAML dans ['general_info']['phases']
                elif len(self.parameters['general_info']['phases']) > 1:
                        if self.parameters['general_info']['phase_mode'] == 'one_list':
                            ##si on veut une liste de choix 'listbox' au start de la release
                            if self.parameters['general_info']['template_package_mode'] == 'listbox'\
                                and 'DEV' in self.parameters['general_info']['phases']:
                                Choice_ENV = self.parameters['general_info']['phases']
                                self.parameters['general_info']['phases'].remove('DEV')
                            if 'BUILD' in self.parameters['general_info']['phases']:
                                Choice_ENV = self.parameters['general_info']['phases']
                                ### Build est une phase que l on ne peut pas choisir au start d une
                                Choice_ENV.remove('BUILD')
                                XLRGeneric.create_variable_list_box_package(self,key='Choice_ENV',
                                                                            value=Choice_ENV,
                                                                            requiresValue=True,
                                                                            showOnReleaseStart=True)
                                Choice_ENV.insert(0,'BUILD')
                            else: 
                                Choice_ENV = self.parameters['general_info']['phases']
                                XLRGeneric.create_variable_list_box_package(self,
                                                                            key='Choice_ENV',
                                                                            value=Choice_ENV,
                                                                            requiresValue=True,
                                                                            showOnReleaseStart=True)
                            if not self.parameters['general_info']['option_latest'] and  self.parameters['general_info']['template_package_mode'] == 'listbox':
                                if 'BUILD' in self.parameters['general_info']['phases']:
                                    self.parameters['general_info']['phases'].insert(1, 'DEV')
                                else: 
                                    self.parameters['general_info']['phases'].insert(0, 'DEV')
                            for phase in self.parameters['general_info']['phases'] :
                                if  phase != 'BUILD':
                                    if self.parameters.get('XLD_ENV_'+phase) is None: 
                                        if phase == 'DEV':
                                            value = 'DEV'
                                        elif  phase == 'UAT':
                                            value = 'UAT'
                                        elif  phase == 'BENCH':
                                            value = 'BCH'
                                        elif  phase == 'PRODUCTION':
                                            value = 'PRD'
                                    else: 
                                        value =  self.parameters['XLD_ENV_'+phase][0]
                                    XLRGeneric.template_create_variable(self,key='env_'+phase, 
                                                                        typev='StringVariable', 
                                                                        label='', 
                                                                        description='', 
                                                                        value= value, 
                                                                        requiresValue=False, 
                                                                        showOnReleaseStart=False, 
                                                                        multiline=False)
                        elif self.parameters['general_info']['phase_mode'] == 'multi_list':
                            dev_delete = 'no'
                            if not self.parameters['general_info']['option_latest'] \
                                and  self.parameters['general_info']['template_package_mode'] == 'listbox'\
                                and 'DEV' in self.parameters['general_info']['phases']:
                                    self.parameters['general_info']['phases'].remove('DEV')
                                    dev_delete = 'yes'
                            for phase in self.parameters['general_info']['phases']:
                                if self.parameters['general_info']['type_template'] == 'FROM_NAME_BRANCH':
                                     if phase == 'PRODUCTION':
                                        XLRGeneric.template_create_variable(self,key='env_'+phase, 
                                                                            typev='StringVariable', 
                                                                            label='', 
                                                                            description='', 
                                                                            value='PRD', 
                                                                            requiresValue=False, 
                                                                            showOnReleaseStart=False, 
                                                                            multiline=False)
                                     else:
                                        if  self.parameters.get('XLD_ENV_'+phase) is not None:
                                            # self.parameters['XLD_ENV_'+phase].insert(0,'')
                                            XLRGeneric.create_variable_list_box_env(self,'env_'+phase,
                                                                                self.parameters['XLD_ENV_'+phase])
                                        else: 
                                            list_env = []
                                            # list_env.insert(0,'')
                                            list_env.insert(1,phase)
                                            XLRGeneric.create_variable_list_box_env(self,'env_'+phase,
                                                                                list_env)
                                else:
                                    if  self.parameters.get('XLD_ENV_'+phase) is not None:
                                        # self.parameters['XLD_ENV_'+phase].insert(0,'')
                                    
                                        XLRGeneric.create_variable_list_box_env(self,'env_'+phase,
                                                                        self.parameters['XLD_ENV_'+phase])
                                    else: 
                                            list_env = []
                                            # list_env.insert(0,'')
                                            list_env.insert(1,phase)
                                            XLRGeneric.create_variable_list_box_env(self,'env_'+phase,
                                                                                list_env)
                                if phase == 'BENCH' and  self.parameters.get('XLD_ENV_'+phase) is not None: 
                                    for item in self.parameters['XLD_ENV_'+phase] : 
                                        if item == '':
                                            self.parameters['XLD_ENV_'+phase].pop(0)
    def xld_check_package(self,packagename,package_value,phase,grp_id_xldeploy):
        url=self.url_api_xlr+'tasks/'+grp_id_xldeploy +'/tasks'
        value = package_value["XLD_application_path"]
        response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                        "id" :  None,
                                        "type" : "xlrelease.CustomScriptTask",
                                        "title" : "Check XLD package exist "+packagename,
                                        "status" : "PLANNED",
                                        "locked" : False,
                                        "variableMapping": {
                                                    "pythonScript.exists": '${check_xld_'+packagename+'}'
                                                            },
                                        "waitForScheduledStartDate": True,
                                        "pythonScript": {
                                                "xldeployServer": "Configuration/Custom/XLDeploy PFI PROD",
                                                "type": "xldeploy.DoesCIExist",
                                                "id":  None,
                                                "username": "${"+phase+"_username_xldeploy}",
                                                "password": "${"+phase+"_password_xldeploy}",
                                                "ciID": value+"${"+packagename+"_version}",
                                                "throwOnFail": False,
                                                "exists": False
                                                }
                                        },verify = False)
        response.raise_for_status()
        if response.content:
            if 'id' in response.json():
                if self.parameters['general_info']['type_template'] == 'SKIP':
                    self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'XLD-Deploy "+packagename+"' with precondition : "+ precondition)
                else:
                    self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'XLD-Deploy "+packagename+"'" )
    def create_variable_bolean(self,value):
        url_create_variable=self.url_api_xlr+'releases/Applications/'+self.dict_template['template']['xlr_id']+'/variables'
        reponse_create_variable= requests.post(url_create_variable, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                    "id" : None,
                                    "key" : value,
                                    "type" : "xlrelease.BooleanVariable",
                                    "requiresValue" : False,
                                    "showOnReleaseStart" : False,
                                    "label" : value,
                                    "description" : value,
                                    "multiline" : False,
                                    "inherited" : False,
                                    "externalVariableValue" : None,
                                    "valueProvider" : None
                                    },verify = False)
    def add_task_undeploy(self,phase):
                for package_name in  self.list_package:
                    package_value = next(package for package in self.parameters['template_liste_package'] if package_name in package)
                    if self.parameters['template_liste_package'][package_name]['auto_undeploy']:
                        if phase == 'DEV':
                                xld_prefix_env = 'D'
                                if self.parameters.get('XLD_ENV_DEV') is not None:
                                    xld_env = '${env_'+phase+'}'
                                else: 
                                    xld_env = 'DEV'
                                xld_directory_env = 'DEV'
                        elif phase == 'UAT':
                                xld_prefix_env = 'U'
                                if self.parameters.get('XLD_ENV_UAT') is not None:
                                    xld_env = '${env_'+phase+'}'
                                else: 
                                    xld_env = 'UAT'
                                xld_directory_env = 'UAT'
                        elif phase == 'BENCH':
                                if self.parameters.get('XLD_ENV_BENCH') is not None  and len(self.parameters['XLD_ENV_BENCH']) >1:
                                        xld_prefix_env = "${controlm_prefix_BENCH}"
                                elif 'NXFFA' in self.parameters['general_info']['iua']:
                                        xld_prefix_env = 'Q'
                                else:
                                        xld_prefix_env = 'B'
                                if self.parameters.get('XLD_ENV_BENCH') is not None:
                                    xld_env = '${env_'+phase+'}'
                                else: 
                                    xld_env = 'BCH'
                                xld_directory_env = 'BCH'
                        elif phase == 'PRODUCTION':
                                xld_prefix_env = 'P'
                                if self.parameters.get('XLD_ENV_PRODUCTION') is not None:
                                    xld_env = '${env_'+phase+'}'
                                else: 
                                    xld_env = 'PRD'
                                xld_directory_env = 'PRD'
                        if 'APPCODE' in self.parameters['general_info']['iua'] and phase == 'BENCH':
                            value_env = ''
                            if package_name == 'Interfaces':
                                value = 'INT'
                            elif package_name in ['Interface_summit','Interface_summit_COF','TOGE','NON_LOAN_US','DICTIONNAIRE','MOTOR','ROAR']:
                                value = 'INT'
                                value_env ='_NEW'
                            elif package_name == 'Scripts':
                                value = 'SCR'
                            elif package_name == 'SDK':
                                value = 'SDK'
                            elif package_name == 'App':
                                value = 'APP'
                            elif 'FILEBEAT' in package_name:
                                value = 'THEIA'
                            tempo_XLD_environment_path = 'Environments/PFI/APPCODE_APPLICATION/7.6/<ENV>/${BENCH_APPCODE}/${BENCH_APPCODE}_01/'+value+'/<xld_prefix_env>APPCODE_'+value+'_<XLD_env>_01_ENV'+value_env
                            xld_path_deploymentEnvironment = tempo_XLD_environment_path.replace('<XLD_env>',xld_env).replace('<xld_prefix_env>',xld_prefix_env).replace('<ENV>',xld_directory_env)
                        else:
                            xld_path_deploymentEnvironment = self.parameters['template_liste_package'][package_name]['XLD_environment_path'].replace('<XLD_env>',xld_env).replace('<xld_prefix_env>',xld_prefix_env).replace('<ENV>',xld_directory_env)
                        task_release= 'Applications/'+self.dict_template['template']['xlr_id']+'/'+self.dict_template[phase]['xlr_id_phase']
                        url=self.url_api_xlr+'tasks/'+ task_release+'/tasks'
                        applicationNametmp = self.parameters['template_liste_package'][package_name]['XLD_application_path']
                        if applicationNametmp.endswith('/'):
                            applicationName = applicationNametmp.rstrip('/').split('/')[-1]
                        else:
                            applicationName = applicationNametmp
                        response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                        "id" :  None,
                                                        "type" : "xlrelease.CustomScriptTask",
                                                        "title" : "Undeploy "+package_name,
                                                        "status" : "PLANNED",
                                                        "locked" : False,
                                                        "pythonScript": {
                                                                "server": "Configuration/Custom/XLDeploy PFI PROD",
                                                                "type": "xldeploy.Undeploy",
                                                                "id":  None,
                                                                "username": "${"+phase+"_username_xldeploy}",
                                                                "password": "${"+phase+"_password_xldeploy}",
                                                                "connectionFailureCount": 0,
                                                                "deployedApplication": xld_path_deploymentEnvironment+'/'+applicationName,
                                                                "orchestrators": "",
                                                                "deployedApplicationProperties": "",
                                                                "continueIfStepFails": False,
                                                                "numberOfContinueRetrials": 0,
                                                                "pollingInterval": 10,
                                                                "numberOfPollingTrials": 0,
                                                                "displayStepLogs": True,
                                                                "retryCounter": {},
                                                                "connectionRetries": 10,
                                                                "rollbackOnFailure": False,
                                                                "rollbackOnAbort": False,
                                                                "cancelOnError": False,
                                                                "failOnPause": False,
                                                                "failIfApplicationDoesNotExist": False
                                                                }
                                                        },verify = False)
                        response.raise_for_status()
                        if response.content:
                            if 'id' in response.json():
                                if self.parameters['general_info']['type_template'] == 'SKIP':
                                    self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'Undeploy XLD-Deploypackage: "+package_name+"' with precondition : "+ precondition)
                                else:
                                    self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'Undeploy XLD-Deploypackage: "+package_name+"'" )                      
