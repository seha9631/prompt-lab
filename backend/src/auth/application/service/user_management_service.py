from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entity.user import User
from ...domain.entity.team import Team
from ...domain.service.user_creation_service import UserCreationService
from ...domain.repository.user_repository import UserRepository
from ...domain.repository.team_repository import TeamRepository
from ...domain.value_object.app_credentials import AppId, AppPassword


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
