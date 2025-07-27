from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UUID as SQLAlchemyUUID
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
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # 관계 설정
    users = relationship("UserModel", back_populates="team", cascade="all, delete-orphan")


class UserModel(Base):
    """사용자 SQLAlchemy 모델"""
    __tablename__ = "user"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    app_id = Column(String, nullable=False, unique=True)
    app_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    team_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("team.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # 관계 설정
    team = relationship("TeamModel", back_populates="users") 