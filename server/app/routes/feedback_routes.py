from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.sqlite_db import get_db
from app.schema.feedback import FeedbackCreate, FeedbackResponse, AcknowledgeFeedbackRequest, FeedbackUpdate
from ..database.sqlite_db import Feedback, Manager
from typing import Optional
from app.controllers.feedback_controller import (
    create_feedback,
    get_employee_feedbacks,
    acknowledge_feedback,
    update_feedback
)
router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/submit-feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback_data: FeedbackCreate, db: Session = Depends(get_db)):
    return await create_feedback(feedback_data, db)

@router.get("/received-feedback/{employee_id}", response_model=list[FeedbackResponse])
async def get_complete_employee_feedback(
    employee_id: int,
    db: Session = Depends(get_db)
):
    
    try:
        feedbacks = await get_employee_feedbacks(employee_id, db)
        return feedbacks
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching feedback: {str(e)}"
        )

@router.get("/manager-feedbacks/{manager_id}", response_model=list[FeedbackResponse])
async def get_manager_feedbacks(
    manager_id: int, 
    employee_id: Optional[int] = None, 
    db: Session = Depends(get_db)
):
    """
    Get all feedbacks given by a specific manager
    """
    db_manager = db.query(Manager).filter(
        Manager.id == manager_id
    ).first()
    
    if not db_manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found"
        )

    query = db.query(Feedback).filter(
        Feedback.manager_id == manager_id
    )

    if employee_id:
        query = query.filter(Feedback.employee_id == employee_id)

    feedbacks = query.order_by(Feedback.created_at.desc()).all()

    return [
        FeedbackResponse(
            id=fb.id,
            strengths=fb.strengths,
            areas_to_improve=fb.areas_to_improve,
            overall_sentiment=fb.overall_sentiment,
            manager_id=fb.manager_id,
            employee_id=fb.employee_id,
            manager_name=fb.manager_name,
            manager_email=fb.manager_email,
            employee_name=fb.employee_name,
            employee_email=fb.employee_email,
            created_at=fb.created_at,
            status=fb.status,
        )
        for fb in feedbacks
    ]
    
@router.post("/acknowledge-feedback")
async def acknowledge_feedback_route(
    request: AcknowledgeFeedbackRequest,
    db: Session = Depends(get_db)
):
    return await acknowledge_feedback(request.feedback_id, request.employee_id, db)

@router.put("/update-feedback/{feedback_id}")
async def update_feedback_route(
    feedback_id: str,
    feedback_data: FeedbackUpdate,
    db: Session = Depends(get_db)
):
    return await update_feedback(feedback_id, feedback_data, db)