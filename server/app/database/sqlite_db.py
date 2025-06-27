from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Enum,ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import StaticPool
from datetime import datetime
import enum
from enum import Enum as PyEnum

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={
        "check_same_thread": False,
        "timeout": 30 
    },
    poolclass=StaticPool
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Sentiment(enum.Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"

class FeedbackStatus(str, PyEnum):
    PENDING = "PENDING"
    ACKNOWLEDGED = "ACKNOWLEDGED"

class Manager(Base):
    __tablename__ = "managers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    full_name = Column(String)
    company = Column(String)
    department = Column(String)

    employees = relationship("Employee", back_populates="manager")

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=True)
    password_set = Column(Boolean, default=False)
    invitation_token = Column(String, unique=True, nullable=True)
    token_expires = Column(DateTime, nullable=True)
    full_name = Column(String)
    company = Column(String)
    department = Column(String)
    
    manager_id = Column(Integer, ForeignKey('managers.id'), nullable=True)
    
    manager = relationship("Manager", back_populates="employees")

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    strengths = Column(Text)
    areas_to_improve = Column(Text)
    overall_sentiment = Column(Enum(Sentiment))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    manager_name = Column(String)
    manager_email = Column(String)
    employee_name = Column(String)
    employee_email = Column(String)
    
    manager_id = Column(Integer, ForeignKey('managers.id'), nullable=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    
    status = Column(Enum(FeedbackStatus), default=FeedbackStatus.PENDING, nullable=False)
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()