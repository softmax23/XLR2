# Guide de Configuration YAML - Générateur de Templates XLR

## 📋 Table des Matières

{toc}

---

## 🎯 Introduction

Ce document explique comment configurer le fichier `template.yaml` pour le générateur de templates XLR. Ce fichier YAML définit tous les paramètres nécessaires pour créer automatiquement des pipelines de déploiement XLR.

> **ℹ️ Info**
> Le générateur XLR supporte trois versions :
> - **V1** : Version originale (spécifique Y88/LoanIQ)
> - **V2** : Version générique modulaire
> - **V3** : Architecture propre (recommandée)

---

## 🏗️ Structure Générale du Fichier YAML

```yaml
general_info:          # Informations générales du template
technical_task_list:   # Tâches techniques pre/post déploiement
XLD_ENV_*:            # Environnements XL Deploy par phase
template_liste_package: # Définition des packages à déployer
jenkins:              # Configuration Jenkins
Phases:               # Séquences de déploiement par phase
```

---

## 📝 Section 1 : general_info

### 🔧 Configuration de Base

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `type_template` | String | Type de template généré | `DYNAMIC` |
| `xlr_folder` | String | Dossier XLR de destination | `PFI/APPCODE_Application/OPS_RELEASE_TEST` |
| `iua` | String | Code IUA de l'application | `NXAPPCODE` |
| `appli_name` | String | Nom de l'application | `Application` |
| `name_release` | String | Nom du template de release | `"NXAPPCODE_ALL_PACKAGE_GENERIC"` |

### 🚀 Phases de Déploiement

```yaml
general_info:
  phases:
    - DEV          # Développement
    - UAT          # Tests d'acceptation
    - BENCH        # Pré-production
    - PRODUCTION   # Production
```

### ⚙️ Modes de Configuration

| Paramètre | Valeurs Possibles | Description |
|-----------|-------------------|-------------|
| `technical_task_mode` | `string` / `list` | Mode de gestion des tâches techniques |
| `template_package_mode` | `string` / `listbox` | Mode de sélection des packages |
| `phase_mode` | `multi_list` / `single` | Mode de sélection des phases |

### 📧 Configuration SUN

```yaml
general_info:
  SUN_approuver: ops.team@company.com  # Email d'approbation ServiceNow
  option_latest: false                 # Utiliser la dernière version
  xld_group: True                     # Regroupement XLD
```

> **⚠️ Attention**
> Remplacez `APPCODE` par le code de votre application et `Application` par le nom réel de votre application.

---

## 🛠️ Section 2 : technical_task_list

Cette section définit les tâches techniques à exécuter à différents moments du déploiement.

### 📅 Phases d'Exécution

```yaml
technical_task_list:
  before_deployment:    # Avant le déploiement
    - task_ops
    - task_dba_other

  before_xldeploy:      # Avant XL Deploy
    - task_ops

  after_xldeploy:       # Après XL Deploy
    - task_ops
    - task_dba_factor

  after_deployment:     # Après le déploiement
    - task_ops
    - task_dba_factor
```

### 🔍 Types de Tâches Disponibles

| Type de Tâche | Description |
|----------------|-------------|
| `task_ops` | Tâches opérationnelles génériques |
| `task_dba_other` | Tâches DBA spécifiques |
| `task_dba_factor` | Tâches DBA de factorisation |

---

## 🌍 Section 3 : Environnements XLD (XLD_ENV_*)

Définit les environnements XL Deploy disponibles pour chaque phase.

### 🏢 Configuration par Environnement

```yaml
XLD_ENV_DEV:
  - DEV_01
  - DEV_02
  - DEV_INT
  - DEV_TNR

XLD_ENV_UAT:
  - UAT_01
  - UAT_02
  - UAT_03

XLD_ENV_BENCH:
  - MCO;Q
  - PRJ;B

XLD_ENV_PRODUCTION:
  - PRD_01
```

### 📋 Conventions de Nommage

| Phase | Préfixe | Exemple |
|-------|---------|---------|
| DEV | `DEV_` | `DEV_01`, `DEV_INT` |
| UAT | `UAT_` | `UAT_01`, `UAT_02` |
| BENCH | Codes métier | `MCO;Q`, `PRJ;B` |
| PRODUCTION | `PRD_` | `PRD_01` |

