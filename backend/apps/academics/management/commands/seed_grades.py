from django.core.management.base import BaseCommand
from apps.academics.models import Grade
from apps.schools.models import School

class Command(BaseCommand):
    help = 'Seeds grade levels 1-12 for all schools'

    def handle(self, *args, **kwargs):
        schools = School.objects.all()
        
        if not schools.exists():
            self.stdout.write(self.style.WARNING('No schools found. Please create a school first.'))
            return
        
        for school in schools:
            for grade_num in range(1, 13):  # 1 to 12
                grade, created = Grade.objects.get_or_create(
                    school=school,
                    grade_number=grade_num,
                    defaults={
                        'grade_name': f'Class {grade_num}',
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created: {grade.grade_name} for {school.name}'))
                else:
                    self.stdout.write(f'Already exists: {grade.grade_name}')
        
        self.stdout.write(self.style.SUCCESS('✓ Grade seeding complete!'))
