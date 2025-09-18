"""
XLRControlm - Control-M batch job scheduling integration

This module contains the enhanced XLRControlm class that inherits from XLRBase
for Control-M integration functionality.
"""

from .xlr_base import XLRBase

class XLRControlm(XLRBase):
    """
    Control-M batch job scheduling integration for XLR templates.

    This class inherits from XLRBase and provides specialized functionality
    for integrating Control-M batch job scheduling with XLR release templates.

    Key features:
    - Control-M folder ordering and management
    - Resource allocation and monitoring
    - Job status tracking and waiting
    - Webhook-based Control-M API integration
    - Environment-specific Control-M server selection

    No longer requires composition with XLRGeneric - inherits all base
    functionality directly from XLRBase.
    """

    def __init__(self):
        """
        Initialize XLRControlm with base XLR functionality.

        Inherits all core XLR operations from XLRBase without requiring
        a separate XLRGeneric instance.
        """
        super().__init__()

    def webhook_controlm_ressource(self, phase, grp_id_controlm, task):
        """
        Create Control-M resource management webhook task.

        Args:
            phase (str): Deployment phase (BENCH, PRODUCTION)
            grp_id_controlm (str): XLR group task ID for Control-M operations
            task (dict): Task configuration with resource details

        Creates an XLR webhook task that calls Control-M API to manage
        resource allocation for batch jobs. Automatically selects the
        appropriate Control-M server based on environment.

        Uses inherited template_create_variable method from XLRBase.
        """
        # Create variable for result storage
        value = "result_resource_" + task['name'] + "_" + phase
        self.template_create_variable(value, 'StringVariable', '', '', '', False, False, False)

        # Create webhook task using inherited XLR API methods
        url_webhook = self.url_api_xlr + 'tasks/' + grp_id_controlm + '/tasks'
        try:
            response = requests.post(url_webhook, headers=self.header,
                                   auth=(self.ops_username_api, self.ops_password_api),
                                   json={
                                       "id": "null",
                                       "type": "xlrelease.CustomScriptTask",
                                       "title": 'Change RESOURCE value ' + task['name'],
                                       "locked": True,
                                       "pythonScript": {
                                           "type": "webhook.JsonWebhook",
                                           "id": "null",
                                           "URL": self.url_api_controlm + "/resource",
                                           "method": "POST",
                                           "body": {
                                               "ctm": self.CTM_PROD if phase.lower().startswith('p') else self.CTM_BENCH,
                                               "name": task['name'],
                                               "max": int(task['max']),
                                           },
                                           "username": "${" + phase + "_username_controlm}",
                                           "password": "${" + phase + "_password_controlm}"
                                       }
                                   }, verify=False)
            response.raise_for_status()
            if 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add Control-M resource task: " + task['name'])
        except Exception as e:
            self.logger_error.error("Error creating Control-M resource webhook: " + str(e))
            sys.exit(0)

    def script_jython_date_for_controlm(self, phase):
        """
        Create Jython script task for Control-M date formatting.

        Args:
            phase (str): Deployment phase name

        Creates a Jython script that formats the current date in YYYYMMDD
        format for Control-M job scheduling. Sets the 'controlm_today'
        release variable for use in Control-M folder ordering.

        Uses inherited XLR API methods from XLRBase.
        """
        url_date_script = self.url_api_xlr + 'tasks/' + self.dict_template[phase]['xlr_id_phase'] + '/tasks'
        try:
            response = requests.post(url_date_script, headers=self.header,
                                   auth=(self.ops_username_api, self.ops_password_api),
                                   json={
                                       "id": "null",
                                       "type": "xlrelease.ScriptTask",
                                       "locked": True,
                                       "title": 'Put date from input at format for CONTROLM demand',
                                       "script": (
                                           "##script_jython_date_for_controlm\n"
                                           "from time import strftime\n"
                                           "date_format = strftime('%Y%m%d')\n"
                                           "print(date_format)\n"
                                           "releaseVariables['controlm_today'] = date_format\n"
                                       )
                                   }, verify=False)
            response.raise_for_status()
            if 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add task : 'Put date from input at format for CONTROLM demand'")
        except Exception as e:
            self.logger_error.error("Error creating Control-M date script: " + str(e))
            sys.exit(0)

    def webhook_controlm_order_folder(self, phase, folder_info, grp_id_controlm, task):
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

        Uses inherited methods from XLRBase for variable creation and API calls.
        """
        foldername = list(folder_info.keys())[0]
        value = "result_orderfolder_" + task.split("_", 2)[-1] + "_" + foldername.replace("${controlm_prefix_BENCH}", "") + "_" + phase

        # Use inherited method instead of composition
        self.template_create_variable(value, 'StringVariable', '', '', '', False, False, False)

        url_order_folder = self.url_api_xlr + 'tasks/' + grp_id_controlm + '/tasks'
        try:
            response = requests.post(url_order_folder, headers=self.header,
                                   auth=(self.ops_username_api, self.ops_password_api),
                                   json={
                                       "id": "null",
                                       "type": "xlrelease.CustomScriptTask",
                                       "title": 'demand Folder ' + foldername,
                                       "variableMapping": {
                                           "pythonScript.result": '${' + value + '}',
                                       },
                                       "locked": True,
                                       "pythonScript": {
                                           "type": "webhook.JsonWebhook",
                                           "id": "null",
                                           "URL": self.url_api_controlm + "/orderFolder",
                                           "method": "POST",
                                           "body": {
                                               "createDuplicate": True,
                                               "ctm": self.CTM_PROD if foldername.lower().startswith('p') else self.CTM_BENCH,
                                               "folder": foldername,
                                               "ignoreCriteria": folder_info[foldername].get('ignoreCriteria', False),
                                               "hold": folder_info[foldername].get('hold', False),
                                               "independantFlow": True,
                                               "appendJob": folder_info[foldername].get('appendJob', False),
                                               "jobs": "",
                                               "orderDate": "${controlm_today}",
                                               "waitForOrderDate": False
                                           },
                                           "username": "${" + phase + "_username_controlm}",
                                           "password": "${" + phase + "_password_controlm}",
                                           "jsonPathExpression": 'Data.statuses',
                                       }
                                   }, verify=False)
            response.raise_for_status()
            if 'id' in response.json():
                self.logger_cr.info("ON PHASE : " + phase.upper() + " --- Add Control-M order folder task: " + foldername)
        except Exception as e:
            self.logger_error.error("Error creating Control-M order folder webhook: " + str(e))
            sys.exit(0)

    # Additional Control-M methods would be implemented here
    # Each using inherited functionality from XLRBase instead of composition