---

## 📦 Section 4 : template_liste_package

Cette section est **cruciale** - elle définit tous les packages à déployer.

### 🏗️ Structure d'un Package

```yaml
template_liste_package:
  NomDuPackage:
    package_build_name: "Nom du build Jenkins"
    controlm_mode: "master|Independant"
    XLD_application_path: "Chemin application XLD"
    XLD_environment_path: "Chemin environnement XLD"
    auto_undeploy: True|False|[liste]
    mode: "CHECK_XLD|name_from_jenkins"
```

### 📋 Types de Packages Standard

#### 🔧 Package Interfaces

```yaml
Interfaces:
  package_build_name: BUILD-76-V<version>
  controlm_mode: Independant
  XLD_application_path: Applications/PFI/APPCODE_APPLICATION/INT/APPCODE_INT_APPLICATION/
  XLD_environment_path: Environments/PFI/APPCODE_APPLICATION/7.6/<ENV>/<ENV>/<XLD_env>/INT/<xld_prefix_env>APPCODE_INT_<XLD_env>_ENV
  auto_undeploy: False
  mode: CHECK_XLD
```

#### 📜 Package Scripts

```yaml
Scripts:
  package_build_name: PKG_SCRIPTS-V7.6-<version>
  controlm_mode: master
  XLD_application_path: Applications/PFI/APPCODE_APPLICATION/APP/APPCODE_SCR_APPLICATION/
  XLD_environment_path: Environments/PFI/APPCODE_APPLICATION/7.6/<ENV>/<ENV>/<XLD_env>/SCR/<xld_prefix_env>APPCODE_SCR_<XLD_env>_ENV
  auto_undeploy: False
  mode: CHECK_XLD
```

#### 🚀 Package Application Principale

```yaml
App:
  package_build_name: Application_app_7.6.2.1.<version>
  controlm_mode: master
  XLD_application_path: Applications/PFI/APPCODE_APPLICATION/APP/APPCODE_APP_APPLICATION_76/
  XLD_environment_path: Environments/PFI/APPCODE_APPLICATION/7.6/<ENV>/<ENV>/<XLD_env>/APP/<xld_prefix_env>APPCODE_APP_<XLD_env>_ENV
  auto_undeploy: False
  mode: CHECK_XLD
```

### 🔑 Paramètres Détaillés

| Paramètre | Description | Valeurs |
|-----------|-------------|---------|
| `package_build_name` | Nom du package Jenkins | Utilise `<version>` comme placeholder |
| `controlm_mode` | Mode Control-M | `master` (dépendant) / `Independant` |
| `XLD_application_path` | Chemin application dans XLD | Chemin absolu XLD |
| `XLD_environment_path` | Chemin environnement XLD | Utilise variables `<ENV>`, `<XLD_env>` |
| `auto_undeploy` | Désinstallation automatique | `True/False` ou liste de packages |
| `mode` | Mode de gestion | `CHECK_XLD` / `name_from_jenkins` |

### 🔄 Variables Dynamiques

| Variable | Remplacée par | Exemple |
|----------|---------------|---------|
| `<version>` | Version sélectionnée | `1.2.3` |
| `<ENV>` | Phase de déploiement | `DEV`, `UAT`, `PRODUCTION` |
| `<XLD_env>` | Environnement XLD | `DEV_01`, `PRD_01` |
| `<xld_prefix_env>` | Préfixe environnement | Généré automatiquement |

---

## 🔨 Section 5 : Configuration Jenkins

### 🏭 Serveur Jenkins

```yaml
jenkins:
  jenkinsServer: Configuration/Custom/Jenkins-APPCODE
  taskType: jenkins.Build
  username: apnxappcodep_jenkins@company.com
  apiToken: ${apiToken_jenkins_iua}
  valueapiToken: 11a474dedca78e202f62f82c6544eb7778
  password:  # Alternative à apiToken
```

### 🚀 Jobs Jenkins par Package

