from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import StatsOut
from app.services import stats_service

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats", response_model=StatsOut)
def get_stats(response: Response, db: Session = Depends(get_db)):
    stats, cache_status = stats_service.get_stats(db)
    response.headers["X-Cache"] = cache_status
    return stats
