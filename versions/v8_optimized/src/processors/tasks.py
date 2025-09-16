"""
V8 Optimized Task Processor

Modern technical task processing with async support and intelligent categorization.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..models.config import V8Config
from ..services.xlr_api import AsyncXLRClient


@dataclass
class TaskDefinition:
    """Task definition with metadata."""
    name: str
    task_type: str
    category: str
    phase: str
    properties: Dict[str, Any]
    dependencies: List[str]


class TaskProcessor(ABC):
    """Base task processor interface."""

    @abstractmethod
    async def create_technical_tasks(self, template_id: str, xlr_client: AsyncXLRClient) -> List[str]:
        """Create all technical tasks for template."""
        pass

    @abstractmethod
    async def create_task_category(self, phase_id: str, category: str, tasks: List[str], xlr_client: AsyncXLRClient) -> List[str]:
        """Create tasks for specific category."""
        pass


class StandardTaskProcessor(TaskProcessor):
    """
    Standard technical task processor.

    Handles all 4 technical task categories:
    - before_deployment
    - before_xldeploy
    - after_xldeploy
    - after_deployment
    """

    def __init__(self, config: V8Config):
        """
        Initialize task processor.

        Args:
            config: V8 configuration
        """
        self.config = config
        self.xlr_config = config.xlr_config
        self.logger = logging.getLogger(__name__)

        # Task type mappings
        self.task_type_mapping = {
            'task_ops': 'xlrelease.ScriptTask',
            'task_dba_other': 'xlrelease.ScriptTask',
            'task_dba_factor': 'xlrelease.ScriptTask',
            'task_maintenance': 'xlrelease.ManualTask',
            'task_notification': 'xlrelease.NotificationTask',
            'task_approval': 'xlrelease.UserInputTask'
        }

    async def create_technical_tasks(self, template_id: str, xlr_client: AsyncXLRClient) -> List[str]:
        """
        Create all technical tasks for all phases.

        Args:
            template_id: Template ID
            xlr_client: XLR API client

        Returns:
            List of created task IDs
        """
        if not self.xlr_config.technical_task_list:
            self.logger.info("No technical tasks configured")
            return []

        phases = self.xlr_config.general_info.phases
        self.logger.info(f"🔧 Creating technical tasks for {len(phases)} phases")

        all_task_ids = []

        # Get template phases to get phase IDs
        template_phases = await xlr_client.get_phases(template_id)
        phase_map = {phase['title']: phase['id'] for phase in template_phases}

        # Create technical tasks for each phase
        for phase_name in phases:
            if phase_name not in phase_map:
                self.logger.warning(f"Phase {phase_name} not found in template")
                continue

            phase_id = phase_map[phase_name]
            phase_task_ids = await self._create_phase_technical_tasks(phase_id, phase_name, xlr_client)
            all_task_ids.extend(phase_task_ids)

        self.logger.info(f"✅ Created {len(all_task_ids)} technical tasks")
        return all_task_ids

    async def _create_phase_technical_tasks(self, phase_id: str, phase_name: str, xlr_client: AsyncXLRClient) -> List[str]:
        """
        Create technical tasks for a specific phase.

        Args:
            phase_id: Phase ID
            phase_name: Phase name
            xlr_client: XLR API client

        Returns:
            List of created task IDs
        """
        task_ids = []

        # Skip BUILD and development phases for production tasks
        skip_production_tasks = phase_name in ['BUILD', 'DEV', 'UAT']

        # Create tasks for each category in order
        categories = ['before_deployment', 'before_xldeploy', 'after_xldeploy', 'after_deployment']

        for category in categories:
            # Skip certain categories for certain phases
            if skip_production_tasks and category in ['before_deployment', 'after_deployment']:
                continue

            tasks = getattr(self.xlr_config.technical_task_list, category, [])
            if tasks:
                category_task_ids = await self.create_task_category(phase_id, category, tasks, xlr_client)
                task_ids.extend(category_task_ids)

        return task_ids

    async def create_task_category(self, phase_id: str, category: str, tasks: List[str], xlr_client: AsyncXLRClient) -> List[str]:
        """
        Create tasks for a specific category.

        Args:
            phase_id: Phase ID
            category: Task category
            tasks: List of task names
            xlr_client: XLR API client

        Returns:
            List of created task IDs
        """
        if not tasks:
            return []

        self.logger.debug(f"🔨 Creating {len(tasks)} {category} tasks")

        # Create tasks in parallel for performance
        task_creation_tasks = [
            self._create_technical_task(phase_id, task_name, category, xlr_client)
            for task_name in tasks
        ]

        task_ids = await asyncio.gather(*task_creation_tasks, return_exceptions=True)

        # Filter successful results
        successful_task_ids = []
        for i, result in enumerate(task_ids):
            if isinstance(result, Exception):
                self.logger.error(f"Failed to create task {tasks[i]}: {result}")
            else:
                successful_task_ids.append(result)

        self.logger.debug(f"✅ Created {len(successful_task_ids)}/{len(tasks)} {category} tasks")
        return successful_task_ids

    async def _create_technical_task(self, phase_id: str, task_name: str, category: str, xlr_client: AsyncXLRClient) -> str:
        """
        Create individual technical task.

        Args:
            phase_id: Phase ID
            task_name: Task name
            category: Task category
            xlr_client: XLR API client

        Returns:
            Created task ID
        """
        # Build task data based on type and category
        task_data = await self._build_task_data(task_name, category)

        # Create task
        task_id = await xlr_client.create_task(phase_id, task_data)

        self.logger.debug(f"✅ Created {category} task: {task_name} -> {task_id}")
        return task_id

    async def _build_task_data(self, task_name: str, category: str) -> Dict[str, Any]:
        """
        Build task data configuration.

        Args:
            task_name: Task name
            category: Task category

        Returns:
            Task configuration data
        """
        # Get task type
        task_type = self.task_type_mapping.get(task_name, 'xlrelease.ScriptTask')

        # Base task configuration
        task_data = {
            "title": self._get_task_title(task_name, category),
            "type": task_type,
            "status": "PLANNED",
            "description": self._get_task_description(task_name, category)
        }

        # Add task-specific configuration
        if task_type == 'xlrelease.ScriptTask':
            task_data.update(self._build_script_task_config(task_name, category))
        elif task_type == 'xlrelease.ManualTask':
            task_data.update(self._build_manual_task_config(task_name, category))
        elif task_type == 'xlrelease.UserInputTask':
            task_data.update(self._build_user_input_task_config(task_name, category))
        elif task_type == 'xlrelease.NotificationTask':
            task_data.update(self._build_notification_task_config(task_name, category))

        return task_data

    def _get_task_title(self, task_name: str, category: str) -> str:
        """Get formatted task title."""
        title_map = {
            'task_ops': 'Operations Task',
            'task_dba_other': 'Database Operations',
            'task_dba_factor': 'Database Factor Task',
            'task_maintenance': 'Maintenance Task',
            'task_notification': 'Notification Task',
            'task_approval': 'Approval Task'
        }

        base_title = title_map.get(task_name, task_name.replace('_', ' ').title())
        category_suffix = category.replace('_', ' ').title()

        return f"{base_title} ({category_suffix})"

    def _get_task_description(self, task_name: str, category: str) -> str:
        """Get task description."""
        descriptions = {
            'task_ops': f"Operations task to be executed {category.replace('_', ' ')}",
            'task_dba_other': f"Database operations task for {category.replace('_', ' ')}",
            'task_dba_factor': f"Database factor analysis task for {category.replace('_', ' ')}",
            'task_maintenance': f"Maintenance task for {category.replace('_', ' ')}",
            'task_notification': f"Send notification {category.replace('_', ' ')}",
            'task_approval': f"Approval required {category.replace('_', ' ')}"
        }

        return descriptions.get(task_name, f"Technical task: {task_name} ({category})")

    def _build_script_task_config(self, task_name: str, category: str) -> Dict[str, Any]:
        """Build script task configuration."""
        script_map = {
            'task_ops': '''
# Operations script
echo "Executing operations task for {category}"
echo "Task: {task_name}"
echo "Phase: ${phase}"
echo "Environment: ${environment}"
''',
            'task_dba_other': '''
# Database operations script
echo "Executing database operations for {category}"
sqlplus -s ${db_user}/${db_password}@${db_connection} << EOF
SELECT 'Database connection verified' FROM dual;
EXIT;
EOF
''',
            'task_dba_factor': '''
# Database factor analysis
echo "Executing database factor analysis for {category}"
echo "Analyzing database performance metrics..."
'''
        }

        script = script_map.get(task_name, f'echo "Executing {task_name} for {category}"')

        return {
            "script": script.format(task_name=task_name, category=category),
            "scriptType": "bash",
            "continueOnFailure": False
        }

    def _build_manual_task_config(self, task_name: str, category: str) -> Dict[str, Any]:
        """Build manual task configuration."""
        return {
            "owner": "${ops_team}",
            "instructions": f"Please complete the {task_name} for {category.replace('_', ' ')}",
            "requiresApproval": True
        }

    def _build_user_input_task_config(self, task_name: str, category: str) -> Dict[str, Any]:
        """Build user input task configuration."""
        return {
            "owner": "${approver}",
            "instructions": f"Approval required for {task_name} in {category.replace('_', ' ')} phase",
            "variables": [
                {
                    "key": "approval_status",
                    "type": "xlrelease.StringVariable",
                    "required": True,
                    "description": "Approval status (APPROVED/REJECTED)"
                }
            ]
        }

    def _build_notification_task_config(self, task_name: str, category: str) -> Dict[str, Any]:
        """Build notification task configuration."""
        return {
            "addresses": ["${notification_email}"],
            "subject": f"XLR Notification: {task_name}",
            "body": f"Notification for {task_name} in {category.replace('_', ' ')} phase\n\nTemplate: ${templateTitle}\nPhase: ${phase}\nEnvironment: ${environment}"
        }


class OptimizedTaskProcessor(StandardTaskProcessor):
    """
    Optimized task processor with advanced features.

    Additional optimizations:
    - Intelligent task grouping
    - Dependency resolution
    - Performance caching
    - Error recovery
    """

    def __init__(self, config: V8Config):
        """Initialize optimized processor."""
        super().__init__(config)
        self._task_cache: Dict[str, TaskDefinition] = {}

    async def create_technical_tasks(self, template_id: str, xlr_client: AsyncXLRClient) -> List[str]:
        """Create technical tasks with advanced optimizations."""
        # Build task dependency graph
        task_definitions = self._build_task_definitions()

        # Group tasks for optimal creation
        task_groups = self._group_tasks_optimally(task_definitions)

        # Create tasks in optimized order
        all_task_ids = []
        template_phases = await xlr_client.get_phases(template_id)
        phase_map = {phase['title']: phase['id'] for phase in template_phases}

        for group in task_groups:
            group_task_ids = await self._create_task_group_optimized(group, phase_map, xlr_client)
            all_task_ids.extend(group_task_ids)

        return all_task_ids

    def _build_task_definitions(self) -> List[TaskDefinition]:
        """Build comprehensive task definitions with dependencies."""
        task_definitions = []

        if not self.xlr_config.technical_task_list:
            return task_definitions

        phases = self.xlr_config.general_info.phases

        for phase in phases:
            # Skip certain phases for production tasks
            skip_production = phase in ['BUILD', 'DEV', 'UAT']

            categories = ['before_deployment', 'before_xldeploy', 'after_xldeploy', 'after_deployment']

            for category in categories:
                if skip_production and category in ['before_deployment', 'after_deployment']:
                    continue

                tasks = getattr(self.xlr_config.technical_task_list, category, [])

                for task_name in tasks:
                    task_def = TaskDefinition(
                        name=task_name,
                        task_type=self.task_type_mapping.get(task_name, 'xlrelease.ScriptTask'),
                        category=category,
                        phase=phase,
                        properties=self._get_task_properties(task_name, category),
                        dependencies=self._get_task_dependencies(task_name, category, phase)
                    )
                    task_definitions.append(task_def)

        return task_definitions

    def _get_task_properties(self, task_name: str, category: str) -> Dict[str, Any]:
        """Get task properties for optimization."""
        return {
            'estimated_duration': self._estimate_task_duration(task_name),
            'parallel_safe': self._is_task_parallel_safe(task_name),
            'resource_intensive': self._is_task_resource_intensive(task_name)
        }

    def _get_task_dependencies(self, task_name: str, category: str, phase: str) -> List[str]:
        """Get task dependencies."""
        dependencies = []

        # Category-based dependencies
        if category == 'before_xldeploy':
            dependencies.append('before_deployment')
        elif category == 'after_xldeploy':
            dependencies.append('before_xldeploy')
        elif category == 'after_deployment':
            dependencies.append('after_xldeploy')

        # Task-specific dependencies
        if task_name == 'task_dba_factor':
            dependencies.append('task_dba_other')

        return dependencies

    def _group_tasks_optimally(self, task_definitions: List[TaskDefinition]) -> List[List[TaskDefinition]]:
        """Group tasks for optimal parallel creation."""
        groups = []
        processed = set()

        while len(processed) < len(task_definitions):
            current_group = []

            for task_def in task_definitions:
                if task_def.name in processed:
                    continue

                # Check if dependencies are satisfied
                deps_satisfied = all(dep in processed for dep in task_def.dependencies)

                if deps_satisfied and task_def.properties.get('parallel_safe', True):
                    current_group.append(task_def)
                    processed.add(task_def.name)

            if current_group:
                groups.append(current_group)
            else:
                # Add remaining tasks to avoid infinite loop
                remaining = [td for td in task_definitions if td.name not in processed]
                if remaining:
                    groups.append(remaining[:1])  # Add one task at a time
                    processed.add(remaining[0].name)

        return groups

    async def _create_task_group_optimized(
        self,
        task_group: List[TaskDefinition],
        phase_map: Dict[str, str],
        xlr_client: AsyncXLRClient
    ) -> List[str]:
        """Create task group with optimizations."""
        # Create tasks in parallel within the group
        creation_tasks = []

        for task_def in task_group:
            if task_def.phase in phase_map:
                phase_id = phase_map[task_def.phase]
                creation_tasks.append(
                    self._create_technical_task(phase_id, task_def.name, task_def.category, xlr_client)
                )

        results = await asyncio.gather(*creation_tasks, return_exceptions=True)

        # Process results
        task_ids = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Failed to create task {task_group[i].name}: {result}")
            else:
                task_ids.append(result)

        return task_ids

    def _estimate_task_duration(self, task_name: str) -> int:
        """Estimate task duration in seconds."""
        duration_map = {
            'task_ops': 300,          # 5 minutes
            'task_dba_other': 600,    # 10 minutes
            'task_dba_factor': 900,   # 15 minutes
            'task_maintenance': 1800, # 30 minutes
            'task_notification': 30,  # 30 seconds
            'task_approval': 0        # Manual, no auto duration
        }
        return duration_map.get(task_name, 300)

    def _is_task_parallel_safe(self, task_name: str) -> bool:
        """Check if task can be created in parallel."""
        # Most tasks are parallel safe except certain database operations
        return task_name not in ['task_dba_factor']

    def _is_task_resource_intensive(self, task_name: str) -> bool:
        """Check if task is resource intensive."""
        return task_name in ['task_dba_factor', 'task_maintenance']