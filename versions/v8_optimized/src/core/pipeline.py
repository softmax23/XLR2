"""
V8 Optimized Pipeline System

Modern pipeline orchestration with async support, error handling, and monitoring.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from contextlib import asynccontextmanager

from ..models.config import V8Config, XLRConfig


@dataclass
class PipelineContext:
    """Pipeline execution context."""
    config: V8Config
    template_id: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[datetime] = None

    def set_metric(self, key: str, value: Any) -> None:
        """Set a metric value."""
        self.metrics[key] = value

    def get_metric(self, key: str, default: Any = None) -> Any:
        """Get a metric value."""
        return self.metrics.get(key, default)


@dataclass
class PipelineStep:
    """Pipeline step definition."""
    name: str
    handler: Callable
    async_handler: bool = False
    required: bool = True
    timeout: Optional[float] = None
    retry_count: int = 0
    dependencies: List[str] = field(default_factory=list)


class PipelineError(Exception):
    """Pipeline execution error."""
    pass


class Pipeline:
    """
    Modern pipeline orchestrator for XLR template creation.

    Features:
    - Async/await support
    - Error handling and retries
    - Performance monitoring
    - Step dependencies
    - Context management
    """

    def __init__(self, config: V8Config):
        """
        Initialize pipeline.

        Args:
            config: V8 configuration
        """
        self.config = config
        self.steps: List[PipelineStep] = []
        self.logger = logging.getLogger(__name__)
        self._results: Dict[str, Any] = {}

    def add_step(self, step: PipelineStep) -> 'Pipeline':
        """
        Add a step to the pipeline.

        Args:
            step: Pipeline step to add

        Returns:
            Self for method chaining
        """
        self.steps.append(step)
        return self

    def register_step(
        self,
        name: str,
        handler: Callable,
        async_handler: bool = False,
        required: bool = True,
        timeout: Optional[float] = None,
        retry_count: int = 0,
        dependencies: Optional[List[str]] = None
    ) -> 'Pipeline':
        """
        Register a pipeline step.

        Args:
            name: Step name
            handler: Step handler function
            async_handler: Whether handler is async
            required: Whether step is required
            timeout: Step timeout in seconds
            retry_count: Number of retries on failure
            dependencies: List of dependency step names

        Returns:
            Self for method chaining
        """
        step = PipelineStep(
            name=name,
            handler=handler,
            async_handler=async_handler,
            required=required,
            timeout=timeout,
            retry_count=retry_count,
            dependencies=dependencies or []
        )
        return self.add_step(step)

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """
        Execute the complete pipeline.

        Args:
            context: Pipeline execution context

        Returns:
            Updated context with results

        Raises:
            PipelineError: If pipeline execution fails
        """
        context.start_time = datetime.now()
        self.logger.info(f"🚀 Starting V8 pipeline with {len(self.steps)} steps")

        try:
            # Sort steps by dependencies
            ordered_steps = self._resolve_dependencies()

            # Execute steps
            for step in ordered_steps:
                await self._execute_step(step, context)

            # Calculate execution time
            execution_time = (datetime.now() - context.start_time).total_seconds()
            context.set_metric('execution_time', execution_time)

            self.logger.info(f"✅ Pipeline completed in {execution_time:.2f}s")
            return context

        except Exception as e:
            self.logger.error(f"❌ Pipeline failed: {e}")
            raise PipelineError(f"Pipeline execution failed: {e}") from e

    async def _execute_step(self, step: PipelineStep, context: PipelineContext) -> None:
        """
        Execute a single pipeline step.

        Args:
            step: Step to execute
            context: Pipeline context
        """
        step_start = datetime.now()
        self.logger.info(f"🔄 Executing step: {step.name}")

        try:
            if step.async_handler:
                result = await self._execute_async_step(step, context)
            else:
                result = await self._execute_sync_step(step, context)

            # Store result
            self._results[step.name] = result

            # Calculate step time
            step_time = (datetime.now() - step_start).total_seconds()
            context.set_metric(f'step_{step.name}_time', step_time)

            self.logger.info(f"✅ Step {step.name} completed in {step_time:.2f}s")

        except Exception as e:
            if step.required:
                self.logger.error(f"❌ Required step {step.name} failed: {e}")
                raise
            else:
                self.logger.warning(f"⚠️ Optional step {step.name} failed: {e}")

    async def _execute_async_step(self, step: PipelineStep, context: PipelineContext) -> Any:
        """Execute async step with timeout and retries."""
        for attempt in range(step.retry_count + 1):
            try:
                if step.timeout:
                    return await asyncio.wait_for(
                        step.handler(context),
                        timeout=step.timeout
                    )
                else:
                    return await step.handler(context)
            except Exception as e:
                if attempt < step.retry_count:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.warning(f"Step {step.name} attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    raise

    async def _execute_sync_step(self, step: PipelineStep, context: PipelineContext) -> Any:
        """Execute sync step in executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, step.handler, context)

    def _resolve_dependencies(self) -> List[PipelineStep]:
        """
        Resolve step dependencies using topological sort.

        Returns:
            Steps ordered by dependencies
        """
        # Simple dependency resolution
        ordered = []
        remaining = self.steps.copy()

        while remaining:
            # Find steps with no unresolved dependencies
            ready = []
            for step in remaining:
                deps_satisfied = all(
                    any(s.name == dep for s in ordered)
                    for dep in step.dependencies
                )
                if deps_satisfied:
                    ready.append(step)

            if not ready:
                # Circular dependency
                remaining_names = [s.name for s in remaining]
                raise PipelineError(f"Circular dependency detected in steps: {remaining_names}")

            # Add ready steps to ordered list
            for step in ready:
                ordered.append(step)
                remaining.remove(step)

        return ordered

    def get_result(self, step_name: str) -> Any:
        """Get result from a specific step."""
        return self._results.get(step_name)


