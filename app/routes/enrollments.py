from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/enrollments", tags=["Enrollments"])

@router.post("/", response_model=schemas.EnrollmentCreate)
async def enroll_student(enrollment: schemas.EnrollmentCreate, db: AsyncSession = Depends(get_db), user=Depends(auth.get_current_user)):
    existing_enrollment = await db.execute(select(models.Enrollment).filter(models.Enrollment.user_id == user.id, models.Enrollment.course_id == enrollment.course_id))
    if existing_enrollment.scalars().first():
        raise HTTPException(status_code=400, detail="User is already enrolled in this course")
    
    new_enrollment = models.Enrollment(user_id=user.id, course_id=enrollment.course_id)
    db.add(new_enrollment)
    await db.commit()
    await db.refresh(new_enrollment)
    return new_enrollment

@router.delete("/{id}")
async def cancel_enrollment(id: int, db: AsyncSession = Depends(get_db), user=Depends(auth.get_current_user)):
    enrollment = await db.execute(select(models.Enrollment).filter(models.Enrollment.id == id, models.Enrollment.user_id == user.id))
    enrollment = enrollment.scalars().first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found or not authorized to cancel")
    
    await db.delete(enrollment)
    await db.commit()
    return {"message": "Enrollment canceled successfully"}
