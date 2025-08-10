"""
Credential Repository 인터페이스
API 키 정보의 영속성을 관리하는 추상 인터페이스
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entity.credential import Credential


class CredentialRepository(ABC):
    """Credential Repository 추상 인터페이스"""

    @abstractmethod
    async def create(self, credential: Credential) -> Credential:
        """새로운 credential을 생성합니다."""
        pass

    @abstractmethod
    async def find_by_id(self, credential_id: UUID) -> Optional[Credential]:
        """ID로 credential을 조회합니다."""
        pass

    @abstractmethod
    async def find_by_team_id(self, team_id: UUID) -> List[Credential]:
        """팀 ID로 모든 credential을 조회합니다."""
        pass

    @abstractmethod
    async def find_by_team_and_name(
        self, team_id: UUID, name: str
    ) -> Optional[Credential]:
        """팀 ID와 이름으로 credential을 조회합니다."""
        pass

    @abstractmethod
    async def find_by_team_and_source(
        self, team_id: UUID, source_id: UUID
    ) -> List[Credential]:
        """팀 ID와 source ID로 credential을 조회합니다."""
        pass

    @abstractmethod
    async def update(self, credential: Credential) -> Credential:
        """credential을 업데이트합니다."""
        pass

    @abstractmethod
    async def delete(self, credential_id: UUID) -> bool:
        """credential을 삭제합니다."""
        pass

    @abstractmethod
    async def exists_by_team_and_name(self, team_id: UUID, name: str) -> bool:
        """팀 내에서 해당 이름의 credential이 존재하는지 확인합니다."""
        pass
