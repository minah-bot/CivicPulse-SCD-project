"""
SHARED CONTRACT

This file is read by Person B (imports Category/Priority/TriageResult)
and mirrored by hand by Person C in frontend/src/api/types.ts.
Do NOT change field names/enums without flagging the group first.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional, Protocol

from pydantic import BaseModel, Field, field_validator


class Category(str, Enum):
    WATER = "water"
    ELECTRICITY = "electricity"
    ROADS = "roads"
    SANITATION = "sanitation"
    SAFETY = "safety"
    OTHER = "other"

    water = "water"
    electricity = "electricity"
    roads = "roads"
    sanitation = "sanitation"
    safety = "safety"
    other = "other"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class Status(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


ALLOWED_TRANSITIONS: dict[Status, set[Status]] = {
    Status.OPEN: {Status.IN_PROGRESS, Status.REJECTED},
    Status.IN_PROGRESS: {Status.RESOLVED, Status.REJECTED},
    Status.RESOLVED: set(),
    Status.REJECTED: set(),
}


class TriageResult(BaseModel):
    category: Category
    priority: Priority
    summary: str = Field(max_length=140)
    confidence: float = Field(ge=0.0, le=1.0)


class TriageProvider(Protocol):
    name: str

    def triage(self, text: str, location: str) -> TriageResult:
        ...


class TriagedBy(str, Enum):
    llm_groq = "llm:groq"
    llm_ollama = "llm:ollama"
    rules = "rules"
    rules_fallback = "rules:fallback"


class ComplaintCreate(BaseModel):
    text: str = Field(min_length=10, max_length=2000)
    location: str = Field(min_length=2, max_length=200)

    @field_validator("text")
    @classmethod
    def text_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text must not be blank")
        return v


class ComplaintOut(BaseModel):
    id: int
    text: str
    location: str
    category: Category
    priority: Priority
    ai_summary: str
    status: Status
    triaged_by: str
    triage_latency_ms: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComplaintListOut(BaseModel):
    items: List[ComplaintOut]
    total: int
    page: int
    page_size: int


class StatusUpdate(BaseModel):
    status: Status


class StatsOut(BaseModel):
    total: int
    by_category: dict[str, int]
    by_priority: dict[str, int]
    by_status: dict[str, int]


class ProviderMeta(BaseModel):
    name: str
    calls: int
    fallback_count: int
    avg_latency_ms: Optional[float] = None


class ProvidersMetaOut(BaseModel):
    active_provider: str
    providers: List[ProviderMeta]
