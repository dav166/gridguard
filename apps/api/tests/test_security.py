from app.core.security import (
    hash_password,
    verify_password,
)


def test_hash_password_does_not_store_plain_text() -> None:
    password = "correct-horse-battery-staple"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert password not in hashed_password


def test_verify_password_accepts_correct_password() -> None:
    password = "correct-horse-battery-staple"

    hashed_password = hash_password(password)

    assert verify_password(
        password,
        hashed_password,
    )


def test_verify_password_rejects_wrong_password() -> None:
    hashed_password = hash_password(
        "correct-horse-battery-staple"
    )

    assert not verify_password(
        "wrong-password",
        hashed_password,
    )