```yaml
jenkinsjob:
  App:
    jobName: APPCODE/job/Projet_appcode-application-Package
    parameters:
      - BRANCH_NAME=${App_version}
    precondition: None

  Scripts:
    jobName: APPCODE/job/appcode-application-scripts-7.6-Pipeline
    parameters:
      - BRANCH_NAME=${Scripts_version}
    precondition: None
```

### 🔧 Configuration Job

| Paramètre | Description | Exemple |
|-----------|-------------|---------|
| `jobName` | Nom du job Jenkins | `APPCODE/job/MonJob` |
| `parameters` | Paramètres à passer | `BRANCH_NAME=${Package_version}` |
| `precondition` | Condition préalable | `None` ou expression |

---

## 🔄 Section 6 : Phases de Déploiement

### 🏗️ Structure d'une Phase

```yaml
Phases:
  PHASE_NAME:
    - seq_xldeploy:         # Déploiement XLD
        Titre Groupe:
          - Package1
          - Package2

    - XLR_task_controlm:    # Tâche Control-M
        Titre Groupe:
          type_group: SequentialGroup
          folder:
            - NomDossier:
                hold: True/False
                case:
                  - Package1
```

### 🌟 Phase DEV/UAT (Simple)

```yaml
DEV:
  - seq_xldeploy:
      XLD DICTIONNAIRE:
        - DICTIONNAIRE
  - seq_xldeploy:
      XLD App:
        - App
  - seq_xldeploy:
      XLD Scripts:
        - Scripts
```

### 🏭 Phase BENCH/PRODUCTION (Complexe)

```yaml
BENCH:
  # 1. Arrêt des services
  - XLR_task_controlm:
      STOP APPLICATION:
        type_group: SequentialGroup
        folder:
          - BDCP_OSTOP_${controlm_prefix_BENCH}APPCODE_XLR:
              hold: False
              case:
                - App
                - Scripts

  # 2. Déploiement
  - seq_xldeploy:
      XLD App:
        - App

  # 3. Redémarrage des services
  - XLR_task_controlm:
      START APPLICATION:
        type_group: SequentialGroup
        folder:
          - BDCP_OSTART_${controlm_prefix_BENCH}APPCODE_XLR:
              hold: False
              case:
                - App
```

### 📋 Types d'Actions

| Type | Description | Usage |
|------|-------------|-------|
| `seq_xldeploy` | Déploiement XL Deploy | Déploiement d'applications |
| `XLR_task_controlm` | Tâche Control-M | Gestion des services batch |

### ⚙️ Options Control-M

| Option | Description | Valeurs |
|--------|-------------|---------|
| `type_group` | Type de groupement | `SequentialGroup` / `ParallelGroup` |
| `hold` | Mise en attente | `True` / `False` |
| `case` | Packages concernés | Liste des packages |

---

## 🎯 Section 7 : Exemples Complets

### 🔰 Configuration Minimale

```yaml
general_info:
  type_template: DYNAMIC
  xlr_folder: PFI/MONAPP/OPS_RELEASE
  iua: NXMONAPP
  appli_name: MonApplication
  phases:
    - DEV
  name_release: "NXMONAPP_SIMPLE"
  technical_task_mode: string
  template_package_mode: string
  phase_mode: multi_list

template_liste_package:
  App:
    package_build_name: MonApp-<version>
    controlm_mode: master
    XLD_application_path: Applications/PFI/MONAPP/APP/
    XLD_environment_path: Environments/PFI/MONAPP/<ENV>/
    auto_undeploy: False
    mode: CHECK_XLD

XLD_ENV_DEV:
  - DEV_01

jenkins:
  jenkinsServer: Configuration/Custom/Jenkins-MONAPP
  username: monapp_jenkins@company.com

Phases:
  DEV:
    - seq_xldeploy:
        Déploiement MonApp:
          - App
```

### 🚀 Configuration Complète Multi-Packages

