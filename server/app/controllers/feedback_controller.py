from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..database import get_db
from ..database.sqlite_db import Feedback, Manager, Employee, FeedbackStatus
from ..schema.feedback import FeedbackCreate, FeedbackResponse, FeedbackUpdate

async def create_feedback(feedback_data: FeedbackCreate, db: Session = Depends(get_db)):
    try:
        # Validate manager exists
        db_manager = db.query(Manager).filter(
            Manager.id == feedback_data.manager_id
        ).first()
        if not db_manager:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manager not found"
            )

        # Validate employee exists
        db_employee = db.query(Employee).filter(
            Employee.id == feedback_data.employee_id
        ).first()
        if not db_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )

        # Validate manager-employee relationship
        if db_employee.manager_id != db_manager.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager is not assigned to this employee"
            )

        # Create feedback record
        db_feedback = Feedback(
            strengths=feedback_data.strengths,
            areas_to_improve=feedback_data.areas_to_improve,
            overall_sentiment=feedback_data.overall_sentiment,
            manager_id=feedback_data.manager_id,
            employee_id=feedback_data.employee_id,
            manager_name=db_manager.full_name,
            manager_email=db_manager.email,
            employee_name=db_employee.full_name,
            employee_email=db_employee.email,
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
            manager_id=db_feedback.manager_id,
            employee_id=db_feedback.employee_id,
            manager_name=db_feedback.manager_name,
            manager_email=db_feedback.manager_email,
            employee_name=db_feedback.employee_name,
            employee_email=db_feedback.employee_email,
            created_at=db_feedback.created_at
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating feedback: {str(e)}"
        )
    
async def get_employee_feedbacks(employee_id: int, db: Session):
    feedbacks = db.query(Feedback).filter(
        Feedback.employee_id == employee_id
    ).order_by(Feedback.created_at.desc()).all()

    if not feedbacks:
        return []

    return feedbacks

async def acknowledge_feedback(
    feedback_id: str,
    employee_id: int,
    db: Session = Depends(get_db)
):

    try:
        # Find the feedback
        db_feedback = db.query(Feedback).filter(
            Feedback.id == feedback_id,
            Feedback.employee_id == employee_id
        ).first()

        if not db_feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found or not assigned to this employee"
            )

        # Update the status
        db_feedback.status = FeedbackStatus.ACKNOWLEDGED
        db_feedback.acknowledged_at = datetime.utcnow()
        db.commit()
        db.refresh(db_feedback)

        return {
            "success": True,
            "message": "Feedback acknowledged successfully",
            "feedback_id": db_feedback.id,
            "status": db_feedback.status
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error acknowledging feedback: {str(e)}"
        )
        
async def update_feedback(
    feedback_id: str,
    feedback_data: FeedbackUpdate,
    db: Session = Depends(get_db)
):
    try:
        try:
            feedback_id_int = int(feedback_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feedback ID must be an integer"
            )

        db_feedback = db.query(Feedback).filter(
            Feedback.id == feedback_id_int
        ).first()
        
        if not db_feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )

        if feedback_data.strengths is not None:
            db_feedback.strengths = feedback_data.strengths
        if feedback_data.areas_to_improve is not None:
            db_feedback.areas_to_improve = feedback_data.areas_to_improve
        if feedback_data.overall_sentiment is not None:
            db_feedback.overall_sentiment = feedback_data.overall_sentiment.value

        db.commit()
        db.refresh(db_feedback)

        response_data = {
            "id": db_feedback.id,
            "strengths": db_feedback.strengths,
            "areas_to_improve": db_feedback.areas_to_improve,
            "overall_sentiment": db_feedback.overall_sentiment.value,
            "manager_id": db_feedback.manager_id,
            "employee_id": db_feedback.employee_id,
            "manager_name": db_feedback.manager_name,
            "manager_email": db_feedback.manager_email,
            "employee_name": db_feedback.employee_name,
            "employee_email": db_feedback.employee_email,
            "created_at": db_feedback.created_at,
            "status": db_feedback.status.value if db_feedback.status else None
        }

        return {
            "success": True,
            "message": "Feedback updated successfully",
            "feedback": FeedbackResponse(**response_data)
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating feedback: {str(e)}"
        )