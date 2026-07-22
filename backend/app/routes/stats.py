from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database.database import get_db
from ..controllers.stats_controller import StatsController

router = APIRouter()

@router.get("/")
async def get_stats(db: Session = Depends(get_db)):
    """Get aggregate stats"""
    return StatsController.get_stats(db)