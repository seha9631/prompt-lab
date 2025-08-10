"""
PostgreSQL Source Repository 구현체
SQLAlchemy를 사용한 source 데이터 영속성 구현
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.entity.source import Source
from ....domain.repository.source_repository import SourceRepository
from src.shared.infra.models import SourceModel


class SourceRepositoryImpl(SourceRepository):
    """PostgreSQL Source Repository 구현체"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, source_id: UUID) -> Optional[Source]:
        """ID로 source를 조회합니다."""
        stmt = select(SourceModel).where(SourceModel.id == source_id)
        result = await self.session.execute(stmt)
        source_model = result.scalar_one_or_none()

        return self._to_entity(source_model) if source_model else None

    async def find_by_name(self, name: str) -> Optional[Source]:
        """이름으로 source를 조회합니다."""
        stmt = select(SourceModel).where(SourceModel.name == name)
        result = await self.session.execute(stmt)
        source_model = result.scalar_one_or_none()

        return self._to_entity(source_model) if source_model else None

    async def find_all(self) -> List[Source]:
        """모든 source를 조회합니다."""
        stmt = select(SourceModel)
        result = await self.session.execute(stmt)
        source_models = result.scalars().all()

        return [self._to_entity(model) for model in source_models]

    def _to_entity(self, model: SourceModel) -> Source:
        """모델을 엔티티로 변환합니다."""
        return Source(id=model.id, name=model.name, created_at=model.created_at)
