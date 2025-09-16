"""
V8 Optimized Gate Processor

Modern gate processing with async support and intelligent validation.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..models.config import V8Config
from ..services.xlr_api import AsyncXLRClient


@dataclass
class GateDefinition:
    """Gate definition with metadata."""
    name: str
    gate_type: str
    phase: str
    conditions: List[Dict[str, Any]]
    dependencies: List[str]


class GateProcessor(ABC):
    """Base gate processor interface."""

    @abstractmethod
    async def create_gates(self, template_id: str, xlr_client: AsyncXLRClient) -> List[str]:
        """Create all gates for template."""
        pass

    @abstractmethod
    async def create_gate(self, template_id: str, gate_def: GateDefinition, xlr_client: AsyncXLRClient) -> str:
        """Create individual gate."""
        pass


class StandardGateProcessor(GateProcessor):
    """
    Standard gate processor for XLR templates.

    Creates gates for:
    - Phase transitions
    - Production approvals
    - ServiceNow/SUN integration
    - Quality gates
    """

    def __init__(self, config: V8Config):
        """
        Initialize gate processor.

        Args:
            config: V8 configuration
        """
        self.config = config
        self.xlr_config = config.xlr_config
        self.logger = logging.getLogger(__name__)

    async def create_gates(self, template_id: str, xlr_client: AsyncXLRClient) -> List[str]:
        """
        Create all gates for the template.

        Args:
            template_id: Template ID
            xlr_client: XLR API client

        Returns:
            List of created gate IDs
        """
        phases = self.xlr_config.general_info.phases
        self.logger.info(f"🚪 Creating gates for {len(phases)} phases")

        # Build gate definitions
        gate_definitions = await self._build_gate_definitions(template_id, xlr_client)

        if not gate_definitions:
            self.logger.info("No gates to create")
            return []

        # Create gates in parallel
        gate_tasks = [
            self.create_gate(template_id, gate_def, xlr_client)
            for gate_def in gate_definitions
        ]

        gate_ids = await asyncio.gather(*gate_tasks, return_exceptions=True)

        # Process results
        successful_gates = []
        for i, result in enumerate(gate_ids):
            if isinstance(result, Exception):
                self.logger.error(f"❌ Failed to create gate {gate_definitions[i].name}: {result}")
            else:
                successful_gates.append(result)

        self.logger.info(f"✅ Created {len(successful_gates)}/{len(gate_definitions)} gates")
        return successful_gates

    async def _build_gate_definitions(self, template_id: str, xlr_client: AsyncXLRClient) -> List[GateDefinition]:
        """
        Build gate definitions based on configuration.

        Args:
            template_id: Template ID
            xlr_client: XLR API client

        Returns:
            List of gate definitions
        """
        gate_definitions = []
        phases = self.xlr_config.general_info.phases

        # Get template phases to get phase IDs
        template_phases = await xlr_client.get_phases(template_id)
        phase_map = {phase['title']: phase['id'] for phase in template_phases}

        for i, phase in enumerate(phases):
            if phase not in phase_map:
                continue

            # Create phase entry gate
            if i > 0:  # Not the first phase
                entry_gate = self._create_phase_entry_gate(phase, phases[i-1])
                gate_definitions.append(entry_gate)

            # Create production gates for PRODUCTION phase
            if phase == "PRODUCTION":
                prod_gates = self._create_production_gates(phase)
                gate_definitions.extend(prod_gates)

            # Create SUN/ServiceNow gates
            if phase in ["BENCH", "PRODUCTION"]:
                sun_gate = self._create_sun_gate(phase)
                if sun_gate:
                    gate_definitions.append(sun_gate)

            # Create quality gates for UAT and BENCH
            if phase in ["UAT", "BENCH"]:
                quality_gate = self._create_quality_gate(phase)
                gate_definitions.append(quality_gate)

        return gate_definitions

    def _create_phase_entry_gate(self, current_phase: str, previous_phase: str) -> GateDefinition:
        """Create phase entry gate."""
        return GateDefinition(
            name=f"Enter {current_phase}",
            gate_type="xlrelease.Gate",
            phase=current_phase,
            conditions=[
                {
                    "type": "xlrelease.PhaseCompleteCondition",
                    "phase": previous_phase
                }
            ],
            dependencies=[previous_phase]
        )

    def _create_production_gates(self, phase: str) -> List[GateDefinition]:
        """Create production-specific gates."""
        gates = []

        # Pre-production approval gate
        approval_gate = GateDefinition(
            name="Production Approval",
            gate_type="xlrelease.Gate",
            phase=phase,
            conditions=[
                {
                    "type": "xlrelease.UserInputCondition",
                    "title": "Production Deployment Approval",
                    "description": "Approve production deployment",
                    "variables": [
                        {
                            "key": "production_approved",
                            "type": "boolean",
                            "required": True
                        }
                    ]
                }
            ],
            dependencies=[]
        )
        gates.append(approval_gate)

        # Change management gate
        change_gate = GateDefinition(
            name="Change Management",
            gate_type="xlrelease.Gate",
            phase=phase,
            conditions=[
                {
                    "type": "xlrelease.VariableCondition",
                    "variable": "change_ticket_approved",
                    "operator": "eq",
                    "value": "true"
                }
            ],
            dependencies=["production_approved"]
        )
        gates.append(change_gate)

        return gates

    def _create_sun_gate(self, phase: str) -> Optional[GateDefinition]:
        """Create SUN/ServiceNow integration gate."""
        if not self.xlr_config.general_info.SUN_approuver:
            return None

        return GateDefinition(
            name=f"SUN Approval - {phase}",
            gate_type="xlrelease.Gate",
            phase=phase,
            conditions=[
                {
                    "type": "servicenow.CheckIncidentState",
                    "server": "ServiceNow Server",
                    "ticket": "${sun_ticket_number}",
                    "expectedState": "Approved"
                }
            ],
            dependencies=[]
        )

    def _create_quality_gate(self, phase: str) -> GateDefinition:
        """Create quality gate for testing phases."""
        conditions = [
            {
                "type": "xlrelease.VariableCondition",
                "variable": f"{phase.lower()}_tests_passed",
                "operator": "eq",
                "value": "true"
            }
        ]

        # Add additional conditions for BENCH phase
        if phase == "BENCH":
            conditions.extend([
                {
                    "type": "xlrelease.VariableCondition",
                    "variable": "performance_baseline_met",
                    "operator": "eq",
                    "value": "true"
                },
                {
                    "type": "xlrelease.VariableCondition",
                    "variable": "security_scan_passed",
                    "operator": "eq",
                    "value": "true"
                }
            ])

        return GateDefinition(
            name=f"Quality Gate - {phase}",
            gate_type="xlrelease.Gate",
            phase=phase,
            conditions=conditions,
            dependencies=[]
        )

    async def create_gate(self, template_id: str, gate_def: GateDefinition, xlr_client: AsyncXLRClient) -> str:
        """
        Create individual gate.

        Args:
            template_id: Template ID
            gate_def: Gate definition
            xlr_client: XLR API client

        Returns:
            Created gate ID
        """
        self.logger.debug(f"🚪 Creating gate: {gate_def.name}")

        # Build gate data
        gate_data = await self._build_gate_data(gate_def)

        # Create gate
        gate_id = await xlr_client.create_gate(template_id, gate_data)

        self.logger.debug(f"✅ Created gate {gate_def.name}: {gate_id}")
        return gate_id

    async def _build_gate_data(self, gate_def: GateDefinition) -> Dict[str, Any]:
        """
        Build gate data configuration.

        Args:
            gate_def: Gate definition

        Returns:
            Gate configuration data
        """
        gate_data = {
            "title": gate_def.name,
            "type": gate_def.gate_type,
            "conditions": gate_def.conditions,
            "phase": gate_def.phase
        }

        # Add gate-specific properties
        if "Approval" in gate_def.name:
            gate_data.update({
                "owner": "${approver}",
                "description": f"Approval gate for {gate_def.phase} phase"
            })
        elif "Quality" in gate_def.name:
            gate_data.update({
                "description": f"Quality assurance gate for {gate_def.phase} phase",
                "automated": True
            })
        elif "SUN" in gate_def.name:
            gate_data.update({
                "description": f"ServiceNow integration gate for {gate_def.phase} phase",
                "automated": True
            })

        return gate_data


class OptimizedGateProcessor(StandardGateProcessor):
    """
    Optimized gate processor with advanced features.

    Additional optimizations:
    - Gate dependency resolution
    - Conditional gate creation
    - Performance monitoring
    - Error recovery
    """

    def __init__(self, config: V8Config):
        """Initialize optimized processor."""
        super().__init__(config)
        self._gate_cache: Dict[str, GateDefinition] = {}

    async def create_gates(self, template_id: str, xlr_client: AsyncXLRClient) -> List[str]:
        """Create gates with advanced optimizations."""
        # Build comprehensive gate definitions
        gate_definitions = await self._build_gate_definitions(template_id, xlr_client)

        # Optimize gate creation order
        ordered_gates = self._optimize_gate_order(gate_definitions)

        # Create gates in optimized batches
        gate_ids = await self._create_gates_in_batches(template_id, ordered_gates, xlr_client)

        return gate_ids

    def _optimize_gate_order(self, gate_definitions: List[GateDefinition]) -> List[GateDefinition]:
        """Optimize gate creation order based on dependencies."""
        ordered_gates = []
        remaining_gates = gate_definitions.copy()

        while remaining_gates:
            # Find gates with satisfied dependencies
            ready_gates = []
            for gate in remaining_gates:
                deps_satisfied = all(
                    any(og.name == dep for og in ordered_gates)
                    for dep in gate.dependencies
                )
                if deps_satisfied:
                    ready_gates.append(gate)

            if not ready_gates:
                # No gates ready, add remaining gates (break dependency cycle)
                ready_gates = remaining_gates[:1]

            # Add ready gates to ordered list
            for gate in ready_gates:
                ordered_gates.append(gate)
                remaining_gates.remove(gate)

        return ordered_gates

    async def _create_gates_in_batches(
        self,
        template_id: str,
        gate_definitions: List[GateDefinition],
        xlr_client: AsyncXLRClient
    ) -> List[str]:
        """Create gates in optimized batches."""
        all_gate_ids = []
        batch_size = 3  # Conservative batch size for gates

        for i in range(0, len(gate_definitions), batch_size):
            batch = gate_definitions[i:i + batch_size]

            # Create batch of gates
            batch_tasks = [
                self.create_gate(template_id, gate_def, xlr_client)
                for gate_def in batch
            ]

            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Process batch results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Failed to create gate {batch[j].name}: {result}")
                else:
                    all_gate_ids.append(result)

            # Small delay between batches to avoid overwhelming the server
            if i + batch_size < len(gate_definitions):
                await asyncio.sleep(0.1)

        return all_gate_ids

    async def _build_gate_definitions(self, template_id: str, xlr_client: AsyncXLRClient) -> List[GateDefinition]:
        """Build comprehensive gate definitions with advanced logic."""
        gate_definitions = await super()._build_gate_definitions(template_id, xlr_client)

        # Add conditional gates based on configuration
        if self._should_create_control_m_gates():
            controlm_gates = self._create_control_m_gates()
            gate_definitions.extend(controlm_gates)

        if self._should_create_jenkins_gates():
            jenkins_gates = self._create_jenkins_gates()
            gate_definitions.extend(jenkins_gates)

        return gate_definitions

    def _should_create_control_m_gates(self) -> bool:
        """Check if Control-M gates should be created."""
        # Check if any packages have Control-M integration
        for package_config in self.xlr_config.template_liste_package.values():
            if hasattr(package_config, 'controlm_mode') and package_config.controlm_mode:
                return True
        return False

    def _should_create_jenkins_gates(self) -> bool:
        """Check if Jenkins gates should be created."""
        return self.xlr_config.jenkins is not None

    def _create_control_m_gates(self) -> List[GateDefinition]:
        """Create Control-M specific gates."""
        gates = []

        # Control-M readiness gate
        gates.append(GateDefinition(
            name="Control-M Readiness",
            gate_type="xlrelease.Gate",
            phase="PRODUCTION",
            conditions=[
                {
                    "type": "xlrelease.VariableCondition",
                    "variable": "controlm_jobs_verified",
                    "operator": "eq",
                    "value": "true"
                }
            ],
            dependencies=[]
        ))

        return gates

    def _create_jenkins_gates(self) -> List[GateDefinition]:
        """Create Jenkins specific gates."""
        gates = []

        # Build quality gate
        gates.append(GateDefinition(
            name="Build Quality Gate",
            gate_type="xlrelease.Gate",
            phase="BUILD",
            conditions=[
                {
                    "type": "jenkins.CheckBuildStatus",
                    "server": self.xlr_config.jenkins.jenkinsServer,
                    "expectedStatus": "SUCCESS"
                }
            ],
            dependencies=[]
        ))

        return gates