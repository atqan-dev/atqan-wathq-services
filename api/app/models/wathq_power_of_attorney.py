"""
Power of Attorney models for Wathq schema.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class PowerOfAttorney(Base):
    """
    Power of Attorney master table.
    Links to wathq_call_logs via log_id for data traceability.
    Same POA data can be repeated but each record is linked to a unique call log.
    """

    __tablename__ = "power_of_attorney"
    __table_args__ = {"schema": "wathq"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    log_id = Column(
        UUID(as_uuid=True), ForeignKey("wathq_call_logs.id"), nullable=True, index=True
    )
    fetched_at = Column(DateTime(timezone=True), nullable=True)
    code = Column(String(50), nullable=False, index=True)
    status = Column(String(50), nullable=True)
    issue_hijri_date = Column(String(20), nullable=True)
    issue_greg_date = Column(Date, nullable=True)
    expiry_hijri_date = Column(String(20), nullable=True)
    expiry_greg_date = Column(Date, nullable=True)
    attorney_type = Column(String(100), nullable=True)
    location_id = Column(Integer, nullable=True)
    location_name = Column(String(255), nullable=True)
    agents_behavior_ar = Column(String(50), nullable=True)
    agents_behavior_en = Column(String(50), nullable=True)
    document_text = Column(Text, nullable=True)

    # Audit fields
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    request_body = Column(JSON, nullable=True)

    # Relationships
    allowed_actors = relationship(
        "PoaAllowedActor",
        back_populates="power_of_attorney",
        cascade="all, delete-orphan",
    )
    principals = relationship(
        "PoaPrincipal", back_populates="power_of_attorney", cascade="all, delete-orphan"
    )
    agents = relationship(
        "PoaAgent", back_populates="power_of_attorney", cascade="all, delete-orphan"
    )
    text_list_items = relationship(
        "PoaTextListItem",
        back_populates="power_of_attorney",
        cascade="all, delete-orphan",
    )


class PoaAllowedActor(Base):
    """POA Allowed Actors table"""

    __tablename__ = "poa_allowed_actors"
    __table_args__ = {"schema": "wathq"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    poa_id = Column(
        Integer,
        ForeignKey("wathq.power_of_attorney.id", ondelete="CASCADE"),
        nullable=False,
    )
    identity_no = Column(String(50), nullable=True)
    social_type_id = Column(Integer, nullable=True)
    social_type_name = Column(String(100), nullable=True)
    name = Column(String(255), nullable=True)
    type_id = Column(Integer, nullable=True)
    type_name = Column(String(100), nullable=True)
    type_name_en = Column(String(100), nullable=True)
    sefa_id = Column(Integer, nullable=True)
    sefa_name = Column(String(100), nullable=True)
    national_number = Column(String(50), nullable=True)
    cr_number = Column(String(50), nullable=True)
    karar_number = Column(Integer, nullable=True)
    malaki_number = Column(Integer, nullable=True)
    document_type_name = Column(String(100), nullable=True)
    company_represent_type_id = Column(Integer, nullable=True)
    company_represent_type_name = Column(String(100), nullable=True)
    sakk_number = Column(Integer, nullable=True)

    # Audit fields
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

    # Relationship
    power_of_attorney = relationship("PowerOfAttorney", back_populates="allowed_actors")


class PoaPrincipal(Base):
    """POA Principals table"""

    __tablename__ = "poa_principals"
    __table_args__ = {"schema": "wathq"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    poa_id = Column(
        Integer,
        ForeignKey("wathq.power_of_attorney.id", ondelete="CASCADE"),
        nullable=False,
    )
    principal_identity_id = Column(String(50), nullable=True)
    name = Column(String(255), nullable=True)
    birthday = Column(DateTime, nullable=True)
    sefa_id = Column(Integer, nullable=True)
    sefa_name = Column(String(100), nullable=True)

    # Audit fields
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

    # Relationship
    power_of_attorney = relationship("PowerOfAttorney", back_populates="principals")


class PoaAgent(Base):
    """POA Agents table"""

    __tablename__ = "poa_agents"
    __table_args__ = {"schema": "wathq"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    poa_id = Column(
        Integer,
        ForeignKey("wathq.power_of_attorney.id", ondelete="CASCADE"),
        nullable=False,
    )
    agent_identity_id = Column(String(50), nullable=True)
    name = Column(String(255), nullable=True)
    birthday = Column(DateTime, nullable=True)
    sefa_id = Column(Integer, nullable=True)
    sefa_name = Column(String(100), nullable=True)

    # Audit fields
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

    # Relationship
    power_of_attorney = relationship("PowerOfAttorney", back_populates="agents")


class PoaTextListItem(Base):
    """POA Text List Items table"""

    __tablename__ = "poa_text_list_items"
    __table_args__ = {"schema": "wathq"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    poa_id = Column(
        Integer,
        ForeignKey("wathq.power_of_attorney.id", ondelete="CASCADE"),
        nullable=False,
    )
    list_item_id = Column(Integer, nullable=True)
    text_content = Column(Text, nullable=True)
    item_type = Column(String(100), nullable=True)

    # Audit fields
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

    # Relationship
    power_of_attorney = relationship(
        "PowerOfAttorney", back_populates="text_list_items"
    )
