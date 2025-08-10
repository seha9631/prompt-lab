"""
Source Repository Interface
Source 데이터 접근 인터페이스
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.auth.domain.entity.source import Source


class SourceRepository(ABC):
    """Source Repository 추상 인터페이스"""

    @abstractmethod
    async def find_by_id(self, source_id: UUID) -> Optional[Source]:
        """ID로 source를 조회합니다."""
        pass

    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[Source]:
        """이름으로 source를 조회합니다."""
        pass

    @abstractmethod
    async def find_all(self) -> List[Source]:
        """모든 source를 조회합니다."""
        pass
