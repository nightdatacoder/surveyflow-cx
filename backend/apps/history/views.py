from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from .models import ActivityLog, ProcessingReport
from apps.auth_app.permissions import IsAdminOrManager


class ActivityLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    action_label = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = ActivityLog
        fields = '__all__'


class ProcessingReportSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = ProcessingReport
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class ActivityLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ActivityLogSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'MANAGER']:
            return ActivityLog.objects.all()
        return ActivityLog.objects.filter(user=user)


class ProcessingReportViewSet(viewsets.ModelViewSet):
    serializer_class = ProcessingReportSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'MANAGER']:
            return ProcessingReport.objects.all()
        return ProcessingReport.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def by_project(self, request):
        qs = self.get_queryset()
        survey_type = request.query_params.get('survey_type')
        if survey_type:
            qs = qs.filter(survey_type=survey_type)
        data = qs.values('period_label', 'rows_processed', 'created_at', 'version_mode', 'project_name')
        return Response(list(data))

    @action(detail=False, methods=['get'])
    def nps_evolution(self, request):
        """Évolution du NPS par type d'enquête dans le temps (comparaison période sur période)."""
        qs = self.get_queryset().filter(nps_score__isnull=False).order_by('created_at')
        series = {}
        for r in qs:
            series.setdefault(r.survey_type or 'Autre', []).append({
                'project': r.project_name,
                'date': r.created_at,
                'nps': r.nps_score,
                'rows': r.rows_processed,
                'detail': (r.metrics or {}).get('nps', []),
            })
        # Synthèse : NPS le plus récent + variation par rapport au précédent
        summary = []
        for survey_type, points in series.items():
            latest = points[-1]
            prev = points[-2] if len(points) > 1 else None
            summary.append({
                'survey_type': survey_type,
                'latest_nps': latest['nps'],
                'latest_project': latest['project'],
                'delta': round(latest['nps'] - prev['nps'], 1) if prev else None,
                'count': len(points),
            })
        summary.sort(key=lambda s: -s['latest_nps'])
        return Response({'series': series, 'summary': summary})
