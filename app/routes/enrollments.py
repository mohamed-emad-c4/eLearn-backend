from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/enrollments", tags=["Enrollments"])

@router.post("/", response_model=schemas.EnrollmentCreate)
async def enroll_student(
    enrollment: schemas.EnrollmentCreate,  # Only `course_id` comes from request
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)  # ✅ Get user from token
):
    # Check if the user is already enrolled in the course
    result = await db.execute(
        select(models.Enrollment).filter(
            models.Enrollment.user_id == user.id,
            models.Enrollment.course_id == enrollment.course_id
        )
    )
    existing_enrollment = result.scalars().first()

    if existing_enrollment:
        raise HTTPException(status_code=400, detail="User is already enrolled in this course")

    # Create new enrollment with user_id from the token
    new_enrollment = models.Enrollment(
        user_id=user.id,  # ✅ Extracted from token
        course_id=enrollment.course_id
    )

    db.add(new_enrollment)
    await db.commit()
    await db.refresh(new_enrollment)
    
    return new_enrollment

@router.delete("/{id}")
async def cancel_enrollment(
    id: int,  # Enrollment ID
    db: AsyncSession = Depends(get_db),
    user: models.User = Depends(auth.get_current_user)  # ✅ Get user from token
):
    # Fetch the enrollment record (ensure it belongs to the logged-in user)
    result = await db.execute(
        select(models.Enrollment).filter(
            models.Enrollment.id == id,  # Find by enrollment ID
            models.Enrollment.user_id == user.id  # Ensure it's the logged-in user
        )
    )
    enrollment = result.scalars().first()

    # If enrollment doesn't exist or belongs to another user, return 403
    if not enrollment:
        raise HTTPException(status_code=403, detail="You are not authorized to cancel this enrollment or it does not exist.")

    # Delete the enrollment
    await db.delete(enrollment)
    await db.commit()

    return {"message": "Enrollment canceled successfully"}