from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    phone: Optional[str] = ""


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None


class UserResponse(UserBase):
    id: int
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    is_active: bool
    is_staff: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AddressBase(BaseModel):
    name: str
    address_line1: str
    address_line2: Optional[str] = ""
    city: str
    state: str
    zip_code: str
    country: str
    phone: Optional[str] = ""
    is_default: bool = False


class AddressCreate(AddressBase):
    pass


class AddressResponse(AddressBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = ""
    image: Optional[str] = ""


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    slug: str
    description: str
    price: Decimal
    compare_price: Optional[Decimal] = 0
    stock: int = 0
    sku: Optional[str] = ""
    is_featured: bool = False
    weight: Optional[Decimal] = 0
    image: Optional[str] = ""


class ProductCreate(ProductBase):
    category_id: int


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    compare_price: Optional[Decimal] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    image: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    category_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    price: Decimal
    compare_price: Optional[Decimal]
    stock: int
    image: str
    is_featured: bool
    category: CategoryResponse

    class Config:
        from_attributes = True


class ReviewBase(BaseModel):
    rating: int
    title: str
    comment: str


class ReviewCreate(ReviewBase):
    product_id: int


class ReviewResponse(ReviewBase):
    id: int
    product_id: int
    user_id: int
    is_verified: bool
    created_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True


class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemCreate(CartItemBase):
    pass


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int
    user_id: Optional[int]
    items: List[CartItemResponse] = []

    class Config:
        from_attributes = True


class CartWithTotal(BaseModel):
    id: int
    items: List[dict] = []
    total_items: int = 0
    total_price: float = 0


class OrderItemResponse(BaseModel):
    id: int
    product_name: str
    product_price: Decimal
    quantity: int
    subtotal: Decimal

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    shipping_name: str
    shipping_address_line1: str
    shipping_address_line2: Optional[str] = ""
    shipping_city: str
    shipping_state: str
    shipping_zip_code: str
    shipping_country: str
    shipping_phone: str
    notes: Optional[str] = ""


class OrderCreate(OrderBase):
    user_id: int


class OrderResponse(OrderBase):
    id: int
    user_id: int
    order_number: str
    status: str
    subtotal: Decimal
    tax: Decimal
    shipping_cost: Decimal
    discount: Decimal
    total: Decimal
    is_paid: bool
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str
