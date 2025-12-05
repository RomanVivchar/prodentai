from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=True)
    username = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    risk_assessments = relationship("RiskAssessment", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")
    psychology_sessions = relationship("PsychologySession", back_populates="user")

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    risk_data = Column(Text, nullable=True)  # JSON string (legacy)
    assessment_data = Column(Text, nullable=True)  # JSON string
    risk_scores = Column(Text, nullable=True)  # JSON string
    recommendations = Column(Text, nullable=True)  # JSON string or array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="risk_assessments")

class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reminder_type = Column(String, nullable=True)
    time = Column(String)  # HH:MM format
    date = Column(String, nullable=True)  # YYYY-MM-DD format (for dental_visit)
    message = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True)  # Legacy field
    is_active = Column(Boolean, default=True)  # New field
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="reminders")

class PsychologySession(Base):
    __tablename__ = "psychology_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    messages = Column(Text, nullable=True)  # JSON string (legacy)
    session_type = Column(String, nullable=True, default="general")
    user_message = Column(Text, nullable=True)
    ai_response = Column(Text, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="psychology_sessions")


class Fact(Base):
    __tablename__ = "facts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NutritionLog(Base):
    __tablename__ = "nutrition_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_description = Column(Text, nullable=True)
    calories = Column(Float, nullable=True)
    sugar_content = Column(Float, nullable=True)
    acidity_level = Column(Float, nullable=True)
    health_score = Column(Float, nullable=True)
    recommendations = Column(Text, nullable=True)  # JSON string or array
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BracesFAQ(Base):
    __tablename__ = "braces_faq"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    keywords = Column(Text, nullable=True)  # JSON array
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

