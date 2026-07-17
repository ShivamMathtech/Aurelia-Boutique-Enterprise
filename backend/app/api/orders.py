from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import CartItem, Coupon, Order, OrderItem, User
from app.schemas import CheckoutIn, OrderOut

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/checkout", response_model=OrderOut, status_code=201)
def checkout(payload: CheckoutIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = db.scalars(
        select(CartItem)
        .options(selectinload(CartItem.product), selectinload(CartItem.variant))
        .where(CartItem.user_id == user.id)
    ).all()
    if not cart:
        raise HTTPException(400, "Your cart is empty")
    subtotal = Decimal("0")
    for item in cart:
        if item.quantity > item.variant.stock or not item.variant.is_active:
            raise HTTPException(409, f"Insufficient stock for {item.product.title} ({item.variant.size}, {item.variant.color})")
        subtotal += (item.product.price + item.variant.additional_price) * item.quantity
    discount = Decimal("0")
    if payload.coupon_code:
        coupon = db.scalar(select(Coupon).where(Coupon.code == payload.coupon_code.upper(), Coupon.is_active.is_(True)))
        if not coupon or subtotal < coupon.minimum_order:
            raise HTTPException(400, "Coupon is invalid or minimum order is not met")
        discount = (subtotal * Decimal(coupon.discount_percent) / Decimal(100)).quantize(Decimal("0.01"))
        if coupon.max_discount is not None:
            discount = min(discount, coupon.max_discount)
    shipping_fee = Decimal("0") if subtotal >= Decimal("1499") else Decimal("99")
    order = Order(
        order_number=f"AB-{datetime.now(UTC):%y%m%d}-{uuid4().hex[:6].upper()}",
        user_id=user.id,
        subtotal=subtotal,
        discount=discount,
        shipping_fee=shipping_fee,
        total=subtotal - discount + shipping_fee,
        payment_method=payload.payment_method,
        payment_status="paid" if payload.payment_method == "mock_card" else "pending",
        shipping_name=payload.shipping_name,
        shipping_phone=payload.shipping_phone,
        shipping_address=payload.shipping_address,
        gift_note=payload.gift_note,
    )
    db.add(order)
    db.flush()
    for item in cart:
        unit_price = item.product.price + item.variant.additional_price
        item.variant.stock -= item.quantity
        item.product.stock = max(0, item.product.stock - item.quantity)
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                variant_id=item.variant_id,
                title=item.product.title,
                variant_sku=item.variant.sku,
                size=item.variant.size,
                color=item.variant.color,
                unit_price=unit_price,
                quantity=item.quantity,
            )
        )
        db.delete(item)
    db.commit()
    saved = db.scalar(select(Order).options(selectinload(Order.items)).where(Order.id == order.id))
    return saved


@router.get("/mine", response_model=list[OrderOut])
def my_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.user_id == user.id)
        .order_by(Order.created_at.desc())
    ).all()


@router.get("/{order_number}", response_model=OrderOut)
def order_detail(order_number: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.scalar(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.order_number == order_number, Order.user_id == user.id)
    )
    if not order:
        raise HTTPException(404, "Order not found")
    return order