class XLRPipelineBuilder:
    """Builder for XLR-specific pipeline."""

    def __init__(self, config: V8Config):
        """Initialize builder with config."""
        self.config = config
        self.pipeline = Pipeline(config)

    def build_standard_pipeline(self) -> Pipeline:
        """
        Build standard XLR template creation pipeline.

        Returns:
            Configured pipeline
        """
        # Step 1: Validation
        self.pipeline.register_step(
            name="validate_config",
            handler=self._validate_config,
            required=True
        )

        # Step 2: Template deletion (if exists)
        self.pipeline.register_step(
            name="delete_existing_template",
            handler=self._delete_existing_template,
            async_handler=True,
            dependencies=["validate_config"]
        )

        # Step 3: Find XLR folder
        self.pipeline.register_step(
            name="find_xlr_folder",
            handler=self._find_xlr_folder,
            async_handler=True,
            dependencies=["validate_config"]
        )

        # Step 4: Create template
        self.pipeline.register_step(
            name="create_template",
            handler=self._create_template,
            async_handler=True,
            dependencies=["delete_existing_template", "find_xlr_folder"]
        )

        # Step 5: Create phases (parallel)
        self.pipeline.register_step(
            name="create_phases",
            handler=self._create_phases,
            async_handler=True,
            dependencies=["create_template"]
        )

        # Step 6: Create technical tasks
        self.pipeline.register_step(
            name="create_technical_tasks",
            handler=self._create_technical_tasks,
            async_handler=True,
            dependencies=["create_phases"]
        )

        # Step 7: Create gates
        self.pipeline.register_step(
            name="create_gates",
            handler=self._create_gates,
            async_handler=True,
            dependencies=["create_phases"]
        )

        # Step 8: Setup variables
        self.pipeline.register_step(
            name="setup_variables",
            handler=self._setup_variables,
            async_handler=True,
            dependencies=["create_template"]
        )

        # Step 9: Finalize template
        self.pipeline.register_step(
            name="finalize_template",
            handler=self._finalize_template,
            async_handler=True,
            dependencies=["create_technical_tasks", "create_gates", "setup_variables"]
        )

        return self.pipeline

    # Placeholder step handlers (will be implemented with actual services)
    def _validate_config(self, context: PipelineContext) -> bool:
        """Validate configuration."""
        return True

    async def _delete_existing_template(self, context: PipelineContext) -> bool:
        """Delete existing template if it exists."""
        return True

    async def _find_xlr_folder(self, context: PipelineContext) -> str:
        """Find XLR folder."""
        return context.config.xlr_config.general_info.xlr_folder

    async def _create_template(self, context: PipelineContext) -> str:
        """Create base template."""
        return "template_id_placeholder"

    async def _create_phases(self, context: PipelineContext) -> List[str]:
        """Create phases."""
        return []

    async def _create_technical_tasks(self, context: PipelineContext) -> List[str]:
        """Create technical tasks."""
        return []

    async def _create_gates(self, context: PipelineContext) -> List[str]:
        """Create gates."""
        return []

    async def _setup_variables(self, context: PipelineContext) -> Dict[str, Any]:
        """Setup template variables."""
        return {}

    async def _finalize_template(self, context: PipelineContext) -> str:
        """Finalize template."""
        return context.template_id or "completed"