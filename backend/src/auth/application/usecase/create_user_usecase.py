"""
Create User Use Case
사용자 생성 비즈니스 로직
"""

from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field, EmailStr

from src.shared.response import BaseResponse
from src.auth.application.service.user_management_service import UserManagementService


class CreateUserWithTeamRequest(BaseModel):
    """새 팀과 함께 사용자 생성 요청"""

    name: str = Field(..., min_length=2, max_length=50, description="사용자 이름")
    app_id: EmailStr = Field(..., description="앱 ID (이메일 주소)")
    app_password: str = Field(
        ...,
        min_length=8,
        description="앱 비밀번호 (대문자, 소문자, 숫자, 특수문자 포함, 최소 8자)",
    )
    team_name: str = Field(..., min_length=2, max_length=50, description="팀 이름")


class CreateUserForTeamRequest(BaseModel):
    """기존 팀에 사용자 추가 요청"""

    name: str = Field(..., min_length=2, max_length=50, description="사용자 이름")
    app_id: EmailStr = Field(..., description="앱 ID (이메일 주소)")
    app_password: str = Field(
        ...,
        min_length=8,
        description="앱 비밀번호 (대문자, 소문자, 숫자, 특수문자 포함, 최소 8자)",
    )
    team_id: str = Field(..., description="팀 ID (UUID)")


class CreateUserResponse(BaseResponse[dict]):
    """사용자 생성 응답 - BaseResponse를 상속받아 일관된 응답 형식 제공"""

    pass


class CreateUserUseCase:
    """사용자 생성 유스케이스"""

    def __init__(self, user_management_service: UserManagementService):
        self.user_management_service = user_management_service

    async def create_user_with_new_team(
        self, request: CreateUserWithTeamRequest
    ) -> CreateUserResponse:
        """
        새 팀과 함께 사용자 생성

        Args:
            request: 사용자 및 팀 생성 요청 데이터

        Returns:
            CreateUserResponse: 생성 결과
        """
        try:
            # 사용자 생성 서비스 호출 (실제 메서드명 사용)
            result = await self.user_management_service.create_user_with_team(
                name=request.name,
                app_id=request.app_id,
                app_password=request.app_password,
                team_name=request.team_name,
            )

            # 서비스에서 딕셔너리를 반환하므로 그대로 사용
            return CreateUserResponse.success_response(
                message="사용자와 팀이 성공적으로 생성되었습니다.", data=result
            )

        except Exception as e:
            return CreateUserResponse.error_response(
                message="사용자 및 팀 생성 중 오류가 발생했습니다.", error=str(e)
            )

    async def create_user_for_existing_team(
        self, request: CreateUserForTeamRequest
    ) -> CreateUserResponse:
        """
        기존 팀에 사용자 추가

        Args:
            request: 사용자 생성 요청 데이터

        Returns:
            CreateUserResponse: 생성 결과
        """
        try:
            # UUID 변환
            team_id = UUID(request.team_id)

            # 사용자 생성 서비스 호출
            result = await self.user_management_service.create_user_for_existing_team(
                name=request.name,
                app_id=request.app_id,
                app_password=request.app_password,
                team_id=team_id,
            )

            # 서비스에서 딕셔너리를 반환하므로 그대로 사용
            return CreateUserResponse.success_response(
                message="사용자가 팀에 성공적으로 추가되었습니다.", data=result
            )

        except Exception as e:
            return CreateUserResponse.error_response(
                message="사용자 추가 중 오류가 발생했습니다.", error=str(e)
            )

    async def get_user_by_app_id(self, app_id: str) -> CreateUserResponse:
        """
        앱 ID로 사용자 조회

        Args:
            app_id: 앱 ID (이메일)

        Returns:
            CreateUserResponse: 조회 결과
        """
        try:
            # 사용자 조회 서비스 호출
            result = await self.user_management_service.get_user_by_app_id(app_id)

            if result is not None:
                return CreateUserResponse.success_response(
                    message="사용자 조회가 완료되었습니다.", data=result
                )
            else:
                return CreateUserResponse.error_response(
                    message="사용자를 찾을 수 없습니다.",
                    error=f"App ID '{app_id}'에 해당하는 사용자가 존재하지 않습니다.",
                )

        except Exception as e:
            return CreateUserResponse.error_response(
                message="사용자 조회 중 오류가 발생했습니다.", error=str(e)
            )
