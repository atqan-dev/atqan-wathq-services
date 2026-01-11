from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid
from app.db.base_class import Base


class CrRequest(Base):
    __tablename__ = "cr_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    url = Column(String(500), nullable=False)
    cr_number = Column(String(50), nullable=False, index=True)
    language = Column(String(10), nullable=False)
    response = Column(JSONB, nullable=True)
    status_number = Column(Integer, nullable=True, index=True)
    status_text = Column(String(100), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_by = Column(String(100), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    updated_by = Column(String(100), nullable=True)
