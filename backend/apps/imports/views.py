import os
import traceback
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import ImportedFile, SurveyTemplate
from .serializers import ImportedFileSerializer, FileUploadSerializer, SurveyTemplateSerializer
from .analyzer import (load_and_analyze, clean_dataframe, detect_missing_values,
                       compute_nps_metrics, detect_duplicate_respondents)


class SurveyTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = SurveyTemplateSerializer

    def get_queryset(self):
        return SurveyTemplate.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # Modèles de base MTN : suppression réservée à l'admin, avec avertissement
    PROTECTED_TEMPLATES = {'Modèle VOC EBU', 'Modèle 4G', 'Modèle FTTH',
                           'Modèle Transactions EU', 'Modèle Transactions Agents'}

    def update(self, request, *args, **kwargs):
        tpl = self.get_object()
        # Même règle que la suppression : créateur ou admin uniquement
        if request.user.role != 'ADMIN' and tpl.created_by_id != request.user.id:
            return Response({'error': 'Seul le créateur de ce modèle ou un administrateur peut le modifier.'}, status=403)
        if tpl.name in self.PROTECTED_TEMPLATES and request.user.role != 'ADMIN':
            return Response({'error': f'« {tpl.name} » est un modèle de base MTN, modifiable uniquement par un administrateur.'}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        tpl = self.get_object()
        if tpl.name in self.PROTECTED_TEMPLATES:
            if request.user.role != 'ADMIN':
                return Response(
                    {'error': f'« {tpl.name} » est un modèle de base MTN. Seul un administrateur peut le supprimer.'},
                    status=403,
                )
            if request.query_params.get('confirm') != 'true':
                return Response(
                    {'warning': f'« {tpl.name} » est un modèle de base utilisé pour les nettoyages automatiques. '
                                'Sa suppression désactivera le traitement automatique de ce type d\'enquête. '
                                'Confirmez-vous la suppression ?'},
                    status=409,
                )
        elif request.user.role != 'ADMIN' and tpl.created_by_id != request.user.id:
            return Response(
                {'error': 'Seul le créateur de ce modèle ou un administrateur peut le supprimer.'},
                status=403,
            )
        return super().destroy(request, *args, **kwargs)


def _do_cleaning(import_obj, column_mapping, columns_to_drop, header_rows_to_skip, column_order=None):
    """Nettoyage commun : retourne la réponse dict ou lève une exception."""
    config = {
        'header_rows_to_skip': header_rows_to_skip,
        'columns_to_drop': columns_to_drop,
        'column_mapping': column_mapping,
        'column_order': column_order or [],
    }
    df = clean_dataframe(import_obj.file.path, config)

    import_obj.column_mapping = column_mapping
    import_obj.columns_to_drop = columns_to_drop
    import_obj.header_rows_to_skip = header_rows_to_skip
    import_obj.total_rows = len(df)
    import_obj.total_columns = len(df.columns)
    import_obj.status = 'CLEANED'

    missing = detect_missing_values(df)
    nps_metrics = compute_nps_metrics(df)
    duplicates = detect_duplicate_respondents(df)
    detected = import_obj.detected_structure or {}
    detected['missing_values_report'] = missing
    detected['nps_metrics'] = nps_metrics
    detected['duplicates'] = duplicates
    detected['cleaned_columns'] = list(df.columns)

    # Cache du résultat nettoyé : les exports et jointures le réutilisent
    # au lieu de re-nettoyer le fichier brut à chaque fois
    cleaned_path = os.path.join(os.path.dirname(import_obj.file.path), f'cleaned_{import_obj.id}.csv')
    df.to_csv(cleaned_path, index=False, encoding='utf-8-sig')
    detected['cleaned_file_path'] = cleaned_path

    join_key_orig = detected.get('join_key', '')
    renamed = column_mapping.get(join_key_orig, join_key_orig) if join_key_orig else ''
    if renamed in df.columns:
        detected['join_key_final'] = renamed
    elif join_key_orig in df.columns:
        detected['join_key_final'] = join_key_orig

    detected['column_order'] = column_order or []
    import_obj.detected_structure = detected
    import_obj.save()

    # Historiser le traitement
    from apps.history.models import ProcessingReport, ActivityLog
    version_mode = (import_obj.detected_structure or {}).get('version_mode', 'NEW')
    if version_mode == 'REPLACE':
        # Remplacer : les anciens rapports de ce type (même utilisateur) sont retirés
        ProcessingReport.objects.filter(
            user=import_obj.user, survey_type=import_obj.survey_type or '',
        ).exclude(import_file=import_obj).delete()
    # Score NPS principal = moyenne des scores NPS (hors CSAT/CES)
    nps_score = round(sum(n['nps'] for n in nps_metrics) / len(nps_metrics), 1) if nps_metrics else None
    ProcessingReport.objects.update_or_create(
        import_file=import_obj,
        defaults={
            'user': import_obj.user,
            'project_name': import_obj.project_name or import_obj.original_filename,
            'survey_type': import_obj.survey_type or '',
            'rows_processed': len(df),
            'columns_count': len(df.columns),
            'version_mode': version_mode,
            'nps_score': nps_score,
            'metrics': {'nps': nps_metrics, 'duplicates': duplicates},
        },
    )
    ActivityLog.objects.create(
        user=import_obj.user, action='CLEAN', import_file=import_obj,
        description=f"Nettoyage de {import_obj.original_filename} : {len(df)} lignes, {len(df.columns)} colonnes.",
    )

    return {
        'status': 'CLEANED',
        'rows': len(df),
        'columns': list(df.columns),
        'missing_report': missing,
        'nps_metrics': nps_metrics,
        'duplicates': duplicates,
        'join_key': detected.get('join_key_final', ''),
        'preview': df.head(10).fillna('').to_dict(orient='records'),
    }


class ImportedFileViewSet(viewsets.ModelViewSet):
    serializer_class = ImportedFileSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'MANAGER']:
            return ImportedFile.objects.all()
        return ImportedFile.objects.filter(user=user)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data['file']
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in ['.xlsx', '.xls', '.csv']:
            return Response({'error': 'Format non supporté. Utilisez XLSX, XLS ou CSV.'}, status=400)

        template_id = serializer.validated_data.get('template_id')
        template = SurveyTemplate.objects.filter(id=template_id).first() if template_id else None

        import_obj = ImportedFile.objects.create(
            user=request.user,
            original_filename=uploaded_file.name,
            file=uploaded_file,
            file_size=uploaded_file.size,
            project_name=serializer.validated_data.get('project_name', ''),
            survey_type=serializer.validated_data.get('survey_type', ''),
            template=template,
            status='ANALYZING',
        )

        from apps.history.models import ActivityLog
        ActivityLog.objects.create(
            user=request.user, action='IMPORT', import_file=import_obj,
            description=f"Import du fichier {uploaded_file.name} ({import_obj.survey_type or 'type non défini'}).",
        )

        auto_cleaned = False
        try:
            structure = load_and_analyze(import_obj.file.path)
            structure['version_mode'] = serializer.validated_data.get('version_mode', 'NEW')
            import_obj.detected_structure = structure
            import_obj.is_surveymonkey = structure.get('is_surveymonkey', False)
            import_obj.total_columns = len(structure.get('detected_columns', []))
            import_obj.total_rows = max(0, structure.get('total_rows_raw', 0) - structure.get('header_rows_to_skip', 2))
            import_obj.header_rows_to_skip = structure.get('header_rows_to_skip', 2)

            if template:
                # Survey existant : pré-remplir avec le modèle puis nettoyer directement
                import_obj.column_mapping = template.column_mapping
                import_obj.columns_to_drop = template.columns_to_drop
                import_obj.status = 'ANALYZED'
                import_obj.save()
                _do_cleaning(import_obj, template.column_mapping, template.columns_to_drop,
                             import_obj.header_rows_to_skip, template.column_order)
                auto_cleaned = True
            else:
                # Nouveau survey : suggestions par défaut, l'agent nommera les colonnes
                import_obj.column_mapping = structure.get('suggested_mapping', {})
                import_obj.columns_to_drop = structure.get('suggested_drops', [])
                import_obj.status = 'ANALYZED'
                import_obj.save()
        except Exception as e:
            import_obj.status = 'ERROR'
            import_obj.error_message = f"{str(e)}\n{traceback.format_exc()}"
            import_obj.save()

        data = ImportedFileSerializer(import_obj).data
        data['auto_cleaned'] = auto_cleaned
        return Response(data, status=201)

    def _check_data_access(self, request, import_obj):
        """Le manager supervise les métadonnées mais ne manipule pas les données des agents."""
        if import_obj.user != request.user and request.user.role != 'ADMIN':
            return Response({'error': 'Accès refusé : seul le propriétaire du fichier ou un administrateur '
                                      'peut accéder à ces données.'}, status=403)
        return None

    def destroy(self, request, *args, **kwargs):
        denied = self._check_data_access(request, self.get_object())
        if denied:
            return denied
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        denied = self._check_data_access(request, self.get_object())
        if denied:
            return denied
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def apply_cleaning(self, request, pk=None):
        import_obj = self.get_object()
        denied = self._check_data_access(request, import_obj)
        if denied:
            return denied
        column_mapping = request.data.get('column_mapping', import_obj.column_mapping) or {}
        columns_to_drop = request.data.get('columns_to_drop', import_obj.columns_to_drop) or []
        header_rows_to_skip = int(request.data.get('header_rows_to_skip', import_obj.header_rows_to_skip))
        column_order = request.data.get('column_order') or []

        try:
            result = _do_cleaning(import_obj, column_mapping, columns_to_drop, header_rows_to_skip, column_order)

            # Sauvegarde auto du modèle si demandé (nouveau survey validé)
            save_template = request.data.get('save_template')
            if save_template:
                name = request.data.get('template_name') or f"Modèle {import_obj.survey_type or import_obj.original_filename}"
                tpl, _ = SurveyTemplate.objects.update_or_create(
                    name=name,
                    defaults={
                        'survey_type': import_obj.survey_type or name,
                        'created_by': request.user,
                        'column_mapping': column_mapping,
                        'columns_to_drop': columns_to_drop,
                        'column_order': column_order,
                        'header_rows_to_skip': header_rows_to_skip,
                    },
                )
                result['template_saved'] = tpl.name
            return Response(result)
        except Exception as e:
            import_obj.status = 'ERROR'
            import_obj.error_message = str(e)
            import_obj.save()
            return Response({'error': str(e), 'detail': traceback.format_exc()}, status=500)

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        import_obj = self.get_object()
        denied = self._check_data_access(request, import_obj)
        if denied:
            return denied
        try:
            config = {
                'header_rows_to_skip': import_obj.header_rows_to_skip,
                'columns_to_drop': import_obj.columns_to_drop,
                'column_mapping': import_obj.column_mapping,
                'column_order': (import_obj.detected_structure or {}).get('column_order', []),
            }
            df = clean_dataframe(import_obj.file.path, config)
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 50))
            start = (page - 1) * page_size
            chunk = df.iloc[start:start + page_size].fillna('').to_dict(orient='records')
            return Response({'total': len(df), 'page': page, 'columns': list(df.columns), 'data': chunk})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['post'])
    def save_as_template(self, request, pk=None):
        import_obj = self.get_object()
        name = request.data.get('name') or f'Modèle {import_obj.survey_type or import_obj.original_filename}'
        survey_type = request.data.get('survey_type', import_obj.survey_type)
        tpl, _ = SurveyTemplate.objects.update_or_create(
            name=name,
            defaults={
                'survey_type': survey_type,
                'created_by': request.user,
                'column_mapping': import_obj.column_mapping,
                'columns_to_drop': import_obj.columns_to_drop,
                'column_order': (import_obj.detected_structure or {}).get('column_order', []),
                'header_rows_to_skip': import_obj.header_rows_to_skip,
            },
        )
        return Response(SurveyTemplateSerializer(tpl).data, status=201)

    DEFAULT_SURVEY_TYPES = ['VOC EBU', 'FTTH', '4G', 'Roaming']

    @action(detail=False, methods=['get'])
    def survey_types(self, request):
        """Types d'enquête : défauts + ceux créés par les utilisateurs (via modèles)."""
        saved = list(SurveyTemplate.objects.values(
            'id', 'name', 'survey_type', 'header_rows_to_skip', 'created_by', 'created_by__username'))
        types = list(self.DEFAULT_SURVEY_TYPES)
        for t in saved:
            st = (t['survey_type'] or '').strip()
            if st and st not in types:
                types.append(st)
        return Response({'types': types, 'saved': saved, 'builtin': []})
