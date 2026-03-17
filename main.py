from sqlalchemy import Column, String, Integer, BigInteger, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from database import Base

class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_name = Column(String, nullable=False)
    subdomain = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    storage_used_bytes = Column(BigInteger, default=0)
    is_active = Column(Boolean, default=True)

    # Relationships
    categories = relationship("Category", back_populates="owner", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="owner", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    owner = relationship("Vendor", back_populates="categories")
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    seo_meta_tag = Column(String) 
    is_active = Column(Boolean, default=True)

    # Relationships
    owner = relationship("Vendor", back_populates="products")
    category = relationship("Category", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True)
    
    name = Column(String, nullable=False) # e.g., "500g", "Large", "Red"
    sku = Column(String, unique=True, index=True, nullable=True) # Stock Keeping Unit
    price_paise = Column(Integer, nullable=False)
    stock_count = Column(Integer, default=0)

    product = relationship("Product", back_populates="variants")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True)
    
    image_url = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False) # Determines which photo shows up first

    product = relationship("Product", back_populates="images")