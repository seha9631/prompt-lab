"""
Project Router
프로젝트 관리 API 엔드포인트
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.shared.injector.container import app_container
from src.shared.security.dependencies import get_current_user
from src.shared.security.jwt_handler import TokenData
from src.shared.response.base_response import BaseResponse
from src.shared.logging import get_logger

from src.llm.application.usecase.project_management_usecase import (
    CreateProjectRequest,
    ProjectResponse,
    UpdateProjectRequest,
    ProjectManagementUseCase,
)

router = APIRouter(prefix="/projects", tags=["projects"])
logger = get_logger(__name__)


# Request/Response Models
class CreateProjectModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="프로젝트 이름")


class UpdateProjectModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="프로젝트 이름")


# Dependency
def get_project_usecase() -> ProjectManagementUseCase:
    """프로젝트 관리 UseCase 의존성"""
    return app_container.get_project_management_usecase()


@router.post("", response_model=BaseResponse[ProjectResponse])
async def create_project(
    request: CreateProjectModel,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_project_usecase),
):
    """프로젝트를 생성합니다."""
    try:
        project_request = CreateProjectRequest(name=request.name)

        response = await usecase.create_project(
            team_id=current_user.team_id,
            request=project_request,
        )

        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": response.message, "error": response.error},
            )

        logger.info(
            "프로젝트 생성",
            extra={
                "user_id": current_user.user_id,
                "team_id": current_user.team_id,
                "project_id": response.data.id,
                "project_name": request.name,
            },
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"프로젝트 생성 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로젝트 생성 중 오류가 발생했습니다.",
        )


@router.get("", response_model=BaseResponse[List[ProjectResponse]])
async def get_team_projects(
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_project_usecase),
):
    """팀의 모든 프로젝트를 조회합니다."""
    try:
        response = await usecase.get_team_projects(team_id=current_user.team_id)

        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": response.message, "error": response.error},
            )

        logger.info(
            "팀 프로젝트 조회",
            extra={
                "user_id": current_user.user_id,
                "team_id": current_user.team_id,
                "project_count": len(response.data),
            },
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팀 프로젝트 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="팀 프로젝트 조회 중 오류가 발생했습니다.",
        )


@router.get("/{project_id}", response_model=BaseResponse[ProjectResponse])
async def get_project(
    project_id: str,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_project_usecase),
):
    """프로젝트를 조회합니다."""
    try:
        response = await usecase.get_project(
            project_id=UUID(project_id),
            team_id=current_user.team_id,
        )

        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": response.message, "error": response.error},
            )

        logger.info(
            "프로젝트 조회",
            extra={
                "user_id": current_user.user_id,
                "team_id": current_user.team_id,
                "project_id": project_id,
            },
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"프로젝트 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로젝트 조회 중 오류가 발생했습니다.",
        )


@router.put("/{project_id}", response_model=BaseResponse[ProjectResponse])
async def update_project(
    project_id: str,
    request: UpdateProjectModel,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_project_usecase),
):
    """프로젝트를 수정합니다."""
    try:
        project_request = UpdateProjectRequest(name=request.name)

        response = await usecase.update_project(
            project_id=UUID(project_id),
            team_id=current_user.team_id,
            request=project_request,
        )

        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": response.message, "error": response.error},
            )

        logger.info(
            "프로젝트 수정",
            extra={
                "user_id": current_user.user_id,
                "team_id": current_user.team_id,
                "project_id": project_id,
                "new_name": request.name,
            },
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"프로젝트 수정 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로젝트 수정 중 오류가 발생했습니다.",
        )


@router.delete("/{project_id}", response_model=BaseResponse[dict])
async def delete_project(
    project_id: str,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_project_usecase),
):
    """프로젝트를 삭제합니다."""
    try:
        response = await usecase.delete_project(
            project_id=UUID(project_id),
            team_id=current_user.team_id,
        )

        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": response.message, "error": response.error},
            )

        logger.info(
            "프로젝트 삭제",
            extra={
                "user_id": current_user.user_id,
                "team_id": current_user.team_id,
                "deleted_project_id": project_id,
            },
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"프로젝트 삭제 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로젝트 삭제 중 오류가 발생했습니다.",
        )
