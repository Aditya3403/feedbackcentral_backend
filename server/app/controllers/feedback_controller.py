# feedback_controller.py
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schema.user import Feedback, Manager, Employee
from ..schema.feedback import FeedbackCreate, FeedbackResponse
from datetime import datetime

async def create_feedback(feedback_data: FeedbackCreate, db: Session):
    # Check if manager exists
    db_manager = db.query(Manager).filter(Manager.id == feedback_data.manager_id).first()
    if not db_manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    # Check if employee exists
    db_employee = db.query(Employee).filter(Employee.id == feedback_data.employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if manager is assigned to this employee
    if db_employee.manager_id != db_manager.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager is not assigned to this employee"
        )
    
    db_feedback = Feedback(
        strengths=feedback_data.strengths,
        areas_to_improve=feedback_data.areas_to_improve,
        overall_sentiment=feedback_data.overall_sentiment,
        manager_id=feedback_data.manager_id,
        employee_id=feedback_data.employee_id,
        created_at=datetime.utcnow()
    )
    
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    return FeedbackResponse(
        id=db_feedback.id,
        strengths=db_feedback.strengths,
        areas_to_improve=db_feedback.areas_to_improve,
        overall_sentiment=db_feedback.overall_sentiment,
        employee_id=db_feedback.employee_id,
        manager_id=db_feedback.manager_id,
        manager_name=db_manager.full_name,
        manager_email=db_manager.email,
        employee_name=db_employee.full_name,
        employee_email=db_employee.email,
        created_at=db_feedback.created_at
    )

async def get_feedback(feedback_id: int, db: Session = Depends(get_db)):
    db_feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not db_feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    return FeedbackResponse(
        id=db_feedback.id,
        strengths=db_feedback.strengths,
        areas_to_improve=db_feedback.areas_to_improve,
        overall_sentiment=db_feedback.overall_sentiment,
        employee_id=db_feedback.employee_id,
        manager_id=db_feedback.manager_id,
        manager_name=db_feedback.manager.full_name,
        manager_email=db_feedback.manager.email,
        employee_name=db_feedback.employee.full_name,
        employee_email=db_feedback.employee.email,
        created_at=db_feedback.created_at
    )

async def get_feedbacks_by_employee(employee_id: int, db: Session):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    feedbacks = db.query(Feedback).filter(Feedback.employee_id == employee_id).all()
    
    return [
        FeedbackResponse(
            id=fb.id,
            strengths=fb.strengths,
            areas_to_improve=fb.areas_to_improve,
            overall_sentiment=fb.overall_sentiment,
            employee_id=fb.employee_id,
            manager_id=fb.manager_id,
            manager_name=fb.manager.full_name,
            manager_email=fb.manager.email,
            employee_name=db_employee.full_name,
            employee_email=db_employee.email,
            created_at=fb.created_at
        )
        for fb in feedbacks
    ]

async def get_feedbacks_by_manager(manager_id: int, db: Session):
    db_manager = db.query(Manager).filter(Manager.id == manager_id).first()
    if not db_manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    feedbacks = db.query(Feedback).filter(Feedback.manager_id == manager_id).all()
    
    return [
        FeedbackResponse(
            id=fb.id,
            strengths=fb.strengths,
            areas_to_improve=fb.areas_to_improve,
            overall_sentiment=fb.overall_sentiment,
            employee_id=fb.employee_id,
            manager_id=fb.manager_id,
            manager_name=db_manager.full_name,
            manager_email=db_manager.email,
            employee_name=fb.employee.full_name,
            employee_email=fb.employee.email,
            created_at=fb.created_at
        )
        for fb in feedbacks
    ]