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

# --- PRODUCT SCHEMAS ---
class ProductCreate(BaseModel):
    # vendor_id is securely pulled from the login token now!
    name: str
    description: str
    price_paise: int = Field(..., gt=0)
    image_url: Optional[str] = None

class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    seo_meta_tag: Optional[str]
    price_paise: int
    image_url: Optional[str]

    class Config:
        from_attributes = True