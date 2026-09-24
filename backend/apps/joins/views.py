import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import JoinOperation
from .matcher import suggest_join_keys, perform_join, analyze_ref_file, read_ref_sheet
from apps.imports.analyzer import clean_dataframe
from apps.imports.models import ImportedFile
import pandas as pd
from rest_framework import serializers


class JoinOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinOperation
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'result_rows', 'result_columns', 'match_rate', 'status']


def _ref_cache_path(uploaded_bytes_md5: str, sheet_name) -> str:
    """Chemin du cache CSV d'une feuille de référence déjà parsée."""
    import re
    from django.conf import settings
    cache_dir = os.path.join(settings.MEDIA_ROOT, 'ref_cache')
    os.makedirs(cache_dir, exist_ok=True)
    # Purge opportuniste des caches de plus de 24h
    import time
    for f in os.listdir(cache_dir):
        p = os.path.join(cache_dir, f)
        try:
            if time.time() - os.path.getmtime(p) > 86400:
                os.unlink(p)
        except OSError:
            pass
    safe = re.sub(r'[^A-Za-z0-9]', '_', str(sheet_name))[:40]
    return os.path.join(cache_dir, f'{uploaded_bytes_md5}__{safe}.csv')


def _md5_of(path: str) -> str:
    import hashlib
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


