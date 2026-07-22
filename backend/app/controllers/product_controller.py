from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, Tuple, List

from ..database.models import Product as ProductModel
from ..database.models import Category as CategoryModel
from ..schemas.product import ProductCreate, ProductUpdate

class ProductController:
    @staticmethod
    def get_products(
        db: Session,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Tuple[List[ProductModel], int]:
        """Get products with pagination, filtering, and search"""
        query = db.query(ProductModel)
        
        # Search
        if search:
            query = query.filter(
                or_(
                    ProductModel.name.ilike(f"%{search}%"),
                    ProductModel.description.ilike(f"%{search}%")
                )
            )
        
        # Category filter
        if category_id:
            query = query.filter(ProductModel.category_id == category_id)
        
        # Price range
        if min_price is not None:
            query = query.filter(ProductModel.price >= min_price)
        if max_price is not None:
            query = query.filter(ProductModel.price <= max_price)
        
        # Sorting
        if sort_by:
            order_column = getattr(ProductModel, sort_by)
            if sort_order == "desc":
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        
        # Pagination
        total = query.count()
        offset = (page - 1) * limit
        products = query.offset(offset).limit(limit).all()
        
        return products, total
    
    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[ProductModel]:
        """Get a single product by ID"""
        return db.query(ProductModel).filter(ProductModel.id == product_id).first()
    
    @staticmethod
    def get_product_by_name(db: Session, name: str) -> Optional[ProductModel]:
        """Get a product by name (for duplicate check)"""
        return db.query(ProductModel).filter(ProductModel.name == name).first()
    
    @staticmethod
    def create_product(db: Session, product_data: ProductCreate) -> ProductModel:
        """Create a new product"""
        product = ProductModel(**product_data.model_dump())
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> Optional[ProductModel]:
        """Update an existing product"""
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            return None
        
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        db.commit()
        db.refresh(product)
        return product
    
    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """Delete a product"""
        product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not product:
            return False
        
        db.delete(product)
        db.commit()
        return True