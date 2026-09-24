from django.urls import path
from .views import AgentDashboardView, ManagerDashboardView, AdminDashboardView

urlpatterns = [
    path('agent/', AgentDashboardView.as_view()),
    path('manager/', ManagerDashboardView.as_view()),
    path('admin/', AdminDashboardView.as_view()),
]
