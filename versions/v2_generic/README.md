# Version 2 - Generic (Modular Structure)

## Description
Generic version of the XLR Dynamic Template with all application-specific references removed and modular file structure. This version provides a clean, reusable template for any application deployment pipeline with improved code organization.

## Changes from V1
- **Removed Y88/LoanIQ references**: All application-specific naming has been replaced with generic terms
- **Generic naming scheme**:
  - `Y88` → `APPCODE`
  - `LoanIQ` → `Application`
  - `NXY88` → `NXAPPCODE`
- **Cleaner configuration**: Template.yaml uses generic application paths and names
- **Improved comments**: Code comments translated to English and clarified

## Files
- `DYNAMIC_template.py` - Main template generation script (cleaned)
- `all_class.py` - All classes in single file (5792 lines, generalized)
- `xlr_classes/` - Modular structure with separate files for each class:
  - `xlr_generic.py` - Core XLR operations (2,463 lines)
  - `xlr_controlm.py` - Control-M integration (1,524 lines)
  - `xlr_dynamic_phase.py` - Dynamic phase management (1,437 lines)
  - `xlr_sun.py` - ServiceNow workflows (501 lines)
  - `xlr_task_script.py` - Script generation
  - `__init__.py` - Module exports
- `template.yaml` - Generic configuration template
- `README.md` - This documentation

## Usage
```bash
python3 DYNAMIC_template.py --infile template.yaml
```

## Configuration
Before using, customize the template.yaml file:
1. Replace `APPCODE` with your application code
2. Replace `Application` with your application name
3. Update XLD paths to match your environment structure
4. Configure Jenkins job names and parameters
5. Set appropriate email addresses for notifications
6. Adjust Control-M folder names for your environment

## Key Configuration Points

### Application Identification
```yaml
general_info:
    iua: NXAPPCODE                    # Replace with your IUA
    appli_name: Application           # Replace with app name
    name_release: "NXAPPCODE_ALL_PACKAGE_GENERIC"
```

### XLD Paths
All XLD paths use the pattern:
- Applications: `Applications/PFI/APPCODE_APPLICATION/...`
- Environments: `Environments/PFI/APPCODE_APPLICATION/...`

### Jenkins Configuration
```yaml
jenkins:
    jenkinsServer: Configuration/Custom/Jenkins-APPCODE
    username: apnxappcodep_jenkins@company.com
```

### Email Notifications
Update email addresses in the `email_end_release` section to match your team distribution lists.

## Deployment Phases Supported
- **DEV**: Development environment deployment
- **UAT**: User Acceptance Testing environment
- **BENCH**: Pre-production testing environment
- **PRODUCTION**: Production environment with approval workflows

## Package Types
- **Interfaces**: Interface layer components
- **Scripts**: Database and configuration scripts
- **SDK**: Software Development Kit components
- **App**: Main application deployment
- **DICTIONNAIRE**: Dictionary/configuration data
- **Interface_external**: External interface components

## Architecture Notes

### Modular Structure Benefits
- ✅ Organized code with separate responsibilities
- ✅ Easier to locate and modify specific functionality
- ✅ Better file organization compared to monolithic V1

### Limitations
- ❌ Circular dependencies cause VS Code import highlighting issues
- ❌ Complex composition patterns in xlr_controlm.py line 60
- ⚠️ Consider upgrading to V3 for clean architecture without circular dependencies

### VS Code Import Issues
The modular structure introduces circular dependencies that cause VS Code to highlight `XLRGeneric()` in xlr_controlm.py. This is a known architectural issue resolved in V3.

## Migration to V3
For new projects or to resolve VS Code import issues, consider using V3 Clean Architecture which provides:
- ✅ Same functionality as V2
- ✅ No circular dependencies
- ✅ Clean inheritance hierarchy
- ✅ Better maintainability

## Status
🟡 **Modular Version** - Functional but has architectural limitations resolved in V3