from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/lessons", tags=["Lessons"])

@router.get("/{chapter_id}", response_model=list[schemas.LessonCreate])
def get_lessons(chapter_id: int, db: Session = Depends(get_db)):
    return db.query(models.Lesson).filter(models.Lesson.chapter_id == chapter_id).all()

@router.post("/", response_model=schemas.LessonCreate)
def create_lesson(lesson: schemas.LessonCreate, db: Session = Depends(get_db)):
    new_lesson = models.Lesson(title=lesson.title, chapter_id=lesson.chapter_id)
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    return new_lesson
