"""
SourceModel 도메인 엔티티
소스 모델 정보를 관리하는 도메인 객체
"""

from datetime import datetime
from uuid import UUID


class SourceModel:
    """소스 모델 정보를 나타내는 도메인 엔티티"""

    def __init__(
        self,
        id: UUID,
        name: str,
        description: str,
        source_id: UUID,
        created_at: datetime,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.source_id = source_id
        self.created_at = created_at

    def __repr__(self) -> str:
        return (
            f"SourceModel(id={self.id}, name='{self.name}', source_id={self.source_id})"
        )
