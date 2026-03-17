from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import jwt
import models, schemas, security
from database import get_db

router = APIRouter()

# This tells FastAPI where the login route is
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# THE VIP CHECKER: We will inject this into any route we want to protect
async def get_current_vendor(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decrypt the token to see who it belongs to
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
        
    # Double check they still exist in the database
    result = await db.execute(select(models.Vendor).filter(models.Vendor.email == email))
    vendor = result.scalars().first()
    if vendor is None:
        raise credentials_exception
    return vendor

@router.post("/api/auth/signup", response_model=schemas.VendorResponse)
async def signup(vendor: schemas.VendorCreate, db: AsyncSession = Depends(get_db)):
    # 1. Check if email already exists
    result = await db.execute(select(models.Vendor).filter(models.Vendor.email == vendor.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # 2. Hash the password securely before saving
    hashed_pwd = security.get_password_hash(vendor.password)
    new_vendor = models.Vendor(
        business_name=vendor.business_name,
        subdomain=vendor.subdomain,
        email=vendor.email,
        hashed_password=hashed_pwd
    )
    db.add(new_vendor)
    await db.commit()
    await db.refresh(new_vendor)
    return new_vendor

@router.post("/api/auth/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # OAuth2 defaults to 'username', so vendors will put their email in the username field
    result = await db.execute(select(models.Vendor).filter(models.Vendor.email == form_data.username))
    vendor = result.scalars().first()
    
    if not vendor or not security.verify_password(form_data.password, vendor.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    # Create the VIP Token
    access_token = security.create_access_token(data={"sub": vendor.email})
    return {"access_token": access_token, "token_type": "bearer"}