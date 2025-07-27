"""
비밀번호 해싱 모듈
"""

import bcrypt
from typing import Optional


class PasswordHasher:
    """비밀번호 해싱 및 검증 클래스"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        비밀번호를 해싱하여 반환

        Args:
            password: 원본 비밀번호

        Returns:
            str: 해싱된 비밀번호 (UTF-8로 디코딩된 bytes)
        """
        # bcrypt로 비밀번호 해싱 (기본 라운드: 12)
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        비밀번호 검증

        Args:
            password: 검증할 원본 비밀번호
            hashed_password: 저장된 해싱된 비밀번호

        Returns:
            bool: 비밀번호가 일치하면 True, 아니면 False
        """
        try:
            # bcrypt로 비밀번호 검증
            return bcrypt.checkpw(
                password.encode("utf-8"), hashed_password.encode("utf-8")
            )
        except Exception:
            # 해싱된 비밀번호 형식이 잘못된 경우
            return False

    @staticmethod
    def is_hashed(password: str) -> bool:
        """
        문자열이 이미 해싱된 비밀번호인지 확인

        Args:
            password: 확인할 문자열

        Returns:
            bool: 해싱된 비밀번호이면 True, 아니면 False
        """
        try:
            # bcrypt 해시는 항상 $2b$로 시작
            return password.startswith("$2b$") and len(password) == 60
        except Exception:
            return False
