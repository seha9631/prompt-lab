import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from src.shared.injector.container import app_container
from src.auth.application.usecase.create_user_usecase import (
    CreateUserWithTeamRequest,
    CreateUserForTeamRequest,
    CreateUserUseCase,
)


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


# FastAPI 앱 생성
app = FastAPI(
    title="Prompt Lab API",
    description="DDD 구조로 구성된 사용자 및 팀 관리 API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """헬스체크 엔드포인트"""
    return {
        "message": "Prompt Lab API is running!",
        "status": "healthy",
        "version": "1.0.0",
    }


@app.post("/auth/users/create-with-team")
async def create_user_with_team(request: CreateUserWithTeamRequest):
    """새 팀과 함께 사용자 생성"""
    try:
        usecase: CreateUserUseCase = app_container.get_create_user_usecase()
        response = await usecase.create_user_with_new_team(request)

        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/users/create-for-team")
async def create_user_for_team(request: CreateUserForTeamRequest):
    """기존 팀에 사용자 추가"""
    try:
        usecase: CreateUserUseCase = app_container.get_create_user_usecase()
        response = await usecase.create_user_for_existing_team(request)

        if not response.success:
            raise HTTPException(status_code=400, detail=response.error)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/auth/users/{app_id}")
async def get_user_by_app_id(app_id: str):
    """앱 ID로 사용자 조회"""
    try:
        usecase: CreateUserUseCase = app_container.get_create_user_usecase()
        response = await usecase.get_user_by_app_id(app_id)

        if not response.success:
            raise HTTPException(status_code=404, detail=response.error)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def main():
    """메인 함수"""
    print("🔥 Starting Prompt Lab API Server...")

    # 서버 설정
    config = uvicorn.Config(
        app=app, host="0.0.0.0", port=8000, log_level="info", reload=False
    )

    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
