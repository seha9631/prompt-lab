"""
기본 커스텀 예외 클래스
"""

from typing import Optional, Dict, Any
from .error_codes import ErrorCode


class BaseCustomException(Exception):
    """
    모든 커스텀 예외의 기본 클래스
    """

    def __init__(
        self,
        error_code: ErrorCode,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        기본 커스텀 예외 초기화

        Args:
            error_code: 에러 코드
            message: 사용자 정의 메시지 (없으면 error_code의 기본 메시지 사용)
            details: 추가 세부 정보
            original_exception: 원본 예외 (wrapping할 때 사용)
        """
        self.error_code = error_code
        self.message = message or error_code.message
        self.details = details or {}
        self.original_exception = original_exception

        super().__init__(self.message)

    @property
    def error_dict(self) -> Dict[str, Any]:
        """예외 정보를 딕셔너리로 반환"""
        result = {
            "error_code": self.error_code.code,
            "message": self.message,
            "details": self.details,
        }

        if self.original_exception:
            result["original_error"] = str(self.original_exception)

        return result

    def __str__(self) -> str:
        return f"[{self.error_code.code}] {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(error_code={self.error_code.code}, message='{self.message}')"