class JoinViewSet(viewsets.ModelViewSet):
    serializer_class = JoinOperationSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'MANAGER']:
            return JoinOperation.objects.all()
        return JoinOperation.objects.filter(user=user)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def analyze_ref(self, request):
        """Analyse le fichier de référence et retourne ses feuilles/colonnes."""
        ref_file = request.FILES.get('ref_file')
        main_file_id = request.data.get('main_file_id')
        if not ref_file or not main_file_id:
            return Response({'error': 'ref_file et main_file_id requis.'}, status=400)

        import tempfile, os
        suffix = os.path.splitext(ref_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in ref_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            # Chaque feuille candidate est mise en cache pendant l'analyse :
            # l'exécution de la jointure n'aura pas à relire le classeur
            md5 = _md5_of(tmp_path)

            def cache_writer(sheet_name, df):
                try:
                    df.to_csv(_ref_cache_path(md5, sheet_name), index=False, encoding='utf-8-sig')
                except Exception:
                    pass  # le cache est un bonus, jamais bloquant

            ref_info = analyze_ref_file(tmp_path, cache_writer=cache_writer)
            main_obj = ImportedFile.objects.get(id=main_file_id)
            main_cols = main_obj.detected_structure.get('cleaned_columns') or list(
                clean_dataframe(main_obj.file.path, {
                    'header_rows_to_skip': main_obj.header_rows_to_skip,
                    'columns_to_drop': main_obj.columns_to_drop,
                    'column_mapping': main_obj.column_mapping,
                }).columns
            )

            suggestions = {}
            for sheet, cols in ref_info['sheets'].items():
                sugg = suggest_join_keys(main_cols, cols)
                suggestions[sheet] = sugg

            return Response({
                'ref_sheets': ref_info,
                'main_columns': main_cols,
                'key_suggestions': suggestions,
                'best_sheet': ref_info.get('best_sheet'),
                'best_key': ref_info.get('best_key'),
            })
        except Exception as e:
            import traceback
            return Response({'error': str(e), 'detail': traceback.format_exc()}, status=500)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass  # Windows : fichier encore verrouillé, le temp sera purgé par l'OS

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def execute(self, request):
        """Exécute la jointure et retourne un aperçu + statistiques."""
        main_file_id = request.data.get('main_file_id')
        left_key = request.data.get('left_key')
        right_key = request.data.get('right_key')
        join_type = request.data.get('join_type', 'LEFT')
        ref_sheet = request.data.get('ref_sheet', 0)
        columns_to_add = request.data.getlist('columns_to_add[]') or request.data.getlist('columns_to_add')
        ref_file = request.FILES.get('ref_file')

        if not all([main_file_id, left_key, right_key, ref_file]):
            return Response({'error': 'Paramètres manquants.'}, status=400)

        import tempfile, os, json
        suffix = os.path.splitext(ref_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in ref_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            main_obj = ImportedFile.objects.get(id=main_file_id)
            cleaned_cache = (main_obj.detected_structure or {}).get('cleaned_file_path')
            if cleaned_cache and os.path.exists(cleaned_cache):
                main_df = pd.read_csv(cleaned_cache, dtype=str, encoding='utf-8-sig')
            else:
                main_df = clean_dataframe(main_obj.file.path, {
                    'header_rows_to_skip': main_obj.header_rows_to_skip,
                    'columns_to_drop': main_obj.columns_to_drop,
                    'column_mapping': main_obj.column_mapping,
                })
            # Cache de l'analyse : si la feuille a déjà été parsée, lecture CSV instantanée
            cache_path = _ref_cache_path(_md5_of(tmp_path), ref_sheet)
            if os.path.exists(cache_path):
                ref_df = pd.read_csv(cache_path, dtype=str, encoding='utf-8-sig')
            else:
                # Retrouver la ligne d'en-tête de la feuille choisie (titres éventuels au-dessus)
                ref_info = analyze_ref_file(tmp_path)
                header_row = ref_info.get('header_rows', {}).get(str(ref_sheet), 0)
                ref_df = read_ref_sheet(tmp_path, ref_sheet, header_row)
                try:
                    ref_df.to_csv(cache_path, index=False, encoding='utf-8-sig')
                except Exception:
                    pass

            merged_df, match_rate, join_stats = perform_join(main_df, ref_df, left_key, right_key, join_type, columns_to_add or None)

            join_obj = JoinOperation.objects.create(
                user=request.user,
                main_file=main_obj,
                ref_filename=ref_file.name,
                ref_sheet=str(ref_sheet),
                join_type=join_type,
                left_key=left_key,
                right_key=right_key,
                columns_to_add=columns_to_add,
                status='DONE',
                result_rows=len(merged_df),
                result_columns=len(merged_df.columns),
                match_rate=match_rate,
            )

            # CSV : écriture quasi instantanée (l'Excel est généré au téléchargement)
            # Nom unique : évite l'erreur si l'ancien fichier est encore ouvert
            from datetime import datetime
            stamp = datetime.now().strftime('%H%M%S')
            out_path = os.path.join(os.path.dirname(main_obj.file.path), f'joined_{main_obj.id}_{stamp}.csv')
            merged_df.to_csv(out_path, index=False, encoding='utf-8-sig')

            structure = main_obj.detected_structure or {}
            structure['joined_file_path'] = out_path
            structure['joined_columns'] = list(merged_df.columns)
            main_obj.detected_structure = structure
            main_obj.status = 'JOINED'
            main_obj.save()

            from apps.history.models import ProcessingReport, ActivityLog
            ProcessingReport.objects.update_or_create(
                import_file=main_obj,
                defaults={
                    'user': request.user,
                    'project_name': main_obj.project_name or main_obj.original_filename,
                    'survey_type': main_obj.survey_type or '',
                    'rows_processed': len(merged_df),
                    'columns_count': len(merged_df.columns),
                    'join_applied': True,
                    'output_file_path': out_path,
                },
            )
            ActivityLog.objects.create(
                user=request.user, action='JOIN', import_file=main_obj,
                description=f"Jointure {join_type} avec {ref_file.name} : {match_rate}% de correspondance.",
            )

            return Response({
                'join_id': join_obj.id,
                'rows': len(merged_df),
                'columns': list(merged_df.columns),
                'match_rate': match_rate,
                'rescued': join_stats.get('rescued', 0),
                'rescued_by': join_stats.get('rescued_by', {}),
                'unmatched': join_stats.get('unmatched', 0),
                'unmatched_sample': join_stats.get('unmatched_sample', []),
                'preview': merged_df.head(10).fillna('').to_dict(orient='records'),
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
