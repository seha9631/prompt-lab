"""
Credential API Router
API 키 관리 CRUD 엔드포인트
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.shared.injector.container import app_container
from src.shared.security.dependencies import get_current_user
from src.shared.security.jwt_handler import TokenData
from src.shared.response.base_response import BaseResponse
from src.shared.exception.business_exception import BusinessException
from src.shared.exception.error_codes import ErrorCode

router = APIRouter(prefix="/credentials", tags=["credentials"])


# Request/Response Models
class CreateCredentialRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Credential 이름")
    source_id: UUID = Field(..., description="소스 ID")
    api_key: str = Field(..., min_length=1, description="API 키")


class UpdateCredentialRequest(BaseModel):
    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Credential 이름"
    )
    source_id: Optional[UUID] = Field(None, description="소스 ID")
    api_key: Optional[str] = Field(None, min_length=1, description="API 키")


class CredentialResponse(BaseModel):
    id: UUID
    team_id: UUID
    name: str
    source_id: UUID
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class DecryptApiKeyResponse(BaseModel):
    api_key: str


def get_credential_usecase():
    """CredentialManagementUseCase 의존성 함수"""
    return app_container.get_credential_management_usecase()


@router.post("/", response_model=BaseResponse[CredentialResponse])
async def create_credential(
    request: CreateCredentialRequest,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_credential_usecase),
):
    """새로운 credential을 생성합니다."""
    try:
        credential = await usecase.create_credential(
            team_id=current_user.team_id,
            name=request.name,
            source_id=request.source_id,
            api_key=request.api_key,
        )

        return BaseResponse.success_response(
            data=CredentialResponse(
                id=credential.id,
                team_id=credential.team_id,
                name=credential.name,
                source_id=credential.source_id,
                created_at=credential.created_at.isoformat(),
                updated_at=credential.updated_at.isoformat(),
            ),
            message="Credential이 성공적으로 생성되었습니다.",
        )
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_dict
        )


@router.get("/", response_model=BaseResponse[List[CredentialResponse]])
async def get_credentials(
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_credential_usecase),
):
    """팀의 모든 credential을 조회합니다."""
    try:
        credentials = await usecase.get_credentials_by_team(current_user.team_id)

        return BaseResponse.success_response(
            data=[
                CredentialResponse(
                    id=credential.id,
                    team_id=credential.team_id,
                    name=credential.name,
                    source_id=credential.source_id,
                    created_at=credential.created_at.isoformat(),
                    updated_at=credential.updated_at.isoformat(),
                )
                for credential in credentials
            ],
            message="Credential 목록을 성공적으로 조회했습니다.",
        )
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_dict
        )


@router.get(
    "/source/{source_id}", response_model=BaseResponse[List[CredentialResponse]]
)
async def get_credentials_by_source(
    source_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_credential_usecase),
):
    """특정 source의 credential을 조회합니다."""
    try:
        credentials = await usecase.get_credentials_by_source(
            current_user.team_id, source_id
        )

        return BaseResponse.success_response(
            data=[
                CredentialResponse(
                    id=credential.id,
                    team_id=credential.team_id,
                    name=credential.name,
                    source_id=credential.source_id,
                    created_at=credential.created_at.isoformat(),
                    updated_at=credential.updated_at.isoformat(),
                )
                for credential in credentials
            ],
            message="Source별 credential 목록을 성공적으로 조회했습니다.",
        )
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_dict
        )


@router.get("/{credential_id}", response_model=BaseResponse[CredentialResponse])
async def get_credential(
    credential_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_credential_usecase),
):
    """특정 credential을 조회합니다."""
    try:
        credential = await usecase.get_credential_by_id(
            credential_id, current_user.team_id
        )

        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.CREDENTIAL_NOT_FOUND.dict,
            )

        return BaseResponse.success_response(
            data=CredentialResponse(
                id=credential.id,
                team_id=credential.team_id,
                name=credential.name,
                source_id=credential.source_id,
                created_at=credential.created_at.isoformat(),
                updated_at=credential.updated_at.isoformat(),
            ),
            message="Credential을 성공적으로 조회했습니다.",
        )
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_dict
        )


@router.put("/{credential_id}", response_model=BaseResponse[CredentialResponse])
async def update_credential(
    credential_id: UUID,
    request: UpdateCredentialRequest,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_credential_usecase),
):
    """credential을 업데이트합니다."""
    try:
        credential = await usecase.update_credential(
            credential_id=credential_id,
            team_id=current_user.team_id,
            name=request.name,
            source_id=request.source_id,
            api_key=request.api_key,
        )

        return BaseResponse.success_response(
            data=CredentialResponse(
                id=credential.id,
                team_id=credential.team_id,
                name=credential.name,
                source_id=credential.source_id,
                created_at=credential.created_at.isoformat(),
                updated_at=credential.updated_at.isoformat(),
            ),
            message="Credential이 성공적으로 업데이트되었습니다.",
        )
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_dict
        )


@router.delete("/{credential_id}", response_model=BaseResponse[dict])
async def delete_credential(
    credential_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_credential_usecase),
):
    """credential을 삭제합니다."""
    try:
        success = await usecase.delete_credential(credential_id, current_user.team_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorCode.CREDENTIAL_NOT_FOUND.dict,
            )

        return BaseResponse.success_response(
            data={"deleted": True}, message="Credential이 성공적으로 삭제되었습니다."
        )
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_dict
        )


@router.post(
    "/{credential_id}/decrypt", response_model=BaseResponse[DecryptApiKeyResponse]
)
async def decrypt_api_key(
    credential_id: UUID,
    current_user: TokenData = Depends(get_current_user),
    usecase=Depends(get_credential_usecase),
):
    """credential의 API 키를 복호화합니다."""
    try:
        api_key = await usecase.decrypt_api_key(credential_id, current_user.team_id)

        return BaseResponse.success_response(
            data=DecryptApiKeyResponse(api_key=api_key),
            message="API 키가 성공적으로 복호화되었습니다.",
        )
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_dict
        )
