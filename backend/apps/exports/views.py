import os
import io
import pandas as pd
from django.http import HttpResponse, FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.imports.models import ImportedFile
from apps.imports.analyzer import clean_dataframe


class ExportView(APIView):
    """
    POST /api/exports/
    Body: { file_id, format: 'xlsx'|'csv', mode: 'cleaned'|'joined'|'raw' }
    """
    def post(self, request):
        file_id = request.data.get('file_id')
        fmt = request.data.get('format', 'xlsx')
        mode = request.data.get('mode', 'cleaned')

        if not file_id:
            return Response({'error': 'file_id requis.'}, status=400)

        try:
            import_obj = ImportedFile.objects.get(id=file_id)
        except ImportedFile.DoesNotExist:
            return Response({'error': 'Fichier introuvable.'}, status=404)

        # Le manager voit les métadonnées mais ne télécharge pas les données des agents
        if import_obj.user != request.user and request.user.role != 'ADMIN':
            return Response({'error': 'Accès refusé : seuls le propriétaire du fichier et un administrateur '
                                      'peuvent télécharger ces données.'}, status=403)

        try:
            structure = import_obj.detected_structure or {}

            cleaned_cache = structure.get('cleaned_file_path')
            if mode == 'joined' and structure.get('joined_file_path'):
                joined_path = structure['joined_file_path']
                if not os.path.exists(joined_path):
                    df = None
                elif joined_path.lower().endswith('.csv'):
                    df = pd.read_csv(joined_path, dtype=str, encoding='utf-8-sig')
                else:
                    df = pd.read_excel(joined_path, dtype=str)
            elif cleaned_cache and os.path.exists(cleaned_cache):
                # Cache du nettoyage : lecture instantanée
                df = pd.read_csv(cleaned_cache, dtype=str, encoding='utf-8-sig')
            else:
                config = {
                    'header_rows_to_skip': import_obj.header_rows_to_skip,
                    'columns_to_drop': import_obj.columns_to_drop,
                    'column_mapping': import_obj.column_mapping,
                }
                df = clean_dataframe(import_obj.file.path, config)

            if df is None:
                return Response({'error': 'Données non disponibles.'}, status=404)

            base_name = os.path.splitext(import_obj.original_filename)[0]
            filename = f"{base_name}_{mode}.{fmt}"

            from apps.history.models import ActivityLog
            ActivityLog.objects.create(
                user=request.user, action='EXPORT', import_file=import_obj,
                description=f"Export {mode} de {import_obj.original_filename} au format {fmt.upper()}.",
            )

            if fmt == 'csv':
                buffer = io.StringIO()
                df.to_csv(buffer, index=False, encoding='utf-8-sig')
                response = HttpResponse(buffer.getvalue(), content_type='text/csv; charset=utf-8-sig')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Données')
                buffer.seek(0)
                response = HttpResponse(
                    buffer.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response

        except Exception as e:
            return Response({'error': str(e)}, status=500)


class BacklogExportView(APIView):
    """Exporte tous les rapports d'un projet en une seule table."""
    def post(self, request):
        from apps.history.models import ProcessingReport
        survey_type = request.data.get('survey_type')
        fmt = request.data.get('format', 'xlsx')

        reports = ProcessingReport.objects.filter(survey_type=survey_type)
        # Données privées : le backlog d'un non-admin ne contient que ses propres traitements
        if request.user.role != 'ADMIN':
            reports = reports.filter(user=request.user)

        dfs = []
        for report in reports:
            try:
                config = {
                    'header_rows_to_skip': report.import_file.header_rows_to_skip,
                    'columns_to_drop': report.import_file.columns_to_drop,
                    'column_mapping': report.import_file.column_mapping,
                }
                df = clean_dataframe(report.import_file.file.path, config)
                df['_period'] = report.period_label
                df['_project'] = report.project_name
                dfs.append(df)
            except Exception:
                continue

        if not dfs:
            return Response({'error': 'Aucune donnée disponible.'}, status=404)

        combined = pd.concat(dfs, ignore_index=True)
        filename = f"backlog_{survey_type}.{fmt}"

        if fmt == 'csv':
            buffer = io.StringIO()
            combined.to_csv(buffer, index=False, encoding='utf-8-sig')
            response = HttpResponse(buffer.getvalue(), content_type='text/csv; charset=utf-8-sig')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                combined.to_excel(writer, index=False, sheet_name='Backlog')
            buffer.seek(0)
            response = HttpResponse(buffer.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
