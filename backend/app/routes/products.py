from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database.database import get_db
from ..controllers.product_controller import ProductController
from ..controllers.category_controller import CategoryController
from ..schemas.product import ProductCreate, ProductUpdate, Product, ProductListResponse

router = APIRouter()

@router.get("/", response_model=ProductListResponse)
async def list_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = Query(None, pattern="^(price|stock|created_at)$"),
    sort_order: Optional[str] = Query("asc", pattern="^(asc|desc)$")
):
    """List products with pagination, filtering, and search"""
    products, total = ProductController.get_products(
        db, page, limit, search, category_id, min_price, max_price, sort_by, sort_order
    )
    
    return ProductListResponse(
        data=products,
        pagination={
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    )

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product by ID"""
    product = ProductController.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=Product, status_code=201)
async def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    # Check if category exists
    category = CategoryController.get_category_by_id(db, product_data.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check for duplicate name
    existing = ProductController.get_product_by_name(db, product_data.name)
    if existing:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    
    product = ProductController.create_product(db, product_data)
    return product

@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing product"""
    # Check if category exists (if updating category)
    if product_data.category_id is not None:
        category = CategoryController.get_category_by_id(db, product_data.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    product = ProductController.update_product(db, product_id, product_data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    if not ProductController.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return None