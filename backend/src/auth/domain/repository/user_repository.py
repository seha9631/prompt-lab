from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from ..entity.user import User


class UserRepository(ABC):
    """사용자 리포지토리 추상화 인터페이스"""
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """사용자 저장"""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        """ID로 사용자 조회"""
        pass
    
    @abstractmethod
    async def find_by_app_id(self, app_id: str) -> Optional[User]:
        """앱 ID로 사용자 조회"""
        pass
    
    @abstractmethod
    async def find_by_team_id(self, team_id: UUID) -> List[User]:
        """팀 ID로 사용자 목록 조회"""
        pass
    
    @abstractmethod
    async def find_team_owner(self, team_id: UUID) -> Optional[User]:
        """팀 오너 조회"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """사용자 정보 업데이트"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """사용자 삭제"""
        pass
    
    @abstractmethod
    async def exists_by_app_id(self, app_id: str) -> bool:
        """앱 ID 중복 확인"""
        pass
    
    @abstractmethod
    async def count_by_team_id(self, team_id: UUID) -> int:
        """팀의 사용자 수 조회"""
        pass 