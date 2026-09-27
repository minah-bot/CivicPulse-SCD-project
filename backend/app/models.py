"""
>>> SHARED CONTRACT <<<
SQLAlchemy tables. Nobody else edits this file, but B/C should know
the columns (they map 1:1 onto schemas.py / types.ts).

Indexes (justify in docs/ENGINEERING-NOTES.md):
  - ix_complaints_status_priority : GET /api/complaints?status=&priority=
  - ix_complaints_created_at      : ORDER BY created_at (default list sort)
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Index,
    func,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    location = Column(String(200), nullable=False)

    category = Column(String(32), nullable=False)
    priority = Column(String(16), nullable=False)
    ai_summary = Column(String(140), nullable=False)
    status = Column(String(16), nullable=False, default="open")

    triaged_by = Column(String(32), nullable=False)          # e.g. "llm:groq", "rules:fallback"
    triage_latency_ms = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_complaints_status_priority", "status", "priority"),
        Index("ix_complaints_created_at", "created_at"),
    )
