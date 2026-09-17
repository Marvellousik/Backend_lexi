"""
Learning Signal Ingestion Service for Lexi.
Processes atomic student interactions (quizzes, flashcard flips, diagnostics) and computes updated mastery scores.
"""
import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from academic_service.models.orm import (
    Course,
    StudentKnowledgeState,
    LearningSignal,
    LearningGap,
)
from academic_service.models.schema import LearningSignalCreate, KnowledgeStateDTO

logger = logging.getLogger(__name__)


class SignalIngestionService:
    """Ingests learning events and updates the student's living knowledge state."""

    @staticmethod
    def record_signal(db: Session, user_id: str, signal_data: LearningSignalCreate) -> KnowledgeStateDTO:
        """
        Record a learning event and compute the new mastery score using Exponential Moving Average.
        """
        course = (
            db.query(Course)
            .filter((Course.id == signal_data.course_id) | (Course.code.ilike(signal_data.course_id.strip())))
            .first()
        )
        if not course:
            raise ValueError(f"Course '{signal_data.course_id}' not found.")

        # 1. Record Atomic Learning Signal
        sig = LearningSignal(
            id=str(uuid.uuid4()),
            user_id=user_id,
            course_id=course.id,
            topic=signal_data.topic,
            subtopic=signal_data.subtopic,
            signal_type=signal_data.signal_type,
            score=signal_data.score,
            max_score=signal_data.max_score,
            raw_details=signal_data.details,
        )
        db.add(sig)

        # 2. Find or create StudentKnowledgeState
        state = (
            db.query(StudentKnowledgeState)
            .filter(
                StudentKnowledgeState.user_id == user_id,
                StudentKnowledgeState.course_id == course.id,
                StudentKnowledgeState.topic == signal_data.topic,
                StudentKnowledgeState.subtopic == signal_data.subtopic,
            )
            .first()
        )

        if not state:
            state = StudentKnowledgeState(
                id=str(uuid.uuid4()),
                user_id=user_id,
                course_id=course.id,
                topic=signal_data.topic,
                subtopic=signal_data.subtopic,
                mastery_score=0,
                status="not_started",
                total_attempts=0,
                correct_attempts=0,
            )
            db.add(state)

        # 3. Calculate Performance Percentage for this interaction
        attempt_pct = int((signal_data.score / max(1, signal_data.max_score)) * 100)
        is_success = attempt_pct >= 70

        state.total_attempts += 1
        if is_success:
            state.correct_attempts += 1

        # 4. Exponential Moving Average update: 60% historical + 40% current signal
        if state.total_attempts == 1:
            state.mastery_score = attempt_pct
        else:
            state.mastery_score = int((0.60 * state.mastery_score) + (0.40 * attempt_pct))

        # Clamp between 0 and 100
        state.mastery_score = max(0, min(100, state.mastery_score))
        state.last_evaluated_at = datetime.now(timezone.utc)

        # Extract last error summary if present
        if signal_data.details and "error_summary" in signal_data.details:
            state.last_error_summary = signal_data.details["error_summary"]
        elif not is_success:
            state.last_error_summary = f"Missed question on {signal_data.subtopic} (scored {signal_data.score}/{signal_data.max_score})."

        # 5. Status Transition
        if state.mastery_score >= 80:
            state.status = "mastered"
        elif state.mastery_score >= 50:
            state.status = "learning"
        elif state.total_attempts >= 2:
            state.status = "struggling"
        else:
            state.status = "learning"

        # 6. Learning Gap Registration / Resolution
        if state.status == "struggling":
            existing_gap = (
                db.query(LearningGap)
                .filter(
                    LearningGap.user_id == user_id,
                    LearningGap.course_id == course.id,
                    LearningGap.topic == signal_data.topic,
                    LearningGap.subtopic == signal_data.subtopic,
                    LearningGap.status == "active",
                )
                .first()
            )
            if not existing_gap:
                gap = LearningGap(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    course_id=course.id,
                    topic=signal_data.topic,
                    subtopic=signal_data.subtopic,
                    gap_description=state.last_error_summary or f"Struggling with {signal_data.subtopic} fundamentals.",
                    severity="high" if state.mastery_score < 35 else "medium",
                    status="active",
                )
                db.add(gap)
        elif state.status in ("mastered", "learning"):
            # Mark any active gap as resolved
            active_gaps = (
                db.query(LearningGap)
                .filter(
                    LearningGap.user_id == user_id,
                    LearningGap.course_id == course.id,
                    LearningGap.topic == signal_data.topic,
                    LearningGap.subtopic == signal_data.subtopic,
                    LearningGap.status == "active",
                )
                .all()
            )
            for g in active_gaps:
                g.status = "resolved"
                g.resolved_at = datetime.now(timezone.utc)

        db.commit()
        logger.info(
            f"🎯 Signal ingested for {user_id} on {course.code} [{signal_data.subtopic}]: "
            f"Score: {state.mastery_score}% ({state.status})"
        )

        return KnowledgeStateDTO(
            topic=state.topic,
            subtopic=state.subtopic,
            mastery_score=state.mastery_score,
            status=state.status,
            total_attempts=state.total_attempts,
            correct_attempts=state.correct_attempts,
            last_evaluated_at=state.last_evaluated_at.isoformat() if state.last_evaluated_at else None,
            last_error_summary=state.last_error_summary,
        )
