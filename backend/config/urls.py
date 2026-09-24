from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.auth_app.urls')),
    path('api/imports/', include('apps.imports.urls')),
    path('api/processing/', include('apps.processing.urls')),
    path('api/joins/', include('apps.joins.urls')),
    path('api/history/', include('apps.history.urls')),
    path('api/exports/', include('apps.exports.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
