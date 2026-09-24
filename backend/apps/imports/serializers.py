from rest_framework import serializers
from .models import ImportedFile, SurveyTemplate


class SurveyTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = SurveyTemplate
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']


class ImportedFileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    file_size_display = serializers.SerializerMethodField()

    class Meta:
        model = ImportedFile
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at', 'detected_structure']

    def get_file_size_display(self, obj):
        size = obj.file_size
        if size < 1024:
            return f"{size} o"
        elif size < 1024 ** 2:
            return f"{size / 1024:.1f} Ko"
        return f"{size / 1024 ** 2:.1f} Mo"


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, f):
        if f.size > 50 * 1024 * 1024:
            raise serializers.ValidationError('Fichier trop volumineux : maximum 50 Mo.')
        return f
    project_name = serializers.CharField(max_length=200, required=False, default='')
    survey_type = serializers.CharField(max_length=100, required=False, default='')
    template_id = serializers.IntegerField(required=False, allow_null=True)
    # NEW = nouvelle version, REPLACE = remplacer l'existant, CONCAT = concaténer à l'historique
    version_mode = serializers.ChoiceField(choices=['NEW', 'REPLACE', 'CONCAT'], required=False, default='NEW')