```yaml
general_info:
  type_template: DYNAMIC
  xlr_folder: PFI/MONAPP/OPS_RELEASE
  iua: NXMONAPP
  appli_name: MonApplication
  phases:
    - DEV
    - UAT
    - PRODUCTION
  name_release: "NXMONAPP_COMPLET"
  SUN_approuver: ops.monapp@company.com

technical_task_list:
  before_deployment:
    - task_ops
  after_deployment:
    - task_ops

template_liste_package:
  Frontend:
    package_build_name: Frontend-<version>
    controlm_mode: Independant
    XLD_application_path: Applications/PFI/MONAPP/FRONT/
    XLD_environment_path: Environments/PFI/MONAPP/<ENV>/FRONT/
    auto_undeploy: False
    mode: CHECK_XLD

  Backend:
    package_build_name: Backend-<version>
    controlm_mode: master
    XLD_application_path: Applications/PFI/MONAPP/BACK/
    XLD_environment_path: Environments/PFI/MONAPP/<ENV>/BACK/
    auto_undeploy:
      - Frontend
    mode: CHECK_XLD

jenkins:
  jenkinsServer: Configuration/Custom/Jenkins-MONAPP
  username: monapp_jenkins@company.com
  jenkinsjob:
    Frontend:
      jobName: MONAPP/job/frontend-build
      parameters:
        - VERSION=${Frontend_version}
    Backend:
      jobName: MONAPP/job/backend-build
      parameters:
        - VERSION=${Backend_version}

XLD_ENV_DEV: [DEV_01]
XLD_ENV_UAT: [UAT_01]
XLD_ENV_PRODUCTION: [PRD_01]

Phases:
  DEV:
    - seq_xldeploy:
        Déploiement Backend:
          - Backend
    - seq_xldeploy:
        Déploiement Frontend:
          - Frontend

  UAT:
    - seq_xldeploy:
        Déploiement Backend:
          - Backend
    - seq_xldeploy:
        Déploiement Frontend:
          - Frontend

  PRODUCTION:
    - XLR_task_controlm:
        ARRÊT SERVICES:
          type_group: SequentialGroup
          folder:
            - PDCP_STOP_MONAPP:
                hold: False
                case:
                  - Backend
                  - Frontend

    - seq_xldeploy:
        Déploiement Backend:
          - Backend
    - seq_xldeploy:
        Déploiement Frontend:
          - Frontend

    - XLR_task_controlm:
        DÉMARRAGE SERVICES:
          type_group: SequentialGroup
          folder:
            - PDCP_START_MONAPP:
                hold: False
                case:
                  - Backend
                  - Frontend
```

---

## ✅ Section 8 : Validation et Bonnes Pratiques

### 🔍 Points de Validation

#### ✅ Cohérence des Noms
- [ ] Les noms de packages sont cohérents entre `template_liste_package`, `jenkins.jenkinsjob` et `Phases`
- [ ] Les phases définies dans `general_info.phases` existent dans la section `Phases`
- [ ] Les environnements `XLD_ENV_*` correspondent aux phases

#### ✅ Chemins XLD
- [ ] Les chemins `XLD_application_path` existent dans XL Deploy
- [ ] Les chemins `XLD_environment_path` utilisent les variables correctes
- [ ] La structure de dossiers respecte les conventions

#### ✅ Configuration Jenkins
- [ ] Les jobs Jenkins existent et sont accessibles
- [ ] Les paramètres correspondent aux attentes des jobs
- [ ] Les credentials Jenkins sont configurés

### 🎯 Bonnes Pratiques

#### 📝 Nommage
```
✅ Bon : NXMONAPP_ALL_PACKAGES_V1.0
❌ Mauvais : template_test_123
```

#### 🔗 Dépendances
```yaml
# ✅ Bon : Auto-undeploy logique
Backend:
  auto_undeploy: False

Frontend:
  auto_undeploy:
    - Backend  # Frontend dépend de Backend
```

#### ⚡ Performance
```yaml
# ✅ Bon : Groupement logique en parallèle
- XLR_task_controlm:
    ARRÊT SERVICES:
      type_group: ParallelGroup  # Services indépendants
```

### 🚨 Erreurs Courantes

| Erreur | Impact | Solution |
|--------|--------|----------|
| Package défini mais pas utilisé | Template gonflé | Supprimer le package inutile |
| Chemin XLD inexistant | Échec de déploiement | Vérifier dans XL Deploy |
| Job Jenkins incorrect | Échec de build | Vérifier l'URL du job |
| Phases incohérentes | Template non fonctionnel | Aligner `general_info.phases` et `Phases` |

