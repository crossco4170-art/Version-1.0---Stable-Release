from pathlib import Path


def test_project_structure_files_exist() -> None:
    expected_paths = [
        Path("main.py"),
        Path("README.md"),
        Path("requirements.txt"),
        Path(".env.example"),
        Path("api"),
        Path("config"),
        Path("database"),
        Path("logs"),
        Path("bots"),
        Path("services"),
        Path("models"),
        Path("utils"),
        Path("templates"),
        Path("tests"),
    ]

    for path in expected_paths:
        assert path.exists(), f"Expected project path to exist: {path}"
