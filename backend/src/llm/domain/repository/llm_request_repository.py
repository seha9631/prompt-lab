"""
LLM 요청 Repository Interface
LLM 요청 데이터 접근 인터페이스
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.llm.domain.entity.llm_request import LLMRequest


class LLMRequestRepository(ABC):
    """LLM 요청 Repository 추상 인터페이스"""

    @abstractmethod
    async def create(self, llm_request: LLMRequest) -> LLMRequest:
        """새로운 LLM 요청을 생성합니다."""
        pass

    @abstractmethod
    async def find_by_id(self, request_id: UUID) -> Optional[LLMRequest]:
        """ID로 LLM 요청을 조회합니다."""
        pass

    @abstractmethod
    async def find_by_team_id(self, team_id: UUID) -> List[LLMRequest]:
        """팀 ID로 모든 LLM 요청을 조회합니다."""
        pass

    @abstractmethod
    async def find_by_project_id_and_team_id(
        self, project_id: UUID, team_id: UUID
    ) -> List[LLMRequest]:
        """프로젝트 ID와 팀 ID로 LLM 요청을 조회합니다."""
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: UUID) -> List[LLMRequest]:
        """사용자 ID로 모든 LLM 요청을 조회합니다."""
        pass

    @abstractmethod
    async def update(self, llm_request: LLMRequest) -> LLMRequest:
        """LLM 요청을 업데이트합니다."""
        pass

    @abstractmethod
    async def delete(self, request_id: UUID) -> bool:
        """LLM 요청을 삭제합니다."""
        pass
