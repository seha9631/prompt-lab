"""
LLM API Router
LLM 실행 및 파일 업로드 엔드포인트
"""

import os
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel, Field

from src.shared.injector.container import app_container
from src.shared.security.dependencies import get_current_user
from src.shared.security.jwt_handler import TokenData
from src.shared.response.base_response import BaseResponse
from src.shared.exception.business_exception import BusinessException
from src.shared.exception.error_codes import ErrorCode
from src.shared.logging import get_logger

from src.llm.application.usecase.llm_management_usecase import (
    CreateLLMRequestRequest,
    CreateBatchLLMRequestRequest,
    LLMRequestResponse,
    LLMManagementUseCase,
)

router = APIRouter(prefix="/llm", tags=["llm"])
logger = get_logger(__name__)


# Request/Response Models
class CreateLLMRequestModel(BaseModel):
    system_prompt: str = Field(
        ..., min_length=1, max_length=10000, description="시스템 프롬프트"
    )
    question: str = Field(..., min_length=1, max_length=10000, description="질문")
    model_name: str = Field(..., description="모델명 (예: gpt-4, gpt-3.5-turbo)")
    credential_name: str = Field(..., description="사용할 credential 이름")
    project_id: str = Field(..., description="프로젝트 ID")
    file_paths: List[str] = Field(default=[], description="업로드된 파일 경로들")


class CreateBatchLLMRequestModel(BaseModel):
    system_prompt: str = Field(
        ..., min_length=1, max_length=10000, description="시스템 프롬프트"
    )
    questions: List[str] = Field(
        ..., min_items=1, max_items=10, description="질문 목록 (최대 10개)"
    )
    model_name: str = Field(..., description="모델명 (예: gpt-4, gpt-3.5-turbo)")
    credential_name: str = Field(..., description="사용할 credential 이름")
    project_id: str = Field(..., description="프로젝트 ID")
    file_paths: List[str] = Field(default=[], description="업로드된 파일 경로들")


class FileUploadResponse(BaseModel):
    filename: str


class FileListResponse(BaseModel):
    files: List[str]


def get_llm_usecase():
    """LLMManagementUseCase 의존성 함수"""
    return app_container.get_llm_management_usecase()


@router.post("/upload", response_model=BaseResponse[FileUploadResponse])
async def upload_file(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    current_user: TokenData = Depends(get_current_user),
):
    """파일을 업로드합니다."""
    try:
        # 파일 크기 제한 (10MB)
        if file.size and file.size > 10 * 1024 * 1024:
            raise BusinessException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message="파일 크기는 10MB를 초과할 수 없습니다.",
            )

        # 허용된 파일 확장자
        allowed_extensions = {
            ".txt",
            ".md",
            ".py",
            ".js",
            ".html",
            ".css",
            ".json",
            ".xml",
            ".csv",
        }
        file_extension = os.path.splitext(file.filename)[1].lower()

        if file_extension not in allowed_extensions:
            raise BusinessException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message=f"지원하지 않는 파일 형식입니다. 허용된 형식: {', '.join(allowed_extensions)}",
            )

        # 파일 내용 읽기
        file_content = await file.read()

        # LLM 관리 서비스를 통해 파일 저장
        llm_service = app_container.get_llm_management_service()
        file_path = llm_service.save_uploaded_file(
            file_content, file.filename, str(current_user.team_id), project_id
        )

        logger.info(
            "파일 업로드 성공",
            extra={
                "user_id": current_user.user_id,
                "team_id": current_user.team_id,
                "project_id": project_id,
                "uploaded_filename": file.filename,
            },
        )

        return BaseResponse.success_response(
            data=FileUploadResponse(filename=file.filename),
            message="파일이 성공적으로 업로드되었습니다.",
        )

    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_dict
        )
    except Exception as e:
        logger.error(f"파일 업로드 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="파일 업로드 중 오류가 발생했습니다.",
        )


