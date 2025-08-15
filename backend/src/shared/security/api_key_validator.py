"""
API 키 검증 모듈
"""

import httpx
from typing import Optional, Dict, Any
from src.shared.logging import get_logger
from src.shared.exception import BusinessException, ErrorCode

logger = get_logger(__name__)


class APIKeyValidator:
    """API 키 유효성 검증 클래스"""

    @staticmethod
    async def validate_openai_api_key(api_key: str) -> bool:
        """
        OpenAI API 키의 유효성을 검증합니다.

        Args:
            api_key: 검증할 OpenAI API 키

        Returns:
            bool: API 키가 유효하면 True, 그렇지 않으면 False

        Raises:
            ValidationException: API 키 형식이 잘못된 경우
        """
        try:
            # API 키 형식 검증 (sk-로 시작하는지 확인)
            if not api_key.startswith("sk-"):
                raise BusinessException(
                    error_code=ErrorCode.INVALID_API_KEY_FORMAT,
                    message="OpenAI API 키는 'sk-'로 시작해야 합니다",
                )

            # OpenAI API를 호출하여 키 유효성 검증
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            # 간단한 모델 목록 조회로 키 유효성 확인
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.openai.com/v1/models", headers=headers
                )

                if response.status_code == 200:
                    logger.info("OpenAI API 키 검증 성공")
                    return True
                elif response.status_code == 401:
                    logger.warning("OpenAI API 키가 유효하지 않습니다")
                    return False
                else:
                    logger.warning(
                        f"OpenAI API 응답 오류: {response.status_code}",
                        extra={"status_code": response.status_code},
                    )
                    return False

        except httpx.TimeoutException:
            logger.error("OpenAI API 키 검증 중 타임아웃 발생")
            raise BusinessException(
                error_code=ErrorCode.API_KEY_VALIDATION_TIMEOUT,
                message="API 키 검증 중 타임아웃이 발생했습니다. 잠시 후 다시 시도해주세요",
            )
        except httpx.RequestError as e:
            logger.error(f"OpenAI API 키 검증 중 네트워크 오류: {str(e)}")
            raise BusinessException(
                error_code=ErrorCode.API_KEY_VALIDATION_NETWORK_ERROR,
                message="API 키 검증 중 네트워크 오류가 발생했습니다",
            )
        except Exception as e:
            logger.error(f"OpenAI API 키 검증 중 예상치 못한 오류: {str(e)}")
            raise BusinessException(
                error_code=ErrorCode.API_KEY_VALIDATION_ERROR,
                message="API 키 검증 중 오류가 발생했습니다",
            )

    @staticmethod
    async def validate_api_key(source_id: str, api_key: str) -> bool:
        """
        소스 ID에 따른 API 키 유효성을 검증합니다.

        Args:
            source_id: API 소스 ID (예: "openai", "anthropic" 등)
            api_key: 검증할 API 키

        Returns:
            bool: API 키가 유효하면 True, 그렇지 않으면 False
        """
        if source_id.lower() == "openai":
            return await APIKeyValidator.validate_openai_api_key(api_key)
        else:
            logger.warning(f"지원하지 않는 API 소스: {source_id}")
            raise BusinessException(
                error_code=ErrorCode.UNSUPPORTED_API_SOURCE,
                message=f"지원하지 않는 API 소스입니다: {source_id}",
            )
