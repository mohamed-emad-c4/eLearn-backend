from fastapi import FastAPI
from app.database import Base, engine
from app.routes import users, courses, chapters, lessons, enrollments, quizzes, problems

# إنشاء الجداول عند بدء التشغيل
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Educational API", version="1.0.0", description="API for managing educational content.")

# تضمين جميع المسارات
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(chapters.router)
app.include_router(lessons.router)
app.include_router(enrollments.router)
app.include_router(quizzes.router)
app.include_router(problems.router)
