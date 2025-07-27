from databases import Database
from typing import Dict, Any

from ...shared.infra.database import db_connection
from ...auth.domain.service.user_creation_service import UserCreationService
from ...auth.application.service.user_management_service import UserManagementService
from ...auth.application.usecase.create_user_usecase import CreateUserUseCase
from ...auth.infra.repository.postgres.user_repository_impl import UserRepositoryImpl
from ...auth.infra.repository.postgres.team_repository_impl import TeamRepositoryImpl


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
        
        self._services['database'] = database
        self._services['sqlalchemy_engine'] = sqlalchemy_engine
        
        # 2. SQLAlchemy 세션 팩토리
        self._services['get_session'] = db_connection.get_async_session
        
        # 3. Repository 클래스들 (PostgreSQL 구현체)
        self._services['user_repository_class'] = UserRepositoryImpl
        self._services['team_repository_class'] = TeamRepositoryImpl
        
        # 4. Domain Service 계층 (기본 인스턴스 - 필요시 재생성)
        # 실제로는 각 요청마다 새 세션으로 새 Repository를 만들어 사용
        dummy_session = None  # 실제 사용시에는 새 세션으로 교체됨
        user_creation_service = UserCreationService(
            user_repository=None,  # 실제 사용시 교체
            team_repository=None   # 실제 사용시 교체
        )
        self._services['user_creation_service'] = user_creation_service
        
        # 5. Application Service 계층
        user_management_service = UserManagementService(
            get_session_func=self._services['get_session'],
            user_repository_class=UserRepositoryImpl,  # PostgreSQL 구현체
            team_repository_class=TeamRepositoryImpl,  # PostgreSQL 구현체
            user_creation_service=user_creation_service  # 이것은 참조용, 실제로는 내부에서 새로 생성
        )
        self._services['user_management_service'] = user_management_service
        
        # 6. Use Case 계층
        create_user_usecase = CreateUserUseCase(
            user_management_service=user_management_service
        )
        self._services['create_user_usecase'] = create_user_usecase
        
        self._initialized = True
    
    async def shutdown(self):
        """컨테이너 정리"""
        if 'database' in self._services:
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
        return self.get('database')
    
    def get_create_user_usecase(self) -> CreateUserUseCase:
        return self.get('create_user_usecase')
    
    def get_session_factory(self):
        """SQLAlchemy 세션 팩토리 반환"""
        return self.get('get_session')


# 싱글톤 인스턴스
app_container = AppContainer() 