"""
Employee models for Wathq schema.
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Employee(Base):
    """
    Employees master table.
    Links to wathq_call_logs via log_id for data traceability.
    Same employee data can be repeated but each record is linked to a unique call log.
    """

    __tablename__ = "employees"
    __table_args__ = {"schema": "wathq"}

    employee_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    log_id = Column(
        UUID(as_uuid=True), ForeignKey("wathq_call_logs.id"), nullable=True, index=True
    )
    fetched_at = Column(DateTime(timezone=True), nullable=True)
    name = Column(String(255), nullable=True, index=True)
    nationality = Column(String(100), nullable=True, index=True)
    working_months = Column(Integer, nullable=True)

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
    employment_details = relationship(
        "EmploymentDetail", back_populates="employee", cascade="all, delete-orphan"
    )


class EmploymentDetail(Base):
    """Employment Details table"""

    __tablename__ = "employment_details"
    __table_args__ = {"schema": "wathq"}

    employment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(
        Integer,
        ForeignKey("wathq.employees.employee_id", ondelete="CASCADE"),
        nullable=False,
    )
    employer = Column(String(255), nullable=True)
    status = Column(String(50), nullable=True)
    basic_wage = Column(Numeric(12, 2), nullable=True)
    housing_allowance = Column(Numeric(12, 2), nullable=True)
    other_allowance = Column(Numeric(12, 2), nullable=True)
    full_wage = Column(Numeric(12, 2), nullable=True)

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
    employee = relationship("Employee", back_populates="employment_details")
