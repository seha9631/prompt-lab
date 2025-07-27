"""
인프라스트럭처 관련 예외 클래스들
"""

from typing import Optional
from .base_exception import BaseCustomException
from .error_codes import ErrorCode


class InfrastructureException(BaseCustomException):
    """인프라스트럭처 예외의 기본 클래스"""

    pass


class DatabaseException(InfrastructureException):
    """데이터베이스 관련 예외"""

    def __init__(
        self, message: Optional[str] = None, query: Optional[str] = None, **kwargs
    ):
        details = kwargs.get("details", {})
        if query:
            details["query"] = query

        super().__init__(
            error_code=ErrorCode.DATABASE_QUERY_ERROR,
            message=message,
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )


class DatabaseConnectionException(DatabaseException):
    """데이터베이스 연결 예외"""

    def __init__(self, message: Optional[str] = None, **kwargs):
        super().__init__(message=message, **kwargs)
        self.error_code = ErrorCode.DATABASE_CONNECTION_ERROR


class DatabaseTransactionException(DatabaseException):
    """데이터베이스 트랜잭션 예외"""

    def __init__(self, message: Optional[str] = None, **kwargs):
        super().__init__(message=message, **kwargs)
        self.error_code = ErrorCode.DATABASE_TRANSACTION_ERROR


class ExternalServiceException(InfrastructureException):
    """외부 서비스 관련 예외"""

    def __init__(
        self,
        service_name: str,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        details.update({"service_name": service_name, "status_code": status_code})

        if not message:
            message = f"{service_name} 서비스 호출에 실패했습니다."
            if status_code:
                message += f" (Status: {status_code})"

        super().__init__(
            error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            message=message,
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )


class ExternalServiceTimeoutException(ExternalServiceException):
    """외부 서비스 타임아웃 예외"""

    def __init__(
        self, service_name: str, timeout_seconds: Optional[float] = None, **kwargs
    ):
        details = kwargs.get("details", {})
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds

        message = f"{service_name} 서비스 요청이 시간 초과되었습니다."
        if timeout_seconds:
            message += f" (Timeout: {timeout_seconds}초)"

        super().__init__(
            service_name=service_name,
            message=message,
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )
        self.error_code = ErrorCode.EXTERNAL_SERVICE_TIMEOUT
