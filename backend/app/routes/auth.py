"""
Authentication routes for the support system.
Simple JWT-based authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

security = HTTPBearer()

# Users (in production, this would be a database)
USERS = {
    "agent@company.com": {
        "password": "agent123",
        "name": "Sarah Johnson",
        "role": "agent"
    },
    "manager@company.com": {
        "password": "manager123",
        "name": "John Manager",
        "role": "manager"
    },
    "admin@company.com": {
        "password": "admin123",
        "name": "Admin User",
        "role": "admin"
    }
}


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"email": email, "role": payload.get("role"), "name": payload.get("name")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_role(role: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") != role and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login and get access token."""
    user = USERS.get(request.email)
    if not user or user["password"] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": request.email, "role": user["role"], "name": user["name"]}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={"email": request.email, "name": user["name"], "role": user["role"]}
    )


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info."""
    return current_user


@router.get("/protected")
async def protected_route(current_user: dict = Depends(require_role("agent"))):
    """Protected route for agents."""
    return {"message": f"Hello {current_user['name']}, you have agent access"}


@router.get("/admin-only")
async def admin_route(current_user: dict = Depends(require_role("admin"))):
    """Admin only route."""
    return {"message": f"Hello {current_user['name']}, you have admin access"}