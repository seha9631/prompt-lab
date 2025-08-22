"""
Project Management UseCase
프로젝트 관리 유스케이스
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from src.shared.response.base_response import BaseResponse
from src.llm.application.service.project_management_service import (
    ProjectManagementService,
)
from src.llm.domain.entity.project import Project


class CreateProjectRequest:
    """프로젝트 생성 요청 모델"""

    def __init__(self, name: str):
        self.name = name


class ProjectResponse(BaseModel):
    """프로젝트 응답 모델"""

    id: str
    team_id: str
    name: str
    created_at: str
    updated_at: str


class UpdateProjectRequest:
    """프로젝트 수정 요청 모델"""

    def __init__(self, name: str):
        self.name = name


class ProjectManagementUseCase:
    """프로젝트 관리 유스케이스"""

    def __init__(self, project_management_service: ProjectManagementService):
        self.project_management_service = project_management_service

    async def create_project(
        self, team_id: UUID, request: CreateProjectRequest
    ) -> BaseResponse[ProjectResponse]:
        """프로젝트를 생성합니다."""
        try:
            project = await self.project_management_service.create_project(
                team_id=team_id,
                name=request.name,
            )

            response = ProjectResponse(
                id=str(project.id),
                team_id=str(project.team_id),
                name=project.name,
                created_at=project.created_at.isoformat(),
                updated_at=project.updated_at.isoformat(),
            )

            return BaseResponse.success_response(
                data=response,
                message="프로젝트가 성공적으로 생성되었습니다.",
            )

        except Exception as e:
            return BaseResponse.error_response(
                message="프로젝트 생성 중 오류가 발생했습니다.",
                error=str(e),
            )

    async def get_project(
        self, project_id: UUID, team_id: UUID
    ) -> BaseResponse[ProjectResponse]:
        """프로젝트를 조회합니다."""
        try:
            project = await self.project_management_service.get_project(
                project_id, team_id
            )

            if not project:
                return BaseResponse.error_response(
                    message="프로젝트를 찾을 수 없습니다.",
                    error="Project not found",
                )

            response = ProjectResponse(
                id=str(project.id),
                team_id=str(project.team_id),
                name=project.name,
                created_at=project.created_at.isoformat(),
                updated_at=project.updated_at.isoformat(),
            )

            return BaseResponse.success_response(
                data=response,
                message="프로젝트를 성공적으로 조회했습니다.",
            )

        except Exception as e:
            return BaseResponse.error_response(
                message="프로젝트 조회 중 오류가 발생했습니다.",
                error=str(e),
            )

    async def get_team_projects(
        self, team_id: UUID
    ) -> BaseResponse[List[ProjectResponse]]:
        """팀의 모든 프로젝트를 조회합니다."""
        try:
            projects = await self.project_management_service.get_team_projects(team_id)

            responses = [
                ProjectResponse(
                    id=str(project.id),
                    team_id=str(project.team_id),
                    name=project.name,
                    created_at=project.created_at.isoformat(),
                    updated_at=project.updated_at.isoformat(),
                )
                for project in projects
            ]

            return BaseResponse.success_response(
                data=responses,
                message="팀의 프로젝트 목록을 성공적으로 조회했습니다.",
            )

        except Exception as e:
            return BaseResponse.error_response(
                message="팀 프로젝트 조회 중 오류가 발생했습니다.",
                error=str(e),
            )

    async def update_project(
        self, project_id: UUID, team_id: UUID, request: UpdateProjectRequest
    ) -> BaseResponse[ProjectResponse]:
        """프로젝트를 수정합니다."""
        try:
            project = await self.project_management_service.update_project(
                project_id, team_id, request.name
            )

            if not project:
                return BaseResponse.error_response(
                    message="프로젝트를 찾을 수 없습니다.",
                    error="Project not found",
                )

            response = ProjectResponse(
                id=str(project.id),
                team_id=str(project.team_id),
                name=project.name,
                created_at=project.created_at.isoformat(),
                updated_at=project.updated_at.isoformat(),
            )

            return BaseResponse.success_response(
                data=response,
                message="프로젝트가 성공적으로 수정되었습니다.",
            )

        except Exception as e:
            return BaseResponse.error_response(
                message="프로젝트 수정 중 오류가 발생했습니다.",
                error=str(e),
            )

    async def delete_project(
        self, project_id: UUID, team_id: UUID
    ) -> BaseResponse[dict]:
        """프로젝트를 삭제합니다."""
        try:
            success = await self.project_management_service.delete_project(
                project_id, team_id
            )

            if not success:
                return BaseResponse.error_response(
                    message="프로젝트를 찾을 수 없거나 삭제할 권한이 없습니다.",
                    error="Project not found or no permission",
                )

            return BaseResponse.success_response(
                data={"deleted": True},
                message="프로젝트가 성공적으로 삭제되었습니다.",
            )

        except Exception as e:
            return BaseResponse.error_response(
                message="프로젝트 삭제 중 오류가 발생했습니다.",
                error=str(e),
            )
