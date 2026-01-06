"""
Radiology Orchestrator - Main Agent Coordination System

Coordinates the 6 Thinking Hats agents and Sentinel validator
to produce accurate, validated radiology reports.

OSINT-Inspired Architecture:
- Context engineering for strategic input preparation
- Multi-agent hypothesis generation
- Error collapse for confident output
- Structured report generation
"""

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import logging

from .thinking_hats import (
    WhiteHatAgent,
    RedHatAgent,
    BlackHatAgent,
    YellowHatAgent,
    GreenHatAgent,
    BlueHatAgent,
    ClinicalContext,
    AgentOutput,
    DiagnosticConfidence
)
from .sentinel import (
    SentinelValidator,
    DiagnosticHypothesis,
    StructuredReport,
    UrgencyLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator."""
    parallel_execution: bool = True
    confidence_threshold: float = 0.90
    max_hypotheses: int = 8
    enable_learning: bool = True
    timeout_seconds: float = 30.0
    require_all_agents: bool = False


@dataclass
class AnalysisRequest:
    """Input request for radiology analysis."""
    image_data: bytes
    image_metadata: Dict[str, Any]
    clinical_context: ClinicalContext
    study_id: str
    priority: str = "routine"  # routine, urgent, stat


@dataclass
class AnalysisResult:
    """Complete result of radiology analysis."""
    study_id: str
    report: StructuredReport
    agent_outputs: Dict[str, AgentOutput]
    processing_time_ms: float
    hypothesis_timeline: List[Dict[str, Any]]
    validation_summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "study_id": self.study_id,
            "report": self.report.to_dict(),
            "agent_outputs": {k: v.to_dict() for k, v in self.agent_outputs.items()},
            "processing_time_ms": self.processing_time_ms,
            "hypothesis_timeline": self.hypothesis_timeline,
            "validation_summary": self.validation_summary
        }


class RadiologyOrchestrator:
    """
    Main orchestrator for emergency radiology AI analysis.

    Architecture:
    1. Context Engineering: Prepare optimized input for analysis
    2. Parallel Agent Execution: Run 6 Thinking Hats agents
    3. Hypothesis Aggregation: Collect and rank diagnoses
    4. Error Collapse: Sentinel validation and collapse
    5. Report Generation: Structured clinical output

    Design Philosophy (OSINT-Inspired):
    - Fast prototyping with rapid iteration
    - Error detection early and often
    - Confidence through consensus
    - Human-in-the-loop for validation
    """

    def __init__(
        self,
        config: Optional[OrchestratorConfig] = None,
        model_client: Any = None
    ):
        self.config = config or OrchestratorConfig()
        self.model_client = model_client

        # Initialize agents
        self.agents = {
            "white_hat": WhiteHatAgent(model_client),
            "red_hat": RedHatAgent(model_client),
            "black_hat": BlackHatAgent(model_client),
            "yellow_hat": YellowHatAgent(model_client),
            "green_hat": GreenHatAgent(model_client),
            "blue_hat": BlueHatAgent(model_client)
        }

        # Initialize sentinel
        self.sentinel = SentinelValidator(
            confidence_threshold=self.config.confidence_threshold
        )

        # Analysis tracking
        self.analysis_log: List[Dict[str, Any]] = []

    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Main analysis pipeline.

        Flow:
        1. Context Engineering
        2. Initial Hypothesis Generation (Red Hat)
        3. Parallel Agent Analysis
        4. Aggregation (Blue Hat)
        5. Sentinel Validation & Error Collapse
        6. Report Generation
        """
        start_time = datetime.utcnow()
        hypothesis_timeline = []

        logger.info(f"Starting analysis for study {request.study_id}")

        # Step 1: Context Engineering
        enriched_context = self._engineer_context(
            request.clinical_context,
            request.image_metadata
        )

        # Step 2: Initial Hypothesis (Red Hat first for gestalt)
        red_hat_output = await self.agents["red_hat"].analyze(
            request.image_data,
            request.image_metadata,
            enriched_context
        )

        initial_hypothesis = DiagnosticHypothesis(
            diagnosis=red_hat_output.hypotheses[0] if red_hat_output.hypotheses else "Unknown",
            confidence=max(red_hat_output.confidence_scores.values(), default=0.5)
        )

        hypothesis_timeline.append({
            "stage": "initial",
            "timestamp": datetime.utcnow().isoformat(),
            "hypothesis": initial_hypothesis.diagnosis,
            "confidence": initial_hypothesis.confidence
        })

        # Step 3: Parallel Agent Analysis
        agent_outputs = {"red_hat": red_hat_output}

        if self.config.parallel_execution:
            other_outputs = await self._run_agents_parallel(
                request,
                enriched_context,
                [red_hat_output]  # Pass red hat output for context
            )
        else:
            other_outputs = await self._run_agents_sequential(
                request,
                enriched_context,
                [red_hat_output]
            )

        agent_outputs.update(other_outputs)

        # Step 4: Blue Hat Aggregation
        all_outputs = list(agent_outputs.values())
        blue_hat_output = await self.agents["blue_hat"].analyze(
            request.image_data,
            request.image_metadata,
            enriched_context,
            all_outputs
        )
        agent_outputs["blue_hat"] = blue_hat_output

        # Step 5: Sentinel Validation & Error Collapse
        collapse_result = await self.sentinel.validate_and_collapse(
            initial_hypothesis,
            all_outputs,
            enriched_context
        )

        hypothesis_timeline.append({
            "stage": "final",
            "timestamp": datetime.utcnow().isoformat(),
            "hypothesis": collapse_result.final_diagnosis.diagnosis,
            "confidence": collapse_result.final_diagnosis.confidence,
            "collapse_summary": {
                "initial": len(collapse_result.initial_hypotheses),
                "stage1": len(collapse_result.stage1_survivors),
                "stage2": len(collapse_result.stage2_survivors)
            }
        })

        # Step 6: Report Generation
        report = await self.sentinel.generate_structured_report(
            collapse_result,
            request.image_metadata,
            enriched_context.chief_complaint or "Evaluate for acute findings",
            all_outputs
        )

        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time_ms = (end_time - start_time).total_seconds() * 1000

        # Generate validation summary
        validation_summary = self._generate_validation_summary(
            collapse_result,
            agent_outputs
        )

        logger.info(
            f"Analysis complete for {request.study_id}: "
            f"{collapse_result.final_diagnosis.diagnosis} "
            f"({collapse_result.final_diagnosis.confidence:.0%})"
        )

        return AnalysisResult(
            study_id=request.study_id,
            report=report,
            agent_outputs=agent_outputs,
            processing_time_ms=processing_time_ms,
            hypothesis_timeline=hypothesis_timeline,
            validation_summary=validation_summary
        )

    def _engineer_context(
        self,
        context: ClinicalContext,
        metadata: Dict[str, Any]
    ) -> ClinicalContext:
        """
        Context Engineering - Optimize input for analysis.

        Principles:
        - Extract relevant signals from metadata
        - Enrich clinical context
        - Normalize terminology
        - Identify high-priority indicators
        """
        enriched = ClinicalContext(
            age=context.age,
            sex=context.sex,
            chief_complaint=context.chief_complaint,
            mechanism_of_injury=context.mechanism_of_injury,
            vital_signs=context.vital_signs.copy(),
            relevant_history=context.relevant_history.copy(),
            recent_procedures=context.recent_procedures.copy(),
            medications=context.medications.copy()
        )

        # Extract from metadata
        patient_age = metadata.get("PatientAge")
        if patient_age and not enriched.age:
            try:
                # Handle DICOM age format (e.g., "045Y")
                age_str = str(patient_age).replace("Y", "").strip()
                enriched.age = int(age_str)
            except ValueError:
                pass

        patient_sex = metadata.get("PatientSex")
        if patient_sex and not enriched.sex:
            enriched.sex = "Male" if patient_sex.upper() == "M" else "Female"

        # Identify high-priority modality contexts
        modality = metadata.get("Modality", "")
        body_part = metadata.get("BodyPartExamined", "").lower()

        if body_part == "chest":
            # Add chest-specific considerations
            if "trauma" in (enriched.chief_complaint or "").lower():
                enriched.relevant_history.append("TRAUMA EVALUATION")
            if any("cvc" in p.lower() or "central" in p.lower()
                   for p in enriched.recent_procedures):
                enriched.relevant_history.append("POST-CVC EVALUATION")

        return enriched

    async def _run_agents_parallel(
        self,
        request: AnalysisRequest,
        context: ClinicalContext,
        previous_outputs: List[AgentOutput]
    ) -> Dict[str, AgentOutput]:
        """Run remaining agents in parallel."""
        agents_to_run = ["white_hat", "black_hat", "yellow_hat", "green_hat"]

        tasks = []
        for agent_name in agents_to_run:
            task = self.agents[agent_name].analyze(
                request.image_data,
                request.image_metadata,
                context,
                previous_outputs
            )
            tasks.append((agent_name, task))

        results = {}
        for agent_name, task in tasks:
            try:
                output = await asyncio.wait_for(
                    task,
                    timeout=self.config.timeout_seconds
                )
                results[agent_name] = output
            except asyncio.TimeoutError:
                logger.warning(f"Agent {agent_name} timed out")
                # Create empty output for failed agent
                results[agent_name] = AgentOutput(
                    agent_type=agent_name,
                    reasoning=f"Agent timed out after {self.config.timeout_seconds}s"
                )

        return results

    async def _run_agents_sequential(
        self,
        request: AnalysisRequest,
        context: ClinicalContext,
        previous_outputs: List[AgentOutput]
    ) -> Dict[str, AgentOutput]:
        """Run agents sequentially (for debugging or resource constraints)."""
        agents_to_run = ["white_hat", "black_hat", "yellow_hat", "green_hat"]

        results = {}
        accumulated_outputs = previous_outputs.copy()

        for agent_name in agents_to_run:
            try:
                output = await self.agents[agent_name].analyze(
                    request.image_data,
                    request.image_metadata,
                    context,
                    accumulated_outputs
                )
                results[agent_name] = output
                accumulated_outputs.append(output)
            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}")
                results[agent_name] = AgentOutput(
                    agent_type=agent_name,
                    reasoning=f"Agent failed: {str(e)}"
                )

        return results

    def _generate_validation_summary(
        self,
        collapse_result: Any,
        agent_outputs: Dict[str, AgentOutput]
    ) -> Dict[str, Any]:
        """Generate summary of validation process."""
        # Calculate agent consensus
        all_hypotheses = []
        for output in agent_outputs.values():
            all_hypotheses.extend(output.hypotheses)

        from collections import Counter
        hypothesis_counts = Counter(all_hypotheses)

        # Most common hypothesis
        most_common = hypothesis_counts.most_common(1)
        consensus_hypothesis = most_common[0][0] if most_common else "none"
        consensus_count = most_common[0][1] if most_common else 0

        return {
            "total_hypotheses_generated": len(all_hypotheses),
            "unique_hypotheses": len(hypothesis_counts),
            "consensus_hypothesis": consensus_hypothesis,
            "consensus_count": consensus_count,
            "collapse_stages": {
                "initial": len(collapse_result.initial_hypotheses),
                "stage1": len(collapse_result.stage1_survivors),
                "stage2": len(collapse_result.stage2_survivors),
                "final": 1
            },
            "final_confidence": collapse_result.final_diagnosis.confidence,
            "hypothesis_changed": (
                collapse_result.initial_hypotheses[0].diagnosis
                != collapse_result.final_diagnosis.diagnosis
                if collapse_result.initial_hypotheses else True
            ),
            "agents_completed": len(agent_outputs),
            "agents_with_findings": sum(
                1 for o in agent_outputs.values() if o.findings
            ),
            "total_processing_time_ms": sum(
                o.processing_time_ms for o in agent_outputs.values()
            )
        }

    async def submit_correction(
        self,
        result: AnalysisResult,
        corrected_diagnosis: str,
        corrected_by: str,
        correction_reason: str
    ) -> Dict[str, Any]:
        """Submit radiologist correction for learning."""
        if not self.config.enable_learning:
            return {"status": "disabled", "message": "Learning is disabled"}

        return await self.sentinel.learn_from_correction(
            result.report,
            corrected_diagnosis,
            corrected_by,
            correction_reason
        )

    def get_learning_data(self) -> List[Dict[str, Any]]:
        """Get accumulated learning data for model training."""
        return self.sentinel.get_learning_buffer()

    def export_analysis_log(self) -> str:
        """Export analysis log as JSON."""
        return json.dumps(self.analysis_log, indent=2)


