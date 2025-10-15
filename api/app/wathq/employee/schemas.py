"""
Pydantic schemas for Wathq Employee Information API.
"""

from typing import List, Optional
from pydantic import BaseModel


class WageDetails(BaseModel):
    basicWage: Optional[float] = None
    housingAllowance: Optional[float] = None
    otherAllowance: Optional[float] = None
    fullWage: Optional[float] = None


class EmploymentInfo(BaseModel):
    employer: Optional[str] = None
    status: Optional[str] = None
    wageDetails: Optional[WageDetails] = None


class EmployeeInfoResponse(BaseModel):
    name: str
    nationality: str
    workingMonths: str
    employmentInfo: List[EmploymentInfo]