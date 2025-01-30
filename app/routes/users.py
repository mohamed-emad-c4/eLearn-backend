import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app import models, schemas, auth
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await db.execute(select(models.User).filter(models.User.email == user.email))
    if existing_user.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username = await db.execute(select(models.User).filter(models.User.username == user.username))
    if existing_username.scalars().first():
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = auth.get_password_hash(user.password)

    new_user = models.User(
        name=user.name,
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=user.role
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user
@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_profile(user: models.User = Depends(auth.get_current_user)):
    return user

@router.get("/{id}", response_model=schemas.UserResponse)
async def get_user(id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    result = await db.execute(select(models.User).filter(models.User.id == id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{id}")
async def delete_user(id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Fetch the user from the database
    result = await db.execute(select(models.User).filter(models.User.id == id))
    user_to_delete = result.scalars().first()

    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")

    # Allow deletion if the user is an admin or if they are deleting their own account
    if current_user.id != id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You do not have permission to delete this user.")

    await db.delete(user_to_delete)
    await db.commit()
    
    return {"message": "User deleted successfully"}


@router.post("/login", response_model=schemas.Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter(models.User.email == user_credentials.username))
    user = result.scalars().first()
    
    if not user or not auth.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


