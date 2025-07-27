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


class InvalidTokenException(BusinessException):
    """유효하지 않은 토큰 예외"""

    def __init__(self, message: Optional[str] = None, **kwargs):
        if not message:
            message = "유효하지 않은 토큰입니다."
        super().__init__(error_code=ErrorCode.INVALID_TOKEN, message=message, **kwargs)


class TokenRefreshFailedException(BusinessException):
    """토큰 갱신 실패 예외"""

    def __init__(self, message: Optional[str] = None, **kwargs):
        if not message:
            message = "토큰 갱신에 실패했습니다."
        super().__init__(
            error_code=ErrorCode.TOKEN_REFRESH_FAILED, message=message, **kwargs
        )


class UserNotActiveException(BusinessException):
    """비활성화된 사용자 예외"""

    def __init__(self, message: Optional[str] = None, **kwargs):
        if not message:
            message = "비활성화된 사용자입니다."
        super().__init__(
            error_code=ErrorCode.USER_NOT_ACTIVE, message=message, **kwargs
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


class UserApprovalException(BusinessException):
    """사용자 승인 관련 예외"""

    def __init__(
        self,
        message: Optional[str] = None,
        user_id: Optional[str] = None,
        approver_id: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        details.update({"user_id": user_id, "approver_id": approver_id})

        super().__init__(
            error_code=ErrorCode.USER_APPROVAL_FAILED,
            message=message,
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )


class UserAlreadyActiveException(BusinessException):
    """사용자가 이미 활성화된 예외"""

    def __init__(
        self,
        message: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        details.update({"user_id": user_id})

        if not message:
            message = "사용자가 이미 활성화되어 있습니다."

        super().__init__(
            error_code=ErrorCode.USER_ALREADY_ACTIVE,
            message=message,
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )


class InsufficientPermissionException(BusinessException):
    """권한 부족 예외"""

    def __init__(
        self,
        message: Optional[str] = None,
        required_role: Optional[str] = None,
        current_role: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        details.update({"required_role": required_role, "current_role": current_role})

        if not message:
            message = "권한이 부족합니다."
            if required_role:
                message += f" (필요한 권한: {required_role})"

        super().__init__(
            error_code=ErrorCode.INSUFFICIENT_PERMISSION,
            message=message,
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )


class TeamMismatchException(BusinessException):
    """팀 불일치 예외"""

    def __init__(
        self,
        message: Optional[str] = None,
        user_team_id: Optional[str] = None,
        approver_team_id: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        details.update(
            {"user_team_id": user_team_id, "approver_team_id": approver_team_id}
        )

        if not message:
            message = "팀이 일치하지 않습니다."

        super().__init__(
            error_code=ErrorCode.TEAM_MISMATCH,
            message=message,
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )


class UserRoleChangeException(BusinessException):
    """사용자 권한 변경 예외"""

    def __init__(
        self,
        message: Optional[str] = None,
        user_id: Optional[str] = None,
        new_role: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        details.update({"user_id": user_id, "new_role": new_role})

        if not message:
            message = "사용자 권한 변경에 실패했습니다."

        super().__init__(
            error_code=ErrorCode.USER_ROLE_CHANGE_FAILED,
            message=message,
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )


class LastOwnerProtectionException(BusinessException):
    """마지막 owner 보호 예외"""

    def __init__(
        self,
        message: Optional[str] = None,
        user_id: Optional[str] = None,
        team_id: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        details.update({"user_id": user_id, "team_id": team_id})

        if not message:
            message = "마지막 owner는 권한을 변경할 수 없습니다."

        super().__init__(
            error_code=ErrorCode.LAST_OWNER_PROTECTION,
            message=message,
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )


class InvalidRoleException(BusinessException):
    """유효하지 않은 권한 예외"""

    def __init__(
        self,
        message: Optional[str] = None,
        role: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        details.update({"role": role})

        if not message:
            message = "유효하지 않은 권한입니다."

        super().__init__(
            error_code=ErrorCode.INVALID_ROLE,
            message=message,
            details=details,
            **{k: v for k, v in kwargs.items() if k != "details"},
        )
