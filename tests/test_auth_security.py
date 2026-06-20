import pytest
from pydantic import ValidationError

from backend.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    hash_token,
    verify_password,
)
from backend.models.schemas import UserCreate


def test_password_hash_round_trip():
    password = "ValidPassword!123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)


def test_password_policy_rejects_weak_password():
    with pytest.raises(ValidationError):
        UserCreate(email="qa@example.com", password="password")


def test_access_token_is_created():
    token = create_access_token("qa@example.com")
    assert token.count(".") == 2


def test_refresh_tokens_are_random_and_hashed():
    first, first_hash, _ = create_refresh_token()
    second, second_hash, _ = create_refresh_token()

    assert first != second
    assert first_hash == hash_token(first)
    assert second_hash == hash_token(second)
    assert first_hash != second_hash
