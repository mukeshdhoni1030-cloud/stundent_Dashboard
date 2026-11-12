
from app.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token
)


def test_password_is_hashed():
    password = "Student@123"

    hashed_password = get_password_hash(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password)


def test_wrong_password_is_rejected():
    password = "Student@123"

    hashed_password = get_password_hash(password)

    assert not verify_password("WrongPassword", hashed_password)


def test_jwt_token_creation():
    token = create_access_token({
        "sub": "2",
        "role": "student"
    })

    assert isinstance(token, str)
    assert len(token) > 0


def test_jwt_token_decoding():
    token = create_access_token({
        "sub": "2",
        "role": "student"
    })

    decoded_data = decode_access_token(token)

    assert decoded_data is not None
    assert decoded_data["sub"] == "2"
    assert decoded_data["role"] == "student"


def test_invalid_jwt_token():
    decoded_data = decode_access_token("invalid.token.value")

    assert decoded_data is None
