from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import traceback

from src.shared.injector.container import app_container
from src.shared.logging import setup_logging, get_logger
from src.shared.exception import BaseCustomException, ErrorCode


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 로깅 시스템 초기화
    setup_logging(level="INFO", use_colors=True)
    logger = get_logger(__name__)

    # 시작시 초기화
    logger.info("🚀 Starting application...")
    await app_container.initialize()
    logger.info("✅ Application initialized successfully!")

    yield

    # 종료시 정리
    logger.info("🛑 Shutting down application...")
    await app_container.shutdown()
    logger.info("✅ Application shutdown complete!")


async def custom_exception_handler(request: Request, exc: BaseCustomException):
    """커스텀 예외 핸들러"""
    logger = get_logger(__name__)

    # 에러 로그 출력
    logger.error(
        f"Custom exception occurred: {exc}",
        extra={
            "error_code": exc.error_code.code,
            "path": str(request.url),
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=(
            400
            if exc.error_code.code.startswith("E3")
            or exc.error_code.code.startswith("E5")
            or exc.error_code.code.startswith("E6")
            else 500
        ),
        content=exc.error_dict,
    )


async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 핸들러"""
    logger = get_logger(__name__)

    # 예상치 못한 에러 로그 출력
    logger.error(
        f"Unexpected exception occurred: {str(exc)}",
        extra={
            "path": str(request.url),
            "method": request.method,
            "traceback": traceback.format_exc(),
        },
    )

    # 일반 예외를 커스텀 예외로 변환
    error_response = BaseCustomException(
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        message="내부 서버 에러가 발생했습니다.",
        original_exception=exc,
    )

    return JSONResponse(status_code=500, content=error_response.error_dict)


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 생성 및 설정"""
    app = FastAPI(
        title="Prompt Lab API",
        description="DDD 구조로 구성된 사용자 및 팀 관리 API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # 예외 핸들러 등록
    app.add_exception_handler(BaseCustomException, custom_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # 헬스체크 엔드포인트
    @app.get("/")
    async def root():
        """헬스체크 엔드포인트"""
        logger = get_logger(__name__)
        logger.info("Health check requested")

        return {
            "message": "Prompt Lab API is running!",
            "status": "healthy",
            "version": "1.0.0",
        }

    # 라우터 등록
    from src.auth.presentation.router import auth_router
    from src.auth.presentation.credential_router import router as credential_router
    from src.auth.presentation.source_router import router as source_router

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(credential_router, prefix="/api/v1")
    app.include_router(source_router, prefix="/api/v1")

    return app
