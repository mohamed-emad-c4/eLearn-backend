from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import auth, models, schemas
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas

router = APIRouter(prefix="/api/problems", tags=["Problems"])
router_problems = APIRouter(prefix="/api/problems", tags=["Problems"])

@router_problems.get("/", response_model=list[schemas.ProblemCreate])
async def get_problems(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Problem))
    return result.scalars().all()

@router_problems.post("/", response_model=schemas.ProblemCreate)
async def create_problem(problem: schemas.ProblemCreate, db: AsyncSession = Depends(get_db), instructor=Depends(auth.get_current_instructor)):
    new_problem = models.Problem(title=problem.title, description=problem.description, difficulty=problem.difficulty, tags=problem.tags, sample_input=problem.sample_input, sample_output=problem.sample_output, constraints=problem.constraints, author_id=instructor.id)
    db.add(new_problem)
    await db.commit()
    await db.refresh(new_problem)
    return new_problem

@router_problems.delete("/{id}")
async def delete_problem(id: int, db: AsyncSession = Depends(get_db), admin=Depends(auth.get_current_admin)):
    problem = await db.execute(select(models.Problem).filter(models.Problem.id == id))
    problem = problem.scalars().first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    await db.delete(problem)
    await db.commit()
    return {"message": "Problem deleted successfully"}