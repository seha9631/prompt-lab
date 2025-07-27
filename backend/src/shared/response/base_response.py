"""
공통 응답 클래스들
"""

from typing import Optional, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """
    모든 API 응답의 기본 클래스

    Args:
        success: 요청 성공 여부
        message: 응답 메시지
        data: 응답 데이터 (성공 시)
        error: 에러 메시지 (실패 시)
    """

    success: bool = Field(..., description="요청 성공 여부")
    message: str = Field(..., description="응답 메시지")
    data: Optional[T] = Field(None, description="응답 데이터")
    error: Optional[str] = Field(None, description="에러 메시지")

    @classmethod
    def success_response(
        cls,
        message: str = "요청이 성공적으로 처리되었습니다.",
        data: Optional[T] = None,
    ) -> "BaseResponse[T]":
        """성공 응답 생성"""
        return cls(success=True, message=message, data=data, error=None)

    @classmethod
    def error_response(
        cls,
        message: str = "요청 처리 중 오류가 발생했습니다.",
        error: Optional[str] = None,
    ) -> "BaseResponse[T]":
        """에러 응답 생성"""
        return cls(success=False, message=message, data=None, error=error or message)


class SuccessResponse(BaseResponse[T]):
    """성공 응답 전용 클래스"""

    def __init__(self, message: str, data: Optional[T] = None):
        super().__init__(success=True, message=message, data=data, error=None)


class ErrorResponse(BaseResponse[T]):
    """에러 응답 전용 클래스"""

    def __init__(self, message: str, error: Optional[str] = None):
        super().__init__(
            success=False, message=message, data=None, error=error or message
        )


# 편의 함수들
def create_success_response(
    message: str = "요청이 성공적으로 처리되었습니다.", data: Optional[Any] = None
) -> BaseResponse:
    """성공 응답 생성 편의 함수"""
    return BaseResponse.success_response(message=message, data=data)


def create_error_response(
    message: str = "요청 처리 중 오류가 발생했습니다.", error: Optional[str] = None
) -> BaseResponse:
    """에러 응답 생성 편의 함수"""
    return BaseResponse.error_response(message=message, error=error)
