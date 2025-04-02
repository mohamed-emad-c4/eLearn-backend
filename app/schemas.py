from datetime import datetime
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

class OptionCreate(BaseModel):
    option_text: str

# Quiz & Question Schemas
class QuestionCreate(BaseModel):
    question_text: str
    options: List[str]
    correct_answer: int

    class Config:
        orm_mode = True

class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    total_marks: int
    lesson_id: int
    time_limit: Optional[int] = 10  # ⏱️ الوقت المحدد (افتراضي 10 دقائق)
    questions: List[QuestionCreate]  # ✅ قائمة الأسئلة

    class Config:
        orm_mode = True

# ✅ Modify Quiz Schema to Include Questions in Response
# استجابة الكويز مع الوقت وتاريخ الانتهاء
class QuizResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    total_marks: int
    lesson_id: int
    time_limit: Optional[int]
    questions: List[QuestionCreate]  # ✅ عرض الأسئلة أيضًا

    class Config:
        orm_mode = True


# Problem Schemas

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
class CourseResponse(BaseModel):
    id: int
    name: str
    level: str
    description: Optional[str]
    category: Optional[str]
    language: Optional[str]
    image_url: Optional[str]
    status: Optional[str]

    class Config:
        orm_mode = True


class TokenVerificationResponse(BaseModel):
    valid: bool
    user: Optional[dict]

class Chapter(BaseModel):
    id: int
    title: str
    content: Optional[str]
    order_number: Optional[int]
    course_id: int

    class Config:
        from_attributes = True


class Lesson(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    video_url: Optional[str] = None
    chapter_id: int

    class Config:
        from_attributes = True  # For Pydantic V2 compatibility

class LessonResponse(BaseModel):
    lesson_id: int               # ✅ Use 'lesson_id' instead of 'id'
    title: str
    chapter_id: int
    video_url: Optional[str] = None
    content: Optional[dict] = None
    resource_links: Optional[List[str]] = None
    order_number: int

    class Config:
        orm_mode = True


class QuizAttemptResponse(BaseModel):
    id: int
    user_id: int
    quiz_id: int
    date: datetime
    score: float

    class Config:
        from_attributes = True  # For Pydantic V2 compatibility
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": 101,
                "quiz_id": 202,
                "date": "2024-04-27T12:30:00Z",
                "score": 85.0
            }
        }

# Quiz Attempt Creation
class QuizAttemptCreate(BaseModel):
    user_id: int
    quiz_id: int
    score: float
    date: Optional[datetime] = datetime.utcnow()  # Defaults to current datetime

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "user_id": 101,
                "quiz_id": 202,
                "score": 92.5,
                "date": "2024-04-27T14:45:00Z"
            }
        }

# Option Update
class OptionUpdate(BaseModel):
    id: int
    option_text: str
    is_correct: bool

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "option_text": "Option A",
                "is_correct": True
            }
        }

# Question Update
class QuestionUpdate(BaseModel):
    id: int
    question_text: str
    question_type: str
    mark: int
    options: List[OptionUpdate]

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 101,
                "question_text": "What is the capital of France?",
                "question_type": "multiple_choice",
                "mark": 5,
                "options": [
                    {"id": 1, "option_text": "Paris", "is_correct": True},
                    {"id": 2, "option_text": "London", "is_correct": False},
                    {"id": 3, "option_text": "Berlin", "is_correct": False}
                ]
            }
        }

# Quiz Update
class QuizUpdate(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    total_marks: int
    time_limit: int
    questions: List[QuestionUpdate]

    class Config:
        from_attributes = True  # Pydantic V2 compatibility
        schema_extra = {
            "example": {
                "id": 1001,
                "title": "General Knowledge Quiz",
                "description": "Test your knowledge on general topics.",
                "total_marks": 20,
                "time_limit": 30,
                "questions": [
                    {
                        "id": 101,
                        "question_text": "What is the capital of France?",
                        "question_type": "multiple_choice",
                        "mark": 5,
                        "options": [
                            {"id": 1, "option_text": "Paris", "is_correct": True},
                            {"id": 2, "option_text": "London", "is_correct": False},
                            {"id": 3, "option_text": "Berlin", "is_correct": False}
                        ]
                    },
                    {
                        "id": 102,
                        "question_text": "Which planet is known as the Red Planet?",
                        "question_type": "multiple_choice",
                        "mark": 5,
                        "options": [
                            {"id": 4, "option_text": "Earth", "is_correct": False},
                            {"id": 5, "option_text": "Mars", "is_correct": True},
                            {"id": 6, "option_text": "Jupiter", "is_correct": False}
                        ]
                    }
                ]
            }
        }




class OptionSchema(BaseModel):
    id: int
    question_id: int
    option_text: str
    is_correct: bool

class QuestionSchema(BaseModel):
    id: int
    quiz_id: int
    question_text: str
    question_type: str
    mark: int
    options: List[OptionSchema]

class QuizSchema(BaseModel):
    id: int
    lesson_id: int
    total_mark: int
    time_limit: int
    questions: List[QuestionSchema]

    class Config:
        orm_mode = True


# Schema لتقديم الكويز (Submit Quiz)
class AnswerSubmission(BaseModel):
    question_id: int
    selected_option: int

class SubmitQuiz(BaseModel):
    answers: List[AnswerSubmission]


# Schema لعرض نتيجة الكويز
class QuizResultResponse(BaseModel):
    quiz_id: int
    user_id: int
    score: int
    submitted_at: datetime

    class Config:
        from_attributes = True

class ProblemAttemptCreate(BaseModel):
    problem_id: int
    user_solution: str
    is_correct: bool  

    class Config:
        from_attributes = True

class ProblemAttemptResponse(BaseModel):
    id: int
    problem_id: int
    user_solution: str
    is_correct: bool
    points_earned: int
    attempt_time: datetime

    class Config:
        orm_mode = True

class ProblemTagCreate(BaseModel):
    name: str
    description: Optional[str] = None
    url_image: Optional[str] = None

    class Config:
        from_attributes = True

class ProblemTagResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    url_image: Optional[str] = None


    class Config:
        orm_mode = True


class ProblemCreate(BaseModel):
    title: str
    description: str
    level: int  # ✅ مستوى الصعوبة
    tag_id: int  # ✅ ربط المشكلة بالـ Tag

    constraints: Optional[str] = None

    class Config:
        from_attributes = True

class ProblemResponse(BaseModel):
    id: int
    title: str
    description: str
    level: int
    tag: ProblemTagResponse  # ✅ عرض تفاصيل الـ Tag

    constraints: Optional[str] = None

    class Config:
        orm_mode = True


















