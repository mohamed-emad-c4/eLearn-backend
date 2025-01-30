from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/enrollments", tags=["Enrollments"])

@router.post("/", response_model=schemas.EnrollmentCreate)
def enroll_student(enrollment: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    new_enrollment = models.Enrollment(user_id=enrollment.user_id, course_id=enrollment.course_id)
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    return new_enrollment

@router.delete("/{id}")
def cancel_enrollment(id: int, db: Session = Depends(get_db)):
    enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db.delete(enrollment)
    db.commit()
    return {"message": "Enrollment canceled"}
