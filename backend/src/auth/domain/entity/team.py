from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional


class Team:
    """팀 엔티티"""
    
    def __init__(
        self,
        name: str,
        payment: str = "free",
        is_active: bool = True,
        id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id or uuid4()
        self.name = name
        self.is_active = is_active
        self.payment = payment
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def update_name(self, name: str) -> None:
        """팀 이름 업데이트"""
        self.name = name
        self.updated_at = datetime.utcnow()
    
    def update_payment(self, payment: str) -> None:
        """결제 플랜 업데이트"""
        self.payment = payment
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """팀 비활성화"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """팀 활성화"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Team):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id) 