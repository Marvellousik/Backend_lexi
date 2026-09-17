"""
Academic Structure and Course Service for Lexi.
Manages institutions, departments, courses, syllabi, canonical lectures, and student enrollments.
"""
import uuid
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from academic_service.models.orm import (
    Institution,
    Faculty,
    Department,
    Course,
    CourseSchedule,
    StudentEnrollment,
    Lecture,
    AcademicEvent,
)
from academic_service.models.schema import CourseDetailDTO, CourseScheduleDTO, LectureDTO, AcademicEventDTO

logger = logging.getLogger(__name__)

DAY_NAMES = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}


class AcademicService:
    """Core domain logic for courses, syllabus, and enrollments."""

    @staticmethod
    def get_enrolled_courses(db: Session, user_id: str) -> List[CourseDetailDTO]:
        """Fetch all courses a student is actively enrolled in."""
        enrollments = (
            db.query(StudentEnrollment)
            .filter(StudentEnrollment.user_id == user_id, StudentEnrollment.status == "active")
            .all()
        )
        course_ids = [e.course_id for e in enrollments]
        if not course_ids:
            return []

        courses = db.query(Course).filter(Course.id.in_(course_ids)).all()
        return [AcademicService._to_course_dto(c) for c in courses]

    @staticmethod
    def get_course_by_id(db: Session, course_id: str) -> Optional[CourseDetailDTO]:
        """Fetch full details for a course including syllabus, schedules, and lectures."""
        # Query by ID or by Course Code (case-insensitive)
        course = (
            db.query(Course)
            .filter((Course.id == course_id) | (Course.code.ilike(course_id.strip())))
            .first()
        )
        if not course:
            return None
        return AcademicService._to_course_dto(course)

    @staticmethod
    def enroll_student(db: Session, user_id: str, course_identifier: str, semester: str = "2025/2026_FIRST") -> CourseDetailDTO:
        """Enroll a student into a course by ID or Code."""
        course = (
            db.query(Course)
            .filter((Course.id == course_identifier) | (Course.code.ilike(course_identifier.strip())))
            .first()
        )
        if not course:
            raise ValueError(f"Course '{course_identifier}' not found in academic catalog.")

        # Check existing enrollment
        existing = (
            db.query(StudentEnrollment)
            .filter(StudentEnrollment.user_id == user_id, StudentEnrollment.course_id == course.id)
            .first()
        )
        if not existing:
            enrollment = StudentEnrollment(
                id=str(uuid.uuid4()),
                user_id=user_id,
                course_id=course.id,
                semester=semester,
                status="active",
            )
            db.add(enrollment)
            db.commit()
            logger.info(f"Enrolled user {user_id} into course {course.code}")

        return AcademicService._to_course_dto(course)

    @staticmethod
    def _to_course_dto(c: Course) -> CourseDetailDTO:
        """Convert Course ORM to detailed DTO."""
        schedules_dto = [
            CourseScheduleDTO(
                id=s.id,
                course_id=s.course_id,
                day_of_week=s.day_of_week,
                day_name=DAY_NAMES.get(s.day_of_week, f"Day {s.day_of_week}"),
                start_time=s.start_time.strftime("%H:%M:%S") if hasattr(s.start_time, "strftime") else str(s.start_time),
                end_time=s.end_time.strftime("%H:%M:%S") if hasattr(s.end_time, "strftime") else str(s.end_time),
                venue=s.venue,
                recurrence=s.recurrence or "weekly",
            )
            for s in (c.schedules or [])
        ]

        lectures_dto = [
            LectureDTO(
                id=l.id,
                course_id=l.course_id,
                lecture_number=l.lecture_number,
                title=l.title,
                date=l.date.isoformat() if l.date else None,
                start_time=str(l.start_time) if l.start_time else None,
                end_time=str(l.end_time) if l.end_time else None,
                topics_covered=l.topics_covered or [],
                slides_url=l.slides_url,
                summary_text=l.summary_text,
                is_processed=l.is_processed,
            )
            for l in (c.lectures or [])
        ]

        events_dto = [
            AcademicEventDTO(
                id=e.id,
                course_id=e.course_id,
                event_type=e.event_type,
                title=e.title,
                description=e.description,
                due_date=e.due_date.isoformat() if e.due_date else "",
                weight_percent=e.weight_percent,
            )
            for e in (c.events or [])
        ]

        return CourseDetailDTO(
            id=c.id,
            institution_id=c.institution_id,
            department_id=c.department_id,
            code=c.code,
            title=c.title,
            level=c.level,
            credit_units=c.credit_units,
            syllabus=c.syllabus or [],
            description=c.description,
            schedules=schedules_dto,
            lectures=lectures_dto,
            events=events_dto,
        )
