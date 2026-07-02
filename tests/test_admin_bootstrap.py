from __future__ import annotations

from pathlib import Path

from services.admin_user_service import AdminUserService
from services.seed_admin import bootstrap_admin_user, seed_admin_user
from tests.helpers import build_test_session
from utils.passwords import verify_password


def test_seed_admin_user_requires_credentials_on_first_run(tmp_path: Path) -> None:
    session = build_test_session(tmp_path / "bootstrap_requires_creds.db")

    try:
        seed_admin_user(session=session)
    except ValueError as exc:
        assert "username" in str(exc)
    else:
        raise AssertionError("Expected ValueError when no bootstrap credentials are provided")


def test_seed_admin_user_creates_hashed_password_admin(tmp_path: Path) -> None:
    session = build_test_session(tmp_path / "bootstrap_seed.db")

    admin = seed_admin_user(
        session=session,
        username="founder",
        password="super-secure-pass",
    )

    assert admin.username == "founder"
    assert admin.password_hash != "super-secure-pass"
    assert admin.password_hash.startswith("scrypt$")
    assert verify_password("super-secure-pass", admin.password_hash) is True


def test_bootstrap_admin_user_interactive_first_run(tmp_path: Path) -> None:
    session = build_test_session(tmp_path / "bootstrap_interactive.db")

    prompts: list[str] = []
    printed: list[str] = []

    username_answers = iter(["founder"])
    password_answers = iter(["super-secure-pass", "super-secure-pass"])

    def fake_input(prompt: str) -> str:
        prompts.append(prompt)
        return next(username_answers)

    def fake_getpass(prompt: str) -> str:
        prompts.append(prompt)
        return next(password_answers)

    admin = bootstrap_admin_user(
        session=session,
        input_fn=fake_input,
        getpass_fn=fake_getpass,
        print_fn=printed.append,
    )

    assert admin.username == "founder"
    assert verify_password("super-secure-pass", admin.password_hash) is True
    assert any("first-run bootstrap" in text.lower() for text in printed)


def test_bootstrap_skips_prompt_if_admin_exists(tmp_path: Path) -> None:
    session = build_test_session(tmp_path / "bootstrap_existing.db")

    service = AdminUserService(session=session)
    existing = service.create(
        username="admin",
        email="admin@example.com",
        password_hash="scrypt$16384$8$1$aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa$bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        is_active=True,
    )

    call_count = {"input": 0, "getpass": 0}

    def fake_input(_: str) -> str:
        call_count["input"] += 1
        return "ignored"

    def fake_getpass(_: str) -> str:
        call_count["getpass"] += 1
        return "ignored"

    bootstrap_admin = bootstrap_admin_user(
        session=session,
        input_fn=fake_input,
        getpass_fn=fake_getpass,
        print_fn=lambda _: None,
    )

    assert bootstrap_admin.username == existing.username
    assert call_count["input"] == 0
    assert call_count["getpass"] == 0
