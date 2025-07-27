"""
커스텀 로그 포맷터
"""

import logging
import sys
from datetime import datetime
from typing import Optional


class ColorCodes:
    """ANSI 색상 코드"""

    RESET = "\033[0m"
    BOLD = "\033[1m"

    # 일반 색상
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # 밝은 색상
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


class CustomFormatter(logging.Formatter):
    """
    커스텀 로그 포맷터
    로그 레벨에 따라 색상을 다르게 표시하고, 보기 좋은 형태로 출력
    """

    def __init__(self, use_colors: bool = True):
        """
        Args:
            use_colors: 색상 사용 여부 (터미널이 색상을 지원하지 않을 경우 False)
        """
        self.use_colors = use_colors and self._supports_color()

        # 기본 포맷 - msg 필드 사용
        self.base_format = "[{asctime}] {levelname:<8} | {name:<20} | {msg}"

        # 로그 레벨별 색상 정의
        self.level_colors = {
            logging.DEBUG: ColorCodes.BRIGHT_BLACK,
            logging.INFO: ColorCodes.BRIGHT_BLUE,
            logging.WARNING: ColorCodes.BRIGHT_YELLOW,
            logging.ERROR: ColorCodes.BRIGHT_RED,
            logging.CRITICAL: ColorCodes.RED + ColorCodes.BOLD,
        }

        super().__init__(style="{")

    def _supports_color(self) -> bool:
        """터미널이 색상을 지원하는지 확인"""
        return (
            hasattr(sys.stderr, "isatty")
            and sys.stderr.isatty()
            and sys.platform != "win32"
        )

    def format(self, record: logging.LogRecord) -> str:
        """로그 레코드를 포맷팅"""
        # 시간 포맷 설정
        record.asctime = datetime.fromtimestamp(record.created).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # 로거 이름 단축 (너무 길면 축약)
        logger_name = record.name
        if len(logger_name) > 20:
            parts = logger_name.split(".")
            if len(parts) > 2:
                logger_name = f"{parts[0]}...{parts[-1]}"
        record.name = logger_name

        # 기본 메시지 포맷팅 - msg 필드 사용
        formatted_message = self.base_format.format(**record.__dict__)

        # 색상 적용
        if self.use_colors:
            color = self.level_colors.get(record.levelno, ColorCodes.WHITE)
            formatted_message = f"{color}{formatted_message}{ColorCodes.RESET}"

        # 예외 정보가 있으면 추가
        if record.exc_info:
            formatted_message += "\n" + self.formatException(record.exc_info)

        # 추가 필드가 있으면 표시
        extra_fields = self._get_extra_fields(record)
        if extra_fields:
            extra_str = " | ".join([f"{k}={v}" for k, v in extra_fields.items()])
            formatted_message += f" | {extra_str}"

        return formatted_message

    def _get_extra_fields(self, record: logging.LogRecord) -> dict:
        """로그 레코드에서 추가 필드 추출"""
        # 기본 필드들 제외
        standard_fields = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
            "exc_info",
            "exc_text",
            "stack_info",
            "asctime",
        }

        extra = {}
        for key, value in record.__dict__.items():
            if key not in standard_fields and not key.startswith("_"):
                extra[key] = value

        return extra
