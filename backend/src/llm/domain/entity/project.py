"""
Project 도메인 엔티티
"""

from datetime import datetime
from typing import Optional
from uuid import UUID


class Project:
    """프로젝트를 나타내는 도메인 엔티티"""

    def __init__(
        self,
        id: UUID,
        team_id: UUID,
        name: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.team_id = team_id
        self.name = name
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update_name(self, name: str) -> None:
        """프로젝트 이름을 업데이트합니다."""
        self.name = name
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"Project(id={self.id}, team_id={self.team_id}, name='{self.name}')"
