from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/api/progress", tags=["Progress"])

# ✅ Helper Function to Check Chapter Completion
async def check_and_complete_chapter(db: AsyncSession, user_id: int, chapter_id: int):
    # Get all lessons in the chapter
    lessons = (await db.execute(
        select(models.Lesson).filter(models.Lesson.chapter_id == chapter_id)
    )).scalars().all()

    # Check if all lessons are completed
    for lesson in lessons:
        progress = (await db.execute(
            select(models.LessonProgress)
            .filter(models.LessonProgress.user_id == user_id, models.LessonProgress.lesson_id == lesson.id)
        )).scalars().first()

        if not progress or not progress.is_completed:
            return False  # Found an incomplete lesson

    # ✅ Mark Chapter as Complete
    chapter_progress = (await db.execute(
        select(models.ChapterProgress)
        .filter(models.ChapterProgress.user_id == user_id, models.ChapterProgress.chapter_id == chapter_id)
    )).scalars().first()

    if not chapter_progress:
        chapter_progress = models.ChapterProgress(
            user_id=user_id,
            chapter_id=chapter_id,
            course_id=lessons[0].chapter.course_id,
            progress=100.0,
            is_completed=True
        )
        db.add(chapter_progress)
    else:
        chapter_progress.progress = 100.0
        chapter_progress.is_completed = True

    await db.commit()
    return True

# ✅ Helper Function to Check Course Completion
async def check_and_complete_course(db: AsyncSession, user_id: int, course_id: int):
    # Get all chapters in the course
    chapters = (await db.execute(
        select(models.Chapter).filter(models.Chapter.course_id == course_id)
    )).scalars().all()

    # Check if all chapters are completed
    for chapter in chapters:
        progress = (await db.execute(
            select(models.ChapterProgress)
            .filter(models.ChapterProgress.user_id == user_id, models.ChapterProgress.chapter_id == chapter.id)
        )).scalars().first()

        if not progress or not progress.is_completed:
            return False  # Found an incomplete chapter

    # ✅ Mark Course as Complete
    course_progress = (await db.execute(
        select(models.CourseProgress)
        .filter(models.CourseProgress.user_id == user_id, models.CourseProgress.course_id == course_id)
    )).scalars().first()

    if not course_progress:
        course_progress = models.CourseProgress(
            user_id=user_id,
            course_id=course_id,
            progress=100.0,
            is_completed=True
        )
        db.add(course_progress)
    else:
        course_progress.progress = 100.0
        course_progress.is_completed = True

    await db.commit()
    return True

# ✅ Complete Lesson Endpoint
@router.post("/lessons/complete", response_model=schemas.LessonProgress)
async def complete_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Eager load related chapter and course
    lesson = (await db.execute(
        select(models.Lesson)
        .options(selectinload(models.Lesson.chapter))
        .filter(models.Lesson.id == lesson_id)
    )).scalars().first()

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Check if the lesson is already completed
    progress_record = (await db.execute(
        select(models.LessonProgress)
        .filter(models.LessonProgress.user_id == current_user.id, models.LessonProgress.lesson_id == lesson_id)
    )).scalars().first()

    if progress_record:
        if progress_record.is_completed:
            return progress_record
        progress_record.is_completed = True
        progress_record.progress = 100.0
    else:
        progress_record = models.LessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            chapter_id=lesson.chapter_id,
            course_id=lesson.chapter.course_id,
            progress=100.0,
            is_completed=True
        )
        db.add(progress_record)

    await db.commit()
    await db.refresh(progress_record)

    # ✅ Check and Complete Chapter if All Lessons Completed
    chapter_completed = await check_and_complete_chapter(db, current_user.id, lesson.chapter_id)

    # ✅ If Chapter is Completed, Check and Complete Course
    if chapter_completed:
        await check_and_complete_course(db, current_user.id, lesson.chapter.course_id)

    return progress_record
# ✅ Get Chapter Progress for Current User
@router.get("/chapters/{chapter_id}")
async def get_chapter_progress(
    chapter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # ✅ الحصول على جميع الدروس داخل الشابتر
    lessons = (await db.execute(
        select(models.Lesson).filter(models.Lesson.chapter_id == chapter_id)
    )).scalars().all()

    total_lessons = len(lessons)
    if total_lessons == 0:
        raise HTTPException(status_code=404, detail="No lessons found in this chapter.")

    # ✅ حساب عدد الدروس المكتملة للمستخدم الحالي
    completed_lessons = (await db.execute(
        select(models.LessonProgress)
        .filter(
            models.LessonProgress.user_id == current_user.id,
            models.LessonProgress.chapter_id == chapter_id,
            models.LessonProgress.is_completed == True
        )
    )).scalars().all()

    completed_count = len(completed_lessons)

    # ✅ حساب نسبة التقدم
    progress_percentage = (completed_count / total_lessons) * 100

    # ✅ إرجاع النتيجة
    return {
        "chapter_id": chapter_id,
        "user_id": current_user.id,
        "completed_lessons": completed_count,
        "total_lessons": total_lessons,
        "progress_percentage": round(progress_percentage, 2)
    }
@router.get("/courses/{course_id}/progress")
async def get_course_progress(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # ✅ الحصول على جميع الدروس المرتبطة بالكورس
    lessons = (await db.execute(
        select(models.Lesson)
        .join(models.Chapter)
        .filter(models.Chapter.course_id == course_id)
    )).scalars().all()

    total_lessons = len(lessons)
    if total_lessons == 0:
        raise HTTPException(status_code=404, detail="No lessons found in this course.")

    # ✅ حساب عدد الدروس المكتملة للمستخدم الحالي
    completed_lessons = (await db.execute(
        select(models.LessonProgress)
        .filter(
            models.LessonProgress.user_id == current_user.id,
            models.LessonProgress.course_id == course_id,
            models.LessonProgress.is_completed == True
        )
    )).scalars().all()

    completed_count = len(completed_lessons)

    # ✅ حساب نسبة التقدم في الكورس بناءً على الدروس المكتملة
    progress_percentage = (completed_count / total_lessons) * 100

    # ✅ إرجاع النتيجة
    return {
        "course_id": course_id,
        "user_id": current_user.id,
        "completed_lessons": completed_count,
        "total_lessons": total_lessons,
        "progress_percentage": round(progress_percentage, 2)
    }

