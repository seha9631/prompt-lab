"""
Credential Repository PostgreSQL 구현체
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth.domain.entity.credential import Credential
from src.auth.domain.repository.credential_repository import CredentialRepository
from src.shared.infra.models import CredentialModel


class CredentialRepositoryImpl(CredentialRepository):
    """PostgreSQL Credential Repository 구현체"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, credential: Credential) -> Credential:
        """새로운 credential을 생성합니다."""
        credential_model = CredentialModel(
            id=credential.id,
            team_id=credential.team_id,
            name=credential.name,
            source_id=credential.source_id,
            api_key=credential.api_key,
            created_at=credential.created_at,
            updated_at=credential.updated_at,
        )

        self.session.add(credential_model)
        await self.session.commit()
        await self.session.refresh(credential_model)

        return self._to_entity(credential_model)

    async def find_by_id(self, credential_id: UUID) -> Optional[Credential]:
        """ID로 credential을 조회합니다."""
        stmt = select(CredentialModel).where(CredentialModel.id == credential_id)
        result = await self.session.execute(stmt)
        credential_model = result.scalar_one_or_none()

        return self._to_entity(credential_model) if credential_model else None

    async def find_by_team_id(self, team_id: UUID) -> List[Credential]:
        """팀 ID로 모든 credential을 조회합니다."""
        stmt = select(CredentialModel).where(CredentialModel.team_id == team_id)
        result = await self.session.execute(stmt)
        credential_models = result.scalars().all()

        return [self._to_entity(model) for model in credential_models]

    async def find_by_team_and_name(
        self, team_id: UUID, name: str
    ) -> Optional[Credential]:
        """팀 ID와 이름으로 credential을 조회합니다."""
        stmt = select(CredentialModel).where(
            CredentialModel.team_id == team_id, CredentialModel.name == name
        )
        result = await self.session.execute(stmt)
        credential_model = result.scalar_one_or_none()

        return self._to_entity(credential_model) if credential_model else None

    async def find_by_team_and_source(
        self, team_id: UUID, source_id: UUID
    ) -> List[Credential]:
        """팀 ID와 source ID로 credential을 조회합니다."""
        stmt = select(CredentialModel).where(
            CredentialModel.team_id == team_id, CredentialModel.source_id == source_id
        )
        result = await self.session.execute(stmt)
        credential_models = result.scalars().all()

        return [self._to_entity(model) for model in credential_models]

    async def update(self, credential: Credential) -> Credential:
        """credential을 업데이트합니다."""
        stmt = (
            update(CredentialModel)
            .where(CredentialModel.id == credential.id)
            .values(
                name=credential.name,
                source_id=credential.source_id,
                api_key=credential.api_key,
                updated_at=credential.updated_at,
            )
        )

        await self.session.execute(stmt)
        await self.session.commit()

        # 업데이트된 데이터 조회
        return await self.find_by_id(credential.id)

    async def delete(self, credential_id: UUID) -> bool:
        """credential을 삭제합니다."""
        stmt = delete(CredentialModel).where(CredentialModel.id == credential_id)
        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount > 0

    async def exists_by_team_and_name(self, team_id: UUID, name: str) -> bool:
        """팀 내에서 해당 이름의 credential이 존재하는지 확인합니다."""
        stmt = select(CredentialModel).where(
            CredentialModel.team_id == team_id, CredentialModel.name == name
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def _to_entity(self, model: CredentialModel) -> Credential:
        """모델을 엔티티로 변환합니다."""
        return Credential(
            id=model.id,
            team_id=model.team_id,
            name=model.name,
            source_id=model.source_id,
            api_key=model.api_key,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
