from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
import json
from .models import (
    Grade, Section, Subject, SubjectMapping, Timetable, Period,
    Syllabus, Chapter, Exam, Result, ReportCard
)
from apps.features.services import school_has_feature


# ============================================================
# CLASS & SECTION SERIALIZERS
# ============================================================

class GradeSerializer(serializers.ModelSerializer):
    sections_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Grade
        fields = ['id', 'grade_number', 'grade_name', 'is_active', 'sections_count', 'created_at']
        read_only_fields = ['created_at']
    
    def get_sections_count(self, obj):
        return obj.sections.filter(is_active=True).count()


class SectionListSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source='grade.grade_name', read_only=True)
    class_teacher_name = serializers.CharField(source='class_teacher.user.full_name', read_only=True, allow_null=True)
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Section
        fields = ['id', 'full_name', 'grade_name', 'section_letter', 'capacity', 'class_teacher_name', 'student_count', 'is_active']
    
    def get_student_count(self, obj):
        from apps.enrollments.models import StudentEnrollment
        # grade and section are stored as strings in StudentEnrollment
        return StudentEnrollment.objects.filter(
            school_id=obj.school_id,
            grade=str(obj.grade.grade_number),
            section=obj.section_letter,
            status='ACTIVE'
        ).count()


class SectionDetailSerializer(serializers.ModelSerializer):
    grade_info = GradeSerializer(source='grade', read_only=True)
    class_teacher_info = serializers.SerializerMethodField()
    subjects = serializers.SerializerMethodField()
    
    class Meta:
        model = Section
        fields = ['id', 'grade_info', 'section_letter', 'capacity', 'class_teacher_info', 'is_active', 'subjects', 'created_at']
    
    def get_class_teacher_info(self, obj):
        if obj.class_teacher:
            return {
                'id': str(obj.class_teacher.id),
                'name': obj.class_teacher.user.full_name,
                'email': obj.class_teacher.user.email
            }
        return None
    
    def get_subjects(self, obj):
        mappings = obj.subject_mappings.filter(is_active=True)
        return SubjectMappingListSerializer(mappings, many=True).data


class SectionSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating sections with write-only foreign key IDs"""
    school_id = serializers.UUIDField(write_only=True)
    grade_id = serializers.UUIDField(write_only=True)
    class_teacher_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    co_class_teacher_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    # Read-only display fields
    grade_name = serializers.CharField(source='grade.grade_name', read_only=True)
    class_teacher_name = serializers.CharField(source='class_teacher.user.full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Section
        fields = [
            'id', 'school_id', 'grade_id', 'grade_name', 'section_letter', 'capacity',
            'class_teacher_id', 'class_teacher_name', 'co_class_teacher_id',
            'room_number', 'capacity_locked', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        from apps.schools.models import School
        from apps.teachers.models import Teacher
        
        school_id = data.get('school_id')
        grade_id = data.get('grade_id')
        
        # Validate school exists
        try:
            school = School.objects.get(id=school_id)
        except School.DoesNotExist:
            raise serializers.ValidationError({'school_id': 'School not found'})
        
        # Validate grade exists and belongs to school
        try:
            grade = Grade.objects.get(id=grade_id, school=school)
        except Grade.DoesNotExist:
            raise serializers.ValidationError({'grade_id': 'Grade not found or does not belong to this school'})
        
        # Validate class teacher if provided
        class_teacher_id = data.get('class_teacher_id')
        if class_teacher_id:
            try:
                teacher = Teacher.objects.get(id=class_teacher_id)
                # Store teacher instance for create method
                data['class_teacher'] = teacher
            except Teacher.DoesNotExist:
                raise serializers.ValidationError({'class_teacher_id': 'Teacher not found'})
        
        # Validate co-class teacher if provided
        co_class_teacher_id = data.get('co_class_teacher_id')
        if co_class_teacher_id:
            try:
                teacher = Teacher.objects.get(id=co_class_teacher_id)
                data['co_class_teacher'] = teacher
            except Teacher.DoesNotExist:
                raise serializers.ValidationError({'co_class_teacher_id': 'Co-teacher not found'})
        
        # Check uniqueness
        section_letter = data.get('section_letter')
        if Section.objects.filter(school_id=school_id, grade_id=grade_id, section_letter=section_letter).exists():
            raise serializers.ValidationError(
                f'Section {section_letter} already exists for {grade.grade_name}'
            )
        
        # Store resolved instances
        data['school'] = school
        data['grade'] = grade
        
        return data
    
    def create(self, validated_data):
        # Remove write-only ID fields and use resolved instances
        validated_data.pop('school_id', None)
        validated_data.pop('grade_id', None)
        validated_data.pop('class_teacher_id', None)
        validated_data.pop('co_class_teacher_id', None)
        
        return Section.objects.create(**validated_data)


# ============================================================
# SUBJECT SERIALIZERS
# ============================================================

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'description', 'is_core', 'is_active', 'created_at']
        read_only_fields = ['created_at']


class SubjectMappingListSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True, allow_null=True)
    section_name = serializers.CharField(source='section.full_name', read_only=True)
    
    class Meta:
        model = SubjectMapping
        fields = ['id', 'subject_name', 'subject_code', 'section_name', 'teacher_name', 'periods_per_week', 'max_marks', 'is_active']


class SubjectMappingDetailSerializer(serializers.ModelSerializer):
    subject_info = SubjectSerializer(source='subject', read_only=True)
    teacher_info = serializers.SerializerMethodField()
    section_info = SectionListSerializer(source='section', read_only=True)
    
    class Meta:
        model = SubjectMapping
        fields = ['id', 'subject_info', 'section_info', 'teacher_info', 'periods_per_week', 'max_marks', 'is_active']
    
    def get_teacher_info(self, obj):
        if obj.teacher:
            return {
                'id': str(obj.teacher.id),
                'name': obj.teacher.user.full_name,
                'email': obj.teacher.user.email
            }
        return None


# ============================================================
# TIMETABLE SERIALIZERS
# ============================================================

class PeriodSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject_mapping.subject.name', read_only=True, allow_null=True)
    teacher_name = serializers.CharField(source='subject_mapping.teacher.user.full_name', read_only=True, allow_null=True)
    day_display = serializers.CharField(source='get_day_display', read_only=True)
    
    # Write-only fields
    timetable_id = serializers.UUIDField(write_only=True, required=False)
    subject_mapping_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Period
        fields = [
            'id', 'day', 'day_display', 'period_number', 'start_time', 'end_time', 
            'subject_name', 'teacher_name', 'classroom', 'timetable_id', 'subject_mapping_id'
        ]
        read_only_fields = ['day_display']
    
    def validate(self, data):
        """Validate period data"""
        timetable_id = data.get('timetable_id')
        subject_mapping_id = data.get('subject_mapping_id')
        
        # Validate timetable if provided
        if timetable_id:
            try:
                timetable = Timetable.objects.get(id=timetable_id)
                data['timetable'] = timetable
            except Timetable.DoesNotExist:
                raise serializers.ValidationError({'timetable_id': 'Timetable not found'})
        
        # Validate subject mapping if provided
        if subject_mapping_id:
            try:
                subject_mapping = SubjectMapping.objects.get(id=subject_mapping_id)
                data['subject_mapping'] = subject_mapping
            except SubjectMapping.DoesNotExist:
                raise serializers.ValidationError({'subject_mapping_id': 'Subject mapping not found'})
        
        return data
    
    def create(self, validated_data):
        """Create period with explicit FK relationships"""
        timetable_id = validated_data.pop('timetable_id', None)
        subject_mapping_id = validated_data.pop('subject_mapping_id', None)
        
        if timetable_id:
            validated_data['timetable_id'] = timetable_id
        if subject_mapping_id:
            validated_data['subject_mapping_id'] = subject_mapping_id
        
        return Period.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update period"""
        timetable_id = validated_data.pop('timetable_id', None)
        subject_mapping_id = validated_data.pop('subject_mapping_id', None)
        
        if timetable_id:
            validated_data['timetable_id'] = timetable_id
        if subject_mapping_id:
            validated_data['subject_mapping_id'] = subject_mapping_id
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TimetableSerializer(serializers.ModelSerializer):
    # Read-only display fields
    section_name = serializers.CharField(source='section.full_name', read_only=True)
    section_id = serializers.SerializerMethodField()
    periods = PeriodSerializer(many=True, read_only=True)
    
    # Write-only ID fields for creation
    school_id = serializers.UUIDField(write_only=True, required=True)
    section_id_write = serializers.UUIDField(write_only=True, required=True)
    
    class Meta:
        model = Timetable
        fields = ['id', 'section_name', 'section_id', 'periods', 'created_at', 'updated_at', 'school_id', 'section_id_write']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_section_id(self, obj):
        return str(obj.section.id)
    
    def validate(self, data):
        """Validate same-school and feature flag"""
        if self.instance:  # Skip on update
            return data
        
        school_id = data.get('school_id')
        section_id_write = data.get('section_id_write')
        
        # 1. Check feature flag
        if not school_has_feature(school_id, 'TIMETABLE'):
            raise serializers.ValidationError({'school_id': 'Timetable management not enabled for this school'})
        
        # 2. Validate section belongs to school
        try:
            section = Section.objects.get(id=section_id_write)
            if str(section.school_id) != str(school_id):
                raise serializers.ValidationError({'section_id': 'Section does not belong to this school'})
        except Section.DoesNotExist:
            raise serializers.ValidationError({'section_id': 'Section not found'})
        
        # 3. Check if timetable already exists for section
        if Timetable.objects.filter(section_id=section_id_write).exists():
            raise serializers.ValidationError({'section_id': 'Timetable already exists for this section'})
        
        return data
    
    def create(self, validated_data):
        """Create timetable with explicit FKs"""
        school_id = validated_data.pop('school_id')
        section_id_write = validated_data.pop('section_id_write')
        
        return Timetable.objects.create(
            school_id=school_id,
            section_id=section_id_write,
            **validated_data
        )


