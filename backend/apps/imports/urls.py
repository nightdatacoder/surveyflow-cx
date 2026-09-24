from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImportedFileViewSet, SurveyTemplateViewSet

router = DefaultRouter()
router.register('files', ImportedFileViewSet, basename='import')
router.register('templates', SurveyTemplateViewSet, basename='template')

urlpatterns = [path('', include(router.urls))]
