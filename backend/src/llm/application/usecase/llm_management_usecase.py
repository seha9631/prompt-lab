"""
LLM 관리 Use Case
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from src.llm.application.service.llm_management_service import LLMManagementService
from src.llm.domain.entity.llm_request import LLMRequest
from src.shared.response.base_response import BaseResponse


class CreateLLMRequestRequest(BaseModel):
    """LLM 요청 생성 요청 모델"""

    system_prompt: str
    question: str
    model_name: str
    credential_name: str
    project_id: str
    file_paths: Optional[List[str]] = None


class CreateBatchLLMRequestRequest(BaseModel):
    """배치 LLM 요청 생성 요청 모델"""

    system_prompt: str
    questions: List[str]
    model_name: str
    credential_name: str
    project_id: str
    file_paths: Optional[List[str]] = None


class LLMRequestResponse(BaseModel):
    """LLM 요청 응답 모델"""

    id: str
    team_id: str
    user_id: str
    project_id: str
    system_prompt: str
    question: str
    model_name: str
    file_paths: List[str]
    status: str
    result: Optional[str]
    error_message: Optional[str]
    created_at: str
    updated_at: str


class LLMManagementUseCase:
    """LLM 관리 Use Case"""

    def __init__(self, llm_management_service: LLMManagementService):
        self.llm_management_service = llm_management_service

    async def create_llm_request(
        self,
        team_id: UUID,
        user_id: UUID,
        request: CreateLLMRequestRequest,
    ) -> BaseResponse[LLMRequestResponse]:
        """LLM 요청을 생성합니다."""
        try:
            llm_request = await self.llm_management_service.create_llm_request(
                team_id=team_id,
                user_id=user_id,
                project_id=UUID(request.project_id),
                system_prompt=request.system_prompt,
                question=request.question,
                model_name=request.model_name,
                credential_name=request.credential_name,
                file_paths=request.file_paths or [],
            )

            response = LLMRequestResponse(
                id=str(llm_request.id),
                team_id=str(llm_request.team_id),
                user_id=str(llm_request.user_id),
                project_id=str(llm_request.project_id),
                system_prompt=llm_request.system_prompt,
                question=llm_request.question,
                model_name=llm_request.model_name,
                file_paths=llm_request.file_paths,
                status=llm_request.status,
                result=llm_request.result,
                error_message=llm_request.error_message,
                created_at=llm_request.created_at.isoformat(),
                updated_at=llm_request.updated_at.isoformat(),
            )

            return BaseResponse.success_response(
                data=response,
                message="LLM 요청이 성공적으로 생성되었습니다.",
            )

        except Exception as e:
            return BaseResponse.error_response(
                message="LLM 요청 생성 중 오류가 발생했습니다.",
                error=str(e),
            )

    async def create_batch_llm_requests(
        self,
        team_id: UUID,
        user_id: UUID,
        request: CreateBatchLLMRequestRequest,
    ) -> BaseResponse[List[LLMRequestResponse]]:
        """여러 LLM 요청을 생성합니다."""
        try:
            llm_requests = await self.llm_management_service.create_batch_llm_requests(
                team_id=team_id,
                user_id=user_id,
                project_id=UUID(request.project_id),
                system_prompt=request.system_prompt,
                questions=request.questions,
                model_name=request.model_name,
                credential_name=request.credential_name,
                file_paths=request.file_paths or [],
            )

            responses = [
                LLMRequestResponse(
                    id=str(llm_request.id),
                    team_id=str(llm_request.team_id),
                    user_id=str(llm_request.user_id),
                    project_id=str(llm_request.project_id),
                    system_prompt=llm_request.system_prompt,
                    question=llm_request.question,
                    model_name=llm_request.model_name,
                    file_paths=llm_request.file_paths,
                    status=llm_request.status,
                    result=llm_request.result,
                    error_message=llm_request.error_message,
                    created_at=llm_request.created_at.isoformat(),
                    updated_at=llm_request.updated_at.isoformat(),
                )
                for llm_request in llm_requests
            ]

            return BaseResponse.success_response(
                data=responses,
                message=f"{len(responses)}개의 LLM 요청이 성공적으로 생성되었습니다.",
            )

        except Exception as e:
            return BaseResponse.error_response(
                message="배치 LLM 요청 생성 중 오류가 발생했습니다.",
                error=str(e),
            )

    async def get_llm_request(
        self, request_id: UUID, team_id: UUID
    ) -> BaseResponse[LLMRequestResponse]:
        """LLM 요청을 조회합니다."""
        try:
            llm_request = await self.llm_management_service.get_llm_request(
                request_id, team_id
            )

            if not llm_request:
                return BaseResponse.error_response(
                    message="LLM 요청을 찾을 수 없습니다.",
                    error="Request not found",
                )

            response = LLMRequestResponse(
                id=str(llm_request.id),
                team_id=str(llm_request.team_id),
                user_id=str(llm_request.user_id),
                project_id=str(llm_request.project_id),
                system_prompt=llm_request.system_prompt,
                question=llm_request.question,
                model_name=llm_request.model_name,
                file_paths=llm_request.file_paths,
                status=llm_request.status,
                result=llm_request.result,
                error_message=llm_request.error_message,
                created_at=llm_request.created_at.isoformat(),
                updated_at=llm_request.updated_at.isoformat(),
            )

            return BaseResponse.success_response(
                data=response,
                message="LLM 요청을 성공적으로 조회했습니다.",
            )

        except Exception as e:
            return BaseResponse.error_response(
                message="LLM 요청 조회 중 오류가 발생했습니다.",
                error=str(e),
            )

    async def get_team_llm_requests(
        self, team_id: UUID
    ) -> BaseResponse[List[LLMRequestResponse]]:
        """팀의 모든 LLM 요청을 조회합니다."""
        try:
            llm_requests = await self.llm_management_service.get_team_llm_requests(
                team_id
            )

            responses = [
                LLMRequestResponse(
                    id=str(req.id),
                    team_id=str(req.team_id),
                    user_id=str(req.user_id),
                    project_id=str(req.project_id),
                    system_prompt=req.system_prompt,
                    question=req.question,
                    model_name=req.model_name,
                    file_paths=req.file_paths,
                    status=req.status,
                    result=req.result,
                    error_message=req.error_message,
                    created_at=req.created_at.isoformat(),
                    updated_at=req.updated_at.isoformat(),
                )
                for req in llm_requests
            ]

            return BaseResponse.success_response(
                data=responses,
                message="팀의 LLM 요청 목록을 성공적으로 조회했습니다.",
            )

        except Exception as e:
            return BaseResponse.error_response(
                message="팀 LLM 요청 조회 중 오류가 발생했습니다.",
                error=str(e),
            )

    async def get_project_llm_requests(
        self, project_id: UUID, team_id: UUID
    ) -> BaseResponse[List[LLMRequestResponse]]:
        """프로젝트의 모든 LLM 요청을 조회합니다."""
        try:
            llm_requests = await self.llm_management_service.get_project_llm_requests(
                project_id, team_id
            )

            responses = [
                LLMRequestResponse(
                    id=str(req.id),
                    team_id=str(req.team_id),
                    user_id=str(req.user_id),
                    project_id=str(req.project_id),
                    system_prompt=req.system_prompt,
                    question=req.question,
                    model_name=req.model_name,
                    file_paths=req.file_paths,
                    status=req.status,
                    result=req.result,
                    error_message=req.error_message,
                    created_at=req.created_at.isoformat(),
                    updated_at=req.updated_at.isoformat(),
                )
                for req in llm_requests
            ]

            return BaseResponse.success_response(
                data=responses,
                message="프로젝트의 LLM 요청 목록을 성공적으로 조회했습니다.",
            )

        except Exception as e:
            return BaseResponse.error_response(
                message="프로젝트 LLM 요청 조회 중 오류가 발생했습니다.",
                error=str(e),
            )

    async def delete_llm_request(
        self, request_id: UUID, team_id: UUID
    ) -> BaseResponse[dict]:
        """LLM 요청을 삭제합니다."""
        try:
            success = await self.llm_management_service.delete_llm_request(
                request_id, team_id
            )

            if not success:
                return BaseResponse.error_response(
                    message="LLM 요청을 찾을 수 없거나 삭제할 권한이 없습니다.",
                    error="Request not found or no permission",
                )

            return BaseResponse.success_response(
                data={"deleted": True},
                message="LLM 요청이 성공적으로 삭제되었습니다.",
            )

        except Exception as e:
            return BaseResponse.error_response(
                message="LLM 요청 삭제 중 오류가 발생했습니다.",
                error=str(e),
            )
