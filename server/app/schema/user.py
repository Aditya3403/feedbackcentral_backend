from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional, Union
from datetime import datetime

class ManagerBase(BaseModel):
    email: EmailStr
    full_name: str

class ManagerCreate(ManagerBase):
    password: str = Field(..., min_length=8)
    company: str
    department: str

class ManagerResponse(ManagerBase):
    id: int
    company: str
    department: str
    employees: List[Dict[str, str]] = []  # Format: [{"employee_name": str, "employee_email": str}]
    given_feedbacks: List[Dict[str, Union[str, datetime]]] = Field(default_factory=list)  
    # Format: [{
    #   "employee_name": str,
    #   "employee_email": str,
    #   "strengths": str,
    #   "areas_to_improve": str,
    #   "overall_sentiment": str,
    #   "created_at": datetime
    # }]  # Changed to default_factory

class EmployeeBase(BaseModel):
    email: EmailStr
    full_name: str

class EmployeeCreate(EmployeeBase):
    password: str = Field(..., min_length=8)
    company: str
    department: str

class EmployeeResponse(EmployeeBase):
    id: int
    company: str
    department: str
    managers: List[Dict[str, str]] = Field(default_factory=list)  # Format: [{"manager_name": str, "manager_email": str}]
    received_feedbacks: List[Dict[str, Union[str, datetime]]] = Field(default_factory=list)
    # Format: [{
    #   "manager_name": str,
    #   "manager_email": str,
    #   "strengths": str,
    #   "areas_to_improve": str,
    #   "overall_sentiment": str,
    #   "created_at": datetime
    # }]
class ManagerShort(BaseModel):
    id: int
    email: EmailStr
    full_name: str

class EmployeeShort(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    
class AddEmployeeRequest(BaseModel):
    employee_name: str
    employee_email: EmailStr
    manager_id: int

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_type: str
    user: ManagerResponse | EmployeeResponse
    
# Add these new schemas
class InvitationResponse(BaseModel):
    success: bool
    message: str
    employee: Dict[str, str]
    invitation_link: str

class SetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    

ManagerResponse.update_forward_refs()
EmployeeResponse.update_forward_refs()