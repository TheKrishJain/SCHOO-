from django.db import models
import uuid

class School(models.Model):
    """
    The TENANT model.
    Every piece of data (StudentEnrollment, TeacherAssignment, Exam)
    must point back to a School.
    """
    BOARD_CHOICES = [
        ('CBSE', 'CBSE'),
        ('ICSE', 'ICSE'),
        ('IGCSE', 'IGCSE'),
        ('IB', 'IB'),
        ('STATE', 'State Board'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True, help_text="Unique School Code (e.g., DAV-MUM-01)")
    board = models.CharField(max_length=10, choices=BOARD_CHOICES)
    
    # Address/Contact info (Optional but practical)
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


# Import settings model at the end to avoid circular import
from .models_settings import SchoolSettings
from .models_academic_config import (
    SchoolAcademicConfig, 
    GradeTermConfig, 
    ExamType, 
    GradeExamStructure, 
    CustomGradeScale
)
from .models_calendar import Holiday, SchoolEvent