from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_admin
from app.db.session import get_db
from app.models import AuditLog, Category, Coupon, Order, OrderStatus, Product, ProductVariant, SiteSetting, User
from app.schemas import (
    CategoryIn,
    CategoryOut,
    CouponIn,
    CouponOut,
    OrderOut,
    OrderStatusIn,
    ProductIn,
    ProductOut,
    SettingIn,
    UserOut,
    UserStatusIn,
)
from app.services.serializers import serialize_product

router = APIRouter(prefix="/admin", tags=["Administration"])


def audit(db: Session, actor: User, action: str, resource: str, resource_id: str = "", details: str = "") -> None:
    db.add(AuditLog(actor_id=actor.id, action=action, resource=resource, resource_id=resource_id, details=details))


def product_query():
    return select(Product).options(
        selectinload(Product.category),
        selectinload(Product.reviews),
        selectinload(Product.variants),
    )


def apply_product_payload(db: Session, product: Product, payload: ProductIn) -> None:
    values = payload.model_dump(exclude={"variants"})
    for key, value in values.items():
        setattr(product, key, value)
    product.stock = sum(item.stock for item in payload.variants if item.is_active)
    existing_by_id = {variant.id: variant for variant in product.variants}
    retained: set[int] = set()
    for item in payload.variants:
        variant = existing_by_id.get(item.id) if item.id else None
        if variant:
            retained.add(variant.id)
            for key, value in item.model_dump(exclude={"id"}).items():
                setattr(variant, key, value)
        else:
            product.variants.append(ProductVariant(**item.model_dump(exclude={"id"})))
    for variant in list(product.variants):
        if variant.id and variant.id not in retained and variant.id in existing_by_id:
            db.delete(variant)


@router.get("/dashboard")
def dashboard(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    month_start = datetime.now(UTC) - timedelta(days=30)
    valid_order = Order.status.notin_([OrderStatus.cancelled, OrderStatus.returned])
    revenue = db.scalar(select(func.coalesce(func.sum(Order.total), 0)).where(valid_order)) or Decimal("0")
    recent_revenue = db.scalar(
        select(func.coalesce(func.sum(Order.total), 0)).where(Order.created_at >= month_start, valid_order)
    ) or Decimal("0")
    recent_orders = db.scalars(
        select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc()).limit(6)
    ).all()
    stock_total = db.scalar(select(func.coalesce(func.sum(ProductVariant.stock), 0))) or 0
    return {
        "products": db.scalar(select(func.count(Product.id))) or 0,
        "variants": db.scalar(select(func.count(ProductVariant.id))) or 0,
        "inventory_units": stock_total,
        "low_stock": db.scalar(select(func.count(ProductVariant.id)).where(ProductVariant.stock <= 3)) or 0,
        "customers": db.scalar(select(func.count(User.id)).where(User.role == "customer")) or 0,
        "orders": db.scalar(select(func.count(Order.id))) or 0,
        "revenue": str(revenue),
        "revenue_30d": str(recent_revenue),
        "recent_orders": [OrderOut.model_validate(item).model_dump(mode="json") for item in recent_orders],
    }


@router.get("/products", response_model=list[ProductOut])
def all_products(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    products = db.scalars(product_query().order_by(Product.created_at.desc())).unique().all()
    return [serialize_product(product) for product in products]


@router.post("/products", response_model=ProductOut, status_code=201)
def create_product(payload: ProductIn, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    product = Product(**payload.model_dump(exclude={"variants", "stock"}))
    product.stock = sum(item.stock for item in payload.variants if item.is_active)
    product.variants = [ProductVariant(**item.model_dump(exclude={"id"})) for item in payload.variants]
    db.add(product)
    db.flush()
    audit(db, admin, "create", "product", str(product.id), product.title)
    db.commit()
    saved = db.scalar(product_query().where(Product.id == product.id))
    return serialize_product(saved)


@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductIn,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    product = db.scalar(product_query().where(Product.id == product_id))
    if not product:
        raise HTTPException(404, "Product not found")
    apply_product_payload(db, product, payload)
    audit(db, admin, "update", "product", str(product.id), product.title)
    db.commit()
    saved = db.scalar(product_query().where(Product.id == product.id))
    return serialize_product(saved)


@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    audit(db, admin, "delete", "product", str(product.id), product.title)
    db.delete(product)
    db.commit()


@router.get("/categories", response_model=list[CategoryOut])
def admin_categories(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.scalars(select(Category).order_by(Category.name)).all()


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryIn, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = Category(**payload.model_dump())
    db.add(item)
    db.flush()
    audit(db, admin, "create", "category", str(item.id), item.name)
    db.commit()
    db.refresh(item)
    return item


@router.put("/categories/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    payload: CategoryIn,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    item = db.get(Category, category_id)
    if not item:
        raise HTTPException(404, "Category not found")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    audit(db, admin, "update", "category", str(item.id), item.name)
    db.commit()
    db.refresh(item)
    return item


@router.get("/orders", response_model=list[OrderOut])
def all_orders(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.scalars(select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc())).all()


@router.patch("/orders/{order_id}/status", response_model=OrderOut)
def order_status(
    order_id: int,
    payload: OrderStatusIn,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    order = db.scalar(select(Order).options(selectinload(Order.items)).where(Order.id == order_id))
    if not order:
        raise HTTPException(404, "Order not found")
    order.status = payload.status
    if payload.status == OrderStatus.delivered and order.payment_method == "cod":
        order.payment_status = "paid"
    if payload.status in {OrderStatus.cancelled, OrderStatus.returned}:
        order.payment_status = "refund_pending" if order.payment_status == "paid" else order.payment_status
    audit(db, admin, "status_change", "order", str(order.id), payload.status.value)
    db.commit()
    db.refresh(order)
    return order


@router.get("/users", response_model=list[UserOut])
def users(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.created_at.desc())).all()


@router.patch("/users/{user_id}/active", response_model=UserOut)
def update_user_status(
    user_id: int,
    payload: UserStatusIn,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    if user.id == admin.id and not payload.is_active:
        raise HTTPException(400, "You cannot disable your own administrator account")
    user.is_active = payload.is_active
    audit(db, admin, "status_change", "user", str(user.id), str(payload.is_active))
    db.commit()
    db.refresh(user)
    return user


@router.get("/coupons", response_model=list[CouponOut])
def coupons(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return db.scalars(select(Coupon).order_by(Coupon.code)).all()


@router.post("/coupons", response_model=CouponOut, status_code=201)
def create_coupon(payload: CouponIn, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    values = payload.model_dump()
    values["code"] = payload.code.upper()
    item = Coupon(**values)
    db.add(item)
    db.flush()
    audit(db, admin, "create", "coupon", str(item.id), item.code)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/coupons/{coupon_id}", status_code=204)
def delete_coupon(coupon_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = db.get(Coupon, coupon_id)
    if not item:
        raise HTTPException(404, "Coupon not found")
    audit(db, admin, "delete", "coupon", str(item.id), item.code)
    db.delete(item)
    db.commit()


@router.put("/settings/{key}")
def update_setting(
    key: str,
    payload: SettingIn,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    item = db.get(SiteSetting, key)
    if item:
        item.value = payload.value
    else:
        db.add(SiteSetting(key=key, value=payload.value))
    audit(db, admin, "update", "setting", key, payload.value[:200])
    db.commit()
    return {"key": key, "value": payload.value}
