"""
Prompt Lab API 메인 엔트리포인트
"""

from src.shared.web.app import create_app
from src.shared.web.server import main

# uvicorn main:app 명령어를 위한 app 객체 노출
app = create_app()

if __name__ == "__main__":
    main()
