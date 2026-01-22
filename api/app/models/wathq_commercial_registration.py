"""
Commercial Registration model for Wathq schema.
"""

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, Numeric, String, JSON, func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import Base


class CommercialRegistration(Base):
    """
    Commercial Registration model representing CR data from Wathq.
    """

    __tablename__ = "commercial_registrations"
    __table_args__ = {'schema': 'wathq'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    log_id = Column(UUID(as_uuid=True), ForeignKey('wathq_call_logs.id'), nullable=True, index=True)  # Link to the call log
    cr_number = Column(String(20), nullable=False, index=True)  # Removed unique constraint to allow historical records
    cr_national_number = Column(String(20), nullable=True)
    version_no = Column(Integer, nullable=True)
    fetched_at = Column(DateTime(timezone=True), nullable=True)  # Track when this data was fetched from Wathq
    name = Column(String(255), nullable=True)
    name_lang_id = Column(Integer, nullable=True)
    name_lang_desc = Column(String(50), nullable=True)
    cr_capital = Column(Numeric(15, 2), nullable=True)
    company_duration = Column(Integer, nullable=True)
    is_main = Column(Boolean, nullable=True)
    issue_date_gregorian = Column(Date, nullable=True)
    issue_date_hijri = Column(String(10), nullable=True)
    main_cr_national_number = Column(String(20), nullable=True)
    main_cr_number = Column(String(20), nullable=True)
    in_liquidation_process = Column(Boolean, nullable=True)
    has_ecommerce = Column(Boolean, nullable=True)
    headquarter_city_id = Column(Integer, nullable=True)
    headquarter_city_name = Column(String(100), nullable=True)
    is_license_based = Column(Boolean, nullable=True)
    license_issuer_national_number = Column(String(20), nullable=True)
    license_issuer_name = Column(String(100), nullable=True)
    partners_nationality_id = Column(Integer, nullable=True)
    partners_nationality_name = Column(String(100), nullable=True)
    
    entity_type_id = Column(Integer, nullable=True)
    entity_type_name = Column(String(100), nullable=True)
    entity_form_id = Column(Integer, nullable=True)
    entity_form_name = Column(String(100), nullable=True)
    
    status_id = Column(Integer, nullable=True)
    status_name = Column(String(50), nullable=True)
    
    confirmation_date_gregorian = Column(Date, nullable=True)
    confirmation_date_hijri = Column(String(10), nullable=True)
    reactivation_date_gregorian = Column(Date, nullable=True)
    reactivation_date_hijri = Column(String(10), nullable=True)
    suspension_date_gregorian = Column(Date, nullable=True)
    suspension_date_hijri = Column(String(10), nullable=True)
    deletion_date_gregorian = Column(Date, nullable=True)
    deletion_date_hijri = Column(String(10), nullable=True)
    
    contact_phone = Column(String(20), nullable=True)
    contact_mobile = Column(String(20), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_website = Column(String(255), nullable=True)

    fiscal_is_first = Column(Boolean, nullable=True)
    fiscal_calendar_type_id = Column(Integer, nullable=True)
    fiscal_calendar_type_name = Column(String(50), nullable=True)
    fiscal_end_month = Column(Integer, nullable=True)
    fiscal_end_day = Column(Integer, nullable=True)
    fiscal_end_year = Column(Integer, nullable=True)

    mgmt_structure_id = Column(Integer, nullable=True)
    mgmt_structure_name = Column(String(100), nullable=True)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    request_body = Column(JSON, nullable=True)

    capital_info = relationship("CapitalInfo", back_populates="commercial_registration", uselist=False)
    entity_characters = relationship("CREntityCharacter", back_populates="commercial_registration")
    activities = relationship("CRActivity", back_populates="commercial_registration")
    stocks = relationship("CRStock", back_populates="commercial_registration")
    estores = relationship("CREstore", back_populates="commercial_registration")
    parties = relationship("CRParty", back_populates="commercial_registration")
    managers = relationship("CRManager", back_populates="commercial_registration")
    liquidators = relationship("CRLiquidator", back_populates="commercial_registration")
