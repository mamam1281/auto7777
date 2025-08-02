from sqlalchemy.orm import Session
from typing import List, Dict, Any

from .. import models

class QuizService:
    def __init__(self, db: Session):
        self.db = db

    def get_quiz(self, quiz_id: int) -> models.Quiz:
        """
        Retrieves a single quiz with its questions and answers.
        """
        quiz = self.db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
        if not quiz:
            raise ValueError("Quiz not found")
        return quiz

    def submit_answers(self, user_id: int, quiz_id: int, answers: Dict[int, int]) -> models.UserQuizAttempt:
        """
        Submits a user's answers for a quiz, calculates the score, and updates their profile.
        - answers: A dictionary of {question_id: answer_id}
        """
        total_score = 0
        for question_id, answer_id in answers.items():
            answer = self.db.query(models.QuizAnswer).filter_by(id=answer_id, question_id=question_id).first()
            if answer:
                total_score += answer.score

        # Determine risk profile based on score
        if total_score > 10:
            risk_profile = "High-Risk"
        elif total_score > 5:
            risk_profile = "Calculated-Risk"
        else:
            risk_profile = "Low-Risk"

        # Save the attempt
        attempt = models.UserQuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            final_score=total_score,
            risk_profile_result=risk_profile,
            answers_json=answers
        )
        self.db.add(attempt)

        # Update the user's segment profile
        user_segment = self.db.query(models.UserSegment).filter_by(user_id=user_id).first()
        if user_segment:
            user_segment.risk_profile = risk_profile
        else:
            # If no segment exists, create one
            user_segment = models.UserSegment(user_id=user_id, risk_profile=risk_profile, rfm_group="New")
            self.db.add(user_segment)

        self.db.commit()
        self.db.refresh(attempt)

        return attempt
