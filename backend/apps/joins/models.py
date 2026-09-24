from django.db import models
from apps.imports.models import ImportedFile
from apps.auth_app.models import User


class JoinOperation(models.Model):
    JOIN_TYPE_CHOICES = [
        ('LEFT', 'LEFT JOIN'),
        ('INNER', 'INNER JOIN'),
        ('FULL', 'FULL OUTER JOIN'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('RUNNING', 'En cours'),
        ('DONE', 'Terminé'),
        ('ERROR', 'Erreur'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    main_file = models.ForeignKey(ImportedFile, on_delete=models.CASCADE, related_name='joins_as_main')
    ref_file = models.FileField(upload_to='joins/%Y/%m/', null=True, blank=True)
    ref_filename = models.CharField(max_length=255, blank=True)
    ref_sheet = models.CharField(max_length=100, blank=True)
    join_type = models.CharField(max_length=10, choices=JOIN_TYPE_CHOICES, default='LEFT')
    left_key = models.CharField(max_length=100)
    right_key = models.CharField(max_length=100)
    columns_to_add = models.JSONField(default=list)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    result_rows = models.IntegerField(default=0)
    result_columns = models.IntegerField(default=0)
    match_rate = models.FloatField(default=0.0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"JOIN {self.main_file.original_filename} ↔ {self.ref_filename}"
