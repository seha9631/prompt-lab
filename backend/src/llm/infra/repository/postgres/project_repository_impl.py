"""
Project Repository PostgreSQL 구현체
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.llm.domain.entity.project import Project
from src.llm.domain.repository.project_repository import ProjectRepository
from src.shared.infra.models import ProjectModel


class ProjectRepositoryImpl(ProjectRepository):
    """PostgreSQL Project Repository 구현체"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, project: Project) -> Project:
        """새로운 project를 생성합니다."""
        project_model = ProjectModel(
            id=project.id,
            team_id=project.team_id,
            name=project.name,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )

        self.session.add(project_model)
        await self.session.commit()
        await self.session.refresh(project_model)

        return self._to_entity(project_model)

    async def find_by_id(self, project_id: UUID) -> Optional[Project]:
        """ID로 project를 조회합니다."""
        stmt = select(ProjectModel).where(ProjectModel.id == project_id)
        result = await self.session.execute(stmt)
        project_model = result.scalar_one_or_none()

        return self._to_entity(project_model) if project_model else None

    async def find_by_team_id(self, team_id: UUID) -> List[Project]:
        """팀 ID로 모든 project를 조회합니다."""
        stmt = (
            select(ProjectModel)
            .where(ProjectModel.team_id == team_id)
            .order_by(ProjectModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        project_models = result.scalars().all()

        return [self._to_entity(model) for model in project_models]

    async def find_by_team_and_name(
        self, team_id: UUID, name: str
    ) -> Optional[Project]:
        """팀 ID와 이름으로 project를 조회합니다."""
        stmt = select(ProjectModel).where(
            ProjectModel.team_id == team_id, ProjectModel.name == name
        )
        result = await self.session.execute(stmt)
        project_model = result.scalar_one_or_none()

        return self._to_entity(project_model) if project_model else None

    async def update(self, project: Project) -> Project:
        """project를 업데이트합니다."""
        stmt = (
            update(ProjectModel)
            .where(ProjectModel.id == project.id)
            .values(
                name=project.name,
                updated_at=project.updated_at,
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

        return project

    async def delete(self, project_id: UUID) -> bool:
        """project를 삭제합니다."""
        stmt = delete(ProjectModel).where(ProjectModel.id == project_id)
        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount > 0

    def _to_entity(self, model: ProjectModel) -> Project:
        """SQLAlchemy 모델을 도메인 엔티티로 변환합니다."""
        return Project(
            id=model.id,
            team_id=model.team_id,
            name=model.name,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
