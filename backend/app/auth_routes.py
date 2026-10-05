import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth_models import User
from app.audit_models import AuditLog
from app.auth_engine import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token"
)

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

def validate_username(username):
    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username is required"
        )

    if len(username) < 4:
        raise HTTPException(
            status_code=400,
            detail="Username must contain at least 4 characters"
        )

    if len(username) > 100:
        raise HTTPException(
            status_code=400,
            detail="Username must not exceed 100 characters"
        )

    if not re.fullmatch(
        r"[A-Za-z0-9_.-]+",
        username
    ):
        raise HTTPException(
            status_code=400,
            detail="Username can contain only letters, numbers, underscore, dot and hyphen"
        )

def validate_password(password):
    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 8 characters"
        )

    if len(password) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password must not exceed 72 characters"
        )

    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one uppercase letter"
        )

    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one lowercase letter"
        )

    if not re.search(r"[0-9]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one number"
        )

@router.post("/register")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    username = request.username.strip()

    validate_username(username)
    validate_password(request.password)

    existing_user = db.query(User).filter(
        User.username == username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    user = User(
        username=username,
        password_hash=hash_password(
            request.password
        ),
        role="Investigator"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    audit = AuditLog(
        username=user.username,
        action="USER_REGISTERED",
        resource=f"User:{user.user_id}",
        details="New Investigator account created"
    )

    db.add(audit)
    db.commit()

    return {
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role,
        "message": "User registered successfully"
    }

@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    username = request.username.strip()

    user = db.query(User).filter(
        User.username == username
    ).first()

    if not user or not verify_password(
        request.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(
        user.user_id,
        user.username,
        user.role
    )

    audit = AuditLog(
        username=user.username,
        action="USER_LOGIN",
        resource=f"User:{user.user_id}",
        details="Successful user login"
    )

    db.add(audit)
    db.commit()

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role
    }

@router.post("/token")
def token_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    username = form_data.username.strip()

    user = db.query(User).filter(
        User.username == username
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(
        user.user_id,
        user.username,
        user.role
    )

    audit = AuditLog(
        username=user.username,
        action="USER_LOGIN",
        resource=f"User:{user.user_id}",
        details="Successful OAuth2 login"
    )

    db.add(audit)
    db.commit()

    return {
        "access_token": token,
        "token_type": "bearer"
    }

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = decode_access_token(token)

        user_id = int(
            payload["sub"]
        )

        user = db.query(User).filter(
            User.user_id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return user

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )