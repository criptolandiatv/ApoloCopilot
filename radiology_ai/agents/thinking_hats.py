"""
6 Thinking Hats Agent Architecture for Emergency Radiology AI

Each agent represents a different cognitive mode for analyzing medical images:
- WHITE: Facts and data (DICOM metadata, clinical context)
- RED: Intuition and pattern recognition
- BLACK: Critical analysis (false positives, edge cases)
- YELLOW: Benefits and confirmatory evidence
- GREEN: Alternative diagnoses and creative solutions
- BLUE: Process control and meta-analysis
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json
from datetime import datetime


class DiagnosticConfidence(Enum):
    """Confidence levels for diagnostic findings."""
    VERY_LOW = 0.2
    LOW = 0.4
    MODERATE = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95


@dataclass
class Finding:
    """Represents a single radiological finding."""
    name: str
    location: Optional[str] = None
    severity: Optional[str] = None  # mild, moderate, severe
    confidence: float = 0.5
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    icd10_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "location": self.location,
            "severity": self.severity,
            "confidence": self.confidence,
            "supporting_evidence": self.supporting_evidence,
            "contradicting_evidence": self.contradicting_evidence,
            "icd10_code": self.icd10_code
        }


@dataclass
class ClinicalContext:
    """Patient clinical context for context engineering."""
    age: Optional[int] = None
    sex: Optional[str] = None
    chief_complaint: Optional[str] = None
    mechanism_of_injury: Optional[str] = None
    vital_signs: Dict[str, Any] = field(default_factory=dict)
    relevant_history: List[str] = field(default_factory=list)
    recent_procedures: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)

    def get_context_prompt(self) -> str:
        """Generate context prompt for LMM."""
        parts = []
        if self.age:
            parts.append(f"Patient is {self.age} years old")
        if self.sex:
            parts.append(f"Sex: {self.sex}")
        if self.chief_complaint:
            parts.append(f"Chief complaint: {self.chief_complaint}")
        if self.mechanism_of_injury:
            parts.append(f"Mechanism of injury: {self.mechanism_of_injury}")
        if self.recent_procedures:
            parts.append(f"Recent procedures: {', '.join(self.recent_procedures)}")
        if self.relevant_history:
            parts.append(f"Relevant history: {', '.join(self.relevant_history)}")
        return ". ".join(parts) + "." if parts else "No clinical context provided."


@dataclass
class AgentOutput:
    """Standardized output from each thinking hat agent."""
    agent_type: str
    findings: List[Finding] = field(default_factory=list)
    hypotheses: List[str] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    reasoning: str = ""
    recommendations: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)  # urgent findings
    processing_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_type": self.agent_type,
            "findings": [f.to_dict() for f in self.findings],
            "hypotheses": self.hypotheses,
            "confidence_scores": self.confidence_scores,
            "reasoning": self.reasoning,
            "recommendations": self.recommendations,
            "flags": self.flags,
            "processing_time_ms": self.processing_time_ms
        }


class BaseThinkingHatAgent(ABC):
    """Base class for all thinking hat agents."""

    def __init__(self, model_client: Any = None):
        self.model_client = model_client
        self.agent_type = "base"

    @abstractmethod
    async def analyze(
        self,
        image_data: bytes,
        image_metadata: Dict[str, Any],
        clinical_context: ClinicalContext,
        previous_outputs: Optional[List[AgentOutput]] = None
    ) -> AgentOutput:
        """Analyze the image from this agent's perspective."""
        pass

    def _build_base_prompt(
        self,
        clinical_context: ClinicalContext,
        modality: str = "chest_xray"
    ) -> str:
        """Build base prompt with clinical context."""
        return f"""
You are analyzing a {modality} image in an emergency department setting.

CLINICAL CONTEXT:
{clinical_context.get_context_prompt()}

ANALYSIS MODE: {self.agent_type.upper()}
"""


