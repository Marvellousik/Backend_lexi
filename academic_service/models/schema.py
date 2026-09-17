"""
Pydantic schemas and DTOs for the Academic Context Graph & Timetables.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, time, date
from pydantic import BaseModel, Field


class InstitutionDTO(BaseModel):
    id: str
    name: str
    code: str
    domain: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class FacultyDTO(BaseModel):
    id: str
    institution_id: str
    name: str
    code: str


class DepartmentDTO(BaseModel):
    id: str
    faculty_id: str
    institution_id: str
    name: str
    code: str


class CourseScheduleDTO(BaseModel):
    id: str
    course_id: str
    day_of_week: int = Field(..., ge=1, le=7, description="1=Monday, 7=Sunday")
    day_name: Optional[str] = None
    start_time: str
    end_time: str
    venue: Optional[str] = None
    recurrence: str = "weekly"


class LectureDTO(BaseModel):
    id: str
    course_id: str
    lecture_number: int
    title: str
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    topics_covered: Optional[List[str]] = None
    slides_url: Optional[str] = None
    summary_text: Optional[str] = None
    is_processed: bool = False


class AcademicEventDTO(BaseModel):
    id: str
    course_id: str
    event_type: str
    title: str
    description: Optional[str] = None
    due_date: str
    weight_percent: Optional[int] = None


class CourseDetailDTO(BaseModel):
    id: str
    institution_id: str
    department_id: str
    code: str
    title: str
    level: int
    credit_units: int
    syllabus: Optional[List[Dict[str, Any]]] = None
    description: Optional[str] = None
    schedules: List[CourseScheduleDTO] = []
    lectures: List[LectureDTO] = []
    events: List[AcademicEventDTO] = []


class CourseEnrollmentRequest(BaseModel):
    course_id: str = Field(..., description="Course ID or Course Code (e.g. CSC 301)")
    semester: Optional[str] = "2025/2026_FIRST"


class TimetableSlotCreate(BaseModel):
    course_id: str
    day_of_week: int = Field(..., ge=1, le=7)
    start_time: str = Field(..., description="HH:MM:SS format")
    end_time: str = Field(..., description="HH:MM:SS format")
    venue: Optional[str] = "Main Lecture Hall"


class NextClassResponse(BaseModel):
    has_upcoming: bool
    course_code: Optional[str] = None
    course_title: Optional[str] = None
    day_of_week: Optional[int] = None
    start_time: Optional[str] = None
    venue: Optional[str] = None
    minutes_until_class: Optional[int] = None
    message: Optional[str] = None


class ContextGapDTO(BaseModel):
    id: str
    user_id: str
    course_id: str
    gap_type: str
    prompt_question: str
    field_target: str
    is_resolved: bool = False


class ResolveGapRequest(BaseModel):
    response_value: str = Field(..., description="Student input value (e.g. '09:00' or 'Science Lab 2')")


# ==============================================================================
# Phase 2: Knowledge State & Learning Signals Schemas
# ==============================================================================

class LearningSignalCreate(BaseModel):
    course_id: str = Field(..., description="Course ID or Code (e.g. 'CSC 301')")
    topic: str = Field(..., description="e.g. 'Dynamic Programming'")
    subtopic: str = Field(..., description="e.g. 'Optimal Substructure'")
    signal_type: str = Field(..., description="'quiz_attempt', 'diagnostic', 'flashcard_review', 'chat_question'")
    score: int = Field(..., ge=0, description="Points scored")
    max_score: int = Field(default=1, ge=1, description="Maximum possible points")
    details: Optional[Dict[str, Any]] = None


class KnowledgeStateDTO(BaseModel):
    topic: str
    subtopic: str
    mastery_score: int = Field(..., description="0-100%")
    status: str = Field(..., description="'not_started', 'learning', 'struggling', 'mastered'")
    total_attempts: int
    correct_attempts: int
    last_evaluated_at: Optional[str] = None
    last_error_summary: Optional[str] = None


class TopicMasteryGroupDTO(BaseModel):
    topic: str
    average_mastery: int
    subtopics: List[KnowledgeStateDTO]


class CourseMasteryGraphDTO(BaseModel):
    course_id: str
    course_code: str
    overall_mastery: int
    mastered_count: int
    struggling_count: int
    total_subtopics: int
    topic_groups: List[TopicMasteryGroupDTO]


class WeakTopicDTO(BaseModel):
    course_id: str
    course_code: str
    topic: str
    subtopic: str
    mastery_score: int
    status: str
    reason: str


class LecturerClassSignalDTO(BaseModel):
    course_id: str
    course_code: str
    topic: str
    subtopic: str
    total_students: int
    struggling_count: int
    struggling_percentage: int
    recommendation: Optional[str] = None


# ==============================================================================
# Phase 4: Proactive Engine & "Today" Timeline Schemas
# ==============================================================================

class TimelineCardDTO(BaseModel):
    id: str
    card_type: str = Field(..., description="'class_countdown', 'pre_class_prep', 'post_class_summary', 'practice_gap', 'deadline'")
    priority: int = Field(default=2, description="1=High, 2=Medium, 3=Low")
    title: str
    subtitle: Optional[str] = None
    action_type: str = Field(..., description="'start_diagnostic', 'review_summary', 'view_class', 'solve_gap', 'open_deadline', 'review_notes'")
    action_payload: Optional[Dict[str, Any]] = None
    estimated_minutes: Optional[int] = None
    course_id: Optional[str] = None
    course_code: Optional[str] = None
    created_at: Optional[str] = None
    is_dismissed: bool = False
    is_acted_upon: bool = False


class TodayTimelineResponse(BaseModel):
    date: str
    current_academic_session: Optional[str] = "2025/2026_FIRST"
    cards: List[TimelineCardDTO] = []


class InterventionDecisionDTO(BaseModel):
    should_intervene: bool
    reason: str
    card: Optional[TimelineCardDTO] = None


class TimelineActionResponse(BaseModel):
    status: str
    message: str
    intervention_id: str
    learning_signal_recorded: bool = False


# ==============================================================================
# Phase 3: Course Academic Partner (Student ↔ Lexi) Schemas & Widget DTOs
# ==============================================================================

class FlashcardItemDTO(BaseModel):
    id: Optional[str] = None
    front: str = Field(..., description="Front question / prompt")
    back: str = Field(..., description="Back answer / concept explanation")
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    citation: Optional[str] = None


class FlashcardWidgetDTO(BaseModel):
    title: str = Field(..., description="Widget deck title")
    topic: Optional[str] = None
    cards: List[FlashcardItemDTO] = []
    count: int = 0


class QuizQuestionDTO(BaseModel):
    id: Optional[str] = None
    question: str = Field(..., description="Question text")
    options: Dict[str, str] = Field(default_factory=dict, description="Options dictionary, e.g. {'A': '...', 'B': '...'}")
    correct_answer: str = Field(..., description="Correct option key, e.g. 'A'")
    explanation: Optional[str] = None
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    citation: Optional[str] = None


class QuizWidgetDTO(BaseModel):
    title: str = Field(..., description="Quiz widget title")
    topic: Optional[str] = None
    quiz_type: str = "multiple_choice"
    questions: List[QuizQuestionDTO] = []
    count: int = 0


class ConceptItemDTO(BaseModel):
    term: str = Field(..., description="Concept name / term")
    definition: str = Field(..., description="Definition or explanation")
    example: Optional[str] = None
    formula: Optional[str] = None
    key_takeaway: Optional[str] = None
    citation: Optional[str] = None


class ConceptWidgetDTO(BaseModel):
    title: str = Field(..., description="Concept widget title")
    topic: Optional[str] = None
    concepts: List[ConceptItemDTO] = []
    summary: Optional[str] = None


class PartnerChatMessageDTO(BaseModel):
    id: Optional[str] = None
    role: str = Field(..., description="'user', 'assistant', 'system'")
    content: str = Field(..., description="Markdown message text")
    widget_type: Optional[str] = None
    widget_data: Optional[Dict[str, Any]] = None
    provenance_citations: Optional[List[str]] = None
    created_at: Optional[str] = None


class PartnerChatRequest(BaseModel):
    course_id: Optional[str] = Field(None, description="Course ID or Course Code (e.g. 'CSC 301')")
    topic: Optional[str] = Field(None, description="Optional focused topic or subtopic")
    message: str = Field(..., description="Student input message")
    session_id: Optional[str] = Field(None, description="Session ID for continuous dialogue")
    history: Optional[List[Dict[str, Any]]] = Field(default=[], description="Recent conversation turns")


class PartnerChatResponse(BaseModel):
    session_id: str
    course_id: str
    course_code: str
    message: str
    intent: str = Field(..., description="'FLASHCARD_GENERATION', 'DIAGNOSTIC_QUIZ', 'EXPLANATION', 'FORMULA_CARD', 'CONCEPT_BREAKDOWN', 'GENERAL_TUTOR'")
    widget_type: Optional[str] = None
    widget_data: Optional[Dict[str, Any]] = None
    provenance_citations: List[str] = []
    weak_topics_referenced: List[str] = []
    created_at: str


class PartnerHistoryResponse(BaseModel):
    course_id: str
    course_code: str
    session_id: Optional[str] = None
    messages: List[PartnerChatMessageDTO] = []


class LectureIngestRequest(BaseModel):
    file_url: Optional[str] = None
    raw_text: Optional[str] = None


class LectureIngestionResponse(BaseModel):
    lecture_id: str
    course_code: str
    lecture_number: int
    title: str
    slides_processed: int
    chunks_indexed: int
    topics_bound: List[str]
    summary: str
    status: str




