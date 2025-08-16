"""
Project Repository Interface
Project 데이터 접근 인터페이스
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.llm.domain.entity.project import Project


class ProjectRepository(ABC):
    """Project Repository 추상 인터페이스"""

    @abstractmethod
    async def create(self, project: Project) -> Project:
        """새로운 project를 생성합니다."""
        pass

    @abstractmethod
    async def find_by_id(self, project_id: UUID) -> Optional[Project]:
        """ID로 project를 조회합니다."""
        pass

    @abstractmethod
    async def find_by_team_id(self, team_id: UUID) -> List[Project]:
        """팀 ID로 모든 project를 조회합니다."""
        pass

    @abstractmethod
    async def find_by_team_and_name(
        self, team_id: UUID, name: str
    ) -> Optional[Project]:
        """팀 ID와 이름으로 project를 조회합니다."""
        pass

    @abstractmethod
    async def update(self, project: Project) -> Project:
        """project를 업데이트합니다."""
        pass

    @abstractmethod
    async def delete(self, project_id: UUID) -> bool:
        """project를 삭제합니다."""
        pass
