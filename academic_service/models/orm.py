"""
SQLAlchemy ORM models for Lexi's Academic Context Graph (academic.* schema).
Supports Veritas University hierarchy, courses, timetables, canonical lectures, and context gaps.
"""
from datetime import datetime, timezone, time, date
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    Text,
    DateTime,
    Date,
    Time,
    JSON,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Institution(Base):
    """University / Educational Institution entity."""
    __tablename__ = "institutions"
    __table_args__ = {"schema": "academic"}

    id = Column(String, primary_key=True)  # e.g., "veritas_uni"
    name = Column(String, nullable=False)  # "Veritas University"
    code = Column(String, nullable=False)  # "VUNA"
    domain = Column(String, nullable=True) # "veritas.edu.ng"
    settings = Column(JSON, nullable=True) # Working hours, active semester dates
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    faculties = relationship("Faculty", back_populates="institution", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="institution", cascade="all, delete-orphan")


class Faculty(Base):
    """Faculty / College within an institution."""
    __tablename__ = "faculties"
    __table_args__ = (
        Index("idx_academic_faculties_inst", "institution_id"),
        {"schema": "academic"},
    )

    id = Column(String, primary_key=True)  # e.g., "faculty_science_veritas"
    institution_id = Column(String, ForeignKey("academic.institutions.id"), nullable=False)
    name = Column(String, nullable=False)  # "Faculty of Natural and Applied Sciences"
    code = Column(String, nullable=False)  # "FNAS"

    institution = relationship("Institution", back_populates="faculties")
    departments = relationship("Department", back_populates="faculty", cascade="all, delete-orphan")


class Department(Base):
    """Academic Department offering courses."""
    __tablename__ = "departments"
    __table_args__ = (
        Index("idx_academic_depts_faculty", "faculty_id"),
        {"schema": "academic"},
    )

    id = Column(String, primary_key=True)  # e.g., "dept_cs_veritas"
    faculty_id = Column(String, ForeignKey("academic.faculties.id"), nullable=False)
    institution_id = Column(String, nullable=False)
    name = Column(String, nullable=False)  # "Department of Computer Science"
    code = Column(String, nullable=False)  # "CSC"

    faculty = relationship("Faculty", back_populates="departments")
    courses = relationship("Course", back_populates="department", cascade="all, delete-orphan")


class Course(Base):
    """Academic Course offering."""
    __tablename__ = "courses"
    __table_args__ = (
        Index("idx_academic_courses_dept", "department_id"),
        Index("idx_academic_courses_code", "institution_id", "code"),
        {"schema": "academic"},
    )

    id = Column(String, primary_key=True)  # e.g., "course_csc301_veritas"
    institution_id = Column(String, ForeignKey("academic.institutions.id"), nullable=False)
    department_id = Column(String, ForeignKey("academic.departments.id"), nullable=False)
    code = Column(String, nullable=False)  # "CSC 301"
    title = Column(String, nullable=False) # "Data Structures and Algorithms"
    level = Column(Integer, default=300)   # 100, 200, 300, 400
    credit_units = Column(Integer, default=3)
    syllabus = Column(JSON, nullable=True) # [{"topic": "...", "subtopics": [...]}]
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    institution = relationship("Institution", back_populates="courses")
    department = relationship("Department", back_populates="courses")
    schedules = relationship("CourseSchedule", back_populates="course", cascade="all, delete-orphan")
    lectures = relationship("Lecture", back_populates="course", cascade="all, delete-orphan")
    events = relationship("AcademicEvent", back_populates="course", cascade="all, delete-orphan")


