# Updated routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.sqlite_db import get_db
from app.controllers.user_controller import (
    create_manager,
    create_employee,
    get_manager,  # Add these
    get_employee,
    login_user,
    add_employee_to_manager,
    set_employee_password,
    get_employees
)
from app.schema.user import (
    EmployeeResponse,
    ManagerResponse,
    ManagerCreate,
    EmployeeCreate,
    LoginRequest,
    LoginResponse,
    AddEmployeeRequest,
    SetPasswordRequest
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    return await login_user(login_data.email, login_data.password, db)

@router.post("/signup/manager", response_model=ManagerResponse)
async def signup_manager(user_data: ManagerCreate, db: Session = Depends(get_db)):
    return await create_manager(user_data, db)

@router.post("/signup/employee", response_model=EmployeeResponse)
async def signup_employee(user_data: EmployeeCreate, db: Session = Depends(get_db)):
    return await create_employee(user_data, db)

@router.post("/add-employee", response_model=dict)
async def add_employee_route(employee_data: AddEmployeeRequest, db: Session = Depends(get_db)):
    return await add_employee_to_manager(employee_data, db)

@router.post("/set-password")
async def set_password(password_data: SetPasswordRequest, db: Session = Depends(get_db)):
    return await set_employee_password(password_data, db)

@router.get("/get-employees", response_model=dict)
async def get_employees_route(manager_id: int, db: Session = Depends(get_db)):
    return await get_employees(manager_id, db)

# @router.get("/users/{user_id}", response_model=UserResponse)
# async def read_user(user_id: str, db: Session = Depends(get_db)):
#     return await get_user(user_id, db)

# @router.get("/me", response_model=UserResponse)
# async def get_current_user(user_id: str, db: Session = Depends(get_db)):
#     return await get_user(user_id, db)