from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.shared.security.jwt_handler import JWTHandler, TokenData
from src.shared.exception import InvalidTokenException, AuthenticationException
from src.shared.logging import get_logger

logger = get_logger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """
    현재 인증된 사용자 정보를 반환하는 의존성 함수

    Args:
        credentials: HTTP Bearer 토큰

    Returns:
        TokenData: 현재 사용자 정보

    Raises:
        HTTPException: 토큰이 유효하지 않은 경우
    """
    try:
        token = credentials.credentials
        token_data = JWTHandler.verify_access_token(token)

        if token_data is None:
            raise InvalidTokenException(message="유효하지 않은 액세스 토큰입니다")

        logger.info(f"User authenticated: {token_data.app_id}")
        return token_data

    except InvalidTokenException as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증에 실패했습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user),
) -> TokenData:
    """
    현재 활성화된 사용자 정보를 반환하는 의존성 함수

    Args:
        current_user: 현재 사용자 정보

    Returns:
        TokenData: 활성화된 사용자 정보

    Raises:
        HTTPException: 사용자가 비활성화된 경우
    """
    # 여기서는 토큰에 is_active 정보가 없으므로,
    # 필요시 데이터베이스에서 사용자 상태를 확인해야 함
    return current_user


async def require_owner_role(
    current_user: TokenData = Depends(get_current_user),
) -> TokenData:
    """
    owner 권한이 필요한 의존성 함수

    Args:
        current_user: 현재 사용자 정보

    Returns:
        TokenData: owner 권한을 가진 사용자 정보

    Raises:
        HTTPException: owner 권한이 없는 경우
    """
    if current_user.role != "owner":
        logger.warning(
            f"User {current_user.app_id} attempted to access owner-only endpoint"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="owner 권한이 필요합니다"
        )

    return current_user
