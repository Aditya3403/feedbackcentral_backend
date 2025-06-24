# feedback.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

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

    class Config:
        orm_mode = True