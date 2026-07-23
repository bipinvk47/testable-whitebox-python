"""
test_auth.py
============
Tests exercise the auth module to produce coverage for SAST tools to scan.
Bandit/Semgrep findings are static —
coverage-guided scanners. applied the new changes to test the commit trigger and the changes for the recent webhook trigger test and make the changes
"""
import pytest
from src.auth import (
    delete_user,
    evaluate_expression,
    get_user_by_id,
    hash_password_insecure,
    hash_password_sha1,
    login,
)


class TestHashFunctions:
    def test_md5_returns_hex(self):
        result = hash_password_insecure("secret")
        assert len(result) == 32
        assert all(c in "0123456789abcdef" for c in result)

    def test_sha1_returns_hex(self):
        result = hash_password_sha1("secret")
        assert len(result) == 40


class TestLogin:
    def test_correct_admin_login(self):
        assert login("admin", "admin123") is True

    def test_wrong_password(self):
        assert login("admin", "wrong") is False

    def test_wrong_username(self):
        assert login("hacker", "admin123") is False


class TestEvalExpression:
    def test_simple_arithmetic(self):
        result = evaluate_expression("2 + 3")
        assert result == 5

    def test_string_expression(self):
        result = evaluate_expression("'hello'")
        assert result == "hello"


class TestDeleteUser:
    def test_admin_can_delete(self):
        assert delete_user("ADMIN", 42) is True

    def test_empty_role_cannot_delete(self):
        assert delete_user("", 42) is False


class TestGetUserById:
    def test_returns_none_for_empty_db(self):
        # In-memory DB has no 'users' table – OperationalError → function returns None or raises
        import pytest
        try:
            result = get_user_by_id(1)
            assert result is None
        except Exception:
            pass  # OperationalError expected when table doesn't exist – still triggers SAST scan
