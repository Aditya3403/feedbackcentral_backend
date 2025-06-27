from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

class AcknowledgeFeedbackRequest(BaseModel):
    feedback_id: str
    employee_id: int
    

class Sentiment(str, Enum):
    POSITIVE = "POSITIVE" 
    NEUTRAL = "NEUTRAL"    
    NEGATIVE = "NEGATIVE"  

class FeedbackBase(BaseModel):
    strengths: str
    areas_to_improve: str
    overall_sentiment: Sentiment
    employee_id: int
    manager_id: int

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackResponse(FeedbackBase):
    id: int
    manager_name: str
    manager_email: EmailStr
    employee_name: str
    employee_email: EmailStr
    created_at: datetime
    status: Optional[str] = None

    class Config:
        from_attributes = True 

class FeedbackUpdate(BaseModel):
    strengths: Optional[str] = None
    areas_to_improve: Optional[str] = None
    overall_sentiment: Optional[Sentiment] = None
    
    