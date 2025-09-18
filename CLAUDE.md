# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an XLR (XebiaLabs Release) Dynamic Template Generator for automated deployment pipelines. The system generates XLR release templates that orchestrate deployments across multiple environments (DEV, UAT, BENCH, PRODUCTION) with integration to Jenkins, XL Deploy, Control-M, and SUN systems.

## Architecture

### Core Components
- **Template Generator**: Main orchestrator that reads YAML configuration and generates XLR templates via API calls
- **Class Hierarchy**: Multiple inheritance model combining specialized deployment handlers:
  - `XLRGeneric`: Base XLR API operations and template management
  - `XLRControlm`: Control-M job scheduling and folder management
  - `XLRDynamicPhase`: Dynamic phase creation based on configuration
  - `XLRSun`: SUN approval workflow integration
  - `XLRTaskScript`: Custom script task generation

### Key Integration Points
- **XLR API**: REST API calls to create templates, phases, tasks, and variables
- **Jenkins**: Build job triggering with parameterized builds
- **XL Deploy**: Application deployment across environments
- **Control-M**: Batch job scheduling and resource management
- **SUN**: Approval workflow system

## Version Structure

The repository contains multiple versions of the XLR template generator:

### versions/v1_original/
Legacy monolithic implementation with Y88/LoanIQ-specific references:
- `DYNAMIC_template.py`: Main entry point and orchestrator class
- `all_class.py`: Single file containing all 5792 lines of class definitions
- `template.yaml`: Y88/LoanIQ-specific configuration example
- `README.md`: Version-specific documentation

### versions/v2_generic/
Cleaned generic version suitable for any application (modular structure):
- `DYNAMIC_template.py`: Main entry point with cleaned comments and code
- `all_class.py`: Generalized class definitions (Y88 → APPCODE, LoanIQ → Application)
- `xlr_classes/`: Modular structure with separate files for each class
- `template.yaml`: Generic template configuration ready for customization
- `README.md`: Generic version documentation and customization guide

### versions/v3_clean_architecture/
Clean architecture implementation with proper inheritance hierarchy:
- `DYNAMIC_template.py`: Main orchestrator using composition and delegation
- `xlr_classes/xlr_base.py`: Foundation class with shared functionality
- `xlr_classes/`: Clean architecture classes inheriting from XLRBase
- No circular dependencies, eliminates VS Code import highlighting issues
- Same functionality as V2 but with improved maintainability and testability
- `README.md`: Clean architecture documentation and benefits

### versions/v4_enhanced_logging/
Enhanced logging and monitoring implementation (RECOMMENDED):
- `DYNAMIC_template.py`: Main orchestrator with enhanced logging capabilities
- `xlr_classes/xlr_logger.py`: Advanced logging system with JSON output
- `xlr_classes/xlr_base.py`: Foundation class with integrated enhanced logging
- Structured JSON logging for monitoring systems
- Performance timing and metrics collection
- Automatic log rotation and colored console output
- 100% backward compatibility with same log messages
- `README.md`: Enhanced logging features and monitoring integration

## Running the System

### Basic Usage

**V1 Original (Y88-specific):**
```bash
cd versions/v1_original/
python3 DYNAMIC_template.py --infile template.yaml
```

**V2 Generic (modular structure):**
```bash
cd versions/v2_generic/
python3 DYNAMIC_template.py --infile template.yaml
```

**V3 Clean Architecture:**
```bash
cd versions/v3_clean_architecture/
python3 DYNAMIC_template.py --infile template.yaml
```

**V4 Enhanced Logging (RECOMMENDED for production):**
```bash
cd versions/v4_enhanced_logging/
python3 DYNAMIC_template.py --infile template.yaml
```

### Configuration Requirements
Before running, ensure you have:
1. XLR API credentials in `_conf/xlr_create_template_change.ini`
2. Valid YAML template configuration file
3. Network access to XLR, Jenkins, and Control-M systems

## YAML Configuration Structure

