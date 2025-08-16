"""
Project Management Service
프로젝트 관리 서비스
"""

import uuid
from typing import List, Optional, Callable, Type
from uuid import UUID

from src.llm.domain.entity.project import Project
from src.llm.domain.repository.project_repository import ProjectRepository
from src.shared.exception import (
    ResourceNotFoundException,
    DuplicateResourceException,
    ValidationException,
)


class ProjectManagementService:
    """프로젝트 관리 서비스"""

    def __init__(
        self,
        project_repository_class: Type[ProjectRepository],
        get_session_func: Callable,
    ):
        self.project_repository_class = project_repository_class
        self.get_session = get_session_func

    async def create_project(self, team_id: UUID, name: str) -> Project:
        """프로젝트를 생성합니다."""
        async with self.get_session() as session:
            try:
                project_repo = self.project_repository_class(session)

                # 동일한 이름의 프로젝트가 있는지 확인
                existing_project = await project_repo.find_by_team_and_name(
                    team_id, name
                )
                if existing_project:
                    raise DuplicateResourceException(
                        resource_type="Project",
                        resource_id=name,
                        message=f"팀에 '{name}' 이름의 프로젝트가 이미 존재합니다",
                    )

                # 프로젝트 생성
                project = Project(
                    id=uuid.uuid4(),
                    team_id=team_id,
                    name=name,
                )

                created_project = await project_repo.create(project)
                await session.commit()
                return created_project

            except Exception as e:
                await session.rollback()
                raise e

    async def get_project(self, project_id: UUID, team_id: UUID) -> Optional[Project]:
        """프로젝트를 조회합니다."""
        async with self.get_session() as session:
            project_repo = self.project_repository_class(session)
            project = await project_repo.find_by_id(project_id)

            if project and str(project.team_id) == str(team_id):
                return project
            return None

    async def get_team_projects(self, team_id: UUID) -> List[Project]:
        """팀의 모든 프로젝트를 조회합니다."""
        async with self.get_session() as session:
            project_repo = self.project_repository_class(session)
            return await project_repo.find_by_team_id(team_id)

    async def update_project(
        self, project_id: UUID, team_id: UUID, name: str
    ) -> Optional[Project]:
        """프로젝트를 수정합니다."""
        async with self.get_session() as session:
            try:
                project_repo = self.project_repository_class(session)

                # 프로젝트 존재 확인 및 팀 소속 확인
                project = await project_repo.find_by_id(project_id)
                if not project:
                    return None

                if str(project.team_id) != str(team_id):
                    return None

                # 동일한 이름의 다른 프로젝트가 있는지 확인
                existing_project = await project_repo.find_by_team_and_name(
                    team_id, name
                )
                if existing_project and existing_project.id != project_id:
                    raise DuplicateResourceException(
                        resource_type="Project",
                        resource_id=name,
                        message=f"팀에 '{name}' 이름의 프로젝트가 이미 존재합니다",
                    )

                # 프로젝트 수정
                project.update_name(name)
                updated_project = await project_repo.update(project)
                await session.commit()
                return updated_project

            except Exception as e:
                await session.rollback()
                raise e

    async def delete_project(self, project_id: UUID, team_id: UUID) -> bool:
        """프로젝트를 삭제합니다."""
        async with self.get_session() as session:
            try:
                project_repo = self.project_repository_class(session)

                # 프로젝트 존재 확인 및 팀 소속 확인
                project = await project_repo.find_by_id(project_id)
                if not project:
                    return False

                if str(project.team_id) != str(team_id):
                    return False

                # 프로젝트 삭제
                success = await project_repo.delete(project_id)
                await session.commit()
                return success

            except Exception as e:
                await session.rollback()
                raise e
