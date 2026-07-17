from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import OrderStatus, UserRole


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(ORMModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool


class AuthOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class UserStatusIn(BaseModel):
    is_active: bool


class CategoryIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=120)
    description: str = ""
    image_url: str = ""
    is_active: bool = True


class CategoryOut(ORMModel):
    id: int
    name: str
    slug: str
    description: str
    image_url: str
    is_active: bool


class VariantIn(BaseModel):
    id: int | None = None
    sku: str = Field(min_length=2, max_length=64)
    size: str = Field(min_length=1, max_length=24)
    color: str = Field(min_length=1, max_length=60)
    stock: int = Field(default=0, ge=0)
    additional_price: Decimal = Field(default=0, ge=0)
    is_active: bool = True


class VariantOut(ORMModel):
    id: int
    sku: str
    size: str
    color: str
    stock: int
    additional_price: Decimal
    is_active: bool


class ProductIn(BaseModel):
    title: str
    slug: str
    brand: str
    sku: str
    description: str
    fabric: str = "Premium blend"
    fit: str = "Regular"
    care_instructions: str = "Dry clean recommended"
    occasion: str = "Everyday"
    price: Decimal = Field(gt=0)
    compare_at_price: Decimal | None = None
    image_url: str = ""
    gallery_urls: str = ""
    vendor: str = "Aurelia Atelier"
    weight_grams: int = Field(default=0, ge=0)
    featured: bool = False
    bestseller: bool = False
    published: bool = True
    category_id: int
    variants: list[VariantIn] = Field(min_length=1)


class ProductOut(ORMModel):
    id: int
    title: str
    slug: str
    brand: str
    sku: str
    description: str
    fabric: str
    fit: str
    care_instructions: str
    occasion: str
    price: Decimal
    compare_at_price: Decimal | None
    stock: int
    image_url: str
    gallery_urls: str
    vendor: str
    weight_grams: int
    featured: bool
    bestseller: bool
    published: bool
    category_id: int
    category: CategoryOut
    variants: list[VariantOut]
    average_rating: float = 0
    review_count: int = 0


class CartItemIn(BaseModel):
    product_id: int
    variant_id: int
    quantity: int = Field(default=1, ge=1, le=20)


class CartUpdate(BaseModel):
    quantity: int = Field(ge=1, le=20)


class CheckoutIn(BaseModel):
    shipping_name: str
    shipping_phone: str
    shipping_address: str
    payment_method: str = "cod"
    coupon_code: str | None = None
    gift_note: str = Field(default="", max_length=500)


class OrderItemOut(ORMModel):
    id: int
    product_id: int
    variant_id: int | None
    title: str
    variant_sku: str
    size: str
    color: str
    unit_price: Decimal
    quantity: int


class OrderOut(ORMModel):
    id: int
    order_number: str
    status: OrderStatus
    subtotal: Decimal
    discount: Decimal
    shipping_fee: Decimal
    total: Decimal
    payment_method: str
    payment_status: str
    shipping_name: str
    shipping_phone: str
    shipping_address: str
    gift_note: str
    created_at: datetime
    items: list[OrderItemOut]


class ReviewIn(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=1500)


class CouponIn(BaseModel):
    code: str
    discount_percent: int = Field(ge=1, le=90)
    minimum_order: Decimal = Field(default=0, ge=0)
    max_discount: Decimal | None = Field(default=None, ge=0)
    is_active: bool = True


class CouponOut(ORMModel):
    id: int
    code: str
    discount_percent: int
    minimum_order: Decimal
    max_discount: Decimal | None
    is_active: bool


class OrderStatusIn(BaseModel):
    status: OrderStatus


class SettingIn(BaseModel):
    value: str
