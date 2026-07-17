from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import CartItem, Product, ProductVariant, User
from app.schemas import CartItemIn, CartUpdate

router = APIRouter(prefix="/cart", tags=["Cart"])


def cart_response(db: Session, user_id: int):
    items = db.scalars(
        select(CartItem)
        .options(selectinload(CartItem.product), selectinload(CartItem.variant))
        .where(CartItem.user_id == user_id)
    ).all()
    result, subtotal = [], Decimal("0")
    for item in items:
        unit_price = item.product.price + item.variant.additional_price
        line_total = unit_price * item.quantity
        subtotal += line_total
        result.append(
            {
                "id": item.id,
                "quantity": item.quantity,
                "line_total": str(line_total),
                "unit_price": str(unit_price),
                "variant": {
                    "id": item.variant.id,
                    "sku": item.variant.sku,
                    "size": item.variant.size,
                    "color": item.variant.color,
                    "stock": item.variant.stock,
                },
                "product": {
                    "id": item.product.id,
                    "title": item.product.title,
                    "slug": item.product.slug,
                    "brand": item.product.brand,
                    "price": str(item.product.price),
                    "image_url": item.product.image_url,
                    "stock": item.product.stock,
                },
            }
        )
    return {"items": result, "subtotal": str(subtotal), "count": sum(item.quantity for item in items)}


@router.get("")
def get_cart(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return cart_response(db, user.id)


@router.post("/items", status_code=201)
def add_item(
    payload: CartItemIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.get(Product, payload.product_id)
    variant = db.get(ProductVariant, payload.variant_id)
    if not product or not product.published or not variant or variant.product_id != product.id or not variant.is_active:
        raise HTTPException(404, "Product variant not found")
    existing = db.scalar(select(CartItem).where(CartItem.user_id == user.id, CartItem.variant_id == variant.id))
    new_quantity = (existing.quantity if existing else 0) + payload.quantity
    if new_quantity > variant.stock:
        raise HTTPException(400, "Requested quantity exceeds available variant stock")
    if existing:
        existing.quantity = new_quantity
    else:
        db.add(CartItem(user_id=user.id, product_id=product.id, variant_id=variant.id, quantity=payload.quantity))
    db.commit()
    return cart_response(db, user.id)


@router.patch("/items/{item_id}")
def update_item(
    item_id: int,
    payload: CartUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.scalar(
        select(CartItem)
        .options(selectinload(CartItem.product), selectinload(CartItem.variant))
        .where(CartItem.id == item_id, CartItem.user_id == user.id)
    )
    if not item:
        raise HTTPException(404, "Cart item not found")
    if payload.quantity > item.variant.stock:
        raise HTTPException(400, "Requested quantity exceeds available variant stock")
    item.quantity = payload.quantity
    db.commit()
    return cart_response(db, user.id)


@router.delete("/items/{item_id}")
def remove_item(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.scalar(select(CartItem).where(CartItem.id == item_id, CartItem.user_id == user.id))
    if not item:
        raise HTTPException(404, "Cart item not found")
    db.delete(item)
    db.commit()
    return cart_response(db, user.id)
