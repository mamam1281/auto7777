from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, unique=True)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    text = Column(String, nullable=False)
    order = Column(Integer, default=0)
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("QuizAnswer", back_populates="question", cascade="all, delete-orphan")

class QuizAnswer(Base):
    __tablename__ = "quiz_answers"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    text = Column(String, nullable=False)
    score = Column(Integer, default=0) # This score will contribute to the risk profile
    question = relationship("QuizQuestion", back_populates="answers")

class UserQuizAttempt(Base):
    __tablename__ = "user_quiz_attempts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    final_score = Column(Integer)
    risk_profile_result = Column(String) # e.g., "High-Risk", "Calculated-Risk"
    answers_json = Column(JSON) # Store the actual answers given by the user

    user = relationship("User")
    quiz = relationship("Quiz")
