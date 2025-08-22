"""
SourceModel Repository Interface
SourceModel 데이터 접근 인터페이스
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.auth.domain.entity.source_model import SourceModel


class SourceModelRepository(ABC):
    """SourceModel Repository 추상 인터페이스"""

    @abstractmethod
    async def find_by_id(self, source_model_id: UUID) -> Optional[SourceModel]:
        """ID로 source_model을 조회합니다."""
        pass

    @abstractmethod
    async def find_by_source_id(self, source_id: UUID) -> List[SourceModel]:
        """source_id로 source_model들을 조회합니다."""
        pass

    @abstractmethod
    async def find_all(self) -> List[SourceModel]:
        """모든 source_model을 조회합니다."""
        pass
