from django.urls import path
from .views import ExportView, BacklogExportView

urlpatterns = [
    path('', ExportView.as_view(), name='export'),
    path('backlog/', BacklogExportView.as_view(), name='backlog_export'),
]
