import os
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import google.generativeai as genai
import models, schemas
from database import get_db
from routers.auth import get_current_vendor # IMPORT THE LOCK

router = APIRouter()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    ai_model = genai.GenerativeModel('gemini-2.5-flash')
else:
    ai_model = None

async def generate_seo_meta(name: str, description: str) -> str:
    if not ai_model:
        return f"Order fresh {name} online from our local store."
    prompt = f"Write a punchy, 150-character SEO meta description for a local shop product: {name}. Details: {description}."
    try:
        response = ai_model.generate_content(prompt)
        return response.text.strip().replace('"', '')
    except Exception:
        return f"Order fresh {name} online from our local store."

# THE LOCK IS APPLIED HERE via 'current_vendor'
@router.post("/api/dashboard/products", response_model=schemas.ProductResponse)
async def create_product(
    product: schemas.ProductCreate, 
    db: AsyncSession = Depends(get_db),
    current_vendor: models.Vendor = Depends(get_current_vendor) 
):
    seo_tag = await generate_seo_meta(product.name, product.description)
    
    new_product = models.Product(
        vendor_id=current_vendor.id, # Securely linked to whoever is logged in!
        name=product.name,
        description=product.description,
        seo_meta_tag=seo_tag,
        price_paise=product.price_paise,
        image_url=product.image_url
    )
    
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product