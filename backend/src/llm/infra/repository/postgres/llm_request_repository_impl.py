"""
LLM 요청 Repository PostgreSQL 구현체
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.llm.domain.entity.llm_request import LLMRequest
from src.llm.domain.repository.llm_request_repository import LLMRequestRepository
from src.shared.infra.models import LLMRequestModel


class LLMRequestRepositoryImpl(LLMRequestRepository):
    """PostgreSQL LLM 요청 Repository 구현체"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, llm_request: LLMRequest) -> LLMRequest:
        """새로운 LLM 요청을 생성합니다."""
        llm_request_model = LLMRequestModel(
            id=llm_request.id,
            team_id=llm_request.team_id,
            user_id=llm_request.user_id,
            project_id=llm_request.project_id,
            system_prompt=llm_request.system_prompt,
            question=llm_request.question,
            model_name=llm_request.model_name,
            file_paths=llm_request.file_paths,
            status=llm_request.status,
            result=llm_request.result,
            error_message=llm_request.error_message,
            created_at=llm_request.created_at,
            updated_at=llm_request.updated_at,
        )

        self.session.add(llm_request_model)
        await self.session.commit()
        await self.session.refresh(llm_request_model)

        return self._to_entity(llm_request_model)

    async def find_by_id(self, request_id: UUID) -> Optional[LLMRequest]:
        """ID로 LLM 요청을 조회합니다."""
        stmt = select(LLMRequestModel).where(LLMRequestModel.id == request_id)
        result = await self.session.execute(stmt)
        llm_request_model = result.scalar_one_or_none()

        return self._to_entity(llm_request_model) if llm_request_model else None

    async def find_by_team_id(self, team_id: UUID) -> List[LLMRequest]:
        """팀 ID로 모든 LLM 요청을 조회합니다."""
        stmt = (
            select(LLMRequestModel)
            .where(LLMRequestModel.team_id == team_id)
            .order_by(LLMRequestModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        llm_request_models = result.scalars().all()

        return [self._to_entity(model) for model in llm_request_models]

    async def find_by_project_id_and_team_id(
        self, project_id: UUID, team_id: UUID
    ) -> List[LLMRequest]:
        """프로젝트 ID와 팀 ID로 LLM 요청을 조회합니다."""
        stmt = (
            select(LLMRequestModel)
            .where(
                LLMRequestModel.project_id == project_id,
                LLMRequestModel.team_id == team_id,
            )
            .order_by(LLMRequestModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        llm_request_models = result.scalars().all()

        return [self._to_entity(model) for model in llm_request_models]

    async def find_by_user_id(self, user_id: UUID) -> List[LLMRequest]:
        """사용자 ID로 모든 LLM 요청을 조회합니다."""
        stmt = (
            select(LLMRequestModel)
            .where(LLMRequestModel.user_id == user_id)
            .order_by(LLMRequestModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        llm_request_models = result.scalars().all()

        return [self._to_entity(model) for model in llm_request_models]

    async def update(self, llm_request: LLMRequest) -> LLMRequest:
        """LLM 요청을 업데이트합니다."""
        stmt = (
            update(LLMRequestModel)
            .where(LLMRequestModel.id == llm_request.id)
            .values(
                system_prompt=llm_request.system_prompt,
                question=llm_request.question,
                model_name=llm_request.model_name,
                file_paths=llm_request.file_paths,
                status=llm_request.status,
                result=llm_request.result,
                error_message=llm_request.error_message,
                updated_at=llm_request.updated_at,
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

        return llm_request

    async def delete(self, request_id: UUID) -> bool:
        """LLM 요청을 삭제합니다."""
        stmt = delete(LLMRequestModel).where(LLMRequestModel.id == request_id)
        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount > 0

    def _to_entity(self, model: LLMRequestModel) -> LLMRequest:
        """SQLAlchemy 모델을 도메인 엔티티로 변환합니다."""
        return LLMRequest(
            id=model.id,
            team_id=model.team_id,
            user_id=model.user_id,
            project_id=model.project_id,
            system_prompt=model.system_prompt,
            question=model.question,
            model_name=model.model_name,
            file_paths=model.file_paths,
            status=model.status,
            result=model.result,
            error_message=model.error_message,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
