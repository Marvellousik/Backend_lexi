"""
Services package for Academic Context, Timetables, Knowledge States, and Signals.
"""
from academic_service.services.academic_service import AcademicService
from academic_service.services.timetable_service import TimetableService
from academic_service.services.context_completion import ContextCompletionEngine
from academic_service.services.knowledge_state_service import KnowledgeStateService
from academic_service.services.signal_ingestion_service import SignalIngestionService
from academic_service.services.lecturer_signal_service import LecturerSignalService
from academic_service.services.proactive_engine import ProactiveEngine, ProactiveGovernor
from academic_service.services.course_partner_service import CoursePartnerService
from academic_service.services.context_assembler import ContextAssembler, AssembledContext

__all__ = [
    "AcademicService",
    "TimetableService",
    "ContextCompletionEngine",
    "KnowledgeStateService",
    "SignalIngestionService",
    "LecturerSignalService",
    "ProactiveEngine",
    "ProactiveGovernor",
    "CoursePartnerService",
    "ContextAssembler",
    "AssembledContext",
]


