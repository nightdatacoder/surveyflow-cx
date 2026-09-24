from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from apps.imports.models import ImportedFile
from apps.history.models import ActivityLog, ProcessingReport
from apps.auth_app.models import User
from apps.auth_app.permissions import IsAdminOrManager


class AgentDashboardView(APIView):
    def get(self, request):
        user = request.user
        files = ImportedFile.objects.filter(user=user)
        recent = files.order_by('-created_at')[:5]

        return Response({
            'total_reports': files.count(),
            'total_rows': sum(f.total_rows for f in files),
            'recent_files': [
                {
                    'id': f.id,
                    'name': f.original_filename,
                    'project': f.project_name,
                    'status': f.status,
                    'rows': f.total_rows,
                    'date': f.created_at,
                }
                for f in recent
            ],
            'status_breakdown': {
                s['status']: s['count']
                for s in files.values('status').annotate(count=Count('id'))
            },
        })


class ManagerDashboardView(APIView):
    permission_classes = [IsAdminOrManager]

    def get(self, request):
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0)

        files = ImportedFile.objects.all()
        this_month = files.filter(created_at__gte=month_start)

        by_survey_type = (
            files.values('survey_type')
            .annotate(count=Count('id'), rows=Sum('total_rows'))
            .order_by('-count')
        )

        monthly_volume = (
            files.annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'), rows=Sum('total_rows'))
            .order_by('month')
        )

        agent_activity = (
            files.values('user__username', 'user__first_name', 'user__last_name')
            .annotate(files_count=Count('id'), total_rows=Sum('total_rows'))
            .order_by('-files_count')[:10]
        )

        return Response({
            'total_reports': files.count(),
            'total_users': User.objects.filter(role='AGENT').count(),
            'this_month_reports': this_month.count(),
            'total_rows_processed': files.aggregate(t=Sum('total_rows'))['t'] or 0,
            'by_survey_type': list(by_survey_type),
            'monthly_volume': list(monthly_volume),
            'agent_activity': list(agent_activity),
        })


class AdminDashboardView(APIView):
    permission_classes = [IsAdminOrManager]

    def get(self, request):
        users = User.objects.all()
        logs = ActivityLog.objects.order_by('-created_at')[:50]

        return Response({
            'users_count': users.count(),
            'agents_count': users.filter(role='AGENT').count(),
            'managers_count': users.filter(role='MANAGER').count(),
            'admins_count': users.filter(role='ADMIN').count(),
            'recent_logs': [
                {
                    'user': log.user.username if log.user else 'Système',
                    'action': log.get_action_display(),
                    'description': log.description,
                    'date': log.created_at,
                }
                for log in logs
            ],
        })
