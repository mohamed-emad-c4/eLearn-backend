from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CourseCreate(BaseModel):
    title: str

class ChapterCreate(BaseModel):
    title: str

class LessonCreate(BaseModel):
    title: str

class EnrollmentCreate(BaseModel):
    user_id: int
    course_id: int
