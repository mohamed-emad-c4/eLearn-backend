from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/chapters", tags=["Chapters"])

@router.get("/{course_id}", response_model=list[schemas.ChapterCreate])
def get_chapters(course_id: int, db: Session = Depends(get_db)):
    return db.query(models.Chapter).filter(models.Chapter.course_id == course_id).all()

@router.post("/", response_model=schemas.ChapterCreate)
def create_chapter(chapter: schemas.ChapterCreate, db: Session = Depends(get_db)):
    new_chapter = models.Chapter(title=chapter.title, course_id=chapter.course_id)
    db.add(new_chapter)
    db.commit()
    db.refresh(new_chapter)
    return new_chapter
