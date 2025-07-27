from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.shared.injector.container import app_container
from src.auth.application.usecase.create_user_usecase import (
    CreateUserWithTeamRequest,
    CreateUserForTeamRequest,
    CreateUserUseCase,
)

auth_router = APIRouter(tags=["auth"])


class CreateUserForTeamBody(BaseModel):
    """기존 팀에 사용자 추가 요청 Body (team_id 제외)"""

    name: str = Field(..., min_length=2, max_length=50, description="사용자 이름")
    app_id: str = Field(..., min_length=3, max_length=50, description="앱 ID")
    app_password: str = Field(..., min_length=8, description="앱 비밀번호")


@auth_router.post("/users")
async def create_user_with_team(request: CreateUserWithTeamRequest):
    """새 팀과 함께 사용자 생성 (REST: POST /users with team data)"""
    try:
        usecase: CreateUserUseCase = app_container.get_create_user_usecase()
        response = await usecase.create_user_with_new_team(request)

        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@auth_router.post("/teams/{team_id}/users")
async def add_user_to_team(team_id: str, body: CreateUserForTeamBody):
    """기존 팀에 사용자 추가 (REST: POST /teams/{team_id}/users)"""
    try:
        # path parameter의 team_id와 body를 합쳐서 request 생성
        request = CreateUserForTeamRequest(
            name=body.name,
            app_id=body.app_id,
            app_password=body.app_password,
            team_id=team_id,
        )

        usecase: CreateUserUseCase = app_container.get_create_user_usecase()
        response = await usecase.create_user_for_existing_team(request)

        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@auth_router.get("/users/{app_id}")
async def get_user_by_app_id(app_id: str):
    """앱 ID로 사용자 조회 (REST: GET /users/{app_id})"""
    try:
        usecase: CreateUserUseCase = app_container.get_create_user_usecase()
        response = await usecase.get_user_by_app_id(app_id)

        if not response.success:
            raise HTTPException(status_code=404, detail=response.error)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
