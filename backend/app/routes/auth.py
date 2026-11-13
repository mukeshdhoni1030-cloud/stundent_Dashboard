from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenResponse
from app.security import verify_password, create_access_token
from app.limiter import limiter


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# Maximum 5 login requests per minute per IP.
@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    total_started = perf_counter()

    # Measure the database user lookup without logging email or credentials.
    lookup_started = perf_counter()
    user = db.query(User).filter(
        User.email == login_data.email
    ).first()
    lookup_ms = (perf_counter() - lookup_started) * 1000

    if user is None:
        print(
            "Login timing: "
            f"user_lookup_ms={lookup_ms:.1f} "
            f"total_ms={(perf_counter() - total_started) * 1000:.1f} "
            "result=unknown_user",
            flush=True
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Password verification is intentionally computationally expensive.
    verify_started = perf_counter()
    password_correct = verify_password(
        login_data.password,
        user.password_hash
    )
    verify_ms = (perf_counter() - verify_started) * 1000

    if not password_correct:
        print(
            "Login timing: "
            f"user_lookup_ms={lookup_ms:.1f} "
            f"password_verify_ms={verify_ms:.1f} "
            f"total_ms={(perf_counter() - total_started) * 1000:.1f} "
            "result=invalid_password",
            flush=True
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token_started = perf_counter()
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role
        }
    )
    token_ms = (perf_counter() - token_started) * 1000
    total_ms = (perf_counter() - total_started) * 1000

    print(
        "Login timing: "
        f"user_lookup_ms={lookup_ms:.1f} "
        f"password_verify_ms={verify_ms:.1f} "
        f"token_ms={token_ms:.1f} "
        f"total_ms={total_ms:.1f} "
        "result=success",
        flush=True
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }