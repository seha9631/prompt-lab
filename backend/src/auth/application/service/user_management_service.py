"""
User Management Application Service
사용자 관리 애플리케이션 서비스
"""

from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.domain.entity.user import User
from src.auth.domain.entity.team import Team
from src.auth.domain.service.user_creation_service import UserCreationService
from src.auth.domain.repository.user_repository import UserRepository
from src.auth.domain.repository.team_repository import TeamRepository
from src.auth.domain.value_object.app_credentials import AppId, AppPassword
from src.shared.exception import (
    ValidationException,
    DuplicateResourceException,
    ResourceNotFoundException,
    UserApprovalException,
    UserAlreadyActiveException,
    InsufficientPermissionException,
    TeamMismatchException,
    UserRoleChangeException,
    LastOwnerProtectionException,
    InvalidRoleException,
)


class UserManagementService:
    """사용자 관리 애플리케이션 서비스 (SQLAlchemy 기반)"""

    def __init__(
        self,
        get_session_func,  # 세션 팩토리 함수
        user_repository_class,
        team_repository_class,
        user_creation_service: UserCreationService,
    ):
        self.get_session = get_session_func
        self.user_repository_class = user_repository_class
        self.team_repository_class = team_repository_class
        self.user_creation_service = user_creation_service

    async def create_user_with_team(
        self, name: str, app_id: str, app_password: str, team_name: str
    ) -> dict:
        """
        새 팀과 함께 사용자 생성 (owner 권한)

        Args:
            name: 사용자 이름
            app_id: 앱 ID (이메일)
            app_password: 앱 비밀번호
            team_name: 새 팀 이름

        Returns:
            dict: 생성된 사용자 및 팀 정보
        """

        # SQLAlchemy 세션으로 트랜잭션 관리
        async with self.get_session() as session:
            try:
                # Repository 인스턴스 생성
                user_repo = self.user_repository_class(session)
                team_repo = self.team_repository_class(session)

                # UserCreationService에 새로운 Repository 주입
                creation_service = UserCreationService(user_repo, team_repo)

                # 1. 입력값 검증
                await creation_service.validate_user_creation_data(
                    name, app_id, app_password
                )

                # 값 객체로 검증 및 비밀번호 해싱
                app_id_vo = AppId(app_id)
                app_password_vo = AppPassword(app_password)
                hashed_password = app_password_vo.hash()

                # 2. 도메인 서비스로 사용자 및 팀 생성 (해싱된 비밀번호 전달)
                user, team = await creation_service.create_user_with_team_logic(
                    name=name.strip(),
                    app_id=str(app_id_vo),
                    app_password=hashed_password,  # 해싱된 비밀번호 사용
                    team_name=team_name.strip(),
                )

                # 3. 팀 저장
                saved_team = await team_repo.save(team)

                # 4. 사용자 저장
                saved_user = await user_repo.save(user)

                # 5. 트랜잭션 커밋
                await session.commit()

                return {
                    "user": {
                        "id": str(saved_user.id),
                        "name": saved_user.name,
                        "app_id": saved_user.app_id,
                        "role": saved_user.role,
                        "team_id": str(saved_user.team_id),
                        "is_active": saved_user.is_active,
                        "created_at": saved_user.created_at.isoformat(),
                        "updated_at": saved_user.updated_at.isoformat(),
                    },
                    "team": {
                        "id": str(saved_team.id),
                        "name": saved_team.name,
                        "payment": saved_team.payment,
                        "is_active": saved_team.is_active,
                        "created_at": saved_team.created_at.isoformat(),
                        "updated_at": saved_team.updated_at.isoformat(),
                    },
                }

            except Exception as e:
                await session.rollback()
                raise e

    async def create_user_for_existing_team(
        self, name: str, app_id: str, app_password: str, team_id: UUID
    ) -> dict:
        """
        기존 팀에 사용자 추가 (user 권한)

        Args:
            name: 사용자 이름
            app_id: 앱 ID (이메일)
            app_password: 앱 비밀번호
            team_id: 기존 팀 ID

        Returns:
            dict: 생성된 사용자 정보
        """

        # SQLAlchemy 세션으로 트랜잭션 관리
        async with self.get_session() as session:
            try:
                # Repository 인스턴스 생성
                user_repo = self.user_repository_class(session)
                team_repo = self.team_repository_class(session)

                # UserCreationService에 새로운 Repository 주입
                creation_service = UserCreationService(user_repo, team_repo)

                # 1. 입력값 검증
                await creation_service.validate_user_creation_data(
                    name, app_id, app_password
                )

                # 값 객체로 검증 및 비밀번호 해싱
                app_id_vo = AppId(app_id)
                app_password_vo = AppPassword(app_password)
                hashed_password = app_password_vo.hash()

                # 2. 도메인 서비스로 사용자 생성 (해싱된 비밀번호 전달)
                user, _ = await creation_service.create_user_with_team_logic(
                    name=name.strip(),
                    app_id=str(app_id_vo),
                    app_password=hashed_password,  # 해싱된 비밀번호 사용
                    team_id=team_id,
                )

                # 3. 사용자 저장
                saved_user = await user_repo.save(user)

                # 4. 팀 정보 조회 (응답에 포함하기 위해)
                team = await team_repo.find_by_id(team_id)

                # 5. 트랜잭션 커밋
                await session.commit()

                return {
                    "user": {
                        "id": str(saved_user.id),
                        "name": saved_user.name,
                        "app_id": saved_user.app_id,
                        "role": saved_user.role,
                        "team_id": str(saved_user.team_id),
                        "is_active": saved_user.is_active,
                        "created_at": saved_user.created_at.isoformat(),
                        "updated_at": saved_user.updated_at.isoformat(),
                    },
                    "team": (
                        {
                            "id": str(team.id),
                            "name": team.name,
                            "payment": team.payment,
                            "is_active": team.is_active,
                        }
                        if team
                        else None
                    ),
                }

            except Exception as e:
                await session.rollback()
                raise e

    async def get_user_by_app_id(self, app_id: str) -> Optional[dict]:
        """앱 ID로 사용자 조회"""

        async with self.get_session() as session:
            user_repo = self.user_repository_class(session)
            team_repo = self.team_repository_class(session)

            user = await user_repo.find_by_app_id(app_id)
            if user is None:
                return None

            # 팀 정보도 함께 조회
            team = await team_repo.find_by_id(user.team_id)

            return {
                "user": {
                    "id": str(user.id),
                    "name": user.name,
                    "app_id": user.app_id,
                    "role": user.role,
                    "team_id": str(user.team_id),
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat(),
                    "updated_at": user.updated_at.isoformat(),
                },
                "team": (
                    {
                        "id": str(team.id),
                        "name": team.name,
                        "payment": team.payment,
                        "is_active": team.is_active,
                    }
                    if team
                    else None
                ),
            }

    async def approve_user(self, user_id: UUID, owner_user_id: UUID) -> dict:
        """
        사용자 승인 (owner만 가능)

        Args:
            user_id: 승인할 사용자 ID
            owner_user_id: 승인하는 owner의 사용자 ID

        Returns:
            dict: 승인된 사용자 정보
        """
        async with self.get_session() as session:
            try:
                user_repo = self.user_repository_class(session)
                team_repo = self.team_repository_class(session)

                # 1. 승인할 사용자 조회
                user_to_approve = await user_repo.find_by_id(user_id)
                if user_to_approve is None:
                    raise ResourceNotFoundException(
                        resource_type="User",
                        resource_id=str(user_id),
                        message=f"ID '{user_id}'인 사용자를 찾을 수 없습니다",
                    )

                # 2. 승인하는 사용자 조회 (owner 권한 확인)
                approver = await user_repo.find_by_id(owner_user_id)
                if approver is None:
                    raise ResourceNotFoundException(
                        resource_type="User",
                        resource_id=str(owner_user_id),
                        message=f"ID '{owner_user_id}'인 승인자를 찾을 수 없습니다",
                    )

                # 3. 승인하는 사용자가 owner인지 확인
                if approver.role != "owner":
                    raise InsufficientPermissionException(
                        message="팀 소유자만 사용자를 승인할 수 있습니다",
                        required_role="owner",
                        current_role=approver.role,
                    )

                # 4. 같은 팀인지 확인
                if approver.team_id != user_to_approve.team_id:
                    raise TeamMismatchException(
                        message="승인자와 사용자는 같은 팀에 속해야 합니다",
                        user_team_id=str(user_to_approve.team_id),
                        approver_team_id=str(approver.team_id),
                    )

                # 5. 승인할 사용자가 이미 활성화되어 있는지 확인
                if user_to_approve.is_active:
                    raise UserAlreadyActiveException(
                        message="사용자가 이미 활성화되어 있습니다",
                        user_id=str(user_id),
                    )

                # 6. 사용자 활성화
                user_to_approve.activate()
                updated_user = await user_repo.update(user_to_approve)

                # 7. 팀 정보 조회
                team = await team_repo.find_by_id(updated_user.team_id)

                # 8. 트랜잭션 커밋
                await session.commit()

                return {
                    "user": {
                        "id": str(updated_user.id),
                        "name": updated_user.name,
                        "app_id": updated_user.app_id,
                        "role": updated_user.role,
                        "team_id": str(updated_user.team_id),
                        "is_active": updated_user.is_active,
                        "created_at": updated_user.created_at.isoformat(),
                        "updated_at": updated_user.updated_at.isoformat(),
                    },
                    "team": (
                        {
                            "id": str(team.id),
                            "name": team.name,
                            "payment": team.payment,
                            "is_active": team.is_active,
                        }
                        if team
                        else None
                    ),
                }

            except Exception as e:
                await session.rollback()
                raise e

    async def get_team_users(self, team_id: UUID) -> list:
        """
        팀의 모든 사용자 조회
        Args:
            team_id: 팀 ID
        Returns:
            list: 팀의 모든 사용자 목록
        """
        async with self.get_session() as session:
            try:
                user_repo = self.user_repository_class(session)
                team_repo = self.team_repository_class(session)

                # 팀 존재 확인
                team = await team_repo.find_by_id(team_id)
                if team is None:
                    raise ResourceNotFoundException(
                        resource_type="Team",
                        resource_id=str(team_id),
                        message=f"ID '{team_id}'인 팀을 찾을 수 없습니다",
                    )

                # 팀의 모든 사용자 조회
                users = await user_repo.find_by_team_id(team_id)

                return [
                    {
                        "id": str(user.id),
                        "name": user.name,
                        "app_id": user.app_id,
                        "role": user.role,
                        "team_id": str(user.team_id),
                        "is_active": user.is_active,
                        "created_at": user.created_at.isoformat(),
                        "updated_at": user.updated_at.isoformat(),
                    }
                    for user in users
                ]

            except Exception as e:
                await session.rollback()
                raise e

    async def change_user_role(
        self, target_user_id: UUID, new_role: str, owner_user_id: UUID
    ) -> dict:
        """
        사용자 권한 변경 (owner만 가능)
        Args:
            target_user_id: 권한을 변경할 사용자 ID
            new_role: 새로운 권한 (owner, user)
            owner_user_id: 권한을 변경하는 owner의 사용자 ID
        Returns:
            dict: 변경된 사용자 정보
        """
        async with self.get_session() as session:
            try:
                user_repo = self.user_repository_class(session)

                # 권한을 변경할 사용자 조회
                target_user = await user_repo.find_by_id(target_user_id)
                if target_user is None:
                    raise ResourceNotFoundException(
                        resource_type="User",
                        resource_id=str(target_user_id),
                        message=f"ID '{target_user_id}'인 사용자를 찾을 수 없습니다",
                    )

                # 권한을 변경하는 owner 조회
                owner_user = await user_repo.find_by_id(owner_user_id)
                if owner_user is None:
                    raise ResourceNotFoundException(
                        resource_type="User",
                        resource_id=str(owner_user_id),
                        message=f"ID '{owner_user_id}'인 승인자를 찾을 수 없습니다",
                    )

                # owner 권한 확인
                if owner_user.role != "owner":
                    raise InsufficientPermissionException(
                        message="owner 권한만 사용자 권한을 변경할 수 있습니다",
                        required_role="owner",
                        current_role=owner_user.role,
                    )

                # 같은 팀인지 확인
                if owner_user.team_id != target_user.team_id:
                    raise TeamMismatchException(
                        message="같은 팀의 사용자만 권한을 변경할 수 있습니다",
                        user_team_id=str(target_user.team_id),
                        approver_team_id=str(owner_user.team_id),
                    )

                # 유효한 권한인지 확인
                if new_role not in ["owner", "user"]:
                    raise InvalidRoleException(
                        message=f"유효하지 않은 권한입니다: {new_role}",
                        role=new_role,
                    )

                # 현재 권한과 같은지 확인
                if target_user.role == new_role:
                    raise UserRoleChangeException(
                        message=f"사용자가 이미 '{new_role}' 권한을 가지고 있습니다",
                        user_id=str(target_user_id),
                        new_role=new_role,
                    )

                # 마지막 owner 보호 로직
                if target_user.role == "owner" and new_role == "user":
                    # 팀의 owner 수 확인
                    team_owners = await user_repo.find_by_team_id_and_role(
                        target_user.team_id, "owner"
                    )
                    if len(team_owners) <= 1:
                        raise LastOwnerProtectionException(
                            message="팀에 최소 하나의 owner가 필요합니다. 마지막 owner는 권한을 변경할 수 없습니다",
                            user_id=str(target_user_id),
                            team_id=str(target_user.team_id),
                        )

                # 권한 변경
                target_user.change_role(new_role)
                updated_user = await user_repo.update(target_user)
                await session.commit()

                return {
                    "user": {
                        "id": str(updated_user.id),
                        "name": updated_user.name,
                        "app_id": updated_user.app_id,
                        "role": updated_user.role,
                        "team_id": str(updated_user.team_id),
                        "is_active": updated_user.is_active,
                        "created_at": updated_user.created_at.isoformat(),
                        "updated_at": updated_user.updated_at.isoformat(),
                    }
                }

            except Exception as e:
                await session.rollback()
                raise e
