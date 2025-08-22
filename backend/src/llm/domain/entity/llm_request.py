"""
LLM 요청 도메인 엔티티
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID


class LLMRequest:
    """LLM 요청을 나타내는 도메인 엔티티"""

    def __init__(
        self,
        id: UUID,
        team_id: UUID,
        user_id: UUID,
        project_id: UUID,
        system_prompt: str,
        question: str,
        model_name: str,
        file_paths: Optional[List[str]] = None,
        status: str = "pending",  # pending, processing, completed, failed
        result: Optional[str] = None,
        error_message: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.team_id = team_id
        self.user_id = user_id
        self.project_id = project_id
        self.system_prompt = system_prompt
        self.question = question
        self.model_name = model_name
        self.file_paths = file_paths or []
        self.status = status
        self.result = result
        self.error_message = error_message
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update_status(
        self,
        status: str,
        result: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """요청 상태를 업데이트합니다."""
        self.status = status
        if result is not None:
            self.result = result
        if error_message is not None:
            self.error_message = error_message
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"LLMRequest(id={self.id}, team_id={self.team_id}, project_id={self.project_id}, model='{self.model_name}', status='{self.status}')"
