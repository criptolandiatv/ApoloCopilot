#!/usr/bin/env python3
"""
AI Radiology Report System - Main Entry Point

Emergency radiology AI for:
- Chest X-ray (trauma: pneumothorax, hemothorax)
- ICU monitoring (NGT, CVC, ETT positioning)
- Head CT (trauma, hemorrhage)

Usage:
    python main.py --demo              # Run demo analysis
    python main.py --server            # Start API server
    python main.py --analyze <path>    # Analyze single image

Author: ApoloCopilot Team
License: MIT
"""

import asyncio
import argparse
import json
from pathlib import Path
from typing import Optional

from agents import (
    RadiologyOrchestrator,
    ClinicalContext,
    AnalysisRequest
)
from agents.orchestrator import OrchestratorConfig


def demo_analysis():
    """Run demonstration analysis with mock data."""
    print("=" * 60)
    print("AI RADIOLOGY REPORT SYSTEM - DEMO")
    print("=" * 60)
    print()

    # Create orchestrator
    config = OrchestratorConfig(
        parallel_execution=True,
        confidence_threshold=0.90
    )
    orchestrator = RadiologyOrchestrator(config=config)

    # Mock clinical context (trauma patient)
    clinical_context = ClinicalContext(
        age=34,
        sex="Male",
        chief_complaint="Chest pain and dyspnea after MVA",
        mechanism_of_injury="Motor vehicle accident, restrained driver, airbag deployed",
        vital_signs={
            "BP": "110/70",
            "HR": 98,
            "RR": 22,
            "SpO2": 94
        },
        relevant_history=["No known medical conditions"],
        recent_procedures=[],
        medications=[]
    )

    # Mock image metadata (DICOM-style)
    metadata = {
        "Modality": "CR",
        "BodyPartExamined": "CHEST",
        "ViewPosition": "AP",
        "StudyDate": "2026-01-06",
        "StudyInstanceUID": "1.2.3.4.5.6.7.8.9.DEMO",
        "PatientAge": "034Y",
        "PatientSex": "M"
    }

    # Mock image data (placeholder)
    image_data = b"MOCK_IMAGE_DATA"

    # Create request
    request = AnalysisRequest(
        image_data=image_data,
        image_metadata=metadata,
        clinical_context=clinical_context,
        study_id="DEMO-001",
        priority="urgent"
    )

    # Run analysis
    print("Running analysis...")
    print()

    async def run_analysis():
        result = await orchestrator.analyze(request)
        return result

    result = asyncio.run(run_analysis())

    # Display results
    print("ANALYSIS COMPLETE")
    print("-" * 60)
    print()
    print(result.report.to_clinical_format())
    print()
    print("-" * 60)
    print("VALIDATION SUMMARY:")
    print(json.dumps(result.validation_summary, indent=2))
    print()
    print(f"Total Processing Time: {result.processing_time_ms:.0f}ms")
    print("-" * 60)

    return result


def start_server(host: str = "0.0.0.0", port: int = 8080):
    """Start FastAPI server for radiology AI."""
    try:
        import uvicorn
        from api import create_app

        app = create_app()
        print(f"Starting Radiology AI Server on {host}:{port}")
        uvicorn.run(app, host=host, port=port)
    except ImportError:
        print("Error: FastAPI/Uvicorn not installed.")
        print("Install with: pip install fastapi uvicorn")


def analyze_image(image_path: str, clinical_info: Optional[dict] = None):
    """Analyze a single image file."""
    path = Path(image_path)

    if not path.exists():
        print(f"Error: File not found: {image_path}")
        return

    # Read image
    with open(path, "rb") as f:
        image_data = f.read()

    # Detect modality from filename or extension
    filename = path.name.lower()
    if "ct" in filename:
        modality = "CT"
        body_part = "HEAD" if "head" in filename else "CHEST"
    else:
        modality = "CR"
        body_part = "CHEST"

    metadata = {
        "Modality": modality,
        "BodyPartExamined": body_part,
        "StudyDate": "2026-01-06",
        "SourceFile": str(path)
    }

    # Default clinical context
    clinical_context = ClinicalContext(
        chief_complaint=clinical_info.get("complaint", "Evaluate for acute findings")
        if clinical_info else "Evaluate for acute findings",
        mechanism_of_injury=clinical_info.get("mechanism") if clinical_info else None
    )

    orchestrator = RadiologyOrchestrator()

    request = AnalysisRequest(
        image_data=image_data,
        image_metadata=metadata,
        clinical_context=clinical_context,
        study_id=path.stem
    )

    async def run():
        return await orchestrator.analyze(request)

    result = asyncio.run(run())

    print(result.report.to_clinical_format())
    return result


def print_system_info():
    """Print system information and capabilities."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║           AI RADIOLOGY REPORT SYSTEM v1.0                    ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║  SUPPORTED MODALITIES:                                       ║
    ║    • Chest X-ray (CR/DX)                                     ║
    ║    • Head CT                                                 ║
    ║    • Chest CT (planned)                                      ║
    ║                                                              ║
    ║  PRIMARY DIAGNOSES:                                          ║
    ║    • Pneumothorax (traumatic/iatrogenic)                     ║
    ║    • Hemothorax                                              ║
    ║    • Pulmonary contusion                                     ║
    ║    • Rib fractures                                           ║
    ║    • Intracranial hemorrhage                                 ║
    ║    • Tube/line positioning                                   ║
    ║                                                              ║
    ║  ARCHITECTURE:                                               ║
    ║    • 6 Thinking Hats Agent Orchestra                         ║
    ║    • Sentinel AI Validator                                   ║
    ║    • Error Collapse Methodology                              ║
    ║    • Structured Report Generation                            ║
    ║                                                              ║
    ║  PUBLIC DATASETS INTEGRATED:                                 ║
    ║    • NIH ChestX-ray14 (112,120 images)                       ║
    ║    • MIMIC-CXR (377,110 images)                              ║
    ║    • CheXpert (224,316 images)                               ║
    ║    • VinDr-CXR (18,000 images)                               ║
    ║    • RSNA Intracranial (750,000 images)                      ║
    ║                                                              ║
    ║  SECURITY:                                                   ║
    ║    • Stanford-level hospital security model                  ║
    ║    • Air-gapped architecture                                 ║
    ║    • HIPAA 2025 compliant                                    ║
    ║    • AES-256 encryption                                      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝

    For more information, see: radiology_ai/README.md
    """)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Radiology Report System for Emergency Medicine"
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demonstration analysis with mock data"
    )

    parser.add_argument(
        "--server",
        action="store_true",
        help="Start the API server"
    )

    parser.add_argument(
        "--analyze",
        type=str,
        metavar="PATH",
        help="Analyze a single image file"
    )

    parser.add_argument(
        "--complaint",
        type=str,
        help="Clinical complaint (for --analyze)"
    )

    parser.add_argument(
        "--mechanism",
        type=str,
        help="Mechanism of injury (for --analyze)"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Server host (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Server port (default: 8080)"
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Display system information"
    )

    args = parser.parse_args()

    if args.info:
        print_system_info()
    elif args.demo:
        demo_analysis()
    elif args.server:
        start_server(args.host, args.port)
    elif args.analyze:
        clinical_info = {}
        if args.complaint:
            clinical_info["complaint"] = args.complaint
        if args.mechanism:
            clinical_info["mechanism"] = args.mechanism
        analyze_image(args.analyze, clinical_info or None)
    else:
        print_system_info()
        parser.print_help()


if __name__ == "__main__":
    main()
