"""
Team Repository Interface
팀 데이터 접근 인터페이스
"""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from src.auth.domain.entity.team import Team


class TeamRepository(ABC):
    """팀 리포지토리 추상화 인터페이스"""

    @abstractmethod
    async def save(self, team: Team) -> Team:
        """팀 저장"""
        pass

    @abstractmethod
    async def find_by_id(self, team_id: UUID) -> Optional[Team]:
        """ID로 팀 조회"""
        pass

    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[Team]:
        """이름으로 팀 조회"""
        pass

    @abstractmethod
    async def find_all_active(self) -> List[Team]:
        """활성화된 모든 팀 조회"""
        pass

    @abstractmethod
    async def update(self, team: Team) -> Team:
        """팀 정보 업데이트"""
        pass

    @abstractmethod
    async def delete(self, team_id: UUID) -> bool:
        """팀 삭제"""
        pass

    @abstractmethod
    async def exists_by_name(self, name: str) -> bool:
        """팀 이름 중복 확인"""
        pass
