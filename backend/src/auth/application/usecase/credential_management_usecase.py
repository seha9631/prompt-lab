"""
Credential 관리 Use Case
API 키 생성, 조회, 수정, 삭제 비즈니스 로직
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from src.auth.domain.entity.credential import Credential
from src.auth.domain.repository.credential_repository import CredentialRepository
from src.auth.domain.repository.team_repository import TeamRepository
from src.auth.domain.repository.source_repository import SourceRepository
from src.shared.exception.business_exception import BusinessException
from src.shared.exception.error_codes import ErrorCode
from src.shared.security.encryption import EncryptionService
from src.shared.security import APIKeyValidator


class CredentialManagementUseCase:
    """Credential 관리 Use Case"""

    def __init__(
        self,
        credential_repository_class,
        team_repository_class,
        source_repository_class,
        get_session_func,
    ):
        self.credential_repository_class = credential_repository_class
        self.team_repository_class = team_repository_class
        self.source_repository_class = source_repository_class
        self.get_session_func = get_session_func

    async def _get_repositories(self):
        """새로운 세션으로 repository들을 생성합니다."""
        session = self.get_session_func()
        return (
            self.credential_repository_class(session),
            self.team_repository_class(session),
            self.source_repository_class(session),
        ), session

    async def create_credential(
        self, team_id: UUID, name: str, source_id: UUID, api_key: str
    ) -> Credential:
        """새로운 credential을 생성합니다."""
        (credential_repo, team_repo, source_repo), session = (
            await self._get_repositories()
        )

        try:
            # 팀 존재 확인
            team = await team_repo.find_by_id(team_id)
            if not team:
                raise BusinessException(
                    ErrorCode.TEAM_NOT_FOUND, "팀을 찾을 수 없습니다."
                )

            # source 존재 확인
            source = await source_repo.find_by_id(source_id)
            if not source:
                raise BusinessException(
                    ErrorCode.SOURCE_NOT_FOUND, "소스를 찾을 수 없습니다."
                )

            # 팀 내에서 동일한 이름의 credential이 있는지 확인
            existing_credential = await credential_repo.find_by_team_and_name(
                team_id, name
            )
            if existing_credential:
                raise BusinessException(
                    ErrorCode.CREDENTIAL_ALREADY_EXISTS,
                    "동일한 이름의 credential이 이미 존재합니다.",
                )

            # API 키 유효성 검증
            is_valid = await APIKeyValidator.validate_api_key(source.name, api_key)
            if not is_valid:
                raise BusinessException(
                    ErrorCode.API_KEY_VALIDATION_ERROR,
                    "API 키가 유효하지 않습니다. 키를 확인하고 다시 시도해주세요.",
                )

            # API 키 암호화
            encrypted_api_key = EncryptionService.encrypt_api_key(api_key, str(team_id))

            # credential 생성
            credential = Credential(
                id=uuid4(),
                team_id=team_id,
                name=name,
                source_id=source_id,
                api_key=encrypted_api_key,
                created_at=datetime.utcnow(),
            )

            return await credential_repo.create(credential)
        finally:
            await session.close()

    async def get_credential_by_id(
        self, credential_id: UUID, team_id: UUID
    ) -> Optional[Credential]:
        """ID로 credential을 조회합니다."""
        (credential_repo, _, _), session = await self._get_repositories()

        try:
            credential = await credential_repo.find_by_id(credential_id)

            if not credential:
                return None

            # 팀 소유권 확인 (타입 안전한 비교)
            if str(credential.team_id) != str(team_id):
                raise BusinessException(
                    ErrorCode.UNAUTHORIZED, "해당 credential에 접근할 권한이 없습니다."
                )

            return credential
        finally:
            await session.close()

    async def get_credentials_by_team(self, team_id: UUID) -> List[Credential]:
        """팀의 모든 credential을 조회합니다."""
        (credential_repo, team_repo, _), session = await self._get_repositories()

        try:
            # 팀 존재 확인
            team = await team_repo.find_by_id(team_id)
            if not team:
                raise BusinessException(
                    ErrorCode.TEAM_NOT_FOUND, "팀을 찾을 수 없습니다."
                )

            return await credential_repo.find_by_team_id(team_id)
        finally:
            await session.close()

    async def get_credentials_by_source(
        self, team_id: UUID, source_id: UUID
    ) -> List[Credential]:
        """팀의 특정 source에 대한 credential을 조회합니다."""
        (credential_repo, team_repo, source_repo), session = (
            await self._get_repositories()
        )

        try:
            # 팀 존재 확인
            team = await team_repo.find_by_id(team_id)
            if not team:
                raise BusinessException(
                    ErrorCode.TEAM_NOT_FOUND, "팀을 찾을 수 없습니다."
                )

            # source 존재 확인
            source = await source_repo.find_by_id(source_id)
            if not source:
                raise BusinessException(
                    ErrorCode.SOURCE_NOT_FOUND, "소스를 찾을 수 없습니다."
                )

            return await credential_repo.find_by_team_and_source(team_id, source_id)
        finally:
            await session.close()

    async def update_credential(
        self,
        credential_id: UUID,
        team_id: UUID,
        name: Optional[str] = None,
        source_id: Optional[UUID] = None,
        api_key: Optional[str] = None,
    ) -> Credential:
        """credential을 업데이트합니다."""
        (credential_repo, _, source_repo), session = await self._get_repositories()

        try:
            # credential 조회 및 소유권 확인
            credential = await self.get_credential_by_id(credential_id, team_id)
            if not credential:
                raise BusinessException(
                    ErrorCode.CREDENTIAL_NOT_FOUND, "Credential을 찾을 수 없습니다."
                )

            # 업데이트할 필드 검증 및 적용
            if name is not None:
                # 동일한 이름의 다른 credential이 있는지 확인
                existing_credential = await credential_repo.find_by_team_and_name(
                    team_id, name
                )
                if existing_credential and existing_credential.id != credential_id:
                    raise BusinessException(
                        ErrorCode.CREDENTIAL_ALREADY_EXISTS,
                        "동일한 이름의 credential이 이미 존재합니다.",
                    )
                credential.update_name(name)

            if source_id is not None:
                # source 존재 확인
                source = await source_repo.find_by_id(source_id)
                if not source:
                    raise BusinessException(
                        ErrorCode.SOURCE_NOT_FOUND, "소스를 찾을 수 없습니다."
                    )
                credential.update_source(source_id)

            if api_key is not None:
                # API 키 유효성 검증
                # source 정보가 필요한데, source_id가 변경되지 않았다면 기존 source_id 사용
                current_source_id = (
                    source_id if source_id is not None else credential.source_id
                )
                current_source = await source_repo.find_by_id(current_source_id)
                if not current_source:
                    raise BusinessException(
                        ErrorCode.SOURCE_NOT_FOUND, "소스를 찾을 수 없습니다."
                    )

                is_valid = await APIKeyValidator.validate_api_key(
                    current_source.name, api_key
                )
                if not is_valid:
                    raise BusinessException(
                        ErrorCode.API_KEY_VALIDATION_ERROR,
                        "API 키가 유효하지 않습니다. 키를 확인하고 다시 시도해주세요.",
                    )

                # API 키 암호화
                encrypted_api_key = EncryptionService.encrypt_api_key(
                    api_key, str(team_id)
                )
                credential.update_api_key(encrypted_api_key)

            return await credential_repo.update(credential)
        finally:
            await session.close()

    async def delete_credential(self, credential_id: UUID, team_id: UUID) -> bool:
        """credential을 삭제합니다."""
        (credential_repo, _, _), session = await self._get_repositories()

        try:
            # credential 조회 및 소유권 확인
            credential = await self.get_credential_by_id(credential_id, team_id)
            if not credential:
                raise BusinessException(
                    ErrorCode.CREDENTIAL_NOT_FOUND, "Credential을 찾을 수 없습니다."
                )

            return await credential_repo.delete(credential_id)
        finally:
            await session.close()

    async def decrypt_api_key(self, credential_id: UUID, team_id: UUID) -> str:
        """credential의 API 키를 복호화합니다."""
        credential = await self.get_credential_by_id(credential_id, team_id)
        if not credential:
            raise BusinessException(
                ErrorCode.CREDENTIAL_NOT_FOUND, "Credential을 찾을 수 없습니다."
            )

        try:
            return EncryptionService.decrypt_api_key(credential.api_key, str(team_id))
        except ValueError as e:
            raise BusinessException(
                ErrorCode.ENCRYPTION_ERROR, f"API 키 복호화에 실패했습니다: {str(e)}"
            )
