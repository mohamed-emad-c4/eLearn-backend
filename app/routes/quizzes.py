from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app import models, schemas, auth
from sqlalchemy.orm import joinedload
from datetime import datetime
from sqlalchemy.orm import selectinload
from app import models, schemas
from fastapi import Query

router = APIRouter(prefix="/api/quizzes", tags=["Quizzes"])

# ✅ Create a Quiz with Questions and Options
@router.post("/")
async def create_quiz(
    quiz_data: schemas.QuizCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(auth.get_current_admin)  # ✅ Restrict to Admins only
):
    new_quiz = models.Quiz(
        title=quiz_data.title,
        description=quiz_data.description,
        total_marks=quiz_data.total_marks,
        lesson_id=quiz_data.lesson_id,
        time_limit=quiz_data.time_limit
    )
    db.add(new_quiz)
    await db.flush()  # للحصول على معرّف الاختبار الجديد قبل إضافة الأسئلة

    for question in quiz_data.questions:
        new_question = models.Question(
            question_text=question.question_text,
            options=question.options,
            correct_answer=question.correct_answer,
            quiz_id=new_quiz.id
        )
        db.add(new_question)

    await db.commit()
    await db.refresh(new_quiz)
    
    return {"message": "Quiz created successfully", "quiz_id": new_quiz.id}



@router.get("/{quiz_id}")
async def get_quiz_by_id(quiz_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Quiz)
        .filter(models.Quiz.id == quiz_id)
        .options(selectinload(models.Quiz.questions))  # ✅ Eager load questions
    )
    quiz = result.scalars().first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return {
        "id": quiz.id,
        "title": quiz.title,
        "description": quiz.description,
        "total_marks": quiz.total_marks,
        "lesson_id": quiz.lesson_id,
        "time_limit": quiz.time_limit,
        "questions": [
            {
                "id": q.id,  # ✅ Add question ID here
                "question_text": q.question_text,
                "options": q.options,
                "correct_answer": q.correct_answer
            }
            for q in quiz.questions
        ]
    }


@router.get("/by-lesson/{lesson_id}")
async def get_quizzes_by_lesson_id(lesson_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Quiz)
        .filter(models.Quiz.lesson_id == lesson_id)
        .options(selectinload(models.Quiz.questions))  # ✅ Eager load questions
    )
    quizzes = result.scalars().all()

    if not quizzes:
        raise HTTPException(status_code=404, detail="No quizzes found for this lesson")

    return [
        {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "total_marks": quiz.total_marks,
            "time_limit": quiz.time_limit,
            "questions": [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "options": q.options,
                    # "correct_answer": q.correct_answer
                }
                for q in quiz.questions
            ]
        }
        for quiz in quizzes
    ]

@router.post("/{quiz_id}/submit", response_model=schemas.QuizResultResponse)
async def submit_quiz(
    quiz_id: int,
    submission: schemas.SubmitQuiz,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)  # ✅ Extract user from token
):
    # ✅ Fetch the quiz
    quiz = await db.execute(select(models.Quiz).filter(models.Quiz.id == quiz_id))
    quiz = quiz.scalars().first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # ✅ Calculate Score
    correct_answers = 0
    total_questions = len(submission.answers)

    for answer in submission.answers:
        question = await db.execute(
            select(models.Question).filter(models.Question.id == answer.question_id)
        )
        question = question.scalars().first()

        if question and question.correct_answer == answer.selected_option:
            correct_answers += 1

    # ✅ Save Submission to StudentQuiz
    submission_record = models.StudentQuiz(
        user_id=current_user.id,
        quiz_id=quiz_id,
        score=correct_answers,
        submitted_at=datetime.utcnow()
    )
    db.add(submission_record)
    await db.commit()
    await db.refresh(submission_record)

    return {
        "quiz_id": quiz_id,
        "user_id": current_user.id,
        "score": correct_answers,
        "total_questions": total_questions,
        "submitted_at": submission_record.submitted_at
    }






@router.get("/{quiz_id}/results", response_model=List[schemas.QuizResultResponse])
async def get_all_results(
    quiz_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    admin=Depends(auth.get_current_admin)  # تأكد من أنك تستخدم حساب Admin هنا
):
    result = await db.execute(
        select(models.StudentQuiz)  # ✅ التغيير هنا
        .filter(models.StudentQuiz.quiz_id == quiz_id)
        .order_by(models.StudentQuiz.score.desc())
        .offset(offset)
        .limit(limit)
        .options(selectinload(models.StudentQuiz.user))  # ✅ تحميل تفاصيل المستخدم
    )

    quiz_results = result.scalars().all()

    if not quiz_results:
        raise HTTPException(status_code=404, detail="No results found for this quiz.")

    return [
        {
            "quiz_id": result.quiz_id,
            "user_id": result.user_id,
            "username": result.user.username if result.user else "Unknown",  # ✅ التعامل مع احتمال غياب المستخدم
            "email": result.user.email if result.user else "Unknown",
            "score": result.score,
            "submitted_at": result.submitted_at
        }
        for result in quiz_results
    ]




@router.get("/{quiz_id}/results")
async def get_quiz_result(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    result = await db.execute(
        select(models.StudentQuiz)
        .filter(models.StudentQuiz.quiz_id == quiz_id, models.StudentQuiz.user_id == current_user.id)
    )
    quiz_result = result.scalars().first()

    if not quiz_result:
        raise HTTPException(status_code=404, detail="Result not found")

    return {
        "quiz_id": quiz_result.quiz_id,
        "user_id": quiz_result.user_id,
        "score": quiz_result.score,
        "submitted_at": quiz_result.submitted_at
    }






@router.delete("/{quiz_id}")
async def delete_quiz(quiz_id: int, db: AsyncSession = Depends(get_db), admin=Depends(auth.get_current_admin)):
    quiz = await db.execute(select(models.Quiz).filter(models.Quiz.id == quiz_id))
    quiz = quiz.scalars().first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    await db.delete(quiz)
    await db.commit()

    return {"message": "Quiz deleted successfully"}
