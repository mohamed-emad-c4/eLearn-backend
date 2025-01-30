from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/chapters", tags=["Chapters"])

@router.get("/{course_id}", response_model=list[schemas.ChapterCreate])
async def get_chapters(course_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Chapter).filter(models.Chapter.course_id == course_id))
    return result.scalars().all()

# ✅ Create Chapter (Only Instructors)
@router.post("/", response_model=schemas.ChapterCreate)
async def create_chapter(
    chapter: schemas.ChapterCreate,
    db: AsyncSession = Depends(get_db),
    instructor=Depends(auth.get_current_instructor)
):
    # ✅ Step 1: Check if the course exists before inserting the chapter
    result = await db.execute(select(models.Course).filter(models.Course.id == chapter.course_id))
    course = result.scalars().first()
    
    if not course:
        raise HTTPException(status_code=400, detail=f"Course with id {chapter.course_id} does not exist.")

    # ✅ Step 2: Insert the new chapter
    new_chapter = models.Chapter(
        title=chapter.title,
        content=chapter.content,
        order_number=chapter.order_number,
        course_id=chapter.course_id
    )
    
    db.add(new_chapter)
    await db.commit()
    await db.refresh(new_chapter)
    return new_chapter

# ✅ Delete Chapter (Only Admins)
@router.delete("/{course_id}/{chapter_id}")
async def delete_chapter(
    course_id: int,
    chapter_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(auth.get_current_admin)
):
    # ✅ Step 1: Check if the chapter exists within the specified course
    result = await db.execute(
        select(models.Chapter).filter(models.Chapter.id == chapter_id, models.Chapter.course_id == course_id)
    )
    chapter = result.scalars().first()

    if not chapter:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found in course {course_id}")

    # ✅ Step 2: Delete the chapter
    await db.delete(chapter)
    await db.commit()
    
    return {"message": f"Chapter {chapter_id} from course {course_id} deleted successfully"}
