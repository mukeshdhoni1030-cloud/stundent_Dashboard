
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.database import engine
from app.limiter import limiter
from app.routes import auth, student, teacher, principal

app = FastAPI(
    title="Student Dashboard API",
    description="Student, Teacher and Principal Dashboard",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://localhost:4173",
        "https://student-dashboard.vercel.app",
    ],
    allow_origin_regex=r"https://student-dashboard-[a-z0-9-]+-kris-lynx-team\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(student.router)
app.include_router(teacher.router)
app.include_router(principal.router)


@app.get("/")
def home():
    return {"message": "Student Dashboard API is running"}


@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception:
        return {
            "status": "unhealthy",
            "database": "disconnected"
        }
