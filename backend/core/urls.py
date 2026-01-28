from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.accounts.views import dashboard_summary

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth & Dashboard
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/dashboard/summary/', dashboard_summary, name='dashboard_summary'),
    
    # Core Entities
    path('api/v1/schools/', include('apps.schools.urls')),
    path('api/v1/students/', include('apps.students.urls')),
    path('api/v1/teachers/', include('apps.teachers.urls')),
    path('api/v1/enrollments/', include('apps.enrollments.urls')),
    
    # Academic Features
    path('api/v1/academics/', include('apps.academics.urls')),
    path('api/v1/attendance/', include('apps.attendance.urls')),
    
    # Student Lifecycle
    path('api/v1/transfers/', include('apps.transfers.urls')),
    path('api/v1/discipline/', include('apps.discipline.urls')),
    path('api/v1/achievements/', include('apps.achievements.urls')),
    
    # Operations
    path('api/v1/gatepass/', include('apps.gatepass.urls')),
    path('api/v1/health/', include('apps.health.urls')),
    path('api/v1/finance/', include('apps.finance.urls')),
    path('api/v1/promotions/', include('apps.promotions.urls')),
    
    # Platform Management
    path('api/v1/platform/', include('apps.platform_admin.urls')),
    
    # System
    path('api/v1/audit/', include('apps.audit.urls')),
    
    # Notifications
    path('api/v1/notifications/', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)