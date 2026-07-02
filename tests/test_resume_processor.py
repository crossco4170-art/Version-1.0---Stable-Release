from pathlib import Path

from services.resume_processor import ResumeProcessor


def test_resume_processor_returns_structured_json(tmp_path: Path) -> None:
    processor = ResumeProcessor(database_url=f"sqlite:///{tmp_path / 'resumes.db'}")

    sample_text = """
    Jane Doe
    (555) 123-4567
    jane@example.com
    Experience: 5 years in software development
    Skills: Python, SQL, FastAPI
    Education: BS Computer Science
    Employment History: Senior Engineer at Acme Corp
    """

    resume_path = tmp_path / "resume.txt"
    resume_path.write_text(sample_text, encoding="utf-8")

    result = processor.process_resume(resume_path)

    assert result["name"] == "Jane Doe"
    assert result["phone"] == "(555) 123-4567"
    assert result["email"] == "jane@example.com"
    assert result["experience"] == "5 years in software development"
    assert result["skills"] == ["Python", "SQL", "FastAPI"]
    assert result["education"] == ["BS Computer Science"]
    assert result["employment_history"] == ["Senior Engineer at Acme Corp"]
    assert result["source_type"] == "text"
