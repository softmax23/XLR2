"""
V8 Optimized Factory and Dependency Injection System

Modern factory patterns with dependency injection for flexible, testable architecture.
"""

import logging
from typing import Dict, Any, Type, TypeVar, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps

from ..models.config import V8Config, APIConfig
from ..services.xlr_api import AsyncXLRClient


T = TypeVar('T')


class ServiceRegistry:
    """Service registry for dependency injection."""

    def __init__(self):
        """Initialize service registry."""
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)

    def register_service(self, name: str, service: Any) -> None:
        """Register a service instance."""
        self._services[name] = service
        self.logger.debug(f"📦 Registered service: {name}")

    def register_factory(self, name: str, factory: Callable) -> None:
        """Register a service factory."""
        self._factories[name] = factory
        self.logger.debug(f"🏭 Registered factory: {name}")

    def register_singleton(self, name: str, factory: Callable) -> None:
        """Register a singleton service."""
        self._factories[name] = factory
        self._singletons[name] = None
        self.logger.debug(f"🔒 Registered singleton: {name}")

    def get_service(self, name: str) -> Any:
        """Get service by name."""
        # Check direct services first
        if name in self._services:
            return self._services[name]

        # Check singletons
        if name in self._singletons:
            if self._singletons[name] is None:
                self._singletons[name] = self._factories[name]()
            return self._singletons[name]

        # Check factories
        if name in self._factories:
            return self._factories[name]()

        raise ValueError(f"Service '{name}' not found in registry")

    def has_service(self, name: str) -> bool:
        """Check if service exists."""
        return name in self._services or name in self._factories


# Global service registry
_registry = ServiceRegistry()


