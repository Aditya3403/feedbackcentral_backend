from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..database.sqlite_db import Manager, Employee, Feedback
from ..schema.user import (
    ManagerResponse,
    EmployeeResponse,
    ManagerCreate,
    EmployeeCreate,
    LoginResponse,
    ManagerShort,
    EmployeeShort,
    AddEmployeeRequest,
    InvitationResponse, 
    SetPasswordRequest
)
from ..schema.feedback import FeedbackResponse
import hashlib
import secrets
from datetime import datetime, timedelta
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ..config import settings
from app.logger import configure_logging
import logging
import os

configure_logging()
logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    return secrets.token_urlsafe(32)

def send_invitation_email(email: str, employee_name: str, invitation_link: str):
    """
    Send invitation email using SMTP
    """
    try:
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Invitation to join FeedbackCentral"
        msg['From'] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
        msg['To'] = email
        
        # Create the HTML version of your message
        html = f"""\
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to FeedbackCentral</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to FeedbackCentral!</h1>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e9ecef;">
                <h2 style="color: #495057; margin-top: 0;">Hi {employee_name},</h2>
                
                <p style="font-size: 16px; margin-bottom: 25px;">
                    You've been invited to join FeedbackCentral as an employee. We're excited to have you on board!
                </p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; margin: 25px 0;">
                    <p style="margin: 0; font-size: 16px;">
                        To get started, please set your password by clicking the button below:
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{invitation_link}" 
                       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; 
                              padding: 15px 30px; 
                              text-decoration: none; 
                              border-radius: 25px; 
                              font-weight: bold; 
                              font-size: 16px; 
                              display: inline-block; 
                              box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
                        Set Your Password
                    </a>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; color: #856404; font-size: 14px;">
                        ⏰ <strong>Important:</strong> This invitation link will expire in 48 hours for security reasons.
                    </p>
                </div>
                
                <p style="font-size: 14px; color: #6c757d; margin-top: 30px;">
                    If you're having trouble clicking the button, copy and paste this link into your browser:<br>
                    <a href="{invitation_link}" style="color: #667eea; word-break: break-all;">{invitation_link}</a>
                </p>
                
                <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
                
                <p style="font-size: 14px; color: #6c757d; margin: 0;">
                    Best regards,<br>
                    <strong>The FeedbackCentral Team</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        # Create the plain-text version of your message
        text = f"""\
        Hi {employee_name},
        
        You've been invited to join FeedbackCentral as an employee.
        
        Please set your password by visiting this link:
        {invitation_link}
        
        This link will expire in 48 hours.
        
        Best regards,
        The FeedbackCentral Team
        """
        
        # Record the MIME types of both parts - text/plain and text/html
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        
        # Attach parts into message container
        msg.attach(part1)
        msg.attach(part2)
        
        # Create SMTP connection
        if settings.SMTP_USE_SSL:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        
        if settings.SMTP_USE_TLS and not settings.SMTP_USE_SSL:
            server.starttls()
        
        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Invitation email sent successfully to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email via SMTP: {str(e)}")
        return False
    
async def create_manager(manager_data: ManagerCreate, db: Session):
    # Check if email already exists
    if (db.query(Manager).filter(Manager.email == manager_data.email).first() or
        db.query(Employee).filter(Employee.email == manager_data.email).first()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(manager_data.password)
    
    # Create manager without initializing relationships
    db_manager = Manager(
        email=manager_data.email,
        password=hashed_password,
        full_name=manager_data.full_name,
        company=manager_data.company,
        department=manager_data.department
    )
    
    db.add(db_manager)
    db.commit()
    db.refresh(db_manager)
    
    return ManagerResponse(
        id=db_manager.id,
        email=db_manager.email,
        full_name=db_manager.full_name,
        company=db_manager.company,
        department=db_manager.department,
        employees=[],  # Will be populated when employees are assigned
        given_feedbacks=[]  # Will be populated when feedback is given
    )

async def create_employee(employee_data: EmployeeCreate, db: Session):
    # Check if email already exists
    if (db.query(Employee).filter(Employee.email == employee_data.email).first() or
        db.query(Manager).filter(Manager.email == employee_data.email).first()):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(employee_data.password)
    
    # Create employee without initializing relationships
    db_employee = Employee(
        email=employee_data.email,
        password=hashed_password,
        full_name=employee_data.full_name,
        company=employee_data.company,
        department=employee_data.department
    )
    
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    return EmployeeResponse(
        id=db_employee.id,
        email=db_employee.email,
        full_name=db_employee.full_name,
        company=db_employee.company,
        department=db_employee.department,
        managers=[],  # Will be populated when assigned to manager
        received_feedbacks=[]  # Will be populated when feedback is received
    )

async def get_manager(manager_id: int, db: Session = Depends(get_db)):
    db_manager = db.query(Manager).filter(Manager.id == manager_id).first()
    if not db_manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    # Get employees (just name and email)
    employees = [
        {"employee_name": emp.full_name, "employee_email": emp.email}
        for emp in db_manager.employees
    ]
    
    # Get given feedbacks with all required fields
    given_feedbacks = [
        {
            "employee_name": fb.employee_name,
            "employee_email": fb.employee_email,
            "strengths": fb.strengths,
            "areas_to_improve": fb.areas_to_improve,
            "overall_sentiment": fb.overall_sentiment.value,
            "created_at": fb.created_at.isoformat()
        }
        for fb in db.query(Feedback).filter(Feedback.manager_id == manager_id).all()
    ]
    
    return ManagerResponse(
        id=db_manager.id,
        email=db_manager.email,
        full_name=db_manager.full_name,
        company=db_manager.company,
        department=db_manager.department,
        employees=employees,
        given_feedbacks=given_feedbacks
    )

async def get_employee(employee_id: int, db: Session):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Get manager info (if assigned)
    managers = []
    if db_employee.manager:
        managers.append({
            "manager_name": db_employee.manager.full_name,
            "manager_email": db_employee.manager.email
        })
    
    # Get received feedbacks with all required fields
    received_feedbacks = [
        {
            "manager_name": fb.manager_name,
            "manager_email": fb.manager_email,
            "strengths": fb.strengths,
            "areas_to_improve": fb.areas_to_improve,
            "overall_sentiment": fb.overall_sentiment.value,
            "created_at": fb.created_at.isoformat()
        }
        for fb in db.query(Feedback).filter(Feedback.employee_id == employee_id).all()
    ]
    
    return EmployeeResponse(
        id=db_employee.id,
        email=db_employee.email,
        full_name=db_employee.full_name,
        company=db_employee.company,
        department=db_employee.department,
        managers=managers,
        received_feedbacks=received_feedbacks
    )
    
def generate_invitation_token() -> str:
    return str(uuid.uuid4())

def get_invitation_link(token: str) -> str:
    # In production, use your actual domain
    base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    return f"{base_url}/set-password?token={token}"

async def add_employee_to_manager(employee_data: AddEmployeeRequest, db: Session):
    """
    Adds an employee to a manager and sends an invitation email with password setup link
    """
    try:
        # Check if manager exists
        db_manager = db.query(Manager).filter(Manager.id == employee_data.manager_id).first()
        if not db_manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        
        # Check if email exists
        if db.query(Employee).filter(Employee.email == employee_data.employee_email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Generate invitation token and expiration
        token = generate_invitation_token()
        expires = datetime.utcnow() + timedelta(days=2)
        
        # Create employee record
        db_employee = Employee(
            email=employee_data.employee_email,
            full_name=employee_data.employee_name,
            company=db_manager.company,
            department=db_manager.department,
            manager_id=db_manager.id,
            invitation_token=token,
            token_expires=expires,
            password_set=False
        )
        
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        
        # Generate invitation link
        invitation_link = get_invitation_link(token)
        
        # Send invitation email via SMTP
        email_sent = send_invitation_email(
            email=employee_data.employee_email,
            employee_name=employee_data.employee_name,
            invitation_link=invitation_link
        )
        
        if not email_sent:
            logger.warning(f"Failed to send invitation email to {employee_data.employee_email}")
        
        return {
            "success": True,
            "message": "Employee added successfully. Invitation email sent." if email_sent else "Employee added successfully. Email sending failed - please check logs.",
            "employee": {
                "id": str(db_employee.id),
                "name": db_employee.full_name,
                "email": db_employee.email
            },
            "invitation_link": invitation_link  # For debugging purposes
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding employee: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to add employee. Please try again."
        )

# Add these new functions
async def validate_invitation_token(token: str, db: Session):
    db_employee = db.query(Employee).filter(Employee.invitation_token == token).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Invalid invitation token")
    
    if db_employee.token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invitation link has expired")
    
    if db_employee.password_set:
        raise HTTPException(status_code=400, detail="Password already set")
    
    return db_employee

async def set_employee_password(password_data: SetPasswordRequest, db: Session):
    # Validate passwords match
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # Validate token
    db_employee = await validate_invitation_token(password_data.token, db)
    
    # Set password
    db_employee.password = hash_password(password_data.new_password)
    db_employee.password_set = True
    db_employee.invitation_token = None  # Invalidate token after use
    db_employee.token_expires = None
    
    db.commit()
    db.refresh(db_employee)
    
    return {
        "success": True,
        "message": "Password set successfully. You can now login.",
        "email": db_employee.email
    }
    
async def get_employees(manager_id: int, db: Session):
    """
    Fetch all employees under a specific manager where password_set is True
    """
    try:
        # Check if manager exists
        db_manager = db.query(Manager).filter(Manager.id == manager_id).first()
        if not db_manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        
        # Get employees with password_set=True
        employees = db.query(Employee).filter(
            Employee.manager_id == manager_id,
            Employee.password_set == True
        ).all()
        
        # Count feedback for each employee
        employees_with_feedback = []
        for emp in employees:
            feedback_count = db.query(Feedback).filter(
                Feedback.manager_id == manager_id,
                Feedback.employee_id == emp.id
            ).count()
            
            employees_with_feedback.append({
                "id": emp.id,
                "full_name": emp.full_name,
                "email": emp.email,
                "feedback_count": feedback_count
            })
        
        return {
            "success": True,
            "employees": employees_with_feedback
        }
        
    except Exception as e:
        logger.error(f"Error fetching employees for manager {manager_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch employees. Please try again."
        )
    
async def login_user(email: str, password: str, db: Session):
    db_manager = db.query(Manager).filter(Manager.email == email).first()
    if db_manager:
        user_type = "manager"
        hashed_input = hash_password(password)
        if db_manager.password != hashed_input:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        user_data = await get_manager(db_manager.id, db)
    else:
        db_employee = db.query(Employee).filter(Employee.email == email).first()
        if not db_employee:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        user_type = "employee"
        hashed_input = hash_password(password)
        if db_employee.password != hashed_input:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        user_data = await get_employee(db_employee.id, db)
    
    return LoginResponse(
        access_token=generate_token(),
        token_type="bearer",
        user_type=user_type,
        user=user_data
    )