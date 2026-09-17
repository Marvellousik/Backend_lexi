"""
Timetable and Schedule Service for Lexi.
Builds student weekly timetables, calculates next upcoming classes, and computes minute countdowns.
"""
import uuid
import logging
from datetime import datetime, timezone, time, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from academic_service.models.orm import CourseSchedule, Course, StudentEnrollment
from academic_service.models.schema import CourseScheduleDTO, NextClassResponse, TimetableSlotCreate

logger = logging.getLogger(__name__)

DAY_NAMES = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}


class TimetableService:
    """Calculates student schedules and upcoming class countdowns."""

    @staticmethod
    def get_student_timetable(db: Session, user_id: str) -> List[Dict[str, Any]]:
        """Fetch full weekly timetable grouped by day for a student."""
        enrollments = (
            db.query(StudentEnrollment)
            .filter(StudentEnrollment.user_id == user_id, StudentEnrollment.status == "active")
            .all()
        )
        course_ids = [e.course_id for e in enrollments]
        if not course_ids:
            return []

        schedules = (
            db.query(CourseSchedule, Course)
            .join(Course, CourseSchedule.course_id == Course.id)
            .filter(CourseSchedule.course_id.in_(course_ids))
            .order_by(CourseSchedule.day_of_week, CourseSchedule.start_time)
            .all()
        )

        result = []
        for schedule, course in schedules:
            result.append({
                "id": schedule.id,
                "course_id": course.id,
                "course_code": course.code,
                "course_title": course.title,
                "day_of_week": schedule.day_of_week,
                "day_name": DAY_NAMES.get(schedule.day_of_week, ""),
                "start_time": schedule.start_time.strftime("%H:%M:%S") if hasattr(schedule.start_time, "strftime") else str(schedule.start_time),
                "end_time": schedule.end_time.strftime("%H:%M:%S") if hasattr(schedule.end_time, "strftime") else str(schedule.end_time),
                "venue": schedule.venue,
            })
        return result

    @staticmethod
    def get_next_class_for_student(
        db: Session,
        user_id: str,
        current_time: Optional[datetime] = None
    ) -> NextClassResponse:
        """
        Calculate the immediate next upcoming class for the student and minutes remaining.
        Supports wrap-around across weekdays and weekends.
        """
        now = current_time or datetime.now()
        current_weekday = now.isoweekday()  # 1 = Monday, 7 = Sunday
        current_time_val = now.time()

        enrollments = (
            db.query(StudentEnrollment)
            .filter(StudentEnrollment.user_id == user_id, StudentEnrollment.status == "active")
            .all()
        )
        course_ids = [e.course_id for e in enrollments]
        if not course_ids:
            return NextClassResponse(has_upcoming=False, message="No active courses enrolled")

        schedules = (
            db.query(CourseSchedule, Course)
            .join(Course, CourseSchedule.course_id == Course.id)
            .filter(CourseSchedule.course_id.in_(course_ids))
            .all()
        )

        if not schedules:
            return NextClassResponse(has_upcoming=False, message="No timetable schedules found for enrolled courses")

        # Find the earliest class occurrence ahead of `now`
        candidate_classes = []
        for schedule, course in schedules:
            slot_day = schedule.day_of_week
            slot_start = schedule.start_time

            # Days difference (0 to 6 days ahead)
            day_diff = (slot_day - current_weekday) % 7
            
            # If slot is today but already passed, push to next week (7 days ahead)
            if day_diff == 0 and slot_start <= current_time_val:
                day_diff = 7

            target_date = now.date() + timedelta(days=day_diff)
            target_dt = datetime.combine(target_date, slot_start)

            total_minutes = int((target_dt - now).total_seconds() // 60)
            candidate_classes.append((total_minutes, schedule, course))

        # Sort by earliest upcoming
        candidate_classes.sort(key=lambda x: x[0])
        minutes_remaining, next_sched, next_course = candidate_classes[0]

        return NextClassResponse(
            has_upcoming=True,
            course_code=next_course.code,
            course_title=next_course.title,
            day_of_week=next_sched.day_of_week,
            start_time=next_sched.start_time.strftime("%H:%M:%S") if hasattr(next_sched.start_time, "strftime") else str(next_sched.start_time),
            venue=next_sched.venue or "Main Lecture Hall",
            minutes_until_class=minutes_remaining,
            message=f"{next_course.code} starts in {minutes_remaining} minutes at {next_sched.venue or 'lecture hall'}",
        )

    @staticmethod
    def add_timetable_slot(db: Session, slot_data: TimetableSlotCreate, institution_id: str = "veritas_uni") -> CourseScheduleDTO:
        """Manually add or update a timetable slot for a course."""
        # Parse time strings
        start_parts = [int(p) for p in slot_data.start_time.split(":")]
        end_parts = [int(p) for p in slot_data.end_time.split(":")]
        
        start_t = time(hour=start_parts[0], minute=start_parts[1], second=start_parts[2] if len(start_parts) > 2 else 0)
        end_t = time(hour=end_parts[0], minute=end_parts[1], second=end_parts[2] if len(end_parts) > 2 else 0)

        slot = CourseSchedule(
            id=str(uuid.uuid4()),
            course_id=slot_data.course_id,
            institution_id=institution_id,
            day_of_week=slot_data.day_of_week,
            start_time=start_t,
            end_time=end_t,
            venue=slot_data.venue,
            recurrence="weekly",
        )
        db.add(slot)
        db.commit()

        return CourseScheduleDTO(
            id=slot.id,
            course_id=slot.course_id,
            day_of_week=slot.day_of_week,
            day_name=DAY_NAMES.get(slot.day_of_week, ""),
            start_time=slot_data.start_time,
            end_time=slot_data.end_time,
            venue=slot.venue,
            recurrence=slot.recurrence,
        )
