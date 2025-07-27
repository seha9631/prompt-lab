"""
이메일 검증 모듈
"""

import re
from typing import Optional


class EmailValidator:
    """이메일 검증 클래스"""

    # 이메일 정규식 패턴
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        이메일 형식이 유효한지 검증

        Args:
            email: 검증할 이메일 주소

        Returns:
            bool: 유효한 이메일이면 True, 아니면 False
        """
        if not email or not isinstance(email, str):
            return False

        # 기본 길이 검증
        if len(email) > 254:  # RFC 5321 최대 길이
            return False

        # 정규식 패턴 검증
        if not EmailValidator.EMAIL_PATTERN.match(email):
            return False

        # 추가 검증 규칙
        return EmailValidator._additional_validation(email)

    @staticmethod
    def _additional_validation(email: str) -> bool:
        """
        추가 이메일 검증 규칙

        Args:
            email: 검증할 이메일 주소

        Returns:
            bool: 추가 검증을 통과하면 True, 아니면 False
        """
        # @ 기호가 정확히 하나만 있는지 확인
        if email.count("@") != 1:
            return False

        # 로컬 부분과 도메인 부분 분리
        local_part, domain_part = email.split("@")

        # 로컬 부분 검증
        if not local_part or len(local_part) > 64:  # RFC 5321
            return False

        # 도메인 부분 검증
        if not domain_part or len(domain_part) > 253:  # RFC 5321
            return False

        # 도메인에 점이 있는지 확인
        if "." not in domain_part:
            return False

        # 도메인 부분이 점으로 시작하거나 끝나지 않는지 확인
        if domain_part.startswith(".") or domain_part.endswith("."):
            return False

        # 연속된 점이 없는지 확인
        if ".." in domain_part:
            return False

        return True

    @staticmethod
    def normalize_email(email: str) -> str:
        """
        이메일 주소를 정규화 (소문자 변환)

        Args:
            email: 정규화할 이메일 주소

        Returns:
            str: 정규화된 이메일 주소
        """
        return email.lower().strip()

    @staticmethod
    def extract_domain(email: str) -> Optional[str]:
        """
        이메일에서 도메인 부분 추출

        Args:
            email: 이메일 주소

        Returns:
            Optional[str]: 도메인 부분, 실패 시 None
        """
        if not EmailValidator.is_valid_email(email):
            return None

        return email.split("@")[1].lower()
