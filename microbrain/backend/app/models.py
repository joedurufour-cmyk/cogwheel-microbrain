from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), default="Untitled system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    turns = relationship("Turn", back_populates="session", cascade="all, delete-orphan")
    narrative_state = relationship("NarrativeState", back_populates="session", uselist=False, cascade="all, delete-orphan")


class Turn(Base):
    __tablename__ = "turns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    raw_input: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="turns")
    report = relationship("TurnReport", back_populates="turn", uselist=False, cascade="all, delete-orphan")


class NarrativeState(Base):
    __tablename__ = "narrative_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), unique=True, index=True)
    objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    active_problem: Mapped[str | None] = mapped_column(Text, nullable=True)
    central_objects_json: Mapped[str] = mapped_column(Text, default="[]")
    active_relations_json: Mapped[str] = mapped_column(Text, default="[]")
    blocking_gap: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_hypothesis: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_architecture_json: Mapped[str] = mapped_column(Text, default="[]")
    current_risks_json: Mapped[str] = mapped_column(Text, default="[]")
    open_loops_json: Mapped[str] = mapped_column(Text, default="[]")
    decisions_json: Mapped[str] = mapped_column(Text, default="[]")
    validations_json: Mapped[str] = mapped_column(Text, default="[]")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = relationship("Session", back_populates="narrative_state")


class TurnReport(Base):
    __tablename__ = "turn_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    turn_id: Mapped[int] = mapped_column(ForeignKey("turns.id"), unique=True, index=True)
    report_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    turn = relationship("Turn", back_populates="report")


class Collision(Base):
    __tablename__ = "collisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    turn_id: Mapped[int] = mapped_column(ForeignKey("turns.id"), index=True)
    collision_type: Mapped[str] = mapped_column(String(80))
    severity: Mapped[float] = mapped_column(Float)
    evidence_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DomainObject(Base):
    __tablename__ = "domain_objects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    canonical_name: Mapped[str] = mapped_column(String(160), index=True)
    object_type: Mapped[str] = mapped_column(String(80))
    aliases_json: Mapped[str] = mapped_column(Text, default="[]")
    properties_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ObjectRelation(Base):
    __tablename__ = "object_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    subject: Mapped[str] = mapped_column(String(160), index=True)
    predicate: Mapped[str] = mapped_column(String(80))
    object: Mapped[str] = mapped_column(String(160), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    source_turn_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    valid_from: Mapped[str | None] = mapped_column(String(80), nullable=True)
    valid_to: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
