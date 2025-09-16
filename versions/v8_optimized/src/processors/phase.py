"""
V8 Optimized Phase Processor

Modern phase processing with async support and intelligent orchestration.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

from ..models.config import V8Config
from ..services.xlr_api import AsyncXLRClient


class PhaseProcessor(ABC):
    """Base phase processor interface."""

    @abstractmethod
    async def create_phases(self, template_id: str, xlr_client: AsyncXLRClient) -> List[str]:
        """Create phases for template."""
        pass

    @abstractmethod
    async def create_phase(self, template_id: str, phase_name: str, xlr_client: AsyncXLRClient) -> str:
        """Create single phase."""
        pass


class StandardPhaseProcessor(PhaseProcessor):
    """
    Standard phase processor with optimized creation patterns.

    Features:
    - Parallel phase creation
    - Intelligent dependency management
    - Performance monitoring
    - Error resilience
    """

    def __init__(self, config: V8Config):
        """
        Initialize phase processor.

        Args:
            config: V8 configuration
        """
        self.config = config
        self.xlr_config = config.xlr_config
        self.logger = logging.getLogger(__name__)

    async def create_phases(self, template_id: str, xlr_client: AsyncXLRClient) -> List[str]:
        """
        Create all phases for template with optimal parallelization.

        Args:
            template_id: Template ID
            xlr_client: XLR API client

        Returns:
            List of created phase IDs
        """
        phases = self.xlr_config.general_info.phases
        self.logger.info(f"🏗️ Creating {len(phases)} phases for template {template_id}")

        # Create phases in parallel (they don't depend on each other structurally)
        phase_tasks = [
            self.create_phase(template_id, phase_name, xlr_client)
            for phase_name in phases
        ]

        phase_ids = await asyncio.gather(*phase_tasks, return_exceptions=True)

        # Process results
        successful_phases = []
        for i, result in enumerate(phase_ids):
            if isinstance(result, Exception):
                self.logger.error(f"❌ Failed to create phase {phases[i]}: {result}")
            else:
                successful_phases.append(result)

        self.logger.info(f"✅ Created {len(successful_phases)}/{len(phases)} phases")
        return successful_phases

    async def create_phase(self, template_id: str, phase_name: str, xlr_client: AsyncXLRClient) -> str:
        """
        Create individual phase with optimized configuration.

        Args:
            template_id: Template ID
            phase_name: Phase name
            xlr_client: XLR API client

        Returns:
            Created phase ID
        """
        self.logger.debug(f"🔨 Creating phase: {phase_name}")

        # Build phase configuration
        phase_data = await self._build_phase_data(phase_name)

        # Create phase
        phase_id = await xlr_client.create_phase(template_id, phase_data)

        # Create phase tasks if configured
        if phase_name in self.xlr_config.Phases:
            await self._create_phase_tasks(phase_id, phase_name, xlr_client)

        self.logger.debug(f"✅ Created phase {phase_name}: {phase_id}")
        return phase_id

    async def _build_phase_data(self, phase_name: str) -> Dict[str, Any]:
        """
        Build phase data configuration.

        Args:
            phase_name: Phase name

        Returns:
            Phase configuration data
        """
        # Base phase configuration
        phase_data = {
            "title": phase_name,
            "type": "xlrelease.Phase",
            "status": "PLANNED",
            "color": self._get_phase_color(phase_name),
            "tasks": []
        }

        # Add phase-specific configuration
        if phase_name == "BUILD":
            phase_data.update({
                "description": "Build and package phase",
                "automated": True
            })
        elif phase_name in ["DEV", "UAT"]:
            phase_data.update({
                "description": f"Deployment to {phase_name} environment",
                "automated": True
            })
        elif phase_name == "BENCH":
            phase_data.update({
                "description": "Benchmarking and performance testing",
                "automated": False
            })
        elif phase_name == "PRODUCTION":
            phase_data.update({
                "description": "Production deployment",
                "automated": False,
                "requiresApproval": True
            })

        return phase_data

    def _get_phase_color(self, phase_name: str) -> str:
        """Get phase color based on name."""
        color_map = {
            "BUILD": "#4CAF50",      # Green
            "DEV": "#2196F3",        # Blue
            "UAT": "#FF9800",        # Orange
            "BENCH": "#9C27B0",      # Purple
            "PRODUCTION": "#F44336"   # Red
        }
        return color_map.get(phase_name, "#607D8B")  # Default: Blue Grey

    async def _create_phase_tasks(self, phase_id: str, phase_name: str, xlr_client: AsyncXLRClient) -> None:
        """
        Create tasks for the phase.

        Args:
            phase_id: Phase ID
            phase_name: Phase name
            xlr_client: XLR API client
        """
        phase_config = self.xlr_config.Phases.get(phase_name, [])

        if not phase_config:
            self.logger.debug(f"No tasks configured for phase {phase_name}")
            return

        self.logger.debug(f"🔧 Creating {len(phase_config)} task groups for phase {phase_name}")

        # Process each task group in the phase
        for task_group in phase_config:
            await self._create_task_group(phase_id, task_group, xlr_client)

    async def _create_task_group(self, phase_id: str, task_group: Dict[str, Any], xlr_client: AsyncXLRClient) -> None:
        """
        Create a group of tasks (sequential or parallel).

        Args:
            phase_id: Phase ID
            task_group: Task group configuration
            xlr_client: XLR API client
        """
        for task_type, task_config in task_group.items():
            if task_type == "seq_xldeploy":
                await self._create_sequential_xld_tasks(phase_id, task_config, xlr_client)
            elif task_type == "par_xldeploy":
                await self._create_parallel_xld_tasks(phase_id, task_config, xlr_client)
            elif task_type == "XLR_task_controlm_tasks":
                await self._create_controlm_tasks(phase_id, task_config, xlr_client)
            else:
                self.logger.warning(f"Unknown task type: {task_type}")

    async def _create_sequential_xld_tasks(self, phase_id: str, task_config: Dict[str, List[str]], xlr_client: AsyncXLRClient) -> None:
        """Create sequential XLD deployment tasks."""
        for xld_group, packages in task_config.items():
            for package in packages:
                task_data = {
                    "title": f"Deploy {package}",
                    "type": "xldeploy.Deploy",
                    "deploymentPackage": f"{package}-${{{package}_version}}",
                    "deploymentEnvironment": self._get_environment_path(package),
                    "rollbackOnError": True
                }
                await xlr_client.create_task(phase_id, task_data)

    async def _create_parallel_xld_tasks(self, phase_id: str, task_config: Dict[str, List[str]], xlr_client: AsyncXLRClient) -> None:
        """Create parallel XLD deployment tasks."""
        # Create a parallel group
        parallel_group_data = {
            "title": "Parallel Deployments",
            "type": "xlrelease.ParallelGroup",
            "tasks": []
        }

        # Add tasks to parallel group
        for xld_group, packages in task_config.items():
            for package in packages:
                task_data = {
                    "title": f"Deploy {package}",
                    "type": "xldeploy.Deploy",
                    "deploymentPackage": f"{package}-${{{package}_version}}",
                    "deploymentEnvironment": self._get_environment_path(package),
                    "rollbackOnError": True
                }
                parallel_group_data["tasks"].append(task_data)

        await xlr_client.create_task(phase_id, parallel_group_data)

    async def _create_controlm_tasks(self, phase_id: str, controlm_tasks: List[str], xlr_client: AsyncXLRClient) -> None:
        """Create Control-M tasks."""
        for controlm_task in controlm_tasks:
            task_data = {
                "title": f"Control-M: {controlm_task}",
                "type": "controlm.RunJob",
                "jobDefinitionsPath": f"${{{controlm_task}}}",
                "ctmServer": "controlm-server",
                "waitForCompletion": True
            }
            await xlr_client.create_task(phase_id, task_data)

    def _get_environment_path(self, package: str) -> str:
        """Get environment path for package."""
        # This would normally come from package configuration
        package_config = self.xlr_config.template_liste_package.get(package)
        if package_config:
            return package_config.XLD_environment_path
        return f"Environments/Default/{package}"


class OptimizedPhaseProcessor(StandardPhaseProcessor):
    """
    Optimized phase processor with advanced features.

    Additional optimizations:
    - Intelligent batching
    - Dependency graph analysis
    - Performance caching
    - Error recovery
    """

    def __init__(self, config: V8Config):
        """Initialize optimized processor."""
        super().__init__(config)
        self._phase_cache: Dict[str, Any] = {}

    async def create_phases(self, template_id: str, xlr_client: AsyncXLRClient) -> List[str]:
        """Create phases with advanced optimizations."""
        phases = self.xlr_config.general_info.phases

        # Analyze phase dependencies
        dependency_graph = self._analyze_phase_dependencies(phases)

        # Create phases in optimal order
        phase_ids = await self._create_phases_optimized(template_id, dependency_graph, xlr_client)

        return phase_ids

    def _analyze_phase_dependencies(self, phases: List[str]) -> Dict[str, List[str]]:
        """Analyze phase dependencies for optimal creation order."""
        dependency_graph = {}

        for phase in phases:
            dependencies = []

            # Standard dependencies
            if phase == "UAT" and "DEV" in phases:
                dependencies.append("DEV")
            elif phase == "BENCH" and "UAT" in phases:
                dependencies.append("UAT")
            elif phase == "PRODUCTION":
                if "BENCH" in phases:
                    dependencies.append("BENCH")
                elif "UAT" in phases:
                    dependencies.append("UAT")

            dependency_graph[phase] = dependencies

        return dependency_graph

    async def _create_phases_optimized(self, template_id: str, dependency_graph: Dict[str, List[str]], xlr_client: AsyncXLRClient) -> List[str]:
        """Create phases in optimal order based on dependencies."""
        created_phases = {}
        remaining_phases = set(dependency_graph.keys())

        while remaining_phases:
            # Find phases with satisfied dependencies
            ready_phases = []
            for phase in remaining_phases:
                dependencies_satisfied = all(
                    dep in created_phases for dep in dependency_graph[phase]
                )
                if dependencies_satisfied:
                    ready_phases.append(phase)

            if not ready_phases:
                # No phases ready - create remaining phases in parallel
                ready_phases = list(remaining_phases)

            # Create ready phases in parallel
            phase_tasks = [
                self.create_phase(template_id, phase, xlr_client)
                for phase in ready_phases
            ]

            phase_results = await asyncio.gather(*phase_tasks, return_exceptions=True)

            # Update created phases
            for i, result in enumerate(phase_results):
                phase_name = ready_phases[i]
                if not isinstance(result, Exception):
                    created_phases[phase_name] = result
                    remaining_phases.remove(phase_name)
                else:
                    self.logger.error(f"Failed to create phase {phase_name}: {result}")

        return list(created_phases.values())