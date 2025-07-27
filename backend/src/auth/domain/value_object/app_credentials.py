import re
from typing import Any


class AppId:
    """앱 ID 값 객체"""
    
    def __init__(self, value: str):
        if not value or not value.strip():
            raise ValueError("App ID cannot be empty")
        
        # 영문, 숫자, 언더스코어, 하이픈만 허용, 3-50자
        if not re.match(r'^[a-zA-Z0-9_-]{3,50}$', value):
            raise ValueError(
                "App ID must be 3-50 characters long and contain only letters, numbers, underscores, and hyphens"
            )
        
        self.value = value.strip()
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AppId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)


class AppPassword:
    """앱 비밀번호 값 객체"""
    
    def __init__(self, value: str):
        if not value or not value.strip():
            raise ValueError("App password cannot be empty")
        
        # 최소 8자 이상
        if len(value) < 8:
            raise ValueError("App password must be at least 8 characters long")
        
        self.value = value.strip()
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AppPassword):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value) 