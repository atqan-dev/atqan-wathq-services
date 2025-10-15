"""
CRUD operations for ManagementUser model.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.management_user import ManagementUser
from app.schemas.management_user import ManagementUserCreate, ManagementUserUpdate


class CRUDManagementUser(CRUDBase[ManagementUser, ManagementUserCreate, ManagementUserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> ManagementUser | None:
        return db.query(ManagementUser).filter(ManagementUser.email == email).first()

    def create(self, db: Session, *, obj_in: ManagementUserCreate) -> ManagementUser:
        db_obj = ManagementUser(
            email=obj_in.email,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            name_ar=obj_in.name_ar,
            logo=obj_in.logo,
            hashed_password=get_password_hash(obj_in.password),
            is_active=obj_in.is_active,
            is_super_admin=obj_in.is_super_admin,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ManagementUser, obj_in: ManagementUserUpdate | dict[str, Any]
    ) -> ManagementUser:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> ManagementUser | None:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: ManagementUser) -> bool:
        return user.is_active

    def is_super_admin(self, user: ManagementUser) -> bool:
        return user.is_super_admin

    def activate(self, db: Session, *, user_id: int) -> ManagementUser | None:
        user = db.query(ManagementUser).filter(ManagementUser.id == user_id).first()
        if user:
            user.is_active = True
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def deactivate(self, db: Session, *, user_id: int) -> ManagementUser | None:
        user = db.query(ManagementUser).filter(ManagementUser.id == user_id).first()
        if user:
            user.is_active = False
            db.add(user)
            db.commit()
            db.refresh(user)
        return user


management_user = CRUDManagementUser(ManagementUser)
