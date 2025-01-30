from pydantic import BaseModel, Field
from typing import Optional, List

# User Schemas
class UserCreate(BaseModel):
    name: str
    username: str
    email: str
    password: str
    role: Optional[str] = "student"

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Course Schemas
class CourseCreate(BaseModel):
    name: str
    level: str
    description: Optional[str] = None
    category: Optional[str] = None
    language: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[str] = "active"

    class Config:
        from_attributes = True
class ChapterCreate(BaseModel):
    title: str
    content: Optional[str]  # Add content field
    order_number: Optional[int]  # Add order_number field
    course_id: int

    class Config:
        from_attributes = True


class LessonCreate(BaseModel):
    title: str
    chapter_id: int
    video_url: Optional[str] = None
    content: Optional[dict] = None  # Ensure JSON compatibility
    resource_links: Optional[List[str]] = None  # Accepts list of URLs
    order_number: int  # Required field to fix the error

    class Config:
        from_attributes = True

class EnrollmentCreate(BaseModel):
    course_id: int

# Quiz & Question Schemas
class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    total_marks: int
    lesson_id: int

    class Config:
        from_attributes = True

class QuestionCreate(BaseModel):
    quiz_id: int
    question_text: str
    options: List[str]
    correct_answer: int

    class Config:
        from_attributes = True

# Problem Schemas
class ProblemCreate(BaseModel):
    title: str
    description: str
    difficulty: str
    tags: List[str]
    sample_input: Optional[str] = None
    sample_output: Optional[str] = None
    constraints: Optional[str] = None
    author_id: int

    class Config:
        from_attributes = True

# Student Progress Schemas
class LessonProgressCreate(BaseModel):
    lesson_id: int
    user_id: int
    chapter_id: int
    course_id: int
    progress: float
    is_completed: bool

    class Config:
        from_attributes = True

class LessonProgress(BaseModel):
    lesson_id: int
    user_id: int
    chapter_id: int
    course_id: int
    progress: float
    is_completed: bool

    class Config:
        from_attributes = True

class ChapterProgress(BaseModel):
    chapter_id: int
    user_id: int
    course_id: int
    progress: float
    is_completed: bool

    class Config:
        from_attributes = True

class CourseProgress(BaseModel):
    course_id: int
    user_id: int
    progress: float
    is_completed: bool

    class Config:
        from_attributes = True