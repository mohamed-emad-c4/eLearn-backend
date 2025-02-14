from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app import auth, models, schemas

router = APIRouter(prefix="/api/problems", tags=["Problems"])

# ---------------------------
# Tag Endpoints
# ---------------------------

@router.post("/tags", response_model=schemas.ProblemTagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(tag: schemas.ProblemTagCreate, db: AsyncSession = Depends(get_db), admin=Depends(auth.get_current_admin)):
    existing_tag = await db.execute(select(models.ProblemTag).filter(models.ProblemTag.name == tag.name))
    if existing_tag.scalars().first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tag already exists.")
    
    new_tag = models.ProblemTag(name=tag.name, description=tag.description)
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    return new_tag

@router.get("/tags", response_model=list[schemas.ProblemTagResponse])
async def get_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.ProblemTag))
    return result.scalars().all()

# ---------------------------
# Problem Endpoints
# ---------------------------

@router.get("/", response_model=list[schemas.ProblemResponse])
async def get_problems(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Problem)
        .options(selectinload(models.Problem.tag))
    )
    return result.scalars().all()

@router.get("/", response_model=list[schemas.ProblemResponse])
async def get_problems(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Problem)
        .options(selectinload(models.Problem.tag))
    )
    problems = result.scalars().all()
    return problems
@router.post("/", response_model=schemas.ProblemResponse, status_code=status.HTTP_201_CREATED)
async def create_problem(problem: schemas.ProblemCreate, db: AsyncSession = Depends(get_db), admin=Depends(auth.get_current_admin)):
    new_problem = models.Problem(
        title=problem.title,
        description=problem.description,
        level=problem.level,
        tag_id=problem.tag_id,
        constraints=problem.constraints,
        author_id=admin.id
    )
    db.add(new_problem)
    await db.commit()
    await db.refresh(new_problem)
    return new_problem

@router.get("/{problem_id}", response_model=schemas.ProblemResponse)
async def get_problem(problem_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Problem)
        .options(selectinload(models.Problem.tag))
        .filter(models.Problem.id == problem_id)
    )
    problem = result.scalars().first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found.")
    return problem

# ---------------------------
# Problem Solving Endpoints
# ---------------------------

@router.post("/solve", response_model=schemas.ProblemAttemptResponse)
async def solve_problem(attempt: schemas.ProblemAttemptCreate, db: AsyncSession = Depends(get_db), user=Depends(auth.get_current_user)):
    problem = await db.execute(select(models.Problem).filter(models.Problem.id == attempt.problem_id))
    problem = problem.scalars().first()
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found.")

    # المستخدم هو اللي بيحدد is_correct
    is_correct = attempt.is_correct

    # حساب النقاط حسب الـ Level
    points = problem.level if is_correct else 0

    # إضافة النقاط للمستخدم
    user.points += points
    await db.commit()

    # حفظ المحاولة في قاعدة البيانات
    new_attempt = models.ProblemAttempt(
        user_id=user.id,
        problem_id=attempt.problem_id,
        user_solution=attempt.user_solution,
        is_correct=is_correct,
        points_earned=points
    )
    db.add(new_attempt)
    await db.commit()
    await db.refresh(new_attempt)
    return new_attempt

@router.get("/{problem_id}/attempts", response_model=list[schemas.ProblemAttemptResponse])
async def get_problem_attempts(problem_id: int, db: AsyncSession = Depends(get_db), user=Depends(auth.get_current_user)):
    result = await db.execute(
        select(models.ProblemAttempt)
        .filter(models.ProblemAttempt.problem_id == problem_id, models.ProblemAttempt.user_id == user.id)
    )
    return result.scalars().all()
