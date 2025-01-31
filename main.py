from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from app.database import Base, engine
from app.routes import users, courses, chapters, lessons, enrollments, quizzes, problems

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base, engine
from app.routes import progress
from app.routes import questions

# تشغيل الوظيفة عند بدء التشغيل

app = FastAPI(
    title="Educational API",
    version="1.0.0",
    description="API for managing users, courses, lessons, quizzes, and coding challenges.",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    await init_db()
# إعداد تسجيل الأخطاء (Logging)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# معالج خطأ عام
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."},
    )
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response status: {response.status_code}")
    return response
# تضمين جميع المسارات
app.include_router(users.router, prefix="/api")
app.include_router(courses.router)
app.include_router(chapters.router)
app.include_router(lessons.router)
app.include_router(enrollments.router)
app.include_router(quizzes.router)
app.include_router(problems.router)
app.include_router(progress.router)
app.include_router(questions.router) 