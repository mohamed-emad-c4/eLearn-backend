from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, auth
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter(prefix="/api/courses", tags=["Courses"])

@router.get("/", response_model=list[schemas.CourseCreate])
async def get_courses(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 10):
    result = await db.execute(select(models.Course).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/", response_model=schemas.CourseCreate)
async def create_course(
    course: schemas.CourseCreate,
    db: AsyncSession = Depends(get_db),
    instructor=Depends(auth.get_current_instructor)
):
    new_course = models.Course(
        name=course.name,
        instructor_id=instructor.id,
        level=course.level,
        description=course.description,
        category=course.category,
        language=course.language,
        image_url=course.image_url,
        status=course.status
    )

    db.add(new_course)
    await db.commit()
    await db.refresh(new_course)
    return new_course




@router.delete("/{id}")
async def delete_course(id: int, db: AsyncSession = Depends(get_db), admin=Depends(auth.get_current_admin)):
    result = await db.execute(select(models.Course).filter(models.Course.id == id))
    course = result.scalars().first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    await db.delete(course)
    await db.commit()
    return {"message": "Course deleted successfully"}