# ============================================================
# SYLLABUS & CHAPTER SERIALIZERS
# ============================================================

class ChapterSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    last_updated_by_name = serializers.CharField(source='last_updated_by.full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Chapter
        fields = [
            'id', 'chapter_number', 'title', 'description', 'status', 'status_display',
            'planned_start_date', 'planned_end_date', 'actual_completion_date',
            'last_updated_by_name', 'last_updated_at'
        ]
        read_only_fields = ['last_updated_at']


class SyllabusSerializer(serializers.ModelSerializer):
    # Read-only display fields
    subject_name = serializers.CharField(source='subject_mapping.subject.name', read_only=True)
    section_name = serializers.CharField(source='subject_mapping.section.full_name', read_only=True)
    teacher_name = serializers.CharField(source='subject_mapping.teacher.user.full_name', read_only=True, allow_null=True)
    chapters = ChapterSerializer(many=True, read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    
    # Write-only ID fields for creation
    school_id = serializers.UUIDField(write_only=True, required=True)
    subject_mapping_id = serializers.UUIDField(write_only=True, required=True)
    
    class Meta:
        model = Syllabus
        fields = [
            'id', 'subject_name', 'section_name', 'teacher_name', 'total_chapters',
            'academic_year', 'chapters', 'progress_percentage', 'created_at', 'updated_at',
            'school_id', 'subject_mapping_id'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """Validate same-school, feature flag, and active academic year"""
        from apps.features.models import SchoolFeatureConfig
        
        if self.instance:  # Skip on update
            return data
        
        school_id = data.get('school_id')
        subject_mapping_id = data.get('subject_mapping_id')
        
        # 1. Check feature flag
        if not school_has_feature(school_id, 'TIMETABLE'):  # Syllabus often tied to timetable feature
            raise serializers.ValidationError({'school_id': 'Syllabus tracking not enabled for this school'})
        
        # 2. Validate subject_mapping belongs to school
        try:
            subject_mapping = SubjectMapping.objects.get(id=subject_mapping_id)
            if str(subject_mapping.school_id) != str(school_id):
                raise serializers.ValidationError({'subject_mapping_id': 'Subject mapping does not belong to this school'})
        except SubjectMapping.DoesNotExist:
            raise serializers.ValidationError({'subject_mapping_id': 'Subject mapping not found'})
        
        # 3. Check if syllabus already exists
        if Syllabus.objects.filter(subject_mapping_id=subject_mapping_id).exists():
            raise serializers.ValidationError({'subject_mapping_id': 'Syllabus already exists for this subject mapping'})
        
        # 4. Validate active academic year (optional enforcement)
        try:
            config = SchoolFeatureConfig.objects.get(school_id=school_id, feature__code='ACADEMIC_YEAR')
            config_data = json.loads(config.config_json)
            current_year = config_data.get('current')
            if current_year and data.get('academic_year') != current_year:
                raise serializers.ValidationError({'academic_year': f'Academic year must be {current_year}'})
        except (SchoolFeatureConfig.DoesNotExist, json.JSONDecodeError, KeyError):
            pass
        
        return data
    
    def create(self, validated_data):
        """Create syllabus with explicit FKs"""
        school_id = validated_data.pop('school_id')
        subject_mapping_id = validated_data.pop('subject_mapping_id')
        
        return Syllabus.objects.create(
            school_id=school_id,
            subject_mapping_id=subject_mapping_id,
            **validated_data
        )


# ============================================================
# EXAM & RESULT SERIALIZERS
# ============================================================

class ExamSerializer(serializers.ModelSerializer):
    # Read-only display fields
    subject_name = serializers.CharField(source='subject_mapping.subject.name', read_only=True)
    section_name = serializers.CharField(source='section.full_name', read_only=True)
    exam_type_display = serializers.CharField(source='get_exam_type_display', read_only=True)
    
    # Write-only ID fields for creation
    school_id = serializers.UUIDField(write_only=True, required=True)
    section_id = serializers.UUIDField(write_only=True, required=True)
    subject_mapping_id = serializers.UUIDField(write_only=True, required=True)
    invigilator_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Exam
        fields = [
            'id', 'name', 'exam_type', 'exam_type_display', 'subject_name', 'section_name',
            'exam_date', 'duration_minutes', 'max_marks', 'passing_marks', 'academic_year',
            'exam_room', 'min_attendance_percentage', 'grace_marks',
            'school_id', 'section_id', 'subject_mapping_id', 'invigilator_ids'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """Validate same-school, feature flag, and active academic year"""
        from apps.schools.models import School
        from apps.teachers.models import Teacher
        from apps.features.models import SchoolFeatureConfig
        
        if self.instance:  # Skip on update
            return data
        
        school_id = data.get('school_id')
        section_id = data.get('section_id')
        subject_mapping_id = data.get('subject_mapping_id')
        invigilator_ids = data.get('invigilator_ids', [])
        
        # 1. Check feature flag
        if not school_has_feature(school_id, 'MARKS_ENTRY'):
            raise serializers.ValidationError({'school_id': 'Exam management not enabled for this school'})
        
        # 2. Validate same-school for section
        try:
            section = Section.objects.get(id=section_id)
            if str(section.school_id) != str(school_id):
                raise serializers.ValidationError({'section_id': 'Section does not belong to this school'})
        except Section.DoesNotExist:
            raise serializers.ValidationError({'section_id': 'Section not found'})
        
        # 3. Validate same-school for subject_mapping
        try:
            subject_mapping = SubjectMapping.objects.get(id=subject_mapping_id)
            if str(subject_mapping.school_id) != str(school_id):
                raise serializers.ValidationError({'subject_mapping_id': 'Subject mapping does not belong to this school'})
            if str(subject_mapping.section_id) != str(section_id):
                raise serializers.ValidationError({'subject_mapping_id': 'Subject mapping does not belong to this section'})
        except SubjectMapping.DoesNotExist:
            raise serializers.ValidationError({'subject_mapping_id': 'Subject mapping not found'})
        
        # 4. Validate invigilators belong to school
        if invigilator_ids:
            invigilators = Teacher.objects.filter(id__in=invigilator_ids, school_id=school_id)
            if invigilators.count() != len(invigilator_ids):
                raise serializers.ValidationError({'invigilator_ids': 'One or more invigilators do not belong to this school'})
        
        # 5. Validate active academic year
        try:
            config = SchoolFeatureConfig.objects.get(school_id=school_id, feature__code='ACADEMIC_YEAR')
            config_data = json.loads(config.config_json)
            current_year = config_data.get('current')
            if current_year and data.get('academic_year') != current_year:
                raise serializers.ValidationError({'academic_year': f'Academic year must be {current_year}'})
        except SchoolFeatureConfig.DoesNotExist:
            pass  # No enforcement if not configured
        except (json.JSONDecodeError, KeyError):
            pass
        
        return data
    
    def create(self, validated_data):
        """Create exam with explicit FKs from write-only IDs"""
        from apps.teachers.models import Teacher
        
        school_id = validated_data.pop('school_id')
        section_id = validated_data.pop('section_id')
        subject_mapping_id = validated_data.pop('subject_mapping_id')
        invigilator_ids = validated_data.pop('invigilator_ids', [])
        
        exam = Exam.objects.create(
            school_id=school_id,
            section_id=section_id,
            subject_mapping_id=subject_mapping_id,
            **validated_data
        )
        
        if invigilator_ids:
            invigilators = Teacher.objects.filter(id__in=invigilator_ids)
            exam.invigilators.set(invigilators)
        
        return exam


class ResultSerializer(serializers.ModelSerializer):
    # Read-only display fields
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    student_suid = serializers.CharField(source='student.suid', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    subject_name = serializers.CharField(source='exam.subject_mapping.subject.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.full_name', read_only=True, allow_null=True)
    percentage = serializers.SerializerMethodField()
    
    # Write-only ID fields for creation
    exam_id = serializers.UUIDField(write_only=True, required=True)
    student_id = serializers.UUIDField(write_only=True, required=True)
    
    class Meta:
        model = Result
        fields = [
            'id', 'student_name', 'student_suid', 'exam_name', 'subject_name',
            'marks_obtained', 'percentage', 'grade', 'grade_point', 'is_absent',
            'remarks', 'recorded_by_name', 'recorded_at',
            'exam_id', 'student_id'
        ]
        read_only_fields = ['grade', 'grade_point', 'recorded_at']
    
    def get_percentage(self, obj):
        if obj.is_absent:
            return 0
        return round((obj.marks_obtained / obj.exam.max_marks) * 100, 2)
    
    def validate(self, data):
        """Validate exam active, result window open, teacher permission, same school"""
        from apps.students.models import Student
        from apps.features.models import SchoolFeatureConfig
        
        if self.instance:  # Skip on update
            return data
        
        exam_id = data.get('exam_id')
        student_id = data.get('student_id')
        request = self.context.get('request')
        
        # 1. Validate exam exists
        try:
            exam = Exam.objects.select_related('school', 'subject_mapping__teacher').get(id=exam_id)
        except Exam.DoesNotExist:
            raise serializers.ValidationError({'exam_id': 'Exam not found'})
        
        # 2. Check feature flag
        if not school_has_feature(exam.school_id, 'MARKS_ENTRY'):
            raise serializers.ValidationError({'exam_id': 'Result entry not enabled for this school'})
        
        # 3. Validate exam is ACTIVE (today <= exam_date)
        if timezone.now().date() > exam.exam_date:
            raise serializers.ValidationError({'exam_id': 'Cannot enter results for past exams'})
        
        # 4. Validate result entry window is OPEN
        try:
            config = SchoolFeatureConfig.objects.get(school_id=exam.school_id, feature__code='MARKS_ENTRY')
            config_data = json.loads(config.config_json)
            days_after = config_data.get('result_entry_days_after_exam', 7)
        except (SchoolFeatureConfig.DoesNotExist, json.JSONDecodeError, KeyError):
            days_after = 7  # Default
        
        window_close = exam.exam_date + timedelta(days=days_after)
        if timezone.now().date() > window_close:
            raise serializers.ValidationError({'exam_id': f'Result entry window closed {days_after} days after exam date'})
        
        # 5. Validate student belongs to same school
        try:
            student = Student.objects.select_related('school').get(id=student_id)
            if str(student.school_id) != str(exam.school_id):
                raise serializers.ValidationError({'student_id': 'Student does not belong to exam school'})
        except Student.DoesNotExist:
            raise serializers.ValidationError({'student_id': 'Student not found'})
        
        # 6. Validate teacher permission (if request available)
        if request and request.user:
            user = request.user
            is_admin = user.is_superuser or getattr(user, 'is_staff', False)
            is_subject_teacher = (
                hasattr(user, 'teacher') and 
                exam.subject_mapping.teacher_id and
                str(exam.subject_mapping.teacher_id) == str(user.teacher.id)
            )
            is_invigilator = exam.invigilators.filter(user_id=user.id).exists()
            
            if not (is_admin or is_subject_teacher or is_invigilator):
                raise serializers.ValidationError('You do not have permission to enter results for this exam')
        
        # 7. Check for duplicate result
        if Result.objects.filter(exam_id=exam_id, student_id=student_id).exists():
            raise serializers.ValidationError('Result already exists for this student and exam')
        
        return data
    
    def create(self, validated_data):
        """Create result with explicit FKs and record user"""
        exam_id = validated_data.pop('exam_id')
        student_id = validated_data.pop('student_id')
        request = self.context.get('request')
        
        return Result.objects.create(
            exam_id=exam_id,
            student_id=student_id,
            recorded_by=request.user if request else None,
            **validated_data
        )


class ReportCardSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.full_name', read_only=True)
    student_suid = serializers.CharField(source='student.suid', read_only=True)
    section_name = serializers.CharField(source='section.full_name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = ReportCard
        fields = [
            'id', 'student_name', 'student_suid', 'section_name', 'term_name',
            'academic_year', 'total_marks_obtained', 'total_marks_possible',
            'percentage', 'grade_awarded', 'rank', 'remarks', 'generated_by_name',
            'generated_date', 'file_path'
        ]
        read_only_fields = ['generated_date']