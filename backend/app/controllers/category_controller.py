from sqlalchemy.orm import Session
from typing import List, Optional

from ..database.models import Category as CategoryModel

class CategoryController:
    @staticmethod
    def get_all_categories(db: Session) -> List[CategoryModel]:
        """Get all categories"""
        return db.query(CategoryModel).all()
    
    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> Optional[CategoryModel]:
        """Get a category by ID"""
        return db.query(CategoryModel).filter(CategoryModel.id == category_id).first()