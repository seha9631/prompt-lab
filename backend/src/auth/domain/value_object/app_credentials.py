import re
from typing import Any

from src.shared.security import EmailValidator, PasswordHasher


class AppId:
    """앱 ID 값 객체 (이메일 형식)"""

    def __init__(self, value: str):
        if not value or not value.strip():
            raise ValueError("App ID cannot be empty")

        # 이메일 형식 검증
        if not EmailValidator.is_valid_email(value):
            raise ValueError("App ID must be a valid email address")

        # 이메일 정규화 (소문자 변환)
        self.value = EmailValidator.normalize_email(value)

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AppId):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    @property
    def domain(self) -> str:
        """이메일 도메인 부분 반환"""
        return EmailValidator.extract_domain(self.value) or ""


class AppPassword:
    """앱 비밀번호 값 객체 (암호화 지원)"""

    def __init__(self, value: str, is_hashed: bool = False):
        if not value or not value.strip():
            raise ValueError("App password cannot be empty")

        if is_hashed:
            # 이미 해싱된 비밀번호인 경우
            if not PasswordHasher.is_hashed(value):
                raise ValueError("Invalid hashed password format")
            self.value = value
            self._is_hashed = True
        else:
            # 원본 비밀번호인 경우
            if len(value) < 8:
                raise ValueError("App password must be at least 8 characters long")

            # 비밀번호 복잡도 검증
            if not self._validate_password_strength(value):
                raise ValueError(
                    "Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character"
                )

            self.value = value.strip()
            self._is_hashed = False

    def _validate_password_strength(self, password: str) -> bool:
        """비밀번호 복잡도 검증"""
        # 최소 8자 이상
        if len(password) < 8:
            return False

        # 대문자, 소문자, 숫자, 특수문자 포함 여부 확인
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        return has_upper and has_lower and has_digit and has_special

    def hash(self) -> str:
        """비밀번호를 해싱하여 반환"""
        if self._is_hashed:
            return self.value

        return PasswordHasher.hash_password(self.value)

    def verify(self, plain_password: str) -> bool:
        """비밀번호 검증"""
        if self._is_hashed:
            return PasswordHasher.verify_password(plain_password, self.value)
        else:
            return self.value == plain_password

    @property
    def is_hashed(self) -> bool:
        """해싱된 비밀번호인지 확인"""
        return self._is_hashed

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AppPassword):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
