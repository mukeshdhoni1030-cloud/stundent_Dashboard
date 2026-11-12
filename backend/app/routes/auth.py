
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


# ==================================
# COMMON LOGIN API
# Maximum 5 requests per minute per IP
# ==================================

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    # Find user using email
    user = db.query(User).filter(
        User.email == login_data.email
    ).first()

    # Check whether user exists
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify entered password
    password_correct = verify_password(
        login_data.password,
        user.password_hash
    )

    if not password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create JWT token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role
        }
    )

    # Return token and user's role
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }
