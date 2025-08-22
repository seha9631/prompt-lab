"""
SourceModel Repository PostgreSQL 구현체
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.domain.entity.source_model import SourceModel
from src.auth.domain.repository.source_model_repository import SourceModelRepository
from src.shared.infra.models import SourceModelModel


class SourceModelRepositoryImpl(SourceModelRepository):
    """PostgreSQL SourceModel Repository 구현체"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, source_model_id: UUID) -> Optional[SourceModel]:
        """ID로 source_model을 조회합니다."""
        stmt = select(SourceModelModel).where(SourceModelModel.id == source_model_id)
        result = await self.session.execute(stmt)
        source_model_model = result.scalar_one_or_none()

        return self._to_entity(source_model_model) if source_model_model else None

    async def find_by_source_id(self, source_id: UUID) -> List[SourceModel]:
        """source_id로 source_model들을 조회합니다."""
        stmt = select(SourceModelModel).where(SourceModelModel.source_id == source_id)
        result = await self.session.execute(stmt)
        source_model_models = result.scalars().all()

        return [self._to_entity(model) for model in source_model_models]

    async def find_all(self) -> List[SourceModel]:
        """모든 source_model을 조회합니다."""
        stmt = select(SourceModelModel)
        result = await self.session.execute(stmt)
        source_model_models = result.scalars().all()

        return [self._to_entity(model) for model in source_model_models]

    def _to_entity(self, model: SourceModelModel) -> SourceModel:
        """모델을 엔티티로 변환합니다."""
        return SourceModel(
            id=model.id,
            name=model.name,
            description=model.description or "",
            source_id=model.source_id,
            created_at=model.created_at,
        )
