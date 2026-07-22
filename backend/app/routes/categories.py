from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database.database import get_db
from ..controllers.category_controller import CategoryController
from ..schemas.product import Category

router = APIRouter()

@router.get("/", response_model=list[Category])
async def list_categories(db: Session = Depends(get_db)):
    """List all categories"""
    categories = CategoryController.get_all_categories(db)
    return categories