class CourseSchedule(Base):
    """Weekly recurring timetable slot for a course."""
    __tablename__ = "course_schedules"
    __table_args__ = (
        Index("idx_academic_schedules_course", "course_id"),
        Index("idx_academic_schedules_day", "day_of_week"),
        {"schema": "academic"},
    )

    id = Column(String, primary_key=True)
    course_id = Column(String, ForeignKey("academic.courses.id"), nullable=False)
    institution_id = Column(String, nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 1 = Monday, 7 = Sunday
    start_time = Column(Time, nullable=False)      # e.g. 09:00:00
    end_time = Column(Time, nullable=False)        # e.g. 11:00:00
    venue = Column(String, nullable=True)          # "Science Lab 2"
    recurrence = Column(String, default="weekly")

    course = relationship("Course", back_populates="schedules")


class StudentEnrollment(Base):
    """Student enrollment record mapping a user to a course."""
    __tablename__ = "student_enrollments"
    __table_args__ = (
        Index("idx_academic_enrollments_user", "user_id"),
        Index("idx_academic_enrollments_course", "course_id"),
        Index("idx_academic_enrollments_user_course", "user_id", "course_id", unique=True),
        {"schema": "academic"},
    )

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    course_id = Column(String, ForeignKey("academic.courses.id"), nullable=False)
    semester = Column(String, default="2025/2026_FIRST")
    status = Column(String, default="active")  # active, completed, dropped
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Lecture(Base):
    """Canonical course lecture bank."""
    __tablename__ = "lectures"
    __table_args__ = (
        Index("idx_academic_lectures_course", "course_id"),
        Index("idx_academic_lectures_date", "course_id", "date"),
        {"schema": "academic"},
    )

    id = Column(String, primary_key=True)
    course_id = Column(String, ForeignKey("academic.courses.id"), nullable=False)
    lecture_number = Column(Integer, nullable=False)  # e.g. 14
    title = Column(String, nullable=False)            # "Dynamic Programming & Optimal Substructure"
    date = Column(Date, nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    topics_covered = Column(JSON, nullable=True)      # ["Optimal Substructure", "Memoization"]
    slides_url = Column(String, nullable=True)
    transcript_doc_id = Column(String, nullable=True) # Linked document ID in vector chunks
    summary_text = Column(Text, nullable=True)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    course = relationship("Course", back_populates="lectures")


class AcademicEvent(Base):
    """Deadlines, midterms, and examination events."""
    __tablename__ = "academic_events"
    __table_args__ = (
        Index("idx_academic_events_course", "course_id"),
        Index("idx_academic_events_due", "due_date"),
        {"schema": "academic"},
    )

    id = Column(String, primary_key=True)
    course_id = Column(String, ForeignKey("academic.courses.id"), nullable=False)
    event_type = Column(String, nullable=False)  # "assignment", "midterm", "final_exam", "project"
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=False)
    weight_percent = Column(Integer, nullable=True)  # e.g., 20%
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    course = relationship("Course", back_populates="events")


class ContextGap(Base):
    """Identifies and tracks missing academic information for proactive completion."""
    __tablename__ = "context_gaps"
    __table_args__ = (
        Index("idx_academic_gaps_user", "user_id"),
        Index("idx_academic_gaps_status", "user_id", "is_resolved"),
        {"schema": "academic"},
    )

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    course_id = Column(String, nullable=False)
    gap_type = Column(String, nullable=False)  # "missing_class_time", "missing_venue", "missing_exam_date"
    prompt_question = Column(Text, nullable=False)
    field_target = Column(String, nullable=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    response_value = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class StudentKnowledgeState(Base):
    """Living mastery state of a student for a specific topic/subtopic in a course."""
    __tablename__ = "student_knowledge_states"
    __table_args__ = (
        Index("idx_academic_ks_user_course", "user_id", "course_id"),
        Index("idx_academic_ks_status", "user_id", "status"),
        Index("idx_academic_ks_unique", "user_id", "course_id", "topic", "subtopic", unique=True),
        {"schema": "academic"},
    )

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    course_id = Column(String, ForeignKey("academic.courses.id"), nullable=False)
    topic = Column(String, nullable=False)        # e.g. "Dynamic Programming"
    subtopic = Column(String, nullable=False)     # e.g. "Optimal Substructure"
    mastery_score = Column(Integer, default=0)    # 0 to 100 percentage
    status = Column(String, default="not_started") # "not_started", "learning", "struggling", "mastered"
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    last_evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_error_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class LearningSignal(Base):
    """Atomic learning interaction event (quiz, diagnostic, flashcard, explanation)."""
    __tablename__ = "learning_signals"
    __table_args__ = (
        Index("idx_academic_signals_user_course", "user_id", "course_id"),
        Index("idx_academic_signals_created", "created_at"),
        {"schema": "academic"},
    )

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    course_id = Column(String, ForeignKey("academic.courses.id"), nullable=False)
    topic = Column(String, nullable=False)
    subtopic = Column(String, nullable=False)
    signal_type = Column(String, nullable=False)  # "quiz_attempt", "diagnostic", "flashcard_review", "chat_question"
    score = Column(Integer, nullable=False)       # Points scored (e.g. 1 out of 1, or 3 out of 5)
    max_score = Column(Integer, default=1)
    raw_details = Column(JSON, nullable=True)     # Detailed answers, misconception hints
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class LearningGap(Base):
    """Active conceptual gap or misconception diagnosed for a student."""
    __tablename__ = "learning_gaps"
    __table_args__ = (
        Index("idx_academic_gaps_student_course", "user_id", "course_id"),
        {"schema": "academic"},
    )

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    course_id = Column(String, ForeignKey("academic.courses.id"), nullable=False)
    topic = Column(String, nullable=False)
    subtopic = Column(String, nullable=False)
    gap_description = Column(Text, nullable=False) # "Repeatedly misses base cases in recurrence formulations"
    severity = Column(String, default="medium")    # "low", "medium", "high"
    status = Column(String, default="active")      # "active", "improving", "resolved"
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class LecturerClassSignal(Base):
    """Aggregated academic insight card for lecturers and departments."""
    __tablename__ = "lecturer_class_signals"
    __table_args__ = (
        Index("idx_academic_class_signals_course", "course_id"),
        {"schema": "academic"},
    )

    id = Column(String, primary_key=True)
    course_id = Column(String, ForeignKey("academic.courses.id"), nullable=False)
    topic = Column(String, nullable=False)
    subtopic = Column(String, nullable=False)
    cohort = Column(String, default="2025/2026_FIRST")
    total_students = Column(Integer, default=0)
    struggling_count = Column(Integer, default=0)
    struggling_percentage = Column(Integer, default=0) # e.g. 62%
    recommendation = Column(Text, nullable=True)       # e.g. "Review state transitions in next lecture"
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ProactiveIntervention(Base):
    """Logs proactive interventions dispatched to the student to govern frequency and fatigue."""
    __tablename__ = "proactive_interventions"
    __table_args__ = (
        Index("idx_academic_interventions_user", "user_id"),
        Index("idx_academic_interventions_delivered", "delivered_at"),
        Index("idx_academic_interventions_user_delivered", "user_id", "delivered_at"),
        {"schema": "academic"},
    )

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    course_id = Column(String, ForeignKey("academic.courses.id"), nullable=True)
    event_type = Column(String, nullable=False) # e.g. 'CLASS_APPROACHING', 'CLASS_ENDED', 'EXAM_APPROACHING', 'GAP_DETECTED'
    card_type = Column(String, nullable=False)  # 'class_countdown', 'pre_class_prep', 'post_class_summary', 'practice_gap', 'deadline'
    title = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)
    is_dismissed = Column(Boolean, default=False)
    is_acted_upon = Column(Boolean, default=False)
    delivered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PartnerConversation(Base):
    """Course Academic Partner conversational dialogue turn with structured interactive artifacts."""
    __tablename__ = "partner_conversations"
    __table_args__ = (
        Index("idx_academic_partner_conv_user_course", "user_id", "course_id"),
        Index("idx_academic_partner_conv_session", "session_id", "created_at"),
        {"schema": "academic"},
    )

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    course_id = Column(String, ForeignKey("academic.courses.id"), nullable=False, index=True)
    session_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    widget_type = Column(String, nullable=True)  # "flashcard_deck", "quiz_card", "concept_card", etc.
    widget_data = Column(JSON, nullable=True)
    provenance_citations = Column(JSON, nullable=True)  # List[str]
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    course = relationship("Course")