def inject(service_name: str):
    """Decorator for dependency injection."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            service = _registry.get_service(service_name)
            return func(service, *args, **kwargs)
        return wrapper
    return decorator


class ServiceFactory(ABC):
    """Base service factory."""

    @abstractmethod
    def create(self, config: V8Config) -> Any:
        """Create service instance."""
        pass


class XLRClientFactory(ServiceFactory):
    """Factory for XLR API client."""

    def create(self, config: V8Config) -> AsyncXLRClient:
        """Create XLR client."""
        return AsyncXLRClient(config.api_config)


class ProcessorFactory(ABC):
    """Base processor factory."""

    @abstractmethod
    def create_phase_processor(self, config: V8Config) -> 'PhaseProcessor':
        """Create phase processor."""
        pass

    @abstractmethod
    def create_task_processor(self, config: V8Config) -> 'TaskProcessor':
        """Create task processor."""
        pass

    @abstractmethod
    def create_gate_processor(self, config: V8Config) -> 'GateProcessor':
        """Create gate processor."""
        pass


class StandardProcessorFactory(ProcessorFactory):
    """Standard processor factory."""

    def create_phase_processor(self, config: V8Config) -> 'PhaseProcessor':
        """Create standard phase processor."""
        try:
            from ..processors.phase import StandardPhaseProcessor
            return StandardPhaseProcessor(config)
        except ImportError:
            # Fallback for circular import issues
            return None

    def create_task_processor(self, config: V8Config) -> 'TaskProcessor':
        """Create standard task processor."""
        try:
            from ..processors.tasks import StandardTaskProcessor
            return StandardTaskProcessor(config)
        except ImportError:
            # Fallback for circular import issues
            return None

    def create_gate_processor(self, config: V8Config) -> 'GateProcessor':
        """Create standard gate processor."""
        try:
            from ..processors.gates import StandardGateProcessor
            return StandardGateProcessor(config)
        except ImportError:
            # Fallback for circular import issues
            return None


@dataclass
class ComponentConfig:
    """Component configuration."""
    name: str
    factory_class: Type[ServiceFactory]
    singleton: bool = True
    config_required: bool = True


class V8ServiceContainer:
    """
    Main service container for V8 architecture.

    Manages all services, factories, and dependencies with optimized patterns.
    """

    def __init__(self, config: V8Config):
        """
        Initialize service container.

        Args:
            config: V8 configuration
        """
        self.config = config
        self.registry = _registry
        self.logger = logging.getLogger(__name__)
        self._setup_core_services()

    def _setup_core_services(self) -> None:
        """Setup core services."""
        # Register config as service
        self.registry.register_service("config", self.config)

        # Register XLR client factory
        self.registry.register_singleton(
            "xlr_client",
            lambda: XLRClientFactory().create(self.config)
        )

        # Register processor factory
        self.registry.register_singleton(
            "processor_factory",
            lambda: StandardProcessorFactory()
        )

        # Register processors
        processor_factory = StandardProcessorFactory()
        self.registry.register_factory(
            "phase_processor",
            lambda: processor_factory.create_phase_processor(self.config)
        )
        self.registry.register_factory(
            "task_processor",
            lambda: processor_factory.create_task_processor(self.config)
        )
        self.registry.register_factory(
            "gate_processor",
            lambda: processor_factory.create_gate_processor(self.config)
        )

        self.logger.info("🏗️ Core services registered")

    def get_xlr_client(self) -> AsyncXLRClient:
        """Get XLR API client."""
        return self.registry.get_service("xlr_client")

    def get_phase_processor(self) -> 'PhaseProcessor':
        """Get phase processor."""
        return self.registry.get_service("phase_processor")

    def get_task_processor(self) -> 'TaskProcessor':
        """Get task processor."""
        return self.registry.get_service("task_processor")

    def get_gate_processor(self) -> 'GateProcessor':
        """Get gate processor."""
        return self.registry.get_service("gate_processor")

    def register_custom_service(self, name: str, service: Any) -> None:
        """Register custom service."""
        self.registry.register_service(name, service)

    def register_custom_factory(self, name: str, factory: Callable) -> None:
        """Register custom factory."""
        self.registry.register_factory(name, factory)


class TemplateStrategy(ABC):
    """Base template creation strategy."""

    @abstractmethod
    async def create_template(self, context: 'PipelineContext') -> str:
        """Create template using specific strategy."""
        pass


class DynamicTemplateStrategy(TemplateStrategy):
    """Strategy for dynamic templates."""

    def __init__(self, container: V8ServiceContainer):
        """Initialize with service container."""
        self.container = container
        self.logger = logging.getLogger(__name__)

    async def create_template(self, context: 'PipelineContext') -> str:
        """Create dynamic template."""
        config = context.config.xlr_config
        xlr_client = self.container.get_xlr_client()

        template_data = {
            "title": config.general_info.name_release,
            "folderId": await xlr_client.find_folder_by_path(config.general_info.xlr_folder),
            "templateType": "TEMPLATE",
            "scheduledStartDate": None,
            "variables": {},
            "phases": []
        }

        template_id = await xlr_client.create_template(template_data)
        self.logger.info(f"📄 Created dynamic template: {template_id}")
        return template_id


class StaticTemplateStrategy(TemplateStrategy):
    """Strategy for static templates."""

    def __init__(self, container: V8ServiceContainer):
        """Initialize with service container."""
        self.container = container
        self.logger = logging.getLogger(__name__)

    async def create_template(self, context: 'PipelineContext') -> str:
        """Create static template."""
        # Implementation for static templates
        self.logger.info("📄 Creating static template")
        return "static_template_id"


class TemplateStrategyFactory:
    """Factory for template strategies."""

    def __init__(self, container: V8ServiceContainer):
        """Initialize with service container."""
        self.container = container

    def create_strategy(self, template_type: str) -> TemplateStrategy:
        """Create strategy based on template type."""
        if template_type.upper() == "DYNAMIC":
            return DynamicTemplateStrategy(self.container)
        elif template_type.upper() == "STATIC":
            return StaticTemplateStrategy(self.container)
        else:
            raise ValueError(f"Unknown template type: {template_type}")


# Context manager for service container
from contextlib import asynccontextmanager

@asynccontextmanager
async def service_container(config: V8Config):
    """Async context manager for service container."""
    container = V8ServiceContainer(config)
    try:
        yield container
    finally:
        # Cleanup if needed
        pass