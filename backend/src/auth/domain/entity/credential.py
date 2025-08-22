"""
Credential 도메인 엔티티
API 키 정보를 관리하는 도메인 객체
"""

from datetime import datetime
from typing import Optional
from uuid import UUID


class Credential:
    """API 키 정보를 나타내는 도메인 엔티티"""

    def __init__(
        self,
        id: UUID,
        team_id: UUID,
        name: str,
        source_id: UUID,
        api_key: str,
        created_at: datetime,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.team_id = team_id
        self.name = name
        self.source_id = source_id
        self.api_key = api_key
        self.created_at = created_at
        self.updated_at = updated_at or created_at

    def update_name(self, name: str) -> None:
        """credential 이름을 업데이트합니다."""
        self.name = name
        self.updated_at = datetime.utcnow()

    def update_api_key(self, api_key: str) -> None:
        """API 키를 업데이트합니다."""
        self.api_key = api_key
        self.updated_at = datetime.utcnow()

    def update_source(self, source_id: UUID) -> None:
        """source를 업데이트합니다."""
        self.source_id = source_id
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"Credential(id={self.id}, team_id={self.team_id}, name='{self.name}', source_id={self.source_id})"
