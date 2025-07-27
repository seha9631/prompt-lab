from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional


class User:
    """사용자 엔티티"""
    
    def __init__(
        self,
        name: str,
        app_id: str,
        app_password: str,
        team_id: UUID,
        role: str = "user",
        is_active: bool = True,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id or uuid4()
        self.name = name
        self.is_active = is_active
        self.app_id = app_id
        self.app_password = app_password
        self.role = role
        self.team_id = team_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def update_name(self, name: str) -> None:
        """사용자 이름 업데이트"""
        self.name = name
        self.updated_at = datetime.utcnow()
    
    def update_password(self, new_password: str) -> None:
        """비밀번호 업데이트"""
        self.app_password = new_password
        self.updated_at = datetime.utcnow()
    
    def change_role(self, role: str) -> None:
        """권한 변경"""
        if role not in ["user", "admin", "owner"]:
            raise ValueError("Invalid role. Must be 'user', 'admin', or 'owner'")
        self.role = role
        self.updated_at = datetime.utcnow()
    
    def change_team(self, team_id: UUID) -> None:
        """팀 변경"""
        self.team_id = team_id
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """사용자 비활성화"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """사용자 활성화"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def is_owner(self) -> bool:
        """오너 권한 확인"""
        return self.role == "owner"
    
    def is_admin(self) -> bool:
        """관리자 권한 확인"""
        return self.role in ["admin", "owner"]
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id) 