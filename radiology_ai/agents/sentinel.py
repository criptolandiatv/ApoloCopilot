"""
Sentinel AI Validator - "Dumb" Learning System

The Sentinel is intentionally simple and focused on:
1. Comparing initial hypothesis vs final conclusion
2. Error collapse: 8 scenarios -> 2 -> 1
3. Learning from radiologist corrections
4. Generating structured reports
5. Confidence calibration

Design principle: "Dumb" but rigorous - catches what complex systems miss
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
from datetime import datetime
import hashlib


class UrgencyLevel(Enum):
    """Report urgency classification."""
    ROUTINE = "routine"
    PRIORITY = "priority"
    URGENT = "urgent"
    CRITICAL = "critical"


class ReportStatus(Enum):
    """Report workflow status."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    REVIEWED = "reviewed"
    SIGNED = "signed"
    AMENDED = "amended"


@dataclass
class DiagnosticHypothesis:
    """Single diagnostic hypothesis with metadata."""
    diagnosis: str
    icd10_code: Optional[str] = None
    confidence: float = 0.5
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    collapsed: bool = False  # True if eliminated by error collapse
    collapse_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "diagnosis": self.diagnosis,
            "icd10_code": self.icd10_code,
            "confidence": self.confidence,
            "supporting_evidence": self.supporting_evidence,
            "contradicting_evidence": self.contradicting_evidence,
            "collapsed": self.collapsed,
            "collapse_reason": self.collapse_reason
        }


@dataclass
class ErrorCollapseResult:
    """Result of error collapse process."""
    initial_hypotheses: List[DiagnosticHypothesis]
    stage1_survivors: List[DiagnosticHypothesis]  # After first collapse
    stage2_survivors: List[DiagnosticHypothesis]  # After second collapse
    final_diagnosis: DiagnosticHypothesis
    collapse_log: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "initial_count": len(self.initial_hypotheses),
            "stage1_count": len(self.stage1_survivors),
            "stage2_count": len(self.stage2_survivors),
            "final_diagnosis": self.final_diagnosis.to_dict(),
            "collapse_log": self.collapse_log
        }


@dataclass
class StructuredReport:
    """Structured radiology report output."""
    report_id: str
    study_date: str
    study_type: str
    clinical_indication: str
    technique: str
    comparison: Optional[str]
    findings: str
    impression: str
    recommendations: List[str]
    urgency: UrgencyLevel
    status: ReportStatus
    ai_confidence: float
    radiologist_required: bool
    error_collapse_result: Optional[ErrorCollapseResult] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    reviewed_by: Optional[str] = None
    signed_by: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "study_date": self.study_date,
            "study_type": self.study_type,
            "clinical_indication": self.clinical_indication,
            "technique": self.technique,
            "comparison": self.comparison,
            "findings": self.findings,
            "impression": self.impression,
            "recommendations": self.recommendations,
            "urgency": self.urgency.value,
            "status": self.status.value,
            "ai_confidence": self.ai_confidence,
            "radiologist_required": self.radiologist_required,
            "created_at": self.created_at,
            "reviewed_by": self.reviewed_by,
            "signed_by": self.signed_by
        }

    def to_clinical_format(self) -> str:
        """Generate clinical report format."""
        lines = [
            "=" * 60,
            "RADIOLOGY REPORT",
            "=" * 60,
            "",
            f"Study Date: {self.study_date}",
            f"Study Type: {self.study_type}",
            f"Report ID: {self.report_id}",
            "",
            "CLINICAL INDICATION:",
            self.clinical_indication,
            "",
            "TECHNIQUE:",
            self.technique,
            "",
        ]

        if self.comparison:
            lines.extend([
                "COMPARISON:",
                self.comparison,
                "",
            ])

        lines.extend([
            "FINDINGS:",
            self.findings,
            "",
            "IMPRESSION:",
            self.impression,
            "",
        ])

        if self.recommendations:
            lines.extend([
                "RECOMMENDATIONS:",
                *[f"  {i+1}. {rec}" for i, rec in enumerate(self.recommendations)],
                "",
            ])

        lines.extend([
            "-" * 60,
            f"Urgency: {self.urgency.value.upper()}",
            f"AI Confidence: {self.ai_confidence:.0%}",
            f"Status: {self.status.value}",
            "",
        ])

        if self.signed_by:
            lines.append(f"Electronically signed by: {self.signed_by}")
        elif self.reviewed_by:
            lines.append(f"Reviewed by: {self.reviewed_by}")
        else:
            lines.append("*** PENDING RADIOLOGIST REVIEW ***")

        lines.append("=" * 60)

        return "\n".join(lines)


