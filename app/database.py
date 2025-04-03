import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Get the database URL from .env file
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create the async engine for PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a session maker for async database operations
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Define a base class for declarative models
Base = declarative_base()

# Function to get a database session
async def get_db():
    async with SessionLocal() as session:
        yield session
