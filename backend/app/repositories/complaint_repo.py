"""Every SQL/ORM query in the app lives here, and nowhere else.
Routes and services never import sqlalchemy.orm.Session query methods directly."""
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Complaint
from app.schemas import TriageResult


def create_complaint(
    db: Session,
    text: str,
    location: str,
    triage: TriageResult,
    triaged_by: str,
    triage_latency_ms: int,
) -> Complaint:
    complaint = Complaint(
        text=text,
        location=location,
        category=triage.category.value,
        priority=triage.priority.value,
        ai_summary=triage.summary,
        status="open",
        triaged_by=triaged_by,
        triage_latency_ms=triage_latency_ms,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


def get_complaint(db: Session, complaint_id: int) -> Optional[Complaint]:
    return db.get(Complaint, complaint_id)


def list_complaints(
    db: Session,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Complaint], int]:
    stmt = select(Complaint)
    count_stmt = select(func.count()).select_from(Complaint)

    if category:
        stmt = stmt.where(Complaint.category == category)
        count_stmt = count_stmt.where(Complaint.category == category)
    if priority:
        stmt = stmt.where(Complaint.priority == priority)
        count_stmt = count_stmt.where(Complaint.priority == priority)
    if status:
        stmt = stmt.where(Complaint.status == status)
        count_stmt = count_stmt.where(Complaint.status == status)

    total = db.execute(count_stmt).scalar_one()

    stmt = (
        stmt.order_by(Complaint.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(db.execute(stmt).scalars().all())
    return items, total


def update_status(db: Session, complaint: Complaint, new_status: str) -> Complaint:
    complaint.status = new_status
    db.commit()
    db.refresh(complaint)
    return complaint


def get_aggregate_counts(db: Session) -> dict:
    """Used by stats_service for /api/stats. One grouped query per dimension —
    small table, so three cheap queries beat one convoluted pivot."""
    total = db.execute(select(func.count()).select_from(Complaint)).scalar_one()

    by_category = dict(
        db.execute(
            select(Complaint.category, func.count()).group_by(Complaint.category)
        ).all()
    )
    by_priority = dict(
        db.execute(
            select(Complaint.priority, func.count()).group_by(Complaint.priority)
        ).all()
    )
    by_status = dict(
        db.execute(
            select(Complaint.status, func.count()).group_by(Complaint.status)
        ).all()
    )

    return {
        "total": total,
        "by_category": by_category,
        "by_priority": by_priority,
        "by_status": by_status,
    }
