from __future__ import annotations

import hashlib
import hmac
import secrets

from utils.exceptions import BlackcrestInputError

SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_DKLEN = 64


def hash_password(password: str) -> str:
    """Hash a password using scrypt with a random salt."""
    if not password or len(password) < 12:
        raise BlackcrestInputError("Password must be at least 12 characters long")

    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=SCRYPT_DKLEN,
    )
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored scrypt hash."""
    try:
        algorithm, n, r, p, salt_hex, digest_hex = password_hash.split("$")
    except ValueError:
        return False

    if algorithm != "scrypt":
        return False

    try:
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        derived = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(expected),
        )
    except Exception:
        return False

    return hmac.compare_digest(derived, expected)