@router.get(
    "/projects/{project_id}/files", response_model=BaseResponse[FileListResponse]
)
async def get_project_files(
    project_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """프로젝트의 업로드된 파일 목록을 조회합니다."""
    try:
        # LLM 관리 서비스를 통해 파일 목록 조회
        llm_service = app_container.get_llm_management_service()
        files = llm_service.get_project_files(str(current_user.team_id), project_id)

        logger.info(
            "프로젝트 파일 목록 조회",
            extra={
                "user_id": current_user.user_id,
                "team_id": current_user.team_id,
                "project_id": project_id,
                "file_count": len(files),
            },
        )

        return BaseResponse.success_response(
            data=FileListResponse(files=files),
            message="파일 목록을 성공적으로 조회했습니다.",
        )

    except Exception as e:
        logger.error(f"프로젝트 파일 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="파일 목록 조회 중 오류가 발생했습니다.",
        )


@router.post("/requests", response_model=BaseResponse[LLMRequestResponse])
async def create_llm_request(
    request: CreateLLMRequestModel,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_llm_usecase),
):
    """LLM 요청을 생성합니다."""
    try:
        llm_request = CreateLLMRequestRequest(
            system_prompt=request.system_prompt,
            question=request.question,
            model_name=request.model_name,
            credential_name=request.credential_name,
            project_id=request.project_id,
            file_paths=request.file_paths,
        )

        response = await usecase.create_llm_request(
            team_id=current_user.team_id,
            user_id=current_user.user_id,
            request=llm_request,
        )

        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": response.message, "error": response.error},
            )

        logger.info(
            "LLM 요청 생성",
            extra={
                "user_id": current_user.user_id,
                "team_id": current_user.team_id,
                "request_id": response.data.id,
                "llm_model_name": request.model_name,
            },
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LLM 요청 생성 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM 요청 생성 중 오류가 발생했습니다.",
        )


@router.post("/batch-requests", response_model=BaseResponse[List[LLMRequestResponse]])
async def create_batch_llm_requests(
    request: CreateBatchLLMRequestModel,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_llm_usecase),
):
    """여러 LLM 요청을 생성합니다."""
    try:
        batch_request = CreateBatchLLMRequestRequest(
            system_prompt=request.system_prompt,
            questions=request.questions,
            model_name=request.model_name,
            credential_name=request.credential_name,
            project_id=request.project_id,
            file_paths=request.file_paths,
        )

        response = await usecase.create_batch_llm_requests(
            team_id=current_user.team_id,
            user_id=current_user.user_id,
            request=batch_request,
        )

        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": response.message, "error": response.error},
            )

        logger.info(
            "배치 LLM 요청 생성",
            extra={
                "user_id": current_user.user_id,
                "team_id": current_user.team_id,
                "question_count": len(request.questions),
                "llm_model_name": request.model_name,
            },
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"배치 LLM 요청 생성 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="배치 LLM 요청 생성 중 오류가 발생했습니다.",
        )


@router.get("/requests", response_model=BaseResponse[List[LLMRequestResponse]])
async def get_team_llm_requests(
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_llm_usecase),
):
    """팀의 모든 LLM 요청을 조회합니다."""
    try:
        response = await usecase.get_team_llm_requests(current_user.team_id)

        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": response.message, "error": response.error},
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팀 LLM 요청 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="팀 LLM 요청 조회 중 오류가 발생했습니다.",
        )


@router.get(
    "/projects/{project_id}/requests",
    response_model=BaseResponse[List[LLMRequestResponse]],
)
async def get_project_llm_requests(
    project_id: str,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_llm_usecase),
):
    """프로젝트의 모든 LLM 요청을 조회합니다."""
    try:
        response = await usecase.get_project_llm_requests(
            project_id=UUID(project_id),
            team_id=current_user.team_id,
        )

        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": response.message, "error": response.error},
            )

        logger.info(
            "프로젝트 LLM 요청 조회",
            extra={
                "user_id": current_user.user_id,
                "team_id": current_user.team_id,
                "project_id": project_id,
                "request_count": len(response.data),
            },
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"프로젝트 LLM 요청 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로젝트 LLM 요청 조회 중 오류가 발생했습니다.",
        )


@router.get("/requests/{request_id}", response_model=BaseResponse[LLMRequestResponse])
async def get_llm_request(
    request_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_llm_usecase),
):
    """특정 LLM 요청을 조회합니다."""
    try:
        response = await usecase.get_llm_request(request_id, current_user.team_id)

        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": response.message, "error": response.error},
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LLM 요청 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM 요청 조회 중 오류가 발생했습니다.",
        )


@router.delete("/requests/{request_id}", response_model=BaseResponse[dict])
async def delete_llm_request(
    request_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_llm_usecase),
):
    """LLM 요청을 삭제합니다."""
    try:
        response = await usecase.delete_llm_request(request_id, current_user.team_id)

        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": response.message, "error": response.error},
            )

        logger.info(
            "LLM 요청 삭제",
            extra={
                "user_id": current_user.user_id,
                "team_id": current_user.team_id,
                "deleted_request_id": str(request_id),
            },
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LLM 요청 삭제 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM 요청 삭제 중 오류가 발생했습니다.",
        )
