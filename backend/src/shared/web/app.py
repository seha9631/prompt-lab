from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.shared.injector.container import app_container


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작시 초기화
    print("🚀 Starting application...")
    await app_container.initialize()
    print("✅ Application initialized successfully!")

    yield

    # 종료시 정리
    print("🛑 Shutting down application...")
    await app_container.shutdown()
    print("✅ Application shutdown complete!")


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 생성 및 설정"""
    app = FastAPI(
        title="Prompt Lab API",
        description="DDD 구조로 구성된 사용자 및 팀 관리 API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # 헬스체크 엔드포인트
    @app.get("/")
    async def root():
        """헬스체크 엔드포인트"""
        return {
            "message": "Prompt Lab API is running!",
            "status": "healthy",
            "version": "1.0.0",
        }

    # 라우터 등록
    from src.auth.presentation.router import auth_router

    app.include_router(auth_router, prefix="/api/v1")

    return app
