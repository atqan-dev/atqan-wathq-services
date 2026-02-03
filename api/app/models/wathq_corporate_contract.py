"""
Corporate Contract models for Wathq schema.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    Numeric,
    Text,
    DateTime,
    JSON,
    ForeignKey,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CorporateContract(Base):
    """
    Corporate Contract model representing contract data from Wathq.
    Links to wathq_call_logs via log_id for data traceability.
    Same contract data can be repeated but each record is linked to a unique call log.
    """

    __tablename__ = "corporate_contracts"
    __table_args__ = {"schema": "wathq"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    log_id = Column(
        UUID(as_uuid=True), ForeignKey("wathq_call_logs.id"), nullable=True, index=True
    )
    fetched_at = Column(DateTime(timezone=True), nullable=True)
    contract_id = Column(Integer, nullable=True)
    contract_copy_number = Column(Integer, nullable=True)
    contract_date = Column(Date, nullable=True)

    # Entity Details
    cr_national_number = Column(String(50), nullable=True)
    cr_number = Column(String(50), nullable=True, index=True)
    entity_name = Column(String(255), nullable=True)
    entity_name_lang_desc = Column(String(50), nullable=True)
    company_duration = Column(Integer, nullable=True)
    headquarter_city_name = Column(String(100), nullable=True)
    is_license_based = Column(Boolean, nullable=True)
    entity_type_name = Column(String(100), nullable=True)
    entity_form_name = Column(String(100), nullable=True)

    # Fiscal Year
    fiscal_calendar_type = Column(String(50), nullable=True)
    fiscal_year_end_month = Column(Integer, nullable=True)
    fiscal_year_end_day = Column(Integer, nullable=True)
    fiscal_year_end_year = Column(Integer, nullable=True)

    # Capital Summary
    currency_name = Column(String(50), nullable=True)
    total_capital = Column(Numeric(15, 2), nullable=True)
    paid_capital = Column(Numeric(15, 2), nullable=True)
    cash_capital = Column(Numeric(15, 2), nullable=True)
    in_kind_capital = Column(Numeric(15, 2), nullable=True)

    # Set Aside / Profit Allocation
    is_set_aside_enabled = Column(Boolean, nullable=True)
    profit_allocation_percentage = Column(Numeric(5, 2), nullable=True)
    profit_allocation_purpose = Column(Text, nullable=True)
    additional_decision_text = Column(Text, nullable=True)

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
    stocks = relationship(
        "ContractStock", back_populates="contract", cascade="all, delete-orphan"
    )
    parties = relationship(
        "ContractParty", back_populates="contract", cascade="all, delete-orphan"
    )
    managers = relationship(
        "ContractManager", back_populates="contract", cascade="all, delete-orphan"
    )
    management_config = relationship(
        "ContractManagementConfig",
        back_populates="contract",
        cascade="all, delete-orphan",
        uselist=False,
    )
    activities = relationship(
        "ContractActivity", back_populates="contract", cascade="all, delete-orphan"
    )
    articles = relationship(
        "ContractArticle", back_populates="contract", cascade="all, delete-orphan"
    )
    decisions = relationship(
        "ContractDecision", back_populates="contract", cascade="all, delete-orphan"
    )
    notification_channels = relationship(
        "NotificationChannel", back_populates="contract", cascade="all, delete-orphan"
    )


class ContractStock(Base):
    """Contract Stock model."""

    __tablename__ = "contract_stocks"
    __table_args__ = {"schema": "wathq"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(
        Integer,
        ForeignKey("wathq.corporate_contracts.id", ondelete="CASCADE"),
        nullable=False,
    )
    stock_type_name = Column(String(100), nullable=True)
    stock_count = Column(Integer, nullable=True)
    stock_value = Column(Numeric(15, 2), nullable=True)

    contract = relationship("CorporateContract", back_populates="stocks")


class ContractParty(Base):
    """Contract Party model."""

    __tablename__ = "contract_parties"
    __table_args__ = {"schema": "wathq"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(
        Integer,
        ForeignKey("wathq.corporate_contracts.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=True)
    type_name = Column(String(100), nullable=True)
    identity_number = Column(String(50), nullable=True)
    identity_type = Column(String(50), nullable=True)
    nationality = Column(String(100), nullable=True)

    # Guardian Info
    guardian_name = Column(String(255), nullable=True)
    guardian_identity_number = Column(String(50), nullable=True)
    is_father_guardian = Column(Boolean, nullable=True)

    contract = relationship("CorporateContract", back_populates="parties")


class ContractManager(Base):
    """Contract Manager model."""

    __tablename__ = "contract_managers"
    __table_args__ = {"schema": "wathq"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(
        Integer,
        ForeignKey("wathq.corporate_contracts.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=True)
    type_name = Column(String(100), nullable=True)
    is_licensed = Column(Boolean, nullable=True)
    identity_number = Column(String(50), nullable=True)
    nationality = Column(String(100), nullable=True)
    position_name = Column(String(100), nullable=True)

    contract = relationship("CorporateContract", back_populates="managers")


class ContractManagementConfig(Base):
    """Contract Management Configuration model."""

    __tablename__ = "contract_management_config"
    __table_args__ = {"schema": "wathq"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(
        Integer,
        ForeignKey("wathq.corporate_contracts.id", ondelete="CASCADE"),
        nullable=False,
    )
    structure_name = Column(String(100), nullable=True)
    meeting_quorum_name = Column(String(100), nullable=True)
    can_delegate_attendance = Column(Boolean, nullable=True)
    term_years = Column(Integer, nullable=True)

    contract = relationship("CorporateContract", back_populates="management_config")


class ContractActivity(Base):
    """Contract Activity model."""

    __tablename__ = "contract_activities"
    __table_args__ = {"schema": "wathq"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(
        Integer,
        ForeignKey("wathq.corporate_contracts.id", ondelete="CASCADE"),
        nullable=False,
    )
    activity_id = Column(String(50), nullable=True)
    activity_name = Column(Text, nullable=True)

    contract = relationship("CorporateContract", back_populates="activities")


class ContractArticle(Base):
    """Contract Article model."""

    __tablename__ = "contract_articles"
    __table_args__ = {"schema": "wathq"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(
        Integer,
        ForeignKey("wathq.corporate_contracts.id", ondelete="CASCADE"),
        nullable=False,
    )
    original_id = Column(Integer, nullable=True)
    article_text = Column(Text, nullable=True)
    part_name = Column(String(100), nullable=True)

    contract = relationship("CorporateContract", back_populates="articles")


class ContractDecision(Base):
    """Contract Decision model."""

    __tablename__ = "contract_decisions"
    __table_args__ = {"schema": "wathq"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(
        Integer,
        ForeignKey("wathq.corporate_contracts.id", ondelete="CASCADE"),
        nullable=False,
    )
    decision_name = Column(Text, nullable=True)
    approve_percentage = Column(Numeric(5, 2), nullable=True)

    contract = relationship("CorporateContract", back_populates="decisions")


class NotificationChannel(Base):
    """Notification Channel model."""

    __tablename__ = "notification_channels"
    __table_args__ = {"schema": "wathq"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(
        Integer,
        ForeignKey("wathq.corporate_contracts.id", ondelete="CASCADE"),
        nullable=False,
    )
    channel_name = Column(String(100), nullable=True)

    contract = relationship("CorporateContract", back_populates="notification_channels")
