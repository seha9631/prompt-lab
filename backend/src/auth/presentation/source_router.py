"""
Source API Router
소스 및 소스 모델 조회 엔드포인트
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.shared.injector.container import app_container
from src.shared.security.dependencies import get_current_user
from src.shared.security.jwt_handler import TokenData
from src.shared.response.base_response import BaseResponse
from src.shared.exception.business_exception import BusinessException

router = APIRouter(prefix="/sources", tags=["sources"])


# Response Models
class SourceResponse(BaseModel):
    id: UUID
    name: str
    created_at: str

    class Config:
        from_attributes = True


class SourceModelResponse(BaseModel):
    id: UUID
    name: str
    description: str
    source_id: UUID
    created_at: str

    class Config:
        from_attributes = True


def get_source_usecase():
    """SourceManagementUseCase 의존성 함수"""
    return app_container.get_source_management_usecase()


@router.get("/", response_model=BaseResponse[List[SourceResponse]])
async def get_sources(
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_source_usecase),
):
    """모든 source를 조회합니다."""
    try:
        sources = await usecase.get_all_sources()

        return BaseResponse.success_response(
            data=[
                SourceResponse(
                    id=source.id,
                    name=source.name,
                    created_at=source.created_at.isoformat(),
                )
                for source in sources
            ],
            message="Source 목록을 성공적으로 조회했습니다.",
        )
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_dict
        )


@router.get("/{source_id}", response_model=BaseResponse[SourceResponse])
async def get_source(
    source_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_source_usecase),
):
    """특정 source를 조회합니다."""
    try:
        source = await usecase.get_source_by_id(source_id)

        return BaseResponse.success_response(
            data=SourceResponse(
                id=source.id,
                name=source.name,
                created_at=source.created_at.isoformat(),
            ),
            message="Source를 성공적으로 조회했습니다.",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_dict
        )


@router.get("/models", response_model=BaseResponse[List[SourceModelResponse]])
async def get_source_models(
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_source_usecase),
):
    """모든 source_model을 조회합니다."""
    try:
        source_models = await usecase.get_all_source_models()

        return BaseResponse.success_response(
            data=[
                SourceModelResponse(
                    id=source_model.id,
                    name=source_model.name,
                    description=source_model.description,
                    source_id=source_model.source_id,
                    created_at=source_model.created_at.isoformat(),
                )
                for source_model in source_models
            ],
            message="Source Model 목록을 성공적으로 조회했습니다.",
        )
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_dict
        )


@router.get(
    "/{source_id}/models", response_model=BaseResponse[List[SourceModelResponse]]
)
async def get_source_models_by_source(
    source_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_source_usecase),
):
    """특정 source의 모든 source_model을 조회합니다."""
    try:
        source_models = await usecase.get_source_models_by_source_id(source_id)

        return BaseResponse.success_response(
            data=[
                SourceModelResponse(
                    id=source_model.id,
                    name=source_model.name,
                    description=source_model.description,
                    source_id=source_model.source_id,
                    created_at=source_model.created_at.isoformat(),
                )
                for source_model in source_models
            ],
            message="Source별 Model 목록을 성공적으로 조회했습니다.",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_dict
        )
