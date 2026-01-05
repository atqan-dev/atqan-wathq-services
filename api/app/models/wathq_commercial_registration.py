"""
Commercial Registration model for Wathq schema.
"""

from sqlalchemy import Boolean, Column, Date, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CommercialRegistration(Base):
    """
    Commercial Registration model representing CR data from Wathq.
    """

    __tablename__ = "commercial_registrations"
    __table_args__ = {'schema': 'wathq'}

    cr_number = Column(String(20), primary_key=True)
    cr_national_number = Column(String(20), nullable=True)
    version_no = Column(Integer, nullable=True)
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

    capital_info = relationship("CapitalInfo", back_populates="commercial_registration", uselist=False)
    entity_characters = relationship("CREntityCharacter", back_populates="commercial_registration")
    activities = relationship("CRActivity", back_populates="commercial_registration")
    stocks = relationship("CRStock", back_populates="commercial_registration")
    estores = relationship("CREstore", back_populates="commercial_registration")
    parties = relationship("CRParty", back_populates="commercial_registration")
    managers = relationship("CRManager", back_populates="commercial_registration")
    liquidators = relationship("CRLiquidator", back_populates="commercial_registration")
