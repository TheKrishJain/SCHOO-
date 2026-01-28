from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import GatePass
from .serializers import GatePassSerializer
from apps.accounts.permission_utils import RBACPermission

class GatePassViewSet(viewsets.ModelViewSet):
    queryset = GatePass.objects.all()
    serializer_class = GatePassSerializer
    permission_classes = [IsAuthenticated, RBACPermission]
    
    # RBAC Configuration
    rbac_module = 'gatepass'
    rbac_resource = 'gatepass'
    rbac_action_permissions = {
        'scan': 'gatepass.scan_gatepass',
        'active': 'gatepass.view_gatepass',
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        
        student_id = self.request.query_params.get('student')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        pass_status = self.request.query_params.get('status')
        if pass_status:
            queryset = queryset.filter(status=pass_status)
            
        # `issued_at` was renamed to `requested_at` in migrations; order by the actual field
        return queryset.order_by('-requested_at')
    
    def perform_create(self, serializer):
        serializer.save(
            issued_by=self.request.user,
            issued_at=timezone.now(),
            valid_until=timezone.now() + timedelta(hours=2),
            status='ACTIVE'
        )
    
    @action(detail=True, methods=['post'])
    def scan(self, request, pk=None):
        gate_pass = self.get_object()
        
        if gate_pass.status == 'USED':
            return Response({'error': 'Pass already used'}, status=status.HTTP_400_BAD_REQUEST)
        
        if timezone.now() > gate_pass.valid_until:
            gate_pass.status = 'EXPIRED'
            gate_pass.save()
            return Response({'error': 'Pass expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        gate_pass.status = 'USED'
        gate_pass.scanned_by = request.user
        gate_pass.scanned_at = timezone.now()
        gate_pass.save()
        
        return Response(GatePassSerializer(gate_pass).data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        active_passes = self.get_queryset().filter(status='ACTIVE')
        serializer = self.get_serializer(active_passes, many=True)
        return Response(serializer.data)