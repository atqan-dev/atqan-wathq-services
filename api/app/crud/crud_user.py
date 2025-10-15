"""
CRUD operations for User model.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base_tenant import CRUDBaseTenant
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBaseTenant[User, UserCreate, UserUpdate]):
    def get_by_email(
        self, db: Session, *, email: str, tenant_id: int = None
    ) -> User | None:
        query = db.query(User).filter(User.email == email)
        if tenant_id:
            query = query.filter(User.tenant_id == tenant_id)
        return query.first()

    def create(self, db: Session, *, obj_in: UserCreate, tenant_id: int = None) -> User:
        if tenant_id is None:
            from app.core.multitenancy import get_current_tenant

            tenant_id = get_current_tenant().tenant_id

        db_obj = User(
            email=obj_in.email,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            name_ar=obj_in.name_ar,
            logo=obj_in.logo,
            hashed_password=get_password_hash(obj_in.password),
            is_superuser=obj_in.is_superuser,
            tenant_id=tenant_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: UserUpdate | dict[str, Any]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(
        self, db: Session, *, email: str, password: str, tenant_id: int = None
    ) -> User | None:
        user = self.get_by_email(db, email=email, tenant_id=tenant_id)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def get_users_by_tenant(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> list[User]:
        return (
            db.query(User)
            .filter(User.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_count_by_tenant(self, db: Session, *, tenant_id: int) -> int:
        return db.query(User).filter(User.tenant_id == tenant_id).count()

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser

    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        return db.query(User).offset(skip).limit(limit).all()


user = CRUDUser(User)
