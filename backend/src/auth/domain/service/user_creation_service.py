from uuid import UUID
from typing import Optional, Tuple
from ..entity.user import User
from ..entity.team import Team
from ..repository.user_repository import UserRepository
from ..repository.team_repository import TeamRepository
from ....shared.exception import (
    ResourceNotFoundException,
    DuplicateResourceException,
    ValidationException,
)


class UserCreationService:
    """사용자 생성 도메인 서비스"""

    def __init__(
        self, user_repository: UserRepository, team_repository: TeamRepository
    ):
        self.user_repository = user_repository
        self.team_repository = team_repository

    async def create_user_with_team_logic(
        self,
        name: str,
        app_id: str,
        app_password: str,
        team_name: Optional[str] = None,
        team_id: Optional[UUID] = None,
    ) -> Tuple[User, Optional[Team]]:
        """
        사용자 생성 비즈니스 로직

        Args:
            name: 사용자 이름
            app_id: 앱 ID
            app_password: 앱 비밀번호
            team_name: 새 팀 이름 (새 팀 생성시)
            team_id: 기존 팀 ID (기존 팀 참여시)

        Returns:
            Tuple[User, Optional[Team]]: (생성된 사용자, 생성된 팀 또는 None)

        Raises:
            ValueError: 잘못된 입력값
            Exception: 비즈니스 규칙 위반
        """

        # 1. 앱 ID 중복 확인
        if await self.user_repository.exists_by_app_id(app_id):
            raise DuplicateResourceException(
                resource_type="User",
                resource_id=app_id,
                message=f"앱 ID '{app_id}'가 이미 존재합니다",
            )

        # 2. 케이스 분기
        if team_id is not None:
            # 기존 팀에 참여하는 경우
            return await self._create_user_for_existing_team(
                name, app_id, app_password, team_id
            )
        else:
            # 새 팀을 생성하는 경우
            if not team_name:
                raise ValidationException(
                    message="새 팀을 생성할 때는 팀 이름이 필요합니다"
                )

            return await self._create_user_with_new_team(
                name, app_id, app_password, team_name
            )

    async def _create_user_for_existing_team(
        self, name: str, app_id: str, app_password: str, team_id: UUID
    ) -> Tuple[User, None]:
        """기존 팀에 사용자 추가"""

        # 1. 팀 존재 확인
        team = await self.team_repository.find_by_id(team_id)
        if team is None:
            raise ResourceNotFoundException(
                resource_type="Team",
                resource_id=str(team_id),
                message=f"ID '{team_id}'인 팀을 찾을 수 없습니다",
            )

        # 2. 팀이 활성화되어 있는지 확인
        if not team.is_active:
            raise ValidationException(message=f"팀 '{team.name}'이 비활성화 상태입니다")

        # 3. 'user' 권한으로 사용자 생성 (승인 대기 상태)
        user = User(
            name=name,
            app_id=app_id,
            app_password=app_password,
            team_id=team_id,
            role="user",  # 기존 팀 참여시는 항상 user 권한
            is_active=False,  # owner 승인 전까지는 비활성화 상태
        )

        return user, None

    async def _create_user_with_new_team(
        self, name: str, app_id: str, app_password: str, team_name: str
    ) -> Tuple[User, Team]:
        """새 팀과 함께 사용자 생성"""

        # 1. 팀 이름 중복 확인
        if await self.team_repository.exists_by_name(team_name):
            raise DuplicateResourceException(
                resource_type="Team",
                resource_id=team_name,
                message=f"팀 이름 '{team_name}'이 이미 존재합니다",
            )

        # 2. 새 팀 생성
        team = Team(name=team_name)

        # 3. 'owner' 권한으로 사용자 생성
        user = User(
            name=name,
            app_id=app_id,
            app_password=app_password,
            team_id=team.id,
            role="owner",  # 새 팀 생성시는 항상 owner 권한
        )

        return user, team

    async def validate_user_creation_data(
        self, name: str, app_id: str, app_password: str
    ) -> None:
        """사용자 생성 데이터 검증"""

        if not name or not name.strip():
            raise ValueError("User name cannot be empty")

        if len(name.strip()) < 2:
            raise ValueError("User name must be at least 2 characters long")

        if len(name.strip()) > 50:
            raise ValueError("User name cannot exceed 50 characters")

        # AppId, AppPassword는 값 객체에서 검증됨
        # 여기서는 추가적인 비즈니스 규칙만 검증