# Convenience functions for quick usage

async def analyze_chest_xray(
    image_data: bytes,
    metadata: Dict[str, Any],
    clinical_info: Dict[str, Any]
) -> AnalysisResult:
    """
    Quick analysis for chest X-ray.

    Args:
        image_data: Raw image bytes
        metadata: DICOM metadata dict
        clinical_info: Dict with keys:
            - chief_complaint
            - mechanism_of_injury (optional)
            - age (optional)
            - sex (optional)
            - recent_procedures (optional list)

    Returns:
        AnalysisResult with complete report
    """
    orchestrator = RadiologyOrchestrator()

    context = ClinicalContext(
        age=clinical_info.get("age"),
        sex=clinical_info.get("sex"),
        chief_complaint=clinical_info.get("chief_complaint"),
        mechanism_of_injury=clinical_info.get("mechanism_of_injury"),
        recent_procedures=clinical_info.get("recent_procedures", [])
    )

    request = AnalysisRequest(
        image_data=image_data,
        image_metadata=metadata,
        clinical_context=context,
        study_id=metadata.get("StudyInstanceUID", "unknown")
    )

    return await orchestrator.analyze(request)


async def quick_trauma_assessment(
    image_data: bytes,
    mechanism: str,
    patient_age: Optional[int] = None
) -> str:
    """
    Quick trauma assessment returning clinical summary.

    Args:
        image_data: Raw image bytes
        mechanism: Mechanism of injury description
        patient_age: Patient age (optional)

    Returns:
        Clinical summary string
    """
    result = await analyze_chest_xray(
        image_data,
        {"Modality": "CR", "BodyPartExamined": "CHEST"},
        {
            "chief_complaint": f"Trauma - {mechanism}",
            "mechanism_of_injury": mechanism,
            "age": patient_age
        }
    )

    return result.report.to_clinical_format()
