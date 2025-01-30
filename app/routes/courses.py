from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/courses", tags=["Courses"])

@router.get("/", response_model=list[schemas.CourseCreate])
def get_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()

@router.post("/", response_model=schemas.CourseCreate)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    new_course = models.Course(title=course.title)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.delete("/{id}")
def delete_course(id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}
