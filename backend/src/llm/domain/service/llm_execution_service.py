"""
LLM 실행 도메인 서비스
"""

import asyncio
import json
from typing import Optional, Dict, Any
from uuid import UUID

from src.auth.domain.repository.credential_repository import CredentialRepository
from src.auth.domain.repository.source_repository import SourceRepository
from src.llm.domain.entity.llm_request import LLMRequest
from src.shared.exception import BusinessException, ErrorCode
from src.shared.security.encryption import EncryptionService
from src.shared.logging import get_logger

logger = get_logger(__name__)


class LLMExecutionService:
    """LLM 실행 도메인 서비스"""

    def __init__(
        self,
        credential_repository: CredentialRepository,
        source_repository: SourceRepository,
    ):
        self.credential_repository = credential_repository
        self.source_repository = source_repository

    async def execute_llm_request(
        self, llm_request: LLMRequest, credential_name: str
    ) -> str:
        """
        LLM 요청을 실행합니다.

        Args:
            llm_request: 실행할 LLM 요청
            credential_name: 사용할 credential 이름

        Returns:
            str: LLM 응답 결과
        """
        try:
            # 1. Credential 조회
            credential = await self.credential_repository.find_by_team_and_name(
                llm_request.team_id, credential_name
            )
            if not credential:
                raise BusinessException(
                    error_code=ErrorCode.CREDENTIAL_NOT_FOUND,
                    message=f"Credential '{credential_name}'을 찾을 수 없습니다.",
                )

            # 2. Source 정보 조회
            source = await self.source_repository.find_by_id(credential.source_id)
            if not source:
                raise BusinessException(
                    error_code=ErrorCode.SOURCE_NOT_FOUND,
                    message="소스 정보를 찾을 수 없습니다.",
                )

            # 3. API 키 복호화
            try:
                api_key = EncryptionService.decrypt_api_key(
                    credential.api_key, str(llm_request.team_id)
                )
            except Exception as e:
                raise BusinessException(
                    error_code=ErrorCode.ENCRYPTION_ERROR,
                    message=f"API 키 복호화에 실패했습니다: {str(e)}",
                )

            # 4. LLM 실행
            if source.name.lower() == "openai":
                return await self._execute_openai_request(llm_request, api_key)
            else:
                raise BusinessException(
                    error_code=ErrorCode.UNSUPPORTED_API_SOURCE,
                    message=f"지원하지 않는 LLM 소스입니다: {source.name}",
                )

        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"LLM 실행 중 예상치 못한 오류: {str(e)}")
            raise BusinessException(
                error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                message="LLM 실행 중 오류가 발생했습니다.",
            )

    async def _execute_openai_request(
        self, llm_request: LLMRequest, api_key: str
    ) -> str:
        """OpenAI API를 사용하여 LLM 요청을 실행합니다."""
        import httpx

        # OpenAI API 요청 데이터 구성
        messages = [{"role": "user", "content": llm_request.prompt}]

        # 파일이 있는 경우 파일 내용을 메시지에 추가
        if llm_request.file_paths:
            file_contents = []
            for file_path in llm_request.file_paths:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        file_contents.append(f"파일: {file_path}\n내용:\n{content}")
                except Exception as e:
                    logger.warning(f"파일 읽기 실패: {file_path}, 오류: {str(e)}")

            if file_contents:
                file_content = "\n\n".join(file_contents)
                messages.append(
                    {
                        "role": "user",
                        "content": f"다음 파일들을 참고하여 답변해주세요:\n\n{file_content}",
                    }
                )

        request_data = {
            "model": llm_request.model_name,
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.7,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=request_data,
                )

                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error_msg = f"OpenAI API 오류: {response.status_code}"
                    try:
                        error_data = response.json()
                        if "error" in error_data:
                            error_msg += f" - {error_data['error'].get('message', '')}"
                    except:
                        pass

                    raise BusinessException(
                        error_code=ErrorCode.EXTERNAL_SERVICE_ERROR, message=error_msg
                    )

        except httpx.TimeoutException:
            raise BusinessException(
                error_code=ErrorCode.EXTERNAL_SERVICE_TIMEOUT,
                message="LLM 요청이 시간 초과되었습니다.",
            )
        except httpx.RequestError as e:
            raise BusinessException(
                error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
                message=f"LLM 요청 중 네트워크 오류가 발생했습니다: {str(e)}",
            )
