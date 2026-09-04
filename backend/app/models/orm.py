"""SQLAlchemy models per PRD section 30."""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.db import Base


def _now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)

    projects = relationship("Project", back_populates="user")


class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    description = Column(Text, nullable=False)
    team_size = Column(Integer, nullable=False)
    budget = Column(String, nullable=False)
    expected_users = Column(String, nullable=False)
    availability = Column(String, nullable=False)
    created_at = Column(DateTime, default=_now)

    user = relationship("User", back_populates="projects")
    requirement = relationship("Requirement", back_populates="project", uselist=False)
    prediction = relationship("Prediction", back_populates="project", uselist=False)
    report = relationship("Report", back_populates="project", uselist=False)


class Requirement(Base):
    __tablename__ = "requirements"

    requirement_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    requirement_data = Column(Text, nullable=False)  # JSON-serialized Requirements

    project = relationship("Project", back_populates="requirement")


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    architecture = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    model_version = Column(String, nullable=False, default="random_forest_v1")

    project = relationship("Project", back_populates="prediction")


class Report(Base):
    __tablename__ = "reports"

    report_id = Column(String, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    report_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now)

    project = relationship("Project", back_populates="report")
