from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/chapters", tags=["Chapters"])

@router.get("/{course_id}", response_model=list[schemas.ChapterCreate])
async def get_chapters(course_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Chapter).filter(models.Chapter.course_id == course_id))
    return result.scalars().all()

@router.post("/", response_model=schemas.ChapterCreate)
async def create_chapter(chapter: schemas.ChapterCreate, db: AsyncSession = Depends(get_db), instructor=Depends(auth.get_current_instructor)):
    new_chapter = models.Chapter(title=chapter.title, content=chapter.content, order_number=chapter.order_number, course_id=chapter.course_id)
    db.add(new_chapter)
    await db.commit()
    await db.refresh(new_chapter)
    return new_chapter

@router.delete("/{id}")
async def delete_chapter(id: int, db: AsyncSession = Depends(get_db), admin=Depends(auth.get_current_admin)):
    chapter = await db.execute(select(models.Chapter).filter(models.Chapter.id == id))
    chapter = chapter.scalars().first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    await db.delete(chapter)
    await db.commit()
    return {"message": "Chapter deleted successfully"}