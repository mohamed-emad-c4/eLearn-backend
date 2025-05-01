# eLearn Backend

A FastAPI-based backend for an e-learning platform that supports courses, lessons, quizzes, and user management.

## Features

- 👤 **User Management**: Registration, authentication, and authorization with JWT tokens
- 📚 **Course Management**: Create, read, update, and delete courses
- 📝 **Lesson Management**: Create lessons with content and attach them to courses
- 📋 **Quiz System**: Create quizzes with questions and options
- 📊 **Quiz Assessment**: Take quizzes and view results
- 🔒 **Role-Based Access Control**: Admin and student roles with different permissions

## API Endpoints

### Authentication
- POST `/api/auth/register` - Register a new user
- POST `/api/auth/token` - Get access token

### Courses
- GET `/api/courses` - Get all courses
- GET `/api/courses/{course_id}` - Get course by ID
- POST `/api/courses` - Create a new course (admin only)
- PUT `/api/courses/{course_id}` - Update a course (admin only)
- DELETE `/api/courses/{course_id}` - Delete a course (admin only)

### Lessons
- GET `/api/lessons/by-course/{course_id}` - Get lessons by course ID
- GET `/api/lessons/{lesson_id}` - Get lesson by ID
- POST `/api/lessons` - Create a new lesson (admin only)
- PUT `/api/lessons/{lesson_id}` - Update a lesson (admin only)
- DELETE `/api/lessons/{lesson_id}` - Delete a lesson (admin only)

### Quizzes
- GET `/api/quizzes/{quiz_id}` - Get quiz by ID
- GET `/api/quizzes/by-lesson/{lesson_id}` - Get quizzes by lesson ID
- POST `/api/quizzes` - Create a quiz with questions (admin only)
- POST `/api/quizzes/{quiz_id}/submit` - Submit a quiz
- GET `/api/quizzes/{quiz_id}/results` - Get all quiz results (admin only)
- GET `/api/quizzes/{quiz_id}/my-result` - Get personal quiz result (any authenticated user)
- DELETE `/api/quizzes/{quiz_id}` - Delete a quiz (admin only)

## Setup and Installation

### Prerequisites
- Python 3.8+
- PostgreSQL

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/eLearn-backend.git
   cd eLearn-backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables in a `.env` file:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/elearndb
   SECRET_KEY=yoursecretkey
   ```

5. Initialize the database:
   ```bash
   alembic upgrade head
   ```

6. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

After starting the application, access the automatic API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Technologies Used

- FastAPI - Web framework
- SQLAlchemy - ORM
- Pydantic - Data validation
- PostgreSQL - Database
- Alembic - Database migrations
- JWT - Authentication
- Uvicorn - ASGI server

## Development

### Database Migrations

After modifying models, create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
``` 