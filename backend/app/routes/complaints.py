from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import complaint_repo
from app.schemas import (
    ComplaintCreate,
    ComplaintListOut,
    ComplaintOut,
    Status,
    StatusUpdate,
)
from app.services import stats_service
from app.services.status_service import InvalidTransitionError, validate_transition
from app.services.triage_service import run_triage

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.post("", response_model=ComplaintOut, status_code=201)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    outcome = run_triage(payload.text, payload.location)
    complaint = complaint_repo.create_complaint(
        db,
        text=payload.text,
        location=payload.location,
        triage=outcome.result,
        triaged_by=outcome.triaged_by.value,
        triage_latency_ms=outcome.latency_ms,
    )
    stats_service.invalidate_stats_cache()
    return complaint


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    complaint = complaint_repo.get_complaint(db, complaint_id)
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@router.get("", response_model=ComplaintListOut)
def list_complaints(
    category: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = complaint_repo.list_complaints(
        db, category=category, priority=priority, status=status, page=page, page_size=page_size
    )
    return ComplaintListOut(items=items, total=total, page=page, page_size=page_size)


@router.patch("/{complaint_id}/status", response_model=ComplaintOut)
def update_status(complaint_id: int, payload: StatusUpdate, db: Session = Depends(get_db)):
    complaint = complaint_repo.get_complaint(db, complaint_id)
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")

    current = Status(complaint.status)
    try:
        validate_transition(current, payload.status)
    except InvalidTransitionError as exc:
        # API contract: message names the attempted transition
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    updated = complaint_repo.update_status(db, complaint, payload.status.value)
    stats_service.invalidate_stats_cache()
    return updated