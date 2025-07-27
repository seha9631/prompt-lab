import asyncio
import uvicorn
from .app import create_app
from src.shared.logging import get_logger


async def run_server():
    """서버 실행"""
    logger = get_logger(__name__)
    logger.info("🔥 Starting Prompt Lab API Server...")

    app = create_app()

    # 서버 설정
    config = uvicorn.Config(
        app=app, host="0.0.0.0", port=8000, log_level="info", reload=False
    )

    server = uvicorn.Server(config)
    await server.serve()


def main():
    """메인 엔트리포인트"""
    asyncio.run(run_server())
