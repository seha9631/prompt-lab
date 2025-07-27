from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import IntegrityError

from ....domain.entity.user import User
from ....domain.repository.user_repository import UserRepository
from .....shared.infra.models import UserModel


class UserRepositoryImpl(UserRepository):
    """PostgreSQL 기반 사용자 리포지토리 구현체"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, user: User) -> User:
        """사용자 저장"""
        try:
            user_model = UserModel(
                id=user.id,
                name=user.name,
                is_active=user.is_active,
                app_id=user.app_id,
                app_password=user.app_password,
                role=user.role,
                team_id=user.team_id,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
            self.session.add(user_model)
            await self.session.flush()  # 데이터베이스에 변경사항 반영
            
            return self._model_to_entity(user_model)
            
        except IntegrityError:
            await self.session.rollback()
            raise ValueError(f"User with app_id '{user.app_id}' already exists")
    
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        """ID로 사용자 조회"""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model is None:
            return None
        
        return self._model_to_entity(user_model)
    
    async def find_by_app_id(self, app_id: str) -> Optional[User]:
        """앱 ID로 사용자 조회"""
        stmt = select(UserModel).where(UserModel.app_id == app_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model is None:
            return None
        
        return self._model_to_entity(user_model)
    
    async def find_by_team_id(self, team_id: UUID) -> List[User]:
        """팀 ID로 사용자 목록 조회"""
        stmt = select(UserModel).where(UserModel.team_id == team_id).order_by(UserModel.created_at.desc())
        result = await self.session.execute(stmt)
        user_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in user_models]
    
    async def find_team_owner(self, team_id: UUID) -> Optional[User]:
        """팀 오너 조회"""
        stmt = select(UserModel).where(
            UserModel.team_id == team_id,
            UserModel.role == "owner"
        )
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model is None:
            return None
        
        return self._model_to_entity(user_model)
    
    async def update(self, user: User) -> User:
        """사용자 정보 업데이트"""
        try:
            stmt = (
                update(UserModel)
                .where(UserModel.id == user.id)
                .values(
                    name=user.name,
                    is_active=user.is_active,
                    app_id=user.app_id,
                    app_password=user.app_password,
                    role=user.role,
                    team_id=user.team_id,
                    updated_at=user.updated_at
                )
                .returning(UserModel)
            )
            
            result = await self.session.execute(stmt)
            updated_model = result.scalar_one()
            
            return self._model_to_entity(updated_model)
            
        except IntegrityError:
            await self.session.rollback()
            raise ValueError(f"User with app_id '{user.app_id}' already exists")
    
    async def delete(self, user_id: UUID) -> bool:
        """사용자 삭제"""
        stmt = delete(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        
        return result.rowcount > 0
    
    async def exists_by_app_id(self, app_id: str) -> bool:
        """앱 ID 중복 확인"""
        stmt = select(func.count(UserModel.id)).where(UserModel.app_id == app_id)
        result = await self.session.execute(stmt)
        count = result.scalar()
        
        return count > 0
    
    async def count_by_team_id(self, team_id: UUID) -> int:
        """팀의 사용자 수 조회"""
        stmt = select(func.count(UserModel.id)).where(UserModel.team_id == team_id)
        result = await self.session.execute(stmt)
        count = result.scalar()
        
        return count
    
    def _model_to_entity(self, model: UserModel) -> User:
        """SQLAlchemy 모델을 도메인 엔티티로 변환"""
        return User(
            id=model.id,
            name=model.name,
            is_active=model.is_active,
            app_id=model.app_id,
            app_password=model.app_password,
            role=model.role,
            team_id=model.team_id,
            created_at=model.created_at,
            updated_at=model.updated_at
        ) 