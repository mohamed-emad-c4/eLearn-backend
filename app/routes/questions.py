from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/questions", tags=["Questions"])

# ✅ Get all questions for a specific quiz
@router.get("/{quiz_id}", response_model=list[schemas.QuestionCreate])
async def get_questions(quiz_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Question).filter(models.Question.quiz_id == quiz_id))
    questions = result.scalars().all()

    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this quiz")

    return questions

# ✅ Create a new question for a specific quiz
@router.post("/{quiz_id}", response_model=schemas.QuestionCreate)
async def create_question(
    quiz_id: int,
    question_data: schemas.QuestionCreate,
    db: AsyncSession = Depends(get_db),
    instructor=Depends(auth.get_current_instructor)  # Only instructors can create questions
):
    # Ensure the quiz exists
    result = await db.execute(select(models.Quiz).filter(models.Quiz.id == quiz_id))
    quiz = result.scalars().first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Create new question
    new_question = models.Question(
        quiz_id=quiz_id,
        question_text=question_data.question_text,
        options=question_data.options,
        correct_answer=question_data.correct_answer
    )

    db.add(new_question)
    await db.commit()
    await db.refresh(new_question)
    
    return new_question

# ✅ Delete a question (Only Admins or Instructors)
@router.delete("/{question_id}")
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    instructor=Depends(auth.get_current_instructor)  # Only instructors/admins can delete
):
    result = await db.execute(select(models.Question).filter(models.Question.id == question_id))
    question = result.scalars().first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    await db.delete(question)
    await db.commit()

    return {"message": f"Question {question_id} deleted successfully"}
