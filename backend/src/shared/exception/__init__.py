"""
공통 예외 처리 모듈
"""

from .base_exception import BaseCustomException
from .business_exception import (
    BusinessException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    InvalidTokenException,
    TokenRefreshFailedException,
    UserNotActiveException,
    DuplicateResourceException,
    ResourceNotFoundException,
    UserApprovalException,
    UserAlreadyActiveException,
    InsufficientPermissionException,
    TeamMismatchException,
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
    "InvalidTokenException",
    "TokenRefreshFailedException",
    "UserNotActiveException",
    "DuplicateResourceException",
    "ResourceNotFoundException",
    "UserApprovalException",
    "UserAlreadyActiveException",
    "InsufficientPermissionException",
    "TeamMismatchException",
    "InfrastructureException",
    "DatabaseException",
    "ExternalServiceException",
    "ErrorCode",
]
