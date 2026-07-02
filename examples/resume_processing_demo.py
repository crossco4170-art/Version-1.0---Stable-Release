from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.resume_processor import ResumeProcessor


def main() -> None:
    """Minimal demo for PDF and DOCX resume extraction."""
    base_dir = Path(__file__).resolve().parent
    processor = ResumeProcessor(database_url="sqlite:///./demo_resumes.db")

    pdf_path = base_dir / "sample_resume.pdf"
    docx_path = base_dir / "sample_resume.docx"

    if not pdf_path.exists():
        raise FileNotFoundError(f"Sample PDF not found: {pdf_path}")
    if not docx_path.exists():
        raise FileNotFoundError(f"Sample DOCX not found: {docx_path}")

    print("PDF extraction:")
    pdf_result = processor.process_resume(pdf_path)
    print(pdf_result["raw_text"])
    print("\nDOCX extraction:")
    docx_result = processor.process_resume(docx_path)
    print(docx_result["raw_text"])


if __name__ == "__main__":
    main()
