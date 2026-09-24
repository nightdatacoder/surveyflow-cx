from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JoinViewSet

router = DefaultRouter()
router.register('', JoinViewSet, basename='join')

urlpatterns = [path('', include(router.urls))]
