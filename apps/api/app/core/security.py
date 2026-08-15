from hashlib import sha256
from secrets import token_urlsafe

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def _generate_secure_token() -> str:
    return token_urlsafe(32)


def _hash_secure_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def generate_session_token() -> str:
    return _generate_secure_token()


def hash_session_token(token: str) -> str:
    return _hash_secure_token(token)


def generate_invitation_token() -> str:
    return _generate_secure_token()


def hash_invitation_token(token: str) -> str:
    return _hash_secure_token(token)
