"""
Employee schemas for Wathq.
"""

from typing import List, Optional, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


# EmploymentDetail Schemas
class EmploymentDetailBase(BaseModel):
    employer: Optional[str] = None
    status: Optional[str] = None
    basic_wage: Optional[Decimal] = None
    housing_allowance: Optional[Decimal] = None
    other_allowance: Optional[Decimal] = None
    full_wage: Optional[Decimal] = None


class EmploymentDetailCreate(EmploymentDetailBase):
    employee_id: int


class EmploymentDetailUpdate(EmploymentDetailBase):
    pass


class EmploymentDetail(EmploymentDetailBase):
    employment_id: int
    employee_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# Employee Schemas
class EmployeeBase(BaseModel):
    name: Optional[str] = None
    nationality: Optional[str] = None
    working_months: Optional[int] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass


class Employee(EmployeeBase):
    employee_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    request_body: Optional[Any] = None
    
    # Nested relationships
    employment_details: List[EmploymentDetail] = []

    model_config = ConfigDict(from_attributes=True)