class WhiteHatAgent(BaseThinkingHatAgent):
    """
    WHITE HAT: Facts and Information

    Focuses on:
    - DICOM metadata extraction
    - Objective image quality assessment
    - Technical parameters
    - Patient positioning
    - Prior study comparison
    """

    def __init__(self, model_client: Any = None):
        super().__init__(model_client)
        self.agent_type = "white_hat"

    async def analyze(
        self,
        image_data: bytes,
        image_metadata: Dict[str, Any],
        clinical_context: ClinicalContext,
        previous_outputs: Optional[List[AgentOutput]] = None
    ) -> AgentOutput:
        """Extract factual information from image."""
        import time
        start_time = time.time()

        findings = []

        # Extract DICOM metadata facts
        modality = image_metadata.get("Modality", "Unknown")
        study_date = image_metadata.get("StudyDate", "Unknown")
        body_part = image_metadata.get("BodyPartExamined", "Unknown")
        view_position = image_metadata.get("ViewPosition", "Unknown")

        # Technical quality assessment
        quality_findings = self._assess_technical_quality(image_metadata)
        findings.extend(quality_findings)

        # Build factual summary
        reasoning = f"""
FACTUAL ANALYSIS (White Hat):
- Modality: {modality}
- Study Date: {study_date}
- Body Part: {body_part}
- View Position: {view_position}
- Image Quality: {"Adequate" if not any(f.name == "Poor Image Quality" for f in findings) else "Suboptimal"}

Clinical Context Summary:
{clinical_context.get_context_prompt()}
"""

        processing_time = (time.time() - start_time) * 1000

        return AgentOutput(
            agent_type=self.agent_type,
            findings=findings,
            hypotheses=[],  # White hat doesn't generate hypotheses
            confidence_scores={},
            reasoning=reasoning,
            recommendations=["Review technical adequacy before interpretation"],
            flags=[],
            processing_time_ms=processing_time
        )

    def _assess_technical_quality(self, metadata: Dict[str, Any]) -> List[Finding]:
        """Assess technical quality of the image."""
        findings = []

        # Check exposure
        exposure = metadata.get("Exposure", 0)
        if exposure and (exposure < 1 or exposure > 100):
            findings.append(Finding(
                name="Suboptimal Exposure",
                severity="mild",
                confidence=0.8,
                supporting_evidence=[f"Exposure value: {exposure}"]
            ))

        # Check patient rotation (would require actual image analysis)
        # Placeholder for LMM-based assessment

        return findings


class RedHatAgent(BaseThinkingHatAgent):
    """
    RED HAT: Intuition and Pattern Recognition

    Focuses on:
    - First impression ("gestalt")
    - Pattern matching from experience
    - Subtle abnormalities
    - "Something doesn't look right" detection
    """

    def __init__(self, model_client: Any = None):
        super().__init__(model_client)
        self.agent_type = "red_hat"

    async def analyze(
        self,
        image_data: bytes,
        image_metadata: Dict[str, Any],
        clinical_context: ClinicalContext,
        previous_outputs: Optional[List[AgentOutput]] = None
    ) -> AgentOutput:
        """Generate intuitive pattern-based assessment."""
        import time
        start_time = time.time()

        # This is where LMM inference would happen
        # For now, providing structure for intuitive analysis

        prompt = self._build_intuition_prompt(clinical_context)

        # Placeholder for actual LMM call
        # response = await self.model_client.analyze_image(image_data, prompt)

        findings = []
        hypotheses = [
            "pneumothorax",
            "hemothorax",
            "pulmonary_contusion",
            "rib_fracture",
            "normal_study"
        ]

        # Initial confidence based on clinical context
        confidence_scores = self._generate_prior_probabilities(clinical_context)

        reasoning = f"""
INTUITIVE ANALYSIS (Red Hat):
Based on initial pattern recognition and clinical context:

Primary Impression: Requires detailed assessment
Gestalt: {"High concern for trauma" if clinical_context.mechanism_of_injury else "Routine evaluation"}

Initial probability estimates generated based on:
- Clinical presentation
- Mechanism of injury
- Patient demographics
"""

        processing_time = (time.time() - start_time) * 1000

        return AgentOutput(
            agent_type=self.agent_type,
            findings=findings,
            hypotheses=hypotheses,
            confidence_scores=confidence_scores,
            reasoning=reasoning,
            recommendations=["Proceed with systematic analysis"],
            flags=["TRAUMA_MECHANISM"] if clinical_context.mechanism_of_injury else [],
            processing_time_ms=processing_time
        )

    def _build_intuition_prompt(self, context: ClinicalContext) -> str:
        """Build prompt for intuitive analysis."""
        return f"""
{self._build_base_prompt(context)}

TASK: Provide your initial intuitive assessment.
Focus on:
1. Overall impression (normal vs abnormal)
2. Areas of immediate concern
3. Subtle patterns that warrant attention
4. Confidence level in initial assessment

Respond with structured findings.
"""

    def _generate_prior_probabilities(
        self,
        context: ClinicalContext
    ) -> Dict[str, float]:
        """Generate prior probabilities based on clinical context."""
        priors = {
            "pneumothorax": 0.1,
            "hemothorax": 0.05,
            "pulmonary_contusion": 0.05,
            "rib_fracture": 0.1,
            "normal_study": 0.6
        }

        # Adjust for trauma mechanism
        if context.mechanism_of_injury:
            moi_lower = context.mechanism_of_injury.lower()
            if "mva" in moi_lower or "collision" in moi_lower:
                priors["pneumothorax"] = 0.25
                priors["hemothorax"] = 0.15
                priors["pulmonary_contusion"] = 0.2
                priors["rib_fracture"] = 0.3
                priors["normal_study"] = 0.2
            elif "fall" in moi_lower:
                priors["rib_fracture"] = 0.25
                priors["pneumothorax"] = 0.15
                priors["normal_study"] = 0.4
            elif "penetrating" in moi_lower or "stab" in moi_lower or "gsw" in moi_lower:
                priors["pneumothorax"] = 0.4
                priors["hemothorax"] = 0.35
                priors["normal_study"] = 0.1

        # Adjust for recent procedures
        if context.recent_procedures:
            procedures = " ".join(context.recent_procedures).lower()
            if "cvc" in procedures or "central line" in procedures:
                priors["pneumothorax"] = max(priors["pneumothorax"], 0.2)
            if "thoracentesis" in procedures:
                priors["pneumothorax"] = max(priors["pneumothorax"], 0.15)

        return priors


