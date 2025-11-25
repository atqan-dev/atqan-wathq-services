"""
Base CRUD operations with tenant filtering.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.core.multitenancy import get_current_tenant
from app.crud.base import CRUDBase, CreateSchemaType, ModelType, UpdateSchemaType


class CRUDBaseTenant(CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD class with tenant filtering for models that have tenant_id.
    """

    def get(self, db: Session, id: Any, tenant_id: int = None) -> ModelType | None:
        """Get object by id with tenant filtering."""
        if tenant_id is None:
            tenant_id = get_current_tenant().tenant_id
        
        query = db.query(self.model).filter(self.model.id == id)
        if hasattr(self.model, 'tenant_id') and tenant_id:
            query = query.filter(self.model.tenant_id == tenant_id)
        return query.first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, tenant_id: int = None
    ) -> list[ModelType]:
        """Get multiple objects with tenant filtering."""
        if tenant_id is None:
            tenant_id = get_current_tenant().tenant_id
            
        query = db.query(self.model)
        if hasattr(self.model, 'tenant_id') and tenant_id:
            query = query.filter(self.model.tenant_id == tenant_id)
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType, tenant_id: int = None) -> ModelType:
        """Create object with tenant_id."""
        if tenant_id is None:
            tenant_id = get_current_tenant().tenant_id
            
        obj_in_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
        
        # Add tenant_id if model has it
        if hasattr(self.model, 'tenant_id') and tenant_id:
            obj_in_data['tenant_id'] = tenant_id
            
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int, tenant_id: int = None) -> ModelType:
        """Remove object with tenant filtering."""
        if tenant_id is None:
            tenant_id = get_current_tenant().tenant_id
            
        query = db.query(self.model).filter(self.model.id == id)
        if hasattr(self.model, 'tenant_id') and tenant_id:
            query = query.filter(self.model.tenant_id == tenant_id)
            
        obj = query.first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj