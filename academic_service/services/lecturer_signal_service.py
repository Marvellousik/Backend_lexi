"""
Lecturer Signal Aggregator Service for Lexi.
Aggregates individual student performance into actionable class-wide misconception insights.
"""
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from academic_service.models.orm import (
    Course,
    StudentKnowledgeState,
    StudentEnrollment,
    LecturerClassSignal,
)
from academic_service.models.schema import LecturerClassSignalDTO

logger = logging.getLogger(__name__)


class LecturerSignalService:
    """Aggregates class-wide student mastery signals into lecturer intelligence cards."""

    @staticmethod
    def get_course_class_signals(db: Session, course_id: str) -> List[LecturerClassSignalDTO]:
        """
        Aggregate class-wide student performance to identify concepts where the cohort is struggling.
        """
        course = (
            db.query(Course)
            .filter((Course.id == course_id) | (Course.code.ilike(course_id.strip())))
            .first()
        )
        if not course:
            return []

        # Count total active enrolled students in this course
        total_students = (
            db.query(StudentEnrollment)
            .filter(StudentEnrollment.course_id == course.id, StudentEnrollment.status == "active")
            .count()
        )

        if total_students == 0:
            total_students = 1  # Fallback to prevent division by zero in demo environments

        # Query all student knowledge states for this course
        states = (
            db.query(StudentKnowledgeState)
            .filter(StudentKnowledgeState.course_id == course.id)
            .all()
        )

        # Aggregate stats per subtopic
        subtopic_stats: Dict[str, Dict[str, Any]] = {}
        for s in states:
            key = f"{s.topic}::{s.subtopic}"
            if key not in subtopic_stats:
                subtopic_stats[key] = {
                    "topic": s.topic,
                    "subtopic": s.subtopic,
                    "evaluated_students": 0,
                    "struggling_count": 0,
                    "total_score": 0,
                }
            subtopic_stats[key]["evaluated_students"] += 1
            subtopic_stats[key]["total_score"] += s.mastery_score
            if s.status == "struggling" or s.mastery_score < 50:
                subtopic_stats[key]["struggling_count"] += 1

        signals = []
        for key, data in subtopic_stats.items():
            evaluated_count = max(1, data["evaluated_students"])
            struggling_pct = int((data["struggling_count"] / evaluated_count) * 100)

            # Generate actionable recommendation for lecturer if > 30% are struggling
            recommendation = None
            if struggling_pct >= 50:
                recommendation = (
                    f"{struggling_pct}% of students struggled with {data['subtopic']} on recent diagnostics. "
                    f"Recommended action: Dedicate 10-15 minutes in the next lecture to review core definitions and state transitions."
                )
            elif struggling_pct >= 30:
                recommendation = f"{struggling_pct}% have partial understanding of {data['subtopic']}. Consider sharing an extra worked example."

            signals.append(
                LecturerClassSignalDTO(
                    course_id=course.id,
                    course_code=course.code,
                    topic=data["topic"],
                    subtopic=data["subtopic"],
                    total_students=evaluated_count,
                    struggling_count=data["struggling_count"],
                    struggling_percentage=struggling_pct,
                    recommendation=recommendation,
                )
            )

        # Sort by highest struggling percentage first
        signals.sort(key=lambda s: s.struggling_percentage, reverse=True)
        return signals
