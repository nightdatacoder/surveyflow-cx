from django.db import models
from apps.auth_app.models import User


class SurveyTemplate(models.Model):
    name = models.CharField(max_length=200)
    survey_type = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    column_mapping = models.JSONField(default=dict)
    columns_to_drop = models.JSONField(default=list)
    # Ordre final des colonnes (liste de noms cibles) — MySQL ne préserve pas
    # l'ordre des clés JSON, d'où une liste explicite
    column_order = models.JSONField(default=list)
    header_rows_to_skip = models.IntegerField(default=2)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.survey_type})"


class ImportedFile(models.Model):
    STATUS_CHOICES = [
        ('UPLOADED', 'Uploadé'),
        ('ANALYZING', 'Analyse en cours'),
        ('ANALYZED', 'Analysé'),
        ('CLEANING', 'Nettoyage en cours'),
        ('CLEANED', 'Nettoyé'),
        ('JOINED', 'Enrichi'),
        ('EXPORTED', 'Exporté'),
        ('ERROR', 'Erreur'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='imports')
    original_filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/%Y/%m/')
    file_size = models.BigIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UPLOADED')
    survey_type = models.CharField(max_length=100, blank=True)
    project_name = models.CharField(max_length=200, blank=True)
    template = models.ForeignKey(SurveyTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    total_rows = models.IntegerField(default=0)
    total_columns = models.IntegerField(default=0)
    detected_structure = models.JSONField(default=dict)
    column_mapping = models.JSONField(default=dict)
    columns_to_drop = models.JSONField(default=list)
    header_rows_to_skip = models.IntegerField(default=2)
    is_surveymonkey = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.original_filename} — {self.user.username}"
