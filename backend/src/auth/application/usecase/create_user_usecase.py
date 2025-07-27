from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field

from ..service.user_management_service import UserManagementService


class CreateUserWithTeamRequest(BaseModel):
    """새 팀과 함께 사용자 생성 요청"""
    name: str = Field(..., min_length=2, max_length=50, description="사용자 이름")
    app_id: str = Field(..., min_length=3, max_length=50, description="앱 ID")
    app_password: str = Field(..., min_length=8, description="앱 비밀번호")
    team_name: str = Field(..., min_length=2, max_length=50, description="팀 이름")


class CreateUserForTeamRequest(BaseModel):
    """기존 팀에 사용자 추가 요청"""
    name: str = Field(..., min_length=2, max_length=50, description="사용자 이름")
    app_id: str = Field(..., min_length=3, max_length=50, description="앱 ID")  
    app_password: str = Field(..., min_length=8, description="앱 비밀번호")
    team_id: str = Field(..., description="팀 ID (UUID)")


class CreateUserResponse(BaseModel):
    """사용자 생성 응답"""
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None


class CreateUserUseCase:
    """사용자 생성 유스케이스"""
    
    def __init__(self, user_management_service: UserManagementService):
        self.user_management_service = user_management_service
    
    async def create_user_with_new_team(
        self, 
        request: CreateUserWithTeamRequest
    ) -> CreateUserResponse:
        """
        새 팀과 함께 사용자 생성
        
        Args:
            request: 사용자 및 팀 생성 요청 데이터
        
        Returns:
            CreateUserResponse: 생성 결과
        """
        try:
            result = await self.user_management_service.create_user_with_team(
                name=request.name,
                app_id=request.app_id,
                app_password=request.app_password,
                team_name=request.team_name
            )
            
            return CreateUserResponse(
                success=True,
                message="User and team created successfully",
                data=result
            )
            
        except ValueError as e:
            return CreateUserResponse(
                success=False,
                message="Validation error",
                error=str(e)
            )
        
        except Exception as e:
            return CreateUserResponse(
                success=False,
                message="Failed to create user and team",
                error=str(e)
            )
    
    async def create_user_for_existing_team(
        self, 
        request: CreateUserForTeamRequest
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
            
            result = await self.user_management_service.create_user_for_existing_team(
                name=request.name,
                app_id=request.app_id,
                app_password=request.app_password,
                team_id=team_id
            )
            
            return CreateUserResponse(
                success=True,
                message="User created successfully",
                data=result
            )
            
        except ValueError as e:
            return CreateUserResponse(
                success=False,
                message="Validation error",
                error=str(e)
            )
        
        except Exception as e:
            return CreateUserResponse(
                success=False,
                message="Failed to create user",
                error=str(e)
            )
    
    async def get_user_by_app_id(self, app_id: str) -> CreateUserResponse:
        """
        앱 ID로 사용자 조회
        
        Args:
            app_id: 앱 ID
        
        Returns:
            CreateUserResponse: 조회 결과
        """
        try:
            result = await self.user_management_service.get_user_by_app_id(app_id)
            
            if result is None:
                return CreateUserResponse(
                    success=False,
                    message="User not found",
                    error=f"No user found with app_id: {app_id}"
                )
            
            return CreateUserResponse(
                success=True,
                message="User found successfully",
                data=result
            )
            
        except Exception as e:
            return CreateUserResponse(
                success=False,
                message="Failed to get user",
                error=str(e)
            ) 