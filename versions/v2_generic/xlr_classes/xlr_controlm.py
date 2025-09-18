
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

from .xlr_generic import XLRGeneric
class XLRControlm:
    """
    Control-M batch job scheduling integration for XLR templates.

    This class provides functionality to integrate Control-M batch job scheduling
    with XLR release templates. It handles:
    - Control-M folder ordering and management
    - Resource allocation and monitoring
    - Job status tracking and waiting
    - Webhook-based Control-M API integration
    - Environment-specific Control-M server selection

    Control-M is used for:
    - Starting/stopping application services before/after deployment
    - Managing batch job dependencies
    - Coordinating scheduled tasks across environments
    - Resource management and allocation

    Attributes:
        XLRGeneric: Instance of XLRGeneric for base XLR operations
    """

    def __init__(self):
        """
        Initialize XLRControlm with reference to generic XLR operations.

        Sets up the connection to XLRGeneric for base template operations
        while providing specialized Control-M functionality.
        """
        self.XLRGeneric = XLRGeneric()
    def webhook_controlm_ressource(self,phase,grp_id_controlm,task):
        """
        Create Control-M resource management webhook task.

        Args:
            phase (str): Deployment phase (BENCH, PRODUCTION)
            grp_id_controlm (str): XLR group task ID for Control-M operations
            task (dict): Task configuration with resource details

        Creates an XLR webhook task that calls Control-M API to manage
        resource allocation for batch jobs. Automatically selects the
        appropriate Control-M server based on environment.
        """
        requests.post(self.url_api_xlr+'tasks/'+ grp_id_controlm+'/tasks', headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.CustomScriptTask",
                                                            "title" : 'Change RESSOURCE value  '+ task['name'],
                                                            "locked" : True,
                                                            "pythonScript": {
                                                                        "type":"webhook.JsonWebhook",
                                                                        "id": "null",
                                                                        "URL" : self.url_api_controlm +"/resource",
                                                                        "method": "POST",
                                                                        "body":{
                                                                                "ctm": self.CTM_PROD if foldername.lower().startswith('p') else self.CTM_BENCH ,
                                                                                "name": task['name'],
                                                                                "max": int(task['max']),
                                                                                },
                                                                        "username": "${"+phase+"_username_controlm}",
                                                                        "password": "${"+phase+"_password_controlm}"
                                                                        }},verify = False)  
    def script_jython_date_for_controlm(self,phase):
        """
        Create Jython script task for Control-M date formatting.

        Args:
            phase (str): Deployment phase name

        Creates a Jython script that formats the current date in YYYYMMDD
        format for Control-M job scheduling. Sets the 'controlm_today'
        release variable for use in Control-M folder ordering.
        """
        response= requests.post(self.url_api_xlr+'tasks/'+ self.dict_template[phase]['xlr_id_phase']+'/tasks', headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'Put date from input at format for COTROLM demand' ,
                                                            "script":  "##script_jython_date_for_controlm\n"
                                                                        "from time import strftime\n"
                                                                        "date_format = strftime('%Y%m%d')\n"
                                                                        "print(date_format)\n"
                                                                        "releaseVariables['controlm_today'] = date_format\n"                                                                     
                                                                        },verify = False)
        if 'id' in response.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'Put date from input at format for COTROLM demand'" ) 
    def script_jython_date_for_XLR_task_controlm(self,phase,grp_id_controlm):
        """
        Create Jython script for Control-M date formatting in task groups.

        Args:
            phase (str): Deployment phase name
            grp_id_controlm (str): XLR group task ID

        Creates a Jython script that formats the current date in ISO format
        with timezone for Control-M operations within XLR task groups.
        Used for precise timestamp management in batch job scheduling.
        """
        response= requests.post(self.url_api_xlr+'tasks/'+ grp_id_controlm+'/tasks', headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.ScriptTask",
                                                            "locked" : True,
                                                            "title" : 'Put date from input at format for COTROLM demand' ,
                                                            "script":  '##script_jython_date_for_XLR_task_controlm\n'
                                                                        'from java.util import Date, TimeZone\n'
                                                                        'from java.text import SimpleDateFormat\n'
                                                                        'now = Date()\n'
                                                                        'sdf = SimpleDateFormat("yyyy-MM-dd\'T\'HH:mm:ssXXX")\n'
                                                                        'sdf.setTimeZone(TimeZone.getTimeZone("UTC+1"))\n'
                                                                        'formatted_date = sdf.format(now)\n'
                                                                        'releaseVariables["controlm_today"] = formatted_date\n'
                                                                        },verify = False)
        if 'id' in response.json():
                        self.logger_cr.info("ON PHASE : "+ phase.upper()+" --- Add task : 'Put date from input at format for COTROLM demand'" ) 
    def webhook_controlm_order_folder(self,phase,folder_info,grp_id_controlm,task):
        """
        Create Control-M folder ordering webhook task.

        Args:
            phase (str): Deployment phase
            folder_info (dict): Control-M folder configuration
            grp_id_controlm (str): XLR group task ID
            task (str): Task identifier for variable naming

        Creates a webhook task that orders a Control-M folder for execution.
        This triggers batch jobs defined in Control-M for application
        start/stop operations during deployment.
        """    
        foldername = list(folder_info.keys())[0]
        value = "result_orderfolder_"+task.split("_", 2)[-1]+"_"+list(folder_info.keys())[0].replace("${controlm_prefix_BENCH}", "")+"_"+phase
        XLRGeneric.template_create_variable(self,value,'StringVariable','','','',False,False,False )
        # xlr_task_controlm.create_variable(self,value)
        requests.post(self.url_api_xlr+'tasks/'+ grp_id_controlm+'/tasks', headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                            "id" : "null",
                                                            "type" : "xlrelease.CustomScriptTask",
                                                            "title" : 'demand Folder '+ foldername,
                                                            "variableMapping": {
                                                                    "pythonScript.result": '${result_orderfolder_'+task.split("_", 2)[-1]+"_"+list(folder_info.keys())[0].replace("${controlm_prefix_BENCH}", "")+"_"+phase+'}',
                                                                        },
                                                            "locked" : True,
                                                            "pythonScript": {
                                                                        "type":"webhook.JsonWebhook",
                                                                        "id": "null",
                                                                        "URL" : self.url_api_controlm +"/orderFolder",
                                                                        "method": "POST",
                                                                        "body":{
                                                                                "createDuplicate": True,
                                                                                "ctm": self.CTM_PROD if foldername.lower().startswith('p') else self.CTM_BENCH ,
                                                                                "folder": foldername,
                                                                                "ignoreCriteria": folder_info[foldername].get('ignoreCriteria', False),
                                                                                "hold": folder_info[foldername].get('hold', False),
                                                                                "independantFlow": True,
                                                                                "appendJob": folder_info[foldername].get('appendJob', False),
                                                                                "jobs": "",
                                                                                "orderDate": "${controlm_today}",
                                                                                "waitForOrderDate": False
                                                                                },
                                                                        "username": "${"+phase+"_username_controlm}",
                                                                        "password": "${"+phase+"_password_controlm}",
                                                                        "jsonPathExpression": 'Data.statuses',
                                                                        # 'result': 'orderjob'
                                                                        }},verify = False)
    def set_variable_task_controlm(self,phase,grp_id_controlm,count_task_controlm_spec,job):
        """
        Create variable assignment task for Control-M operations.

        Args:
            phase (str): Deployment phase
            grp_id_controlm (str): XLR group task ID
            count_task_controlm_spec (str): Variable name to create
            job (str): Job identifier value to assign

        Creates a Jython script task that sets a release variable
        with a Control-M job identifier for tracking purposes.
        """
        value = count_task_controlm_spec
        XLRGeneric.template_create_variable(self,value,'StringVariable','','','',False,False,False )
        url_set_variable_task_controlm=self.url_api_xlr+'tasks/'+ grp_id_controlm+'/tasks'
        requests.post(url_set_variable_task_controlm, headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                                                "id" : "null",
                                                                "locked" : True,
                                                                "type" : "xlrelease.ScriptTask",
                                                                "title" : 'Create variable for controlm demand', 
                                                                "script": 'releaseVariables[\''+value+'\'] = "'+str(job)+'"',
                                                                            },verify = False)         
    def XLR_plugin_controlm_OrderFolder(self,folder_info,grp_id_controlm):
        foldername2 = list(folder_info.keys())[0].replace('${controlm_prefix_BENCH}','')
        foldername = list(folder_info.keys())[0]
        requests.post(self.url_api_xlr+'tasks/'+ grp_id_controlm+'/tasks', headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                    "id" : "null",
                                    "locked" : False,
                                    "type" : "xlrelease.CustomScriptTask",
                                    "title" : 'Order Folder ' + foldername,
                                    "variableMapping": {
                                                "pythonScript.orderDate": "${controlm_today}",
                                                "pythonScript.folderId": "${id_"+foldername2+"}"
                                                },
                                    "pythonScript": {
                                                "type":"controlM.OrderFolder",
                                                "id": "null",
                                                "server": "Configuration/Custom/API_CONTROLM",
                                                "ctm": self.CTM_PROD if foldername.lower().startswith('p') else self.CTM_BENCH,
                                                "folderName": foldername,
                                                "ignoreCriteria": folder_info[foldername].get('ignoreCriteria', False),
                                                "appendJob": folder_info[foldername].get('appendJob', True),
                                                "hold": False if (folder_info[foldername].get('hold') is None or not folder_info[foldername]['hold'])  else True,
                                                "jobIds": {}
                                                },
                                    "keepPreviousOutputPropertiesOnRetry": False}
                                ,verify = False) 
    def XLR_plugin_controlm_WaitJobStatusById(self,foldername,statusToWaitFor,grp_id_controlm):
        foldername2= foldername.replace('${controlm_prefix_BENCH}','')
        requests.post(self.url_api_xlr+'tasks/'+ grp_id_controlm+'/tasks', headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                    "id" : "null",
                                    "locked" : False,
                                    "type" : "xlrelease.CustomScriptTask",
                                    "title" : 'Wait ' + foldername +' in status'+statusToWaitFor,
                                    "pythonScript": {
                                                "type":"controlM.WaitJobStatusById",
                                                "id": "null",
                                                "server": "Configuration/Custom/API_CONTROLM",
                                                "ctm": self.CTM_PROD if foldername.lower().startswith('p') else self.CTM_BENCH,
                                                "folderName": foldername, 
                                                "attempts": 15,
                                                "interval": 60,
                                                "statusToFailOn": "Ended Not OK",
                                                "statusToWaitFor": statusToWaitFor,
                                                "jobId": "${id_"+foldername2+"}"
                                                },
                                    "keepPreviousOutputPropertiesOnRetry": False}
                                ,verify = False) 
    def XLR_plugin_controlm_edit_job(self,foldername,action,grp_id_controlm):
        foldername2 = foldername('${controlm_prefix_BENCH}','')
        requests.post(self.url_api_xlr+'tasks/'+ grp_id_controlm+'/tasks', headers=self.header,auth=(self.ops_username_api, self.ops_password_api), json={
                                    "id" : "null",
                                    "locked" : False,
                                    "type" : "xlrelease.CustomScriptTask",
                                    "title" : action.upper()+' FOLDER ' + foldername,
                                    "pythonScript": {
                                                "type":"controlM.EditJob",
                                                "id": "null",
                                                "server": "Configuration/Custom/API_CONTROLM",
                                                "ctm": self.CTM_PROD if foldername.lower().startswith('p') else self.CTM_BENCH,
                                                "jobId": "${id_"+foldername2+"}", 
                                                "action": action
                                                },
                                    "keepPreviousOutputPropertiesOnRetry": False}
                                ,verify = False) 
