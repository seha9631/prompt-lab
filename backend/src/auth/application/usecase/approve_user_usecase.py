from uuid import UUID
from pydantic import BaseModel, Field

from src.shared.response import BaseResponse
from ..service.user_management_service import UserManagementService


class ApproveUserRequest(BaseModel):
    """사용자 승인 요청"""

    approver_app_id: str = Field(
        ..., description="승인하는 사용자의 앱 ID (owner 권한 확인용)"
    )


class ApproveUserResponse(BaseResponse[dict]):
    """사용자 승인 응답"""

    @classmethod
    def success_response(cls, message: str, data: dict) -> "ApproveUserResponse":
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_response(cls, message: str, error: str) -> "ApproveUserResponse":
        return cls(success=False, message=message, error=error)


class ApproveUserUseCase:
    """사용자 승인 유스케이스"""

    def __init__(self, user_management_service: UserManagementService):
        self.user_management_service = user_management_service

    async def approve_user(
        self, user_id: str, request: ApproveUserRequest
    ) -> ApproveUserResponse:
        """
        사용자 승인

        Args:
            user_id: 승인할 사용자 ID
            request: 승인 요청 데이터

        Returns:
            ApproveUserResponse: 승인 결과
        """
        try:
            # UUID 변환
            user_uuid = UUID(user_id)

            # 사용자 승인 서비스 호출
            result = await self.user_management_service.approve_user(
                user_id=user_uuid,
                approver_app_id=request.approver_app_id,
            )

            return ApproveUserResponse.success_response(
                message="사용자가 성공적으로 승인되었습니다.", data=result
            )

        except Exception as e:
            return ApproveUserResponse.error_response(
                message="사용자 승인 중 오류가 발생했습니다.", error=str(e)
            )
