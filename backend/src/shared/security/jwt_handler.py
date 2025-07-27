from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from pydantic import BaseModel

from src.shared.logging import get_logger

logger = get_logger(__name__)


class TokenData(BaseModel):
    """토큰 데이터 모델"""

    user_id: str
    app_id: str
    role: str
    team_id: str


class JWTConfig:
    """JWT 설정"""

    SECRET_KEY = (
        "your-secret-key-here-change-in-production"  # 실제 운영에서는 환경변수로 관리
    )
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 6 * 60  # 6시간
    REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7일


class JWTHandler:
    """JWT 토큰 핸들러"""

    @staticmethod
    def create_access_token(data: Dict[str, Any]) -> str:
        """액세스 토큰 생성"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire, "type": "access"})

        encoded_jwt = jwt.encode(
            to_encode, JWTConfig.SECRET_KEY, algorithm=JWTConfig.ALGORITHM
        )
        logger.info(f"Access token created for user: {data.get('app_id')}")
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """리프레시 토큰 생성"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})

        encoded_jwt = jwt.encode(
            to_encode, JWTConfig.SECRET_KEY, algorithm=JWTConfig.ALGORITHM
        )
        logger.info(f"Refresh token created for user: {data.get('app_id')}")
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """토큰 검증"""
        try:
            payload = jwt.decode(
                token, JWTConfig.SECRET_KEY, algorithms=[JWTConfig.ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return None

    @staticmethod
    def verify_access_token(token: str) -> Optional[TokenData]:
        """액세스 토큰 검증"""
        payload = JWTHandler.verify_token(token)
        if payload is None:
            return None

        # 토큰 타입 확인
        if payload.get("type") != "access":
            logger.warning("Invalid token type for access token")
            return None

        try:
            token_data = TokenData(
                user_id=payload.get("user_id"),
                app_id=payload.get("app_id"),
                role=payload.get("role"),
                team_id=payload.get("team_id"),
            )
            return token_data
        except Exception as e:
            logger.error(f"Failed to parse token data: {str(e)}")
            return None

    @staticmethod
    def verify_refresh_token(token: str) -> Optional[TokenData]:
        """리프레시 토큰 검증"""
        payload = JWTHandler.verify_token(token)
        if payload is None:
            return None

        # 토큰 타입 확인
        if payload.get("type") != "refresh":
            logger.warning("Invalid token type for refresh token")
            return None

        try:
            token_data = TokenData(
                user_id=payload.get("user_id"),
                app_id=payload.get("app_id"),
                role=payload.get("role"),
                team_id=payload.get("team_id"),
            )
            return token_data
        except Exception as e:
            logger.error(f"Failed to parse token data: {str(e)}")
            return None

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[str]:
        """리프레시 토큰으로 액세스 토큰 갱신"""
        token_data = JWTHandler.verify_refresh_token(refresh_token)
        if token_data is None:
            return None

        # 새로운 액세스 토큰 생성
        data = {
            "user_id": token_data.user_id,
            "app_id": token_data.app_id,
            "role": token_data.role,
            "team_id": token_data.team_id,
        }

        new_access_token = JWTHandler.create_access_token(data)
        logger.info(f"Access token refreshed for user: {token_data.app_id}")
        return new_access_token
