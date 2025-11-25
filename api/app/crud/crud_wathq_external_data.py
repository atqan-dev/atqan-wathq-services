"""
CRUD operations for WATHQ External Data.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from uuid import UUID
import hashlib
import json

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.wathq_external_data import WathqExternalData
from app.schemas.wathq_external_data import WathqExternalDataCreate, WathqExternalDataUpdate


class CRUDWathqExternalData(CRUDBase[WathqExternalData, WathqExternalDataCreate, WathqExternalDataUpdate]):
    """CRUD operations for WATHQ external data with caching logic."""
    
    def generate_cache_key(
        self,
        service_id: UUID,
        tenant_id: Optional[int],
        user_id: int,
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a unique cache key for the request."""
        # Create a deterministic string from parameters
        key_parts = [
            str(service_id),
            str(tenant_id) if tenant_id else "global",
            str(user_id),
            json.dumps(params, sort_keys=True) if params else "{}"
        ]
        key_string = "|".join(key_parts)
        
        # Create a hash for the cache key
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def get_cached_data(
        self,
        db: Session,
        service_id: UUID,
        tenant_id: Optional[int],
        user_id: int,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[WathqExternalData]:
        """Get cached data if available and not expired."""
        cache_key = self.generate_cache_key(service_id, tenant_id, user_id, params)
        
        # Query for non-expired cache entry
        cached_entry = db.query(WathqExternalData).filter(
            and_(
                WathqExternalData.cache_key == cache_key,
                WathqExternalData.expires_at > datetime.utcnow()
            )
        ).first()
        
        return cached_entry
    
    def save_external_data(
        self,
        db: Session,
        service_id: UUID,
        tenant_id: Optional[int],
        user_id: int,
        data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        status_code: int = 200,
        ttl_seconds: int = 3600
    ) -> WathqExternalData:
        """Save external API data to cache."""
        cache_key = self.generate_cache_key(service_id, tenant_id, user_id, params)
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        
        # Check if entry exists
        existing = db.query(WathqExternalData).filter(
            WathqExternalData.cache_key == cache_key
        ).first()
        
        if existing:
            # Update existing entry
            existing.data = data
            existing.status_code = status_code
            existing.ttl_seconds = ttl_seconds
            existing.expires_at = expires_at
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new entry
            db_obj = WathqExternalData(
                tenant_id=tenant_id,
                user_id=user_id,
                service_id=service_id,
                request_params=params,
                cache_key=cache_key,
                data=data,
                status_code=status_code,
                ttl_seconds=ttl_seconds,
                expires_at=expires_at
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
    
    def get_user_cached_data(
        self,
        db: Session,
        user_id: int,
        tenant_id: Optional[int] = None,
        service_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[WathqExternalData]:
        """Get all cached data for a user."""
        query = db.query(WathqExternalData).filter(
            WathqExternalData.user_id == user_id
        )
        
        if tenant_id is not None:
            query = query.filter(WathqExternalData.tenant_id == tenant_id)
        
        if service_id:
            query = query.filter(WathqExternalData.service_id == service_id)
        
        # Only return non-expired entries
        query = query.filter(WathqExternalData.expires_at > datetime.utcnow())
        
        return query.offset(skip).limit(limit).all()
    
    def get_tenant_cached_data(
        self,
        db: Session,
        tenant_id: int,
        service_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[WathqExternalData]:
        """Get all cached data for a tenant."""
        query = db.query(WathqExternalData).filter(
            WathqExternalData.tenant_id == tenant_id
        )
        
        if service_id:
            query = query.filter(WathqExternalData.service_id == service_id)
        
        # Only return non-expired entries
        query = query.filter(WathqExternalData.expires_at > datetime.utcnow())
        
        return query.offset(skip).limit(limit).all()
    
    def clear_expired_cache(self, db: Session) -> int:
        """Clear all expired cache entries."""
        expired_count = db.query(WathqExternalData).filter(
            WathqExternalData.expires_at <= datetime.utcnow()
        ).count()
        
        db.query(WathqExternalData).filter(
            WathqExternalData.expires_at <= datetime.utcnow()
        ).delete()
        
        db.commit()
        return expired_count
    
    def clear_user_cache(
        self,
        db: Session,
        user_id: int,
        service_id: Optional[UUID] = None
    ) -> int:
        """Clear cache for a specific user."""
        query = db.query(WathqExternalData).filter(
            WathqExternalData.user_id == user_id
        )
        
        if service_id:
            query = query.filter(WathqExternalData.service_id == service_id)
        
        count = query.count()
        query.delete()
        db.commit()
        
        return count
    
    def clear_tenant_cache(
        self,
        db: Session,
        tenant_id: int,
        service_id: Optional[UUID] = None
    ) -> int:
        """Clear cache for a specific tenant."""
        query = db.query(WathqExternalData).filter(
            WathqExternalData.tenant_id == tenant_id
        )
        
        if service_id:
            query = query.filter(WathqExternalData.service_id == service_id)
        
        count = query.count()
        query.delete()
        db.commit()
        
        return count


wathq_external_data = CRUDWathqExternalData(WathqExternalData)
