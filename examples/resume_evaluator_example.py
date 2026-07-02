from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_project_path() -> None:
    """Ensure the project root is importable when running this script directly."""
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def main() -> None:
    """Run a small end-to-end resume evaluation example."""
    _bootstrap_project_path()
    from services.resume_evaluator import ResumeEvaluator

    evaluator = ResumeEvaluator(database_url="./blackcrest.db")
    sample_resume = (
        "Jane Doe has 8 years of experience in Python, SQL, and cloud infrastructure. "
        "She led a small engineering team and improved release reliability."
    )
    result = evaluator.evaluate_resume(resume_text=sample_resume, candidate_name="Jane Doe")
    print("Evaluation result:")
    print(result)


if __name__ == "__main__":
    main()