class BlackHatAgent(BaseThinkingHatAgent):
    """
    BLACK HAT: Critical Judgment and Caution

    Focuses on:
    - False positive identification
    - Edge cases and mimics
    - Potential errors in analysis
    - Contradictory evidence
    - Artifact recognition
    """

    def __init__(self, model_client: Any = None):
        super().__init__(model_client)
        self.agent_type = "black_hat"

    async def analyze(
        self,
        image_data: bytes,
        image_metadata: Dict[str, Any],
        clinical_context: ClinicalContext,
        previous_outputs: Optional[List[AgentOutput]] = None
    ) -> AgentOutput:
        """Provide critical analysis and identify potential errors."""
        import time
        start_time = time.time()

        findings = []
        flags = []

        # Analyze previous outputs for potential issues
        critique = self._critique_previous_outputs(previous_outputs or [])

        # Common mimics and pitfalls
        pitfalls = self._identify_diagnostic_pitfalls(clinical_context)

        reasoning = f"""
CRITICAL ANALYSIS (Black Hat):

Potential Issues Identified:
{critique}

Diagnostic Pitfalls to Consider:
{chr(10).join(f"- {p}" for p in pitfalls)}

Recommendations:
- Consider alternative diagnoses
- Review for artifacts
- Ensure adequate clinical correlation
"""

        recommendations = [
            "Verify findings with clinical correlation",
            "Consider artifact vs true pathology",
            "Review prior studies if available"
        ]

        processing_time = (time.time() - start_time) * 1000

        return AgentOutput(
            agent_type=self.agent_type,
            findings=findings,
            hypotheses=[],
            confidence_scores={},
            reasoning=reasoning,
            recommendations=recommendations,
            flags=flags,
            processing_time_ms=processing_time
        )

    def _critique_previous_outputs(self, outputs: List[AgentOutput]) -> str:
        """Critique findings from other agents."""
        critiques = []

        for output in outputs:
            for finding in output.findings:
                if finding.confidence < 0.7:
                    critiques.append(
                        f"Low confidence finding '{finding.name}' "
                        f"({finding.confidence:.0%}) - needs verification"
                    )
                if not finding.supporting_evidence:
                    critiques.append(
                        f"Finding '{finding.name}' lacks supporting evidence"
                    )

        return "\n".join(critiques) if critiques else "No major issues identified"

    def _identify_diagnostic_pitfalls(
        self,
        context: ClinicalContext
    ) -> List[str]:
        """Identify common diagnostic pitfalls."""
        pitfalls = [
            "Skin folds mimicking pneumothorax",
            "Scapular edge simulating pneumothorax line",
            "Costophrenic angle blunting from positioning",
            "Artifact from patient movement"
        ]

        if context.recent_procedures:
            procedures = " ".join(context.recent_procedures).lower()
            if "cvc" in procedures:
                pitfalls.append("Expected post-procedure changes")

        return pitfalls


