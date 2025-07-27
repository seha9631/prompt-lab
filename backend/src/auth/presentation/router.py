from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.shared.injector.container import app_container
from src.shared.logging import get_logger
from src.shared.exception import (
    ValidationException,
    ResourceNotFoundException,
    DuplicateResourceException,
    ErrorCode,
)
from src.auth.application.usecase.create_user_usecase import (
    CreateUserWithTeamRequest,
    CreateUserForTeamRequest,
    CreateUserUseCase,
)

auth_router = APIRouter(tags=["auth"])
logger = get_logger(__name__)


class CreateUserForTeamBody(BaseModel):
    """기존 팀에 사용자 추가 요청 Body (team_id 제외)"""

    name: str = Field(..., min_length=2, max_length=50, description="사용자 이름")
    app_id: str = Field(..., min_length=3, max_length=50, description="앱 ID")
    app_password: str = Field(..., min_length=8, description="앱 비밀번호")


@auth_router.post("/users")
async def create_user_with_team(request: CreateUserWithTeamRequest):
    """새 팀과 함께 사용자 생성 (REST: POST /users with team data)"""
    logger.info(
        "Creating user with new team",
        extra={
            "app_id": request.app_id,
            "team_name": request.team_name,
            "user_name": request.name,
        },
    )

    try:
        usecase: CreateUserUseCase = app_container.get_create_user_usecase()
        response = await usecase.create_user_with_new_team(request)

        if not response.success:
            logger.warning(
                "User creation failed",
                extra={"app_id": request.app_id, "error": response.error},
            )

            # 에러 내용에 따라 적절한 예외 발생
            if (
                "already exists" in response.error.lower()
                or "이미 존재" in response.error
            ):
                raise DuplicateResourceException(
                    resource_type="User",
                    resource_id=request.app_id,
                    message=response.error,
                )
            elif "validation" in response.error.lower() or "유효성" in response.error:
                raise ValidationException(message=response.error)
            else:
                raise HTTPException(status_code=400, detail=response.error)

        logger.info(
            "User created successfully",
            extra={"app_id": request.app_id, "team_name": request.team_name},
        )
        return response

    except Exception as e:
        logger.error(
            "Unexpected error during user creation",
            extra={"app_id": request.app_id, "error": str(e)},
        )
        raise


@auth_router.post("/teams/{team_id}/users")
async def add_user_to_team(team_id: str, body: CreateUserForTeamBody):
    """기존 팀에 사용자 추가 (REST: POST /teams/{team_id}/users)"""
    logger.info(
        "Adding user to existing team",
        extra={"team_id": team_id, "app_id": body.app_id, "user_name": body.name},
    )

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
            logger.warning(
                "User addition to team failed",
                extra={
                    "team_id": team_id,
                    "app_id": body.app_id,
                    "error": response.error,
                },
            )

            # 에러 내용에 따라 적절한 예외 발생
            if "not found" in response.error.lower() or "찾을 수 없" in response.error:
                raise ResourceNotFoundException(
                    resource_type="Team", resource_id=team_id, message=response.error
                )
            elif (
                "already exists" in response.error.lower()
                or "이미 존재" in response.error
            ):
                raise DuplicateResourceException(
                    resource_type="User",
                    resource_id=body.app_id,
                    message=response.error,
                )
            elif "validation" in response.error.lower() or "유효성" in response.error:
                raise ValidationException(message=response.error)
            else:
                raise HTTPException(status_code=400, detail=response.error)

        logger.info(
            "User added to team successfully",
            extra={"team_id": team_id, "app_id": body.app_id},
        )
        return response

    except Exception as e:
        logger.error(
            "Unexpected error during user addition to team",
            extra={"team_id": team_id, "app_id": body.app_id, "error": str(e)},
        )
        raise


@auth_router.get("/users/{app_id}")
async def get_user_by_app_id(app_id: str):
    """앱 ID로 사용자 조회 (REST: GET /users/{app_id})"""
    logger.info("Getting user by app_id", extra={"app_id": app_id})

    try:
        usecase: CreateUserUseCase = app_container.get_create_user_usecase()
        response = await usecase.get_user_by_app_id(app_id)

        if not response.success:
            logger.warning(
                "User retrieval failed",
                extra={"app_id": app_id, "error": response.error},
            )

            # 사용자를 찾을 수 없는 경우
            if "not found" in response.error.lower() or "찾을 수 없" in response.error:
                raise ResourceNotFoundException(
                    resource_type="User", resource_id=app_id, message=response.error
                )
            else:
                raise HTTPException(status_code=404, detail=response.error)

        logger.info("User retrieved successfully", extra={"app_id": app_id})
        return response

    except Exception as e:
        logger.error(
            "Unexpected error during user retrieval",
            extra={"app_id": app_id, "error": str(e)},
        )
        raise
