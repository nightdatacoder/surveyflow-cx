from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActivityLogViewSet, ProcessingReportViewSet

router = DefaultRouter()
router.register('logs', ActivityLogViewSet, basename='log')
router.register('reports', ProcessingReportViewSet, basename='report')

urlpatterns = [path('', include(router.urls))]
