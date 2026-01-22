"""
CRUD operations for Employees.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.crud.base import CRUDBase
from app.models.wathq_employee import Employee
from app.schemas.wathq_employee import EmployeeCreate, EmployeeUpdate


class CRUDEmployee(CRUDBase[Employee, EmployeeCreate, EmployeeUpdate]):
    """CRUD operations for Employees"""
    
    def get_with_relations(self, db: Session, *, id: int) -> Optional[Employee]:
        """
        Get an employee by ID with all related employment details eagerly loaded.
        """
        return db.query(Employee).options(
            joinedload(Employee.employment_details)
        ).filter(Employee.employee_id == id).first()
    
    def get_by_nationality(self, db: Session, *, nationality: str) -> List[Employee]:
        """
        Get employees by nationality.
        """
        return db.query(Employee).filter(Employee.nationality == nationality).all()
    
    def get_multi_with_relations(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Employee]:
        """
        Get multiple employees with all related employment details eagerly loaded.
        """
        return db.query(Employee).options(
            joinedload(Employee.employment_details)
        ).offset(skip).limit(limit).all()


employee = CRUDEmployee(Employee)
