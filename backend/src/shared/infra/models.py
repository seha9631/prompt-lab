from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    UUID as SQLAlchemyUUID,
    Text,
    ARRAY,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()


class TeamModel(Base):
    """팀 SQLAlchemy 모델"""

    __tablename__ = "team"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
    payment = Column(String, nullable=False, default="free")
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # 관계 설정
    users = relationship(
        "UserModel", back_populates="team", cascade="all, delete-orphan"
    )


class UserModel(Base):
    """사용자 SQLAlchemy 모델"""

    __tablename__ = "user"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    app_id = Column(String, nullable=False, unique=True)
    app_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    team_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("team.id"), nullable=False
    )
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # 관계 설정
    team = relationship("TeamModel", back_populates="users")


class SourceModel(Base):
    """소스 SQLAlchemy 모델"""

    __tablename__ = "source"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    # 관계 설정
    source_models = relationship("SourceModelModel", back_populates="source")
    credentials = relationship("CredentialModel", back_populates="source")


class SourceModelModel(Base):
    """소스 모델 SQLAlchemy 모델"""

    __tablename__ = "source_model"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    source_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("source.id"), nullable=False
    )
    created_at = Column(DateTime, nullable=False, default=func.now())

    # 관계 설정
    source = relationship("SourceModel", back_populates="source_models")


class CredentialModel(Base):
    """Credential SQLAlchemy 모델"""

    __tablename__ = "credential"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("team.id"), nullable=False
    )
    name = Column(String, nullable=False)
    source_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("source.id"), nullable=False
    )
    api_key = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # 관계 설정
    team = relationship("TeamModel")
    source = relationship("SourceModel", back_populates="credentials")


class ProjectModel(Base):
    """Project SQLAlchemy 모델"""

    __tablename__ = "project"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("team.id"), nullable=False
    )
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # 관계 설정
    team = relationship("TeamModel")
    llm_requests = relationship("LLMRequestModel", back_populates="project")


class LLMRequestModel(Base):
    """LLM 요청 SQLAlchemy 모델"""

    __tablename__ = "llm_request"

    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("team.id"), nullable=False
    )
    user_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("user.id"), nullable=False
    )
    project_id = Column(
        SQLAlchemyUUID(as_uuid=True), ForeignKey("project.id"), nullable=False
    )
    system_prompt = Column(Text, nullable=False)
    question = Column(Text, nullable=False)
    model_name = Column(String, nullable=False)
    file_paths = Column(ARRAY(String), nullable=False, default=[])
    status = Column(
        String, nullable=False, default="pending"
    )  # pending, processing, completed, failed
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # 관계 설정
    team = relationship("TeamModel")
    user = relationship("UserModel")
    project = relationship("ProjectModel", back_populates="llm_requests")
