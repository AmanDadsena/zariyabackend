from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import models, schemas
from database import get_db

router = APIRouter()

def get_subdomain(request: Request):
    host = request.headers.get("host", "")
    if not host:
        raise HTTPException(status_code=400, detail="No host header found")
    parts = host.split('.')
    # Local fallback testing
    if len(parts) <= 2 or parts[0] in ["www", "api", "localhost:8000", "127"]:
        return "test-shop" 
    return parts[0]

@router.get("/api/storefront/products", response_model=list[schemas.ProductResponse])
async def get_storefront_products(
    subdomain: str = Depends(get_subdomain), 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Vendor).filter(models.Vendor.subdomain == subdomain))
    vendor = result.scalars().first()
    
    if not vendor or not vendor.is_active:
        raise HTTPException(status_code=404, detail="Store not found")

    result = await db.execute(select(models.Product).filter(models.Product.vendor_id == vendor.id))
    return result.scalars().all()