"""
Source 도메인 엔티티
소스 정보를 관리하는 도메인 객체
"""

from datetime import datetime
from uuid import UUID


class Source:
    """소스 정보를 나타내는 도메인 엔티티"""

    def __init__(self, id: UUID, name: str, created_at: datetime):
        self.id = id
        self.name = name
        self.created_at = created_at

    def __repr__(self) -> str:
        return f"Source(id={self.id}, name='{self.name}')"
