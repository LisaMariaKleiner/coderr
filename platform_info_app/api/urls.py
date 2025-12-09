from django.urls import path
from .views import BaseInfoView

urlpatterns = [
    path('platform-info/', BaseInfoView.as_view(), name='platform-info'),
]
