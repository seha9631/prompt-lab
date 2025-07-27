"""
비즈니스 로직 관련 예외 클래스들
"""

from typing import Optional, Dict, Any
from .base_exception import BaseCustomException
from .error_codes import ErrorCode


class BusinessException(BaseCustomException):
    """비즈니스 로직 예외의 기본 클래스"""

    pass


class ValidationException(BusinessException):
    """유효성 검증 예외"""

    def __init__(
        self,
        message: Optional[str] = None,
        field_errors: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if field_errors:
            details["field_errors"] = field_errors

        super().__init__(
            error_code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )


class AuthenticationException(BusinessException):
    """인증 예외"""

    def __init__(self, message: Optional[str] = None, **kwargs):
        super().__init__(
            error_code=ErrorCode.AUTHENTICATION_FAILED, message=message, **kwargs
        )


class AuthorizationException(BusinessException):
    """인가 예외"""

    def __init__(self, message: Optional[str] = None, **kwargs):
        super().__init__(
            error_code=ErrorCode.AUTHORIZATION_FAILED, message=message, **kwargs
        )


class DuplicateResourceException(BusinessException):
    """중복 리소스 예외"""

    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        details.update({"resource_type": resource_type, "resource_id": resource_id})

        if not message:
            message = f"{resource_type}이(가) 이미 존재합니다."
            if resource_id:
                message += f" (ID: {resource_id})"

        super().__init__(
            error_code=ErrorCode.RESOURCE_ALREADY_EXISTS,
            message=message,
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )


class ResourceNotFoundException(BusinessException):
    """리소스를 찾을 수 없는 예외"""

    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        details.update({"resource_type": resource_type, "resource_id": resource_id})

        if not message:
            message = f"{resource_type}을(를) 찾을 수 없습니다."
            if resource_id:
                message += f" (ID: {resource_id})"

        super().__init__(
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            message=message,
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )
