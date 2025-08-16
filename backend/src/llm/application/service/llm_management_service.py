"""
LLM 관리 Application 서비스
"""

import os
import asyncio
import uuid
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.llm.domain.entity.llm_request import LLMRequest
from src.llm.domain.repository.llm_request_repository import LLMRequestRepository
from src.llm.domain.service.llm_execution_service import LLMExecutionService
from src.shared.exception import BusinessException, ErrorCode
from src.shared.logging import get_logger

logger = get_logger(__name__)


class LLMManagementService:
    """LLM 관리 Application 서비스"""

    def __init__(
        self,
        llm_request_repository_class,
        credential_repository_class,
        source_repository_class,
        get_session_func,
        upload_dir: str = "uploads",
    ):
        self.llm_request_repository_class = llm_request_repository_class
        self.credential_repository_class = credential_repository_class
        self.source_repository_class = source_repository_class
        self.get_session_func = get_session_func
        self.upload_dir = upload_dir

        # 업로드 디렉토리 생성
        os.makedirs(self.upload_dir, exist_ok=True)

    async def _get_repositories(self):
        """새로운 세션으로 repository들을 생성합니다."""
        session = self.get_session_func()
        return (
            self.llm_request_repository_class(session),
            self.credential_repository_class(session),
            self.source_repository_class(session),
        ), session

    async def create_llm_request(
        self,
        team_id: UUID,
        user_id: UUID,
        project_id: UUID,
        system_prompt: str,
        question: str,
        model_name: str,
        credential_name: str,
        file_paths: Optional[List[str]] = None,
    ) -> LLMRequest:
        """새로운 LLM 요청을 생성하고 실행합니다."""
        (llm_repo, credential_repo, source_repo), session = (
            await self._get_repositories()
        )

        try:
            # LLM 요청 생성
            llm_request = LLMRequest(
                id=uuid.uuid4(),
                team_id=team_id,
                user_id=user_id,
                project_id=project_id,
                system_prompt=system_prompt,
                question=question,
                model_name=model_name,
                file_paths=file_paths or [],
                status="pending",
            )

            # DB에 저장
            saved_request = await llm_repo.create(llm_request)

            # LLM 실행 서비스 생성
            llm_execution_service = LLMExecutionService(
                credential_repository=credential_repo,
                source_repository=source_repo,
            )

            # 비동기로 LLM 실행
            asyncio.create_task(
                self._execute_llm_async(
                    saved_request, llm_execution_service, credential_name, llm_repo
                )
            )

            return saved_request

        finally:
            await session.close()

    async def create_batch_llm_requests(
        self,
        team_id: UUID,
        user_id: UUID,
        project_id: UUID,
        system_prompt: str,
        questions: List[str],
        model_name: str,
        credential_name: str,
        file_paths: Optional[List[str]] = None,
    ) -> List[LLMRequest]:
        """여러 LLM 요청을 생성합니다."""
        (llm_repo, credential_repo, source_repo), session = (
            await self._get_repositories()
        )

        try:
            created_requests = []

            for question in questions:
                # LLM 요청 생성
                llm_request = LLMRequest(
                    id=uuid.uuid4(),
                    team_id=team_id,
                    user_id=user_id,
                    project_id=project_id,
                    system_prompt=system_prompt,
                    question=question,
                    model_name=model_name,
                    file_paths=file_paths or [],
                    status="pending",
                )

                # DB에 저장
                saved_request = await llm_repo.create(llm_request)
                created_requests.append(saved_request)

                # 비동기로 LLM 실행 (새로운 세션 사용)
                asyncio.create_task(
                    self._execute_llm_async_with_new_session(
                        saved_request, credential_name
                    )
                )

            return created_requests

        finally:
            await session.close()

    async def _execute_llm_async(
        self,
        llm_request: LLMRequest,
        llm_execution_service: LLMExecutionService,
        credential_name: str,
        llm_repo: LLMRequestRepository,
    ):
        """비동기로 LLM을 실행하고 결과를 업데이트합니다."""
        try:
            # 상태를 processing으로 변경
            llm_request.update_status("processing")
            await llm_repo.update(llm_request)

            # LLM 실행
            result = await llm_execution_service.execute_llm_request(
                llm_request, credential_name, self.upload_dir
            )

            # 성공 상태로 업데이트
            llm_request.update_status("completed", result=result)
            await llm_repo.update(llm_request)

            logger.info(f"LLM 요청 완료: {llm_request.id}")

        except Exception as e:
            # 실패 상태로 업데이트
            error_message = str(e)
            llm_request.update_status("failed", error_message=error_message)
            await llm_repo.update(llm_request)

            logger.error(f"LLM 요청 실패: {llm_request.id}, 오류: {error_message}")

    async def _execute_llm_async_with_new_session(
        self,
        llm_request: LLMRequest,
        credential_name: str,
    ):
        """새로운 세션으로 LLM을 비동기 실행하고 결과를 업데이트합니다."""
        (llm_repo, credential_repo, source_repo), session = (
            await self._get_repositories()
        )

        try:
            # 상태를 processing으로 변경
            llm_request.update_status("processing")
            await llm_repo.update(llm_request)

            # LLM 실행 서비스 생성
            llm_execution_service = LLMExecutionService(
                credential_repository=credential_repo,
                source_repository=source_repo,
            )

            # LLM 실행
            result = await llm_execution_service.execute_llm_request(
                llm_request, credential_name, self.upload_dir
            )

            # 성공 상태로 업데이트
            llm_request.update_status("completed", result=result)
            await llm_repo.update(llm_request)

            logger.info(f"LLM 요청 완료: {llm_request.id}")

        except Exception as e:
            # 실패 상태로 업데이트
            error_message = str(e)
            llm_request.update_status("failed", error_message=error_message)
            await llm_repo.update(llm_request)

            logger.error(f"LLM 요청 실패: {llm_request.id}, 오류: {error_message}")

        finally:
            await session.close()

    async def get_llm_request(
        self, request_id: UUID, team_id: UUID
    ) -> Optional[LLMRequest]:
        """LLM 요청을 조회합니다."""
        (llm_repo, _, _), session = await self._get_repositories()

        try:
            llm_request = await llm_repo.find_by_id(request_id)
            if llm_request and str(llm_request.team_id) == str(team_id):
                return llm_request
            return None
        finally:
            await session.close()

    async def get_team_llm_requests(self, team_id: UUID) -> List[LLMRequest]:
        """팀의 모든 LLM 요청을 조회합니다."""
        (llm_repo, _, _), session = await self._get_repositories()

        try:
            return await llm_repo.find_by_team_id(team_id)
        finally:
            await session.close()

    async def get_project_llm_requests(
        self, project_id: UUID, team_id: UUID
    ) -> List[LLMRequest]:
        """프로젝트의 모든 LLM 요청을 조회합니다."""
        (llm_repo, _, _), session = await self._get_repositories()

        try:
            return await llm_repo.find_by_project_id_and_team_id(project_id, team_id)
        finally:
            await session.close()

    async def get_user_llm_requests(self, user_id: UUID) -> List[LLMRequest]:
        """사용자의 모든 LLM 요청을 조회합니다."""
        (llm_repo, _, _), session = await self._get_repositories()

        try:
            return await llm_repo.find_by_user_id(user_id)
        finally:
            await session.close()

    async def delete_llm_request(self, request_id: UUID, team_id: UUID) -> bool:
        """LLM 요청을 삭제합니다."""
        (llm_repo, _, _), session = await self._get_repositories()

        try:
            # 요청이 해당 팀의 것인지 확인
            llm_request = await llm_repo.find_by_id(request_id)
            if not llm_request or str(llm_request.team_id) != str(team_id):
                return False

            return await llm_repo.delete(request_id)
        finally:
            await session.close()

    def save_uploaded_file(
        self, file_content: bytes, filename: str, team_id: str, project_id: str
    ) -> str:
        """업로드된 파일을 저장하고 파일명을 반환합니다."""
        # team_id/project_id 기준으로 폴더 생성
        project_upload_dir = os.path.join(self.upload_dir, team_id, project_id)
        os.makedirs(project_upload_dir, exist_ok=True)

        # 원본 파일명 그대로 사용
        file_path = os.path.join(project_upload_dir, filename)

        with open(file_path, "wb") as f:
            f.write(file_content)

        return filename

    def get_project_files(self, team_id: str, project_id: str) -> List[str]:
        """프로젝트 폴더의 파일 목록을 조회합니다."""
        project_upload_dir = os.path.join(self.upload_dir, team_id, project_id)

        if not os.path.exists(project_upload_dir):
            return []

        try:
            files = []
            for filename in os.listdir(project_upload_dir):
                file_path = os.path.join(project_upload_dir, filename)
                if os.path.isfile(file_path):
                    files.append(filename)
            return sorted(files)
        except Exception as e:
            logger.error(f"프로젝트 파일 목록 조회 중 오류: {str(e)}")
            return []
