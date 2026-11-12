
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.database import Base, engine
from app import models
from app.limiter import limiter

# Import API route files
from app.routes import auth, student, teacher, principal

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Dashboard API",
    description="Student, Teacher and Principal Dashboard",
    version="1.0.0"
)

# Configure rate limiting
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)
app.add_middleware(SlowAPIMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect API routes
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(teacher.router)
app.include_router(principal.router)


@app.get("/")
def home():
    return {"message": "Student Dashboard API is running"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected"
    }
