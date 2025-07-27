"""
로거 설정 및 생성
"""

import logging
import sys
from typing import Optional
from .formatter import CustomFormatter


# 전역 로거 설정 상태
_logger_configured = False


def setup_logging(
    level: str = "INFO", use_colors: bool = True, format_style: str = "custom"
) -> None:
    """
    전역 로깅 설정

    Args:
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_colors: 색상 사용 여부
        format_style: 포맷 스타일 ("custom" 또는 "standard")
    """
    global _logger_configured

    if _logger_configured:
        return

    # 로그 레벨 설정
    log_level = getattr(logging, level.upper(), logging.INFO)

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 콘솔 핸들러 생성
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # 포맷터 설정
    if format_style == "custom":
        formatter = CustomFormatter(use_colors=use_colors)
    else:
        formatter = logging.Formatter(
            fmt="[%(asctime)s] %(levelname)-8s | %(name)-20s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 외부 라이브러리 로그 레벨 조정
    _configure_external_loggers()

    _logger_configured = True


def _configure_external_loggers() -> None:
    """외부 라이브러리의 로그 레벨 조정"""
    # SQLAlchemy 로그 레벨 조정
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.orm").setLevel(logging.WARNING)

    # FastAPI/Uvicorn 로그 레벨 조정
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    로거 인스턴스 가져오기

    Args:
        name: 로거 이름 (None이면 호출한 모듈의 이름 사용)

    Returns:
        Logger 인스턴스
    """
    if not _logger_configured:
        setup_logging()

    if name is None:
        # 호출한 모듈의 이름을 자동으로 사용
        import inspect

        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller_module = frame.f_back.f_globals.get("__name__", "unknown")
            name = caller_module
        else:
            name = "unknown"

    return logging.getLogger(name)


class LoggerMixin:
    """
    로거를 쉽게 사용할 수 있게 해주는 믹스인 클래스
    """

    @property
    def logger(self) -> logging.Logger:
        """클래스별 로거 인스턴스"""
        if not hasattr(self, "_logger"):
            class_name = self.__class__.__module__ + "." + self.__class__.__name__
            self._logger = get_logger(class_name)
        return self._logger


# 편의 함수들
def debug(message: str, **kwargs) -> None:
    """디버그 로그"""
    get_logger().debug(message, extra=kwargs)


def info(message: str, **kwargs) -> None:
    """정보 로그"""
    get_logger().info(message, extra=kwargs)


def warning(message: str, **kwargs) -> None:
    """경고 로그"""
    get_logger().warning(message, extra=kwargs)


def error(message: str, **kwargs) -> None:
    """에러 로그"""
    get_logger().error(message, extra=kwargs)


def critical(message: str, **kwargs) -> None:
    """치명적 에러 로그"""
    get_logger().critical(message, extra=kwargs)
