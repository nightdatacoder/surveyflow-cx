from django.db import models
from apps.auth_app.models import User
from apps.imports.models import ImportedFile


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('IMPORT', 'Import fichier'),
        ('CLEAN', 'Nettoyage'),
        ('JOIN', 'Jointure'),
        ('EXPORT', 'Export'),
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Déconnexion'),
        ('CREATE_USER', 'Création utilisateur'),
        ('DELETE', 'Suppression'),
        ('TEMPLATE_SAVE', 'Sauvegarde modèle'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    import_file = models.ForeignKey(ImportedFile, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.created_at:%d/%m/%Y %H:%M} — {self.user} — {self.action}"


class ProcessingReport(models.Model):
    VERSION_CHOICES = [
        ('NEW', 'Nouvelle version'),
        ('REPLACE', 'Remplacement'),
        ('CONCAT', 'Concaténation'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    import_file = models.ForeignKey(ImportedFile, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=200)
    survey_type = models.CharField(max_length=100)
    period_label = models.CharField(max_length=100, blank=True)
    version_mode = models.CharField(max_length=10, choices=VERSION_CHOICES, default='NEW')
    rows_processed = models.IntegerField(default=0)
    columns_count = models.IntegerField(default=0)
    join_applied = models.BooleanField(default=False)
    output_file_path = models.CharField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    # Score NPS principal (pour la comparaison période sur période) + détail JSON
    nps_score = models.FloatField(null=True, blank=True)
    metrics = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project_name} — {self.period_label}"
