
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_access_token


# Read the JWT token from the request
bearer_scheme = HTTPBearer()


# ==================================
# 1. GET THE CURRENT LOGGED-IN USER
# ==================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    # Verify the token
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # Get user ID from the token
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token information"
        )

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )

    # Find the user in PostgreSQL
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


# ==================================
# 2. CHECK USER ROLE
# ==================================

def require_roles(*allowed_roles):

    def role_checker(
        current_user: User = Depends(get_current_user)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )

        return current_user

    return role_checker


# ==================================
# 3. ROLE-SPECIFIC PERMISSIONS
# ==================================

require_student = require_roles("student")

require_teacher = require_roles("teacher")

require_principal = require_roles("principal")