class YellowHatAgent(BaseThinkingHatAgent):
    """
    YELLOW HAT: Optimism and Benefits

    Focuses on:
    - Confirming positive diagnoses
    - Supporting evidence for findings
    - Clinical correlation that supports diagnosis
    - Best-case interpretations
    """

    def __init__(self, model_client: Any = None):
        super().__init__(model_client)
        self.agent_type = "yellow_hat"

    async def analyze(
        self,
        image_data: bytes,
        image_metadata: Dict[str, Any],
        clinical_context: ClinicalContext,
        previous_outputs: Optional[List[AgentOutput]] = None
    ) -> AgentOutput:
        """Provide supportive analysis for findings."""
        import time
        start_time = time.time()

        # Gather supporting evidence for hypotheses
        support_analysis = self._gather_supporting_evidence(
            previous_outputs or [],
            clinical_context
        )

        reasoning = f"""
SUPPORTIVE ANALYSIS (Yellow Hat):

{support_analysis}

Clinical Correlation:
{self._analyze_clinical_correlation(clinical_context)}
"""

        processing_time = (time.time() - start_time) * 1000

        return AgentOutput(
            agent_type=self.agent_type,
            findings=[],
            hypotheses=[],
            confidence_scores={},
            reasoning=reasoning,
            recommendations=["Clinical correlation supports imaging findings"],
            flags=[],
            processing_time_ms=processing_time
        )

    def _gather_supporting_evidence(
        self,
        outputs: List[AgentOutput],
        context: ClinicalContext
    ) -> str:
        """Gather evidence supporting findings."""
        evidence_lines = []

        for output in outputs:
            for finding in output.findings:
                if finding.supporting_evidence:
                    evidence_lines.append(
                        f"{finding.name}: {', '.join(finding.supporting_evidence)}"
                    )

        return "\n".join(evidence_lines) if evidence_lines else "Awaiting findings to support"

    def _analyze_clinical_correlation(self, context: ClinicalContext) -> str:
        """Analyze how clinical context supports findings."""
        correlations = []

        if context.mechanism_of_injury:
            correlations.append(
                f"Mechanism ({context.mechanism_of_injury}) consistent with thoracic trauma"
            )

        if context.chief_complaint:
            if "pain" in context.chief_complaint.lower():
                correlations.append("Patient symptoms support imaging evaluation")
            if "dyspnea" in context.chief_complaint.lower():
                correlations.append("Respiratory symptoms warrant careful lung evaluation")

        return "\n".join(correlations) if correlations else "Limited clinical correlation available"


class GreenHatAgent(BaseThinkingHatAgent):
    """
    GREEN HAT: Creativity and Alternatives

    Focuses on:
    - Differential diagnosis generation
    - Alternative interpretations
    - Novel pattern recognition
    - Unexpected findings
    """

    def __init__(self, model_client: Any = None):
        super().__init__(model_client)
        self.agent_type = "green_hat"

    async def analyze(
        self,
        image_data: bytes,
        image_metadata: Dict[str, Any],
        clinical_context: ClinicalContext,
        previous_outputs: Optional[List[AgentOutput]] = None
    ) -> AgentOutput:
        """Generate alternative diagnoses and interpretations."""
        import time
        start_time = time.time()

        # Generate differential diagnoses
        differentials = self._generate_differentials(
            previous_outputs or [],
            clinical_context
        )

        reasoning = f"""
ALTERNATIVE ANALYSIS (Green Hat):

Differential Diagnoses to Consider:
{chr(10).join(f"{i+1}. {d}" for i, d in enumerate(differentials))}

Alternative Interpretations:
- Consider atypical presentations
- Evaluate for incidental findings
- Consider combination of pathologies
"""

        processing_time = (time.time() - start_time) * 1000

        return AgentOutput(
            agent_type=self.agent_type,
            findings=[],
            hypotheses=differentials,
            confidence_scores={d: 0.3 for d in differentials},  # Lower confidence for alternatives
            reasoning=reasoning,
            recommendations=["Consider alternative diagnoses if primary findings don't correlate"],
            flags=[],
            processing_time_ms=processing_time
        )

    def _generate_differentials(
        self,
        outputs: List[AgentOutput],
        context: ClinicalContext
    ) -> List[str]:
        """Generate differential diagnoses."""
        # Base differentials for chest trauma
        differentials = [
            "Tension pneumothorax",
            "Simple pneumothorax",
            "Hemothorax",
            "Pulmonary contusion",
            "Rib fractures (multiple)",
            "Flail chest",
            "Cardiac contusion",
            "Aortic injury",
            "Diaphragmatic rupture",
            "Tracheobronchial injury"
        ]

        # Add ICU-specific differentials if relevant
        if context.recent_procedures:
            procedures = " ".join(context.recent_procedures).lower()
            if "ngt" in procedures or "sne" in procedures:
                differentials.insert(0, "NGT malposition")
            if "ett" in procedures or "intubation" in procedures:
                differentials.insert(0, "ETT malposition")
            if "cvc" in procedures:
                differentials.insert(0, "Iatrogenic pneumothorax")
                differentials.insert(1, "CVC malposition")

        return differentials[:8]  # Return top 8


class BlueHatAgent(BaseThinkingHatAgent):
    """
    BLUE HAT: Process Control and Meta-Analysis

    Focuses on:
    - Orchestrating the analysis process
    - Synthesizing outputs from all agents
    - Ensuring systematic coverage
    - Quality control
    - Final recommendations
    """

    def __init__(self, model_client: Any = None):
        super().__init__(model_client)
        self.agent_type = "blue_hat"

    async def analyze(
        self,
        image_data: bytes,
        image_metadata: Dict[str, Any],
        clinical_context: ClinicalContext,
        previous_outputs: Optional[List[AgentOutput]] = None
    ) -> AgentOutput:
        """Synthesize all agent outputs and provide process control."""
        import time
        start_time = time.time()

        outputs = previous_outputs or []

        # Synthesize all findings
        synthesis = self._synthesize_outputs(outputs)

        # Generate final recommendations
        recommendations = self._generate_final_recommendations(outputs, clinical_context)

        # Identify urgent flags
        flags = self._identify_urgent_flags(outputs)

        reasoning = f"""
META-ANALYSIS (Blue Hat):

Process Summary:
- {len(outputs)} agent analyses completed
- Total findings: {sum(len(o.findings) for o in outputs)}
- Total hypotheses considered: {sum(len(o.hypotheses) for o in outputs)}

Synthesis:
{synthesis}

Quality Metrics:
- Analysis completeness: {self._calculate_completeness(outputs):.0%}
- Consensus level: {self._calculate_consensus(outputs):.0%}
"""

        processing_time = (time.time() - start_time) * 1000

        return AgentOutput(
            agent_type=self.agent_type,
            findings=[],  # Blue hat synthesizes, doesn't add new findings
            hypotheses=[],
            confidence_scores={},
            reasoning=reasoning,
            recommendations=recommendations,
            flags=flags,
            processing_time_ms=processing_time
        )

    def _synthesize_outputs(self, outputs: List[AgentOutput]) -> str:
        """Synthesize outputs from all agents."""
        if not outputs:
            return "No agent outputs to synthesize"

        lines = []
        for output in outputs:
            lines.append(f"- {output.agent_type}: {len(output.findings)} findings, "
                        f"{len(output.hypotheses)} hypotheses")

        return "\n".join(lines)

    def _generate_final_recommendations(
        self,
        outputs: List[AgentOutput],
        context: ClinicalContext
    ) -> List[str]:
        """Generate final recommendations."""
        recommendations = [
            "Complete systematic review of all lung fields",
            "Evaluate mediastinal contour",
            "Assess cardiac silhouette",
            "Review costophrenic angles",
            "Check tube/line positions if present"
        ]

        # Add urgency recommendations based on context
        if context.mechanism_of_injury:
            recommendations.insert(0, "PRIORITY: Evaluate for traumatic injury")

        return recommendations

    def _identify_urgent_flags(self, outputs: List[AgentOutput]) -> List[str]:
        """Identify urgent findings requiring immediate attention."""
        flags = []
        for output in outputs:
            flags.extend(output.flags)
        return list(set(flags))

    def _calculate_completeness(self, outputs: List[AgentOutput]) -> float:
        """Calculate analysis completeness score."""
        if not outputs:
            return 0.0

        expected_agents = {"white_hat", "red_hat", "black_hat",
                         "yellow_hat", "green_hat", "blue_hat"}
        present_agents = {o.agent_type for o in outputs}

        return len(present_agents) / len(expected_agents)

    def _calculate_consensus(self, outputs: List[AgentOutput]) -> float:
        """Calculate consensus level among agents."""
        if not outputs:
            return 0.0

        # Simple consensus based on hypothesis overlap
        all_hypotheses = []
        for output in outputs:
            all_hypotheses.extend(output.hypotheses)

        if not all_hypotheses:
            return 1.0  # No disagreement if no hypotheses

        from collections import Counter
        hypothesis_counts = Counter(all_hypotheses)

        if not hypothesis_counts:
            return 1.0

        # Consensus is high if few hypotheses are repeated across agents
        max_count = max(hypothesis_counts.values())
        total_unique = len(hypothesis_counts)

        return max_count / (total_unique + 1)
