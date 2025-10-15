"""
Route guards for authentication and authorization.
"""

from functools import wraps
from typing import Callable, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas.user import TokenPayload
from app import crud

reusable_oauth2 = HTTPBearer()


def super_admin_required(func: Callable) -> Callable:
    """
    Decorator that requires super admin privileges (management super admin or regular superuser).
    Can be applied to any FastAPI route.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract dependencies from kwargs
        db = kwargs.get('db')
        token = kwargs.get('token')
        
        if not db or not token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Missing required dependencies"
            )
        
        try:
            payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
            token_data = TokenPayload(**payload)
        except (JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )

        # Check if management user
        if token_data.is_management_user:
            user = crud.management_user.get(db, id=token_data.sub)
            if not user or not user.is_active or not user.is_super_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Management super admin privileges required"
                )
        else:
            # Check if regular super user
            user = crud.user.get(db, id=token_data.sub)
            if not user or not user.is_active or not user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Super user privileges required"
                )
        
        return await func(*args, **kwargs)
    return wrapper


def management_user_required(func: Callable) -> Callable:
    """
    Decorator that requires management user privileges.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        db = kwargs.get('db')
        token = kwargs.get('token')
        
        if not db or not token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Missing required dependencies"
            )
        
        try:
            payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
            token_data = TokenPayload(**payload)
        except (JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )

        if not token_data.is_management_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Management user privileges required"
            )

        user = crud.management_user.get(db, id=token_data.sub)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Active management user required"
            )
        
        return await func(*args, **kwargs)
    return wrapper


# Dependency functions for use with FastAPI Depends()
def require_super_admin():
    """Dependency that requires super admin privileges."""
    def _check_super_admin(
        db: Session = Depends(deps.get_db),
        token: str = Depends(reusable_oauth2)
    ):
        try:
            payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
            token_data = TokenPayload(**payload)
        except (JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )

        # Check if management user
        if token_data.is_management_user:
            user = crud.management_user.get(db, id=token_data.sub)
            if not user or not user.is_active or not user.is_super_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Management super admin privileges required"
                )
            return {"type": "management", "user": user}
        else:
            # Check if regular super user
            user = crud.user.get(db, id=token_data.sub)
            if not user or not user.is_active or not user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Super user privileges required"
                )
            return {"type": "regular", "user": user}
    
    return _check_super_admin


def require_management_user():
    """Dependency that requires management user privileges."""
    def _check_management_user(
        db: Session = Depends(deps.get_db),
        token: str = Depends(reusable_oauth2)
    ):
        try:
            payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
            token_data = TokenPayload(**payload)
        except (JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )

        if not token_data.is_management_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Management user privileges required"
            )

        user = crud.management_user.get(db, id=token_data.sub)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Active management user required"
            )
        
        return user
    
    return _check_management_user