from enum import Enum
from typing import Any


class UserRoleType(Enum):
    """사용자 권한 타입"""
    USER = "user"
    ADMIN = "admin"
    OWNER = "owner"


class UserRole:
    """사용자 권한 값 객체"""
    
    def __init__(self, role: str):
        try:
            self.role_type = UserRoleType(role.lower())
        except ValueError:
            raise ValueError(f"Invalid role: {role}. Must be one of: user, admin, owner")
    
    @property
    def value(self) -> str:
        return self.role_type.value
    
    def is_user(self) -> bool:
        return self.role_type == UserRoleType.USER
    
    def is_admin(self) -> bool:
        return self.role_type == UserRoleType.ADMIN
    
    def is_owner(self) -> bool:
        return self.role_type == UserRoleType.OWNER
    
    def has_admin_privileges(self) -> bool:
        """관리자 권한이 있는지 확인 (admin 또는 owner)"""
        return self.role_type in [UserRoleType.ADMIN, UserRoleType.OWNER]
    
    def can_manage_team(self) -> bool:
        """팀 관리 권한이 있는지 확인 (owner만 가능)"""
        return self.role_type == UserRoleType.OWNER
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, UserRole):
            return False
        return self.role_type == other.role_type
    
    def __hash__(self) -> int:
        return hash(self.role_type) 