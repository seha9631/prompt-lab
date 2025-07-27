from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, EmailStr

from src.shared.injector.container import app_container
from src.shared.logging import get_logger
from src.shared.security.dependencies import get_current_user, require_owner_role
from src.shared.security.jwt_handler import TokenData
from src.shared.exception import (
    ValidationException,
    ResourceNotFoundException,
    DuplicateResourceException,
    AuthenticationException,
    UserNotActiveException,
    TokenRefreshFailedException,
    ErrorCode,
)
from src.auth.application.usecase.create_user_usecase import (
    CreateUserWithTeamRequest,
    CreateUserForTeamRequest,
    CreateUserUseCase,
)
from src.auth.application.usecase.approve_user_usecase import (
    ApproveUserRequest,
    ApproveUserUseCase,
)
from src.auth.application.usecase.authentication_usecase import (
    LoginRequest,
    RefreshTokenRequest,
    AuthenticationUseCase,
)

auth_router = APIRouter(tags=["auth"])
logger = get_logger(__name__)


class CreateUserForTeamBody(BaseModel):
    """기존 팀에 사용자 추가 요청 Body (team_id 제외)"""

    name: str = Field(..., min_length=2, max_length=50, description="사용자 이름")
    app_id: EmailStr = Field(..., description="앱 ID (이메일 주소)")
    app_password: str = Field(
        ...,
        min_length=8,
        description="앱 비밀번호 (대문자, 소문자, 숫자, 특수문자 포함, 최소 8자)",
    )


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
                or "가 이미 존재합니다" in response.error
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
                or "가 이미 존재합니다" in response.error
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
async def get_user_by_app_id(
    app_id: str, current_user: TokenData = Depends(get_current_user)
):
    """앱 ID로 사용자 조회 (REST: GET /users/{app_id})"""
    logger.info(
        "Getting user by app_id",
        extra={
            "app_id": app_id,
            "requested_by": current_user.app_id,
            "user_id": current_user.user_id,
        },
    )

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


@auth_router.patch("/users/{owner_user_id}/approve")
async def approve_user(
    owner_user_id: str,
    request: ApproveUserRequest,
    current_user: TokenData = Depends(require_owner_role),
):
    """사용자 승인 (REST: PATCH /users/{owner_user_id}/approve)"""

    # 토큰의 사용자 ID와 URL 파라미터의 owner_user_id가 일치하는지 확인
    if current_user.user_id != owner_user_id:
        logger.warning(
            "Token user ID mismatch",
            extra={
                "token_user_id": current_user.user_id,
                "url_owner_user_id": owner_user_id,
                "app_id": current_user.app_id,
            },
        )
        raise ValidationException(
            message="토큰의 사용자 ID와 요청한 사용자 ID가 일치하지 않습니다"
        )

    logger.info(
        "Approving user",
        extra={
            "owner_user_id": owner_user_id,
            "user_id_to_approve": request.user_id_to_approve,
            "token_user_id": current_user.user_id,
            "app_id": current_user.app_id,
        },
    )

    try:
        usecase: ApproveUserUseCase = app_container.get_approve_user_usecase()
        response = await usecase.approve_user(owner_user_id, request)

        if not response.success:
            logger.warning(
                "User approval failed",
                extra={
                    "owner_user_id": owner_user_id,
                    "user_id_to_approve": request.user_id_to_approve,
                    "error": response.error,
                },
            )

            # 에러 내용에 따라 적절한 예외 발생
            if "not found" in response.error.lower() or "찾을 수 없" in response.error:
                raise ResourceNotFoundException(
                    resource_type="User",
                    resource_id=request.user_id_to_approve,
                    message=response.error,
                )
            elif (
                "only team owners" in response.error.lower()
                or "팀 소유자만" in response.error
            ):
                raise ValidationException(message=response.error)
            elif (
                "already active" in response.error.lower()
                or "이미 활성화" in response.error
            ):
                raise ValidationException(message=response.error)
            else:
                raise HTTPException(status_code=400, detail=response.error)

        logger.info(
            "User approved successfully",
            extra={
                "owner_user_id": owner_user_id,
                "user_id_to_approve": request.user_id_to_approve,
            },
        )
        return response

    except Exception as e:
        logger.error(
            "Unexpected error during user approval",
            extra={
                "owner_user_id": owner_user_id,
                "user_id_to_approve": request.user_id_to_approve,
                "error": str(e),
            },
        )
        raise


@auth_router.post("/login")
async def login(request: LoginRequest):
    """로그인 (REST: POST /login)"""
    logger.info("User login attempt", extra={"app_id": request.app_id})

    try:
        usecase: AuthenticationUseCase = app_container.get_authentication_usecase()
        response = await usecase.login(request)

        if not response.success:
            logger.warning(
                "Login failed",
                extra={"app_id": request.app_id, "error": response.error},
            )

            # 에러 내용에 따라 적절한 예외 발생
            if "이메일 또는 비밀번호" in response.error:
                raise AuthenticationException(message=response.error)
            elif "비활성화된 사용자" in response.error:
                raise UserNotActiveException(message=response.error)
            else:
                raise HTTPException(status_code=400, detail=response.error)

        logger.info("User logged in successfully", extra={"app_id": request.app_id})
        return response

    except Exception as e:
        logger.error(
            "Unexpected error during login",
            extra={"app_id": request.app_id, "error": str(e)},
        )
        raise


@auth_router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """토큰 갱신 (REST: POST /refresh)"""
    logger.info("Token refresh attempt")

    try:
        usecase: AuthenticationUseCase = app_container.get_authentication_usecase()
        response = await usecase.refresh_token(request)

        if not response.success:
            logger.warning(
                "Token refresh failed",
                extra={"error": response.error},
            )

            # 에러 내용에 따라 적절한 예외 발생
            if "토큰 갱신에 실패" in response.error or "다시 로그인" in response.error:
                raise TokenRefreshFailedException(message=response.error)
            else:
                raise HTTPException(status_code=400, detail=response.error)

        logger.info("Token refreshed successfully")
        return response

    except Exception as e:
        logger.error(
            "Unexpected error during token refresh",
            extra={"error": str(e)},
        )
        raise
