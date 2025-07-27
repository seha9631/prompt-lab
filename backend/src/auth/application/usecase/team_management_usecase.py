from uuid import UUID
from pydantic import BaseModel, Field

from src.shared.response import BaseResponse
from ..service.user_management_service import UserManagementService


class ChangeUserRoleRequest(BaseModel):
    """사용자 권한 변경 요청"""

    target_user_id: str = Field(..., description="권한을 변경할 사용자의 ID")
    new_role: str = Field(..., description="새로운 권한 (owner 또는 user)")


class TeamManagementResponse(BaseResponse[dict]):
    """팀 관리 응답"""

    @classmethod
    def success_response(cls, message: str, data: dict) -> "TeamManagementResponse":
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_response(cls, message: str, error: str) -> "TeamManagementResponse":
        return cls(success=False, message=message, error=error)


class TeamManagementUseCase:
    """팀 관리 유스케이스"""

    def __init__(self, user_management_service: UserManagementService):
        self.user_management_service = user_management_service

    async def get_team_users(self, team_id: str) -> TeamManagementResponse:
        """
        팀의 모든 사용자 조회

        Args:
            team_id: 팀 ID

        Returns:
            TeamManagementResponse: 팀 사용자 목록
        """
        try:
            team_uuid = UUID(team_id)
            users = await self.user_management_service.get_team_users(team_uuid)

            return TeamManagementResponse.success_response(
                message="팀 사용자 목록을 성공적으로 조회했습니다.",
                data={"users": users},
            )

        except Exception as e:
            return TeamManagementResponse.error_response(
                message="팀 사용자 목록 조회 중 오류가 발생했습니다.", error=str(e)
            )

    async def change_user_role(
        self, owner_user_id: str, request: ChangeUserRoleRequest
    ) -> TeamManagementResponse:
        """
        사용자 권한 변경

        Args:
            owner_user_id: 권한을 변경하는 owner의 사용자 ID
            request: 권한 변경 요청 데이터

        Returns:
            TeamManagementResponse: 권한 변경 결과
        """
        try:
            owner_uuid = UUID(owner_user_id)
            target_uuid = UUID(request.target_user_id)

            result = await self.user_management_service.change_user_role(
                target_user_id=target_uuid,
                new_role=request.new_role,
                owner_user_id=owner_uuid,
            )

            return TeamManagementResponse.success_response(
                message="사용자 권한이 성공적으로 변경되었습니다.", data=result
            )

        except Exception as e:
            return TeamManagementResponse.error_response(
                message="사용자 권한 변경 중 오류가 발생했습니다.", error=str(e)
            )
