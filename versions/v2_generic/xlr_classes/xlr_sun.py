
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
class XLRSun:
    """
    ServiceNow (SUN) approval workflow integration for XLR templates.

    This class provides integration with ServiceNow change management system
    for production deployment approvals. It handles:
    - Change request creation and management
    - Approval workflow coordination
    - State transitions (Initial, Scheduled, Implement, etc.)
    - Technical task integration with change requests
    - Email notifications for change management
    - Change request closure and documentation

    SUN integration is used for:
    - Production deployment approvals
    - Change management compliance
    - Audit trail maintenance
    - Risk assessment coordination
    - Rollback planning and execution

    The class coordinates between XLR deployment automation and
    ServiceNow governance processes to ensure compliant production changes.
    """

    def __init__(self):
        """
        Initialize XLRSun with reference to generic XLR operations.

        Sets up the connection to XLRGeneric for base template operations
        while providing specialized ServiceNow integration functionality.
        """
        self.XLRGeneric = XLRGeneric()
    def parameter_phase_sun(self,phase):
        if  (self.parameters['general_info']['template_package_mode'] == 'listbox' and self.parameters['general_info']['option_latest']) or self.parameters['general_info']['option_latest'] :
                id_task = ''+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] 
                if  any(phase+'_username_xldeploy' in d for d in self.dict_template['CREATE_CHANGE_'+phase]):
                        pass
                else:
                        XLRGeneric.add_task_user_input(self,'CREATE_CHANGE_'+phase,'xldeploy',self.dict_template['template']['xlr_id']+'/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] )
                for numtask,task in enumerate(self.parameters['Phases'][phase]):
                        if 'xldeploy' in list(task.keys())[0] :
                                for self.demandxld,xld_value in task[list(task.keys())[0]].items():
                                        if xld_value[0] in self.dict_value_for_template['package']:
                                                        XLRGeneric.add_task_xldeploy_get_last_version(self.demandxld,xld_value,'CREATE_CHANGE_'+phase,id_task)
                #XLRScriptLatest.latest_rename_package_xlr_variable(phase)
        XLRGeneric.template_create_variable(self,'controlm_today','StringVariable','date controlm demand','','',False,False,False )
        XLRGeneric.template_create_variable(self,"change_user_assign",'StringVariable','User assign on change','','',False,False,False )
        self.add_description_CHANGE_SUN = ''
        self.shortDescription = "${Title_SUN_CHANGE}"
        self.Long_description_SUN_CHANGE = "${Long_description_SUN_CHANGE}"
        if 'CTROLM_SPEC' in self.parameters['general_info']['type_template']:
                resultat = any('seq_controlmspec' in d for d in self.parameters['Phases'][phase])
                if resultat: 
                        for item in self.parameters["Phases"][phase]:
                                if "seq_controlmspec" in item:
                                        value = item["seq_controlmspec"]
                                        for grtp_controlm in value:
                                                for self.demandfolderdate in grtp_controlm[list(grtp_controlm.keys())[0]]:
                                                        forjobname = grtp_controlm[list(grtp_controlm.keys())[0]][0]['${DATE}']['job'][0]
                                                        folder = list(grtp_controlm[list(grtp_controlm.keys())[0]][0]['${DATE}']['job'][0])
                                                        job = list(forjobname[list(grtp_controlm.keys())[0]][0]['job'][0])
                                                self.add_description_CHANGE_SUN = ' On date:  ${DATE} \n    FOLDER : '+folder[0]+'\n       JOB : '+job[0]+' \n             MODULE = ${Deploy_script_LOCATION}\n             PARMS = ${Deploy_script_PARAMS}\n'
                                                self.shortDescription = 'Recovery on '+ phase +' with :'+ folder[0] +'-'+job[0]
                                                self.Long_description_SUN_CHANGE = 'Recovery procedure with deployment of XLD package : PATCH_RECOVERY_${Date}_${PATCH_RECOVERY_version}'
        if phase == 'PRODUCTION':
                if 'CAB' not in  self.parameters['general_info']['type_template']  and 'FROM_NAME_BRANCH' not in  self.parameters['general_info']['type_template']:
                        self.dict_template,self.variables_date_sun = self.add_task_date_for_sun_change(phase)
                        XLRGeneric.XLRJythonScript_format_date_from_xlr_input(self,self.variables_date_sun,'CREATE_CHANGE_'+phase)
                        self.add_task_sun_change(phase,'${BENCH.sun.id}')
                elif self.parameters['general_info']['type_template']  == 'CAB':
                             self.XLRSun_update_change_value_CAB(phase) 
                elif self.parameters['general_info']['type_template'] == 'FROM_NAME_BRANCH':
                             self.XLRSun_update_change_value(phase)
        else: 
              self.dict_template,self.variables_date_sun = self.add_task_date_for_sun_change(phase)
        #       if  self.transformation_variable_branch:
        #                         self.XLRTaskScript.XLD_directory_evaluation(self,'CREATE_CHANGE_'+phase)
              XLRGeneric.XLRJythonScript_format_date_from_xlr_input(self,self.variables_date_sun,'CREATE_CHANGE_'+phase)
              self.add_task_sun_change(phase,None)
        for numtask,task in enumerate(self.parameters['Phases'][phase]):
            if 'xldeploy' in list(task.keys())[0] :
                self.XLRSun_creation_technical_task(phase,'before_deployment')                
                self.XLRSun_creation_technical_task(phase,'before_xldeploy')                        

                if 'sunxld_XLR_grp_'+phase not in self.list_xlr_group_task_done :
                                    self.xld_ID_XLR_group_task_grp = XLRGeneric.XLR_group_task(self,
                                        ID_XLR_task= self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'],
                                        type_group='SequentialGroup',
                                        title_group='XLD DEPLOY',     
                                        precondition='')
                                    self.list_xlr_group_task_done.append('sunxld_XLR_grp_'+phase)
                print('task')
                print(task)
                for self.demandxld,xld_value in task[list(task.keys())[0]].items():
                        if xld_value[0] in self.list_package:
                                precondition = ''
                                self.add_task_sun_xldeploy(xld_value,phase,precondition,self.xld_ID_XLR_group_task_grp)
                                self.count_task = self.count_task + 10
                listA= []
                for num,dictionnaire in enumerate(self.parameters['Phases'][phase]):
                        if num > numtask and 'xldeploy' in list(dictionnaire.keys())[0]:
                                listA.append(num)
                if len(listA) == 0:
                        self.XLRSun_creation_technical_task(phase,'after_xldeploy')
            if 'launch_script_windows' in list(task.keys())[0]:
                for groupwin_task in task:
                        for index,sunscript_windows_item in enumerate(groupwin_task[list(groupwin_task.keys())[0]]):
                                self.add_task_sun_launch_script_windows(sunscript_windows_item,phase,index)
                                self.count_task = self.count_task + 10
            if 'launch_script_linux' in list(task.keys())[0]:
                for grouplinux_task in task.items():
                        for index,sunscript_linux_item in enumerate(groupwin_task[list(grouplinux_task.keys())[0]]):
                                self.add_task_sun_launch_script_linux(sunscript_linux_item,phase,index)
                                self.count_task = self.count_task + 10
            if isinstance(task, dict) and 'controlm_resource' in list(task.keys())[0]:
                        # value = task_value
                        self.add_task_sun_controlm_resource(phase,task[list(task.keys())[0]].items(),'')
                        self.count_task = self.count_task + 10 
            elif 'controlm' in list(task.keys())[0]:
                    self.XLRSun_creation_technical_task(phase,'before_deployment')
                    task_XLR_controlm = list(task.keys())[0]
                    for self.grtp_controlm,grtp_controlm_value in task[list(task.keys())[0]].items():
                        if type(grtp_controlm_value) == str:
                                controlm_value_tempo = {}
                                controlm_value_tempo[grtp_controlm_value] = None
                                grtp_controlm_value = controlm_value_tempo
                        # print(grtp_controlm_value)
                        grtp_controlm_value_notype_group = grtp_controlm_value.copy()  # Créer une copie du dictionnaire
                        grtp_controlm_value_notype_group.pop('type_group', None)
                        ctrl_group = False
                        if 'STOP' in self.grtp_controlm or 'START' in self.grtp_controlm or 'CLEAN' in self.grtp_controlm: 
                            if 'STOP' in self.grtp_controlm : 
                                titlegrp = 'STOP'
                            elif 'START' in self.grtp_controlm: 
                                titlegrp = 'START'
                            elif 'CLEAN' in self.grtp_controlm: 
                                titlegrp = 'CLEAN'
                            if 'SUN_XLR_grp_'+titlegrp+'_'+phase not in self.list_xlr_group_task_done :
                                    self.SUN_ID_XLR_group_task_grp = XLRGeneric.XLR_group_task(self,
                                        ID_XLR_task= self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'],
                                        type_group='SequentialGroup',
                                        title_group='CONTROLM : '+titlegrp,     
                                        precondition='')
                                    self.list_xlr_group_task_done.append('SUN_XLR_grp_'+titlegrp+'_'+phase)
                            ctrl_group = True

                        for sub_item_name,sub_item_value in grtp_controlm_value_notype_group.items():
                                if 'folder' in sub_item_value:
                                        sub_item_value = sub_item_value['folder']
                                for folder in sub_item_value:
                                        if type(folder) == str:
                                                foldername= folder
                                                cases = ''
                                                folder= {foldername: {}}
                                        else: 
                                                foldername = list(folder.keys())[0]
                                                cases = folder[foldername]['case']
                                        self.add_task_sun_controlm(phase,list(task.keys())[0],foldername,cases,self.SUN_ID_XLR_group_task_grp)
                                        self.count_task = self.count_task + 10 
            if isinstance(task, dict):
                if 'controlmspec' in list(task.keys())[0]:
                        self.XLRSun_creation_technical_task(phase,'before_deployment')
                        # profil_present = any(item.get('mode') == 'profil' for item in task_value)
                        # # mode_present = any('mode' in d for d in task_value)
                        # print('ororror')
                        # print(profil_present)
                        if task[list(task.keys())[0]].get('mode') is not None:
                                if task[list(task.keys())[0]]['mode'] == 'profil':
                                        self.add_task_sun_controlm_spec_profil(phase,task[list(task.keys())[0]])
                                elif task[list(task.keys())[0]]['mode'] == 'free':
                                        XLRGeneric.template_create_variable(self,'CONTROLM_DEMAND','StringVariable','CONTROLM DEMAND','',task[list(task.keys())[0]]['render'],False,True,True )
                                        XLRGeneric.template_create_variable(self,'FREE_DEMAND_json','StringVariable','FREE_DEMAND_json','','',False,False,False )   
                                        self.add_task_sun_controlm_spec_free(phase)
                                else: 
                                        for self.grtp_controlm in task[list(task.keys())[0]]:
                                                for self.demandfolderdate in self.grtp_controlm[list(self.grtp_controlm.keys())[0]]:         
                                                        self.add_task_sun_controlm_spec(phase,task)
                        self.count_task = self.count_task + 10  
    def add_phase_sun(self,phase):
                url=self.url_api_xlr+'phases/'+self.dict_template['template']['xlr_id']+'/phase'
                try:
                        response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                        "id" : None,
                                        "type" : "xlrelease.Phase",
                                        "flagStatus" : "OK",
                                        "title" : "CREATE_CHANGE_"+phase,
                                        "status" : "PLANNED",
                                        "color" : "#00FF00"
                                        },verify = False)
                        response.raise_for_status()            
                        if response.content:
                                if 'id' in response.json():
                                        self.logger_cr.info("------------------------------------------")
                                        self.logger_cr.info("ADD PHASE : CREATE_CHANGE_"+ phase.upper())
                                        self.logger_cr.info("------------------------------------------") 
                                        self.dict_template['CREATE_CHANGE_'+phase] = {'xlr_id_phase': response.json()["id"] }
                                else: 
                                        self.logger_error.error("ERROR on ADD PHASE : CREATE_CHANGE_"+ phase.upper())
                                        sys.exit(0)
                except requests.exceptions.RequestException as e:
                # Affichage d'un message d'erreur en cas d'échec de la requête
                        self.logger_error.error("Detail ERROR: on ADD PHASE : CREATE_CHANGE_"+ phase.upper())
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error( e)
                        sys.exit(0)

                return self.dict_template
    def add_task_date_for_sun_change(self,phase):  
        variables_date_sun = []       
        list_key_date_sun = []
        for value in [phase+'_sun_start_date',phase+'_sun_end_date']:
                XLRGeneric.template_create_variable(self,value,'DateVariable',value,'',None,False,False,False )
        for value in [phase+'_sun_start_format',phase+'_sun_end_format']:
                XLRGeneric.template_create_variable(self,value,'StringVariable',value,'','',False,False,False )
        for value in self.dict_template['variables']:
            if list(value.keys())[0] == phase+'_sun_end_date':
                variables_date_sun.append(value[phase+'_sun_end_date'])
                list_key_date_sun.append(list(value.keys())[0])
            elif  list(value.keys())[0] == phase+'_sun_start_date':
                variables_date_sun.append(value[phase+'_sun_start_date'])
                list_key_date_sun.append(list(value.keys())[0]) 
        url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
                variables_date_sun.sort(key=lambda x: x != phase+'_sun_start_date')
                response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                "id" : "null",
                                "type" : "xlrelease.UserInputTask",
                                "title" : "Please enter a start date end end date for "+phase,
                                "status" : "PLANNED",
                                "variables": variables_date_sun
                                },verify = False)
                response.raise_for_status() 
                if response.content:
                        if 'id' in response.json():
                                if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : Input Date For SUN "+phase+ " with precondition : "+ precondition)
                                else:
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : Input Date For SUN "+phase)

        except requests.exceptions.RequestException as e:
        # Affichage d'un message d'erreur en cas d'échec de la requête
                self.logger_error.error("Detail ERROR: ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : Input Date For SUN "+phase)
                self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                self.logger_error.error("Error call api : "+url)
                self.logger_error.error( e)
                sys.exit(0)
                
        return self.dict_template,list_key_date_sun
    def add_task_sun_change(self,phase,sun_bench):
        for value in ["Release_Email_resquester"]:
                requiresValue = False
                XLRGeneric.template_create_variable(self,value,'StringVariable','Email of launher of the release','','',False,False,False )
        if self.parameters['general_info']['SUN_approuver'] is not None:
              initialApprover = self.parameters['general_info']['SUN_approuver']
        else: 
              initialApprover = None

        url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try :   
                if phase == "DEV":
                       environment = 'Dev'
                elif phase == "UAT":
                       environment = 'Uat'
                elif phase == "BENCH":
                       environment = 'Bench'
                elif phase == "PRODUCTION":
                       environment = 'Production'
                response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : None,
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : "Creation Change SUN "+phase,
                            "owner": "${release.owner}",
                            "status" : "PLANNED",
                            "variableMapping": {
                                    "pythonScript.changeRequestUrl": "${"+phase+".sun.url}",
                                    "pythonScript.changeRequestNumber": "${"+phase+".sun.id}",
                                },
                            "pythonScript": {
                                "type": "servicenowNxs.CreateChangeRequest",
                                "id": None,
                                "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "iua": self.parameters['general_info']['iua'],
                                    "requestedBy": "${Release_Email_resquester}",
                                    "assignedTo": "",
                                    "assignmentgroup": self.sun_group_ops_team,
                                    "initialApprover": initialApprover,
                                    "environment": environment,
                                    "snowType": 'Normal' if self.parameters['general_info'].get('Template_standard_id') is None else 'Standard',
                                    "modelNumber": self.parameters['general_info'].get('Template_standard_id', ''),
                                    "startDate": "${"+phase+"_sun_start_format}", 
                                    "endDate": "${"+phase+"_sun_end_format}",
                                    "shortDescription": self.shortDescription ,
                                    "createInDraftState": True,
                                    "impact": "Without impact on the service rendered",
                                    "impactedPerimeter": "Restrained",
                                    "riskIfDone": "Low",
                                    "description": "Hello,\n"
                                                   "\n"
                                                   "Thanks to look at the release : ${release.url}"
                                                   "\n"
                                                   "Content of the delivery :\n"
                                                   "\n"
                                                   ""+self.Long_description_SUN_CHANGE+"\n"
                                                   "\n"
                                                   ""+self.add_description_CHANGE_SUN+"\n"
                                                   "\n",
                                    "impactDescription": "RAS",
                                    "rollbackPlan": "RAS",
                                    "assessmentTask": True,
                                    "nonProdChange": sun_bench,
                                    "impactCountries": "France only"}
                            },verify = False)
                response.raise_for_status() 
                if response.content:
                        if 'id' in response.json():
                                if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'Creation SUN CHANGE "+phase +"' with precondition : "+ precondition)

                                else:       
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'Creation SUN CHANGE "+phase+"'")
        except requests.exceptions.RequestException as e:
        # Affichage d'un message d'erreur en cas d'échec de la requête
                self.logger_error.error("Detail ERROR: ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : Creation SUN CHANGE "+phase+"'")
                self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                self.logger_error.error("Error call api : "+url)
                self.logger_error.error( e)
                sys.exit(0)
        return self.dict_template
    def change_state_sun(self,phase,state):
        value_phase= "CREATE_CHANGE_"+ phase.upper()
        valuetask = "Add SUN task"
        if state == 'Assess' or state == 'Initial validation':
                url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        elif self.parameters['general_info'].get('Template_standard_id') is not None and state == 'Scheduled' :
            
                url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
            
        elif state == 'Implement' or state == 'Scheduled':
                valuetask = "Add task"
                value_phase= phase.upper()
                url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        try : 
                response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : None,
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : "Put change ${"+phase+".sun.id} in state "+state ,
                            "owner": "${release.owner}",
                            "dueSoonNotified": False,
                            "status" : "PLANNED",
                            "locked": False,
                            "pythonScript": {
                                "type": "servicenowNxs.UpdateChangeState",
                                "id": None,
                                "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                "changeNumber": '${'+phase+'.sun.id}',
                                "newState": state
                            },
                            },verify = False)
                response.raise_for_status()
                if response.content:
                        if 'id' in response.json():
                                if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                        self.logger_cr.info("ON PHASE : "+value_phase+" --- "+valuetask+" :' Change status SUN CHANGE: "+state+"' with precondition : "+ precondition)
                                else:
                                        self.logger_cr.info("ON PHASE : "+value_phase+" --- "+valuetask+" : 'Change status SUN CHANGE: "+state+"'")

        except requests.exceptions.RequestException as e:
        # Affichage d'un message d'erreur en cas d'échec de la requête
                self.logger_error.error("Detail ERROR: ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'Change status SUN CHANGE: "+state+"'")
                self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                self.logger_error.error("Error call api : "+url)
                self.logger_error.error( e)
                sys.exit(0)
        return self.dict_template
    def change_wait_state(self,phase,state):
        if state in [ 'Assess','WaitForInitialChangeApproval','Initial validation']:
                url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        elif state in [ 'Implement','Scheduled']:
                url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        try:
                response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : None,
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : "wait state SUN "+phase+" APPROVAL CHG: ${"+phase+".sun.id}",
                            "owner": "${release.owner}",
                            "flagStatus": "OK",
                            "dueSoonNotified": False,
                            "waitForScheduledStartDate": True,
                            "delayDuringBlackout": False,
                            "postponedDueToBlackout": False,
                            "postponedUntilEnvironmentsAreReserved": False,
                            "hasBeenFlagged": False,
                            "hasBeenDelayed": False,
                            "taskFailureHandlerEnabled": False,
                            "failuresCount": 0,
                            "variableMapping": {},
                            "externalVariableMapping": {},
                            "tags": [],
                            "checkAttributes": False,
                            "overdueNotified": False,
                            "status" : "PLANNED",
                            "locked": False,
                            "pythonScript": {
                                "type": "servicenowNxs.WaitForInitialChangeApproval",
                                "id": None,
                                "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                "changeNumber": '${'+phase+'.sun.id}',
                                "interval": 1
                            },
                            },verify = False)
                response.raise_for_status() 
                if response.content:
                        if 'id' in response.json():
                                if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'wait state SUN "+phase+" APPROVAL' with precondition : "+ precondition)
                                else:
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'wait state SUN "+phase+" APPROVAL'")

        except requests.exceptions.RequestException as e:
        # Affichage d'un message d'erreur en cas d'échec de la requête
                self.logger_error.error("Detail ERROR: ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : wait state SUN "+phase+" APPROVAL")
                self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                self.logger_error.error("Error call api : "+url)
                self.logger_error.error( e)
                sys.exit(0)
        return self.dict_template
    def sun_create_inc(self,name_phase,state,env,task,spec):
        for value in ["Release_Email_resquester"]:
                XLRGeneric.template_create_variable(self,value,'StringVariable','Email of launher of the release','','',False,False,False )
        if state in [ 'Assess','Scheduled' ]:
                url=self.url_api_xlr+'tasks/'+self.dict_template[spec]['xlr_id_phase'] +'/tasks'
        if 'Bench-' in env:
              env == 'Bench'
        response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : None,
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : "Create INC "+name_phase.upper() ,
                            "owner": "${release.owner}",
                            "dueSoonNotified": False,
                            "status" : "PLANNED",
                            "locked": False,
                            "variableMapping": {    
                                    "pythonScript.incidentNumber": "${sun_id_"+name_phase+"}",
                                },
                            "pythonScript": {
                                "type": "servicenowNxs.CreateIncident",
                                "id": None,
                                "iua": self.parameters['general_info']['iua'],
                                "requestedBy": "${Release_Email_resquester}",
                                "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                "environment": env,
                                "category": "Assistance => Technical assistance",
                                "assignedGroup": self.sun_group_ops_team,
                                "impact": "Low",
                                "urgency": "Low",
                                "shortDescription": task['sun']['short_Description'],
                                "description": task['sun']['Description'],
                            },
                            },verify = False)
        if 'sun_'+name_phase not in self.dict_template:              
                self.dict_template.update({'sun_'+name_phase: {'xlr_task_sun_change': response.json()['id']}})
        else: 
                self.dict_template['sun_'+name_phase].update({'xlr_task_sun_change': response.json()['id']})
        return self.dict_template
    def add_task_sun_dba_factor(self,task,phase,precondition):
        if self.parameters['general_info']['technical_task_mode'] == 'listbox': 
               description = None  
        else: 
               description = "Please can you make factor SQL number: ${"+task['xlr_variable_name']+"}"
        url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try: 
                response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : "null",
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : task['sun_title'],
                            "owner": "${release.owner}",
                            "status" : "PLANNED",
                            "variableMapping": {
                                    "pythonScript.taskNumber": "${"+task['xlr_sun_task_variable_name']+"_"+phase+"}"
                                        },
                            "pythonScript": {
                                "type": "servicenowNxs.AddDeploymentTask",
                                "id": "null",
                                "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "changeRequestNumber": "${"+phase+".sun.id}",
                                    "shortDescription": task['sun_title'],
                                    "description": description,
                                    "assignmentgroup": self.sun_group_dba_team,
                                    "order":self.count_task}
                            },verify = False)
                
                response.raise_for_status()

                if response.content:
                        if 'id' in response.json():
                                if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'Technical Task' with title : '"+task['xlr_item_name']+ "' with precondition : "+ precondition)  
                                else:
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'Technical Task' with title : '"+task['xlr_item_name']+ "'")  
                                       
        except requests.exceptions.RequestException as e:   
                    self.logger_error.error("Detail ERROR: ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'Technical Task' with title : '"+task['xlr_item_name']+"'")
                    self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                    self.logger_error.error("Error call api : "+url)
                    self.logger_error.error(e)
                    sys.exit(0)
        # if 'CREATE_CHANGE_'+phase not in self.dict_template:              
        #         self.dict_template.update({'CREATE_CHANGE_'+phase: {task['xlr_item_name']: response.json()['id']}})
        # else: 
        #         self.dict_template['CREATE_CHANGE_'+phase].update({task['xlr_item_name']: response.json()['id']})
        return self.dict_template
    def add_task_sun_dba_other(self,task,phase,precondition):
        if self.parameters['general_info']['technical_task_mode'] == 'listbox': 
               description = None
        else: 
               description = "${"+task['xlr_variable_name']+"}"
        url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try: 
                response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : "null",
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : task['sun_title'],
                            "owner": "${release.owner}",
                            "status" : "PLANNED",
                            "variableMapping": {
                                    "pythonScript.taskNumber": "${"+task['xlr_sun_task_variable_name']+"_"+phase+"}"
                                        },
                            "pythonScript": {
                                "type": "servicenowNxs.AddDeploymentTask",
                                "id": "null",
                                "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "changeRequestNumber": "${"+phase+".sun.id}",
                                    "shortDescription": task['sun_title'],
                                    "description": description,
                                    "assignmentgroup": self.sun_group_dba_team,
                                    "order": self.count_task}
                            },verify = False)
                response.raise_for_status()

                if response.content:
                        if 'id' in response.json():
                                if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'Technical Task' with title : '"+task['xlr_item_name']+ "' with precondition : "+ precondition)  
                                else:
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'Technical Task' with title : '"+task['xlr_item_name']+ "'")  

        except requests.exceptions.RequestException as e:   
                    self.logger_error.error("Detail ERROR: ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'Technical Task'  with title : '"+task['xlr_item_name']+"'")
                    self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                    self.logger_error.error("Error call api : "+url)
                    self.logger_error.error(e)
                    sys.exit(0)
        return self.dict_template
    def add_task_sun_controlm_resource(self,phase,type_task,title):

        url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
                response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : "null",
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : "CONTROLM CHANGE resource : "+type_task['name'],
                            "owner": "${release.owner}",
                            "status" : "PLANNED",
                            "pythonScript": {
                                "type": "servicenowNxs.AddDeploymentTask",
                                "id": "null",
                                "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "changeRequestNumber": "${"+phase+".sun.id}",
                                    "shortDescription": 'Change Value Resource : '+type_task['name'] ,
                                    "description": "On Controlm " + phase+" change of the value of the resource\n"
                                                   "       Name : " +type_task['name']+"\n"
                                                   "       Max : " +str(type_task['max'])+"\n"
                                                   ,
                                    "assignmentgroup": self.sun_group_ops_team,
                                    "order": self.count_task}
                            },verify = False)
                response.raise_for_status()
                if response.content:
                        if 'id' in response.json():
                                if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'CONTROLM CHANGE resource : "+type_task['name']+ "' with precondition : "+ precondition)  
                                else:
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'CONTROLM CHANGE resource : "+type_task['name']+"'")
        except requests.exceptions.RequestException as e:   
                    self.logger_error.error("Detail ERROR: ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'CONTROLM CHANGE resource : "+type_task['name']+"'")
                    self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                    self.logger_error.error("Error call api : "+url)
                    self.logger_error.error(e)
                    sys.exit(0)
        return self.dict_template
    def add_task_sun_controlm(self,phase,type_task,foldername,cases,idtask):

        if foldername.startswith('P'):
                folder_value = foldername
                foldername = foldername
        else: 
                foldername =foldername
                folder_value = foldername.replace('${controlm_prefix_BENCH}','')
        value = '${task_sun_'+type_task+'_'+folder_value+'_'+phase+'}'
        XLRGeneric.template_create_variable(self,value,'StringVariable','','','',False,False,False )
        # url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        url=self.url_api_xlr+'tasks/'+idtask +'/tasks'
        type_task_value = type_task.split("_")[-1]
        try : 
                response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : "null",
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : "CONTROLM : "+foldername,
                            "owner": "${release.owner}",
                            "status" : "PLANNED",
                            "variableMapping": {
                                    "pythonScript.taskNumber": '${task_sun_'+type_task+'_'+folder_value+'_'+phase+'}'
                                        },
                            "pythonScript": {
                                "type": "servicenowNxs.AddDeploymentTask",
                                "id": "null",
                                "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "changeRequestNumber": "${"+phase+".sun.id}",
                                    "shortDescription": 'Launch folder: '+foldername ,
                                    "description": "Launch on xld on phase " + phase+" for action "+type_task_value+"\n"
                                                   "       Folder : " +foldername+"\n"
                                                   ,
                                    "assignmentgroup": self.sun_group_ops_team,
                                    "order": self.count_task}
                            },verify = False)
                response.raise_for_status()
                if response.content:
                        if 'id' in response.json():
                                if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'CONTROLM' with title : CONTROLM : "+foldername+ " with precondition : "+ precondition)
                                else:
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'CONTROLM' with title : CONTROLM : "+foldername)

        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR : ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'CONTROLM' with title : CONTROLM : "+foldername)
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)  

        return self.dict_template
    def add_task_sun_controlm_spec_profil(self,phase,task_info):
        url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : "null",
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : "CONTROLM : " + task_info['name_profil'],
                            "owner": "${release.owner}",
                            "status" : "PLANNED",
                            "variableMapping": {
                                    "pythonScript.taskNumber": '${task_sun_'+task_info['name_profil']+'_'+phase+"}"
                                        },
                            "pythonScript": {
                                "type": "servicenowNxs.AddDeploymentTask",
                                "id": "null",
                                "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "changeRequestNumber": "${"+phase+".sun.id}",
                                    "shortDescription": "CONTROLM : " + task_info['name_profil'],
                                    "description": "Launch on xld on phase :" + phase+"\n"
                                                   " On date:  ${controlm_date_profil} \n"
                                                   "\n",
                                    "assignmentgroup": self.sun_group_ops_team,
                                    "order": self.count_task}
                            },verify = False)
        if 'CREATE_CHANGE_'+phase not in self.dict_template:
                self.dict_template.update({'CREATE_CHANGE_'+phase: {'task_sun_'+self.dict_value_for_template['controlmspec'][phase]['profil']+'_'+phase: response.json()['id']}})
        else: 
                self.dict_template['CREATE_CHANGE_'+phase].update({'task_sun_'+self.dict_value_for_template['controlmspec'][phase]['profil']+'_'+phase: response.json()['id']})
        return self.dict_template 
    def add_task_sun_controlm_spec_free(self,phase):
        url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'

        response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : "null",
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : "CONTROLM : FREE DEMAND " ,
                            "owner": "${release.owner}",
                            "status" : "PLANNED",
                            "variableMapping": {
                                    "pythonScript.taskNumber": '${task_sun_CONTROLM_FREE_DEMAND_'+phase+'}'
                                        },
                            "pythonScript": {
                                "type": "servicenowNxs.AddDeploymentTask",
                                "id": "null",
                                "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "changeRequestNumber": "${"+phase+".sun.id}",
                                    "shortDescription": "CONTROLM : FREE DEMAND",
                                    "description": "Launch on xld on phase :" + phase+"\n"
                                                   "  ${CONTROLM_DEMAND}\n"
                                                   "\n",
                                    "assignmentgroup": self.sun_group_ops_team,
                                    "order": self.count_task}
                            },verify = False)
        if 'CREATE_CHANGE_'+phase not in self.dict_template:
                self.dict_template.update({'CREATE_CHANGE_'+phase: {'task_sun_controlmspecfree_'+phase: response.json()['id']}})
        else: 
                self.dict_template['CREATE_CHANGE_'+phase].update({'task_sun_controlmspecfree_'+phase: response.json()['id']})
        return self.dict_template 
    def add_task_sun_controlm_spec(self,phase,type_task):
        url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        forjobname = self.grtp_controlm[list(self.grtp_controlm.keys())[0]][0]['${Deploy_script_DATE}']['job'][0]
        folder = list(self.grtp_controlm[list(self.grtp_controlm.keys())[0]][0]['${Deploy_script_DATE}']['job'][0])
        job = list(forjobname[list(self.grtp_controlm.keys())[0]][0]['job'][0])
        response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : "null",
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : "CONTROLM JOB - "  +folder[0],
                            "owner": "${release.owner}",
                            "status" : "PLANNED",
                            "variableMapping": {
                                    "pythonScript.taskNumber": '${task_sun_'+type_task+'_'+phase+"}"
                                        },
                            "pythonScript": {
                                "type": "servicenowNxs.AddDeploymentTask",
                                "id": "null",
                                "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "changeRequestNumber": "${"+phase+".sun.id}",
                                    "shortDescription": "CONTROLM JOB - "  +folder[0],
                                    "description": "Launch on xld on phase :" + phase+"\n"
                                                   " On date:  ${Deploy_script_DATE} \n"
                                                   "    FOLDER : "+folder[0]+"\n"
                                                   "        JOB : "+job[0]+" \n"
                                                   "             MODULE = ${Deploy_script_LOCATION}\n"
                                                   "             PARMS = ${Deploy_script_PARAMS}\n"
                                                   "\n",
                                    "assignmentgroup": self.sun_group_ops_team,
                                    "order": self.count_task}
                            },verify = False)
        if 'CREATE_CHANGE_'+phase not in self.dict_template:
                self.dict_template.update({'CREATE_CHANGE_'+phase: {'task_sun_'+type_task+'_'+phase: response.json()['id']}})
        else: 
                self.dict_template['CREATE_CHANGE_'+phase].update({'task_sun_'+type_task+'_'+phase: response.json()['id']})
        return self.dict_template 
    def add_task_sun_action_ops(self,task,phase,precondition):
        if self.parameters['general_info']['technical_task_mode'] == 'listbox': 
               description = None
        else: 
               description = "${"+task['xlr_variable_name']+"}"
        url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
                response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : "null",
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : task['sun_title'],
                            "owner": "${release.owner}",
                            "status" : "PLANNED",
                            "variableMapping": {
                                        "pythonScript.taskNumber": "${"+task['xlr_sun_task_variable_name']+"_"+phase+"}"
                                                },   
                            "pythonScript": {
                                    "type": "servicenowNxs.AddDeploymentTask",
                                    "id": "null",
                                    "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "changeRequestNumber": "${"+phase+".sun.id}",
                                    "shortDescription":  task['sun_title'],
                                    "description": description,
                                    "assignmentgroup": self.sun_group_ops_team,
                                    "order": self.count_task}
                            },verify = False)
                response.raise_for_status()
                if response.content:
                        if 'id' in response.json():
                                if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'Technical Task' with title : '"+task['xlr_item_name']+ "' with precondition : "+ precondition)
                                else:
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'Technical Task' with title : '"+task['xlr_item_name']+ "'")

        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR : ON PHASE : CREATE_CHANGE_"+ phase.upper()+" ---Add SUN task : 'Technical Task' with title : '"+task['xlr_item_name']+"'")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
        return self.dict_template
    def add_task_sun_launch_script_windows(self,sunscript_windows_item,phase,index):
        precondition = None
        url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try :
                response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                        "id" : "null",
                        "type" : "xlrelease.CustomScriptTask",
                        "title" : "Launch script for "+list(sunscript_windows_item.keys())[0]+" with script "+ sunscript_windows_item[list(sunscript_windows_item.keys())[0]]['script'],
                        "owner": "${release.owner}",
                        "status" : "PLANNED",
                        "variableMapping": {
                                        "pythonScript.taskNumber": "${task_launch_script_windows_"+list(sunscript_windows_item.keys())[0].replace(' ','')+str(index)+"_"+phase+"}"
                                                },
                        "pythonScript": {
                                "type": "servicenowNxs.AddDeploymentTask",
                                "id": "null",
                                "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                "changeRequestNumber": "${"+phase+".sun.id}",
                                "shortDescription": "Launch script for "+list(sunscript_windows_item.keys())[0]+" with script "+ sunscript_windows_item[list(sunscript_windows_item.keys())[0]]['script'],
                                "description": " Ca you launch the script "+ sunscript_windows_item[list(sunscript_windows_item.keys())[0]]['script'] + "on"+ phase+ "\n"
                                                "address:  "+sunscript_windows_item[list(sunscript_windows_item.keys())[0]]['address']+"\n"
                                                "remotePath: "+sunscript_windows_item[list(sunscript_windows_item.keys())[0]]['remotePath']+"\n",
                                "assignmentgroup": self.sun_group_ops_team,
                                "order": self.count_task}
                        },verify = False)
        
                response.raise_for_status() 
                if response.content:
                        if 'id' in response.json():
                                if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase+" --- Add SUN  task : "+list(sunscript_windows_item.keys())[0]+" with title : Launch script for "+list(sunscript_windows_item.keys())[0]+" with script "+ sunscript_windows_item[list(sunscript_windows_item.keys())[0]]['script']+ " with precondition : "+ precondition)  
                                else:
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase+" --- Add SUN  task : "+list(sunscript_windows_item.keys())[0]+" with title : Launch script for "+list(sunscript_windows_item.keys())[0]+" with script "+ sunscript_windows_item[list(sunscript_windows_item.keys())[0]]['script'])  

        except requests.exceptions.RequestException as e:
        # Affichage d'un message d'erreur en cas d'échec de la requête
                self.logger_error.error("Detail ERROR: ON PHASE : CREATE_CHANGE_"+ phase+" --- Add SUN  task : "+list(sunscript_windows_item.keys())[0]+" with title : Launch script for "+list(sunscript_windows_item.keys())[0]+" with script "+ sunscript_windows_item[list(sunscript_windows_item.keys())[0]]['script'])
                self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                self.logger_error.error("Error call api : "+url)
                self.logger_error.error( e)
                sys.exit(0)
        if 'CREATE_CHANGE_'+phase not in self.dict_template:              
                self.dict_template.update({'CREATE_CHANGE_'+phase: {'task_launch_script_windows_'+list(sunscript_windows_item.keys())[0].replace(' ','')+str(index)+"_"+phase: response.json()['id']}})
        else: 
                self.dict_template['CREATE_CHANGE_'+phase].update({'task_launch_script_windows_'+list(sunscript_windows_item.keys())[0].replace(' ','')+str(index)+"_"+phase: response.json()['id']})
        return self.dict_template
    def add_task_sun_launch_script_linux(self,sunscript_linux_item,phase,index):
        precondition = None
        url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try :

                response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                "id" : "null",
                                "type" : "xlrelease.CustomScriptTask",
                                "title" : "Launch script for "+list(sunscript_linux_item.keys())[0]+" with script "+ sunscript_linux_item[list(sunscript_linux_item.keys())[0]]['script'],
                                "owner": "${release.owner}",
                                "status" : "PLANNED",
                                "variableMapping": {
                                                "pythonScript.taskNumber": "${task_launch_script_linux_"+list(sunscript_linux_item.keys())[0].replace(' ','')+str(index)+"_"+phase+"}"
                                                        },
                                "pythonScript": {
                                        "type": "servicenowNxs.AddDeploymentTask",
                                        "id": "null",
                                        "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                        "changeRequestNumber": "${"+phase+".sun.id}",
                                        "shortDescription": "Launch script for "+list(sunscript_linux_item.keys())[0]+" with script "+ sunscript_linux_item[list(sunscript_linux_item.keys())[0]]['script'],
                                        "description": " Ca you launch the script "+ sunscript_linux_item[list(sunscript_linux_item.keys())[0]]['script'] + "on"+ phase+ "\n"
                                                        "address:  "+sunscript_linux_item[list(sunscript_linux_item.keys())[0]]['address']+"\n"
                                                        "remotePath: "+sunscript_linux_item[list(sunscript_linux_item.keys())[0]]['remotePath']+"\n",
                                        "assignmentgroup": self.sun_group_ops_team,
                                        "order": self.count_task}
                                },verify = False)
                
                response.raise_for_status() 
                if response.content:
                        if 'id' in response.json():
                                if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase+" --- Add SUN  task : "+list(sunscript_linux_item.keys())[0]+" with title : Launch script for "+list(sunscript_linux_item.keys())[0]+" with script "+ sunscript_windows_item[list(sunscript_windows_item.keys())[0]]['script']+ " with precondition : "+ precondition)  
                                else:
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase+" --- Add SUN  task : "+list(sunscript_linux_item.keys())[0]+" with title : Launch script for "+list(sunscript_linux_item.keys())[0]+" with script "+ sunscript_windows_item[list(sunscript_windows_item.keys())[0]]['script'])  

        except requests.exceptions.RequestException as e:
        # Affichage d'un message d'erreur en cas d'échec de la requête
                self.logger_error.error("Detail ERROR: ON PHASE : CREATE_CHANGE_"+ phase+" --- Add SUN  task : "+list(sunscript_linux_item.keys())[0]+" with title : Launch script for "+list(sunscript_linux_item.keys())[0]+" with script "+ sunscript_linux_item[list(sunscript_windows_item.keys())[0]]['script'])
                self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                self.logger_error.error("Error call api : "+response)
                self.logger_error.error( e)
                sys.exit(0)
        if 'CREATE_CHANGE_'+phase not in self.dict_template:              
                self.dict_template.update({'CREATE_CHANGE_'+phase: {'task_launch_script_windows_'+list(sunscript_linux_item.keys())[0].replace(' ','')+str(index)+"_"+phase: response.json()['id']}})
        else: 
                self.dict_template['CREATE_CHANGE_'+phase].update({'task_launch_script_windows_'+list(sunscript_linux_item.keys())[0].replace(' ','')+str(index)+"_"+phase: response.json()['id']})
        return self.dict_template
    def add_task_sun_xldeploy(self,xld_value,phase,precondition,idtask):  
        # xld_path_deploymentEnvironment = self.parameters['XLD_path_ENV']
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
        package_name = next(package for package in self.parameters['template_liste_package'] if xld_value[0] in package)
        if 'APPCODE' in self.parameters['general_info']['iua'] and phase == 'BENCH': 
            value_env = ''
            if package_name == 'Interfaces':
                value = 'INT'
            elif package_name  in ['Interface_summit','Interface_summit_COF','Interface_TOGE','Interface_TOGE_ACK','Interface_NON_LOAN_US','DICTIONNAIRE','Interface_MOTOR','Interface_ROAR_ACK','Interface_ROAR']:
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
        elif self.parameters['general_info'].get('xld_standard') is not None and self.parameters['general_info']['xld_standard']: 
            xld_path_deploymentEnvironment = self.parameters['template_liste_package'][package_name]['XLD_environment_path'].replace('<XLD_env>',xld_env).replace('<xld_prefix_env>',xld_prefix_env).replace('<ENV>',xld_directory_env)
        else:     
            xld_path_deploymentEnvironment = self.parameters['template_liste_package'][package_name]['XLD_environment_path'].replace('<XLD_env>',xld_env).replace('<xld_prefix_env>',xld_prefix_env).replace('<ENV>',xld_directory_env)
        # verion_package = "${"+list(package_value.keys())[0]+"_version}"
        # if  (self.parameters['general_info']['template_package_mode'] == 'listbox' and self.parameters['general_info']['option_latest']) or self.parameters['general_info']['option_latest'] :
        #         deploymentPackage = verion_package
        # else: 
        if self.parameters['general_info']['type_template'] == 'MULTIPACKAGE_AT_ONCE' :
            verion_package = self.parameters['template_liste_package'][package_name]['package_build_name']
        elif self.parameters['general_info']['type_template'] == 'FROM_NAME_BRANCH':
            verion_package = self.parameters['template_liste_package'][package_name]['package_build_name'].replace('<version>','').replace('NAME PACKAGE','')+"${"+package_name+"_version}"
        else:    
            verion_package = "${"+package_name+"_version}"
        if 'DEV' not in self.parameters['general_info']['phases'] and not self.parameters['general_info']['option_latest']:
                deploymentPackage = self.parameters['template_liste_package'][package_name]['XLD_application_path'].replace('Applications/','')+''+verion_package
        elif 'DEV' in self.parameters['general_info']['phases'] or 'BUILD' in self.parameters['general_info']['phases']: 
                deploymentPackage = self.parameters['template_liste_package'][package_name]['XLD_application_path'].replace('Applications/','')+''+verion_package
        else: 
                deploymentPackage = self.parameters['template_liste_package'][package_name]['XLD_application_path'].replace('Applications/','')+''+verion_package
        url=self.url_api_xlr+'tasks/'+idtask +'/tasks'
        try: 
                response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : "null",
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : "XLD-Deploy " + package_name,
                            "owner": "${release.owner}",
                            "status" : "PLANNED",
                            "variableMapping": {
                                        "pythonScript.taskNumber": '${task_sun_xld_'+package_name+'_'+phase+"}"
                                                },
                            "pythonScript": {
                                    "type": "servicenowNxs.AddDeploymentTask",
                                    "id": "null",
                                    "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "changeRequestNumber": "${"+phase+".sun.id}",
                                    "shortDescription": "Deploy XLD "+ package_name,
                                    "description": " Can you deliver on XLD "+ phase+ "\n"
                                                "Env:  "+xld_path_deploymentEnvironment+"\n"
                                                "With package: "+deploymentPackage+"\n",
                                    "assignmentgroup": self.sun_group_ops_team,
                                    "order": self.count_task}
                            },verify = False)

                response.raise_for_status()
                if response.content:
                        if 'id' in response.json():
                                if precondition == '':
                                        precondition = 'None'
                                if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- add SUN task : 'XLD-Deploy " + package_name +"' with precondition : "+ precondition)  
                                else:
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- add SUN task : 'XLD-Deploy " + package_name+"'")  

        except requests.exceptions.RequestException as e:   
                                self.logger_error.error("Detail ERROR : ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- add SUN task : 'XLD-Deploy " + package_name+"'")  
                                self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                                self.logger_error.error("Error call api : "+url)
                                self.logger_error.error(e)
                                sys.exit(0)
        return self.dict_template
    def update_variable(self,key,value,requiresValue,showOnReleaseStart):
        url=self.url_api_xlr+'releases/Applications/'+self.dict_template['template']['xlr_id']+'/variables'
        response= requests.get(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api),verify = False)
        for item in response.json():
              if item['key'] == key:
                url_delete_variable=self.url_api_xlr+'releases/'+item['id']
                response= requests.put(url_delete_variable, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                "type" : "xlrelease.StringVariable",
                                "id" : item['id'],
                                "key" : key,
                                "value" : value,
                                "requiresValue" : requiresValue,
                                "showOnReleaseStart" : showOnReleaseStart,
                                },verify = False)
    def update_delete(self,key):
        url=self.url_api_xlr+'Applications/'+self.dict_template['template']['xlr_id']+'/variables'
        response= requests.get(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api),verify = False)
        for item in response.json():
              if item['key'] == key:
                url_delete_variable=self.url_api_xlr+'releases/'+item['id']
                response= requests.delete(url_delete_variable, headers=self.header,auth=(self.ops_username_api, self.ops_password_api),verify = False)
    def XLRSun_task_close_sun_task(self,task_to_close,title,id_task,type_task,phase):
        if  'xldeploy' in type_task:
                try: 
                        response= requests.post(self.url_api_xlr+'tasks/'+id_task +'/tasks', headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                        "id" : "null",
                                        "type" : "xlrelease.CustomScriptTask",
                                        "title" : "XLD-Deploy " + self.demandxld,
                                        "owner": "${release.owner}",
                                        "locked" : False,
                                        "status" : "PLANNED",
                                        "pythonScript": {
                                                "type": "servicenowNxs.UpdateTask",
                                                "id": "null",
                                                "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                                "taskNumber":  task_to_close,
                                                "status":  "Close complete",
                                                "closeNotes": "task ok",
                                                "updateAs": "${change_user_assign}"
                                                }
                                        },verify = False)

                        response.raise_for_status()
                        precondition = 'None'
                        if response.content:
                                if 'id' in response.json():
                                        if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                                self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : SUN closing for XLD task : "+self.demandxld+" with title : 'XLD-Deploy " + self.demandxld+"' with precondition : "+ precondition)  
                                        else:
                                                self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : SUN closing for XLD task : "+self.demandxld+" with title : 'XLD-Deploy " + self.demandxld+"'")  

                except requests.exceptions.RequestException as e:   
                                self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper()+" --- Add task : SUN closing for XLD task : "+self.demandxld+" with title : XLD-Deploy " + self.demandxld)
                                self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                                self.logger_error.error("Error call api : "+self.url_api_xlr+'tasks/'+id_task +'/tasks')
                                self.logger_error.error(e)
                                sys.exit(0)
        else: 
                try: 
                        response= requests.post(self.url_api_xlr+'tasks/'+id_task +'/tasks', headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                        "id" : "null",
                                        "type" : "xlrelease.CustomScriptTask",
                                        "title" : "CLose task " + title,
                                        "owner": "${release.owner}",
                                        "locked" : True,
                                        "status" : "PLANNED",
                                        "pythonScript": {
                                                "type": "servicenowNxs.UpdateTask",
                                                "id": "null",
                                                "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                                "taskNumber":  task_to_close,
                                                "status":  "Close complete",
                                                "closeNotes": "task ok",
                                                "updateAs": "${change_user_assign}"
                                                }
                                        },verify = False)
                        
                        precondition = 'None'
                        response.raise_for_status()
                        if response.content:
                                if 'id' in response.json():
                                        if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                                self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : SUN closing : "+title+" with title : CLose task '" + title +"' with precondition : "+ precondition)
                                        else:
                                                self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : SUN closing : "+title+" with title : CLose task " + title )  
                except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper()+" --- Add task : SUN closing : "+title+" with title : CLose task " + title)
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+self.url_api_xlr+'tasks/'+id_task +'/tasks')
                        self.logger_error.error(e)
                        sys.exit(0)
    def XLRSun_task_wait_status_sun_task(self,phase,task_to_close):
        url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        try: 
                response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : "null",
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : "CLose task",
                            "owner": "${release.owner}",
                            "status" : "PLANNED",
                            "locked" : True,
                            "pythonScript": {
                                    "type": "servicenowNxs.UpdateTask",
                                    "id": "null",
                                    "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "taskNumber":  "${"+task_to_close+"}",
                                    "status":  "Done",
                                    "updateAs": "${change_user_assign}"
                                    }
                            },verify = False)
                response.raise_for_status()
                if response.content:
                        if 'id' in response.json():
                                if precondition == '':
                                        precondition = 'None'
                                if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : CLose SUN task. For task SUN variale : "+task_to_close+" with precondition : "+ precondition)
                                else:
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : CLose SUN task. For task SUN variale : "+task_to_close)  

        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : CLose SUN task. For task SUN variale : "+task_to_close)
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)
    def XLRSun_close_sun(self,phase):
        url=self.url_api_xlr+'tasks/'+self.dict_template[phase]['xlr_id_phase'] +'/tasks'
        try: 
                response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                            "id" : None,
                            "type" : "xlrelease.CustomScriptTask",
                            "title" : "Close Change ${"+phase+".sun.id}",
                            "owner": "${release.owner}",
                            "status" : "PLANNED",
                            "pythonScript": {
                                "type": "servicenowNxs.UpdateChangeState",
                                "id": None,
                                "servicenowNxsServer": "Configuration/Custom/Sun Prod",
                                    "changeNumber": "${"+phase+".sun.id}",
                                    "newState": "Closed",
                                    "comment":  "done",
                                    "closeCode": "Successful",
                                    "closeNotes": "done"}
                            },verify = False)
                response.raise_for_status()
                if response.content:
                        if 'id' in response.json():
                                if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'Close Change ${"+phase+".sun.id}' with precondition : "+ precondition) 
                                else:
                                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'Close Change ${"+phase+".sun.id}' ")  

        except requests.exceptions.RequestException as e:   
                        self.logger_error.error("Detail ERROR: ON PHASE : "+ phase.upper()+" --- Add task :'Close Change ${"+phase+".sun.id}' ")
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error(e)
                        sys.exit(0)

        return self.dict_template
    def XLRSun_sun_template_create_variable(self,key,typev,label,description,value,requiresValue,showOnReleaseStart,multiline ):
        if 'variables' not in self.dict_template:
                        self.dict_template.update({'variables': []})
        everexist = 'no'
        if type(key) != list:
            if any(key in d for d in self.dict_template['variables']):
                everexist = 'yes'
        if everexist == 'no':
                url=self.url_api_xlr+'Applications/'+self.dict_template['template']['xlr_id']+'/variables'
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

                        response.raise_for_status()
                        if 'A variable already exists by key' not in str(response.content):
                                try: 
                                        self.dict_template['variables'].append({key: response.json()['id']})
                                except TypeError as e:
                                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                                        self.logger_error.error("Update Dico 'dict_template' in error for key : "+ key+" with value: "+value )
                                        self.logger_error.error("TypeError : "+str(e))
                                        sys.exit(0)
                                except  Exception as e:
                                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                                        self.logger_error.error("Update Dico 'dict_template' in error for key : "+ key+" with value: "+value )
                                        self.logger_error.error("Exception : "+str(e))
                                        sys.exit(0)
                        if 'password'in key or 'Token' in key:
                                value = 'secret'
                        if value =='':
                                value = 'Empty'
                        if label == '':
                                label = 'No Label'
                        self.logger_detail.info("CREATE VARIABLE : "+key+" with label : " + label +" --- XLD type variable : "+ typev+ " With value: "+str(value))
                except requests.exceptions.RequestException as e:
                        self.logger_error.error("Detail ERROR: CREATE VARIABLE : "+key+" with label : " + label +" --- XLD type variable : "+ typev+ " With value: "+str(value))
                        self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                        self.logger_error.error("Error call api : "+url)
                        self.logger_error.error( e)
                        sys.exit(0)
        return self.dict_template 
    def XLRSun_update_change_value(self,phase):
        url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try:
                response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : "Update "+phase+" CHANGE :  ${"+phase+".sun.id}",
                                                            "script":   "##script_jython_update_change_value\n"
                                                                        "import ssl\n"
                                                                        "import base64\n"
                                                                        "import urllib2\n"
                                                                        "import json\n"
                                                                        "proxy = urllib2.ProxyHandler({'http': 'proxybusiness.intranet:3125'})\n"
                                                                        "opener = urllib2.build_opener(proxy)\n"
                                                                        "urllib2.install_opener(opener)\n"
                                                                        "url = 'https://itaas.api.intranatixis.com/support/sun/change/v1/updateChange'\n"
                                                                        "request = urllib2.Request(url)\n"
                                                                        "password = release.passwordVariableValues['$' + '{ops_password_api}']\n"
                                                                        "username = releaseVariables['ops_username_api'] \n"
                                                                        "base64string = base64.b64encode('%s:%s' % (username, password))\n"
                                                                        "Long_description_SUN_CHANGE_lines = releaseVariables['Long_description_SUN_CHANGE'].splitlines()\n"
                                                                        "u_description_tempo=  [line + '\\n'  for line in Long_description_SUN_CHANGE_lines]\n"
                                                                        "u_description_tempo = ''.join(u_description_tempo)\n"
                                                                        "u_description =   'Hello,\\nContent of the delivery :\\n'+u_description_tempo+'\\nThanks to look at the release : ${release.url}'\n"
                                                                        "data = json.dumps({'u_change_number': '${PRODUCTION.sun.id}','u_hprod_related_change': '${BENCH.sun.id}', 'u_short_description': '${Title_SUN_CHANGE}', 'u_description': u_description})\n"
                                                                        "request.add_header('Content-Type', 'application/json')\n"
                                                                        "request.add_header('Authorization', 'Basic %s' % base64string)\n"
                                                                        "request.add_data(data)\n"
                                                                        "request.get_method = lambda: 'POST'\n"
                                                                        "response = urllib2.urlopen(request, context=ssl._create_unverified_context())\n"
                                                                        "result = response.read()\n"
                                                                        "result_json = json.loads(result)\n"
                                                                        "print (result_json)\n"

                                                                        },verify = False)
                response.raise_for_status() 
                if response.content:
                        if 'id' in response.json():
                                if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'Update "+phase+" CHANGE' ")
                                else:
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'Update "+phase+" CHANGE'")


        except requests.exceptions.RequestException as e:
        # Affichage d'un message d'erreur en cas d'échec de la requête
                self.logger_error.error("Detail ERROR: ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'Update "+phase+" CHANGE' ")
                self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                self.logger_error.error("Error call api : "+url)
                self.logger_error.error( e)
                sys.exit(0)
    def XLRSun_update_change_value_CAB(self,phase):
        url=self.url_api_xlr+'tasks/'+self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'] +'/tasks'
        try: 
                response= requests.post(url, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : "Update "+phase+" CHANGE :  ${"+phase+".sun.id}",
                                                            "script":  "##script_jython_update_change_value_CAB\n"
                                                                        "import ssl\n"
                                                                        "import base64\n"
                                                                        "import urllib2\n"
                                                                        "import json\n"
                                                                        "proxy = urllib2.ProxyHandler({'http': 'proxybusiness.intranet:3125'})\n"
                                                                        "opener = urllib2.build_opener(proxy)\n"
                                                                        "urllib2.install_opener(opener)\n"
                                                                        "url = 'https://itaas.api.intranatixis.com/support/sun/change/v1/updateChange'\n"
                                                                        "request = urllib2.Request(url)\n"
                                                                        "password = release.passwordVariableValues['$' + '{ops_password_api}']\n"
                                                                        "username = releaseVariables['ops_username_api'] \n"
                                                                        "base64string = base64.b64encode('%s:%s' % (username, password))\n"
                                                                        "Long_description_SUN_CHANGE_lines = releaseVariables['Long_description_SUN_CHANGE'].splitlines()\n"
                                                                        "u_description_tempo=  [line + '\\n'  for line in Long_description_SUN_CHANGE_lines]\n"
                                                                        "u_description_tempo = ''.join(u_description_tempo)\n"
                                                                        "u_description =   'Hello,\\nContent of the delivery :\\n'+u_description_tempo+'\\nThanks to look at the release : ${release.url}'\n"
                                                                        "data = json.dumps({'u_change_number': '${PRODUCTION.sun.id}','u_hprod_related_change': '${BENCH.sun.id}', 'u_short_description': '${Title_SUN_CHANGE}', 'u_description': u_description})\n"
                                                                        "request.add_header('Content-Type', 'application/json')\n"
                                                                        "request.add_header('Authorization', 'Basic %s' % base64string)\n"
                                                                        "request.add_data(data)\n"
                                                                        "request.get_method = lambda: 'POST'\n"
                                                                        "response = urllib2.urlopen(request, context=ssl._create_unverified_context())\n"
                                                                        "result = response.read()\n"
                                                                        "result_json = json.loads(result)\n"
                                                                        "print (result_json)\n"

                                                                        },verify = False)
                response.raise_for_status() 
                if response.content:
                        if 'id' in response.json():
                                if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'Update "+phase+" CHANGE' -- MODE : CAB ")
                                else: 
                                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : 'Update "+phase+" CHANGE' -- MODE : CAB ")

        except requests.exceptions.RequestException as e:
        # Affichage d'un message d'erreur en cas d'échec de la requête
                self.logger_error.error("Detail ERROR: ON PHASE : CREATE_CHANGE_"+ phase.upper()+" --- Add SUN task : Update "+phase+" CHANGE ")
                self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                self.logger_error.error("Error call api : "+url)
                self.logger_error.error( e)
                sys.exit(0)
    def XLRSun_creation_technical_task(self,phase,cat_technicaltask):
            if  'technical_task' in self.dict_value_for_template_technical_task:
                if cat_technicaltask+'_done_'+phase not in self.list_technical_sun_task_done:
                    if  self.dict_value_for_template_technical_task['technical_task'] .get(cat_technicaltask) is not None:
                        self.logger_cr.info("ON PHASE : CREATE_CHANGE_"+phase.upper()+" --- Add SUN task : 'Technical Task' : "+ cat_technicaltask )
                        for technical_task in self.dict_value_for_template_technical_task['technical_task'] [cat_technicaltask]:
                            if 'task_dba_factor' in technical_task :
                                XLRGeneric.template_create_variable(self,key=self.dict_value_for_template_technical_task['technical_task'] [cat_technicaltask][technical_task]['xlr_sun_task_variable_name']+"_"+phase, typev='StringVariable', label='', description='', value='', requiresValue=False, showOnReleaseStart=False, multiline=False)
                                precondition = ''
                                self.add_task_sun_dba_factor(self.dict_value_for_template_technical_task['technical_task'] [cat_technicaltask][technical_task],phase,precondition)
                                self.count_task = self.count_task + 10
                            elif 'task_dba_other' in technical_task :
                                precondition = ''
                                self.add_task_sun_dba_other(self.dict_value_for_template_technical_task['technical_task'] [cat_technicaltask][technical_task],phase,precondition)
                                self.count_task = self.count_task + 10
                            elif 'task_ops' in technical_task:
                                self.update_variable('task_sun_'+technical_task+'_'+phase,'',False,False)
                                precondition = ''
                                self.add_task_sun_action_ops(self.dict_value_for_template_technical_task['technical_task'] [cat_technicaltask][technical_task],phase,precondition)
                                self.count_task = self.count_task + 10
            self.list_technical_sun_task_done.append(cat_technicaltask+'_done_'+phase)
    def XLRSun_check_status_sun_task(self,phase,type_task,technical_task,cat_technicaltask,precondition):
        typesun_task_number = "${"+type_task+"}"
        title = self.dict_value_for_template_technical_task['technical_task'] [cat_technicaltask][technical_task]['sun_title']
        if self.parameters['general_info']['type_template']  == 'SKIP' :
                        variable_xlr = self.dict_value_for_template_technical_task['technical_task'] [cat_technicaltask][technical_task]['xlr_item_name']
                        precondition = "'"+variable_xlr+"' in releaseVariables['"+cat_technicaltask+"']"
        else:
                    precondition = ''
        task_release = self.dict_template['template']['xlr_id']+'/'+self.dict_template[phase]['xlr_id_phase']
        urtcheck_status_sun_task = self.url_api_xlr+'tasks/'+task_release+'/tasks'
        url="https://itaas.api.intranatixis.com/support/sun/change/v1/getTasks?id=${"+phase+".sun.id}&offset=0"
        try:
            response= requests.post(urtcheck_status_sun_task, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : False,
                                                            "title" : title ,
                                                            "script": "##check_status_sun_task\n"
                                                                    "import ssl\n"
                                                                    "import base64\n"
                                                                    "import urllib2\n"
                                                                    "import json\n"
                                                                    "import time\n"
                                                                    "context = ssl._create_unverified_context()\n"
                                                                    "def call_api():\n"
                                                                    "   api_url = '"+url+"'\n"
                                                                    "   password= release.passwordVariableValues['$' + '{ops_password_api}']\n"
                                                                    "   login = '${ops_username_api}'\n"
                                                                    "   auth_header = 'Basic ' + base64.b64encode(login + ':' + password)\n"
                                                                    "   request = urllib2.Request(api_url)\n"
                                                                    "   request.add_header('Authorization', auth_header)\n"
                                                                    "   response = urllib2.urlopen(request, context=context)\n"
                                                                    "   data = json.loads(response.read())\n"
                                                                    "   return data\n"
                                                                    "while True:\n"
                                                                    "    result = call_api()\n"
                                                                    "    state = next(task['state'] for task in result['Data'] if task['number'] == '"+typesun_task_number+"')\n"
                                                                    "    print('Task Sun State:'+ state+' from Change: ${"+phase+".sun.id}')\n"
                                                                    "    if state == 'Closed':\n"
                                                                    "        print('Task Sun State:'+ state+' from Change: ${"+phase+".sun.id}')\n"
                                                                    "        break\n"
                                                                    "    time.sleep(300)\n"
                                                                    },verify = False)
            response.raise_for_status()
            if response.content:
                if 'id' in response.json():
                    if self.parameters['general_info'].get('type_template') is not None and self.parameters['general_info']['type_template'] == 'SKIP':
                        self.logger_cr.info("ON PHASE : "+ phase+" --- Add task : 'Cheack status - "+title+"' with precondition : "+ precondition)
                    else:
                        self.logger_cr.info("ON PHASE : "+ phase+" --- Add task : 'Cheack status - "+title+"'")
        except requests.exceptions.RequestException as e:
                    self.logger_error.error("Detail ERROR: ON PHASE : "+ phase+" --- Add task : Cheack status - "+title)
                    self.logger_error.error("File: "+ os.path.basename(inspect.currentframe().f_code.co_filename)+" --Class: "+self.__class__.__name__+" --Function : "+inspect.currentframe().f_code.co_name+" --Line : "+str(inspect.currentframe().f_lineno))
                    self.logger_error.error("Error call api : "+urtcheck_status_sun_task)
                    self.logger_error.error(response.content)
                    self.logger_error.error(e)
                    sys.exit(0)                    
