from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

# --- VENDOR SCHEMAS ---
class VendorCreate(BaseModel):
    business_name: str
    subdomain: str
    email: str
    password: str

class VendorResponse(BaseModel):
    id: UUID
    business_name: str
    subdomain: str
    email: str
    storage_used_bytes: int
    is_active: bool

    class Config:
        from_attributes = True

# --- TOKEN SCHEMA FOR LOGIN ---
class Token(BaseModel):
    access_token: str
    token_type: str

# --- CATEGORY SCHEMAS ---
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True

# --- VARIANT & IMAGE SCHEMAS ---
class VariantCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    price_paise: int = Field(..., gt=0)
    stock_count: int = 0

class VariantResponse(BaseModel):
    id: UUID
    name: str
    sku: Optional[str]
    price_paise: int
    stock_count: int

    class Config:
        from_attributes = True

class ImageResponse(BaseModel):
    id: UUID
    image_url: str
    is_primary: bool

    class Config:
        from_attributes = True

# --- PRODUCT SCHEMAS (NOW NESTED!) ---
class ProductCreate(BaseModel):
    category_id: Optional[UUID] = None
    name: str
    description: str
    
    # When creating a product, the vendor must provide at least one variant (e.g., standard size and price)
    variants: list[VariantCreate]

class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    seo_meta_tag: Optional[str]
    is_active: bool
    
    # FastAPI will now automatically bundle the category, variants, and images when fetching a product!
    category: Optional[CategoryResponse] = None
    variants: list[VariantResponse] = []
    images: list[ImageResponse] = []

    class Config:
        from_attributes = True