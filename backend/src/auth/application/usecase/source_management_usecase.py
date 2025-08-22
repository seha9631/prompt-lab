"""
Source Management UseCase
소스 및 소스 모델 조회 유스케이스
"""

from typing import List
from uuid import UUID

from src.auth.domain.entity.source import Source
from src.auth.domain.entity.source_model import SourceModel
from src.auth.domain.repository.source_repository import SourceRepository
from src.auth.domain.repository.source_model_repository import SourceModelRepository


class SourceManagementUseCase:
    """소스 및 소스 모델 조회 유스케이스"""

    def __init__(
        self,
        source_repository_class,
        source_model_repository_class,
        get_session_func,
    ):
        self.source_repository_class = source_repository_class
        self.source_model_repository_class = source_model_repository_class
        self.get_session_func = get_session_func

    async def _get_repositories(self):
        """새로운 세션으로 repository들을 생성합니다."""
        session = self.get_session_func()
        return (
            self.source_repository_class(session),
            self.source_model_repository_class(session),
        ), session

    async def get_all_sources(self) -> List[Source]:
        """모든 source를 조회합니다."""
        (source_repo, _), session = await self._get_repositories()

        try:
            return await source_repo.find_all()
        finally:
            await session.close()

    async def get_source_by_id(self, source_id: UUID) -> Source:
        """ID로 source를 조회합니다."""
        (source_repo, _), session = await self._get_repositories()

        try:
            source = await source_repo.find_by_id(source_id)
            if not source:
                raise ValueError(f"Source with id {source_id} not found")
            return source
        finally:
            await session.close()

    async def get_all_source_models(self) -> List[SourceModel]:
        """모든 source_model을 조회합니다."""
        (_, source_model_repo), session = await self._get_repositories()

        try:
            return await source_model_repo.find_all()
        finally:
            await session.close()

    async def get_source_models_by_source_id(
        self, source_id: UUID
    ) -> List[SourceModel]:
        """특정 source의 모든 source_model을 조회합니다."""
        (source_repo, source_model_repo), session = await self._get_repositories()

        try:
            # source 존재 확인
            source = await source_repo.find_by_id(source_id)
            if not source:
                raise ValueError(f"Source with id {source_id} not found")

            return await source_model_repo.find_by_source_id(source_id)
        finally:
            await session.close()
