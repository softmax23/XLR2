
import argparse,yaml,sys,json,configparser
import logging,os
from script_py.xlr_create_template_change.logging import setup_logger,setup_logger_error,setup_logger_detail
from script_py.xlr_create_template_change.check_yaml_file import check_yaml_file
from script_py.xlr_create_template_change.all_class import XLRGeneric,XLRControlm,XLRDynamicPhase,XLRSun,XLRTaskScript
class XLRCreateTemplate(XLRGeneric,XLRSun,XLRTaskScript,XLRControlm,XLRDynamicPhase):
    def __init__(self,parameters):
            ## Load fichier de conf permettant les call API vers XLR pour créer le template
            with open('_conf/xlr_create_template_change.ini', 'r') as file:
                for line in file:
                    key, value = line.strip().split('=')
                    setattr(self, key, value)
            self.header= {'content-type':'application/json','Accept': 'application/json'}
            ## Init variable YAML file in a variable parameters
            self.parameters = parameters
            ## Creation directory if not exist for log file of the template creation 
            if not os.path.exists('log/'+self.parameters['general_info']['name_release']):
                os.makedirs('log/'+self.parameters['general_info']['name_release'])
            ## creation files for logging
            self.logger_cr = setup_logger('LOG_CR', 'log/'+self.parameters['general_info']['name_release']+'/CR.log')
            self.logger_detail = setup_logger_detail('LOG_INFO', 'log/'+self.parameters['general_info']['name_release']+'/info.log')
            self.logger_error = setup_logger_error('LOG_ERROR', 'log/'+self.parameters['general_info']['name_release']+'/error.log')
            ## Init list variable to manage creation XLR task for technical action - OPS or DBA
            self.list_technical_task_done = []
            ## Init list variable to manage creation XLR SUN task for technical action - OPS or DBA
            self.list_technical_sun_task_done = []
            ## Init list variable to manage creation GROUP XLR TASK for CONTROLM - XLDEPLOY TASK 
            self.list_xlr_group_task_done = []
            ## Init variable pour stocker l url du template 
            self.template_url = ''
            ## Init Variable dico pour permettant de valider le fichier  yaml en entré.
            self.dic_for_check = {}
            ## Init Variable dico pour manager le fichier yaml en entré
            self.dict_template = {} 
            ## Focntion permettant de valider le fichier YAML .
            check_yaml_file(self)
            clear = lambda: os.system('clear')
            clear()
            # super().__init__(parameters)
            self.logger_cr.info("")
            self.logger_cr.info("BEGIN")
            self.logger_cr.info("")
            ## Delete du template existant selon la variable dans le YAML : name_release
            self.delete_template()
            ## Récupération id du folder défini dans le YAML ['general_info']['xlr_folder']
            ## et on stocke l if du folder XLR dans self.dict_template['template']['xlr_folder']
            self.find_xlr_folder()
            ## Creation du template et on stocke  lid du tempalte dans self.dict_template['template']['xlr_id'] et dans la variable : self.XLR_template_id
            self.dict_template,self.XLR_template_id = self.CreateTemplate()
            ## Creation des variable  permettant de manager les environnement du template 
            self.create_phase_env_variable()
            ## creation XLR variable release_Variables_in_progress
            self.dict_value_for_template = self.dict_value_for_tempalte()
            self.define_variable_type_template_DYNAMIC()
            self.template_create_variable('release_Variables_in_progress',
                                                'MapStringStringVariable',
                                                '',
                                                '',   
                                                self.release_Variables_in_progress,
                                                False,
                                                False,
                                                False )
            ## Creation de la phase dynamic du template 
            self.dynamics_phase_done = self.dynamic_phase_dynamic()
            ## Creation de variables utilisée au travers des task 
            self.template_create_variable(key='ops_username_api',typev='StringVariable',label='ops_username_api',description='',value=self.ops_username_api,requiresValue=False,showOnReleaseStart=False,multiline=False )
            self.template_create_variable(key='ops_password_api',typev='PasswordStringVariable',label='ops_password_api',description='',value=self.ops_password_api,requiresValue=False,showOnReleaseStart=False,multiline=False )
            self.template_create_variable(key='email_owner_release',typev='StringVariable',label='email_owner_release',description='',value='',requiresValue=False,showOnReleaseStart=False,multiline=False )
            self.template_create_variable(key='xlr_list_phase_selection',typev='StringVariable',label='xlr_list_phase_selection',description='',value='',requiresValue=False,showOnReleaseStart=False,multiline=False )
            self.template_create_variable(key='IUA',typev='StringVariable',label='IUA',description='',value=self.parameters['general_info']['iua'],requiresValue=False,showOnReleaseStart=False,multiline=False )
    def createphase(self,phase):
        ## compteur afin pour le numero des step pour les task SUN 
        self.count_task = 10
        if phase in[ 'BUILD','DEV','UAT']:
            ## Delete dce la phase default
            self.delete_phase_default_in_template()
            ## creation de la phase sous XLR 
            self.add_phase_tasks(phase=phase)
            ## ajout XLR task GATE au début de la phase pour valider la release apres la phase dynamic_release
            self.XLR_GateTask(phase=phase,
                              gate_title="Validation_release_template",
                              description='',
                              cond_title= 'Validation_release_template OK',
                              type_task='Validation_release_template',
                              XLR_ID=self.dict_template[phase]['xlr_id_phase'])
            ## creation des task XLR sur la phase selon la descript de du YAML dans la key 'phase'
            self.parameter_phase_task(phase)
            self.XLR_GateTask(phase=phase,
                                gate_title='DEV team: Validate installation in '+phase,
                                description='',
                                cond_title= 'DEV team: Validate the delivery in '+ phase,
                                type_task='gate_validation_moe',
                                XLR_ID=self.dict_template[phase]['xlr_id_phase'])
        elif phase == 'BENCH' or phase == 'PRODUCTION':
            self.delete_phase_default_in_template()
            self.add_phase_sun(phase)
            self.parameter_phase_sun(phase)
            self.XLRSun_creation_technical_task(phase,'after_deployment')
            self.XLR_GateTask(phase='CREATE_CHANGE_'+phase,
                              gate_title="Validation creation SNOW  ${"+phase+".sun.id}",
                              description='',
                              cond_title= None,
                              type_task='Validation SNOW creation',
                              XLR_ID=self.dict_template['CREATE_CHANGE_'+phase]['xlr_id_phase'])
            if self.parameters['general_info'].get('Template_standard_id') is not None and phase == 'PRODUCTION': 
                self.change_state_sun(phase,'Scheduled')
            else: 
                self.change_state_sun(phase,'Initial validation')
                self.change_wait_state(phase,'WaitForInitialChangeApproval')
            self.add_phase_tasks(phase)
            self.XLR_GateTask(phase=phase,
                              gate_title='OPS TASK : Validation of the SNOW ${'+phase+'.sun.id}',
                              description='',
                              cond_title='change put in state deploiement ${'+phase+'.sun.id}',
                              type_task='check_sun_by_ops',
                              XLR_ID=self.dict_template[phase]['xlr_id_phase'])
            if phase == 'BENCH':
                self.change_state_sun(phase,'Scheduled')
            self.change_state_sun(phase,'Implement')
            self.webhook_get_email_ops_on_change(phase)
            self.script_jython_get_email_ops_on_change(phase)
            self.parameter_phase_task(phase)
            self.creation_technical_task(phase,'after_deployment')
            for item in self.parameters['Phases'][phase]: 
                    if "email_close_release" in item:
                        email_item = item["email_close_release"]
                        self.task_notification(phase=phase,email_item=email_item,aim='email_close_release')
            if phase != 'BENCH': 
                self.XLR_GateTask(phase=phase,
                                gate_title='DEV team: Validate installation in '+phase,
                                description='',
                                cond_title= 'DEV team: Validate the delivery in '+ phase,
                                type_task='gate_validation_moe',
                                XLR_ID=self.dict_template[phase]['xlr_id_phase'])
            
            for item in self.parameters['Phases'][phase]: 
                    if "email_end_release" in item:
                        email_item = item["email_end_release"]
                        self.task_notification(phase=phase,email_item=email_item,aim='email_end_release')
            self.XLRSun_close_sun(phase)
        return self.template_url
    def define_variable_type_template_DYNAMIC(self):
                if len(self.parameters['template_liste_package']) == 1 and self.parameters['general_info']['template_package_mode'] == 'listbox':
                        if len(self.parameters['general_info']['phases']) == 1 and self.parameters['general_info']['phases'][0] == 'DEV':
                            pass
                        else:
                            XLRGeneric.template_create_variable(self,key=self.dict_value_for_template['package'][0]+'_version', typev='StringVariable', label='', description='', value='', requiresValue=False, showOnReleaseStart=False, multiline=False)

                elif len(self.parameters['template_liste_package']) == 1 and self.parameters['general_info']['template_package_mode'] == 'string':
                    if len(self.parameters['general_info']['phases']) == 1 and self.parameters['general_info']['phases'][0]  == 'DEV':
                        pass
                    else:
                        self.add_variable_deliverable_item_showOnReleaseStart()
                    list_package = []

                elif self.parameters['general_info']['template_package_mode'] == 'string' :
                        self.add_variable_deliverable_item_showOnReleaseStart()

                elif self.parameters['general_info']['template_package_mode'] == 'listbox' :
                        list_package = []
                        for package,package_value in self.parameters['template_liste_package'].items():
                            list_package.append(package)
                            XLRGeneric.template_create_variable(self,key=package+'_version', typev='StringVariable', label='', description='', value='', requiresValue=False, showOnReleaseStart=False, multiline=False)

                if 'BENCH' in self.parameters['general_info']['phases'] or 'PRODUCTION' in self.parameters['general_info']['phases']:
                    if 'DEV' not in self.parameters['general_info']['phases'] or 'UAT' not in self.parameters['general_info']['phases']:
                        XLRGeneric.template_create_variable(self,key='Title_SUN_CHANGE', typev='StringVariable', label='Title_SUN_CHANGE', description='Title in SUN change', value='', requiresValue=True, showOnReleaseStart=True, multiline=False)
                        XLRGeneric.template_create_variable(self,key='Long_description_SUN_CHANGE', typev='StringVariable', label='Description in SUN change', description='', value='', requiresValue=True, showOnReleaseStart=True, multiline=True)
                        if ('PRODUCTION' in self.parameters['general_info']['phases'] and 'BENCH' in self.parameters['general_info']['phases']  and len(self.parameters['general_info']['phases']) != 1 ):
                            XLRGeneric.template_create_variable(self,key='BENCH.sun.id', typev='StringVariable', label='SUN Change BENCH', description='Number SUN Change  BENCH', value='', requiresValue=False, showOnReleaseStart=True, multiline=False)
                        if ('PRODUCTION' in self.parameters['general_info']['phases'] and len(self.parameters['general_info']['phases']) == 1 ):
                            XLRGeneric.template_create_variable(self,key='BENCH.sun.id', typev='StringVariable', label='SUN Change BENCH', description='Number SUN Change  BENCH', value='', requiresValue=True, showOnReleaseStart=True, multiline=False)
                    else:
                        XLRGeneric.template_create_variable(self,key='Title_SUN_CHANGE', typev='StringVariable', label='Title_SUN_CHANGE', description='Title in SUN change', value='', requiresValue=False, showOnReleaseStart=True, multiline=False)
                        XLRGeneric.template_create_variable(self,key='Long_description_SUN_CHANGE', typev='StringVariable', label='Description in SUN change', description='', value='', requiresValue=False, showOnReleaseStart=True, multiline=True)
                        if ('PRODUCTION' in self.parameters['general_info']['phases'] and 'BENCH' in self.parameters['general_info']['phases']  and len(self.parameters['general_info']['phases']) != 1 ):
                            XLRGeneric.template_create_variable(self,key='BENCH.sun.id', typev='StringVariable', label='SUN Change BENCH', description='Number SUN Change  BENCH', value='', requiresValue=False, showOnReleaseStart=True, multiline=False)
                        if ('PRODUCTION' in self.parameters['general_info']['phases'] and len(self.parameters['general_info']['phases']) == 1 ):
                            XLRGeneric.template_create_variable(self,key='BENCH.sun.id', typev='StringVariable', label='SUN Change BENCH', description='Number SUN Change  BENCH', value='', requiresValue=True, showOnReleaseStart=True, multiline=False)
                if self.parameters.get('variable_release') is not None and 'EV9' in self.parameters['general_info']['iua']:
                    for variable in self.parameters['variable_release']:
                        if variable == 'Date':
                             requiresValue = False
                             showOnReleaseStart = False
                             value = None
                        else:
                             requiresValue = True
                             showOnReleaseStart = True
                             value = self.parameters['variable_release'][variable]
                        XLRGeneric.template_create_variable(self,key=variable, typev='StringVariable', label='', description='', value=value, requiresValue=requiresValue, showOnReleaseStart=showOnReleaseStart, multiline=False)

                self.name_from_jenkins_value = 'no'
                for package,package_value in self.parameters['template_liste_package'].items():
                    if  package in self.release_Variables_in_progress['list_package']:
                        if package_value.get('mode') is not None:
                            if package_value['mode'] == 'name_from_jenkins':
                                self.name_from_jenkins_value = 'yes'
                                XLRGeneric.template_create_variable(self,key='VARIABLE_XLR_ID_'+package+'_version', 
                                                                    typev='StringVariable', 
                                                                    label='', 
                                                                    description='', 
                                                                    value='', 
                                                                    requiresValue=False, 
                                                                    showOnReleaseStart=False, 
                                                                    multiline=False)

    
    def dynamic_phase_dynamic(self):
        ## Creation d un variable de type dico afin de pouvoir manager la creation de task XLR pour les task technical OPS et DBA.
        self.dict_value_for_template_technical_task = self.dict_value_for_tempalte_technical_task()
         ## il n ya pas de de phase dynamic si il ny a qu une phase, et un seul package et que technical_task n existe pas.
        if self.dict_value_for_template_technical_task.get('technical_task') is None and len(self.dict_value_for_template.get('template_liste_phase')) == 1 and len(self.list_package) == 1:
            pass
        else:
            ##creation de la phase dynamic_release pour y ajouter les task jython.
            self.dict_template = self.add_phase_tasks('dynamic_release')
            ## Si on a du jenkins et que le nom du package est fourni par le jenkins a XLR , exemple les nouvalles  interfaces  LOANIQ
            ## key:value 'mode : name_from_jenkins' present dans template_liste_package
            ## Creatio nde la task permettant de récuprer les id XLD des variable de type: 'VARIABLE_XLR_ID_'+package+'_version' dans la release
            ## qui sera transmise par le biais des jobs jenkins
            if self.name_from_jenkins_value == "yes":
                XLRTaskScript.task_xlr_if_name_from_jenkins(self,'dynamic_release')
            ## Creation task jython pour manager les le delete des phase non demandé au start de la release. 
            if len( self.parameters['general_info']['phases']) > 1:
                ##cas ou dans le YAML on a mis phase_mode: one_list( liste de choix)
                if self.parameters['general_info']['phase_mode'] == 'one_list':
                    if self.parameters['general_info']['template_package_mode'] == 'string':
                            XLRDynamicPhase.XLRJython_delete_phase_one_list_template_package_mode_string(self,'dynamic_release')
                    else:
                        XLRDynamicPhase.XLRJython_delete_phase_one_list(self,'dynamic_release')
                ##cas ou dans le YAML on a mis phase_mode: multi_list un list par ENV defini dans general_info/phases
                elif  self.parameters['general_info']['phase_mode'] == 'multi_list':
                    XLRDynamicPhase.XLRJython_delete_phase_list_multi_list(self,'dynamic_release')
            ## Creation task jython permettant de créer une list package manager par la release 
            if self.parameters['general_info']['template_package_mode']  == 'string':
                    if len(self.parameters['template_liste_package']) > 1:
                        XLRDynamicPhase.script_jython_List_package_string(self,'dynamic_release')
            ## cas loaniq creation, task jython afin de définir le prefix de l environnement de BENCH P ou Q selon le choix fait au start de la release MCO ou PRJ
            if 'BENCH' in self.parameters['general_info']['phases'] and (self.parameters.get('XLD_ENV_BENCH') is not None and len(self.parameters['XLD_ENV_BENCH']) >= 2):
                XLRDynamicPhase.script_jython_define_xld_prefix_new(self,'dynamic_release')
                XLRGeneric.template_create_variable(self,key='controlm_prefix_BENCH', typev='StringVariable', label='controlm_prefix_BENCH', description='', value='B', requiresValue=False, showOnReleaseStart=False, multiline=False)
            ## creation task XLR jython afin de delete les job jenkins non nécessaire si dans le YAML la section jenkins est renseigné.
            ## si il y aplus d un package, sinon cela veut dire que le tempalte ne manage qu un package , donc pas besoin de la tache pour effacer le jenkins. 
            ## et si la phase DEV est demande dans dans le YAML dans la section general_info/phases
            if self.parameters.get('jenkins') is not None:
                if len(self.parameters['template_liste_package']) > 1:
                    if 'DEV' in self.parameters['general_info']['phases']  or 'BUILD' in self.parameters['general_info']['phases']:
                            if self.parameters['general_info']['template_package_mode'] == 'string':
                                XLRDynamicPhase.script_jython_dynamic_delete_task_jenkins_string(self,'dynamic_release')
                            elif self.parameters['general_info']['template_package_mode'] == 'listbox':
                                XLRDynamicPhase.script_jython_dynamic_delete_task_jenkins_listbox(self,'dynamic_release')
            ## Creation de la task XLR jython afin de manager l effacement des task XLR Controlm si il y en a dans le YAML 
            ## key : XLR_task_controlm dans le YAML presente 
            if  self.dict_value_for_template.get('controlm') is not None and len(self.dict_value_for_template['controlm']) !=0:
                    if self.parameters.get('XLD_ENV_BENCH') and len(self.parameters['XLD_ENV_BENCH']) >2:
                        XLRDynamicPhase.script_jython_dynamic_delete_task_controlm_multibench(self,'dynamic_release')
                    else:
                        XLRDynamicPhase.script_jython_dynamic_delete_task_controlm(self,'dynamic_release')
            ## Creation de la task XLR jython permettant d effacer les task XLR XLD selon les package demandé dans la release. 
            if len(self.parameters['template_liste_package']) > 1:
                if 'Y88' in self.parameters['general_info']['iua'] and 'BENCH' in self.parameters['general_info']['phases']:
                    XLRGeneric.template_create_variable(self,key='BENCH_Y88', typev='StringVariable', label='BENCH_Y88', description='', value='', requiresValue=False, showOnReleaseStart=False, multiline=False)
                    XLRDynamicPhase.script_jython_dynamic_delete_task_xld_Y88(self,'dynamic_release')
                else:
                    XLRDynamicPhase.script_jython_dynamic_delete_task_xld(self,'dynamic_release')
            if  self.parameters.get('technical_task_list') is not None:
                XLRGeneric.template_create_variable(self,key='dict_value_for_template_technical_task',typev='StringVariable',label='dict_value_for_template_technical_task',description='',value=self.dict_value_for_template_technical_task,requiresValue=False,showOnReleaseStart=False,multiline=False )

                if ('PRODUCTION' in self.parameters['general_info']['phases'] or 'BENCH' in self.parameters['general_info']['phases']) and self.parameters['general_info']['technical_task_mode'] == 'listbox':
                    XLRDynamicPhase.XLRJythonScript_release_delete_technical_task_ListStringVariable(self,'dynamic_release')
                elif ('PRODUCTION' in self.parameters['general_info']['phases'] or 'BENCH' in self.parameters['general_info']['phases']) and self.parameters['general_info']['technical_task_mode'] == 'string':
                    XLRDynamicPhase.XLRJythonScript_dynamic_release_delete_technical_task_StringVariable(self,'dynamic_release')

            if self.parameters['general_info']['type_template'] == 'FROM_NAME_BRANCH' :
                XLRTaskScript.script_jython_put_value_version(self,'dynamic_release')
            if self.parameters.get('variable_release') is not None and 'Date' in self.parameters['variable_release']:
                XLRTaskScript.script_jython_define_variable_release(self,'dynamic_release')
            return 'done'
        
        
if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument('--infile', nargs=1,
                            help="YAML file to be processed",
                            type=argparse.FileType('r'))
        arguments = parser.parse_args()
        try:
            parameters_yaml = yaml.safe_load(arguments.infile[0])
        except yaml.YAMLError as e:
            print('Error Loading file, it s not yaml reading format:', e)
            print('Please change your file defintion.')
            sys.exit(10)
        json_data= json.dumps(parameters_yaml)
        parameters = json.loads(json_data)
        if not os.path.exists('log/'+parameters['general_info']['name_release']):
                os.makedirs('log/'+parameters['general_info']['name_release'])
        logger = setup_logger('LOG_START', 'log/'+parameters['general_info']['name_release']+'/CR.log')
        # dessiner('nicky')
        CreateTemplate = XLRCreateTemplate(parameters)
        for phase in parameters['general_info']['phases']:
            template_url = CreateTemplate.createphase(phase)
        logger.info("---------------------------")
        logger.info("END CREATION TEMPALTE : OK")
        logger.info("---------------------------")
        logger.info(parameters['general_info']['name_release'])
        logger.info(template_url)
        # dessiner('lapin')
