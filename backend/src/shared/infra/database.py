"""
Database Connection Manager
데이터베이스 연결 관리
"""

import asyncpg
from databases import Database
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import Optional
from .models import Base


class DatabaseConnection:
    """SQLAlchemy & databases 혼용 데이터베이스 연결 관리 클래스"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.async_database_url = database_url.replace(
            "postgresql://", "postgresql+asyncpg://"
        )

        # databases 라이브러리용
        self.database: Optional[Database] = None

        # SQLAlchemy 용
        self.engine = None
        self.async_session_factory = None

    async def connect(self) -> Database:
        """databases 라이브러리 연결"""
        if self.database is None:
            self.database = Database(self.database_url)
            await self.database.connect()
        return self.database

    def get_sqlalchemy_engine(self):
        """SQLAlchemy 엔진 생성/반환"""
        if self.engine is None:
            self.engine = create_async_engine(
                self.async_database_url,
                echo=False,  # 개발시에는 True로 설정하면 SQL 쿼리 로그 확인 가능
                pool_pre_ping=True,
                pool_recycle=300,
            )

            self.async_session_factory = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )

        return self.engine

    def get_async_session(self) -> AsyncSession:
        """SQLAlchemy 비동기 세션 생성"""
        if self.async_session_factory is None:
            self.get_sqlalchemy_engine()

        return self.async_session_factory()

    async def disconnect(self) -> None:
        """연결 해제"""
        if self.database is not None:
            await self.database.disconnect()
            self.database = None

        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
            self.async_session_factory = None

    async def get_database(self) -> Database:
        """데이터베이스 인스턴스 반환"""
        if self.database is None:
            await self.connect()
        return self.database

    async def create_tables(self):
        """테이블 생성 (개발용)"""
        engine = self.get_sqlalchemy_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


# 싱글톤 인스턴스
from src.shared.config.settings import settings

db_connection = DatabaseConnection(settings.DATABASE_URL)