class SentinelValidator:
    """
    Sentinel AI Validator

    A deliberately simple validation system that:
    1. Compares hypotheses across the analysis pipeline
    2. Implements error collapse methodology
    3. Learns from radiologist corrections
    4. Generates structured reports

    The "dumb" design catches errors that complex systems miss
    by applying consistent, simple rules rigorously.
    """

    def __init__(
        self,
        confidence_threshold: float = 0.90,
        error_tolerance: float = 0.01,
        require_radiologist_below: float = 0.95
    ):
        self.confidence_threshold = confidence_threshold
        self.error_tolerance = error_tolerance
        self.require_radiologist_below = require_radiologist_below
        self.learning_buffer: List[Dict[str, Any]] = []

    async def validate_and_collapse(
        self,
        initial_hypothesis: DiagnosticHypothesis,
        agent_outputs: List[Any],  # AgentOutput from thinking_hats
        clinical_context: Any  # ClinicalContext
    ) -> ErrorCollapseResult:
        """
        Main validation pipeline with error collapse.

        Error Collapse Methodology:
        Stage 1: 8 hypotheses -> 3 (eliminate low probability)
        Stage 2: 3 hypotheses -> 1-2 (evidence-based selection)
        Final: 1-2 -> 1 (clinical correlation)
        """

        # Gather all hypotheses from agents
        all_hypotheses = self._gather_hypotheses(agent_outputs)

        # Ensure initial hypothesis is included
        if not any(h.diagnosis == initial_hypothesis.diagnosis for h in all_hypotheses):
            all_hypotheses.insert(0, initial_hypothesis)

        collapse_log = []
        collapse_log.append(f"Initial hypotheses: {len(all_hypotheses)}")

        # Stage 1: Collapse to top 3-4 by probability
        stage1_survivors = self._stage1_collapse(all_hypotheses, collapse_log)
        collapse_log.append(f"Stage 1 survivors: {len(stage1_survivors)}")

        # Stage 2: Evidence-based collapse
        stage2_survivors = self._stage2_collapse(stage1_survivors, collapse_log)
        collapse_log.append(f"Stage 2 survivors: {len(stage2_survivors)}")

        # Final selection
        final = self._select_final_diagnosis(stage2_survivors, clinical_context, collapse_log)
        collapse_log.append(f"Final diagnosis: {final.diagnosis} ({final.confidence:.0%})")

        # Validate against initial hypothesis
        self._validate_hypothesis_consistency(
            initial_hypothesis,
            final,
            collapse_log
        )

        return ErrorCollapseResult(
            initial_hypotheses=all_hypotheses,
            stage1_survivors=stage1_survivors,
            stage2_survivors=stage2_survivors,
            final_diagnosis=final,
            collapse_log=collapse_log
        )

    def _gather_hypotheses(
        self,
        agent_outputs: List[Any]
    ) -> List[DiagnosticHypothesis]:
        """Gather hypotheses from all agent outputs."""
        hypotheses_map: Dict[str, DiagnosticHypothesis] = {}

        for output in agent_outputs:
            # Process hypotheses
            for hyp in output.hypotheses:
                if hyp not in hypotheses_map:
                    confidence = output.confidence_scores.get(hyp, 0.3)
                    hypotheses_map[hyp] = DiagnosticHypothesis(
                        diagnosis=hyp,
                        confidence=confidence
                    )
                else:
                    # Update confidence if higher
                    new_conf = output.confidence_scores.get(hyp, 0.3)
                    if new_conf > hypotheses_map[hyp].confidence:
                        hypotheses_map[hyp].confidence = new_conf

            # Process findings as hypotheses
            for finding in output.findings:
                if finding.name not in hypotheses_map:
                    hypotheses_map[finding.name] = DiagnosticHypothesis(
                        diagnosis=finding.name,
                        icd10_code=finding.icd10_code,
                        confidence=finding.confidence,
                        supporting_evidence=finding.supporting_evidence,
                        contradicting_evidence=finding.contradicting_evidence
                    )

        return list(hypotheses_map.values())

    def _stage1_collapse(
        self,
        hypotheses: List[DiagnosticHypothesis],
        log: List[str]
    ) -> List[DiagnosticHypothesis]:
        """
        Stage 1: Collapse based on probability threshold.
        Keep top 3-4 hypotheses, collapse rest.
        """
        # Sort by confidence
        sorted_hyp = sorted(hypotheses, key=lambda h: h.confidence, reverse=True)

        # Keep top 4 with confidence > 0.1
        survivors = []
        for i, hyp in enumerate(sorted_hyp):
            if i < 4 and hyp.confidence > 0.1:
                survivors.append(hyp)
            else:
                hyp.collapsed = True
                hyp.collapse_reason = f"Stage 1: Low probability ({hyp.confidence:.0%})"
                log.append(f"Collapsed '{hyp.diagnosis}': {hyp.collapse_reason}")

        return survivors

    def _stage2_collapse(
        self,
        hypotheses: List[DiagnosticHypothesis],
        log: List[str]
    ) -> List[DiagnosticHypothesis]:
        """
        Stage 2: Evidence-based collapse.
        Eliminate hypotheses with strong contradicting evidence.
        """
        survivors = []

        for hyp in hypotheses:
            # Calculate evidence ratio
            supporting = len(hyp.supporting_evidence)
            contradicting = len(hyp.contradicting_evidence)

            if contradicting > supporting * 2:
                hyp.collapsed = True
                hyp.collapse_reason = f"Stage 2: Contradicting evidence ({contradicting} vs {supporting})"
                log.append(f"Collapsed '{hyp.diagnosis}': {hyp.collapse_reason}")
            else:
                survivors.append(hyp)

        # Ensure at least one survivor
        if not survivors and hypotheses:
            survivors = [hypotheses[0]]
            survivors[0].collapsed = False
            log.append(f"Preserved '{survivors[0].diagnosis}' as fallback")

        return survivors

    def _select_final_diagnosis(
        self,
        hypotheses: List[DiagnosticHypothesis],
        clinical_context: Any,
        log: List[str]
    ) -> DiagnosticHypothesis:
        """Select final diagnosis from survivors."""
        if not hypotheses:
            return DiagnosticHypothesis(
                diagnosis="Indeterminate",
                confidence=0.0,
                supporting_evidence=["No valid hypotheses survived collapse"]
            )

        if len(hypotheses) == 1:
            return hypotheses[0]

        # Select highest confidence
        final = max(hypotheses, key=lambda h: h.confidence)

        # Log alternatives
        alternatives = [h for h in hypotheses if h != final]
        for alt in alternatives:
            log.append(f"Alternative: {alt.diagnosis} ({alt.confidence:.0%})")

        return final

    def _validate_hypothesis_consistency(
        self,
        initial: DiagnosticHypothesis,
        final: DiagnosticHypothesis,
        log: List[str]
    ) -> None:
        """Validate consistency between initial and final hypothesis."""
        if initial.diagnosis == final.diagnosis:
            log.append("VALIDATION: Initial hypothesis confirmed")
        else:
            log.append(
                f"VALIDATION: Hypothesis changed from '{initial.diagnosis}' "
                f"to '{final.diagnosis}'"
            )
            log.append("Consider reviewing analysis for consistency")

    async def generate_structured_report(
        self,
        collapse_result: ErrorCollapseResult,
        study_metadata: Dict[str, Any],
        clinical_indication: str,
        agent_outputs: List[Any]
    ) -> StructuredReport:
        """Generate structured radiology report."""

        # Generate report ID
        report_id = self._generate_report_id(study_metadata)

        # Determine urgency
        urgency = self._determine_urgency(collapse_result, agent_outputs)

        # Generate findings text
        findings_text = self._generate_findings_text(
            collapse_result,
            agent_outputs
        )

        # Generate impression
        impression = self._generate_impression(collapse_result)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            collapse_result,
            urgency
        )

        # Determine if radiologist required
        radiologist_required = (
            collapse_result.final_diagnosis.confidence < self.require_radiologist_below
            or urgency in [UrgencyLevel.URGENT, UrgencyLevel.CRITICAL]
        )

        return StructuredReport(
            report_id=report_id,
            study_date=study_metadata.get("StudyDate", datetime.now().strftime("%Y-%m-%d")),
            study_type=study_metadata.get("Modality", "Unknown"),
            clinical_indication=clinical_indication,
            technique=self._generate_technique_text(study_metadata),
            comparison=study_metadata.get("PriorStudy"),
            findings=findings_text,
            impression=impression,
            recommendations=recommendations,
            urgency=urgency,
            status=ReportStatus.PENDING_REVIEW if radiologist_required else ReportStatus.DRAFT,
            ai_confidence=collapse_result.final_diagnosis.confidence,
            radiologist_required=radiologist_required,
            error_collapse_result=collapse_result
        )

    def _generate_report_id(self, metadata: Dict[str, Any]) -> str:
        """Generate unique report ID."""
        data = json.dumps(metadata, sort_keys=True) + datetime.utcnow().isoformat()
        return hashlib.sha256(data.encode()).hexdigest()[:12].upper()

    def _determine_urgency(
        self,
        collapse_result: ErrorCollapseResult,
        agent_outputs: List[Any]
    ) -> UrgencyLevel:
        """Determine report urgency."""
        final = collapse_result.final_diagnosis

        # Critical findings
        critical_diagnoses = {
            "tension_pneumothorax", "tension pneumothorax",
            "massive_hemothorax", "massive hemothorax",
            "aortic_dissection", "aortic dissection",
            "cardiac_tamponade", "cardiac tamponade"
        }

        urgent_diagnoses = {
            "pneumothorax", "hemothorax",
            "pulmonary_embolism", "pulmonary embolism",
            "intracranial_hemorrhage", "intracranial hemorrhage"
        }

        diagnosis_lower = final.diagnosis.lower().replace("_", " ")

        if diagnosis_lower in critical_diagnoses:
            return UrgencyLevel.CRITICAL
        elif diagnosis_lower in urgent_diagnoses:
            return UrgencyLevel.URGENT
        elif final.confidence < 0.7:
            return UrgencyLevel.PRIORITY
        else:
            return UrgencyLevel.ROUTINE

    def _generate_findings_text(
        self,
        collapse_result: ErrorCollapseResult,
        agent_outputs: List[Any]
    ) -> str:
        """Generate findings section text."""
        lines = []

        final = collapse_result.final_diagnosis

        # Primary finding
        if final.confidence > 0.5:
            lines.append(f"PRIMARY FINDING: {final.diagnosis}")
            lines.append(f"Confidence: {final.confidence:.0%}")
            lines.append("")

            if final.supporting_evidence:
                lines.append("Supporting evidence:")
                for evidence in final.supporting_evidence:
                    lines.append(f"  - {evidence}")
                lines.append("")

        # Secondary considerations
        alternatives = [h for h in collapse_result.stage2_survivors
                       if h != final and not h.collapsed]
        if alternatives:
            lines.append("DIFFERENTIAL CONSIDERATIONS:")
            for alt in alternatives:
                lines.append(f"  - {alt.diagnosis} ({alt.confidence:.0%})")
            lines.append("")

        # Additional findings from agents
        additional_findings = []
        for output in agent_outputs:
            for finding in output.findings:
                if finding.name != final.diagnosis:
                    additional_findings.append(finding)

        if additional_findings:
            lines.append("ADDITIONAL FINDINGS:")
            for finding in additional_findings[:5]:  # Limit to 5
                lines.append(f"  - {finding.name}: {finding.severity or 'noted'}")

        return "\n".join(lines) if lines else "No significant findings identified."

    def _generate_impression(self, collapse_result: ErrorCollapseResult) -> str:
        """Generate impression section."""
        final = collapse_result.final_diagnosis

        if final.confidence > 0.9:
            return f"{final.diagnosis}."
        elif final.confidence > 0.7:
            return f"{final.diagnosis}, probable."
        elif final.confidence > 0.5:
            return f"Findings suggestive of {final.diagnosis}. Clinical correlation recommended."
        else:
            return f"Indeterminate study. Cannot exclude {final.diagnosis}. Recommend further evaluation."

    def _generate_recommendations(
        self,
        collapse_result: ErrorCollapseResult,
        urgency: UrgencyLevel
    ) -> List[str]:
        """Generate recommendations."""
        recommendations = []

        final = collapse_result.final_diagnosis

        if urgency == UrgencyLevel.CRITICAL:
            recommendations.append("IMMEDIATE physician notification required")
            recommendations.append("Consider emergent intervention")

        elif urgency == UrgencyLevel.URGENT:
            recommendations.append("Urgent physician notification recommended")

        if final.confidence < 0.8:
            recommendations.append("Clinical correlation recommended")

        if collapse_result.stage2_survivors and len(collapse_result.stage2_survivors) > 1:
            recommendations.append("Consider alternative diagnoses if clinical presentation changes")

        # Diagnosis-specific recommendations
        diagnosis_lower = final.diagnosis.lower()
        if "pneumothorax" in diagnosis_lower:
            recommendations.append("Consider chest tube placement if symptomatic")
        elif "hemothorax" in diagnosis_lower:
            recommendations.append("Surgical consultation recommended")
        elif "fracture" in diagnosis_lower:
            recommendations.append("Pain management and follow-up imaging as indicated")

        return recommendations

    def _generate_technique_text(self, metadata: Dict[str, Any]) -> str:
        """Generate technique section text."""
        modality = metadata.get("Modality", "Unknown")
        view = metadata.get("ViewPosition", "")

        if modality == "CR" or modality == "DX":
            return f"Portable chest radiograph, {view or 'AP'} projection."
        elif modality == "CT":
            return "CT examination performed with IV contrast."
        else:
            return f"{modality} examination performed per protocol."

    async def learn_from_correction(
        self,
        original_report: StructuredReport,
        corrected_diagnosis: str,
        corrected_by: str,
        correction_reason: str
    ) -> Dict[str, Any]:
        """
        Learn from radiologist correction.

        Stores correction for federated training.
        """
        learning_record = {
            "report_id": original_report.report_id,
            "original_diagnosis": original_report.error_collapse_result.final_diagnosis.diagnosis
                if original_report.error_collapse_result else "unknown",
            "original_confidence": original_report.ai_confidence,
            "corrected_diagnosis": corrected_diagnosis,
            "corrected_by": corrected_by,
            "correction_reason": correction_reason,
            "timestamp": datetime.utcnow().isoformat(),
            "study_type": original_report.study_type,
            "urgency": original_report.urgency.value
        }

        self.learning_buffer.append(learning_record)

        return {
            "status": "recorded",
            "record_id": len(self.learning_buffer),
            "message": "Correction recorded for model improvement"
        }

    def get_learning_buffer(self) -> List[Dict[str, Any]]:
        """Get accumulated learning records."""
        return self.learning_buffer.copy()

    def flush_learning_buffer(self) -> List[Dict[str, Any]]:
        """Flush and return learning buffer for training."""
        records = self.learning_buffer.copy()
        self.learning_buffer = []
        return records
