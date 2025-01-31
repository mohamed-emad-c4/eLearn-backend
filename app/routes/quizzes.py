from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app import models, schemas, auth
from sqlalchemy.orm import joinedload  # ✅ Add this import

router = APIRouter(prefix="/api/quizzes", tags=["Quizzes"])

@router.get("/{quiz_id}", response_model=schemas.QuizResponse)
async def get_quiz(quiz_id: int, db: AsyncSession = Depends(get_db)):
    # ✅ Fetch quiz along with questions using `joinedload`
    result = await db.execute(
        select(models.Quiz)
        .options(joinedload(models.Quiz.questions))  # ✅ Load related questions
        .filter(models.Quiz.id == quiz_id)
    )
    quiz = result.scalars().first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # ✅ Return Quiz with its Questions
    return schemas.QuizResponse(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        total_marks=quiz.total_marks,
        lesson_id=quiz.lesson_id,
        questions=[
            schemas.QuestionCreate(
                question_text=q.question_text,
                options=q.options,
                correct_answer=q.correct_answer
            ) for q in quiz.questions  # ✅ Include questions in response
        ]
    )
@router.post("/", response_model=schemas.QuizResponse)
async def create_quiz(
    quiz_data: schemas.QuizCreate,
    db: AsyncSession = Depends(get_db),
    instructor=Depends(auth.get_current_instructor)
):
    # ✅ Step 1: Create the Quiz
    new_quiz = models.Quiz(
        title=quiz_data.title,
        description=quiz_data.description,
        total_marks=quiz_data.total_marks,
        lesson_id=quiz_data.lesson_id
    )
    db.add(new_quiz)
    await db.commit()
    await db.refresh(new_quiz)

    # ✅ Step 2: Add Questions (if provided)
    questions = []
    if hasattr(quiz_data, "questions"):  # Ensure `questions` exist in request
        for question in quiz_data.questions:
            new_question = models.Question(
                quiz_id=new_quiz.id,
                question_text=question.question_text,
                options=question.options,
                correct_answer=question.correct_answer
            )
            db.add(new_question)
            questions.append(new_question)

    await db.commit()

    # ✅ Step 3: Return Quiz with Questions
    return schemas.QuizResponse(
        id=new_quiz.id,
        title=new_quiz.title,
        description=new_quiz.description,
        total_marks=new_quiz.total_marks,
        lesson_id=new_quiz.lesson_id,
        questions=quiz_data.questions  # ✅ Return questions in response
    )

@router.delete("/{id}")
async def delete_quiz(id: int, db: AsyncSession = Depends(get_db), admin=Depends(auth.get_current_admin)):
    quiz = await db.execute(select(models.Quiz).filter(models.Quiz.id == id))
    quiz = quiz.scalars().first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    await db.delete(quiz)
    await db.commit()
    return {"message": "Quiz deleted successfully"}