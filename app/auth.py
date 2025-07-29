# app/auth.py
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

SECRET_KEY = "super-secret-key"  # Replace with environment var in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()

fake_users_db = {"demo": {"username": "demo", "password": "test123"}}  # DEMO ONLY!


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"Username received: {form_data.username!r}")
    print(f"Password received: {form_data.password!r}")
    # Just for testing:
    if form_data.username == "wrong":
        raise HTTPException(status_code=401, detail="This is a forced 401 for test")
    # Explicit check for empty/missing username/password
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required",
        )
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        {"sub": user["username"]}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
