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
        is_supervisor = user.role in ('ADMIN', 'MANAGER')
        base_files = ImportedFile.objects.all() if is_supervisor else ImportedFile.objects.filter(user=user)
        base_reports = ProcessingReport.objects.all() if is_supervisor else ProcessingReport.objects.filter(user=user)

        # Filtre optionnel par type d'enquête
        survey_type = request.query_params.get('survey_type') or ''
        files = base_files.filter(survey_type=survey_type) if survey_type else base_files
        reports = base_reports.filter(survey_type=survey_type) if survey_type else base_reports

        available_types = sorted(set(
            base_files.exclude(survey_type='').values_list('survey_type', flat=True)
        ))

        recent = files.order_by('-created_at')[:6]

        # NPS global = moyenne des scores NPS
        nps_scores = [r.nps_score for r in reports if r.nps_score is not None]
        nps_global = round(sum(nps_scores) / len(nps_scores), 1) if nps_scores else None

        # Répartition des sentiments (agrégée depuis les métriques NPS)
        prom = pas = det = 0
        for r in reports:
            for m in (r.metrics or {}).get('nps', []):
                prom += m.get('promoters', 0)
                pas += m.get('passives', 0)
                det += m.get('detractors', 0)
        total_sent = prom + pas + det

        # Tendance : enquêtes ce mois vs mois précédent
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        prev_start = (month_start - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month = files.filter(created_at__gte=month_start).count()
        prev_month = files.filter(created_at__gte=prev_start, created_at__lt=month_start).count()
        if prev_month > 0:
            files_trend = round((this_month - prev_month) / prev_month * 100)
        else:
            files_trend = (100 if this_month > 0 else 0)

        return Response({
            'scope': survey_type or 'all',
            'is_supervisor': is_supervisor,
            'available_types': available_types,
            'total_reports': files.count(),
            'total_rows': files.aggregate(t=Sum('total_rows'))['t'] or 0,
            'joined_count': files.filter(status='JOINED').count(),
            'users_count': User.objects.count() if is_supervisor else None,
            'this_month_reports': this_month,
            'files_trend': files_trend,
            'nps_global': nps_global,
            'sentiment': {'promoters': prom, 'passives': pas, 'detractors': det, 'total': total_sent},
            'satisfaction_pct': round(prom / total_sent * 100, 1) if total_sent else None,
            'detraction_pct': round(det / total_sent * 100, 1) if total_sent else None,
            'recent_files': [
                {
                    'id': f.id, 'name': f.original_filename, 'project': f.project_name,
                    'status': f.status, 'rows': f.total_rows, 'date': f.created_at,
                    'user': f.user.get_full_name() or f.user.username,
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
