"""
CRUD operations for ManagementUserProfile model.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.management_user_profile import ManagementUserProfile
from app.schemas.management_user_profile import ManagementUserProfileCreate, ManagementUserProfileUpdate


class CRUDManagementUserProfile(CRUDBase[ManagementUserProfile, ManagementUserProfileCreate, ManagementUserProfileUpdate]):
    def get_by_management_user_id(self, db: Session, *, management_user_id: int) -> ManagementUserProfile | None:
        return db.query(ManagementUserProfile).filter(ManagementUserProfile.management_user_id == management_user_id).first()

    def create(self, db: Session, *, obj_in: ManagementUserProfileCreate) -> ManagementUserProfile:
        db_obj = ManagementUserProfile(
            management_user_id=obj_in.management_user_id,
            fullname=obj_in.fullname,
            address=obj_in.address,
            mobile=obj_in.mobile,
            city=obj_in.city,
            company_name=obj_in.company_name,
            commercial_registration_number=obj_in.commercial_registration_number,
            entity_number=obj_in.entity_number,
            full_info=obj_in.full_info,
            email=obj_in.email,
            whatsapp_number=obj_in.whatsapp_number,
            avatar_image_url=obj_in.avatar_image_url,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ManagementUserProfile, obj_in: ManagementUserProfileUpdate | dict[str, Any]
    ) -> ManagementUserProfile:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)


management_user_profile = CRUDManagementUserProfile(ManagementUserProfile)
