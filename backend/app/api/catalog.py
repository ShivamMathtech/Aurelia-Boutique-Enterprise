from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Category, Product, ProductVariant, Review, User
from app.schemas import CategoryOut, ProductOut, ReviewIn
from app.services.serializers import serialize_product

router = APIRouter(tags=["Boutique catalogue"])


@router.get("/categories", response_model=list[CategoryOut])
def categories(db: Session = Depends(get_db)):
    return db.scalars(select(Category).where(Category.is_active.is_(True)).order_by(Category.name)).all()


@router.get("/products", response_model=dict)
def products(
    q: str | None = None,
    category: str | None = None,
    featured: bool | None = None,
    bestseller: bool | None = None,
    size: str | None = None,
    color: str | None = None,
    occasion: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str = Query("newest", pattern="^(newest|price_asc|price_desc|title)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    options = (
        selectinload(Product.category),
        selectinload(Product.reviews),
        selectinload(Product.variants),
    )
    stmt = select(Product).options(*options).where(Product.published.is_(True))
    count_stmt = select(func.count(Product.id)).where(Product.published.is_(True))
    filters = []
    if q:
        filters.append(
            or_(
                Product.title.ilike(f"%{q}%"),
                Product.brand.ilike(f"%{q}%"),
                Product.sku.ilike(f"%{q}%"),
                Product.fabric.ilike(f"%{q}%"),
                Product.occasion.ilike(f"%{q}%"),
            )
        )
    if category:
        filters.append(Product.category.has(Category.slug == category))
    if featured is not None:
        filters.append(Product.featured == featured)
    if bestseller is not None:
        filters.append(Product.bestseller == bestseller)
    if occasion:
        filters.append(Product.occasion.ilike(f"%{occasion}%"))
    if size:
        filters.append(Product.variants.any(and_(ProductVariant.size == size, ProductVariant.stock > 0, ProductVariant.is_active.is_(True))))
    if color:
        filters.append(Product.variants.any(and_(ProductVariant.color.ilike(f"%{color}%"), ProductVariant.stock > 0, ProductVariant.is_active.is_(True))))
    if min_price is not None:
        filters.append(Product.price >= min_price)
    if max_price is not None:
        filters.append(Product.price <= max_price)
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)
    ordering = {
        "newest": Product.created_at.desc(),
        "price_asc": Product.price.asc(),
        "price_desc": Product.price.desc(),
        "title": Product.title.asc(),
    }[sort]
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(ordering).offset((page - 1) * page_size).limit(page_size)).unique().all()
    return {
        "items": [serialize_product(item).model_dump(mode="json") for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/products/{slug}", response_model=ProductOut)
def product_detail(slug: str, db: Session = Depends(get_db)):
    product = db.scalar(
        select(Product)
        .options(selectinload(Product.category), selectinload(Product.reviews), selectinload(Product.variants))
        .where(Product.slug == slug, Product.published.is_(True))
    )
    if not product:
        raise HTTPException(404, "Product not found")
    return serialize_product(product)


@router.post("/products/{product_id}/reviews", status_code=201)
def review_product(
    product_id: int,
    payload: ReviewIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    existing = db.scalar(select(Review).where(Review.product_id == product_id, Review.user_id == user.id))
    if existing:
        existing.rating, existing.comment = payload.rating, payload.comment
    else:
        db.add(Review(user_id=user.id, product_id=product_id, rating=payload.rating, comment=payload.comment))
    db.commit()
    return {"message": "Review saved"}
