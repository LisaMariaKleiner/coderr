"""
URL configuration for Coderr Backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('authentication_app.urls')),
    path('api/', include('users_app.urls')),
    path('api/', include('offers_app.urls')),
    path('api/', include('orders_app.urls')),
    path('api/', include('reviews_app.urls')),
    path('api/', include('platform_info_app.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
