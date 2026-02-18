import pytest
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    create_refresh_token,
)

class TestPasswordHashing:
    def test_hash_password_returns_string(self):
        result = hash_password("mypassword")
        assert isinstance(result, str)
        assert result != "mypassword"

    def test_verify_correct_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        hash1 = hash_password("mypassword")
        hash2 = hash_password("mypassword")
        assert hash1 != hash2  # Argon2 uses random salt

class TestJWT:
    def test_create_and_decode_access_token(self):
        token = create_access_token("user-123", "user@example.com")
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"
        assert payload["email"] == "user@example.com"
        assert payload["type"] == "access"

    def test_decode_invalid_token(self):
        result = decode_access_token("invalid-token")
        assert result is None

    def test_create_refresh_token(self):
        token = create_refresh_token()
        assert isinstance(token, str)
        assert len(token) == 36  # UUID format

class TestTokenExpiry:
    def test_token_has_expiry(self):
        token = create_access_token("user-123", "test@example.com")
        payload = decode_access_token(token)
        assert "exp" in payload
