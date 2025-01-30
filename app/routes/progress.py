from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/progress", tags=["Progress"])

@router.get("/courses/{user_id}", response_model=list[schemas.CourseProgress])
async def get_course_progress(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.CourseProgress).filter(models.CourseProgress.user_id == user_id))
    return result.scalars().all()

@router.get("/lessons/{user_id}", response_model=list[schemas.LessonProgress])
async def get_lesson_progress(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.LessonProgress).filter(models.LessonProgress.user_id == user_id))
    return result.scalars().all()

@router.get("/chapters/{user_id}", response_model=list[schemas.ChapterProgress])
async def get_chapter_progress(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.ChapterProgress).filter(models.ChapterProgress.user_id == user_id))
    return result.scalars().all()

@router.post("/lessons/complete", response_model=schemas.LessonProgress)
async def complete_lesson(progress: schemas.LessonProgressCreate, db: AsyncSession = Depends(get_db), user=Depends(auth.get_current_user)):
    existing_progress = await db.execute(select(models.LessonProgress).filter(models.LessonProgress.user_id == user.id, models.LessonProgress.lesson_id == progress.lesson_id))
    existing_progress = existing_progress.scalars().first()
    
    if existing_progress:
        existing_progress.is_completed = True
        await db.commit()
        return existing_progress
    
    new_progress = models.LessonProgress(user_id=user.id, lesson_id=progress.lesson_id, chapter_id=progress.chapter_id, course_id=progress.course_id, progress=100.0, is_completed=True)
    db.add(new_progress)
    await db.commit()
    await db.refresh(new_progress)
    return new_progress