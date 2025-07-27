"""
애플리케이션 에러 코드 정의
"""

from enum import Enum


class ErrorCode(Enum):
    """에러 코드 열거형"""

    # === 일반적인 에러 (1000번대) ===
    UNKNOWN_ERROR = ("E1000", "알 수 없는 에러가 발생했습니다.")
    INTERNAL_SERVER_ERROR = ("E1001", "내부 서버 에러가 발생했습니다.")
    INVALID_REQUEST = ("E1002", "잘못된 요청입니다.")

    # === 인증/인가 에러 (2000번대) ===
    AUTHENTICATION_FAILED = ("E2001", "인증에 실패했습니다.")
    AUTHORIZATION_FAILED = ("E2002", "권한이 없습니다.")
    INVALID_CREDENTIALS = ("E2003", "잘못된 인증 정보입니다.")
    TOKEN_EXPIRED = ("E2004", "토큰이 만료되었습니다.")
    INVALID_TOKEN = ("E2005", "유효하지 않은 토큰입니다.")
    TOKEN_REFRESH_FAILED = ("E2006", "토큰 갱신에 실패했습니다.")
    USER_NOT_ACTIVE = ("E2007", "비활성화된 사용자입니다.")

    # === 유효성 검증 에러 (3000번대) ===
    VALIDATION_ERROR = ("E3001", "유효성 검증에 실패했습니다.")
    REQUIRED_FIELD_MISSING = ("E3002", "필수 필드가 누락되었습니다.")
    INVALID_FORMAT = ("E3003", "잘못된 형식입니다.")
    INVALID_LENGTH = ("E3004", "길이가 유효하지 않습니다.")

    # === 리소스 관련 에러 (4000번대) ===
    RESOURCE_NOT_FOUND = ("E4001", "리소스를 찾을 수 없습니다.")
    RESOURCE_ALREADY_EXISTS = ("E4002", "이미 존재하는 리소스입니다.")
    RESOURCE_CONFLICT = ("E4003", "리소스 충돌이 발생했습니다.")

    # === 사용자 관련 에러 (5000번대) ===
    USER_NOT_FOUND = ("E5001", "사용자를 찾을 수 없습니다.")
    USER_ALREADY_EXISTS = ("E5002", "이미 존재하는 사용자입니다.")
    INVALID_USER_DATA = ("E5003", "잘못된 사용자 데이터입니다.")
    USER_APPROVAL_FAILED = ("E5004", "사용자 승인에 실패했습니다.")
    USER_ALREADY_ACTIVE = ("E5005", "사용자가 이미 활성화되어 있습니다.")
    INSUFFICIENT_PERMISSION = ("E5006", "권한이 부족합니다.")
    TEAM_MISMATCH = ("E5007", "팀이 일치하지 않습니다.")

    # === 팀 관련 에러 (6000번대) ===
    TEAM_NOT_FOUND = ("E6001", "팀을 찾을 수 없습니다.")
    TEAM_ALREADY_EXISTS = ("E6002", "이미 존재하는 팀입니다.")
    TEAM_MEMBER_LIMIT_EXCEEDED = ("E6003", "팀 멤버 수 제한을 초과했습니다.")

    # === 데이터베이스 에러 (7000번대) ===
    DATABASE_CONNECTION_ERROR = ("E7001", "데이터베이스 연결에 실패했습니다.")
    DATABASE_QUERY_ERROR = ("E7002", "데이터베이스 쿼리 실행에 실패했습니다.")
    DATABASE_TRANSACTION_ERROR = ("E7003", "데이터베이스 트랜잭션 처리에 실패했습니다.")

    # === 외부 서비스 에러 (8000번대) ===
    EXTERNAL_SERVICE_ERROR = ("E8001", "외부 서비스 호출에 실패했습니다.")
    EXTERNAL_SERVICE_TIMEOUT = ("E8002", "외부 서비스 요청이 시간 초과되었습니다.")
    EXTERNAL_SERVICE_UNAVAILABLE = ("E8003", "외부 서비스를 사용할 수 없습니다.")

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    @property
    def dict(self) -> dict:
        """에러 코드를 딕셔너리로 반환"""
        return {"code": self.code, "message": self.message}
