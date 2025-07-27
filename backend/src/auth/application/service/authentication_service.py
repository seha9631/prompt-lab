from uuid import UUID
from typing import Optional, Dict, Any

from ...domain.repository.user_repository import UserRepository
from ...domain.value_object.app_credentials import AppPassword
from ....shared.security.jwt_handler import JWTHandler, TokenData
from ....shared.exception import (
    AuthenticationException,
    InvalidTokenException,
    TokenRefreshFailedException,
    UserNotActiveException,
)


class AuthenticationService:
    """인증 서비스"""

    def __init__(self, user_repository_class):
        self.user_repository_class = user_repository_class

    async def authenticate_user(
        self, session, app_id: str, app_password: str
    ) -> Dict[str, Any]:
        """
        사용자 인증

        Args:
            session: 데이터베이스 세션
            app_id: 앱 ID (이메일)
            app_password: 앱 비밀번호

        Returns:
            Dict[str, Any]: 인증 성공 시 토큰 정보
        """
        user_repo = self.user_repository_class(session)

        # 1. 사용자 조회
        user = await user_repo.find_by_app_id(app_id)
        if user is None:
            raise AuthenticationException(
                message="이메일 또는 비밀번호가 잘못되었습니다"
            )

        # 2. 사용자 활성화 상태 확인
        if not user.is_active:
            raise UserNotActiveException(
                message="비활성화된 사용자입니다. 팀 소유자의 승인을 기다려주세요"
            )

        # 3. 비밀번호 검증
        app_password_vo = AppPassword(user.app_password, is_hashed=True)
        if not app_password_vo.verify(app_password):
            raise AuthenticationException(
                message="이메일 또는 비밀번호가 잘못되었습니다"
            )

        # 4. 토큰 생성
        token_data = {
            "user_id": str(user.id),
            "app_id": user.app_id,
            "role": user.role,
            "team_id": str(user.team_id),
        }

        access_token = JWTHandler.create_access_token(token_data)
        refresh_token = JWTHandler.create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "name": user.name,
                "app_id": user.app_id,
                "role": user.role,
                "team_id": str(user.team_id),
                "is_active": user.is_active,
            },
        }

    async def verify_access_token(self, token: str) -> Optional[TokenData]:
        """
        액세스 토큰 검증

        Args:
            token: 액세스 토큰

        Returns:
            Optional[TokenData]: 토큰 데이터 또는 None
        """
        token_data = JWTHandler.verify_access_token(token)
        if token_data is None:
            raise InvalidTokenException(message="유효하지 않은 액세스 토큰입니다")

        return token_data

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        액세스 토큰 갱신

        Args:
            refresh_token: 리프레시 토큰

        Returns:
            Dict[str, Any]: 새로운 액세스 토큰 정보
        """
        new_access_token = JWTHandler.refresh_access_token(refresh_token)
        if new_access_token is None:
            raise TokenRefreshFailedException(
                message="토큰 갱신에 실패했습니다. 다시 로그인해주세요"
            )

        return {"access_token": new_access_token, "token_type": "bearer"}
