#!/usr/bin/env python3
"""
XLR V8 Optimized - Revolutionary Template Creator

Modern, async-powered XLR template creation with advanced architecture patterns.
Same results as V1, but with cutting-edge performance and maintainability.

Features:
- Async/await throughout for maximum performance
- Modern Python patterns (dataclasses, type hints, dependency injection)
- Intelligent pipeline orchestration
- Connection pooling and batch operations
- Comprehensive error handling and monitoring
- Factory patterns and service containers
"""

import asyncio
import argparse
import logging
import sys
import yaml
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models.config import V8Config, XLRConfig, APIConfig
from src.core.pipeline import Pipeline, PipelineContext, XLRPipelineBuilder
from src.core.factory import V8ServiceContainer, service_container, TemplateStrategyFactory
from src.services.xlr_api import xlr_client
from src.processors.phase import OptimizedPhaseProcessor
from src.processors.tasks import OptimizedTaskProcessor
from src.processors.gates import OptimizedGateProcessor


class XLRCreateTemplateV8:
    """
    V8 Optimized XLR Template Creator.

    Revolutionary architecture with same V1 results but modern patterns:
    - Async pipeline orchestration
    - Dependency injection
    - Factory patterns
    - Performance optimization
    - Intelligent error handling
    """

    def __init__(self, config_file: str, debug: bool = False):
        """
        Initialize V8 template creator.

        Args:
            config_file: Path to YAML configuration file
            debug: Enable debug logging
        """
        self.config_file = config_file
        self.debug = debug
        self._setup_logging()
        self.logger = logging.getLogger(__name__)

    def _setup_logging(self) -> None:
        """Setup modern logging configuration."""
        level = logging.DEBUG if self.debug else logging.INFO

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # File handler
        file_handler = logging.FileHandler('xlr_v8.log')
        file_handler.setFormatter(formatter)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

        # Reduce noise from HTTP libraries
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
        logging.getLogger('asyncio').setLevel(logging.WARNING)

    async def create_template(self) -> str:
        """
        Create XLR template using V8 optimized pipeline.

        Returns:
            Created template ID

        Raises:
            Exception: If template creation fails
        """
        start_time = datetime.now()
        self.logger.info("🚀 Starting XLR V8 Optimized Template Creation")
        self.logger.info(f"📋 Configuration: {self.config_file}")

        try:
            # Load and validate configuration
            config = await self._load_config()

            self.logger.info(f"📝 Template: {config.xlr_config.general_info.name_release}")
            self.logger.info(f"🏢 Application: {config.xlr_config.general_info.appli_name}")
            self.logger.info(f"🔧 Phases: {len(config.xlr_config.general_info.phases)}")

            # Create pipeline context
            context = PipelineContext(config=config)

            # Build and execute pipeline
            async with service_container(config) as container:
                pipeline = await self._build_pipeline(container)
                result_context = await pipeline.execute(context)

                # Calculate performance metrics
                execution_time = (datetime.now() - start_time).total_seconds()

                self.logger.info("✅ Template creation completed successfully!")
                self.logger.info(f"⚡ Total execution time: {execution_time:.2f}s")
                self.logger.info(f"📊 Performance metrics: {result_context.metrics}")

                return result_context.template_id or "completed"

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"❌ Template creation failed after {execution_time:.2f}s: {e}")
            raise

    async def _load_config(self) -> V8Config:
        """
        Load and validate configuration from YAML file.

        Returns:
            Validated V8 configuration

        Raises:
            Exception: If configuration is invalid
        """
        self.logger.info(f"📖 Loading configuration from {self.config_file}")

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)

            # Create XLR config from YAML
            xlr_config = XLRConfig(**yaml_data)

            # Create complete V8 config
            config = V8Config(xlr_config=xlr_config)

            self.logger.info("✅ Configuration loaded and validated successfully")
            return config

        except Exception as e:
            self.logger.error(f"❌ Failed to load configuration: {e}")
            raise

    async def _build_pipeline(self, container: V8ServiceContainer) -> Pipeline:
        """
        Build the complete V8 pipeline with all optimized steps.

        Args:
            container: Service container

        Returns:
            Configured pipeline
        """
        self.logger.info("🏗️ Building V8 optimized pipeline")

        # Create pipeline builder
        builder = XLRPipelineBuilder(container.config)

        # Build pipeline with optimized step handlers
        pipeline = Pipeline(container.config)

        # Step 1: Validation
        pipeline.register_step(
            name="validate_config",
            handler=self._validate_config,
            required=True
        )

        # Step 2: Delete existing template
        pipeline.register_step(
            name="delete_existing_template",
            handler=lambda ctx: self._delete_existing_template(ctx, container),
            async_handler=True,
            dependencies=["validate_config"]
        )

        # Step 3: Find XLR folder
        pipeline.register_step(
            name="find_xlr_folder",
            handler=lambda ctx: self._find_xlr_folder(ctx, container),
            async_handler=True,
            dependencies=["validate_config"]
        )

        # Step 4: Create template
        pipeline.register_step(
            name="create_template",
            handler=lambda ctx: self._create_template_step(ctx, container),
            async_handler=True,
            dependencies=["delete_existing_template", "find_xlr_folder"]
        )

        # Step 5: Setup variables
        pipeline.register_step(
            name="setup_variables",
            handler=lambda ctx: self._setup_variables(ctx, container),
            async_handler=True,
            dependencies=["create_template"]
        )

        # Step 6: Create phases
        pipeline.register_step(
            name="create_phases",
            handler=lambda ctx: self._create_phases(ctx, container),
            async_handler=True,
            dependencies=["create_template"]
        )

        # Step 7: Create technical tasks
        pipeline.register_step(
            name="create_technical_tasks",
            handler=lambda ctx: self._create_technical_tasks(ctx, container),
            async_handler=True,
            dependencies=["create_phases"]
        )

        # Step 8: Create gates
        pipeline.register_step(
            name="create_gates",
            handler=lambda ctx: self._create_gates(ctx, container),
            async_handler=True,
            dependencies=["create_phases"]
        )

        # Step 9: Finalize template
        pipeline.register_step(
            name="finalize_template",
            handler=lambda ctx: self._finalize_template(ctx, container),
            async_handler=True,
            dependencies=["create_technical_tasks", "create_gates", "setup_variables"]
        )

        self.logger.info(f"✅ Pipeline built with {len(pipeline.steps)} optimized steps")
        return pipeline

    # Pipeline Step Handlers
    def _validate_config(self, context: PipelineContext) -> bool:
        """Validate configuration step."""
        self.logger.info("🔍 Validating configuration...")

        # Validate required fields
        config = context.config.xlr_config

        if not config.general_info.name_release:
            raise ValueError("Missing required field: name_release")

        if not config.general_info.phases:
            raise ValueError("Missing required field: phases")

        if not config.template_liste_package:
            raise ValueError("Missing required field: template_liste_package")

        self.logger.info("✅ Configuration validation passed")
        return True

    async def _delete_existing_template(self, context: PipelineContext, container: V8ServiceContainer) -> bool:
        """Delete existing template if it exists."""
        self.logger.info("🗑️ Checking for existing template...")

        config = context.config.xlr_config
        template_name = config.general_info.name_release

        async with xlr_client(container.config.api_config) as client:
            # Find existing template
            templates = await client.get_templates()

            for template in templates:
                if template.get('title') == template_name:
                    template_id = template.get('id')
                    self.logger.info(f"🗑️ Deleting existing template: {template_id}")
                    await client.delete_template(template_id)
                    self.logger.info("✅ Existing template deleted")
                    return True

        self.logger.info("ℹ️ No existing template found")
        return True

    async def _find_xlr_folder(self, context: PipelineContext, container: V8ServiceContainer) -> str:
        """Find XLR folder."""
        self.logger.info("📁 Finding XLR folder...")

        config = context.config.xlr_config
        folder_path = config.general_info.xlr_folder

        async with xlr_client(container.config.api_config) as client:
            folder_id = await client.find_folder_by_path(folder_path)

            if not folder_id:
                raise ValueError(f"XLR folder not found: {folder_path}")

            self.logger.info(f"✅ Found XLR folder: {folder_path} -> {folder_id}")
            context.variables['folder_id'] = folder_id
            return folder_id

    async def _create_template_step(self, context: PipelineContext, container: V8ServiceContainer) -> str:
        """Create base template."""
        self.logger.info("📄 Creating base template...")

        config = context.config.xlr_config

        # Use strategy pattern for template creation
        strategy_factory = TemplateStrategyFactory(container)
        strategy = strategy_factory.create_strategy(config.general_info.type_template)

        template_id = await strategy.create_template(context)

        context.template_id = template_id
        self.logger.info(f"✅ Created template: {template_id}")
        return template_id

    async def _setup_variables(self, context: PipelineContext, container: V8ServiceContainer) -> Dict[str, str]:
        """Setup template variables."""
        self.logger.info("🔧 Setting up template variables...")

        config = context.config.xlr_config

        # Build variables
        variables = {}

        # Add standard variables
        if config.variable_release:
            if config.variable_release.Date:
                variables['Date'] = '${global.Date}'
            if config.variable_release.Version:
                variables['Version'] = '${global.Version}'
            if config.variable_release.Environment:
                variables['Environment'] = '${global.Environment}'

        # Add package version variables
        for package_name in config.template_liste_package.keys():
            variables[f'{package_name}_version'] = f'${{{package_name}_version}}'

        # Set variables via API
        async with xlr_client(container.config.api_config) as client:
            await client.set_template_variables(context.template_id, variables)

        context.variables.update(variables)
        self.logger.info(f"✅ Setup {len(variables)} template variables")
        return variables

    async def _create_phases(self, context: PipelineContext, container: V8ServiceContainer) -> List[str]:
        """Create all phases."""
        self.logger.info("🏗️ Creating phases...")

        # Use optimized phase processor
        processor = OptimizedPhaseProcessor(container.config)

        async with xlr_client(container.config.api_config) as client:
            phase_ids = await processor.create_phases(context.template_id, client)

        context.variables['phase_ids'] = phase_ids
        self.logger.info(f"✅ Created {len(phase_ids)} phases")
        return phase_ids

    async def _create_technical_tasks(self, context: PipelineContext, container: V8ServiceContainer) -> List[str]:
        """Create all technical tasks."""
        self.logger.info("🔧 Creating technical tasks...")

        # Use optimized task processor
        processor = OptimizedTaskProcessor(container.config)

        async with xlr_client(container.config.api_config) as client:
            task_ids = await processor.create_technical_tasks(context.template_id, client)

        context.variables['task_ids'] = task_ids
        self.logger.info(f"✅ Created {len(task_ids)} technical tasks")
        return task_ids

    async def _create_gates(self, context: PipelineContext, container: V8ServiceContainer) -> List[str]:
        """Create all gates."""
        self.logger.info("🚪 Creating gates...")

        # Use optimized gate processor
        processor = OptimizedGateProcessor(container.config)

        async with xlr_client(container.config.api_config) as client:
            gate_ids = await processor.create_gates(context.template_id, client)

        context.variables['gate_ids'] = gate_ids
        self.logger.info(f"✅ Created {len(gate_ids)} gates")
        return gate_ids

    async def _finalize_template(self, context: PipelineContext, container: V8ServiceContainer) -> str:
        """Finalize template."""
        self.logger.info("🎯 Finalizing template...")

        # Final template update
        async with xlr_client(container.config.api_config) as client:
            template = await client.get_template(context.template_id)

            # Update template with final metadata
            template.update({
                'tags': ['V8-Optimized', 'Auto-Generated'],
                'description': f"Generated by XLR V8 Optimized on {datetime.now().isoformat()}",
                'status': 'PLANNED'
            })

            await client.update_template(context.template_id, template)

        self.logger.info("✅ Template finalized successfully")
        return context.template_id


async def main():
    """Main entry point for V8 optimized template creator."""
    parser = argparse.ArgumentParser(
        description='XLR V8 Optimized - Revolutionary Template Creator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py --infile basic_template.yaml
  python main.py --infile multi_package_template.yaml --debug
  python main.py --infile ../v5_complete/examples/example-template.yaml

Features:
  • ⚡ Async/await for maximum performance
  • 🏗️ Modern pipeline orchestration
  • 🔧 Dependency injection and factory patterns
  • 📊 Performance monitoring and metrics
  • 🛡️ Comprehensive error handling
  • 🎯 Same results as V1 with modern architecture
        '''
    )

    parser.add_argument(
        '--infile',
        required=True,
        help='Input YAML configuration file'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    # Validate input file
    if not Path(args.infile).exists():
        print(f"❌ Error: Configuration file not found: {args.infile}")
        return 1

    try:
        # Create and run V8 template creator
        creator = XLRCreateTemplateV8(args.infile, args.debug)
        template_id = await creator.create_template()

        print(f"\n🎉 SUCCESS! Template created with ID: {template_id}")
        print("🚀 XLR V8 Optimized - Revolutionary performance with V1 reliability!")
        return 0

    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))