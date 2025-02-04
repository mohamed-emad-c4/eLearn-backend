from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app import models, schemas, auth
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/api/lessons", tags=["Lessons"])
# ✅ GET All Lessons by Chapter ID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/lessons", tags=["Lessons"])

@router.get("/chapter/{chapter_id}", response_model=list[schemas.LessonResponse])
async def get_lessons_by_chapter(chapter_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(models.Lesson).where(models.Lesson.chapter_id == chapter_id))
        lessons = result.scalars().all()

        if not lessons:
            raise HTTPException(status_code=404, detail="No lessons found for this chapter.")

        # ✅ Return lessons with 'lesson_id' instead of 'id'
        formatted_lessons = [
            schemas.LessonResponse(
                lesson_id=lesson.id,
                title=lesson.title,
                chapter_id=lesson.chapter_id,
                video_url=lesson.video_url,
                content=lesson.content,
                resource_links=lesson.resource_links,
                order_number=lesson.order_number
            )
            for lesson in lessons
        ]

        return formatted_lessons

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error: {str(e)}")

    
    
@router.get("/{chapter_id}", response_model=list[schemas.LessonCreate])
async def get_lessons(chapter_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Lesson).filter(models.Lesson.chapter_id == chapter_id))
    return result.scalars().all()

@router.get("/details/{id}", response_model=schemas.LessonCreate)
async def get_lesson_details(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Lesson).filter(models.Lesson.id == id))
    lesson = result.scalars().first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson

@router.post("/", response_model=schemas.LessonCreate)
async def create_lesson(
    lesson: schemas.LessonCreate,
    db: AsyncSession = Depends(get_db),
    instructor=Depends(auth.get_current_instructor)
):
    # Create new lesson instance
    new_lesson = models.Lesson(
        title=lesson.title,
        chapter_id=lesson.chapter_id,
        video_url=lesson.video_url,
        content=lesson.content,
        resource_links=lesson.resource_links,
        order_number=lesson.order_number  # ✅ Ensure this is provided
    )
    
    db.add(new_lesson)
    await db.commit()
    await db.refresh(new_lesson)
    
    return new_lesson


@router.delete("/{id}")
async def delete_lesson(id: int, db: AsyncSession = Depends(get_db), admin=Depends(auth.get_current_admin)):
    lesson = await db.execute(select(models.Lesson).filter(models.Lesson.id == id))
    lesson = lesson.scalars().first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    await db.delete(lesson)
    await db.commit()
    return {"message": "Lesson deleted successfully"}

# ✅ GET Lessons by Chapter ID
# ✅ Corrected: GET Lessons by Chapter ID
@router.get("/{chapter_id}/lessons", response_model=List[schemas.LessonCreate])
async def get_lessons_by_chapter(chapter_id: int, db: AsyncSession = Depends(get_db)):
    try:
        # ✅ Use async select for AsyncSession
        result = await db.execute(select(models.Lesson).where(models.Lesson.chapter_id == chapter_id))
        lessons = result.scalars().all()

        if not lessons:
            raise HTTPException(status_code=404, detail="No lessons found for this chapter.")

        return lessons

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error: {str(e)}")

