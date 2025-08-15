from databases import Database
from typing import Dict, Any

from src.shared.infra.database import db_connection
from src.auth.domain.service.user_creation_service import UserCreationService
from src.auth.application.service.user_management_service import UserManagementService
from src.auth.application.usecase.create_user_usecase import CreateUserUseCase
from src.auth.application.usecase.approve_user_usecase import ApproveUserUseCase
from src.auth.application.usecase.authentication_usecase import AuthenticationUseCase
from src.auth.application.usecase.team_management_usecase import TeamManagementUseCase
from src.auth.application.usecase.credential_management_usecase import (
    CredentialManagementUseCase,
)
from src.auth.application.usecase.source_management_usecase import (
    SourceManagementUseCase,
)
from src.llm.application.service.llm_management_service import LLMManagementService
from src.llm.application.usecase.llm_management_usecase import LLMManagementUseCase
from src.auth.application.service.authentication_service import AuthenticationService
from src.auth.infra.repository.postgres.user_repository_impl import UserRepositoryImpl
from src.auth.infra.repository.postgres.team_repository_impl import TeamRepositoryImpl
from src.auth.infra.repository.postgres.credential_repository_impl import (
    CredentialRepositoryImpl,
)
from src.auth.infra.repository.postgres.source_repository_impl import (
    SourceRepositoryImpl,
)
from src.auth.infra.repository.postgres.source_model_repository_impl import (
    SourceModelRepositoryImpl,
)
from src.llm.infra.repository.postgres.llm_request_repository_impl import (
    LLMRequestRepositoryImpl,
)


class AppContainer:
    """애플리케이션 DI 컨테이너 (PostgreSQL + SQLAlchemy 기반)"""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._initialized = False

    async def initialize(self):
        """컨테이너 초기화"""
        if self._initialized:
            return

        # 1. 데이터베이스 연결 (SQLAlchemy & databases 혼용)
        database = await db_connection.get_database()  # databases 라이브러리용
        sqlalchemy_engine = db_connection.get_sqlalchemy_engine()  # SQLAlchemy용

        self._services["database"] = database
        self._services["sqlalchemy_engine"] = sqlalchemy_engine

        # 2. SQLAlchemy 세션 팩토리
        self._services["get_session"] = db_connection.get_async_session

        # 3. Repository 클래스들 (PostgreSQL 구현체)
        self._services["user_repository_class"] = UserRepositoryImpl
        self._services["team_repository_class"] = TeamRepositoryImpl
        self._services["credential_repository_class"] = CredentialRepositoryImpl
        self._services["source_repository_class"] = SourceRepositoryImpl
        self._services["source_model_repository_class"] = SourceModelRepositoryImpl

        # 4. Domain Service 계층 (기본 인스턴스 - 필요시 재생성)
        # 실제로는 각 요청마다 새 세션으로 새 Repository를 만들어 사용
        dummy_session = None  # 실제 사용시에는 새 세션으로 교체됨
        user_creation_service = UserCreationService(
            user_repository=None,  # 실제 사용시 교체
            team_repository=None,  # 실제 사용시 교체
        )
        self._services["user_creation_service"] = user_creation_service

        # 5. Application Service 계층
        user_management_service = UserManagementService(
            get_session_func=self._services["get_session"],
            user_repository_class=UserRepositoryImpl,  # PostgreSQL 구현체
            team_repository_class=TeamRepositoryImpl,  # PostgreSQL 구현체
            user_creation_service=user_creation_service,  # 이것은 참조용, 실제로는 내부에서 새로 생성
        )
        self._services["user_management_service"] = user_management_service

        # 6. Use Case 계층
        create_user_usecase = CreateUserUseCase(
            user_management_service=user_management_service
        )
        self._services["create_user_usecase"] = create_user_usecase

        approve_user_usecase = ApproveUserUseCase(
            user_management_service=user_management_service
        )
        self._services["approve_user_usecase"] = approve_user_usecase

        # 7. 인증 서비스 및 UseCase
        authentication_service = AuthenticationService(
            user_repository_class=UserRepositoryImpl
        )
        self._services["authentication_service"] = authentication_service

        authentication_usecase = AuthenticationUseCase(
            authentication_service=authentication_service,
            get_session_func=self._services["get_session"],
        )
        self._services["authentication_usecase"] = authentication_usecase

        # 8. 팀 관리 UseCase
        team_management_usecase = TeamManagementUseCase(
            user_management_service=user_management_service
        )
        self._services["team_management_usecase"] = team_management_usecase

        # 9. Credential 관리 UseCase
        credential_management_usecase = CredentialManagementUseCase(
            credential_repository_class=CredentialRepositoryImpl,
            team_repository_class=TeamRepositoryImpl,
            source_repository_class=SourceRepositoryImpl,
            get_session_func=self._services["get_session"],
        )
        self._services["credential_management_usecase"] = credential_management_usecase

        # 10. Source 관리 UseCase
        source_management_usecase = SourceManagementUseCase(
            source_repository_class=SourceRepositoryImpl,
            source_model_repository_class=SourceModelRepositoryImpl,
            get_session_func=self._services["get_session"],
        )
        self._services["source_management_usecase"] = source_management_usecase

        # 11. LLM 관리 서비스 및 UseCase
        llm_management_service = LLMManagementService(
            llm_request_repository_class=LLMRequestRepositoryImpl,
            credential_repository_class=CredentialRepositoryImpl,
            source_repository_class=SourceRepositoryImpl,
            get_session_func=self._services["get_session"],
            upload_dir="uploads",
        )
        self._services["llm_management_service"] = llm_management_service

        llm_management_usecase = LLMManagementUseCase(
            llm_management_service=llm_management_service
        )
        self._services["llm_management_usecase"] = llm_management_usecase

        self._initialized = True

    async def shutdown(self):
        """컨테이너 정리"""
        if "database" in self._services:
            await db_connection.disconnect()
        self._services.clear()
        self._initialized = False

    def get(self, service_name: str) -> Any:
        """서비스 조회"""
        if not self._initialized:
            raise RuntimeError("Container not initialized. Call initialize() first.")

        if service_name not in self._services:
            raise KeyError(f"Service '{service_name}' not found in container")

        return self._services[service_name]

    # 편의 메서드들
    def get_database(self) -> Database:
        return self.get("database")

    def get_create_user_usecase(self) -> CreateUserUseCase:
        return self.get("create_user_usecase")

    def get_approve_user_usecase(self) -> ApproveUserUseCase:
        return self.get("approve_user_usecase")

    def get_authentication_usecase(self) -> AuthenticationUseCase:
        return self.get("authentication_usecase")

    def get_team_management_usecase(self) -> TeamManagementUseCase:
        return self.get("team_management_usecase")

    def get_credential_management_usecase(self) -> CredentialManagementUseCase:
        return self.get("credential_management_usecase")

    def get_source_management_usecase(self) -> SourceManagementUseCase:
        return self.get("source_management_usecase")

    def get_llm_management_service(self) -> LLMManagementService:
        return self.get("llm_management_service")

    def get_llm_management_usecase(self) -> LLMManagementUseCase:
        return self.get("llm_management_usecase")

    def get_session_factory(self):
        """SQLAlchemy 세션 팩토리 반환"""
        return self.get("get_session")


# 싱글톤 인스턴스
app_container = AppContainer()
