"""
Authentication Use Case
인증 비즈니스 로직
"""

from pydantic import BaseModel, Field, EmailStr

from src.shared.response import BaseResponse
from src.auth.application.service.authentication_service import AuthenticationService


class LoginRequest(BaseModel):
    """로그인 요청"""

    app_id: EmailStr = Field(..., description="앱 ID (이메일 주소)")
    app_password: str = Field(..., description="앱 비밀번호")


class RefreshTokenRequest(BaseModel):
    """토큰 갱신 요청"""

    refresh_token: str = Field(..., description="리프레시 토큰")


class AuthenticationResponse(BaseResponse[dict]):
    """인증 응답"""

    @classmethod
    def success_response(cls, message: str, data: dict) -> "AuthenticationResponse":
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_response(cls, message: str, error: str) -> "AuthenticationResponse":
        return cls(success=False, message=message, error=error)


class AuthenticationUseCase:
    """인증 유스케이스"""

    def __init__(self, authentication_service: AuthenticationService, get_session_func):
        self.authentication_service = authentication_service
        self.get_session = get_session_func

    async def login(self, request: LoginRequest) -> AuthenticationResponse:
        """
        로그인

        Args:
            request: 로그인 요청 데이터

        Returns:
            AuthenticationResponse: 로그인 결과
        """
        try:
            async with self.get_session() as session:
                result = await self.authentication_service.authenticate_user(
                    session=session,
                    app_id=request.app_id,
                    app_password=request.app_password,
                )

                return AuthenticationResponse.success_response(
                    message="로그인이 성공적으로 완료되었습니다.", data=result
                )

        except Exception as e:
            return AuthenticationResponse.error_response(
                message="로그인 중 오류가 발생했습니다.", error=str(e)
            )

    async def refresh_token(
        self, request: RefreshTokenRequest
    ) -> AuthenticationResponse:
        """
        토큰 갱신

        Args:
            request: 토큰 갱신 요청 데이터

        Returns:
            AuthenticationResponse: 토큰 갱신 결과
        """
        try:
            result = await self.authentication_service.refresh_access_token(
                refresh_token=request.refresh_token
            )

            return AuthenticationResponse.success_response(
                message="토큰이 성공적으로 갱신되었습니다.", data=result
            )

        except Exception as e:
            return AuthenticationResponse.error_response(
                message="토큰 갱신 중 오류가 발생했습니다.", error=str(e)
            )