---

## 🔧 Section 9 : Variables et Substitutions

### 🔄 Variables Automatiques

Le générateur XLR crée automatiquement des variables pour chaque package :

| Pattern | Description | Exemple |
|---------|-------------|---------|
| `${PackageName_version}` | Version du package | `${App_version}` |
| `${controlm_prefix_PHASE}` | Préfixe Control-M | `${controlm_prefix_BENCH}` |
| `<ENV>` | Phase courante | `DEV`, `PRODUCTION` |
| `<XLD_env>` | Environnement XLD sélectionné | `DEV_01`, `PRD_01` |

### 🏷️ Variables Custom

Vous pouvez définir des variables personnalisées :

```yaml
general_info:
  custom_variables:
    DATABASE_HOST: "db-${ENV}.company.com"
    LOG_LEVEL: "INFO"
```

### 🔀 Substitutions Dynamiques

```yaml
# Dans package_build_name
package_build_name: "MonApp-${ENV}-V<version>"
# Devient : MonApp-DEV-V1.2.3

# Dans XLD paths
XLD_environment_path: "Environments/PFI/<ENV>/MonApp/"
# Devient : Environments/PFI/DEV/MonApp/
```

---

## 📊 Section 10 : Debug et Dépannage

### 🔍 Validation YAML

```bash
# Tester la syntaxe YAML
python3 -c "import yaml; yaml.safe_load(open('template.yaml'))"
```

### 📋 Checklist de Debug

1. **Syntaxe YAML** ✅
   ```bash
   # Vérifier l'indentation et la syntaxe
   yamllint template.yaml
   ```

2. **Structure obligatoire** ✅
   - [ ] Section `general_info` présente
   - [ ] Au moins un package dans `template_liste_package`
   - [ ] Section `Phases` avec phases correspondantes

3. **Cohérence des données** ✅
   - [ ] Noms de packages identiques partout
   - [ ] Phases définies et utilisées
   - [ ] Environnements XLD configurés

### 🐛 Messages d'Erreur Fréquents

#### "Package not found in jenkins configuration"
```yaml
# ❌ Problème : Package défini mais pas de job Jenkins
template_liste_package:
  MonPackage: {...}

# ✅ Solution : Ajouter le job Jenkins
jenkins:
  jenkinsjob:
    MonPackage:
      jobName: "MonJob"
```

#### "XLD path not found"
```yaml
# ❌ Problème : Chemin XLD incorrect
XLD_application_path: Applications/INEXISTANT/

# ✅ Solution : Vérifier dans XL Deploy
XLD_application_path: Applications/PFI/MONAPP/
```

#### "Phase not defined"
```yaml
# ❌ Problème : Phase manquante
general_info:
  phases: [DEV, UAT]

Phases:
  DEV: {...}
  # UAT manquant !

# ✅ Solution : Ajouter toutes les phases
Phases:
  DEV: {...}
  UAT: {...}
```

---

## 📚 Section 11 : Références

### 🔗 Liens Utiles

- **XL Release Documentation** : Documentation officielle XLR
- **XL Deploy Documentation** : Guide des chemins et applications
- **Jenkins API** : Documentation des paramètres de job
- **Control-M** : Guide des conventions de nommage

### 📞 Support

- **Équipe DevOps** : devops@company.com
- **Support XLR** : xlr-support@company.com
- **Documentation Confluence** : [Lien vers la page Confluence]

### 🏷️ Versions

| Version | Date | Changements |
|---------|------|-------------|
| 1.0 | 2024-01 | Version initiale |
| 2.0 | 2024-03 | Ajout architecture modulaire |
| 3.0 | 2024-09 | Architecture propre |

---

> **📝 Note finale**
> Cette documentation couvre tous les aspects de la configuration YAML pour le générateur XLR. Pour des cas d'usage spécifiques ou des questions, contactez l'équipe DevOps.

**🎯 Prochaines étapes :**
1. Personnaliser le fichier `template.yaml` selon vos besoins
2. Tester avec la commande `python3 DYNAMIC_template.py --infile template.yaml`
3. Valider le template généré dans XLR

---

*Document généré pour le Générateur de Templates XLR - Version 3.0*