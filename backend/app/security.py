
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

load_dotenv()

# Read security settings from .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)

if not SECRET_KEY or SECRET_KEY.startswith("replace_with"):
    raise ValueError("Please set a strong SECRET_KEY in your .env file")

# Password hashing system
password_hash = PasswordHash.recommended()


# ==================================
# 1. HASH A PASSWORD
# ==================================

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


# ==================================
# 2. VERIFY A PASSWORD
# ==================================

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# ==================================
# 3. CREATE JWT TOKEN
# ==================================

def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# ==================================
# 4. VERIFY JWT TOKEN
# ==================================

def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload

    except jwt.InvalidTokenError:
        return None
