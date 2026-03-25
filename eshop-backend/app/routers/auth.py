from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import time

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.core.rbac import (
    validate_username,
    validate_email,
    validate_password,
    sanitize_input,
)
from app.core.security_middleware import rate_limiter
from app.models.models import User
from app.schemas.schemas import UserCreate, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["auth"])

# Track failed login attempts
failed_logins = {}


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Validate username
    username = sanitize_input(user.username, 50)
    if not validate_username(username):
        raise HTTPException(
            status_code=400,
            detail="Invalid username. Use 3-50 alphanumeric characters or underscore.",
        )

    # Validate email
    email = sanitize_input(user.email, 255).lower()
    if not validate_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format.")

    # Validate password strength
    valid, error_msg = validate_password(user.password)
    if not valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Check if username exists
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Check if email exists
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user with hashed password
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        first_name=sanitize_input(user.first_name or "", 100),
        last_name=sanitize_input(user.last_name or "", 100),
        phone=sanitize_input(user.phone or "", 20),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    client_ip = request.client.host if request.client else "unknown"

    # Check for brute force attack
    current_time = time.time()
    if client_ip in failed_logins:
        attempts = [
            t for t in failed_logins[client_ip] if current_time - t < 300
        ]  # 5 minutes
        failed_logins[client_ip] = attempts

        if len(attempts) >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later.",
            )

    # Get user
    user = db.query(User).filter(User.username == form_data.username).first()

    # Verify password
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Record failed attempt
        if client_ip not in failed_logins:
            failed_logins[client_ip] = []
        failed_logins[client_ip].append(current_time)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled"
        )

    # Clear failed login attempts on success
    if client_ip in failed_logins:
        del failed_logins[client_ip]

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_user_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user
