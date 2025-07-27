"""
공통 예외 처리 모듈
"""

from .base_exception import BaseCustomException
from .business_exception import (
    BusinessException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    DuplicateResourceException,
    ResourceNotFoundException,
)
from .infrastructure_exception import (
    InfrastructureException,
    DatabaseException,
    ExternalServiceException,
)
from .error_codes import ErrorCode

__all__ = [
    "BaseCustomException",
    "BusinessException",
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "DuplicateResourceException",
    "ResourceNotFoundException",
    "InfrastructureException",
    "DatabaseException",
    "ExternalServiceException",
    "ErrorCode",
]
