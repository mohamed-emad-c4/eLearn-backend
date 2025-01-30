from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/quizzes", tags=["Quizzes"])

@router.get("/{lesson_id}", response_model=list[schemas.QuizCreate])
async def get_quizzes(lesson_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Quiz).filter(models.Quiz.lesson_id == lesson_id))
    return result.scalars().all()

@router.post("/", response_model=schemas.QuizCreate)
async def create_quiz(quiz: schemas.QuizCreate, db: AsyncSession = Depends(get_db), instructor=Depends(auth.get_current_instructor)):
    new_quiz = models.Quiz(title=quiz.title, description=quiz.description, total_marks=quiz.total_marks, lesson_id=quiz.lesson_id)
    db.add(new_quiz)
    await db.commit()
    await db.refresh(new_quiz)
    return new_quiz

@router.delete("/{id}")
async def delete_quiz(id: int, db: AsyncSession = Depends(get_db), admin=Depends(auth.get_current_admin)):
    quiz = await db.execute(select(models.Quiz).filter(models.Quiz.id == id))
    quiz = quiz.scalars().first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    await db.delete(quiz)
    await db.commit()
    return {"message": "Quiz deleted successfully"}