The template.yaml defines:
- **general_info**: Basic release metadata (name, IUA, environments, phases)
- **technical_task_list**: Pre/post deployment technical tasks
- **XLD_ENV_***: Environment-specific XL Deploy targets
- **template_liste_package**: Package definitions with build names and XLD paths
- **jenkins**: Jenkins server configuration and job definitions
- **Phases**: Phase-specific deployment sequences and Control-M orchestration

### Package Types
- `Interfaces`: Interface layer deployments
- `Scripts`: Database and configuration scripts
- `SDK`: Software Development Kit components
- `App`: Main application deployments
- Various specialized interfaces (TOGE, MOTOR, ROAR, etc.)

## Control-M Integration

The system generates Control-M folder orders with:
- Environment-specific prefixes (BDCP_ for BENCH, PDCP_ for PRODUCTION)
- START/STOP job sequences for service management
- Resource allocation and dependency management
- Hold/release mechanisms for production deployments

## Technical Notes

### Legacy Code Characteristics
- Monolithic structure with all classes in single file
- No type hints or modern Python patterns
- Basic error handling with `sys.exit(0)`
- Mixed French/English naming conventions
- Direct API credentials in configuration files

### API Authentication
The system uses basic auth for XLR API calls and stores credentials in configuration files. Ensure proper credential management in production environments.

### Logging
Generates three log files per release:
- `CR.log`: Creation report
- `info.log`: Detailed execution information
- `error.log`: Error tracking

### Dependencies
- `requests`: HTTP API calls
- `yaml`: Configuration parsing
- `configparser`: INI file handling
- Custom logging utilities
- YAML validation utilities

## Version Comparison and Recommendations

### When to Use Each Version

**V1 Original:**
- ✅ Legacy compatibility for Y88/LoanIQ-specific deployments
- ❌ Monolithic architecture (5792 lines in single file)
- ❌ Application-specific naming and configuration

**V2 Generic:**
- ✅ Generic naming suitable for any application
- ✅ Modular file structure for better organization
- ❌ Circular dependencies cause VS Code import highlighting issues
- ❌ Complex composition patterns

**V3 Clean Architecture:**
- ✅ Eliminates all circular dependencies
- ✅ Clean inheritance hierarchy following SOLID principles
- ✅ Better testability and maintainability
- ✅ Same functionality as V1/V2 with improved architecture
- ✅ No VS Code import highlighting issues
- ✅ Easier to extend and debug

**V4 Enhanced Logging (RECOMMENDED):**
- ✅ All V3 benefits plus enhanced observability
- ✅ Structured JSON logging for monitoring systems
- ✅ Performance timing and metrics collection
- ✅ Enhanced error correlation and tracking
- ✅ Automatic log rotation and colored console output
- ✅ 100% backward compatibility with same log messages
- ✅ Real-time feedback and session summaries
- ✅ Enterprise-grade monitoring capabilities

### Migration Path
1. **V1 → V2**: Update configuration to use generic naming (APPCODE, Application)
2. **V2 → V3**: No configuration changes needed, improved architecture only
3. **V3 → V4**: No configuration changes needed, enhanced logging added
4. **V1 → V4**: Combine generic naming, clean architecture, and enhanced logging

### Architecture Evolution
- **V1**: Monolithic inheritance (single 5792-line file)
- **V2**: Modular composition with circular dependencies
- **V3**: Clean inheritance hierarchy with composition delegation
- **V4**: Clean architecture + enhanced logging and monitoring capabilities

All versions maintain 100% functional compatibility with the same XLR API output.

### V4 Enhanced Logging Features
- **Structured Logging**: JSON format for monitoring integration
- **Performance Metrics**: Timing for all operations and API calls
- **Error Correlation**: Enhanced context and stack trace information
- **Automatic Rotation**: 10MB max log files with 5 backups
- **Console Output**: Real-time colored feedback with progress
- **Session Stats**: Complete execution summaries and metrics
- **Monitoring Ready**: Compatible with log aggregation systems