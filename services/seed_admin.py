from __future__ import annotations

import getpass
import sys
from pathlib import Path
from typing import Callable

from sqlalchemy.orm import Session

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database import initialize_database
from database.connection import get_session
from services.admin_user_service import AdminUserService
from utils.exceptions import BlackcrestAuthError
from utils.passwords import hash_password


def seed_admin_user(
    *,
    session: Session | None = None,
    username: str | None = None,
    password: str | None = None,
) -> object:
    """Create an administrator user securely if one does not already exist."""
    service = AdminUserService(session=session or get_session(ensure_schema=True))
    existing_users = service.list()
    if existing_users:
        return existing_users[0]

    if not username or not username.strip():
        raise BlackcrestAuthError("Administrator username is required when no administrator exists")
    if not password:
        raise BlackcrestAuthError("Administrator password is required when no administrator exists")

    normalized_username = username.strip()
    existing = service.get_by_username(normalized_username)
    if existing is not None:
        return existing

    return service.create(
        username=normalized_username,
        email=f"{normalized_username}@local.blackcrest",
        password_hash=hash_password(password),
        is_active=True,
    )


def bootstrap_admin_user(
    *,
    session: Session | None = None,
    input_fn: Callable[[str], str] = input,
    getpass_fn: Callable[[str], str] = getpass.getpass,
    print_fn: Callable[[str], None] = print,
) -> object:
    """Interactively create the first administrator if none exists."""
    service = AdminUserService(session=session or get_session(ensure_schema=True))
    existing_users = service.list()
    if existing_users:
        return existing_users[0]

    print_fn("No administrator found. Complete first-run bootstrap.")
    username = _prompt_admin_username(service=service, input_fn=input_fn, print_fn=print_fn)
    password = _prompt_admin_password(getpass_fn=getpass_fn, print_fn=print_fn)
    return seed_admin_user(session=service.session, username=username, password=password)


def _prompt_admin_username(
    *,
    service: AdminUserService,
    input_fn: Callable[[str], str],
    print_fn: Callable[[str], None],
) -> str:
    while True:
        username = input_fn("Create administrator username: ").strip()
        if not username:
            print_fn("Username cannot be empty.")
            continue
        if service.get_by_username(username) is not None:
            print_fn("Username already exists. Choose a different username.")
            continue
        return username


def _prompt_admin_password(
    *,
    getpass_fn: Callable[[str], str],
    print_fn: Callable[[str], None],
) -> str:
    while True:
        password = getpass_fn("Create administrator password: ")
        confirm = getpass_fn("Confirm administrator password: ")
        if password != confirm:
            print_fn("Passwords do not match. Try again.")
            continue
        if len(password) < 12:
            print_fn("Password must be at least 12 characters long.")
            continue
        return password


if __name__ == "__main__":
    initialize_database()
    bootstrap_admin_user()
