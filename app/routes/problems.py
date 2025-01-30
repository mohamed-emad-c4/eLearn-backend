from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/problems", tags=["Problems"])

@router.get("/")
def get_problems(db: Session = Depends(get_db)):
    return db.query(models.Problem).all()

@router.post("/{problem_id}/submit")
def submit_problem(problem_id: int, db: Session = Depends(get_db)):
    problem = db.query(models.Problem).filter(models.Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return {"message": "Problem submitted successfully"}
