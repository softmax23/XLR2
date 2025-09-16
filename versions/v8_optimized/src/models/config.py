"""
V8 Optimized Configuration Models

Modern data models with Pydantic validation for type safety and performance.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class TemplateType(str, Enum):
    """Template type enumeration."""
    DYNAMIC = "DYNAMIC"
    STATIC = "STATIC"


class PhaseMode(str, Enum):
    """Phase mode enumeration."""
    ONE_LIST = "one_list"
    MULTI_LIST = "multi_list"


class ControlMMode(str, Enum):
    """Control-M mode enumeration."""
    MASTER = "master"
    INDEPENDENT = "Independant"  # Keep original spelling for compatibility


class PackageMode(str, Enum):
    """Package mode enumeration."""
    CHECK_XLD = "CHECK_XLD"
    NAME_FROM_JENKINS = "name_from_jenkins"


class GeneralInfo(BaseModel):
    """General information configuration."""
    type_template: TemplateType
    xlr_folder: str
    iua: str
    appli_name: str
    phases: List[str]
    name_release: str
    SUN_approuver: str
    technical_task_mode: str = "string"
    template_package_mode: str = "string"
    phase_mode: PhaseMode = PhaseMode.MULTI_LIST
    xld_group: bool = True

    @validator('phases')
    def validate_phases(cls, v):
        """Validate phases are in correct order and valid."""
        valid_phases = ['BUILD', 'DEV', 'UAT', 'BENCH', 'PRODUCTION']
        for phase in v:
            if phase not in valid_phases:
                raise ValueError(f"Invalid phase: {phase}")
        return v


class PackageConfig(BaseModel):
    """Package configuration model."""
    package_build_name: str
    controlm_mode: ControlMMode = ControlMMode.MASTER
    XLD_application_path: str
    XLD_environment_path: str
    auto_undeploy: bool = False
    mode: PackageMode = PackageMode.CHECK_XLD


class JenkinsJobConfig(BaseModel):
    """Jenkins job configuration."""
    jobName: str
    parameters: List[str] = []
    precondition: str = "None"


class JenkinsConfig(BaseModel):
    """Jenkins configuration model."""
    jenkinsServer: str
    taskType: str = "jenkins.Build"
    username: str
    apiToken: str
    jenkinsjob: Dict[str, JenkinsJobConfig]


class TechnicalTaskList(BaseModel):
    """Technical task list configuration."""
    before_deployment: List[str] = []
    before_xldeploy: List[str] = []
    after_xldeploy: List[str] = []
    after_deployment: List[str] = []


class VariableRelease(BaseModel):
    """Release variables configuration."""
    Date: bool = True
    Version: bool = True
    Environment: bool = True


class XLRConfig(BaseModel):
    """Complete XLR configuration model."""
    general_info: GeneralInfo
    technical_task_list: Optional[TechnicalTaskList] = None
    template_liste_package: Dict[str, PackageConfig]
    jenkins: Optional[JenkinsConfig] = None
    variable_release: Optional[VariableRelease] = None
    Phases: Dict[str, List[Dict[str, Any]]]

    # Environment configurations
    XLD_ENV_DEV: Optional[List[str]] = None
    XLD_ENV_UAT: Optional[List[str]] = None
    XLD_ENV_BENCH: Optional[List[str]] = None
    XLD_ENV_PRODUCTION: Optional[List[str]] = None

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        extra = "allow"  # Allow additional fields for flexibility


class APIConfig(BaseModel):
    """API configuration for XLR connection."""
    url_api_xlr: str = "https://xlr-server/api/v1/"
    ops_username_api: str = "admin"
    ops_password_api: str = "admin"
    xlr_base_url: str = "https://xlr-server/"
    timeout: int = 30
    verify_ssl: bool = False
    max_retries: int = 3
    retry_delay: float = 1.0
    connection_pool_size: int = 10

    class Config:
        """Pydantic configuration."""
        env_prefix = "XLR_"  # Allow environment variable override


class PerformanceConfig(BaseModel):
    """Performance and optimization settings."""
    enable_async: bool = True
    batch_size: int = 10
    parallel_tasks: int = 5
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes
    enable_compression: bool = True


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_file_logging: bool = True
    log_file: str = "xlr_v8.log"
    max_log_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


class V8Config(BaseModel):
    """Complete V8 configuration model."""
    xlr_config: XLRConfig
    api_config: APIConfig = APIConfig()
    performance_config: PerformanceConfig = PerformanceConfig()
    logging_config: LoggingConfig = LoggingConfig()

    class Config:
        """Pydantic configuration."""
        extra = "allow"