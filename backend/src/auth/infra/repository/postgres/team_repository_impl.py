from uuid import UUID
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import IntegrityError

from ....domain.entity.team import Team
from ....domain.repository.team_repository import TeamRepository
from .....shared.infra.models import TeamModel


class TeamRepositoryImpl(TeamRepository):
    """PostgreSQL 기반 팀 리포지토리 구현체"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, team: Team) -> Team:
        """팀 저장"""
        try:
            team_model = TeamModel(
                id=team.id,
                name=team.name,
                is_active=team.is_active,
                payment=team.payment,
                created_at=team.created_at,
                updated_at=team.updated_at
            )
            
            self.session.add(team_model)
            await self.session.flush()  # 데이터베이스에 변경사항 반영 (commit은 상위에서)
            
            return self._model_to_entity(team_model)
            
        except IntegrityError:
            await self.session.rollback()
            raise ValueError(f"Team with name '{team.name}' already exists")
    
    async def find_by_id(self, team_id: UUID) -> Optional[Team]:
        """ID로 팀 조회"""
        stmt = select(TeamModel).where(TeamModel.id == team_id)
        result = await self.session.execute(stmt)
        team_model = result.scalar_one_or_none()
        
        if team_model is None:
            return None
        
        return self._model_to_entity(team_model)
    
    async def find_by_name(self, name: str) -> Optional[Team]:
        """이름으로 팀 조회"""
        stmt = select(TeamModel).where(TeamModel.name == name)
        result = await self.session.execute(stmt)
        team_model = result.scalar_one_or_none()
        
        if team_model is None:
            return None
        
        return self._model_to_entity(team_model)
    
    async def find_all_active(self) -> List[Team]:
        """활성화된 모든 팀 조회"""
        stmt = select(TeamModel).where(TeamModel.is_active == True).order_by(TeamModel.created_at.desc())
        result = await self.session.execute(stmt)
        team_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in team_models]
    
    async def update(self, team: Team) -> Team:
        """팀 정보 업데이트"""
        try:
            stmt = (
                update(TeamModel)
                .where(TeamModel.id == team.id)
                .values(
                    name=team.name,
                    is_active=team.is_active,
                    payment=team.payment,
                    updated_at=team.updated_at
                )
                .returning(TeamModel)
            )
            
            result = await self.session.execute(stmt)
            updated_model = result.scalar_one()
            
            return self._model_to_entity(updated_model)
            
        except IntegrityError:
            await self.session.rollback()
            raise ValueError(f"Team with name '{team.name}' already exists")
    
    async def delete(self, team_id: UUID) -> bool:
        """팀 삭제"""
        stmt = delete(TeamModel).where(TeamModel.id == team_id)
        result = await self.session.execute(stmt)
        
        return result.rowcount > 0
    
    async def exists_by_name(self, name: str) -> bool:
        """팀 이름 중복 확인"""
        stmt = select(func.count(TeamModel.id)).where(TeamModel.name == name)
        result = await self.session.execute(stmt)
        count = result.scalar()
        
        return count > 0
    
    def _model_to_entity(self, model: TeamModel) -> Team:
        """SQLAlchemy 모델을 도메인 엔티티로 변환"""
        return Team(
            id=model.id,
            name=model.name,
            is_active=model.is_active,
            payment=model.payment,
            created_at=model.created_at,
            updated_at=model.updated_at
        ) 